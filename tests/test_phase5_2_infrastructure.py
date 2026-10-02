"""
Tests d'infrastructure — Phase 5.2 (configuration, connexion, transactions,
logging).

Ces tests ne couvrent AUCUNE règle métier : uniquement le socle technique
créé en Phase 5.2 (`core/configuration.py`, `db/connexion.py`). Les règles
métier restent couvertes par `test_scenarios.py`, `test_contraintes.py` et
`test_phase41.py`, inchangés.
"""
from __future__ import annotations

import logging
import sqlite3

import pytest

from core.configuration import (
    Configuration,
    charger_configuration,
    configuration_par_defaut,
    configuration_test,
    configurer_logging,
    obtenir_logger,
)
from db import connexion, migrate


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def test_configuration_par_defaut_pointe_vers_la_base_du_projet():
    config = configuration_par_defaut()
    assert config.environnement == "development"
    assert config.db_path.name == "gmc.db"
    assert config.db_path.is_absolute()


def test_configuration_test_utilise_le_chemin_fourni(tmp_path):
    db_path = tmp_path / "infra_test.db"
    config = configuration_test(db_path)
    assert config.environnement == "test"
    assert config.db_path == db_path


def test_configuration_rejette_un_environnement_invalide(tmp_path):
    with pytest.raises(ValueError):
        Configuration(db_path=tmp_path / "x.db", environnement="staging")


def test_configuration_rejette_un_niveau_de_log_invalide(tmp_path):
    with pytest.raises(ValueError):
        Configuration(db_path=tmp_path / "x.db", niveau_log="VERBOSE")


def test_charger_configuration_ignore_le_repertoire_courant(monkeypatch, tmp_path):
    """
    charger_configuration() ne doit jamais dépendre du répertoire courant
    du processus — seule une variable d'environnement explicite (ou le
    défaut basé sur l'emplacement du module) doit influencer le résultat.
    """
    monkeypatch.delenv("GMC_DB_PATH", raising=False)
    monkeypatch.delenv("GMC_ENV", raising=False)
    monkeypatch.delenv("GMC_LOG_LEVEL", raising=False)
    monkeypatch.chdir(tmp_path)  # cwd change délibérément
    config = charger_configuration()
    assert config.db_path == configuration_par_defaut().db_path


def test_charger_configuration_respecte_les_variables_environnement(monkeypatch, tmp_path):
    db_path = tmp_path / "surcharge.db"
    monkeypatch.setenv("GMC_ENV", "test")
    monkeypatch.setenv("GMC_DB_PATH", str(db_path))
    monkeypatch.setenv("GMC_LOG_LEVEL", "DEBUG")
    config = charger_configuration()
    assert config.environnement == "test"
    assert config.db_path == db_path
    assert config.niveau_log == "DEBUG"


def test_charger_configuration_rejette_un_gmc_env_invalide(monkeypatch):
    monkeypatch.setenv("GMC_ENV", "staging")
    with pytest.raises(ValueError):
        charger_configuration()


# ---------------------------------------------------------------------------
# Connexion
# ---------------------------------------------------------------------------

@pytest.fixture()
def config_infra(tmp_path):
    db_path = tmp_path / "gmc_infra.db"
    migrate.apply_migrations(db_path, fresh=True)
    return configuration_test(db_path)


def test_get_connection_active_foreign_keys(config_infra):
    conn = connexion.get_connection(config_infra)
    try:
        (valeur,) = conn.execute("PRAGMA foreign_keys").fetchone()
        assert valeur == 1
    finally:
        connexion.fermer(conn)


def test_get_connection_active_wal(config_infra):
    conn = connexion.get_connection(config_infra)
    try:
        (mode,) = conn.execute("PRAGMA journal_mode").fetchone()
        assert mode.lower() == "wal"
    finally:
        connexion.fermer(conn)


def test_get_connection_sans_configuration_utilise_la_configuration_active(
    monkeypatch, config_infra
):
    monkeypatch.setenv("GMC_ENV", "test")
    monkeypatch.setenv("GMC_DB_PATH", str(config_infra.db_path))
    conn = connexion.get_connection()
    try:
        assert conn.execute("SELECT 1").fetchone() == (1,)
    finally:
        connexion.fermer(conn)


def test_fermer_ferme_reellement_la_connexion(config_infra):
    conn = connexion.get_connection(config_infra)
    connexion.fermer(conn)
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

@pytest.fixture()
def conn_infra(config_infra):
    conn = connexion.get_connection(config_infra)
    # Table de test dédiée, jamais une table métier — l'infrastructure ne
    # doit dépendre d'aucune donnée ni règle métier.
    conn.execute("CREATE TABLE test_infra_scratch (id INTEGER PRIMARY KEY, valeur TEXT)")
    conn.commit()
    yield conn
    connexion.fermer(conn)


def test_transaction_commit_sur_succes(conn_infra):
    with connexion.transaction(conn_infra) as tx:
        tx.execute("INSERT INTO test_infra_scratch (valeur) VALUES (?)", ("a",))

    lignes = conn_infra.execute("SELECT valeur FROM test_infra_scratch").fetchall()
    assert [r[0] for r in lignes] == ["a"]


def test_transaction_rollback_sur_exception(conn_infra):
    with pytest.raises(RuntimeError):
        with connexion.transaction(conn_infra) as tx:
            tx.execute("INSERT INTO test_infra_scratch (valeur) VALUES (?)", ("b",))
            raise RuntimeError("échec simulé")

    lignes = conn_infra.execute("SELECT valeur FROM test_infra_scratch").fetchall()
    assert lignes == []  # rien n'a été écrit


def test_transaction_rollback_ne_laisse_aucune_ecriture_partielle(conn_infra):
    with pytest.raises(RuntimeError):
        with connexion.transaction(conn_infra) as tx:
            tx.execute("INSERT INTO test_infra_scratch (valeur) VALUES (?)", ("c1",))
            tx.execute("INSERT INTO test_infra_scratch (valeur) VALUES (?)", ("c2",))
            raise RuntimeError("échec après deux écritures")

    lignes = conn_infra.execute("SELECT valeur FROM test_infra_scratch").fetchall()
    assert lignes == []  # aucune des deux lignes n'a survécu


def test_transaction_propage_exception_d_origine(conn_infra):
    class ErreurSpecifique(Exception):
        pass

    with pytest.raises(ErreurSpecifique):
        with connexion.transaction(conn_infra):
            raise ErreurSpecifique("propagée telle quelle")


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def test_configurer_logging_applique_le_niveau_demande(tmp_path):
    config = Configuration(db_path=tmp_path / "x.db", niveau_log="DEBUG")
    logger = configurer_logging(config)
    assert logger.level == logging.DEBUG


def test_configurer_logging_est_idempotent(tmp_path):
    config = Configuration(db_path=tmp_path / "x.db", niveau_log="INFO")
    configurer_logging(config)
    configurer_logging(config)
    logger = obtenir_logger()
    assert len(logger.handlers) == 1  # pas de handlers dupliqués


def test_configurer_logging_ecrit_dans_le_fichier_demande(tmp_path):
    fichier_log = tmp_path / "gmc.log"
    config = Configuration(
        db_path=tmp_path / "x.db", niveau_log="INFO", destination_log=fichier_log
    )
    logger = configurer_logging(config)
    logger.info("message de test infrastructure")
    for handler in logger.handlers:
        handler.flush()

    assert fichier_log.exists()
    assert "message de test infrastructure" in fichier_log.read_text(encoding="utf-8")


def test_obtenir_logger_enfant_est_rattache_au_logger_racine():
    logger_enfant = obtenir_logger("db.connexion")
    assert logger_enfant.name == "gmc.db.connexion"
