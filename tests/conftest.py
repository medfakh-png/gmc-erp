import pathlib
import sqlite3
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from db import migrate  # noqa: E402


@pytest.fixture()
def conn(tmp_path):
    """
    Base SQLite fraîchement reconstruite (toutes les migrations, --fresh) pour
    chaque test — aucun état partagé entre tests, conforme à l'exigence de
    reproductibilité (Phase 4 §7.5/§7.6, déjà vérifiée sur db/gmc.db).
    """
    db_path = tmp_path / "test_gmc.db"
    migrate.apply_migrations(db_path, fresh=True)
    c = sqlite3.connect(str(db_path))
    c.execute("PRAGMA foreign_keys = ON;")
    c.row_factory = sqlite3.Row
    yield c
    c.close()
