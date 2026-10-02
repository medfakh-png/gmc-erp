"""
Configuration centralisée de l'application GMC (Phase 5.2).

Objectif : un seul endroit qui connaît le chemin de la base SQLite,
l'environnement d'exécution et les paramètres techniques de logging — pour
qu'aucun autre module (connexion, futurs repositories, futurs services)
n'ait besoin de connaître directement ces détails.

    Configuration
        ↓
    connexion DB
        ↓
    repositories (Phase 5.3+)
        ↓
    services (Phase 5.3+)

Aucune logique métier ici. Ce module ne connaît aucune règle GMC (stock,
CMP, affaires, etc.) — uniquement des paramètres techniques.
"""
from __future__ import annotations

import dataclasses
import logging
import os
import pathlib
import typing

# Racine du projet, calculée depuis l'emplacement de ce fichier — jamais
# depuis le répertoire courant du processus (cf. Phase 5.2 §4/§10 :
# "absence de dépendance au répertoire courant si cela peut être évité").
ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = ROOT / "db" / "gmc.db"

ENVIRONNEMENTS_VALIDES = ("development", "test", "production")
NIVEAUX_LOG_VALIDES = ("DEBUG", "INFO", "WARNING", "ERROR")

_LOGGER_RACINE = "gmc"


@dataclasses.dataclass(frozen=True)
class Configuration:
    """
    Paramètres techniques d'exécution de l'application. Immuable
    (frozen=True) : une configuration ne se modifie pas après coup, on en
    construit une nouvelle.

    Ne contient que des paramètres techniques — jamais une règle métier
    (pas de taux de change, pas de seuil MACF, etc.).
    """

    db_path: pathlib.Path
    environnement: str = "development"
    niveau_log: str = "INFO"
    destination_log: typing.Optional[pathlib.Path] = None  # None = console
    foreign_keys: bool = True
    journal_mode: str = "WAL"

    def __post_init__(self) -> None:
        if self.environnement not in ENVIRONNEMENTS_VALIDES:
            raise ValueError(
                f"Environnement invalide : {self.environnement!r} "
                f"(attendu parmi {ENVIRONNEMENTS_VALIDES})"
            )
        if self.niveau_log not in NIVEAUX_LOG_VALIDES:
            raise ValueError(
                f"Niveau de log invalide : {self.niveau_log!r} "
                f"(attendu parmi {NIVEAUX_LOG_VALIDES})"
            )


def configuration_par_defaut() -> Configuration:
    """Configuration de développement — pointe vers la base réelle du projet."""
    return Configuration(db_path=DEFAULT_DB_PATH, environnement="development", niveau_log="INFO")


def configuration_test(db_path: pathlib.Path) -> Configuration:
    """
    Configuration pour les tests automatisés.

    Le chemin de base est toujours fourni explicitement par l'appelant
    (typiquement le `tmp_path` de pytest) — jamais deviné — pour qu'un
    test ne puisse jamais toucher accidentellement `db/gmc.db`.
    """
    return Configuration(db_path=db_path, environnement="test", niveau_log="DEBUG")


def charger_configuration() -> Configuration:
    """
    Résout la configuration active depuis l'environnement d'exécution.

    Variables reconnues (toutes optionnelles) :
      - GMC_ENV        : 'development' (défaut), 'test' ou 'production'
      - GMC_DB_PATH     : chemin de la base SQLite (défaut : db/gmc.db du projet)
      - GMC_LOG_LEVEL   : DEBUG / INFO / WARNING / ERROR (défaut : INFO)
      - GMC_LOG_FILE    : fichier de destination des logs (défaut : console)

    Ne dépend jamais du répertoire courant du processus : le chemin par
    défaut (DEFAULT_DB_PATH) est calculé depuis l'emplacement de ce
    fichier, pas depuis `os.getcwd()`.
    """
    environnement = os.environ.get("GMC_ENV", "development")
    if environnement not in ENVIRONNEMENTS_VALIDES:
        raise ValueError(
            f"GMC_ENV={environnement!r} invalide (attendu parmi {ENVIRONNEMENTS_VALIDES})"
        )

    db_path_env = os.environ.get("GMC_DB_PATH")
    db_path = pathlib.Path(db_path_env) if db_path_env else DEFAULT_DB_PATH

    niveau_log = os.environ.get("GMC_LOG_LEVEL", "INFO").upper()

    destination_env = os.environ.get("GMC_LOG_FILE")
    destination_log = pathlib.Path(destination_env) if destination_env else None

    return Configuration(
        db_path=db_path,
        environnement=environnement,
        niveau_log=niveau_log,
        destination_log=destination_log,
    )


def configurer_logging(config: Configuration) -> logging.Logger:
    """
    Initialise le logger technique racine de l'application ('gmc').

    Ceci est un logging *technique* (diagnostic), pas la traçabilité
    métier : `journal_audit` (table dédiée, Phase 5.3+) reste l'unique
    source de vérité pour l'audit des actions métier. Cette séparation est
    volontaire (cf. Phase 5.2 §7) et ne doit jamais être confondue :

        logging       = diagnostic technique (ce module)
        journal_audit = traçabilité métier (Phase 5.3+)

    Idempotent : peut être appelé plusieurs fois (ex. une fois par test)
    sans accumuler de handlers dupliqués.
    """
    logger = logging.getLogger(_LOGGER_RACINE)
    logger.setLevel(config.niveau_log)

    for ancien_handler in list(logger.handlers):
        logger.removeHandler(ancien_handler)
        ancien_handler.close()

    formatteur = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    handler: logging.Handler
    if config.destination_log is not None:
        config.destination_log.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(config.destination_log, encoding="utf-8")
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatteur)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


def obtenir_logger(nom: typing.Optional[str] = None) -> logging.Logger:
    """
    Renvoie un logger technique rattaché au logger racine 'gmc'.

    `obtenir_logger("db.connexion")` renvoie le logger `gmc.db.connexion`.
    Ne configure rien (pas de handler) — c'est `configurer_logging()` qui
    fait ce travail une fois, en général au démarrage de l'application ou
    en tête de test.
    """
    if nom:
        return logging.getLogger(f"{_LOGGER_RACINE}.{nom}")
    return logging.getLogger(_LOGGER_RACINE)
