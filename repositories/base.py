"""
Base commune aux repositories (Phase 5.3).

Un repository = un module fin qui exécute du SQL nommé pour un agrégat
donné et traduit les erreurs SQLite en erreurs métier lisibles. Pas
d'ORM, pas de logique métier — uniquement de l'accès aux données,
structuré et cohérent.

Ce module ne contient que des aides génériques, réutilisées par chaque
repository concret (ex. `repositories/audit_repository.py`). Les
repositories propres à chaque agrégat métier (lot, mouvement_stock,
commande_client, ...) seront ajoutés au fil des Phases 5.5+, par le futur
service qui en a réellement besoin — ils ne sont pas anticipés ici, pour
ne pas figer des choix qui appartiennent à ces futures phases.
"""
from __future__ import annotations

import sqlite3
import typing

from core.erreurs import traduire_erreur_sqlite


def executer(
    conn: sqlite3.Connection, sql: str, params: typing.Sequence = ()
) -> sqlite3.Cursor:
    """
    Exécute une requête d'écriture (INSERT/UPDATE/DELETE).

    Toute `sqlite3.IntegrityError` (typiquement un trigger qui rejette
    l'opération) est traduite en `ErreurMetier` exploitable — jamais un
    message SQLite brut ne doit remonter jusqu'à l'appelant.
    """
    try:
        return conn.execute(sql, params)
    except sqlite3.IntegrityError as exc:
        raise traduire_erreur_sqlite(exc) from exc


def executer_et_retourner(
    conn: sqlite3.Connection, sql: str, params: typing.Sequence = ()
):
    """
    Exécute une requête d'écriture qui se termine par une clause
    `RETURNING` (ex. un upsert qui renvoie la valeur mise à jour) et
    renvoie la ligne produite. Même traduction d'erreur que `executer()`.
    """
    try:
        return conn.execute(sql, params).fetchone()
    except sqlite3.IntegrityError as exc:
        raise traduire_erreur_sqlite(exc) from exc


def un_ou_aucun(
    conn: sqlite3.Connection, sql: str, params: typing.Sequence = ()
):
    """Exécute une requête de lecture et renvoie au plus une ligne (None si aucune)."""
    return conn.execute(sql, params).fetchone()


def tous(conn: sqlite3.Connection, sql: str, params: typing.Sequence = ()) -> list:
    """Exécute une requête de lecture et renvoie toutes les lignes."""
    return conn.execute(sql, params).fetchall()


def un_dict(
    conn: sqlite3.Connection, sql: str, params: typing.Sequence = ()
) -> typing.Optional[dict]:
    """
    Lecture d'au plus une ligne, renvoyée sous forme de dictionnaire
    {nom de colonne: valeur} — indépendant du `row_factory` de la connexion
    fournie par l'appelant (Phase 5.5).
    """
    curseur = conn.execute(sql, params)
    ligne = curseur.fetchone()
    if ligne is None:
        return None
    noms = [description[0] for description in curseur.description]
    return dict(zip(noms, tuple(ligne)))


def des_dicts(conn: sqlite3.Connection, sql: str, params: typing.Sequence = ()) -> list[dict]:
    """Lecture de toutes les lignes, chacune sous forme de dictionnaire (voir `un_dict`)."""
    curseur = conn.execute(sql, params)
    noms = [description[0] for description in curseur.description]
    return [dict(zip(noms, tuple(ligne))) for ligne in curseur.fetchall()]
