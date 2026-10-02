#!/usr/bin/env python3
"""
Exécuteur de migrations pour la base GMC (SQLite).

Usage :
    python3 db/migrate.py [--db chemin/vers/gmc.db] [--fresh]

--fresh supprime la base existante avant de tout reconstruire depuis zéro
(sert à prouver la reproductibilité, cf. Phase 4 §7.5/§7.6).

Chaque fichier migrations/NNNN_*.sql est appliqué une seule fois, dans l'ordre
numérique, et enregistré dans la table schema_migrations. Ré-exécuter le script
sur une base déjà à jour ne fait rien (idempotent).
"""
import argparse
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MIGRATIONS_DIR = ROOT / "migrations"
DEFAULT_DB = ROOT / "db" / "gmc.db"


def get_connection(db_path: pathlib.Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            filename    TEXT PRIMARY KEY,
            applied_le  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
        )
        """
    )
    conn.commit()


def already_applied(conn: sqlite3.Connection) -> set:
    return {row[0] for row in conn.execute("SELECT filename FROM schema_migrations")}


def apply_migrations(db_path: pathlib.Path, fresh: bool = False) -> list:
    if fresh and db_path.exists():
        db_path.unlink()
        for suffix in ("-wal", "-shm"):
            side = pathlib.Path(str(db_path) + suffix)
            if side.exists():
                side.unlink()

    conn = get_connection(db_path)
    ensure_migrations_table(conn)
    applied_before = already_applied(conn)

    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        raise SystemExit(f"Aucun fichier de migration trouvé dans {MIGRATIONS_DIR}")

    newly_applied = []
    for f in files:
        if f.name in applied_before:
            continue
        sql = f.read_text(encoding="utf-8")
        try:
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES (?)", (f.name,)
            )
            conn.commit()
            newly_applied.append(f.name)
        except sqlite3.Error as exc:
            conn.rollback()
            raise SystemExit(f"Échec de la migration {f.name} : {exc}") from exc

    conn.close()
    return newly_applied


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=pathlib.Path, default=DEFAULT_DB)
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    args.db.parent.mkdir(parents=True, exist_ok=True)
    applied = apply_migrations(args.db, fresh=args.fresh)

    if applied:
        print(f"{len(applied)} migration(s) appliquée(s) sur {args.db} :")
        for name in applied:
            print(f"  - {name}")
    else:
        print(f"Base {args.db} déjà à jour, aucune migration à appliquer.")
