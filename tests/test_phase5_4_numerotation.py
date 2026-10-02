"""
Tests Phase 5.4 — numérotation documentaire
(`core/numerotation.py` + `repositories/numerotation_repository.py`).

Couvre uniquement le socle transverse livré cette phase : génération
atomique du numéro humain à partir de `compteur_numerotation`. Aucune
règle métier propre à un type de document (devis, commande...) n'est
testée ici — ces documents n'existent pas encore (Phase 5.5+).
"""
from __future__ import annotations

import re
import sqlite3

import pytest

from core import numerotation
from core.configuration import configuration_test
from db import connexion, migrate
from repositories import numerotation_repository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def config_num(tmp_path):
    db_path = tmp_path / "gmc_numerotation_5_4.db"
    migrate.apply_migrations(db_path, fresh=True)
    return configuration_test(db_path)


@pytest.fixture()
def conn_num(config_num):
    conn = connexion.get_connection(config_num)
    conn.row_factory = sqlite3.Row
    yield conn
    connexion.fermer(conn)


# ---------------------------------------------------------------------------
# Format et incrémentation
# ---------------------------------------------------------------------------

def test_premier_numero_pour_un_type_et_une_annee_est_0001(conn_num):
    numero = numerotation.prochain_numero(conn_num, "DEV", annee=2026)
    conn_num.commit()
    assert numero == "DEV-2026-0001"


def test_numero_s_incremente_a_chaque_appel(conn_num):
    numeros = [numerotation.prochain_numero(conn_num, "CMD", annee=2026) for _ in range(3)]
    conn_num.commit()
    assert numeros == ["CMD-2026-0001", "CMD-2026-0002", "CMD-2026-0003"]


def test_format_numero_respecte_le_motif_prefixe_annee_quatre_chiffres(conn_num):
    numero = numerotation.prochain_numero(conn_num, "FAC", annee=2026)
    conn_num.commit()
    assert re.fullmatch(r"FAC-2026-\d{4}", numero)


def test_zero_remplissage_est_un_minimum_pas_un_plafond(conn_num):
    # Force le compteur juste avant 9999 pour vérifier qu'un 5e chiffre
    # n'est ni tronqué ni rejeté.
    conn_num.execute(
        "INSERT INTO compteur_numerotation (type_document, annee, dernier_numero) "
        "VALUES ('BLC', 2026, 9999)"
    )
    conn_num.commit()
    numero = numerotation.prochain_numero(conn_num, "BLC", annee=2026)
    conn_num.commit()
    assert numero == "BLC-2026-10000"


# ---------------------------------------------------------------------------
# Isolation des compteurs
# ---------------------------------------------------------------------------

def test_compteurs_independants_par_type_document(conn_num):
    dev = numerotation.prochain_numero(conn_num, "DEV", annee=2026)
    cmd = numerotation.prochain_numero(conn_num, "CMD", annee=2026)
    conn_num.commit()
    assert dev == "DEV-2026-0001"
    assert cmd == "CMD-2026-0001"


def test_compteurs_independants_par_annee(conn_num):
    n_2025 = numerotation.prochain_numero(conn_num, "DEV", annee=2025)
    n_2026 = numerotation.prochain_numero(conn_num, "DEV", annee=2026)
    n_2025_bis = numerotation.prochain_numero(conn_num, "DEV", annee=2025)
    conn_num.commit()
    assert n_2025 == "DEV-2025-0001"
    assert n_2026 == "DEV-2026-0001"
    assert n_2025_bis == "DEV-2025-0002"


# ---------------------------------------------------------------------------
# Année par défaut
# ---------------------------------------------------------------------------

def test_annee_par_defaut_est_l_annee_civile_courante(conn_num):
    import datetime

    annee_attendue = datetime.date.today().year
    numero = numerotation.prochain_numero(conn_num, "DEV")
    conn_num.commit()
    assert numero == f"DEV-{annee_attendue}-0001"


# ---------------------------------------------------------------------------
# Validation du type de document
# ---------------------------------------------------------------------------

def test_type_document_invalide_leve_valueerror_avant_tout_acces_base(conn_num):
    with pytest.raises(ValueError):
        numerotation.prochain_numero(conn_num, "XYZ", annee=2026)

    # Aucune ligne ne doit avoir été créée pour ce type invalide.
    ligne = conn_num.execute(
        "SELECT COUNT(*) FROM compteur_numerotation WHERE type_document = 'XYZ'"
    ).fetchone()
    assert ligne[0] == 0


@pytest.mark.parametrize("type_document", numerotation.TYPES_DOCUMENT_VALIDES)
def test_chaque_type_valide_est_accepte(conn_num, type_document):
    numero = numerotation.prochain_numero(conn_num, type_document, annee=2026)
    conn_num.commit()
    assert numero == f"{type_document}-2026-0001"


def test_dix_types_valides_exactement(conn_num):
    # Garde-fou : la liste doit correspondre exactement aux 10 types
    # confirmés dans docs/BUSINESS_RULES.md et le commentaire de
    # migrations/0002_numerotation.sql — ni plus, ni moins.
    assert set(numerotation.TYPES_DOCUMENT_VALIDES) == {
        "DEV", "CMD", "BCF", "BLF", "FFO", "BCT", "BST", "RTR", "BLC", "FAC",
    }
    assert len(numerotation.TYPES_DOCUMENT_VALIDES) == 10


# ---------------------------------------------------------------------------
# Atomicité et intégration avec le mécanisme de transaction (Phase 5.2)
# ---------------------------------------------------------------------------

def test_numero_confirme_apres_commit_n_est_jamais_redonne(conn_num):
    with connexion.transaction(conn_num):
        numero_1 = numerotation.prochain_numero(conn_num, "DEV", annee=2026)

    with connexion.transaction(conn_num):
        numero_2 = numerotation.prochain_numero(conn_num, "DEV", annee=2026)

    assert numero_1 == "DEV-2026-0001"
    assert numero_2 == "DEV-2026-0002"


def test_rollback_annule_l_incrementation_le_numero_est_redonne(conn_num):
    """
    Test décisif : si la transaction qui a demandé un numéro échoue et
    est annulée, le numéro n'est jamais "brûlé" — le prochain appel
    obtient exactement le même numéro que la tentative annulée.
    """
    class ErreurTest(Exception):
        pass

    with pytest.raises(ErreurTest):
        with connexion.transaction(conn_num):
            numero_tentative = numerotation.prochain_numero(conn_num, "CMD", annee=2026)
            assert numero_tentative == "CMD-2026-0001"
            raise ErreurTest("simulation d'échec après numérotation")

    # Le compteur n'a pas bougé : la ligne n'existe même pas encore.
    assert numerotation.dernier_numero_attribue(conn_num, "CMD", 2026) == 0

    with connexion.transaction(conn_num):
        numero_reel = numerotation.prochain_numero(conn_num, "CMD", annee=2026)

    assert numero_reel == "CMD-2026-0001"


def test_numerotation_partage_la_transaction_d_une_autre_ecriture(conn_num):
    """
    Preuve que prochain_numero() n'ouvre pas sa propre transaction : un
    rollback déclenché par une écriture métier annule aussi
    l'incrémentation du compteur faite juste avant, dans le même bloc.
    """
    conn_num.execute(
        "CREATE TABLE IF NOT EXISTS test_infra_scratch (id INTEGER PRIMARY KEY)"
    )
    conn_num.commit()

    class ErreurTest(Exception):
        pass

    with pytest.raises(ErreurTest):
        with connexion.transaction(conn_num):
            numerotation.prochain_numero(conn_num, "FAC", annee=2026)
            conn_num.execute("INSERT INTO test_infra_scratch (id) VALUES (1)")
            raise ErreurTest("simulation d'échec après les deux écritures")

    assert numerotation.dernier_numero_attribue(conn_num, "FAC", 2026) == 0
    compte = conn_num.execute("SELECT COUNT(*) FROM test_infra_scratch").fetchone()[0]
    assert compte == 0


# ---------------------------------------------------------------------------
# Lecture seule
# ---------------------------------------------------------------------------

def test_dernier_numero_attribue_ne_modifie_rien(conn_num):
    numerotation.prochain_numero(conn_num, "DEV", annee=2026)
    conn_num.commit()

    avant = numerotation.dernier_numero_attribue(conn_num, "DEV", 2026)
    apres = numerotation.dernier_numero_attribue(conn_num, "DEV", 2026)

    assert avant == apres == 1


def test_dernier_numero_attribue_renvoie_zero_si_aucun_numero_donne(conn_num):
    assert numerotation.dernier_numero_attribue(conn_num, "BST", 2026) == 0


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------

def test_repository_incrementer_et_obtenir_cree_la_ligne_si_absente(conn_num):
    valeur = numerotation_repository.incrementer_et_obtenir(conn_num, "RTR", 2026)
    conn_num.commit()
    assert valeur == 1

    ligne = conn_num.execute(
        "SELECT dernier_numero FROM compteur_numerotation "
        "WHERE type_document = 'RTR' AND annee = 2026"
    ).fetchone()
    assert ligne["dernier_numero"] == 1


def test_repository_obtenir_lecture_seule(conn_num):
    numerotation_repository.incrementer_et_obtenir(conn_num, "BLF", 2026)
    conn_num.commit()

    ligne = numerotation_repository.obtenir(conn_num, "BLF", 2026)
    assert ligne["dernier_numero"] == 1

    absente = numerotation_repository.obtenir(conn_num, "BLF", 2099)
    assert absente is None
