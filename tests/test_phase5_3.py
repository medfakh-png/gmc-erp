"""
Tests Phase 5.3 — repositories, hiérarchie d'erreurs métier, service
d'audit, et leur intégration avec le mécanisme de transaction de la
Phase 5.2.

Ces tests ne couvrent aucune règle métier des futurs Stock/Affaire/Achat/
Transformation/Livraison/Facturation Service : uniquement le socle
transverse livré en Phase 5.3 (repositories/base.py,
repositories/audit_repository.py, core/erreurs.py, core/audit.py).
"""
from __future__ import annotations

import json
import re
import sqlite3
import uuid

import pytest

from core import audit
from core.configuration import configuration_test
from core.erreurs import (
    ErreurDeviseMelangee,
    ErreurEnregistrementImmuable,
    ErreurEnregistrementIntrouvable,
    ErreurMetier,
    ErreurPlafondDepasse,
    ErreurReaffectationInvalide,
    ErreurRegleViolee,
    ErreurStockInsuffisant,
    traduire_erreur_sqlite,
)
from db import connexion, migrate
from repositories import audit_repository, base


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def config_infra(tmp_path):
    db_path = tmp_path / "gmc_infra_5_3.db"
    migrate.apply_migrations(db_path, fresh=True)
    return configuration_test(db_path)


@pytest.fixture()
def conn_infra(config_infra):
    conn = connexion.get_connection(config_infra)
    conn.row_factory = sqlite3.Row
    yield conn
    connexion.fermer(conn)


@pytest.fixture()
def utilisateur_id(conn_infra):
    uid = str(uuid.uuid4())
    conn_infra.execute(
        "INSERT INTO utilisateur (id, nom, role, mot_de_passe_hash) VALUES (?, ?, ?, ?)",
        (uid, "Test Infra", "ADMINISTRATEUR", "hash-test"),
    )
    conn_infra.commit()
    return uid


# ---------------------------------------------------------------------------
# Hiérarchie d'erreurs métier
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "classe",
    [
        ErreurStockInsuffisant,
        ErreurPlafondDepasse,
        ErreurReaffectationInvalide,
        ErreurEnregistrementImmuable,
        ErreurDeviseMelangee,
        ErreurEnregistrementIntrouvable,
        ErreurRegleViolee,
    ],
)
def test_toutes_les_erreurs_specifiques_heritent_de_erreur_metier(classe):
    assert issubclass(classe, ErreurMetier)


@pytest.mark.parametrize(
    "fragment,classe_attendue",
    [
        ("trg_mouvement_solde_source", ErreurStockInsuffisant),
        ("trg_affectation_plafond", ErreurPlafondDepasse),
        ("trg_bl_client_ligne_plafond", ErreurPlafondDepasse),
        ("trg_reception_transfo_plafond", ErreurPlafondDepasse),
        ("trg_reaffectation_origine_active", ErreurReaffectationInvalide),
        ("trg_reaffectation_cloture_origine", ErreurReaffectationInvalide),
        ("trg_commande_ligne_qte_immuable", ErreurEnregistrementImmuable),
        ("trg_lot_no_update_quantite", ErreurEnregistrementImmuable),
    ],
)
def test_traduire_erreur_sqlite_reconnait_les_triggers_connus(fragment, classe_attendue):
    exc = sqlite3.IntegrityError(f"CHECK constraint failed: {fragment}")
    resultat = traduire_erreur_sqlite(exc)
    assert isinstance(resultat, classe_attendue)


def test_traduire_erreur_sqlite_no_delete_generique():
    exc = sqlite3.IntegrityError("CHECK constraint failed: trg_lot_no_delete")
    resultat = traduire_erreur_sqlite(exc)
    assert isinstance(resultat, ErreurEnregistrementImmuable)
    assert "suppression" in str(resultat).lower()


def test_traduire_erreur_sqlite_no_update_generique():
    exc = sqlite3.IntegrityError("CHECK constraint failed: trg_mouvement_stock_no_update")
    resultat = traduire_erreur_sqlite(exc)
    assert isinstance(resultat, ErreurEnregistrementImmuable)
    assert "immuable" in str(resultat).lower()


def test_traduire_erreur_sqlite_inconnue_repli_generique_conserve_le_message():
    exc = sqlite3.IntegrityError("FOREIGN KEY constraint failed")
    resultat = traduire_erreur_sqlite(exc)
    assert isinstance(resultat, ErreurRegleViolee)
    assert "FOREIGN KEY constraint failed" in str(resultat)


# ---------------------------------------------------------------------------
# repositories/base.py
# ---------------------------------------------------------------------------

def test_executer_traduit_une_violation_de_check_en_erreur_metier(conn_infra, utilisateur_id):
    with pytest.raises(ErreurMetier):
        base.executer(
            conn_infra,
            """
            INSERT INTO journal_audit (id, utilisateur_id, action, entite_type, entite_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("id-test", utilisateur_id, "ACTION_INEXISTANTE", "test", "1"),
        )


def test_un_ou_aucun_renvoie_none_si_absent(conn_infra):
    resultat = base.un_ou_aucun(
        conn_infra, "SELECT * FROM journal_audit WHERE id = ?", ("absent",)
    )
    assert resultat is None


def test_tous_renvoie_une_liste_vide_si_rien(conn_infra):
    assert base.tous(conn_infra, "SELECT * FROM journal_audit") == []


# ---------------------------------------------------------------------------
# repositories/audit_repository.py
# ---------------------------------------------------------------------------

def test_audit_repository_inserer_et_obtenir(conn_infra, utilisateur_id):
    audit_repository.inserer(
        conn_infra,
        id="a1",
        utilisateur_id=utilisateur_id,
        action="CORRECTION_INVENTAIRE",
        entite_type="test",
        entite_id="123",
        motif="test direct du repository",
    )
    conn_infra.commit()

    ligne = audit_repository.obtenir(conn_infra, "a1")
    assert ligne is not None
    assert ligne["action"] == "CORRECTION_INVENTAIRE"
    assert ligne["motif"] == "test direct du repository"


def test_audit_repository_obtenir_renvoie_none_si_absent(conn_infra):
    assert audit_repository.obtenir(conn_infra, "inexistant") is None


def test_audit_repository_lister_pour_entite_filtre_correctement(conn_infra, utilisateur_id):
    audit_repository.inserer(
        conn_infra, id="a1", utilisateur_id=utilisateur_id, action="CORRECTION_INVENTAIRE",
        entite_type="lot", entite_id="lot-A",
    )
    audit_repository.inserer(
        conn_infra, id="a2", utilisateur_id=utilisateur_id, action="CORRECTION_INVENTAIRE",
        entite_type="lot", entite_id="lot-B",
    )
    conn_infra.commit()

    resultat = audit_repository.lister_pour_entite(conn_infra, "lot", "lot-A")
    assert [r["id"] for r in resultat] == ["a1"]


# ---------------------------------------------------------------------------
# core/audit.py — service d'audit
# ---------------------------------------------------------------------------

def test_enregistrer_rejette_une_action_invalide_sans_toucher_la_db(conn_infra, utilisateur_id):
    with pytest.raises(ValueError):
        audit.enregistrer(
            conn_infra, utilisateur_id=utilisateur_id, action="ACTION_INCONNUE",
            entite_type="test", entite_id="1",
        )
    assert base.tous(conn_infra, "SELECT * FROM journal_audit") == []


def test_enregistrer_serialise_avant_apres_en_json(conn_infra, utilisateur_id):
    id_audit = audit.enregistrer(
        conn_infra, utilisateur_id=utilisateur_id, action="MODIFICATION_PRIX",
        entite_type="lot", entite_id="lot-1",
        avant={"prix_minor": 5000}, apres={"prix_minor": 6000}, motif="test de sérialisation",
    )
    conn_infra.commit()

    ligne = audit_repository.obtenir(conn_infra, id_audit)
    assert json.loads(ligne["valeur_avant"]) == {"prix_minor": 5000}
    assert json.loads(ligne["valeur_apres"]) == {"prix_minor": 6000}


def test_enregistrer_accepte_une_chaine_deja_serialisee(conn_infra, utilisateur_id):
    id_audit = audit.enregistrer(
        conn_infra, utilisateur_id=utilisateur_id, action="MODIFICATION_PRIX",
        entite_type="lot", entite_id="lot-2", avant='{"prix_minor": 1}', apres=None,
    )
    conn_infra.commit()
    ligne = audit_repository.obtenir(conn_infra, id_audit)
    assert ligne["valeur_avant"] == '{"prix_minor": 1}'
    assert ligne["valeur_apres"] is None


def test_historique_entite_ne_renvoie_que_les_lignes_de_cette_entite(conn_infra, utilisateur_id):
    audit.enregistrer(
        conn_infra, utilisateur_id=utilisateur_id, action="CORRECTION_INVENTAIRE",
        entite_type="lot", entite_id="lot-A",
    )
    audit.enregistrer(
        conn_infra, utilisateur_id=utilisateur_id, action="CORRECTION_INVENTAIRE",
        entite_type="lot", entite_id="lot-B",
    )
    conn_infra.commit()

    historique = audit.historique_entite(conn_infra, "lot", "lot-A")
    assert len(historique) == 1
    assert historique[0]["entite_id"] == "lot-A"


def test_historique_affaire_vide_si_aucune_correspondance(conn_infra, utilisateur_id):
    # affaire_id=None ici : aucune affaire réelle n'est créée par ces tests
    # d'infrastructure (voir la note du rapport Phase 5.3 sur ce choix).
    audit.enregistrer(
        conn_infra, utilisateur_id=utilisateur_id, action="CORRECTION_INVENTAIRE",
        entite_type="lot", entite_id="lot-A",
    )
    conn_infra.commit()
    assert audit.historique_affaire(conn_infra, "affaire-inexistante") == []


def test_actions_valides_correspond_exactement_au_check_de_la_base(conn_infra):
    """
    Garde-fou anti-dérive : si une future migration change la liste des
    actions autorisées dans journal_audit.action, ce test échoue tant que
    core.audit.ACTIONS_VALIDES n'est pas mis à jour en conséquence.
    """
    sql = conn_infra.execute(
        "SELECT sql FROM sqlite_master WHERE name = 'journal_audit'"
    ).fetchone()[0]
    match = re.search(r"CHECK \(action IN \(([^)]*)\)\)", sql)
    assert match is not None
    valeurs_en_base = set(re.findall(r"'([A-Z_]+)'", match.group(1)))
    assert valeurs_en_base == set(audit.ACTIONS_VALIDES)


# ---------------------------------------------------------------------------
# Intégration avec db.connexion.transaction (Phase 5.2)
# ---------------------------------------------------------------------------

@pytest.fixture()
def conn_avec_table_scratch(conn_infra):
    conn_infra.execute("CREATE TABLE test_infra_scratch (id INTEGER PRIMARY KEY, valeur TEXT)")
    conn_infra.commit()
    return conn_infra


def test_audit_et_ecriture_metier_partagent_la_meme_transaction(
    conn_avec_table_scratch, utilisateur_id
):
    conn = conn_avec_table_scratch
    with connexion.transaction(conn) as tx:
        tx.execute("INSERT INTO test_infra_scratch (valeur) VALUES (?)", ("écriture simulée",))
        audit.enregistrer(
            tx, utilisateur_id=utilisateur_id, action="CORRECTION_INVENTAIRE",
            entite_type="test_infra_scratch", entite_id="1", motif="test d'intégration 5.3",
        )

    assert len(conn.execute("SELECT * FROM test_infra_scratch").fetchall()) == 1
    assert len(audit.historique_entite(conn, "test_infra_scratch", "1")) == 1


def test_rollback_annule_a_la_fois_l_ecriture_et_l_audit(
    conn_avec_table_scratch, utilisateur_id
):
    conn = conn_avec_table_scratch
    with pytest.raises(RuntimeError):
        with connexion.transaction(conn) as tx:
            tx.execute(
                "INSERT INTO test_infra_scratch (valeur) VALUES (?)",
                ("ne doit pas survivre",),
            )
            audit.enregistrer(
                tx, utilisateur_id=utilisateur_id, action="CORRECTION_INVENTAIRE",
                entite_type="test_infra_scratch", entite_id="2", motif="doit être annulé",
            )
            raise RuntimeError("échec après l'audit")

    assert conn.execute("SELECT * FROM test_infra_scratch").fetchall() == []
    assert audit.historique_entite(conn, "test_infra_scratch", "2") == []
