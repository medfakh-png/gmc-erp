"""
Service d'audit (Phase 5.3).

Enregistre les actions sensibles dans `journal_audit` (table immuable,
Phase 4). Ce module ne décide jamais QUAND auditer — c'est au code
appelant (les futurs services métier, Phase 5.5+) de choisir d'appeler
`enregistrer()` au bon moment. Il garantit seulement QUE l'écriture est
correcte : action valide, JSON bien formé, participation à la transaction
en cours.

Important — séparation avec le logging technique (`core/configuration.py`) :

    logging       = diagnostic technique (core/configuration.py)
    journal_audit = traçabilité métier (ce module)

`enregistrer()` n'ouvre jamais sa propre transaction : il exécute un
simple INSERT sur la connexion fournie, pour que l'appelant puisse le
regrouper avec le reste de son opération dans un seul
`db.connexion.transaction(conn)` — un rollback annule alors aussi la
ligne d'audit correspondante, comme prévu en Phase 5.1 (§H) et 5.2 (§16
du cadrage original).
"""
from __future__ import annotations

import json
import sqlite3
import typing
import uuid

from repositories import audit_repository

# Liste des actions valides — reflète exactement le CHECK de
# `journal_audit.action` (migration 0011_audit_alerte.sql). Un test dédié
# (Phase 5.3) vérifie que cette liste ne dérive jamais du schéma réel.
ACTIONS_VALIDES = (
    "REAFFECTATION",
    "QUANTITE_SUPPLEMENTAIRE",
    "CORRECTION_INVENTAIRE",
    "RECEPTION_FOURNISSEUR",
    "RECEPTION_TRANSFORMATION",
    "SORTIE_TRANSFORMATION",
    "SORTIE_LIVRAISON_CLIENT",
    "MODIFICATION_PRIX",
    "REGULARISATION_FACTURE_FOURNISSEUR",
    "DEPASSEMENT_POIDS_VALIDATION",
    "ARBITRAGE_PENURIE",
    "ANNULATION_DOCUMENT",
)


def _serialiser(valeur: typing.Any) -> typing.Optional[str]:
    """
    `None` reste `None`. Une chaîne est supposée déjà sérialisée et est
    conservée telle quelle. Toute autre valeur (dict, list, ...) est
    sérialisée en JSON.
    """
    if valeur is None or isinstance(valeur, str):
        return valeur
    return json.dumps(valeur, ensure_ascii=False, default=str)


def enregistrer(
    conn: sqlite3.Connection,
    *,
    utilisateur_id: str,
    action: str,
    entite_type: str,
    entite_id: str,
    affaire_id: typing.Optional[str] = None,
    avant: typing.Any = None,
    apres: typing.Any = None,
    motif: typing.Optional[str] = None,
) -> str:
    """
    Enregistre une ligne d'audit et renvoie son identifiant (UUID).

    Lève `ValueError` immédiatement (avant tout accès DB) si `action`
    n'est pas une des valeurs autorisées — un message clair plutôt que le
    rejet brut d'une contrainte CHECK SQLite.
    """
    if action not in ACTIONS_VALIDES:
        raise ValueError(
            f"Action d'audit invalide : {action!r} (attendu parmi {ACTIONS_VALIDES})"
        )

    id_audit = str(uuid.uuid4())
    audit_repository.inserer(
        conn,
        id=id_audit,
        utilisateur_id=utilisateur_id,
        action=action,
        entite_type=entite_type,
        entite_id=entite_id,
        affaire_id=affaire_id,
        valeur_avant=_serialiser(avant),
        valeur_apres=_serialiser(apres),
        motif=motif,
    )
    return id_audit


def historique_entite(conn: sqlite3.Connection, entite_type: str, entite_id: str) -> list:
    """Historique d'audit d'une entité précise, du plus ancien au plus récent."""
    return audit_repository.lister_pour_entite(conn, entite_type, entite_id)


def historique_affaire(conn: sqlite3.Connection, affaire_id: str) -> list:
    """Historique d'audit d'une affaire précise, du plus ancien au plus récent."""
    return audit_repository.lister_pour_affaire(conn, affaire_id)
