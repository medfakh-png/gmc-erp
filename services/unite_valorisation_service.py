"""
Unité de valorisation des articles (Phase 5.5 — règle définitive validée
« unité du CMP / coût de revient »).

Règle validée :
- le CMP n'est PAS systématiquement calculé en DT/kg : il est exprimé dans
  l'unité de valorisation de l'article — DT/kg (KG), DT/ml (ML), DT/unité
  (UNITE) ou DT/tonne (TONNE) ;
- cette unité dépend automatiquement de l'unité de produit définie pour
  l'article ; le système n'en impose ni n'en choisit aucune par défaut ;
- elle peut être modifiée selon les règles de changement déjà validées
  (modification d'un article = dérogation de Mohamed, tracée) : l'ancienne
  unité est conservée dans l'historique, la nouvelle est enregistrée, avec
  la date et l'utilisateur ; les historiques de coûts précédents ne sont
  jamais réécrits silencieusement.

Choix techniques signalés (pas des règles métier) :
- l'historique `article_unite_valorisation` (immuable) est lui-même la
  trace d'audit : il porte l'ancienne et la nouvelle unité, la date
  d'effet, l'utilisateur, le motif de la dérogation, et le CMP de chaque
  pool dans l'ancienne ET la nouvelle unité au moment du changement
  (conversion explicite) ;
- la définition initiale vaut depuis l'origine de l'article ; un
  changement prend effet à sa date, jamais dans le futur, et jamais avant
  un mouvement déjà enregistré de l'article (sinon la valorisation de ce
  mouvement serait réécrite) ;
- le contrôle « seul Mohamed » n'est pas encore appliqué techniquement (le
  module de droits relève de la Phase 14) : l'utilisateur et le motif sont
  toujours enregistrés.
"""

from __future__ import annotations

import json
import sqlite3
import typing
import uuid

from core.erreurs import (
    ErreurMotifObligatoire,
    ErreurUniteValorisation,
)
from db import connexion, valorisation
from repositories import unite_valorisation_repository
from services import stock_service

UNITES_VALORISATION = valorisation.UNITES_VALORISATION
LIBELLES = {"KG": "DT/kg", "ML": "DT/ml", "UNITE": "DT/unité", "TONNE": "DT/tonne"}


def _verifier_unite(unite: typing.Any) -> str:
    if unite not in UNITES_VALORISATION:
        raise ErreurUniteValorisation(
            f"Unité de valorisation inconnue : {unite!r} "
            f"(attendu : {', '.join(UNITES_VALORISATION)})."
        )
    return typing.cast(str, unite)


def unite_valorisation(
    conn: sqlite3.Connection, article_id: str, instant: typing.Optional[str] = None
) -> str:
    """
    Unité de valorisation de l'article à un instant (actuelle si None).
    Erreur si aucune n'est définie : aucune unité n'est jamais supposée.
    """
    stock_service.obtenir_article(conn, article_id)
    unite = valorisation.unite_valorisation_en_vigueur(conn, article_id, instant)
    if unite is None:
        raise ErreurUniteValorisation(
            f"Aucune unité de valorisation n'est définie pour l'article {article_id!r} : elle "
            "doit être définie (KG, ML, UNITE ou TONNE) avant tout lot ou toute valorisation."
        )
    return unite


def historique_unite_valorisation(conn: sqlite3.Connection, article_id: str) -> list[dict]:
    """Historique complet (définition initiale puis changements), jamais effacé."""
    lignes = unite_valorisation_repository.historique(conn, article_id)
    for ligne in lignes:
        if ligne["detail_cmp"]:
            ligne["detail_cmp"] = json.loads(ligne["detail_cmp"])
    return lignes


def definir_unite_valorisation(
    conn: sqlite3.Connection, *, article_id: str, unite: str, utilisateur_id: str
) -> str:
    """
    Définition initiale de l'unité de valorisation d'un article (elle vaut
    depuis l'origine de l'article). Transaction complète. Une seconde
    définition est refusée : une modification passe par
    `changer_unite_valorisation()` (dérogation motivée).
    """
    unite = _verifier_unite(unite)
    stock_service.obtenir_article(conn, article_id)
    stock_service.verifier_utilisateur(conn, utilisateur_id)
    actuelle = valorisation.unite_valorisation_en_vigueur(conn, article_id)
    if actuelle is not None:
        raise ErreurUniteValorisation(
            f"L'unité de valorisation de cet article est déjà définie ({LIBELLES[actuelle]}). "
            "La modifier est un changement (dérogation motivée), jamais une nouvelle définition."
        )
    identifiant = str(uuid.uuid4())
    with connexion.transaction(conn):
        unite_valorisation_repository.inserer(
            conn,
            id=identifiant,
            article_id=article_id,
            nature="DEFINITION_INITIALE",
            unite=unite,
            unite_precedente=None,
            date_effet=stock_service.maintenant(),
            motif=None,
            detail_cmp=None,
            cree_par=utilisateur_id,
        )
    return identifiant


def changer_unite_valorisation(
    conn: sqlite3.Connection,
    *,
    article_id: str,
    nouvelle_unite: str,
    utilisateur_id: str,
    motif: str,
    date_heure: typing.Optional[str] = None,
) -> str:
    """
    Changement de l'unité de valorisation d'un article (dérogation motivée).
    Transaction complète, puis reconstruction du cache CMP. L'ancienne unité
    reste dans l'historique ; les lignes CMP antérieures à la date d'effet
    restent exprimées dans l'ancienne unité (jamais réécrites) ; le CMP de
    chaque pool au moment du changement est tracé dans les deux unités.
    """
    nouvelle_unite = _verifier_unite(nouvelle_unite)
    stock_service.obtenir_article(conn, article_id)
    stock_service.verifier_utilisateur(conn, utilisateur_id)
    if motif is None or not str(motif).strip():
        raise ErreurMotifObligatoire(
            "Un changement d'unité de valorisation est une dérogation : le motif est obligatoire."
        )
    ancienne = unite_valorisation(conn, article_id)
    if ancienne == nouvelle_unite:
        raise ErreurUniteValorisation(
            f"L'article est déjà valorisé en {LIBELLES[ancienne]} : aucun changement à enregistrer."
        )
    maintenant = stock_service.maintenant()
    date_effet = (
        stock_service.normaliser_horodatage(date_heure) if date_heure is not None else maintenant
    )
    if date_effet > maintenant:
        raise ErreurUniteValorisation(
            f"Date d'effet {date_effet} dans le futur : un changement d'unité prend effet au "
            "plus tard maintenant."
        )
    precedent = unite_valorisation_repository.dernier_changement(conn, article_id)
    if precedent is not None and precedent["date_effet"] >= date_effet:
        raise ErreurUniteValorisation(
            f"Date d'effet {date_effet} antérieure ou égale au changement précédent "
            f"({precedent['date_effet']})."
        )
    dernier = unite_valorisation_repository.dernier_mouvement_article(conn, article_id)
    if dernier is not None and dernier >= date_effet:
        raise ErreurUniteValorisation(
            f"Changement refusé : un mouvement de stock de cet article est daté du {dernier}, "
            f"après la date d'effet {date_effet}. Sa valorisation serait réécrite "
            "rétroactivement ; le changement doit prendre effet après le dernier mouvement."
        )
    try:
        etats = valorisation.etat_pools_article(conn, article_id, jusqu_au=date_effet)
    except valorisation.UniteValorisationError as exc:
        raise ErreurUniteValorisation(str(exc)) from exc
    detail = [
        {
            "finition": etat["finition"],
            "longueur_m": etat["longueur_m"],
            "quantite_totale": etat["quantite_totale"],
            "poids_total_kg": etat["poids_total_kg"],
            "valeur_totale_minor": etat["valeur_totale_minor"],
            "devise": etat["devise"],
            "cmp_avant": {
                "unite": ancienne,
                "cmp_unitaire_minor": etat["cmp_unitaire_minor_par_unite"].get(ancienne),
            },
            "cmp_apres": {
                "unite": nouvelle_unite,
                "cmp_unitaire_minor": etat["cmp_unitaire_minor_par_unite"].get(nouvelle_unite),
            },
        }
        for etat in etats
    ]
    identifiant = str(uuid.uuid4())
    with connexion.transaction(conn):
        unite_valorisation_repository.inserer(
            conn,
            id=identifiant,
            article_id=article_id,
            nature="CHANGEMENT",
            unite=nouvelle_unite,
            unite_precedente=ancienne,
            date_effet=date_effet,
            motif=str(motif).strip(),
            detail_cmp=json.dumps({"pools": detail}, ensure_ascii=False),
            cree_par=utilisateur_id,
        )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    return identifiant
