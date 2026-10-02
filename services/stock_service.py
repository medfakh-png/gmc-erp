"""
Stock Service — socle minimal (Phase 5.5).

Périmètre validé (validation officielle de l'analyse Phase 5.5, §12) :
consultation des stocks et des soldes, disponibilité, historique des
mouvements, contrôle de conservation, brique `enregistrer_mouvement`,
retour de transformation sans stock fantôme (M2), correction
d'inventaire, erreurs métier, audit, transactions. Les flux complets
(achats, réceptions, transformations, livraisons, facturation) restent
hors périmètre : ils réutiliseront ces briques en Phases 5.7 à 5.9.

Principes appliqués (tous déjà validés, aucun inventé ici) :

- Le registre `mouvement_stock` (append-only) est la SEULE source de vérité
  du stock : aucune quantité n'est jamais stockée ni saisie directement,
  tout solde est recalculé depuis le registre.
- Un transformateur est un emplacement physique réel du stock GMC
  (`CHEZ_TRANSFORMATEUR:<id>`) : le stock est visible à chaque instant dans
  chaque emplacement.
- Réservation (devis) ≠ affectation ≠ mouvement ; une facture ne crée
  jamais de mouvement.
- Aucune brique de ce module ne fait de COMMIT : `enregistrer_mouvement` et
  `enregistrer_retour_transformation` participent à la transaction de leur
  appelant. Seul `corriger_inventaire` (opération complète) ouvre sa
  propre transaction (`db.connexion.transaction`).
- CMP : jamais de FIFO. Il est exprimé dans l'unité de valorisation de
  l'article (DT/kg, DT/ml, DT/unité, DT/tonne — règle définitive validée,
  `db/valorisation.py`). `reconstruire_cmp()` fait un COMMIT interne ; il
  n'est donc appelé qu'APRÈS la validation de la transaction métier, via
  `reconstruire_cmp_apres_transaction()`. Tout montant calculé est arrondi
  une seule fois au millime le plus proche, 0,5 vers le haut (règle validée,
  `core/arrondi.py`).
- Les articles sont lus, jamais créés ni modifiés ici.
- Unité obligatoire à la saisie (règle transversale validée) : les
  opérations saisies par un utilisateur (`corriger_inventaire`,
  inventaire initial) exigent des mesures avec unité (`core.unites`) et
  conservent la saisie d'origine ; la brique interne
  `enregistrer_mouvement` travaille dans les unités internes, nommées
  explicitement (`quantite` en pièces, `poids_kg` en kg).
- Horodatages du registre : format `AAAA-MM-JJTHH:MM:SS.mmm`, en UTC (comme
  la valeur par défaut de SQLite). Aucun mouvement ne peut être daté avant
  l'instant de mise en service (inventaire initial de démarrage).
"""

from __future__ import annotations

import datetime
import math
import sqlite3
import typing
import uuid

from core import audit, unites
from core.configuration import obtenir_logger
from core.erreurs import (
    ErreurDeviseMelangee,
    ErreurUniteValorisation,
    ErreurDisponibiliteInsuffisante,
    ErreurDocumentSourceManquant,
    ErreurEmplacementInvalide,
    ErreurEnregistrementIntrouvable,
    ErreurMotifObligatoire,
    ErreurMouvementEnDouble,
    ErreurMouvementIncoherent,
    ErreurQuantiteInvalide,
    ErreurRegleViolee,
    ErreurSaisieInvalide,
    ErreurStockInsuffisant,
)
from db import connexion, valorisation
from db.valorisation import reconstruire_cmp
from repositories import article_repository, inventaire_initial_repository, stock_repository

_log = obtenir_logger("services.stock")

# ---------------------------------------------------------------------------
# Emplacements et règles par type de mouvement
# ---------------------------------------------------------------------------

STOCK_GMC = "STOCK_GMC"
CHUTES = "CHUTES"
LIVRE = "LIVRE"
PREFIXE_TRANSFORMATEUR = "CHEZ_TRANSFORMATEUR:"

# Tolérance technique de comparaison des poids (kg) : les poids sont des
# REAL et leurs sommes peuvent porter un résidu d'arrondi binaire minuscule.
TOLERANCE_POIDS_KG = 1e-6

# Nature d'emplacement attendue, pour le contrôle du couple
# type / source / destination.
_AUCUN = "AUCUN"  # emplacement vide (NULL)
_STOCK_GMC = "STOCK_GMC"
_TRANSFORMATEUR = "TRANSFORMATEUR"
_STOCK = "STOCK"  # STOCK_GMC ou chez un transformateur (le stock GMC)
_CHUTES = "CHUTES"
_LIVRE = "LIVRE"


class _Regle(typing.NamedTuple):
    source: str
    destination: str
    document: typing.Optional[str]  # type de document source attendu ; None = généré (correction)
    voie_appariee: bool = False  # uniquement via enregistrer_retour_transformation


REGLES_MOUVEMENT: dict[str, _Regle] = {
    "ENTREE_RECEPTION_FOURNISSEUR": _Regle(_AUCUN, _STOCK_GMC, "bl_fournisseur_ligne"),
    "ENTREE_INVENTAIRE_INITIAL": _Regle(_AUCUN, _STOCK, "inventaire_initial_ligne"),
    "SORTIE_TRANSFORMATION": _Regle(_STOCK_GMC, _TRANSFORMATEUR, "bon_sortie_transformation_ligne"),
    "ENTREE_RETOUR_TRANSFORMATION": _Regle(
        _AUCUN, _STOCK_GMC, "reception_transformation_ligne", voie_appariee=True
    ),
    "CONSOMMATION_TRANSFORMATION": _Regle(
        _TRANSFORMATEUR, _AUCUN, "reception_transformation_ligne", voie_appariee=True
    ),
    "SORTIE_CHUTE": _Regle(_TRANSFORMATEUR, _CHUTES, "reception_transformation_ligne"),
    "SORTIE_LIVRAISON_CLIENT": _Regle(_STOCK_GMC, _LIVRE, "bl_client_ligne"),
    "CORRECTION_INVENTAIRE_POSITIVE": _Regle(_AUCUN, _STOCK, None),
    "CORRECTION_INVENTAIRE_NEGATIVE": _Regle(_STOCK, _AUCUN, None),
}

TYPES_CORRECTION = ("CORRECTION_INVENTAIRE_POSITIVE", "CORRECTION_INVENTAIRE_NEGATIVE")

_LIBELLES_NATURE = {
    _AUCUN: "aucun emplacement",
    _STOCK_GMC: "STOCK_GMC",
    _TRANSFORMATEUR: "CHEZ_TRANSFORMATEUR:<transformateur>",
    _STOCK: "STOCK_GMC ou CHEZ_TRANSFORMATEUR:<transformateur>",
    _CHUTES: "CHUTES",
    _LIVRE: "LIVRE",
}


def _nature(emplacement: typing.Optional[str]) -> str:
    if emplacement is None:
        return _AUCUN
    if emplacement == STOCK_GMC:
        return _STOCK_GMC
    if emplacement.startswith(PREFIXE_TRANSFORMATEUR):
        return _TRANSFORMATEUR
    if emplacement == CHUTES:
        return _CHUTES
    if emplacement == LIVRE:
        return _LIVRE
    return "INCONNU"


def _nature_compatible(nature_reelle: str, nature_attendue: str) -> bool:
    if nature_attendue == _STOCK:
        return nature_reelle in (_STOCK_GMC, _TRANSFORMATEUR)
    return nature_reelle == nature_attendue


def emplacement_transformateur(transformateur_id: str) -> str:
    """Nom d'emplacement d'un transformateur (ex. CHEZ_TRANSFORMATEUR:<id>)."""
    return f"{PREFIXE_TRANSFORMATEUR}{transformateur_id}"


def verifier_emplacement(conn: sqlite3.Connection, emplacement: typing.Optional[str]) -> None:
    """Lève `ErreurEmplacementInvalide` si l'emplacement n'existe pas."""
    if emplacement is None:
        return
    if not isinstance(emplacement, str):
        raise ErreurEmplacementInvalide(f"Emplacement invalide : {emplacement!r}.")
    nature = _nature(emplacement)
    if nature == "INCONNU":
        raise ErreurEmplacementInvalide(
            f"Emplacement inconnu : {emplacement!r}. Emplacements possibles : STOCK_GMC, "
            "CHEZ_TRANSFORMATEUR:<transformateur>, CHUTES, LIVRE."
        )
    if nature == _TRANSFORMATEUR:
        debut = len(PREFIXE_TRANSFORMATEUR)
        transformateur_id = emplacement[debut:]
        if not transformateur_id or not stock_repository.transformateur_existe(
            conn, transformateur_id
        ):
            raise ErreurEmplacementInvalide(
                f"Emplacement {emplacement!r} : ce transformateur n'existe pas dans le référentiel."
            )


# ---------------------------------------------------------------------------
# Contrôles élémentaires
# ---------------------------------------------------------------------------


def maintenant() -> str:
    """Instant présent, au format du registre (UTC, millisecondes)."""
    return _formater(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None))


def _formater(instant: datetime.datetime) -> str:
    return instant.strftime("%Y-%m-%dT%H:%M:%S.") + f"{instant.microsecond // 1000:03d}"


def normaliser_horodatage(valeur: typing.Any, exiger_heure: bool = False) -> str:
    """
    Date/heure ISO 8601 (ex. « 2026-10-01T08:00:00+01:00 ») convertie au
    format du registre (`AAAA-MM-JJTHH:MM:SS.mmm`, UTC). Une valeur sans
    fuseau est lue comme déjà exprimée en UTC, convention du registre
    (valeur par défaut de SQLite). `exiger_heure` refuse une date sans heure.
    """
    if not isinstance(valeur, str) or not valeur.strip():
        raise ErreurSaisieInvalide(f"Date/heure invalide : {valeur!r}.")
    texte = valeur.strip()
    if exiger_heure and "T" not in texte and " " not in texte:
        raise ErreurSaisieInvalide(
            f"« {texte} » : l'heure exacte est obligatoire (ex. « 2026-10-01T08:00:00+01:00 »)."
        )
    try:
        instant = datetime.datetime.fromisoformat(texte)
    except ValueError as exc:
        raise ErreurSaisieInvalide(
            f"Date/heure invalide : « {texte} » (format attendu : AAAA-MM-JJTHH:MM:SS, "
            "avec fuseau horaire de préférence)."
        ) from exc
    if instant.tzinfo is not None:
        instant = instant.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return _formater(instant)


def verifier_quantite_et_poids(quantite: typing.Any, poids_kg: typing.Any) -> None:
    if isinstance(quantite, bool) or not isinstance(quantite, int) or quantite <= 0:
        raise ErreurQuantiteInvalide(
            f"Quantité invalide : {quantite!r}. Une quantité est un nombre entier de pièces, "
            "strictement positif."
        )
    if (
        isinstance(poids_kg, bool)
        or not isinstance(poids_kg, (int, float))
        or not math.isfinite(poids_kg)
        or poids_kg <= 0
    ):
        raise ErreurQuantiteInvalide(
            f"Poids invalide : {poids_kg!r}. Le poids (kg) doit être un nombre strictement positif."
        )


def _poids_egaux(a: float, b: float) -> bool:
    return abs(float(a) - float(b)) <= TOLERANCE_POIDS_KG


def _obtenir_lot(conn: sqlite3.Connection, lot_id: str) -> dict:
    lot = stock_repository.obtenir_lot(conn, lot_id)
    if lot is None:
        raise ErreurEnregistrementIntrouvable(f"Lot introuvable : {lot_id!r}.")
    return lot


def obtenir_article(conn: sqlite3.Connection, article_id: str) -> dict:
    """Caractéristiques d'un article (lecture seule) ; erreur s'il n'existe pas."""
    article = article_repository.obtenir(conn, article_id)
    if article is None:
        raise ErreurEnregistrementIntrouvable(f"Article introuvable : {article_id!r}.")
    return article


def verifier_utilisateur(conn: sqlite3.Connection, utilisateur_id: str) -> None:
    if not utilisateur_id or not stock_repository.utilisateur_existe(conn, utilisateur_id):
        raise ErreurEnregistrementIntrouvable(
            f"Utilisateur introuvable : {utilisateur_id!r}. Tout mouvement doit être "
            "rattaché à un utilisateur existant (traçabilité)."
        )


def _incoherent(message: str) -> ErreurMouvementIncoherent:
    return ErreurMouvementIncoherent(message)


# ---------------------------------------------------------------------------
# Vérification du document source, type par type
# ---------------------------------------------------------------------------


def _verifier_document(
    conn: sqlite3.Connection,
    type_mouvement: str,
    lot: dict,
    quantite: int,
    poids_kg: float,
    emplacement_source: typing.Optional[str],
    emplacement_destination: typing.Optional[str],
    document_source_id: str,
) -> None:
    """
    Vérifie que le document source existe et qu'il correspond réellement au
    mouvement demandé (même lot, même quantité, même transformateur...).
    """

    def introuvable(libelle: str) -> ErreurDocumentSourceManquant:
        return ErreurDocumentSourceManquant(
            f"Document source introuvable : {libelle} {document_source_id!r} n'existe pas."
        )

    if type_mouvement == "ENTREE_RECEPTION_FOURNISSEUR":
        ligne = stock_repository.obtenir_bl_fournisseur_ligne(conn, document_source_id)
        if ligne is None:
            raise introuvable("ligne de BL fournisseur")
        if lot["bl_fournisseur_ligne_id"] != document_source_id:
            raise _incoherent("Ce lot n'a pas été créé à partir de cette ligne de BL fournisseur.")
        _verifier_entree_egale_au_lot(lot, quantite, poids_kg)

    elif type_mouvement == "ENTREE_INVENTAIRE_INITIAL":
        ligne = inventaire_initial_repository.obtenir_ligne(conn, document_source_id)
        if ligne is None:
            raise introuvable("ligne d'inventaire initial")
        if lot["inventaire_initial_ligne_id"] != document_source_id:
            raise _incoherent(
                "Ce lot n'a pas été créé à partir de cette ligne d'inventaire initial."
            )
        if emplacement_destination != ligne["emplacement"]:
            raise _incoherent(
                "L'entrée d'inventaire initial doit aller à l'emplacement réel déclaré "
                f"({ligne['emplacement']}), pas à {emplacement_destination}."
            )
        _verifier_entree_egale_au_lot(lot, quantite, poids_kg)

    elif type_mouvement == "SORTIE_TRANSFORMATION":
        ligne = stock_repository.obtenir_bon_sortie_transformation_ligne(conn, document_source_id)
        if ligne is None:
            raise introuvable("ligne de bon de sortie transformation")
        if ligne["lot_id"] != lot["id"]:
            raise _incoherent("Ce lot n'est pas celui du bon de sortie transformation.")
        if quantite != ligne["quantite"]:
            raise _incoherent(
                f"Quantité {quantite} différente de celle du bon de sortie ({ligne['quantite']})."
            )
        attendu = emplacement_transformateur(ligne["transformateur_id"])
        if emplacement_destination != attendu:
            raise _incoherent(
                f"La marchandise doit partir chez le transformateur du bon de sortie ({attendu})."
            )

    elif type_mouvement in (
        "SORTIE_CHUTE",
        "ENTREE_RETOUR_TRANSFORMATION",
        "CONSOMMATION_TRANSFORMATION",
    ):
        ligne = stock_repository.obtenir_reception_transformation_ligne(conn, document_source_id)
        if ligne is None:
            raise introuvable("ligne de réception de transformation")
        chez = emplacement_transformateur(ligne["transformateur_id"])
        if type_mouvement == "SORTIE_CHUTE":
            if ligne["lot_origine_id"] != lot["id"]:
                raise _incoherent(
                    "La chute doit être enregistrée sur le lot envoyé en transformation."
                )
            if quantite != ligne["quantite_chute"]:
                raise _incoherent(
                    f"Quantité {quantite} différente de la chute déclarée "
                    f"({ligne['quantite_chute']})."
                )
            if not _poids_egaux(poids_kg, ligne["poids_chute_kg"]):
                raise _incoherent(
                    f"Poids {poids_kg} kg différent du poids de chute déclaré "
                    f"({ligne['poids_chute_kg']} kg)."
                )
            if emplacement_source != chez:
                raise _incoherent(
                    f"La chute doit sortir de chez le transformateur concerné ({chez})."
                )
        elif type_mouvement == "CONSOMMATION_TRANSFORMATION":
            if ligne["lot_origine_id"] != lot["id"]:
                raise _incoherent(
                    "La consommation doit porter sur le lot envoyé en transformation."
                )
            if quantite != ligne["quantite_recue"]:
                raise _incoherent(
                    f"Quantité {quantite} différente de la quantité reçue "
                    f"({ligne['quantite_recue']})."
                )
            if emplacement_source != chez:
                raise _incoherent(
                    f"La consommation doit sortir de chez le transformateur concerné ({chez})."
                )
        else:  # ENTREE_RETOUR_TRANSFORMATION
            if ligne["lot_resultat_id"] != lot["id"]:
                raise _incoherent(
                    "Ce lot n'est pas le lot résultat de cette réception de transformation."
                )
            if lot["lot_parent_id"] != ligne["lot_origine_id"]:
                raise _incoherent(
                    "Le lot résultat doit avoir pour parent le lot envoyé en transformation."
                )
            if quantite != ligne["quantite_recue"]:
                raise _incoherent(
                    f"Quantité {quantite} différente de la quantité reçue "
                    f"({ligne['quantite_recue']})."
                )
            if not _poids_egaux(poids_kg, ligne["poids_recu_kg"]):
                raise _incoherent(
                    f"Poids {poids_kg} kg différent du poids reçu déclaré "
                    f"({ligne['poids_recu_kg']} kg)."
                )
            _verifier_entree_egale_au_lot(lot, quantite, poids_kg)

    elif type_mouvement == "SORTIE_LIVRAISON_CLIENT":
        ligne = stock_repository.obtenir_bl_client_ligne(conn, document_source_id)
        if ligne is None:
            raise introuvable("ligne de BL client")
        if ligne["lot_id"] != lot["id"]:
            raise _incoherent("Ce lot n'est pas celui de la ligne de BL client.")
        if quantite != ligne["quantite"]:
            raise _incoherent(
                f"Quantité {quantite} différente de celle de la ligne de BL client "
                f"({ligne['quantite']})."
            )

    else:  # pragma: no cover — garde-fou si une règle est ajoutée sans contrôle de document
        raise _incoherent(f"Aucun contrôle de document défini pour le type {type_mouvement}.")


def _verifier_entree_egale_au_lot(lot: dict, quantite: int, poids_kg: float) -> None:
    """
    Une entrée d'origine fait naître le lot : elle porte exactement sa
    quantité et son poids initiaux.
    """
    if quantite != lot["quantite_initiale"]:
        raise _incoherent(
            "L'entrée d'origine doit porter la quantité initiale du lot "
            f"({lot['quantite_initiale']}), "
            f"pas {quantite}."
        )
    if not _poids_egaux(poids_kg, lot["poids_initial_kg"]):
        raise _incoherent(
            "L'entrée d'origine doit porter le poids initial du lot "
            f"({lot['poids_initial_kg']} kg), "
            f"pas {poids_kg} kg."
        )


# ---------------------------------------------------------------------------
# Brique interne : enregistrer un mouvement
# ---------------------------------------------------------------------------


def enregistrer_mouvement(
    conn: sqlite3.Connection,
    *,
    lot_id: str,
    type_mouvement: str,
    quantite: int,
    poids_kg: float,
    emplacement_source: typing.Optional[str],
    emplacement_destination: typing.Optional[str],
    utilisateur_id: str,
    document_source_type: typing.Optional[str] = None,
    document_source_id: typing.Optional[str] = None,
    motif: typing.Optional[str] = None,
    date_heure: typing.Optional[str] = None,
) -> str:
    """
    Brique interne unique d'écriture dans le registre des mouvements.
    Renvoie l'identifiant du mouvement créé.

    Ne démarre AUCUNE transaction et ne fait AUCUN commit : participe à la
    transaction de l'appelant (qui doit utiliser `db.connexion.transaction`).

    Contrôles, dans l'ordre : type pris en charge ; quantité (pièces
    entières > 0) et poids (> 0) ; utilisateur, lot et article existants ;
    emplacements existants ; couple type / source / destination ; document
    source (présent, existant, cohérent avec le lot et la quantité) ;
    doublons ; solde et poids disponibles à la source. Pour une correction
    d'inventaire : motif obligatoire et écriture de l'audit
    (CORRECTION_INVENTAIRE), qui sert de document source au mouvement.

    Les types ENTREE_RETOUR_TRANSFORMATION et CONSOMMATION_TRANSFORMATION ne
    passent jamais par cette brique seule : ils vont toujours par paire,
    via `enregistrer_retour_transformation()` (pas de stock fantôme).
    """
    return _enregistrer(
        conn,
        lot_id=lot_id,
        type_mouvement=type_mouvement,
        quantite=quantite,
        poids_kg=poids_kg,
        emplacement_source=emplacement_source,
        emplacement_destination=emplacement_destination,
        utilisateur_id=utilisateur_id,
        document_source_type=document_source_type,
        document_source_id=document_source_id,
        motif=motif,
        date_heure=date_heure,
        voie_appariee=False,
    )


def _enregistrer(
    conn: sqlite3.Connection,
    *,
    lot_id: str,
    type_mouvement: str,
    quantite: int,
    poids_kg: float,
    emplacement_source: typing.Optional[str],
    emplacement_destination: typing.Optional[str],
    utilisateur_id: str,
    document_source_type: typing.Optional[str],
    document_source_id: typing.Optional[str],
    motif: typing.Optional[str],
    date_heure: typing.Optional[str],
    voie_appariee: bool,
    saisie_originale: typing.Optional[dict] = None,
) -> str:
    # 1. Type de mouvement pris en charge.
    if type_mouvement == "TRANSFERT":
        raise _incoherent(
            "Le type TRANSFERT n'est pas pris en charge : aucune règle métier n'est encore "
            "définie pour lui (GMC n'a qu'un seul dépôt)."
        )
    regle = REGLES_MOUVEMENT.get(type_mouvement)
    if regle is None:
        raise _incoherent(f"Type de mouvement inconnu : {type_mouvement!r}.")
    if regle.voie_appariee and not voie_appariee:
        raise _incoherent(
            f"Le type {type_mouvement} ne s'enregistre jamais seul : utilisez "
            "enregistrer_retour_transformation(), qui enregistre ensemble l'entrée du lot "
            "résultat en STOCK_GMC et la sortie de la même quantité de chez le transformateur "
            "(sinon la marchandise revenue resterait affichée chez le transformateur)."
        )

    # 2. Quantité, poids, horodatage (jamais avant la mise en service).
    verifier_quantite_et_poids(quantite, poids_kg)
    date_effective = normaliser_horodatage(date_heure) if date_heure is not None else maintenant()
    instant = stock_repository.instant_mise_en_service(conn)
    if (
        instant is not None
        and type_mouvement != "ENTREE_INVENTAIRE_INITIAL"
        and date_effective < instant
    ):
        raise _incoherent(
            f"Mouvement daté du {date_effective}, antérieur à la mise en service du système "
            f"({instant}, inventaire initial de démarrage) : refusé."
        )

    # 3. Utilisateur, lot, article.
    verifier_utilisateur(conn, utilisateur_id)
    lot = _obtenir_lot(conn, lot_id)
    obtenir_article(conn, lot["article_id"])

    # 4. Emplacements existants, puis couple type / source / destination.
    verifier_emplacement(conn, emplacement_source)
    verifier_emplacement(conn, emplacement_destination)
    nature_source = _nature(emplacement_source)
    nature_destination = _nature(emplacement_destination)
    if not _nature_compatible(nature_source, regle.source) or not _nature_compatible(
        nature_destination, regle.destination
    ):
        raise _incoherent(
            f"Emplacements non autorisés pour {type_mouvement} : attendu source = "
            f"{_LIBELLES_NATURE[regle.source]}, "
            f"destination = {_LIBELLES_NATURE[regle.destination]} ; "
            f"reçu source = {emplacement_source or 'aucune'}, destination = "
            f"{emplacement_destination or 'aucune'}."
        )

    # 5. Document source (ou motif pour une correction).
    est_correction = type_mouvement in TYPES_CORRECTION
    if est_correction:
        if motif is None or not str(motif).strip():
            raise ErreurMotifObligatoire(
                "Une correction d'inventaire doit obligatoirement comporter un motif."
            )
        if document_source_type is not None or document_source_id is not None:
            raise _incoherent(
                "Une correction d'inventaire n'accepte pas de document source externe : "
                "son document est l'entrée du journal d'audit créée avec elle."
            )
    else:
        if not document_source_type or not document_source_id:
            raise ErreurDocumentSourceManquant(
                f"Un mouvement {type_mouvement} doit être rattaché à son document source "
                f"({regle.document})."
            )
        if document_source_type != regle.document:
            raise ErreurDocumentSourceManquant(
                f"Document source inattendu pour {type_mouvement} : {document_source_type!r} "
                f"(attendu : {regle.document!r})."
            )
        _verifier_document(
            conn,
            type_mouvement,
            lot,
            quantite,
            poids_kg,
            emplacement_source,
            emplacement_destination,
            document_source_id,
        )

    # 6. Doublons (en plus des index uniques de la base, migration 0017).
    if type_mouvement in stock_repository.TYPES_ENTREE_ORIGINE:
        existante = stock_repository.entree_origine_du_lot(conn, lot_id)
        if existante is not None:
            raise ErreurMouvementEnDouble(
                f"Le lot {lot_id!r} a déjà son entrée d'origine ({existante['type']}, mouvement "
                f"{existante['id']}) : une seconde entrée compterait deux fois la même marchandise."
            )
    if not est_correction:
        assert document_source_type is not None and document_source_id is not None
        doublon = stock_repository.mouvement_pour_document(
            conn, type_mouvement, document_source_type, document_source_id
        )
        if doublon is not None:
            raise ErreurMouvementEnDouble(
                f"Un mouvement {type_mouvement} existe déjà pour ce document "
                f"({document_source_type} {document_source_id}) : mouvement {doublon['id']}."
            )

    # 7. Solde et poids disponibles à la source (jamais de stock négatif).
    solde_avant: typing.Optional[tuple[int, float]] = None
    if emplacement_source is not None:
        qte_dispo, poids_dispo = stock_repository.solde_lot_emplacement(
            conn, lot_id, emplacement_source
        )
        solde_avant = (qte_dispo, poids_dispo)
        if qte_dispo < quantite:
            raise ErreurStockInsuffisant(
                f"Solde insuffisant : le lot {lot_id!r} ne possède que {qte_dispo} pièce(s) à "
                f"{emplacement_source}, impossible d'en retirer {quantite}."
            )
        if poids_kg > poids_dispo + TOLERANCE_POIDS_KG:
            raise ErreurQuantiteInvalide(
                f"Poids incohérent : le lot {lot_id!r} ne pèse plus que "
                f"{round(poids_dispo, 6)} kg à "
                f"{emplacement_source}, impossible d'en retirer {poids_kg} kg."
            )

    # 8. Écriture (audit d'abord pour une correction : il en est le document source).
    mouvement_id = str(uuid.uuid4())
    if est_correction:
        emplacement = emplacement_destination if emplacement_source is None else emplacement_source
        assert emplacement is not None
        if solde_avant is None:
            solde_avant = stock_repository.solde_lot_emplacement(conn, lot_id, emplacement)
        signe = 1 if type_mouvement == "CORRECTION_INVENTAIRE_POSITIVE" else -1
        audit_id = audit.enregistrer(
            conn,
            utilisateur_id=utilisateur_id,
            action="CORRECTION_INVENTAIRE",
            entite_type="mouvement_stock",
            entite_id=mouvement_id,
            avant={
                "lot_id": lot_id,
                "emplacement": emplacement,
                "quantite": solde_avant[0],
                "poids_kg": round(solde_avant[1], 6),
            },
            apres={
                "lot_id": lot_id,
                "emplacement": emplacement,
                "quantite": solde_avant[0] + signe * quantite,
                "poids_kg": round(solde_avant[1] + signe * poids_kg, 6),
                **({"saisie": saisie_originale} if saisie_originale else {}),
            },
            motif=str(motif).strip(),
        )
        document_source_type, document_source_id = "journal_audit", audit_id

    assert document_source_type is not None and document_source_id is not None
    stock_repository.inserer_mouvement(
        conn,
        id=mouvement_id,
        lot_id=lot_id,
        type_mouvement=type_mouvement,
        quantite=quantite,
        poids_kg=poids_kg,
        emplacement_source=emplacement_source,
        emplacement_destination=emplacement_destination,
        document_source_type=document_source_type,
        document_source_id=document_source_id,
        utilisateur_id=utilisateur_id,
        motif=str(motif).strip() if motif is not None else None,
        date_heure=date_effective,
    )
    _log.debug(
        "Mouvement %s enregistré (%s, lot %s, %s pièce(s))",
        mouvement_id,
        type_mouvement,
        lot_id,
        quantite,
    )
    return mouvement_id


# ---------------------------------------------------------------------------
# Retour de transformation sans stock fantôme (M2)
# ---------------------------------------------------------------------------


def enregistrer_retour_transformation(
    conn: sqlite3.Connection,
    *,
    reception_transformation_ligne_id: str,
    poids_consomme_kg: float,
    utilisateur_id: str,
    date_heure: typing.Optional[str] = None,
) -> dict:
    """
    Enregistre ENSEMBLE, dans la transaction de l'appelant, les deux faces
    physiques d'un retour de transformation (décision validée Phase 5.5) :

      - CONSOMMATION_TRANSFORMATION : la quantité reçue quitte l'emplacement
        CHEZ_TRANSFORMATEUR:<id> du lot d'origine (transformateur : -N) ;
      - ENTREE_RETOUR_TRANSFORMATION : le lot résultat entre en STOCK_GMC
        (GMC : +N).

    `poids_consomme_kg` est le poids que le lot d'origine perd chez le
    transformateur (poids avant transformation) ; le poids du lot résultat
    est celui déclaré à la réception (il peut différer, ex. zinc ajouté en
    galvanisation). Les chutes s'enregistrent séparément (SORTIE_CHUTE via
    `enregistrer_mouvement`), selon la règle des chutes déjà validée.

    Hors périmètre 5.5 : la création du lot résultat, de la réception de
    transformation et de la chute (flux complet, Phase 5.8), ainsi que le
    débit 1 → N pièces (bloqué en base par `trg_reception_transfo_plafond`,
    à traiter en Phase 5.8).
    """
    ligne = stock_repository.obtenir_reception_transformation_ligne(
        conn, reception_transformation_ligne_id
    )
    if ligne is None:
        raise ErreurDocumentSourceManquant(
            f"Document source introuvable : ligne de réception de transformation "
            f"{reception_transformation_ligne_id!r} n'existe pas."
        )
    if not ligne["quantite_recue"] or ligne["lot_resultat_id"] is None:
        raise _incoherent(
            "Cette ligne de réception ne déclare aucune quantité reçue (lot résultat absent) : "
            "seule une éventuelle chute est à enregistrer."
        )
    chez = emplacement_transformateur(ligne["transformateur_id"])
    consommation_id = _enregistrer(
        conn,
        lot_id=ligne["lot_origine_id"],
        type_mouvement="CONSOMMATION_TRANSFORMATION",
        quantite=ligne["quantite_recue"],
        poids_kg=poids_consomme_kg,
        emplacement_source=chez,
        emplacement_destination=None,
        utilisateur_id=utilisateur_id,
        document_source_type="reception_transformation_ligne",
        document_source_id=reception_transformation_ligne_id,
        motif=None,
        date_heure=date_heure,
        voie_appariee=True,
    )
    entree_id = _enregistrer(
        conn,
        lot_id=ligne["lot_resultat_id"],
        type_mouvement="ENTREE_RETOUR_TRANSFORMATION",
        quantite=ligne["quantite_recue"],
        poids_kg=ligne["poids_recu_kg"],
        emplacement_source=None,
        emplacement_destination=STOCK_GMC,
        utilisateur_id=utilisateur_id,
        document_source_type="reception_transformation_ligne",
        document_source_id=reception_transformation_ligne_id,
        motif=None,
        date_heure=date_heure,
        voie_appariee=True,
    )
    return {"mouvement_consommation_id": consommation_id, "mouvement_entree_id": entree_id}


# ---------------------------------------------------------------------------
# CMP : reconstruction après validation de la transaction métier
# ---------------------------------------------------------------------------


def reconstruire_cmp_apres_transaction(conn: sqlite3.Connection) -> dict:
    """
    Reconstruit le cache CMP (`db/valorisation.py:reconstruire_cmp`)
    APRÈS la validation de la transaction métier — jamais pendant :
    `reconstruire_cmp()` fait lui-même un COMMIT, qui validerait sinon une
    transaction encore incomplète (constat E7 de l'analyse). Restaure le
    `row_factory` de la connexion (que `reconstruire_cmp()` modifie) et
    traduit ses erreurs en erreurs métier.
    """
    if conn.in_transaction:
        raise RuntimeError(
            "reconstruire_cmp_apres_transaction() appelée alors qu'une transaction est encore "
            "ouverte : le COMMIT interne de reconstruire_cmp() la validerait prématurément."
        )
    row_factory = conn.row_factory
    try:
        return reconstruire_cmp(conn)
    except valorisation.UniteValorisationError as exc:
        raise ErreurUniteValorisation(f"Valorisation CMP impossible : {exc}") from exc
    except ValueError as exc:
        if "devise" in str(exc).lower():
            raise ErreurDeviseMelangee(
                f"Valorisation impossible : un pool CMP mélangerait deux devises. (détail : {exc})"
            ) from exc
        raise ErreurRegleViolee(f"Valorisation CMP impossible. (détail technique : {exc})") from exc
    finally:
        conn.row_factory = row_factory


# ---------------------------------------------------------------------------
# Correction d'inventaire (opération complète)
# ---------------------------------------------------------------------------


def corriger_inventaire(
    conn: sqlite3.Connection,
    *,
    lot_id: str,
    sens: str,
    quantite: typing.Any,
    poids: typing.Any,
    emplacement: str,
    motif: str,
    utilisateur_id: str,
    date_heure: typing.Optional[str] = None,
) -> str:
    """
    Correction d'inventaire sur un lot existant, dans UNE transaction
    complète : mouvement CORRECTION_INVENTAIRE_POSITIVE/NEGATIVE + ligne
    d'audit CORRECTION_INVENTAIRE (motif obligatoire, utilisateur tracé).
    `sens` vaut 'POSITIVE' (pièces retrouvées) ou 'NEGATIVE' (pièces
    manquantes). `emplacement` : STOCK_GMC ou CHEZ_TRANSFORMATEUR:<id>.

    Unité obligatoire (règle validée) : `quantite` en pièces (ex.
    « 3 pièces ») et `poids` avec son unité (ex. « 10,5 kg » ou « 0,0105 t »),
    sous forme de texte ou de `core.unites.Mesure` ; un nombre seul est
    refusé. Le poids est converti en kg ; la saisie d'origine est conservée
    dans la ligne d'audit.

    Tout échec annule à la fois le mouvement et l'audit. Si la correction
    touche STOCK_GMC, le cache CMP est reconstruit après la validation.
    Les droits par rôle seront finalisés en Phase 14.
    """
    if sens not in ("POSITIVE", "NEGATIVE"):
        raise _incoherent(
            f"Sens de correction invalide : {sens!r} (attendu : 'POSITIVE' ou 'NEGATIVE')."
        )
    type_mouvement = f"CORRECTION_INVENTAIRE_{sens}"
    source, destination = (None, emplacement) if sens == "POSITIVE" else (emplacement, None)
    mesure_quantite = unites.exiger(quantite, unites.COMPTAGE, "quantité")
    mesure_poids = unites.exiger(poids, unites.MASSE, "poids")
    with connexion.transaction(conn):
        mouvement_id = _enregistrer(
            conn,
            lot_id=lot_id,
            type_mouvement=type_mouvement,
            quantite=unites.en_pieces(mesure_quantite),
            poids_kg=float(unites.en_kg(mesure_poids)),
            emplacement_source=source,
            emplacement_destination=destination,
            utilisateur_id=utilisateur_id,
            document_source_type=None,
            document_source_id=None,
            motif=motif,
            date_heure=date_heure,
            voie_appariee=False,
            saisie_originale={
                "quantite": mesure_quantite.trace(),
                "poids": mesure_poids.trace(),
            },
        )
    if emplacement == STOCK_GMC:
        reconstruire_cmp_apres_transaction(conn)
    return mouvement_id


# ---------------------------------------------------------------------------
# Consultations (lecture seule)
# ---------------------------------------------------------------------------


def _arrondir(lignes: list[dict]) -> list[dict]:
    for ligne in lignes:
        ligne["quantite"] = int(ligne["quantite"])
        ligne["poids_kg"] = round(float(ligne["poids_kg"]), 6)
    return lignes


def soldes_lot(
    conn: sqlite3.Connection, lot_id: str, jusqu_au: typing.Optional[str] = None
) -> dict[str, dict]:
    """
    Solde du lot dans chaque emplacement où il est présent :
    {emplacement: {quantite, poids_kg}}.
    """
    _obtenir_lot(conn, lot_id)
    return {
        ligne["emplacement"]: {"quantite": ligne["quantite"], "poids_kg": ligne["poids_kg"]}
        for ligne in _arrondir(
            stock_repository.stock_par_lot_et_emplacement(conn, lot_id=lot_id, jusqu_au=jusqu_au)
        )
    }


def stock(
    conn: sqlite3.Connection,
    *,
    emplacement: typing.Optional[str] = None,
    article_id: typing.Optional[str] = None,
    finition: typing.Optional[str] = None,
    longueur_m: typing.Optional[float] = None,
    jusqu_au: typing.Optional[str] = None,
) -> list[dict]:
    """
    Stock par lot et par emplacement (lignes non nulles), filtrable, à la
    date `jusqu_au` si elle est fournie (ex. stock de clôture au 31/12).
    """
    if emplacement is not None:
        verifier_emplacement(conn, emplacement)
    return _arrondir(
        stock_repository.stock_par_lot_et_emplacement(
            conn,
            emplacement=emplacement,
            article_id=article_id,
            finition=finition,
            longueur_m=longueur_m,
            jusqu_au=jusqu_au,
        )
    )


def stock_chez_transformateur(
    conn: sqlite3.Connection,
    transformateur_id: typing.Optional[str] = None,
    jusqu_au: typing.Optional[str] = None,
) -> list[dict]:
    """Stock GMC actuellement chez un transformateur donné (ou chez tous)."""
    if transformateur_id is not None:
        emplacement = emplacement_transformateur(transformateur_id)
        verifier_emplacement(conn, emplacement)
        return stock(conn, emplacement=emplacement, jusqu_au=jusqu_au)
    return _arrondir(
        stock_repository.stock_par_lot_et_emplacement(
            conn, prefixe_emplacement=PREFIXE_TRANSFORMATEUR, jusqu_au=jusqu_au
        )
    )


def quantite_affectable_lot(conn: sqlite3.Connection, lot_id: str) -> int:
    """
    Quantité encore affectable d'un lot = stock physique en STOCK_GMC moins
    ce qui est déjà affecté (affectations actives pas encore sorties).
    À utiliser par le futur Affaire Service (Phase 5.6) avant toute
    affectation — le trigger de la base ne plafonne que sur la quantité
    initiale du lot (constat E3 de l'analyse).
    """
    _obtenir_lot(conn, lot_id)
    physique, _ = stock_repository.solde_lot_emplacement(conn, lot_id, STOCK_GMC)
    return physique - stock_repository.quantite_affectee_non_sortie_lot(conn, lot_id)


def verifier_quantite_affectable(conn: sqlite3.Connection, lot_id: str, quantite: int) -> None:
    """
    Lève `ErreurDisponibiliteInsuffisante` si `quantite` dépasse la
    quantité affectable du lot.
    """
    disponible = quantite_affectable_lot(conn, lot_id)
    if quantite > disponible:
        raise ErreurDisponibiliteInsuffisante(
            f"Quantité demandée ({quantite}) supérieure à la quantité réellement disponible du lot "
            f"({disponible} = stock physique GMC moins quantités déjà affectées)."
        )


def disponibilite(
    conn: sqlite3.Connection,
    article_id: str,
    finition: str,
    longueur_m: float,
    a_la_date: typing.Optional[str] = None,
) -> dict:
    """
    Disponibilité d'un pool (article, finition, longueur) :

      - physique_stock_gmc      : pièces physiquement en STOCK_GMC ;
      - affecte_non_sorti       : pièces affectées à une affaire, pas encore sorties ;
      - disponible              : physique_stock_gmc - affecte_non_sorti ;
      - chez_transformateurs    : pièces du stock GMC actuellement chez un transformateur ;
      - reserve_devis_informatif: badge « réservé » des devis en cours — INFORMATIF,
                                  jamais déduit (une réservation n'est ni un mouvement
                                  ni une affectation).
    """
    obtenir_article(conn, article_id)
    date_ref = a_la_date or datetime.date.today().isoformat()
    lignes_gmc = stock_repository.stock_par_lot_et_emplacement(
        conn, emplacement=STOCK_GMC, article_id=article_id, finition=finition, longueur_m=longueur_m
    )
    lignes_transfo = stock_repository.stock_par_lot_et_emplacement(
        conn,
        prefixe_emplacement=PREFIXE_TRANSFORMATEUR,
        article_id=article_id,
        finition=finition,
        longueur_m=longueur_m,
    )
    physique = sum(int(ligne["quantite"]) for ligne in lignes_gmc)
    affecte = stock_repository.quantite_affectee_non_sortie_pool(
        conn, article_id, finition, longueur_m
    )
    return {
        "article_id": article_id,
        "finition": finition,
        "longueur_m": longueur_m,
        "physique_stock_gmc": physique,
        "poids_stock_gmc_kg": round(sum(float(ligne["poids_kg"]) for ligne in lignes_gmc), 6),
        "affecte_non_sorti": affecte,
        "disponible": physique - affecte,
        "chez_transformateurs": sum(int(ligne["quantite"]) for ligne in lignes_transfo),
        "reserve_devis_informatif": stock_repository.quantite_reservee_devis(
            conn, article_id, finition, longueur_m, date_ref
        ),
    }


def historique_mouvements(
    conn: sqlite3.Connection,
    *,
    lot_id: typing.Optional[str] = None,
    article_id: typing.Optional[str] = None,
    depuis: typing.Optional[str] = None,
    jusqu_au: typing.Optional[str] = None,
) -> list[dict]:
    """Historique des mouvements, du plus ancien au plus récent."""
    return stock_repository.lister_mouvements(
        conn, lot_id=lot_id, article_id=article_id, depuis=depuis, jusqu_au=jusqu_au
    )


def verifier_conservation(conn: sqlite3.Connection) -> dict:
    """
    Test de conservation (Phase 1 §28.8, confirmé Phase 5.5), en pièces :

        entrées externes (réceptions fournisseur + inventaire initial + corrections +)
      - sorties externes (corrections -)
      = STOCK_GMC + chez les transformateurs + CHUTES + LIVRE

    Une égalité n'est possible que si chaque retour de transformation est
    compensé exactement par la sortie de chez le transformateur (pas de
    stock fantôme) et que chaque livraison va bien vers LIVRE. Renvoie le
    détail et la liste des anomalies ; `equilibre` vaut True si tout est
    cohérent. Le poids est indiqué mais non comparé (la galvanisation
    ajoute du poids).
    """
    totaux = stock_repository.totaux_par_type(conn)
    entrees = sum(
        totaux.get(t, 0)
        for t in (
            "ENTREE_RECEPTION_FOURNISSEUR",
            "ENTREE_INVENTAIRE_INITIAL",
            "CORRECTION_INVENTAIRE_POSITIVE",
        )
    )
    sorties = totaux.get("CORRECTION_INVENTAIRE_NEGATIVE", 0)
    zones = {"STOCK_GMC": 0, "CHEZ_TRANSFORMATEURS": 0, "CHUTES": 0, "LIVRE": 0, "AUTRES": 0}
    poids_zones = dict.fromkeys(zones, 0.0)
    for ligne in stock_repository.stock_par_lot_et_emplacement(conn):
        nature = _nature(ligne["emplacement"])
        cle = {
            _STOCK_GMC: "STOCK_GMC",
            _TRANSFORMATEUR: "CHEZ_TRANSFORMATEURS",
            _CHUTES: "CHUTES",
            _LIVRE: "LIVRE",
        }.get(nature, "AUTRES")
        zones[cle] += int(ligne["quantite"])
        poids_zones[cle] += float(ligne["poids_kg"])
    anomalies: list[str] = []
    for retour in stock_repository.retours_transformation_non_apparies(conn):
        anomalies.append(
            f"Retour de transformation {retour['reception_transformation_ligne_id']} : "
            f"{retour['quantite_entree']} pièce(s) entrée(s) en stock mais "
            f"{retour['quantite_consommee']} sortie(s) de chez le transformateur (stock fantôme)."
        )
    for livraison in stock_repository.livraisons_sans_destination_livre(conn):
        anomalies.append(
            f"Livraison {livraison['id']} : destination {livraison['emplacement_destination']!r} "
            "au lieu de LIVRE."
        )
    attendu = entrees - sorties
    total = sum(zones.values())
    return {
        "entrees_externes": entrees,
        "sorties_externes": sorties,
        "attendu": attendu,
        "zones": zones,
        "poids_zones_kg": {cle: round(valeur, 6) for cle, valeur in poids_zones.items()},
        "total_zones": total,
        "ecart": total - attendu,
        "anomalies": anomalies,
        "equilibre": total == attendu and not anomalies,
    }
