"""
Repository `article` — LECTURE SEULE (Phase 5.5).

Décision validée (Phase 5.5, catalogue articles) : le Stock Service lit les
articles, vérifie leur existence et utilise leurs caractéristiques, mais ne
crée ni ne modifie jamais un article. La création (réservée à Mohamed) et
toute modification (dérogation spéciale, auditée) relèveront d'un futur
service de référentiel articles — ce module n'expose donc volontairement
aucune écriture.
"""

from __future__ import annotations

import sqlite3
import typing

from repositories.base import un_dict


def obtenir(conn: sqlite3.Connection, article_id: str) -> typing.Optional[dict]:
    """L'article (dictionnaire de ses caractéristiques), ou None s'il n'existe pas."""
    return un_dict(
        conn,
        "SELECT id, designation, famille_id, masse_lineique_kg_m, pct_galva, cree_le "
        "FROM article WHERE id = ?",
        (article_id,),
    )
