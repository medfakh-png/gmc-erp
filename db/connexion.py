"""
Connexion SQLite centralisée + mécanisme de transaction (Phase 5.2).

Réutilise exactement le comportement déjà validé dans `db/migrate.py`
(`PRAGMA foreign_keys = ON`, `PRAGMA journal_mode = WAL`) — ne le duplique
pas, l'importe directement. Ajoute deux choses, purement infrastructurelles :

  1. la résolution du chemin de base via `core.configuration`, pour
     qu'aucun module appelant n'ait besoin de connaître lui-même le
     chemin de la base ;
  2. `transaction()` : un mécanisme générique de BEGIN/COMMIT/ROLLBACK que
     les futurs services (Phase 5.3+) réutiliseront pour regrouper
     plusieurs écritures en une seule unité atomique.

Aucune logique métier ici : ni règle de stock, ni CMP, ni numérotation, ni
audit métier. Ce module ne fait qu'ouvrir/fermer des connexions et fournir
le mécanisme transactionnel générique.
"""
from __future__ import annotations

import contextlib
import sqlite3
import typing

from core.configuration import Configuration, charger_configuration, obtenir_logger
from db.migrate import get_connection as _get_connection_brute

_log = obtenir_logger("db.connexion")


def get_connection(config: typing.Optional[Configuration] = None) -> sqlite3.Connection:
    """
    Ouvre une connexion vers la base désignée par `config` (ou la
    configuration active résolue depuis l'environnement si `config` est
    omis).

    Le PRAGMA foreign_keys=ON et PRAGMA journal_mode=WAL sont appliqués
    par `db.migrate.get_connection`, réutilisé tel quel — pas de
    duplication de cette logique déjà validée en Phase 4.
    """
    if config is None:
        config = charger_configuration()

    conn = _get_connection_brute(config.db_path)
    _log.debug(
        "Connexion ouverte sur %s (environnement=%s)",
        config.db_path,
        config.environnement,
    )
    return conn


@contextlib.contextmanager
def transaction(conn: sqlite3.Connection) -> typing.Iterator[sqlite3.Connection]:
    """
    Mécanisme technique de transaction : regroupe toutes les écritures
    faites sur `conn` à l'intérieur du bloc `with` en une seule unité
    atomique.

        with transaction(conn) as tx:
            tx.execute(...)
            tx.execute(...)
        # COMMIT automatique si le bloc se termine sans exception.

        with transaction(conn) as tx:
            tx.execute(...)
            raise QuelqueChose(...)
        # ROLLBACK automatique — rien de ce qui a été écrit dans le bloc
        # n'est conservé — et l'exception d'origine est relancée telle
        # quelle (jamais avalée ni remplacée).

    Pure infrastructure : ce mécanisme ne sait rien des opérations
    métier qu'il transporte (pas d'audit, pas de numérotation ici) — ce
    sont les futurs services (Phase 5.3+) qui l'utiliseront pour leurs
    propres séquences d'écritures.
    """
    try:
        yield conn
    except Exception:
        conn.rollback()
        _log.error("Transaction annulée (ROLLBACK) suite à une exception", exc_info=True)
        raise
    else:
        conn.commit()
        _log.debug("Transaction validée (COMMIT)")


def fermer(conn: sqlite3.Connection) -> None:
    """Ferme explicitement une connexion (wrapper fin, pour homogénéité et log)."""
    conn.close()
    _log.debug("Connexion fermée")
