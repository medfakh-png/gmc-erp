#!/usr/bin/env python3
"""
db/valorisation.py — Moteur de calcul du Coût Moyen Pondéré (CMP) du stock général GMC.

Règles de valorisation DÉFINITIVES (Phase 4, remplacent le FIFO des Phases 2/3) :
  1. Stock général GMC (non affecté)      -> CMP, par pool (article_id, finition, longueur_m)
  2. Quantité normale affectée (INITIALE) -> coût réel du lot affecté (prix définitif si
                                              connu, sinon prix provisoire) — ne passe
                                              JAMAIS par le CMP.
  3. Quantité supplémentaire (SUPPLEMENT) -> CMP applicable au moment de la sortie physique.
  4. Chute                                -> CMP applicable au moment de la sortie physique.
  5. FIFO -> abandonné, ne plus utiliser comme méthode de valorisation GMC.

────────────────────────────────────────────────────────────────────────────
PHASE 5.5 — UNITÉ DE VALORISATION (règle définitive validée) :

Le CMP n'est PAS systématiquement calculé en DT/kg : il est exprimé dans
l'UNITÉ DE VALORISATION de l'article — KG (DT/kg), ML (DT/ml), UNITE
(DT/unité = par pièce) ou TONNE (DT/tonne). Cette unité est lue dans
l'historique `article_unite_valorisation` (migration 0019) ; aucune unité
par défaut n'est jamais supposée : un article sans unité définie rend la
valorisation impossible (UniteValorisationError), jamais « par pièce » en
silence.

Quantité d'un mouvement dans une unité (conversions explicites) :
  UNITE -> nombre de pièces ; ML -> pièces × longueur du lot (m) ;
  KG -> poids en kg ; TONNE -> poids en kg / 1 000.

QUATRE NOTIONS D'UNITÉ, toujours distinctes (décision validée, Proposition A) :
  A. unité de valorisation de l'article (KG, TONNE, ML, UNITE) : unité dans
     laquelle le CMP est exprimé (`article_unite_valorisation`) ;
  B. unité du prix saisi : unité dans laquelle un prix a réellement été
     saisi, conservée avec lui (`lot.unite_prix` pour le prix provisoire,
     `lot.unite_prix_definitif` pour le prix définitif, unités de
     `regularisation_prix_fournisseur`). Elle peut différer de A uniquement
     entre unités de masse (kg <-> tonne), conversion physique exacte ;
  C. unité physique : pièces, kg, m (`mouvement_stock.quantite`, `poids_kg`,
     `lot.longueur_m`), inchangée ;
  D. unité de calcul : au moment du calcul seulement, le moteur convertit
     EXACTEMENT (fractions) le prix de B vers A (ex. 2 500 500 millimes/t ->
     2 500,5 millimes/kg, jamais 2 501) ; aucun arrondi intermédiaire, seul
     le montant final est arrondi au millime.

- Coût d'entrée d'un lot dans le pool = quantité du mouvement dans l'unité
  du prix (B) × prix (définitif s'il existe, avec SON unité, sinon
  provisoire) : un montant d'argent, arrondi une seule fois — identique au
  calcul « quantité dans A × prix converti exactement en A ». Un lot créé
  avant un changement d'unité reste donc valorisé exactement à son coût.
- Sortie = retrait proportionnel sur la quantité du pool exprimée dans
  l'unité EN VIGUEUR À LA DATE DU MOUVEMENT (au poids pour KG/TONNE, au
  métrage/à la pièce pour ML/UNITE). Un changement d'unité ne réécrit donc
  jamais les lignes de `cmp_historique` antérieures à sa date d'effet.
- ARRONDI (règle définitive validée, `core/arrondi.py`, implémentation
  unique) : un montant qui ne tombe pas exactement au millime est arrondi
  au millime le plus proche, 0,5 vers le haut, UNE SEULE FOIS, sur le
  montant final (entrée d'un lot, sortie, coût réel, chute, CMP affiché).
  Aucun sous-calcul n'est arrondi : quantités, prix et CMP restent exacts
  (fractions) jusqu'au montant final — en particulier, une chute est
  valorisée avec le CMP EXACT au moment de l'envoi, jamais avec le CMP
  arrondi affiché.

────────────────────────────────────────────────────────────────────────────
PHASE 4.1 — REPRÉSENTATION MONÉTAIRE :

Tous les montants manipulés ici sont des ENTIERS en unité monétaire minimale
(millimes pour TND, centimes pour EUR/USD — cf. docs/PRIX_REVIENT.md), jamais
des flottants. Toute fonction qui renvoie un montant porte le suffixe `_minor`.
Les quantités physiques (REAL en base) sont relues en décimal exact (leur
écriture décimale la plus courte) et combinées en fractions exactes.

Un pool CMP (article_id, finition, longueur_m) est mono-devise : la première
écriture qui l'alimente fixe sa devise, et toute écriture ultérieure dans une
autre devise est REFUSÉE (ValueError) plutôt que silencieusement mélangée.

DÉRIVE D'ARRONDI : `cmp_unitaire_minor` (prix moyen PAR UNITÉ DE
VALORISATION) est une valeur ARRONDIE, dérivée pour l'affichage/le
diagnostic. Elle n'est JAMAIS utilisée comme base de calcul pour mettre à
jour le solde du pool. Le solde (`valeur_totale_minor`) est toujours mis à
jour par un calcul PROPORTIONNEL EXACT sur le total exact courant
(`valeur × quantité_sortie / quantité_pool`, arrondi une seule fois, au plus
proche), jamais par « prix unitaire arrondi × quantité » répété : une sortie
qui vide le pool le ramène à exactement 0. `cmp_historique.montant_mouvement_minor`
conserve ce montant exact pour chaque mouvement.
────────────────────────────────────────────────────────────────────────────
Le ledger CMP (cmp_stock_general + cmp_historique) est un cache MÉCANIQUE,
piloté exclusivement par le registre append-only mouvement_stock : tout
mouvement dont la source et/ou la destination vaut 'STOCK_GMC' fait varier
le pool concerné, QUELLE QUE SOIT l'affectation liée à ce mouvement. La règle
2 (« coût réel du lot affecté ») n'est appliquée qu'au niveau des fonctions
cout_sortie_*(), jamais en modifiant ce ledger.

Convention requise pour que cout_chute_*() fonctionne : le mouvement_stock de
type SORTIE_TRANSFORMATION doit être enregistré avec
document_source_type='bon_sortie_transformation_ligne' et
document_source_id=<id de la ligne de bon de sortie correspondante>.

Toujours rejouable depuis zéro : reconstruire_cmp() relit l'intégralité de
mouvement_stock dans l'ordre chronologique et régénère cmp_stock_general +
cmp_historique (il fait un COMMIT : ne jamais l'appeler dans une transaction
métier ouverte — cf. services/stock_service.reconstruire_cmp_apres_transaction).
"""

from __future__ import annotations

import decimal
import fractions
import pathlib
import sqlite3
import sys
import typing
import uuid

if __package__ in (None, ""):  # exécution directe : « python3 db/valorisation.py »
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from core.arrondi import arrondi_minor  # noqa: E402
from core.unites import unites_de_prix_compatibles  # noqa: E402

DEVISES_VALIDES = ("TND", "EUR", "USD")
UNITES_VALORISATION = ("KG", "ML", "UNITE", "TONNE")
LIBELLES_UNITE = {"KG": "kg", "ML": "ml", "UNITE": "unité", "TONNE": "tonne"}

F = fractions.Fraction


class UniteValorisationError(ValueError):
    """Unité de valorisation absente, inconnue ou incohérente."""


# ---------------------------------------------------------------------------
# Arithmétique exacte et unités
# ---------------------------------------------------------------------------


def _arrondi(valeur: F) -> int:
    """Arrondi monétaire validé (millime le plus proche, 0,5 vers le haut) — core/arrondi.py."""
    return arrondi_minor(valeur)


def _exact(valeur: typing.Any) -> F:
    """Valeur physique (REAL en base) relue en décimal exact : son écriture la plus courte."""
    if isinstance(valeur, int):
        return F(valeur)
    return F(decimal.Decimal(repr(float(valeur))))


def quantite_en_unite(
    unite: str, quantite_pieces: int, poids_kg: typing.Any, longueur_m: typing.Any
) -> F:
    """
    Quantité physique exprimée dans une unité de valorisation (conversion
    explicite, exacte) : UNITE -> pièces ; ML -> pièces × longueur (m) ;
    KG -> kg ; TONNE -> kg / 1 000.
    """
    if unite == "UNITE":
        return F(quantite_pieces)
    if unite == "ML":
        return quantite_pieces * _exact(longueur_m)
    if unite == "KG":
        return _exact(poids_kg)
    if unite == "TONNE":
        return _exact(poids_kg) / 1000
    raise UniteValorisationError(f"Unité de valorisation inconnue : {unite!r}.")


def en_texte(quantite: F) -> str:
    """Quantité exacte écrite en décimal (affichage), sans arrondi si elle est décimale finie."""
    decimal_exact = decimal.Decimal(quantite.numerator) / decimal.Decimal(quantite.denominator)
    return format(decimal_exact.normalize(), "f")


def convertir_prix_exact(prix: typing.Union[int, F], unite_source: str, unite_cible: str) -> F:
    """
    Prix par unité `unite_source` -> prix par unité `unite_cible`, EXACT
    (fraction, jamais arrondi) : identité si les unités sont égales ; kg <->
    tonne (× ou ÷ 1 000) ; toute autre conversion est refusée (implicite).
    Ex. 2 500 500 millimes/t -> 5001/2 = 2 500,5 millimes/kg.
    """
    if unite_source == unite_cible:
        return F(prix)
    if unite_source == "TONNE" and unite_cible == "KG":
        return F(prix) / 1000
    if unite_source == "KG" and unite_cible == "TONNE":
        return F(prix) * 1000
    raise UniteValorisationError(
        f"Conversion de prix {unite_source} -> {unite_cible} impossible : seule la conversion "
        "kg <-> tonne est exacte (aucune conversion implicite)."
    )


def ecart_unitaire_exact(
    prix_provisoire: int, unite_provisoire: str, prix_definitif: int, unite_definitif: str
) -> tuple[int, str]:
    """
    Écart unitaire (définitif - provisoire) d'une régularisation, calculé par
    conversion exacte : dans l'unité commune si les deux prix ont la même
    unité, sinon (kg et tonne) dans la tonne, où les deux prix restent des
    entiers exacts. Renvoie (écart en unités minimales, unité de l'écart).
    """
    if not unites_de_prix_compatibles(unite_definitif, unite_provisoire):
        raise UniteValorisationError(
            f"Régularisation : unités {unite_provisoire} et {unite_definitif} incompatibles "
            "(seule la conversion kg <-> tonne est exacte)."
        )
    unite = unite_definitif if unite_definitif == unite_provisoire else "TONNE"
    ecart = convertir_prix_exact(prix_definitif, unite_definitif, unite) - convertir_prix_exact(
        prix_provisoire, unite_provisoire, unite
    )
    assert ecart.denominator == 1  # kg -> tonne multiplie par 1 000 : toujours entier
    return int(ecart), unite


def montant_arrondi_minor(quantite: F, prix_minor: typing.Union[int, F]) -> int:
    """
    Montant final = quantité (exacte) × prix unitaire (exact), arrondi UNE
    SEULE FOIS au millime le plus proche, 0,5 vers le haut (règle validée).
    Ex. 1 000,5 kg × 2 501 millimes/kg = 2 502 250,5 -> 2 502 251 millimes.
    """
    return _arrondi(quantite * prix_minor)


# ---------------------------------------------------------------------------
# Unité de valorisation des articles (historique immuable, migration 0019)
# ---------------------------------------------------------------------------


def _historiques_unites(conn: sqlite3.Connection) -> dict[str, list[tuple[str, str, str]]]:
    historiques: dict[str, list[tuple[str, str, str]]] = {}
    for article_id, nature, unite, date_effet in conn.execute(
        "SELECT article_id, nature, unite, date_effet FROM article_unite_valorisation "
        "ORDER BY rowid"
    ):
        historiques.setdefault(article_id, []).append((nature, unite, date_effet))
    return historiques


def _unite_a_l_instant(
    historique: typing.Optional[list[tuple[str, str, str]]], instant: typing.Optional[str]
) -> typing.Optional[str]:
    """
    Unité en vigueur à un instant : le dernier CHANGEMENT dont la date d'effet
    est atteinte, sinon la DEFINITION_INITIALE (valable depuis l'origine de
    l'article). None si aucune unité n'est définie. `instant=None` : unité
    actuelle.
    """
    if not historique:
        return None
    unite: typing.Optional[str] = None
    for nature, valeur, _ in historique:
        if nature == "DEFINITION_INITIALE":
            unite = valeur
    changements = sorted(
        (date_effet, valeur) for nature, valeur, date_effet in historique if nature == "CHANGEMENT"
    )
    for date_effet, valeur in changements:
        if instant is None or date_effet <= instant:
            unite = valeur
    return unite


def unite_valorisation_en_vigueur(
    conn: sqlite3.Connection, article_id: str, instant: typing.Optional[str] = None
) -> typing.Optional[str]:
    """Unité de valorisation de l'article à un instant (actuelle si None) ; None si non définie."""
    historique = _historiques_unites(conn).get(article_id)
    return _unite_a_l_instant(historique, instant)


# ---------------------------------------------------------------------------
# Calcul (pur, sans écriture) et reconstruction du cache
# ---------------------------------------------------------------------------


def _nouveau_pool(unite: str) -> dict:
    return {
        "quantite_totale": 0,
        "poids_kg": F(0),
        "valeur_totale_minor": 0,
        "cmp_unitaire_minor": 0,
        "devise": None,
        "unite_valorisation": unite,
        "unite_cmp": unite,
        "longueur_m": None,
    }


def _quantite_pool(pool: dict, unite: str) -> F:
    return quantite_en_unite(unite, pool["quantite_totale"], pool["poids_kg"], pool["longueur_m"])


def calculer_pools(
    conn: sqlite3.Connection,
    jusqu_au: typing.Optional[str] = None,
    article_id: typing.Optional[str] = None,
) -> tuple[dict[tuple, dict], list[dict]]:
    """
    Rejoue le registre (mouvements touchant STOCK_GMC, datés jusqu'à
    `jusqu_au` inclus si fourni, d'un seul article si `article_id` est
    fourni) SANS rien écrire. Renvoie (pools, lignes d'historique) ; pour
    une sortie, la ligne porte aussi, en mémoire seulement, le CMP EXACT au
    moment de la sortie (`_cmp_exact_au_moment`, fraction non arrondie).
    Lève UniteValorisationError ou ValueError (devise, solde) en cas
    d'incohérence.
    """
    cur = conn.cursor()
    cur.row_factory = sqlite3.Row
    requete = """
        SELECT m.id, m.lot_id, m.type, m.quantite, m.poids_kg,
               m.emplacement_source, m.emplacement_destination, m.date_heure,
               l.article_id, l.finition, l.longueur_m, l.unite_prix, l.unite_prix_definitif,
               l.prix_unitaire_provisoire_minor, l.prix_unitaire_definitif_minor, l.devise
        FROM mouvement_stock m
        JOIN lot l ON l.id = m.lot_id
        WHERE (m.emplacement_source = 'STOCK_GMC' OR m.emplacement_destination = 'STOCK_GMC')
    """
    parametres: list = []
    if jusqu_au is not None:
        requete += " AND m.date_heure <= ?"
        parametres.append(jusqu_au)
    if article_id is not None:
        requete += " AND l.article_id = ?"
        parametres.append(article_id)
    mouvements = cur.execute(requete + " ORDER BY m.date_heure, m.rowid", parametres).fetchall()
    historiques = _historiques_unites(conn)

    pools: dict[tuple, dict] = {}
    lignes: list[dict] = []
    for mv in mouvements:
        key = (mv["article_id"], mv["finition"], mv["longueur_m"])
        unite = _unite_a_l_instant(historiques.get(mv["article_id"]), mv["date_heure"])
        if unite is None:
            raise UniteValorisationError(
                f"Unité de valorisation non définie pour l'article {mv['article_id']} : "
                "le CMP ne peut pas être calculé (aucune unité n'est supposée par défaut). "
                "Elle doit être définie pour cet article."
            )
        pool = pools.setdefault(key, _nouveau_pool(unite))
        pool["longueur_m"] = mv["longueur_m"]
        pool["unite_valorisation"] = unite
        montant_mouvement_minor = 0
        cmp_au_moment: typing.Optional[int] = None
        cmp_exact_au_moment: typing.Optional[F] = None

        if mv["emplacement_destination"] == "STOCK_GMC":
            # Coût d'entrée = COALESCE(prix facturé définitif, prix BL provisoire) du lot
            # (Phase 4.1 §1 : dès que le prix définitif est renseigné — régularisation
            # APPLIQUE_AU_LOT — il remplace entièrement le provisoire ; un lot déjà sorti
            # suit ECART_SEPARE et son prix définitif n'est jamais renseigné).
            cout_entree_minor = mv["prix_unitaire_definitif_minor"]
            unite_cout = mv["unite_prix_definitif"]
            if cout_entree_minor is None:
                cout_entree_minor = mv["prix_unitaire_provisoire_minor"]
                unite_cout = mv["unite_prix"]
            devise_mouvement = mv["devise"] or "TND"
            if devise_mouvement not in DEVISES_VALIDES:
                raise ValueError(f"Devise inconnue '{devise_mouvement}' pour le lot {mv['lot_id']}")
            if pool["devise"] is None:
                pool["devise"] = devise_mouvement
            elif pool["devise"] != devise_mouvement:
                raise ValueError(
                    f"Incohérence de devise sur le pool {key} : déjà valorisé en "
                    f"{pool['devise']}, le mouvement {mv['id']} (lot {mv['lot_id']}) apporte "
                    f"un coût en {devise_mouvement}. Un pool CMP ne mélange jamais deux devises "
                    "(Phase 4.1 §2) — ce lot doit constituer un pool séparé ou être re-saisi "
                    "dans la devise du pool."
                )
            if unite_cout not in UNITES_VALORISATION:
                raise UniteValorisationError(
                    f"Le lot {mv['lot_id']} n'a pas d'unité de prix : sa valeur ne peut pas être "
                    "calculée sans supposer une unité."
                )
            # Unité de calcul (D) : quantité exprimée dans l'unité du prix saisi × prix
            # saisi — produit exact, strictement égal à « quantité dans l'unité de
            # valorisation × prix converti exactement » (ex. 1,0003 t × 2 500 500 =
            # 1 000,3 kg × 2 500,5 = 2 501 250,15) ; montant final arrondi une seule fois.
            # (Valable aussi pour un lot antérieur à un changement d'unité de l'article.)
            entree_minor = montant_arrondi_minor(
                quantite_en_unite(unite_cout, mv["quantite"], mv["poids_kg"], mv["longueur_m"]),
                cout_entree_minor,
            )
            pool["quantite_totale"] += mv["quantite"]
            pool["poids_kg"] += _exact(mv["poids_kg"])
            pool["valeur_totale_minor"] += entree_minor
            montant_mouvement_minor += entree_minor

        if mv["emplacement_source"] == "STOCK_GMC":
            qte_avant = pool["quantite_totale"]
            if qte_avant < mv["quantite"]:
                raise ValueError(
                    f"Incohérence CMP : le mouvement {mv['id']} retire {mv['quantite']} "
                    f"du pool {key} qui n'en contient que {qte_avant}"
                )
            quantite_pool = _quantite_pool(pool, unite)
            quantite_sortie = quantite_en_unite(
                unite, mv["quantite"], mv["poids_kg"], mv["longueur_m"]
            )
            valeur = pool["valeur_totale_minor"]
            if quantite_pool > 0:
                cmp_exact_au_moment = F(valeur) / quantite_pool  # exact, jamais arrondi
                cmp_au_moment = _arrondi(cmp_exact_au_moment)  # affichage
            if qte_avant == mv["quantite"]:
                # Le pool est vidé physiquement : toute sa valeur sort (aucun résidu).
                montant_sortie_minor = valeur
            elif quantite_pool > 0:
                # Retrait proportionnel EXACT sur le total courant, dans l'unité en vigueur
                # (au poids pour KG/TONNE, au métrage/à la pièce pour ML/UNITE).
                montant_sortie_minor = min(
                    valeur, _arrondi(valeur * quantite_sortie / quantite_pool)
                )
            else:
                montant_sortie_minor = 0
            pool["valeur_totale_minor"] -= montant_sortie_minor
            pool["quantite_totale"] -= mv["quantite"]
            pool["poids_kg"] -= _exact(mv["poids_kg"])
            if pool["quantite_totale"] == 0:
                pool["valeur_totale_minor"] = 0
                pool["poids_kg"] = F(0)
            elif pool["poids_kg"] < 0:
                pool["poids_kg"] = F(0)
            montant_mouvement_minor -= montant_sortie_minor

        quantite_apres = _quantite_pool(pool, unite)
        if quantite_apres > 0:
            pool["cmp_unitaire_minor"] = _arrondi(F(pool["valeur_totale_minor"]) / quantite_apres)
            pool["unite_cmp"] = unite
        elif cmp_au_moment is not None:
            # Pool vidé par cette sortie : on conserve le CMP au moment de la sortie
            # (une moyenne pondérée ne change pas quand on retire à son propre prix
            # moyen), exprimé dans l'unité en vigueur — c'est la valeur que
            # cout_sortie_*()/cout_chute_*() lisent pour « le CMP au moment de la sortie ».
            pool["cmp_unitaire_minor"] = cmp_au_moment
            pool["unite_cmp"] = unite
        lignes.append(
            {
                "article_id": key[0],
                "finition": key[1],
                "longueur_m": key[2],
                "mouvement_stock_id": mv["id"],
                "unite_valorisation": pool["unite_cmp"],
                "quantite_totale_apres": pool["quantite_totale"],
                "poids_total_apres_kg": float(pool["poids_kg"]),
                "quantite_valorisation_apres": float(quantite_apres),
                "valeur_totale_apres_minor": pool["valeur_totale_minor"],
                "cmp_unitaire_apres_minor": pool["cmp_unitaire_minor"],
                "montant_mouvement_minor": montant_mouvement_minor,
                "devise": pool["devise"] or "TND",
                "date_heure": mv["date_heure"],
                "_cmp_exact_au_moment": cmp_exact_au_moment,
            }
        )

    # État final exprimé dans l'unité en vigueur MAINTENANT (un changement d'unité
    # postérieur au dernier mouvement s'y reflète) ; un pool vide garde son dernier
    # CMP avec l'unité dans laquelle il a été calculé.
    for key, pool in pools.items():
        unite_actuelle = _unite_a_l_instant(historiques.get(key[0]), jusqu_au)
        if unite_actuelle is not None and unite_actuelle != pool["unite_cmp"]:
            quantite = _quantite_pool(pool, unite_actuelle)
            if quantite > 0:
                pool["cmp_unitaire_minor"] = _arrondi(F(pool["valeur_totale_minor"]) / quantite)
                pool["unite_cmp"] = unite_actuelle
        pool["quantite_valorisation"] = _quantite_pool(pool, pool["unite_cmp"])
    return pools, lignes


def _pool_public(pool: dict) -> dict:
    return {
        "quantite_totale": pool["quantite_totale"],
        "poids_total_kg": float(pool["poids_kg"]),
        "unite_valorisation": pool["unite_cmp"],
        "quantite_valorisation": float(pool["quantite_valorisation"]),
        "valeur_totale_minor": pool["valeur_totale_minor"],
        "cmp_unitaire_minor": pool["cmp_unitaire_minor"],
        "devise": pool["devise"] or "TND",
    }


def etat_pools_article(
    conn: sqlite3.Connection, article_id: str, jusqu_au: typing.Optional[str] = None
) -> list[dict]:
    """
    État (sans écriture) des pools d'un article à un instant, avec le CMP
    exprimé dans CHACUNE des unités de valorisation — utilisé pour tracer
    explicitement la conversion lors d'un changement d'unité.
    """
    pools, _ = calculer_pools(conn, jusqu_au, article_id)
    etats = []
    for key, pool in sorted(pools.items(), key=lambda item: (item[0][1], item[0][2])):
        cmp_par_unite = {}
        for unite in UNITES_VALORISATION:
            quantite = _quantite_pool(pool, unite)
            if quantite > 0:
                cmp_par_unite[unite] = _arrondi(F(pool["valeur_totale_minor"]) / quantite)
        etats.append(
            {
                "finition": key[1],
                "longueur_m": key[2],
                "quantite_totale": pool["quantite_totale"],
                "poids_total_kg": float(pool["poids_kg"]),
                "valeur_totale_minor": pool["valeur_totale_minor"],
                "devise": pool["devise"] or "TND",
                "cmp_unitaire_minor_par_unite": cmp_par_unite,
            }
        )
    return etats


def reconstruire_cmp(conn: sqlite3.Connection) -> dict:
    """
    Reconstruit intégralement cmp_stock_general et cmp_historique à partir de
    mouvement_stock (source de vérité exclusive). Idempotent : repart toujours
    de zéro. Le calcul est fait AVANT toute écriture : en cas d'erreur, le
    cache existant n'est pas touché.

    Retourne {(article_id, finition, longueur_m): {"quantite_totale",
    "poids_total_kg", "unite_valorisation", "quantite_valorisation",
    "valeur_totale_minor", "cmp_unitaire_minor", "devise"}}.
    """
    conn.row_factory = sqlite3.Row
    pools, lignes = calculer_pools(conn)
    cur = conn.cursor()
    cur.execute("DELETE FROM cmp_historique")
    cur.execute("DELETE FROM cmp_stock_general")
    for ligne in lignes:
        cur.execute(
            """
            INSERT INTO cmp_historique
                (id, article_id, finition, longueur_m, mouvement_stock_id, unite_valorisation,
                 quantite_totale_apres, poids_total_apres_kg, quantite_valorisation_apres,
                 valeur_totale_apres_minor, cmp_unitaire_apres_minor, montant_mouvement_minor,
                 devise, date_heure)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                ligne["article_id"],
                ligne["finition"],
                ligne["longueur_m"],
                ligne["mouvement_stock_id"],
                ligne["unite_valorisation"],
                ligne["quantite_totale_apres"],
                ligne["poids_total_apres_kg"],
                ligne["quantite_valorisation_apres"],
                ligne["valeur_totale_apres_minor"],
                ligne["cmp_unitaire_apres_minor"],
                ligne["montant_mouvement_minor"],
                ligne["devise"],
                ligne["date_heure"],
            ),
        )
    resultat = {}
    for key, pool in pools.items():
        public = _pool_public(pool)
        cur.execute(
            """
            INSERT INTO cmp_stock_general
                (article_id, finition, longueur_m, unite_valorisation, quantite_totale,
                 poids_total_kg, quantite_valorisation, valeur_totale_minor, cmp_unitaire_minor,
                 devise, derniere_maj)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%f','now'))
            """,
            (
                key[0],
                key[1],
                key[2],
                public["unite_valorisation"],
                public["quantite_totale"],
                public["poids_total_kg"],
                public["quantite_valorisation"],
                public["valeur_totale_minor"],
                public["cmp_unitaire_minor"],
                public["devise"],
            ),
        )
        resultat[key] = public
    conn.commit()
    return resultat


# ---------------------------------------------------------------------------
# Lectures du cache
# ---------------------------------------------------------------------------


def cmp_actuel_minor(
    conn: sqlite3.Connection, article_id: str, finition: str, longueur_m: float
) -> int:
    """CMP courant d'un pool, par unité de valorisation (cf. cmp_actuel()), lu depuis le cache.
    0 si le pool n'existe pas (encore)."""
    row = conn.execute(
        "SELECT cmp_unitaire_minor FROM cmp_stock_general "
        "WHERE article_id=? AND finition=? AND longueur_m=?",
        (article_id, finition, longueur_m),
    ).fetchone()
    return row[0] if row else 0


def cmp_actuel(
    conn: sqlite3.Connection, article_id: str, finition: str, longueur_m: float
) -> typing.Optional[dict]:
    """CMP courant d'un pool AVEC son unité : {cmp_unitaire_minor, unite_valorisation, devise,
    quantite_valorisation, valeur_totale_minor}. None si le pool n'existe pas (encore)."""
    row = conn.execute(
        "SELECT cmp_unitaire_minor, unite_valorisation, devise, quantite_valorisation, "
        "valeur_totale_minor FROM cmp_stock_general "
        "WHERE article_id=? AND finition=? AND longueur_m=?",
        (article_id, finition, longueur_m),
    ).fetchone()
    if row is None:
        return None
    return {
        "cmp_unitaire_minor": row[0],
        "unite_valorisation": row[1],
        "devise": row[2],
        "quantite_valorisation": row[3],
        "valeur_totale_minor": row[4],
    }


def cmp_devise_actuelle(
    conn: sqlite3.Connection, article_id: str, finition: str, longueur_m: float
) -> str | None:
    """Devise du pool CMP courant. None si le pool n'existe pas (encore)."""
    row = conn.execute(
        "SELECT devise FROM cmp_stock_general WHERE article_id=? AND finition=? AND longueur_m=?",
        (article_id, finition, longueur_m),
    ).fetchone()
    return row[0] if row else None


def cmp_au_moment_du_mouvement(conn: sqlite3.Connection, mouvement_stock_id: str) -> int | None:
    """
    CMP figé « au moment de la sortie » (règles 3 et 4), par unité de
    valorisation EN VIGUEUR À CE MOMENT (cf. cmp_au_moment_du_mouvement_detail),
    pour UN mouvement précis : relit cmp_historique, jamais recalculé après
    coup. None si ce mouvement ne touche pas STOCK_GMC ou si le cache n'a pas
    encore été (re)construit.
    """
    detail = cmp_au_moment_du_mouvement_detail(conn, mouvement_stock_id)
    return detail["cmp_unitaire_minor"] if detail else None


def cmp_au_moment_du_mouvement_detail(
    conn: sqlite3.Connection, mouvement_stock_id: str
) -> typing.Optional[dict]:
    """{cmp_unitaire_minor, unite_valorisation, devise} figés pour ce mouvement, ou None."""
    row = conn.execute(
        "SELECT cmp_unitaire_apres_minor, unite_valorisation, devise FROM cmp_historique "
        "WHERE mouvement_stock_id = ?",
        (mouvement_stock_id,),
    ).fetchone()
    if row is None:
        return None
    return {"cmp_unitaire_minor": row[0], "unite_valorisation": row[1], "devise": row[2]}


def montant_mouvement_minor(conn: sqlite3.Connection, mouvement_stock_id: str) -> int | None:
    """
    Valeur EXACTE (signée) dont ce mouvement précis a fait varier le pool CMP :
    positive pour une entrée, négative pour une sortie. Relue telle quelle
    depuis cmp_historique — jamais recalculée après coup. None si ce
    mouvement ne touche pas STOCK_GMC ou si le cache n'a pas encore été
    (re)construit.
    """
    row = conn.execute(
        "SELECT montant_mouvement_minor FROM cmp_historique WHERE mouvement_stock_id = ?",
        (mouvement_stock_id,),
    ).fetchone()
    return row[0] if row else None


def type_affectation_pour_mouvement(
    conn: sqlite3.Connection, mouvement_stock_id: str
) -> str | None:
    """'INITIALE' / 'SUPPLEMENT' si ce mouvement clôture une affectation, sinon None."""
    row = conn.execute(
        "SELECT type FROM affectation_stock WHERE mouvement_physique_id = ?",
        (mouvement_stock_id,),
    ).fetchone()
    return row[0] if row else None


# ---------------------------------------------------------------------------
# Coûts de sortie et de chute
# ---------------------------------------------------------------------------


def _lot(conn: sqlite3.Connection, lot_id: str) -> tuple:
    row = conn.execute(
        "SELECT prix_unitaire_provisoire_minor, prix_unitaire_definitif_minor, unite_prix, "
        "longueur_m, unite_prix_definitif, unite_valorisation_article FROM lot WHERE id = ?",
        (lot_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Lot introuvable : {lot_id}")
    return tuple(row)


def cout_reel_lot_minor(conn: sqlite3.Connection, lot_id: str) -> int:
    """
    Coût réel d'un lot (règle 2), tel que SAISI, par unité de son prix
    (cf. unite_cout_reel_lot()), en unité monétaire minimale :
    prix_unitaire_definitif_minor si la régularisation facture a déjà été
    appliquée à ce lot, sinon prix_unitaire_provisoire_minor. Ne passe jamais
    par le CMP. Pour ce coût converti exactement dans une autre unité, voir
    cout_reel_lot_exact().
    """
    provisoire, definitif = _lot(conn, lot_id)[:2]
    return definitif if definitif is not None else provisoire


def unite_cout_reel_lot(conn: sqlite3.Connection, lot_id: str) -> str:
    """Unité du coût réel du lot : celle du prix définitif s'il existe, sinon du provisoire."""
    ligne = _lot(conn, lot_id)
    unite = ligne[4] if ligne[1] is not None else ligne[2]
    if unite not in UNITES_VALORISATION:
        raise UniteValorisationError(f"Le lot {lot_id} n'a pas d'unité de prix.")
    return unite


def cout_reel_lot_exact(conn: sqlite3.Connection, lot_id: str, unite: str) -> F:
    """Coût réel du lot converti EXACTEMENT dans `unite` (fraction, jamais arrondie)."""
    return convertir_prix_exact(
        cout_reel_lot_minor(conn, lot_id), unite_cout_reel_lot(conn, lot_id), unite
    )


def unite_prix_lot(conn: sqlite3.Connection, lot_id: str) -> str:
    """Unité dans laquelle le prix provisoire du lot a été saisi (KG, ML, UNITE ou TONNE)."""
    unite = _lot(conn, lot_id)[2]
    if unite not in UNITES_VALORISATION:
        raise UniteValorisationError(f"Le lot {lot_id} n'a pas d'unité de prix.")
    return unite


def cout_sortie_minor(conn: sqlite3.Connection, mouvement_stock_id: str, lot_id: str) -> int:
    """
    Coût PAR UNITÉ à attribuer à UNE sortie physique donnée, selon les règles 1-3 :
      - liée à une affectation INITIALE -> coût réel du lot (règle 2), par unité du lot ;
      - SUPPLEMENT ou aucune affectation -> CMP au moment de cette sortie (règles 1, 3),
        par unité de valorisation en vigueur à ce moment.
    L'unité correspondante est donnée par cout_sortie_detail(). Pour le MONTANT
    TOTAL exact, voir cout_sortie_total_minor().
    """
    return cout_sortie_detail(conn, mouvement_stock_id, lot_id)["cout_unitaire_minor"]


def cout_sortie_detail(conn: sqlite3.Connection, mouvement_stock_id: str, lot_id: str) -> dict:
    """{cout_unitaire_minor, unite} applicables à une sortie (cf. cout_sortie_minor())."""
    if type_affectation_pour_mouvement(conn, mouvement_stock_id) == "INITIALE":
        return {
            "cout_unitaire_minor": cout_reel_lot_minor(conn, lot_id),
            "unite": unite_cout_reel_lot(conn, lot_id),
        }
    detail = cmp_au_moment_du_mouvement_detail(conn, mouvement_stock_id)
    if detail is None:
        raise ValueError(
            f"CMP indisponible pour le mouvement {mouvement_stock_id} — "
            "reconstruire_cmp() doit être appelé avant tout calcul de coût de sortie."
        )
    return {
        "cout_unitaire_minor": detail["cmp_unitaire_minor"],
        "unite": detail["unite_valorisation"],
    }


def cout_sortie_total_minor(conn: sqlite3.Connection, mouvement_stock_id: str, lot_id: str) -> int:
    """
    Montant TOTAL exact (unité monétaire minimale) à attribuer à UNE sortie
    physique donnée — valeur à écrire dans bl_client_ligne.cout_cmp_total_minor :
      - INITIALE -> quantité sortie dans l'unité du coût réel du lot × ce
                    coût (dans l'unité où il a été saisi : conversion exacte
                    implicite dans le produit), arrondi une seule fois au
                    millime (règle validée) ;
      - SUPPLEMENT / aucune affectation -> montant_mouvement_minor() du pool
                    pour ce mouvement précis (retrait proportionnel exact), PAS
                    « CMP arrondi × quantité ».
    """
    row = conn.execute(
        "SELECT quantite, poids_kg FROM mouvement_stock WHERE id = ?", (mouvement_stock_id,)
    ).fetchone()
    if row is None:
        raise ValueError(f"Mouvement introuvable : {mouvement_stock_id}")
    quantite, poids_kg = row[0], row[1]

    if type_affectation_pour_mouvement(conn, mouvement_stock_id) == "INITIALE":
        longueur_m = _lot(conn, lot_id)[3]
        unite = unite_cout_reel_lot(conn, lot_id)
        return montant_arrondi_minor(
            quantite_en_unite(unite, quantite, poids_kg, longueur_m),
            cout_reel_lot_minor(conn, lot_id),
        )

    montant = montant_mouvement_minor(conn, mouvement_stock_id)
    if montant is None:
        raise ValueError(
            f"CMP indisponible pour le mouvement {mouvement_stock_id} — "
            "reconstruire_cmp() doit être appelé avant tout calcul de coût de sortie."
        )
    return abs(montant)  # négatif pour une sortie (convention signée du ledger)


def _mouvement_envoi_transformation(conn: sqlite3.Connection, chute_id: str) -> str:
    """ID du mouvement SORTIE_TRANSFORMATION d'origine (départ de GMC vers le
    transformateur) dont cette chute est issue — règle 4 : le coût d'une chute
    se fige à CE moment-là, jamais au moment où elle est constatée au retour."""
    row = conn.execute(
        """
        SELECT ms.id
        FROM chute c
        JOIN reception_transformation_ligne rtl ON rtl.id = c.reception_transformation_ligne_id
        JOIN mouvement_stock ms
             ON ms.document_source_type = 'bon_sortie_transformation_ligne'
            AND ms.document_source_id = rtl.bon_sortie_transformation_ligne_id
        WHERE c.id = ?
        """,
        (chute_id,),
    ).fetchone()
    if row is None:
        raise ValueError(
            f"Mouvement SORTIE_TRANSFORMATION introuvable pour la chute {chute_id} "
            "(convention document_source_type/document_source_id non respectée ?)"
        )
    return row[0]


def cout_chute_detail(conn: sqlite3.Connection, chute_id: str) -> dict:
    """
    {cmp_unitaire_minor, unite_valorisation, devise} applicables à une chute
    (règle 4) = CMP au moment où la matière a quitté STOCK_GMC pour la
    transformation, dans l'unité de valorisation en vigueur à ce moment.
    """
    mv_id = _mouvement_envoi_transformation(conn, chute_id)
    detail = cmp_au_moment_du_mouvement_detail(conn, mv_id)
    if detail is None:
        raise ValueError(
            f"CMP indisponible pour la chute {chute_id} — reconstruire_cmp() requis au préalable."
        )
    return detail


def cout_chute_unitaire_minor(conn: sqlite3.Connection, chute_id: str) -> int:
    """CMP (arrondi, affichage) par unité de valorisation applicable à une chute."""
    return cout_chute_detail(conn, chute_id)["cmp_unitaire_minor"]


def cmp_exact_au_moment_du_mouvement(
    conn: sqlite3.Connection, mouvement_stock_id: str
) -> tuple[F, str]:
    """
    CMP EXACT (fraction non arrondie) et unité au moment d'une sortie de
    STOCK_GMC, recalculés depuis le registre (même calcul que le cache) :
    c'est la précision interne conservée avant l'arrondi du montant final.
    """
    ligne_article = conn.execute(
        "SELECT l.article_id FROM mouvement_stock m JOIN lot l ON l.id = m.lot_id WHERE m.id = ?",
        (mouvement_stock_id,),
    ).fetchone()
    if ligne_article is None:
        raise ValueError(f"Mouvement introuvable : {mouvement_stock_id}")
    _, lignes = calculer_pools(conn, article_id=ligne_article[0])
    for ligne in lignes:
        if ligne["mouvement_stock_id"] == mouvement_stock_id:
            if ligne["_cmp_exact_au_moment"] is None:
                break
            return ligne["_cmp_exact_au_moment"], ligne["unite_valorisation"]
    raise ValueError(
        f"Le mouvement {mouvement_stock_id} n'est pas une sortie de STOCK_GMC valorisée."
    )


def cout_chute_total_minor(conn: sqlite3.Connection, chute_id: str) -> int:
    """
    Montant TOTAL à écrire dans chute.cout_cmp_total_minor = quantité de la
    chute dans l'unité de valorisation figée à l'envoi (pièces, ml, kg ou
    tonnes) × CMP EXACT figé à l'envoi (règle 4), arrondi une seule fois au
    millime (règle validée) — jamais « CMP arrondi × quantité ».

    Rappel Phase 4.1 §3 : ce montant N'EST PAS intégré automatiquement à la
    marge individuelle de l'affaire (chute.impact_marge_valide reste à 0) ; il
    alimente uniquement le bilan consolidé annuel (v_bilan_chutes_annuel).
    """
    row = conn.execute(
        "SELECT c.quantite, c.poids_kg, l.longueur_m FROM chute c JOIN lot l ON l.id = c.lot_id "
        "WHERE c.id = ?",
        (chute_id,),
    ).fetchone()
    if row is None:
        raise ValueError(f"Chute introuvable : {chute_id}")
    cout_chute_detail(conn, chute_id)  # exige un cache CMP construit (comme avant)
    cmp_exact, unite = cmp_exact_au_moment_du_mouvement(
        conn, _mouvement_envoi_transformation(conn, chute_id)
    )
    return montant_arrondi_minor(quantite_en_unite(unite, row[0], row[1], row[2]), cmp_exact)


if __name__ == "__main__":
    db_path = pathlib.Path(__file__).resolve().parent / "gmc.db"
    connexion_cli = sqlite3.connect(str(db_path))
    connexion_cli.execute("PRAGMA foreign_keys = ON;")
    resultat_cli = reconstruire_cmp(connexion_cli)
    connexion_cli.close()
    print(f"{len(resultat_cli)} pool(s) CMP reconstruit(s) depuis mouvement_stock.")
    for cle, p in sorted(resultat_cli.items()):
        print(
            f"  {cle} -> qty={p['quantite_totale']} valeur_minor={p['valeur_totale_minor']} "
            f"cmp_minor={p['cmp_unitaire_minor']}/{p['unite_valorisation']} devise={p['devise']}"
        )
