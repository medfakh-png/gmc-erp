"""
Repository pour `journal_audit` (Phase 5.3).

Accès SQL structuré, sans logique métier : insertion et lecture de lignes
d'audit. Ne décide jamais si une action doit être auditée, ni ne valide
le type d'action — c'est le rôle du service d'audit (`core/audit.py`),
qui appelle ce repository.

`journal_audit` est totalement immuable en base (triggers
`trg_journal_audit_no_delete` / `trg_journal_audit_no_update`) : ce
module n'expose donc volontairement ni mise à jour ni suppression.
"""
from __future__ import annotations

import sqlite3
import typing

from repositories.base import executer, tous, un_ou_aucun


def inserer(
    conn: sqlite3.Connection,
    *,
    id: str,
    utilisateur_id: str,
    action: str,
    entite_type: str,
    entite_id: str,
    affaire_id: typing.Optional[str] = None,
    valeur_avant: typing.Optional[str] = None,
    valeur_apres: typing.Optional[str] = None,
    motif: typing.Optional[str] = None,
) -> None:
    """Insère une ligne dans `journal_audit`."""
    executer(
        conn,
        """
        INSERT INTO journal_audit
            (id, utilisateur_id, action, entite_type, entite_id, affaire_id,
             valeur_avant, valeur_apres, motif)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id,
            utilisateur_id,
            action,
            entite_type,
            entite_id,
            affaire_id,
            valeur_avant,
            valeur_apres,
            motif,
        ),
    )


def obtenir(conn: sqlite3.Connection, id: str):
    """Une ligne d'audit par identifiant (None si absente)."""
    return un_ou_aucun(conn, "SELECT * FROM journal_audit WHERE id = ?", (id,))


def lister_pour_entite(conn: sqlite3.Connection, entite_type: str, entite_id: str) -> list:
    """Historique d'audit d'une entité précise, du plus ancien au plus récent."""
    return tous(
        conn,
        """
        SELECT * FROM journal_audit
        WHERE entite_type = ? AND entite_id = ?
        ORDER BY date_heure ASC
        """,
        (entite_type, entite_id),
    )


def lister_pour_affaire(conn: sqlite3.Connection, affaire_id: str) -> list:
    """Historique d'audit d'une affaire précise, du plus ancien au plus récent."""
    return tous(
        conn,
        "SELECT * FROM journal_audit WHERE affaire_id = ? ORDER BY date_heure ASC",
        (affaire_id,),
    )
