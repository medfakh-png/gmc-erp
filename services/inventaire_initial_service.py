"""
Inventaire initial de démarrage (Phase 5.5 — décision validée « démarrage
du système en 2026 »).

Règle validée :
- GMC ERP commence son exploitation en 2026 par un INVENTAIRE INITIAL DE
  DÉMARRAGE, réalisé à l'instant exact de mise en service ; il devient le
  stock initial du système ;
- il n'est PAS un achat, ne génère PAS de faux BL fournisseur, n'alimente
  PAS les statistiques d'achat et n'est PAS une réception fournisseur ;
- après cet instant, toutes les opérations réelles sont enregistrées
  normalement ;
- le stock du 31/12/2025 n'est PAS l'ouverture automatique de 2026 ;
- chaque fin d'année : inventaire théorique, inventaire physique,
  rapprochement, correction/validation ; l'inventaire validé devient le
  stock d'ouverture de l'année suivante. Ce module annuel sera développé
  dans une phase dédiée : il s'appuiera sur le stock théorique à un instant
  donné (`stock_service.stock(..., jusqu_au=...)`) et sur les corrections
  d'inventaire tracées (`stock_service.corriger_inventaire`) — jamais sur
  une nouvelle entrée de stock (qui compterait deux fois la marchandise).

Chaque ligne enregistre : article, finition, longueur, pièces, poids,
emplacement physique, coût unitaire validé et son unité, valeur, devise,
horodatage (celui de la mise en service), utilisateur et date de saisie,
ainsi que la saisie d'origine avec ses unités (règle « unité obligatoire à
la saisie »). Le coût validé devient le coût d'entrée du lot dans la
valorisation CMP.

Unité du coût (règles définitives validées « unité du CMP » et
« Proposition A ») : le coût est CONSERVÉ dans l'unité où il a été saisi
(unité du prix saisi), qui doit être l'unité de valorisation de l'article
ou, pour un article valorisé au poids, l'autre unité de masse (kg <->
tonne). Il n'est jamais converti ni arrondi à l'enregistrement : la
conversion exacte vers l'unité de valorisation n'a lieu qu'au moment du
calcul. Ex. article en DT/kg, coût saisi « 2 500,5 DT/tonne » -> conservé
2 500 500 millimes/TONNE ; calcul : 2 500,5 millimes/kg exactement.

Choix techniques signalés (pas des règles métier) :
- un coût dans une unité incompatible (ex. DT/pièce pour un article au kg)
  est refusé — aucune conversion implicite ; un coût plus fin que le
  millime dans sa propre unité (ex. « 2 500,5005 DT/tonne ») est refusé,
  jamais arrondi ;
- valeur attendue = quantité dans l'unité × coût, arrondie une seule fois
  au millime le plus proche, 0,5 vers le haut (règle validée) : la valeur
  saisie doit être cette valeur arrondie (ex. 1 000,5 kg × 2,501 DT/kg ->
  « 2 502,251 DT ») ;
- une fois les opérations commencées (premier mouvement autre qu'une ligne
  d'inventaire initial), l'inventaire initial est clos : une ligne ajoutée
  après coup, datée de la mise en service, modifierait rétroactivement le
  CMP de sorties déjà enregistrées.
L'import réel des données n'est pas réalisé ici.
"""

from __future__ import annotations

import json
import sqlite3
import typing
import uuid

from core import unites
from core.erreurs import (
    ErreurDeviseMelangee,
    ErreurEmplacementInvalide,
    ErreurEnregistrementIntrouvable,
    ErreurInventaireInitialInvalide,
    ErreurMontantIncoherent,
    ErreurRegleViolee,
    ErreurSaisieInvalide,
    ErreurUniteValorisation,
)
from db import connexion, valorisation
from repositories import inventaire_initial_repository, stock_repository
from services import stock_service, unite_valorisation_service

FINITIONS_VALIDES = ("NOIR", "GALVA", "GPP")


def obtenir_inventaire_initial(conn: sqlite3.Connection) -> typing.Optional[dict]:
    """L'inventaire initial de démarrage (unique), ou None s'il n'a pas encore été créé."""
    return inventaire_initial_repository.obtenir_entete(conn)


def creer_inventaire_initial(
    conn: sqlite3.Connection,
    *,
    date_heure_mise_en_service: str,
    utilisateur_id: str,
    observation: typing.Optional[str] = None,
) -> str:
    """
    Crée l'en-tête de l'inventaire initial de démarrage, à l'instant exact
    de mise en service (heure obligatoire ; fuseau horaire recommandé, ex.
    « 2026-10-01T08:00:00+01:00 »). Transaction complète. Renvoie son id.
    """
    instant = stock_service.normaliser_horodatage(date_heure_mise_en_service, exiger_heure=True)
    stock_service.verifier_utilisateur(conn, utilisateur_id)
    existant = inventaire_initial_repository.obtenir_entete(conn)
    if existant is not None:
        raise ErreurInventaireInitialInvalide(
            "L'inventaire initial de démarrage existe déjà (mise en service le "
            f"{existant['date_heure_mise_en_service']}). Les années suivantes s'ouvrent par "
            "l'inventaire physique de fin d'année et son rapprochement, jamais par un second "
            "inventaire initial."
        )
    mouvements = stock_repository.compter_mouvements(conn)
    if mouvements:
        raise ErreurInventaireInitialInvalide(
            f"Inventaire initial impossible : le registre contient déjà {mouvements} mouvement(s). "
            "L'inventaire initial est le premier stock du système."
        )
    entete_id = str(uuid.uuid4())
    with connexion.transaction(conn):
        inventaire_initial_repository.inserer_entete(
            conn,
            id=entete_id,
            date_heure_mise_en_service=instant,
            observation=observation,
            cree_par=utilisateur_id,
        )
    return entete_id


def ajouter_ligne_inventaire_initial(
    conn: sqlite3.Connection,
    *,
    article_id: str,
    finition: str,
    longueur: typing.Any,
    quantite: typing.Any,
    poids: typing.Any,
    emplacement: str,
    cout_unitaire: typing.Any,
    valeur: typing.Any,
    utilisateur_id: str,
) -> dict:
    """
    Ajoute une ligne à l'inventaire initial, dans UNE transaction complète :
    ligne d'inventaire + lot d'origine « inventaire initial » + mouvement
    ENTREE_INVENTAIRE_INITIAL vers l'emplacement physique réel, daté de
    l'instant de mise en service. Si la ligne entre en STOCK_GMC, le cache
    CMP est reconstruit après la validation.

    Toutes les valeurs se saisissent AVEC leur unité (texte ou
    `core.unites.Mesure`) : longueur (« 6 m »), quantité (« 100 pièces »),
    poids (« 350 kg » ou « 0,35 t »), coût unitaire par pièce (« 5 DT/pièce »),
    valeur (« 500 DT »). Le coût unitaire est conservé dans l'unité saisie :
    celle de l'article (« 5 DT/unité », « 12 DT/ml », « 2,5 DT/kg »,
    « 2 500 DT/tonne ») ou, pour un article au poids, l'autre unité de masse
    (« 2 500,5 DT/tonne » pour un article en DT/kg).
    Renvoie {"ligne_id", "lot_id", "mouvement_id"}.
    """
    entete = inventaire_initial_repository.obtenir_entete(conn)
    if entete is None:
        raise ErreurEnregistrementIntrouvable(
            "Inventaire initial introuvable : créez d'abord son en-tête "
            "(instant de mise en service)."
        )
    stock_service.verifier_utilisateur(conn, utilisateur_id)
    stock_service.obtenir_article(conn, article_id)
    unite_valorisation = unite_valorisation_service.unite_valorisation(conn, article_id)
    if finition not in FINITIONS_VALIDES:
        raise ErreurRegleViolee(
            f"Finition inconnue : {finition!r} (attendu : {FINITIONS_VALIDES})."
        )

    m_longueur = unites.exiger(longueur, unites.LONGUEUR, "longueur")
    m_quantite = unites.exiger(quantite, unites.COMPTAGE, "quantité")
    m_poids = unites.exiger(poids, unites.MASSE, "poids")
    m_cout = unites.exiger(cout_unitaire, unites.PRIX, "coût unitaire")
    m_valeur = unites.exiger(valeur, unites.MONTANT, "valeur")

    longueur_m = float(unites.en_metres(m_longueur))
    if longueur_m <= 0:
        raise ErreurSaisieInvalide(f"Longueur invalide : « {m_longueur.saisie} ».")
    nb_pieces = unites.en_pieces(m_quantite)
    poids_kg = float(unites.en_kg(m_poids))
    stock_service.verifier_quantite_et_poids(nb_pieces, poids_kg)
    devise = m_cout.devise
    assert devise is not None
    if m_valeur.devise != devise:
        raise ErreurMontantIncoherent(
            f"La valeur « {m_valeur.saisie} » n'est pas dans la devise du coût unitaire ({devise})."
        )
    # Unité du prix saisi (B) : prix conservé tel quel, jamais converti ni arrondi.
    cout_minor, unite_cout = unites.prix_saisi(m_cout)
    if not unites.unites_de_prix_compatibles(unite_cout, unite_valorisation):
        raise ErreurUniteValorisation(
            f"« {m_cout.saisie} » n'est pas exprimé dans l'unité de valorisation de l'article "
            f"({unites.LIBELLES_UNITE_VALORISATION[unite_valorisation]}) ni dans une unité de "
            "masse équivalente : aucune conversion implicite n'est faite (seule la conversion "
            "kg <-> tonne est admise)."
        )
    valeur_minor = unites.montant_minor(m_valeur)
    # Unité de calcul (D) : conversion EXACTE du prix vers l'unité de valorisation.
    prix_exact = valorisation.convertir_prix_exact(cout_minor, unite_cout, unite_valorisation)
    quantite_valorisation = valorisation.quantite_en_unite(
        unite_valorisation, nb_pieces, poids_kg, longueur_m
    )
    libelle_unite = valorisation.LIBELLES_UNITE[unite_valorisation]
    valeur_exacte = quantite_valorisation * prix_exact
    # Montant final arrondi une seule fois au millime (règle validée).
    valeur_attendue = valorisation.montant_arrondi_minor(quantite_valorisation, prix_exact)
    if valeur_minor != valeur_attendue:
        raise ErreurMontantIncoherent(
            f"Valeur incohérente : « {m_valeur.saisie} » ≠ "
            f"{valorisation.en_texte(quantite_valorisation)} "
            f"{libelle_unite} × « {m_cout.saisie} » = {valeur_attendue} unités monétaires "
            "minimales après arrondi au millime (article valorisé en "
            f"{unites.LIBELLES_UNITE_VALORISATION[unite_valorisation]})."
        )

    stock_service.verifier_emplacement(conn, emplacement)
    if emplacement != stock_service.STOCK_GMC and not emplacement.startswith(
        stock_service.PREFIXE_TRANSFORMATEUR
    ):
        raise ErreurEmplacementInvalide(
            f"Emplacement {emplacement!r} refusé : le stock physique se trouve en STOCK_GMC ou "
            "chez un transformateur (CHUTES et LIVRE ne sont pas du stock)."
        )
    if emplacement == stock_service.STOCK_GMC:
        devises = stock_repository.devises_du_pool_en_stock_gmc(
            conn, article_id, finition, longueur_m
        )
        if devises - {devise}:
            raise ErreurDeviseMelangee(
                f"Le pool (article, {finition}, {longueur_m} m) est déjà valorisé en "
                f"{', '.join(sorted(devises))} : une ligne en {devise} mélangerait deux devises "
                "dans un même CMP."
            )
    operations = stock_repository.compter_mouvements(
        conn, types_exclus=("ENTREE_INVENTAIRE_INITIAL",)
    )
    if operations:
        raise ErreurInventaireInitialInvalide(
            f"Inventaire initial clos : {operations} opération(s) ont déjà été enregistrées depuis "
            "la mise en service. Une ligne ajoutée maintenant modifierait rétroactivement la "
            "valorisation de sorties déjà passées."
        )

    saisie = json.dumps(
        {
            "longueur": m_longueur.trace(),
            "quantite": m_quantite.trace(),
            "poids": m_poids.trace(),
            "cout_unitaire": m_cout.trace(),
            "valeur": m_valeur.trace(),
            "unite_prix_saisi": unite_cout,
            "prix_saisi_minor": cout_minor,
            "unite_valorisation": unite_valorisation,
            "conversion": (
                "aucune"
                if unite_cout == unite_valorisation
                else f"{unite_cout} -> {unite_valorisation} "
                f"({'÷' if unite_cout == 'TONNE' else '×'} 1000, exacte)"
            ),
            "prix_en_unite_valorisation_exact_minor": valorisation.en_texte(prix_exact),
            "valeur_calculee_exacte_minor": valorisation.en_texte(valeur_exacte),
            "valeur_arrondie_minor": valeur_attendue,
        },
        ensure_ascii=False,
    )
    ligne_id = str(uuid.uuid4())
    lot_id = str(uuid.uuid4())
    with connexion.transaction(conn):
        inventaire_initial_repository.inserer_ligne(
            conn,
            id=ligne_id,
            inventaire_initial_id=entete["id"],
            article_id=article_id,
            finition=finition,
            longueur_m=longueur_m,
            quantite=nb_pieces,
            poids_kg=poids_kg,
            emplacement=emplacement,
            cout_unitaire_minor=cout_minor,
            unite_cout=unite_cout,
            valeur_minor=valeur_minor,
            devise=devise,
            saisie_originale=saisie,
            cree_par=utilisateur_id,
        )
        # Coût déjà validé : à la fois coût d'entrée et coût définitif du lot
        # (aucune facture fournisseur ne viendra le régulariser).
        stock_repository.inserer_lot(
            conn,
            id=lot_id,
            article_id=article_id,
            finition=finition,
            longueur_m=longueur_m,
            quantite_initiale=nb_pieces,
            poids_initial_kg=poids_kg,
            prix_unitaire_provisoire_minor=cout_minor,
            prix_unitaire_definitif_minor=cout_minor,
            devise=devise,
            inventaire_initial_ligne_id=ligne_id,
            unite_prix=unite_cout,
            unite_prix_definitif=unite_cout,
        )
        mouvement_id = stock_service.enregistrer_mouvement(
            conn,
            lot_id=lot_id,
            type_mouvement="ENTREE_INVENTAIRE_INITIAL",
            quantite=nb_pieces,
            poids_kg=poids_kg,
            emplacement_source=None,
            emplacement_destination=emplacement,
            utilisateur_id=utilisateur_id,
            document_source_type="inventaire_initial_ligne",
            document_source_id=ligne_id,
            date_heure=entete["date_heure_mise_en_service"],
        )
    if emplacement == stock_service.STOCK_GMC:
        stock_service.reconstruire_cmp_apres_transaction(conn)
    return {"ligne_id": ligne_id, "lot_id": lot_id, "mouvement_id": mouvement_id}


def lignes_inventaire_initial(conn: sqlite3.Connection) -> list[dict]:
    """Lignes de l'inventaire initial (lecture seule), saisie d'origine comprise."""
    entete = inventaire_initial_repository.obtenir_entete(conn)
    if entete is None:
        return []
    return inventaire_initial_repository.lister_lignes(conn, entete["id"])
