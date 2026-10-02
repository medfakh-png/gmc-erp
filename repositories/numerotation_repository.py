"""
Repository pour `compteur_numerotation` (Phase 5.4).

Accès SQL structuré à la table de numérotation (en place depuis la
migration `0002_numerotation.sql`, Phase 4) — aucune logique métier ici :
le format du numéro humain et la validation du type de document sont dans
`core/numerotation.py`, pas dans ce module.
"""
from __future__ import annotations

import sqlite3
import typing

from repositories.base import executer_et_retourner, un_ou_aucun


def incrementer_et_obtenir(conn: sqlite3.Connection, type_document: str, annee: int) -> int:
    """
    Incrémente atomiquement le compteur de `type_document`/`annee` (le
    crée à 1 s'il n'existe pas encore pour ce couple type/année) et
    renvoie la nouvelle valeur — une seule instruction SQL (upsert avec
    `RETURNING`), donc jamais deux appels ne peuvent recevoir la même
    valeur, même sans transaction explicite englobante.
    """
    ligne = executer_et_retourner(
        conn,
        """
        INSERT INTO compteur_numerotation (type_document, annee, dernier_numero)
        VALUES (?, ?, 1)
        ON CONFLICT (type_document, annee)
        DO UPDATE SET dernier_numero = dernier_numero + 1
        RETURNING dernier_numero
        """,
        (type_document, annee),
    )
    # Accès positionnel (pas par nom de colonne) : ce module ne doit rien
    # supposer sur le row_factory de la connexion fournie par l'appelant
    # (voir `db/connexion.py`, qui n'en impose aucun).
    return ligne[0]


def obtenir(
    conn: sqlite3.Connection, type_document: str, annee: int
) -> typing.Optional[sqlite3.Row]:
    """Lecture seule, ne modifie rien : la ligne du compteur (None si absente)."""
    return un_ou_aucun(
        conn,
        "SELECT dernier_numero FROM compteur_numerotation WHERE type_document = ? AND annee = ?",
        (type_document, annee),
    )
