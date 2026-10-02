"""
Repository `article_unite_valorisation` (Phase 5.5, migration 0019) —
historique IMMUABLE de l'unité de valorisation de chaque article.

Accès SQL uniquement, sans logique métier : les règles (unité obligatoire,
aucune unité par défaut, changement motivé et non rétroactif) sont portées
par `services/unite_valorisation_service.py` et par les triggers de la base.
"""

from __future__ import annotations

import sqlite3
import typing

from repositories.base import des_dicts, executer, un_dict


def inserer(
    conn: sqlite3.Connection,
    *,
    id: str,
    article_id: str,
    nature: str,
    unite: str,
    unite_precedente: typing.Optional[str],
    date_effet: str,
    motif: typing.Optional[str],
    detail_cmp: typing.Optional[str],
    cree_par: str,
) -> None:
    executer(
        conn,
        """
        INSERT INTO article_unite_valorisation
            (id, article_id, nature, unite, unite_precedente, date_effet, motif, detail_cmp,
             cree_par)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (id, article_id, nature, unite, unite_precedente, date_effet, motif, detail_cmp, cree_par),
    )


def historique(conn: sqlite3.Connection, article_id: str) -> list[dict]:
    """Toutes les lignes de l'article, dans l'ordre d'enregistrement."""
    return des_dicts(
        conn,
        "SELECT id, article_id, nature, unite, unite_precedente, date_effet, motif, detail_cmp, "
        "cree_le, cree_par FROM article_unite_valorisation WHERE article_id = ? ORDER BY rowid",
        (article_id,),
    )


def dernier_changement(conn: sqlite3.Connection, article_id: str) -> typing.Optional[dict]:
    return un_dict(
        conn,
        "SELECT id, unite, unite_precedente, date_effet FROM article_unite_valorisation "
        "WHERE article_id = ? AND nature = 'CHANGEMENT' ORDER BY date_effet DESC, rowid DESC "
        "LIMIT 1",
        (article_id,),
    )


def dernier_mouvement_article(conn: sqlite3.Connection, article_id: str) -> typing.Optional[str]:
    """Date du mouvement de stock le plus récent de l'article (tous lots), ou None."""
    ligne = conn.execute(
        "SELECT MAX(m.date_heure) FROM mouvement_stock m JOIN lot l ON l.id = m.lot_id "
        "WHERE l.article_id = ?",
        (article_id,),
    ).fetchone()
    return ligne[0] if ligne else None
