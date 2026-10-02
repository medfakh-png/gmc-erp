"""
Tests Phase 5.5 — Stock Service (socle) et inventaire initial de démarrage.

Couvre la liste des tests obligatoires de la validation officielle de
l'analyse Phase 5.5 (§13). Les documents (BL fournisseur, bon de sortie,
réception de transformation, BL client...) sont créés ici par de simples
INSERT, au strict minimum nécessaire : les flux complets appartiennent aux
Phases 5.7 à 5.9 et ne sont PAS implémentés. Seuls les mouvements passent
par le Stock Service.

La connexion de test n'impose volontairement aucun `row_factory` : le
Stock Service doit fonctionner quel que soit le réglage de l'appelant.
"""

from __future__ import annotations

import math
import pathlib
import shutil
import sqlite3

import pytest

from core.configuration import configuration_test
from core.erreurs import (
    ErreurDeviseMelangee,
    ErreurDisponibiliteInsuffisante,
    ErreurDocumentSourceManquant,
    ErreurEmplacementInvalide,
    ErreurEnregistrementImmuable,
    ErreurEnregistrementIntrouvable,
    ErreurMetier,
    ErreurMontantIncoherent,
    ErreurMotifObligatoire,
    ErreurMouvementEnDouble,
    ErreurMouvementIncoherent,
    ErreurInventaireInitialInvalide,
    ErreurPlafondDepasse,
    ErreurQuantiteInvalide,
    ErreurSaisieInvalide,
    ErreurStockInsuffisant,
    ErreurUniteManquante,
    ErreurUniteValorisation,
    traduire_erreur_sqlite,
)
from db import connexion, migrate
from db.valorisation import cmp_actuel_minor
from repositories import base, stock_repository
from services import inventaire_initial_service, stock_service
from tests.helpers import affecter, creer_commande, nid, seed_referentiels, tnd

STOCK = stock_service.STOCK_GMC


# ---------------------------------------------------------------------------
# Fixtures et constructeurs de documents (INSERT minimaux, hors flux complets)
# ---------------------------------------------------------------------------


@pytest.fixture()
def conn(tmp_path):
    db_path = tmp_path / "gmc_stock_5_5.db"
    migrate.apply_migrations(db_path, fresh=True)
    c = connexion.get_connection(configuration_test(db_path))
    yield c
    connexion.fermer(c)


@pytest.fixture()
def ids(conn):
    return seed_referentiels(conn)


def chez(ids) -> str:
    return stock_service.emplacement_transformateur(ids["transformateur"])


def compter(conn, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def bl_fournisseur_et_lot(
    conn, ids, quantite=100, poids=350.0, prix=tnd(5.0), finition="NOIR", longueur=6.0, devise="TND"
):
    """BL fournisseur (1 ligne) + lot issu de cette ligne — SANS mouvement."""
    bl_id, ligne_id, lot_id = nid(), nid(), nid()
    conn.execute(
        "INSERT INTO bl_fournisseur (id, numero, numero_origine_fournisseur, fournisseur_id, "
        "date, statut) "
        "VALUES (?,?,?,?,?,?)",
        (bl_id, f"BLF-2026-{nid()[:8]}", "ORIG-1", ids["fournisseur"], "2026-01-05", "VALIDE"),
    )
    conn.execute(
        "INSERT INTO bl_fournisseur_ligne (id, bl_fournisseur_id, article_id, finition, "
        "longueur_m, "
        "quantite, poids_kg, prix_unitaire_provisoire_minor, devise) VALUES (?,?,?,?,?,?,?,?,?)",
        (ligne_id, bl_id, ids["article"], finition, longueur, quantite, poids, prix, devise),
    )
    conn.execute(
        "INSERT INTO lot (id, article_id, bl_fournisseur_ligne_id, finition, longueur_m, "
        "quantite_initiale, "
        "poids_initial_kg, prix_unitaire_provisoire_minor, devise) VALUES (?,?,?,?,?,?,?,?,?)",
        (lot_id, ids["article"], ligne_id, finition, longueur, quantite, poids, prix, devise),
    )
    conn.commit()
    return {"bl_ligne_id": ligne_id, "lot_id": lot_id}


def receptionner(
    conn,
    ids,
    quantite=100,
    poids=350.0,
    prix=tnd(5.0),
    date_heure="2026-01-05T08:00:00.000",
    **kwargs,
):
    doc = bl_fournisseur_et_lot(conn, ids, quantite, poids, prix, **kwargs)
    with connexion.transaction(conn):
        doc["mouvement_id"] = stock_service.enregistrer_mouvement(
            conn,
            lot_id=doc["lot_id"],
            type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
            quantite=quantite,
            poids_kg=poids,
            emplacement_source=None,
            emplacement_destination=STOCK,
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_fournisseur_ligne",
            document_source_id=doc["bl_ligne_id"],
            date_heure=date_heure,
        )
    return doc


def bon_sortie(conn, ids, lot_id, quantite):
    bct_id, bst_id, bstl_id = nid(), nid(), nid()
    conn.execute(
        "INSERT INTO bon_commande_transformation (id, numero, transformateur_id, date) VALUES "
        "(?,?,?,?)",
        (bct_id, f"BCT-2026-{nid()[:8]}", ids["transformateur"], "2026-02-01"),
    )
    conn.execute(
        "INSERT INTO bon_sortie_transformation (id, numero, transformateur_id, "
        "bon_commande_transformation_id, "
        "date) VALUES (?,?,?,?,?)",
        (bst_id, f"BST-2026-{nid()[:8]}", ids["transformateur"], bct_id, "2026-02-01"),
    )
    conn.execute(
        "INSERT INTO bon_sortie_transformation_ligne (id, bon_sortie_transformation_id, lot_id, "
        "quantite) "
        "VALUES (?,?,?,?)",
        (bstl_id, bst_id, lot_id, quantite),
    )
    conn.commit()
    return {"bst_id": bst_id, "bstl_id": bstl_id}


def envoyer(conn, ids, lot_id, quantite, poids, date_heure="2026-02-01T08:00:00.000"):
    doc = bon_sortie(conn, ids, lot_id, quantite)
    with connexion.transaction(conn):
        doc["mouvement_id"] = stock_service.enregistrer_mouvement(
            conn,
            lot_id=lot_id,
            type_mouvement="SORTIE_TRANSFORMATION",
            quantite=quantite,
            poids_kg=poids,
            emplacement_source=STOCK,
            emplacement_destination=chez(ids),
            utilisateur_id=ids["utilisateur"],
            document_source_type="bon_sortie_transformation_ligne",
            document_source_id=doc["bstl_id"],
            date_heure=date_heure,
        )
    return doc


def reception_transfo(
    conn,
    ids,
    envoi,
    lot_origine_id,
    quantite_recue,
    poids_recu,
    quantite_chute,
    poids_chute,
    prix_resultat=tnd(5.3),
):
    """Lot résultat (GALVA) + réception de transformation (1 ligne) — SANS mouvement."""
    lot_resultat_id = None
    if quantite_recue:
        lot_resultat_id = nid()
        conn.execute(
            "INSERT INTO lot (id, article_id, lot_parent_id, finition, longueur_m, "
            "quantite_initiale, "
            "poids_initial_kg, prix_unitaire_provisoire_minor) VALUES (?,?,?,?,?,?,?,?)",
            (
                lot_resultat_id,
                ids["article"],
                lot_origine_id,
                "GALVA",
                6.0,
                quantite_recue,
                poids_recu,
                prix_resultat,
            ),
        )
    rt_id, rtl_id = nid(), nid()
    conn.execute(
        "INSERT INTO reception_transformation (id, numero, bon_sortie_transformation_id, date) "
        "VALUES (?,?,?,?)",
        (rt_id, f"RTR-2026-{nid()[:8]}", envoi["bst_id"], "2026-02-05"),
    )
    conn.execute(
        "INSERT INTO reception_transformation_ligne (id, reception_transformation_id, "
        "bon_sortie_transformation_ligne_id, lot_resultat_id, quantite_recue, poids_recu_kg, "
        "quantite_chute, "
        "poids_chute_kg) VALUES (?,?,?,?,?,?,?,?)",
        (
            rtl_id,
            rt_id,
            envoi["bstl_id"],
            lot_resultat_id,
            quantite_recue,
            poids_recu,
            quantite_chute,
            poids_chute,
        ),
    )
    conn.commit()
    return {"rtl_id": rtl_id, "lot_resultat_id": lot_resultat_id}


def ligne_bl_client(conn, ids, cmd, lot_id, quantite, poids):
    bl_id, ligne_id = nid(), nid()
    conn.execute(
        "INSERT INTO bl_client (id, numero, commande_client_id, date) VALUES (?,?,?,?)",
        (bl_id, f"BLC-2026-{nid()[:8]}", cmd["commande_id"], "2026-03-01"),
    )
    conn.execute(
        "INSERT INTO bl_client_ligne (id, bl_client_id, lot_id, commande_ligne_id, type, quantite, "
        "poids_facturable_kg) VALUES (?,?,?,?,?,?,?)",
        (ligne_id, bl_id, lot_id, cmd["commande_ligne_id"], "INITIALE", quantite, poids),
    )
    conn.commit()
    return ligne_id


def livrer(conn, ids, lot_id, bl_client_ligne_id, quantite, poids, destination="LIVRE"):
    with connexion.transaction(conn):
        return stock_service.enregistrer_mouvement(
            conn,
            lot_id=lot_id,
            type_mouvement="SORTIE_LIVRAISON_CLIENT",
            quantite=quantite,
            poids_kg=poids,
            emplacement_source=STOCK,
            emplacement_destination=destination,
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_client_ligne",
            document_source_id=bl_client_ligne_id,
            date_heure="2026-03-01T08:00:00.000",
        )


def chaine_transformation(conn, ids):
    """Réception 100 -> envoi 100 chez le galvaniseur -> retour 95 (apparié) + chute 5."""
    lot = receptionner(conn, ids)
    envoi = envoyer(conn, ids, lot["lot_id"], 100, 350.0)
    rec = reception_transfo(conn, ids, envoi, lot["lot_id"], 95, 339.0, 5, 17.5)
    with connexion.transaction(conn):
        stock_service.enregistrer_retour_transformation(
            conn,
            reception_transformation_ligne_id=rec["rtl_id"],
            poids_consomme_kg=332.5,
            utilisateur_id=ids["utilisateur"],
            date_heure="2026-02-05T08:00:00.000",
        )
        stock_service.enregistrer_mouvement(
            conn,
            lot_id=lot["lot_id"],
            type_mouvement="SORTIE_CHUTE",
            quantite=5,
            poids_kg=17.5,
            emplacement_source=chez(ids),
            emplacement_destination="CHUTES",
            utilisateur_id=ids["utilisateur"],
            document_source_type="reception_transformation_ligne",
            document_source_id=rec["rtl_id"],
            date_heure="2026-02-05T08:00:00.000",
        )
    return lot, envoi, rec


MISE_EN_SERVICE = "2026-01-01T08:00:00+01:00"  # instant exact de mise en service (heure de Tunis)
INSTANT_REGISTRE = "2026-01-01T07:00:00.000"  # le même instant, au format du registre (UTC)


def inventaire_initial(conn, ids, instant=MISE_EN_SERVICE):
    return inventaire_initial_service.creer_inventaire_initial(
        conn, date_heure_mise_en_service=instant, utilisateur_id=ids["utilisateur"]
    )


def ligne_inventaire(
    conn,
    ids,
    quantite="100 pièces",
    poids="350 kg",
    cout="5 DT/pièce",
    valeur="500 DT",
    emplacement=STOCK,
    finition="NOIR",
    longueur="6 m",
):
    """Toutes les valeurs sont saisies AVEC leur unité (règle validée)."""
    return inventaire_initial_service.ajouter_ligne_inventaire_initial(
        conn,
        article_id=ids["article"],
        finition=finition,
        longueur=longueur,
        quantite=quantite,
        poids=poids,
        emplacement=emplacement,
        cout_unitaire=cout,
        valeur=valeur,
        utilisateur_id=ids["utilisateur"],
    )


# ---------------------------------------------------------------------------
# Mouvement valide
# ---------------------------------------------------------------------------


def test_mouvement_valide_entree_reception(conn, ids):
    lot = receptionner(conn, ids)
    assert stock_service.soldes_lot(conn, lot["lot_id"]) == {
        STOCK: {"quantite": 100, "poids_kg": 350.0}
    }
    historique = stock_service.historique_mouvements(conn, lot_id=lot["lot_id"])
    assert [m["type"] for m in historique] == ["ENTREE_RECEPTION_FOURNISSEUR"]
    assert historique[0]["utilisateur_id"] == ids["utilisateur"]
    assert historique[0]["document_source_id"] == lot["bl_ligne_id"]


def test_la_brique_ne_fait_aucun_commit(conn, ids):
    """
    enregistrer_mouvement participe à la transaction de l'appelant : rien
    n'est validé sans lui.
    """
    doc = bl_fournisseur_et_lot(conn, ids)
    stock_service.enregistrer_mouvement(
        conn,
        lot_id=doc["lot_id"],
        type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
        quantite=100,
        poids_kg=350.0,
        emplacement_source=None,
        emplacement_destination=STOCK,
        utilisateur_id=ids["utilisateur"],
        document_source_type="bl_fournisseur_ligne",
        document_source_id=doc["bl_ligne_id"],
    )
    assert conn.in_transaction  # transaction implicite encore ouverte : aucun COMMIT interne
    conn.rollback()
    assert compter(conn, "mouvement_stock") == 0


# ---------------------------------------------------------------------------
# Mouvements invalides
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("quantite", [0, -5, 2.5, True, "10"])
def test_quantite_invalide_refusee(conn, ids, quantite):
    doc = bl_fournisseur_et_lot(conn, ids)
    with pytest.raises(ErreurQuantiteInvalide):
        stock_service.enregistrer_mouvement(
            conn,
            lot_id=doc["lot_id"],
            type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
            quantite=quantite,
            poids_kg=350.0,
            emplacement_source=None,
            emplacement_destination=STOCK,
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_fournisseur_ligne",
            document_source_id=doc["bl_ligne_id"],
        )


@pytest.mark.parametrize("poids", [0, -1.0, math.nan, math.inf])
def test_poids_invalide_refuse(conn, ids, poids):
    doc = bl_fournisseur_et_lot(conn, ids)
    with pytest.raises(ErreurQuantiteInvalide):
        stock_service.enregistrer_mouvement(
            conn,
            lot_id=doc["lot_id"],
            type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
            quantite=100,
            poids_kg=poids,
            emplacement_source=None,
            emplacement_destination=STOCK,
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_fournisseur_ligne",
            document_source_id=doc["bl_ligne_id"],
        )


def test_couple_type_emplacements_incoherent_refuse(conn, ids):
    doc = bl_fournisseur_et_lot(conn, ids)
    with pytest.raises(ErreurMouvementIncoherent):
        stock_service.enregistrer_mouvement(
            conn,
            lot_id=doc["lot_id"],
            type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
            quantite=100,
            poids_kg=350.0,
            emplacement_source=None,
            emplacement_destination="CHUTES",
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_fournisseur_ligne",
            document_source_id=doc["bl_ligne_id"],
        )


@pytest.mark.parametrize("type_mouvement", ["INVENTE", "TRANSFERT"])
def test_type_inconnu_ou_non_pris_en_charge_refuse(conn, ids, type_mouvement):
    lot = receptionner(conn, ids)
    with pytest.raises(ErreurMouvementIncoherent):
        stock_service.enregistrer_mouvement(
            conn,
            lot_id=lot["lot_id"],
            type_mouvement=type_mouvement,
            quantite=1,
            poids_kg=3.5,
            emplacement_source=STOCK,
            emplacement_destination=chez(ids),
            utilisateur_id=ids["utilisateur"],
            document_source_type="x",
            document_source_id="x",
        )


def test_lot_ne_correspondant_pas_au_document_refuse(conn, ids):
    doc_a = bl_fournisseur_et_lot(conn, ids)
    doc_b = bl_fournisseur_et_lot(conn, ids)
    with pytest.raises(ErreurMouvementIncoherent):
        stock_service.enregistrer_mouvement(
            conn,
            lot_id=doc_a["lot_id"],
            type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
            quantite=100,
            poids_kg=350.0,
            emplacement_source=None,
            emplacement_destination=STOCK,
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_fournisseur_ligne",
            document_source_id=doc_b["bl_ligne_id"],
        )


def test_entree_differente_de_la_quantite_initiale_refusee(conn, ids):
    doc = bl_fournisseur_et_lot(conn, ids)
    with pytest.raises(ErreurMouvementIncoherent):
        stock_service.enregistrer_mouvement(
            conn,
            lot_id=doc["lot_id"],
            type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
            quantite=60,
            poids_kg=210.0,
            emplacement_source=None,
            emplacement_destination=STOCK,
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_fournisseur_ligne",
            document_source_id=doc["bl_ligne_id"],
        )


def test_sortie_transformation_quantite_differente_du_bon_refusee(conn, ids):
    lot = receptionner(conn, ids)
    doc = bon_sortie(conn, ids, lot["lot_id"], 40)
    with pytest.raises(ErreurMouvementIncoherent):
        stock_service.enregistrer_mouvement(
            conn,
            lot_id=lot["lot_id"],
            type_mouvement="SORTIE_TRANSFORMATION",
            quantite=50,
            poids_kg=175.0,
            emplacement_source=STOCK,
            emplacement_destination=chez(ids),
            utilisateur_id=ids["utilisateur"],
            document_source_type="bon_sortie_transformation_ligne",
            document_source_id=doc["bstl_id"],
        )


def test_lot_ou_utilisateur_introuvable_refuse(conn, ids):
    doc = bl_fournisseur_et_lot(conn, ids)
    commun = dict(
        type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
        quantite=100,
        poids_kg=350.0,
        emplacement_source=None,
        emplacement_destination=STOCK,
        document_source_type="bl_fournisseur_ligne",
        document_source_id=doc["bl_ligne_id"],
    )
    with pytest.raises(ErreurEnregistrementIntrouvable):
        stock_service.enregistrer_mouvement(
            conn, lot_id="lot-inexistant", utilisateur_id=ids["utilisateur"], **commun
        )
    with pytest.raises(ErreurEnregistrementIntrouvable):
        stock_service.enregistrer_mouvement(
            conn, lot_id=doc["lot_id"], utilisateur_id="inconnu", **commun
        )


def test_poids_retire_superieur_au_poids_present_refuse(conn, ids):
    lot = receptionner(conn, ids, quantite=10, poids=35.0)
    with pytest.raises(ErreurQuantiteInvalide):
        stock_service.corriger_inventaire(
            conn,
            lot_id=lot["lot_id"],
            sens="NEGATIVE",
            quantite="2 pièces",
            poids="40 kg",
            emplacement=STOCK,
            motif="casse constatée",
            utilisateur_id=ids["utilisateur"],
        )


# ---------------------------------------------------------------------------
# Solde insuffisant, emplacement invalide, document source manquant
# ---------------------------------------------------------------------------


def test_solde_insuffisant_refuse(conn, ids):
    lot = receptionner(conn, ids, quantite=10, poids=35.0)
    with pytest.raises(ErreurStockInsuffisant):
        stock_service.corriger_inventaire(
            conn,
            lot_id=lot["lot_id"],
            sens="NEGATIVE",
            quantite="11 pièces",
            poids="35 kg",
            emplacement=STOCK,
            motif="inventaire",
            utilisateur_id=ids["utilisateur"],
        )
    assert compter(conn, "journal_audit") == 0
    assert stock_service.soldes_lot(conn, lot["lot_id"])[STOCK]["quantite"] == 10


@pytest.mark.parametrize(
    "emplacement", ["STOCK_GMX", "CHEZ_TRANSFORMATEUR:inexistant", "CHEZ_TRANSFORMATEUR:"]
)
def test_emplacement_invalide_refuse(conn, ids, emplacement):
    lot = receptionner(conn, ids)
    with pytest.raises(ErreurEmplacementInvalide):
        stock_service.corriger_inventaire(
            conn,
            lot_id=lot["lot_id"],
            sens="POSITIVE",
            quantite="1 pièce",
            poids="3,5 kg",
            emplacement=emplacement,
            motif="pièce retrouvée",
            utilisateur_id=ids["utilisateur"],
        )


def test_correction_sur_chutes_ou_livre_refusee(conn, ids):
    lot = receptionner(conn, ids)
    for emplacement in ("CHUTES", "LIVRE"):
        with pytest.raises(ErreurMouvementIncoherent):
            stock_service.corriger_inventaire(
                conn,
                lot_id=lot["lot_id"],
                sens="POSITIVE",
                quantite="1 pièce",
                poids="3,5 kg",
                emplacement=emplacement,
                motif="test",
                utilisateur_id=ids["utilisateur"],
            )


def test_document_source_manquant_refuse(conn, ids):
    doc = bl_fournisseur_et_lot(conn, ids)
    for doc_type, doc_id in (
        (None, None),
        ("bl_fournisseur_ligne", None),
        ("bl_client_ligne", doc["bl_ligne_id"]),
        ("bl_fournisseur_ligne", "inexistant"),
    ):
        with pytest.raises(ErreurDocumentSourceManquant):
            stock_service.enregistrer_mouvement(
                conn,
                lot_id=doc["lot_id"],
                type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
                quantite=100,
                poids_kg=350.0,
                emplacement_source=None,
                emplacement_destination=STOCK,
                utilisateur_id=ids["utilisateur"],
                document_source_type=doc_type,
                document_source_id=doc_id,
            )


# ---------------------------------------------------------------------------
# Mouvements en double (service ET base)
# ---------------------------------------------------------------------------


def test_double_entree_de_reception_refusee_par_le_service(conn, ids):
    lot = receptionner(conn, ids)
    with pytest.raises(ErreurMouvementEnDouble):
        stock_service.enregistrer_mouvement(
            conn,
            lot_id=lot["lot_id"],
            type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
            quantite=100,
            poids_kg=350.0,
            emplacement_source=None,
            emplacement_destination=STOCK,
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_fournisseur_ligne",
            document_source_id=lot["bl_ligne_id"],
        )
    assert stock_service.soldes_lot(conn, lot["lot_id"])[STOCK]["quantite"] == 100


def test_double_entree_de_reception_refusee_par_la_base(conn, ids):
    """Même en contournant le service (SQL direct), l'index unique de la migration 0017 refuse."""
    lot = receptionner(conn, ids)
    with pytest.raises(ErreurMouvementEnDouble):
        stock_repository.inserer_mouvement(
            conn,
            id=nid(),
            lot_id=lot["lot_id"],
            type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
            quantite=100,
            poids_kg=350.0,
            emplacement_source=None,
            emplacement_destination=STOCK,
            document_source_type="autre_document",
            document_source_id="autre",
            utilisateur_id=ids["utilisateur"],
        )


def test_double_sortie_pour_une_meme_ligne_de_bl_client_refusee(conn, ids):
    cmd = creer_commande(conn, ids, quantite=100, finition="NOIR")
    lot = receptionner(conn, ids)
    affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 40, 140.0)
    ligne = ligne_bl_client(conn, ids, cmd, lot["lot_id"], 40, 140.0)
    livrer(conn, ids, lot["lot_id"], ligne, 40, 140.0)
    with pytest.raises(ErreurMouvementEnDouble):
        livrer(conn, ids, lot["lot_id"], ligne, 40, 140.0)
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        conn.execute(
            "INSERT INTO mouvement_stock (id, lot_id, type, quantite, poids_kg, "
            "emplacement_source, "
            "emplacement_destination, document_source_type, document_source_id, utilisateur_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                nid(),
                lot["lot_id"],
                "SORTIE_LIVRAISON_CLIENT",
                40,
                140.0,
                STOCK,
                "LIVRE",
                "bl_client_ligne",
                ligne,
                ids["utilisateur"],
            ),
        )
    conn.rollback()
    assert stock_service.soldes_lot(conn, lot["lot_id"])[STOCK]["quantite"] == 60


def test_livraison_client_exige_la_destination_livre(conn, ids):
    cmd = creer_commande(conn, ids, quantite=100, finition="NOIR")
    lot = receptionner(conn, ids)
    affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 40, 140.0)
    ligne = ligne_bl_client(conn, ids, cmd, lot["lot_id"], 40, 140.0)
    for destination in (None, "CHUTES"):
        with pytest.raises(ErreurMouvementIncoherent):
            livrer(conn, ids, lot["lot_id"], ligne, 40, 140.0, destination=destination)
    livrer(conn, ids, lot["lot_id"], ligne, 40, 140.0)
    assert stock_service.soldes_lot(conn, lot["lot_id"]) == {
        "LIVRE": {"quantite": 40, "poids_kg": 140.0},
        STOCK: {"quantite": 60, "poids_kg": 210.0},
    }


# ---------------------------------------------------------------------------
# Correction d'inventaire : motif, atomicité, rollback mouvement + audit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("motif", [None, "", "   "])
def test_motif_obligatoire(conn, ids, motif):
    lot = receptionner(conn, ids)
    with pytest.raises(ErreurMotifObligatoire):
        stock_service.corriger_inventaire(
            conn,
            lot_id=lot["lot_id"],
            sens="NEGATIVE",
            quantite="1 pièce",
            poids="3,5 kg",
            emplacement=STOCK,
            motif=motif,
            utilisateur_id=ids["utilisateur"],
        )
    assert compter(conn, "journal_audit") == 0
    assert compter(conn, "mouvement_stock") == 1


def test_correction_inventaire_atomique_mouvement_et_audit(conn, ids):
    lot = receptionner(conn, ids)
    mouvement_id = stock_service.corriger_inventaire(
        conn,
        lot_id=lot["lot_id"],
        sens="NEGATIVE",
        quantite="2 pièces",
        poids="0,007 t",
        emplacement=STOCK,
        motif="2 pièces introuvables à l'inventaire",
        utilisateur_id=ids["utilisateur"],
    )
    assert not conn.in_transaction  # transaction complète, validée
    mouvement = stock_repository.obtenir_mouvement(conn, mouvement_id)
    assert mouvement["type"] == "CORRECTION_INVENTAIRE_NEGATIVE"
    assert mouvement["motif"] == "2 pièces introuvables à l'inventaire"
    assert mouvement["utilisateur_id"] == ids["utilisateur"]
    assert mouvement["document_source_type"] == "journal_audit"
    audit_ligne = base.un_dict(
        conn, "SELECT * FROM journal_audit WHERE id = ?", (mouvement["document_source_id"],)
    )
    assert audit_ligne["action"] == "CORRECTION_INVENTAIRE"
    assert audit_ligne["entite_type"] == "mouvement_stock"
    assert audit_ligne["entite_id"] == mouvement_id
    assert audit_ligne["utilisateur_id"] == ids["utilisateur"]
    assert '"quantite": 100' in audit_ligne["valeur_avant"]
    assert '"quantite": 98' in audit_ligne["valeur_apres"]
    assert stock_service.soldes_lot(conn, lot["lot_id"])[STOCK] == {
        "quantite": 98,
        "poids_kg": 343.0,
    }


def test_correction_inventaire_positive_chez_le_transformateur(conn, ids):
    lot = receptionner(conn, ids)
    envoyer(conn, ids, lot["lot_id"], 100, 350.0)
    stock_service.corriger_inventaire(
        conn,
        lot_id=lot["lot_id"],
        sens="POSITIVE",
        quantite="1 pièce",
        poids="3,5 kg",
        emplacement=chez(ids),
        motif="pièce comptée en plus chez le galvaniseur",
        utilisateur_id=ids["utilisateur"],
    )
    assert stock_service.soldes_lot(conn, lot["lot_id"])[chez(ids)]["quantite"] == 101


def test_rollback_annule_mouvement_et_audit(conn, ids):
    lot = receptionner(conn, ids)

    class EchecSimule(Exception):
        pass

    with pytest.raises(EchecSimule):
        with connexion.transaction(conn):
            stock_service.enregistrer_mouvement(
                conn,
                lot_id=lot["lot_id"],
                type_mouvement="CORRECTION_INVENTAIRE_NEGATIVE",
                quantite=3,
                poids_kg=10.5,
                emplacement_source=STOCK,
                emplacement_destination=None,
                utilisateur_id=ids["utilisateur"],
                motif="test rollback",
            )
            assert compter(conn, "journal_audit") == 1
            raise EchecSimule()
    assert compter(conn, "journal_audit") == 0
    assert compter(conn, "mouvement_stock") == 1
    assert stock_service.soldes_lot(conn, lot["lot_id"])[STOCK]["quantite"] == 100


# ---------------------------------------------------------------------------
# Disponibilité, réservation, facture
# ---------------------------------------------------------------------------


def test_disponibilite_egale_physique_moins_affecte(conn, ids):
    cmd = creer_commande(conn, ids, quantite=100, finition="NOIR")
    lot = receptionner(conn, ids)
    affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 30, 105.0)
    dispo = stock_service.disponibilite(conn, ids["article"], "NOIR", 6.0)
    assert (dispo["physique_stock_gmc"], dispo["affecte_non_sorti"], dispo["disponible"]) == (
        100,
        30,
        70,
    )
    assert stock_service.quantite_affectable_lot(conn, lot["lot_id"]) == 70


def test_quantite_affectable_tient_compte_du_stock_physique_reel(conn, ids):
    """
    Constat E3 : le trigger plafonne sur la quantité initiale ; le service,
    sur le stock physique réel.
    """
    cmd = creer_commande(conn, ids, quantite=100, finition="NOIR")
    lot = receptionner(conn, ids)
    affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 30, 105.0)
    envoyer(conn, ids, lot["lot_id"], 50, 175.0)
    assert (
        stock_service.quantite_affectable_lot(conn, lot["lot_id"]) == 20
    )  # 50 physiques - 30 affectées
    stock_service.verifier_quantite_affectable(conn, lot["lot_id"], 20)
    with pytest.raises(ErreurDisponibiliteInsuffisante):
        stock_service.verifier_quantite_affectable(conn, lot["lot_id"], 21)


def test_reservation_devis_sans_impact_physique(conn, ids):
    receptionner(conn, ids)
    avant = stock_service.disponibilite(conn, ids["article"], "NOIR", 6.0, a_la_date="2026-02-10")
    mouvements_avant = compter(conn, "mouvement_stock")
    for statut, expire_le, quantite in (
        ("EN_COURS", "2026-03-01", 40),
        ("EN_COURS", "2026-02-01", 7),
        ("ANNULE", "2026-03-01", 9),
    ):
        devis_id, ligne_id = nid(), nid()
        conn.execute(
            "INSERT INTO devis (id, numero, client_id, date, date_validite, taux_change_id, "
            "statut) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                devis_id,
                f"DEV-2026-{nid()[:8]}",
                ids["client"],
                "2026-01-10",
                "2026-03-01",
                ids["taux_change"],
                statut,
            ),
        )
        conn.execute(
            "INSERT INTO devis_ligne (id, devis_id, article_id, finition, longueur_m, quantite, "
            "poids_theorique_kg, "
            "prix_achat_estimatif_minor, prix_vente_minor) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                ligne_id,
                devis_id,
                ids["article"],
                "NOIR",
                6.0,
                quantite,
                quantite * 21.0,
                tnd(5.0),
                tnd(6.0),
            ),
        )
        conn.execute(
            "INSERT INTO reservation_devis (id, devis_ligne_id, article_id, finition, longueur_m, "
            "quantite, expire_le) "
            "VALUES (?,?,?,?,?,?,?)",
            (nid(), ligne_id, ids["article"], "NOIR", 6.0, quantite, expire_le),
        )
    conn.commit()
    apres = stock_service.disponibilite(conn, ids["article"], "NOIR", 6.0, a_la_date="2026-02-10")
    assert apres["physique_stock_gmc"] == avant["physique_stock_gmc"] == 100
    assert apres["disponible"] == avant["disponible"] == 100
    assert apres["reserve_devis_informatif"] == 40  # seul le devis en cours et non expiré
    assert compter(conn, "mouvement_stock") == mouvements_avant


def test_facture_ne_cree_aucun_mouvement(conn, ids):
    cmd = creer_commande(conn, ids, quantite=100, finition="NOIR")
    lot = receptionner(conn, ids)
    affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 40, 140.0)
    ligne = ligne_bl_client(conn, ids, cmd, lot["lot_id"], 40, 140.0)
    livrer(conn, ids, lot["lot_id"], ligne, 40, 140.0)
    soldes_avant, mouvements_avant = (
        stock_service.soldes_lot(conn, lot["lot_id"]),
        compter(conn, "mouvement_stock"),
    )
    facture_id = nid()
    conn.execute(
        "INSERT INTO facture_client (id, numero, commande_client_id, date, montant_minor) VALUES "
        "(?,?,?,?,?)",
        (facture_id, f"FAC-2026-{nid()[:8]}", cmd["commande_id"], "2026-03-02", 22000),
    )
    conn.execute(
        "INSERT INTO facture_client_ligne (id, facture_client_id, bl_client_ligne_id, "
        "prix_applique_minor) "
        "VALUES (?,?,?,?)",
        (nid(), facture_id, ligne, 550),
    )
    conn.commit()
    assert stock_service.soldes_lot(conn, lot["lot_id"]) == soldes_avant
    assert compter(conn, "mouvement_stock") == mouvements_avant


# ---------------------------------------------------------------------------
# Transformateur = emplacement réel ; retour sans stock fantôme ; conservation
# ---------------------------------------------------------------------------


def test_stock_chez_transformateur_visible(conn, ids):
    lot = receptionner(conn, ids)
    envoyer(conn, ids, lot["lot_id"], 100, 350.0)
    assert stock_service.soldes_lot(conn, lot["lot_id"]) == {
        chez(ids): {"quantite": 100, "poids_kg": 350.0}
    }
    lignes = stock_service.stock_chez_transformateur(conn, ids["transformateur"])
    assert [(ligne["lot_id"], ligne["quantite"]) for ligne in lignes] == [(lot["lot_id"], 100)]
    assert [ligne["quantite"] for ligne in stock_service.stock_chez_transformateur(conn)] == [100]
    assert (
        stock_service.disponibilite(conn, ids["article"], "NOIR", 6.0)["chez_transformateurs"]
        == 100
    )
    assert stock_service.stock(conn, emplacement=STOCK) == []


def test_retour_transformateur_sans_stock_fantome(conn, ids):
    lot, _, rec = chaine_transformation(conn, ids)
    # Lot d'origine : plus rien chez le transformateur (95 consommées + 5 chutes).
    assert stock_service.soldes_lot(conn, lot["lot_id"]) == {
        "CHUTES": {"quantite": 5, "poids_kg": 17.5}
    }
    assert stock_service.stock_chez_transformateur(conn, ids["transformateur"]) == []
    # Lot résultat : 95 pièces GALVA en STOCK_GMC.
    assert stock_service.soldes_lot(conn, rec["lot_resultat_id"]) == {
        STOCK: {"quantite": 95, "poids_kg": 339.0}
    }


def test_entree_retour_seule_refusee(conn, ids):
    lot = receptionner(conn, ids)
    envoi = envoyer(conn, ids, lot["lot_id"], 100, 350.0)
    rec = reception_transfo(conn, ids, envoi, lot["lot_id"], 95, 339.0, 5, 17.5)
    for type_mouvement, source, destination, lot_id in (
        ("ENTREE_RETOUR_TRANSFORMATION", None, STOCK, rec["lot_resultat_id"]),
        ("CONSOMMATION_TRANSFORMATION", chez(ids), None, lot["lot_id"]),
    ):
        with pytest.raises(ErreurMouvementIncoherent, match="enregistrer_retour_transformation"):
            stock_service.enregistrer_mouvement(
                conn,
                lot_id=lot_id,
                type_mouvement=type_mouvement,
                quantite=95,
                poids_kg=339.0,
                emplacement_source=source,
                emplacement_destination=destination,
                utilisateur_id=ids["utilisateur"],
                document_source_type="reception_transformation_ligne",
                document_source_id=rec["rtl_id"],
            )


def test_retour_transformation_atomique(conn, ids):
    """Si la 2e face du retour échoue, la 1re est annulée avec elle (même transaction)."""
    lot = receptionner(conn, ids)
    envoi = envoyer(conn, ids, lot["lot_id"], 100, 350.0)
    rec = reception_transfo(conn, ids, envoi, lot["lot_id"], 95, 339.0, 5, 17.5)
    with connexion.transaction(conn):  # le lot résultat a déjà son entrée : la paire devra échouer
        stock_repository.inserer_mouvement(
            conn,
            id=nid(),
            lot_id=rec["lot_resultat_id"],
            type_mouvement="ENTREE_RETOUR_TRANSFORMATION",
            quantite=95,
            poids_kg=339.0,
            emplacement_source=None,
            emplacement_destination=STOCK,
            document_source_type="autre",
            document_source_id="autre",
            utilisateur_id=ids["utilisateur"],
        )
    with pytest.raises(ErreurMouvementEnDouble):
        with connexion.transaction(conn):
            stock_service.enregistrer_retour_transformation(
                conn,
                reception_transformation_ligne_id=rec["rtl_id"],
                poids_consomme_kg=332.5,
                utilisateur_id=ids["utilisateur"],
            )
    assert compter(conn, "mouvement_stock WHERE type = 'CONSOMMATION_TRANSFORMATION'") == 0
    assert stock_service.soldes_lot(conn, lot["lot_id"])[chez(ids)]["quantite"] == 100


def test_chute_doit_correspondre_a_la_reception(conn, ids):
    lot = receptionner(conn, ids)
    envoi = envoyer(conn, ids, lot["lot_id"], 100, 350.0)
    rec = reception_transfo(conn, ids, envoi, lot["lot_id"], 95, 339.0, 5, 17.5)
    for quantite, poids in ((4, 14.0), (5, 20.0)):
        with pytest.raises(ErreurMouvementIncoherent):
            stock_service.enregistrer_mouvement(
                conn,
                lot_id=lot["lot_id"],
                type_mouvement="SORTIE_CHUTE",
                quantite=quantite,
                poids_kg=poids,
                emplacement_source=chez(ids),
                emplacement_destination="CHUTES",
                utilisateur_id=ids["utilisateur"],
                document_source_type="reception_transformation_ligne",
                document_source_id=rec["rtl_id"],
            )


def test_conservation_du_stock_sur_une_chaine_complete(conn, ids):
    cmd = creer_commande(conn, ids, quantite=40, finition="GALVA")
    _, _, rec = chaine_transformation(conn, ids)
    affecter(conn, ids, rec["lot_resultat_id"], cmd["commande_ligne_id"], "INITIALE", 40, 142.7)
    ligne = ligne_bl_client(conn, ids, cmd, rec["lot_resultat_id"], 40, 142.7)
    livrer(conn, ids, rec["lot_resultat_id"], ligne, 40, 142.7)
    bilan = stock_service.verifier_conservation(conn)
    assert bilan["attendu"] == 100
    assert bilan["zones"] == {
        "STOCK_GMC": 55,
        "CHEZ_TRANSFORMATEURS": 0,
        "CHUTES": 5,
        "LIVRE": 40,
        "AUTRES": 0,
    }
    assert bilan["total_zones"] == 100
    assert bilan["anomalies"] == []
    assert bilan["equilibre"] is True


def test_conservation_detecte_le_stock_fantome_et_la_livraison_sans_destination(conn, ids):
    """Reproduit la convention d'avant la Phase 5.5 (constat E1) en contournant le service."""
    lot = receptionner(conn, ids)
    envoi = envoyer(conn, ids, lot["lot_id"], 100, 350.0)
    rec = reception_transfo(conn, ids, envoi, lot["lot_id"], 95, 339.0, 5, 17.5)
    with connexion.transaction(conn):
        # Entrée du lot résultat SANS sortie de chez le transformateur :
        stock_repository.inserer_mouvement(
            conn,
            id=nid(),
            lot_id=rec["lot_resultat_id"],
            type_mouvement="ENTREE_RETOUR_TRANSFORMATION",
            quantite=95,
            poids_kg=339.0,
            emplacement_source=None,
            emplacement_destination=STOCK,
            document_source_type="reception_transformation_ligne",
            document_source_id=rec["rtl_id"],
            utilisateur_id=ids["utilisateur"],
        )
        stock_repository.inserer_mouvement(  # livraison sans destination LIVRE
            conn,
            id=nid(),
            lot_id=rec["lot_resultat_id"],
            type_mouvement="SORTIE_LIVRAISON_CLIENT",
            quantite=10,
            poids_kg=35.0,
            emplacement_source=STOCK,
            emplacement_destination=None,
            document_source_type="bl_client_ligne",
            document_source_id="bidon",
            utilisateur_id=ids["utilisateur"],
        )
    bilan = stock_service.verifier_conservation(conn)
    assert bilan["equilibre"] is False
    assert bilan["zones"]["CHEZ_TRANSFORMATEURS"] == 100  # le stock fantôme est bien visible
    assert any("stock fantôme" in anomalie for anomalie in bilan["anomalies"])
    assert any("au lieu de LIVRE" in anomalie for anomalie in bilan["anomalies"])


# ---------------------------------------------------------------------------
# Inventaire initial de démarrage (remplace l'ouverture au 31/12/N-1)
# ---------------------------------------------------------------------------


def test_inventaire_initial_origine_distincte_jamais_un_achat(conn, ids):
    inventaire_initial(conn, ids)
    resultat = ligne_inventaire(conn, ids)
    lot = stock_repository.obtenir_lot(conn, resultat["lot_id"])
    assert lot["inventaire_initial_ligne_id"] == resultat["ligne_id"]
    assert lot["bl_fournisseur_ligne_id"] is None and lot["lot_parent_id"] is None
    for table in (
        "bl_fournisseur",
        "bl_fournisseur_ligne",
        "facture_fournisseur",
        "bon_commande_fournisseur",
        "macf_ligne_achat",
    ):
        assert compter(conn, table) == 0, table
    mouvement = stock_repository.obtenir_mouvement(conn, resultat["mouvement_id"])
    assert mouvement["type"] == "ENTREE_INVENTAIRE_INITIAL"
    assert mouvement["date_heure"] == INSTANT_REGISTRE  # instant exact de mise en service
    assert (mouvement["document_source_type"], mouvement["document_source_id"]) == (
        "inventaire_initial_ligne",
        resultat["ligne_id"],
    )
    ligne = inventaire_initial_service.lignes_inventaire_initial(conn)[0]
    assert ligne["cree_par"] == ids["utilisateur"] and ligne["cree_le"]
    assert (ligne["quantite"], ligne["poids_kg"], ligne["valeur_minor"]) == (
        100,
        350.0,
        100 * tnd(5.0),
    )
    entete = inventaire_initial_service.obtenir_inventaire_initial(conn)
    assert entete["date_heure_mise_en_service"] == INSTANT_REGISTRE


def test_inventaire_initial_unites_obligatoires_et_saisie_conservee(conn, ids):
    inventaire_initial(conn, ids)
    resultat = ligne_inventaire(conn, ids, poids="0,35 t", longueur="6000 mm")
    ligne = inventaire_initial_service.lignes_inventaire_initial(conn)[0]
    assert (ligne["poids_kg"], ligne["longueur_m"]) == (350.0, 6.0)  # convertis en kg et en m
    import json

    saisie = json.loads(ligne["saisie_originale"])
    assert saisie["poids"]["saisie"] == "0,35 t"  # unité d'origine conservée
    assert saisie["longueur"]["saisie"] == "6000 mm"
    assert saisie["cout_unitaire"]["saisie"] == "5 DT/pièce"
    assert stock_service.soldes_lot(conn, resultat["lot_id"])[STOCK]["poids_kg"] == 350.0
    for champ, valeur_sans_unite in (("poids", 350), ("quantite", 100), ("longueur", 6.0)):
        with pytest.raises(ErreurUniteManquante):
            ligne_inventaire(conn, ids, **{champ: valeur_sans_unite})
    assert compter(conn, "inventaire_initial_ligne") == 1


def test_inventaire_initial_cout_hors_unite_de_l_article_refuse(conn, ids):
    """
    Adapté après la décision « unité du CMP » (le point n'est plus en attente) :
    l'article de test est valorisé en DT/unité, un coût au kg ou à la tonne
    n'est pas converti implicitement (il faudrait le poids du lot).
    """
    inventaire_initial(conn, ids)
    for cout in ("5 DT/kg", "5 000 DT/tonne"):
        with pytest.raises(ErreurUniteValorisation, match="aucune conversion implicite"):
            ligne_inventaire(conn, ids, cout=cout)
    assert compter(conn, "inventaire_initial_ligne") == 0


def test_cout_inventaire_initial_integre_a_la_valorisation_cmp(conn, ids):
    inventaire_initial(conn, ids)
    ligne_inventaire(conn, ids, quantite="100 pièces", cout="5 DT/pièce", valeur="500 DT")
    assert cmp_actuel_minor(conn, ids["article"], "NOIR", 6.0) == tnd(5.0)
    receptionner(conn, ids, quantite=100, prix=tnd(6.0), date_heure="2026-01-05T08:00:00.000")
    stock_service.reconstruire_cmp_apres_transaction(conn)
    assert cmp_actuel_minor(conn, ids["article"], "NOIR", 6.0) == tnd(5.5)


def test_stock_theorique_a_un_instant_pour_le_rapprochement(conn, ids):
    """Base du futur rapprochement annuel : le stock théorique se lit à tout instant."""
    inventaire_initial(conn, ids)
    ligne_inventaire(conn, ids)
    ligne_inventaire(
        conn, ids, quantite="12 pièces", poids="144 kg", valeur="60 DT", emplacement=chez(ids)
    )
    receptionner(conn, ids, quantite=20, poids=70.0, date_heure="2026-01-05T08:00:00.000")
    au_demarrage = stock_service.stock(conn, jusqu_au=INSTANT_REGISTRE)
    assert sorted(ligne["quantite"] for ligne in au_demarrage) == [12, 100]
    assert sum(ligne["quantite"] for ligne in stock_service.stock(conn)) == 132


def test_inventaire_initial_chez_un_transformateur_hors_cmp(conn, ids):
    inventaire_initial(conn, ids)
    resultat = ligne_inventaire(conn, ids, emplacement=chez(ids))
    assert stock_service.soldes_lot(conn, resultat["lot_id"]) == {
        chez(ids): {"quantite": 100, "poids_kg": 350.0}
    }
    assert (
        compter(conn, "cmp_stock_general") == 0
    )  # pas en STOCK_GMC : n'entre pas (encore) dans le CMP


def test_inventaire_initial_refuse_en_chutes_ou_livre(conn, ids):
    inventaire_initial(conn, ids)
    for emplacement in ("CHUTES", "LIVRE"):
        with pytest.raises(ErreurEmplacementInvalide):
            ligne_inventaire(conn, ids, emplacement=emplacement)
    assert compter(conn, "inventaire_initial_ligne") == 0


def test_inventaire_initial_valeur_incoherente_refusee(conn, ids):
    inventaire_initial(conn, ids)
    for valeur in ("499,999 DT", "500 EUR"):
        with pytest.raises(ErreurMontantIncoherent):
            ligne_inventaire(conn, ids, valeur=valeur)
    assert compter(conn, "inventaire_initial_ligne") == 0


def test_inventaire_initial_unique(conn, ids):
    inventaire_initial(conn, ids)
    with pytest.raises(ErreurInventaireInitialInvalide):
        inventaire_initial(conn, ids, instant="2027-01-01T08:00:00+01:00")
    assert compter(conn, "inventaire_initial") == 1


def test_inventaire_initial_heure_exacte_obligatoire(conn, ids):
    for instant in ("2026-01-01", "01/01/2026 08:00"):
        with pytest.raises(ErreurSaisieInvalide):
            inventaire_initial(conn, ids, instant=instant)
    assert compter(conn, "inventaire_initial") == 0


def test_inventaire_initial_impossible_si_des_mouvements_existent(conn, ids):
    receptionner(conn, ids, date_heure="2025-11-15T08:00:00.000")
    with pytest.raises(ErreurInventaireInitialInvalide):
        inventaire_initial(conn, ids)


def test_inventaire_initial_clos_des_la_premiere_operation(conn, ids):
    inventaire_initial(conn, ids)
    ligne_inventaire(conn, ids)
    receptionner(conn, ids, date_heure="2026-01-05T08:00:00.000")
    with pytest.raises(ErreurInventaireInitialInvalide):
        ligne_inventaire(conn, ids, quantite="1 pièce", poids="3,5 kg", valeur="5 DT")
    assert compter(conn, "inventaire_initial_ligne") == 1


def test_aucun_mouvement_avant_la_mise_en_service(conn, ids):
    inventaire_initial(conn, ids)
    with pytest.raises(ErreurMouvementIncoherent, match="antérieur à la mise en service"):
        receptionner(conn, ids, date_heure="2026-01-01T06:59:59.999")
    receptionner(conn, ids, date_heure="2026-01-01T07:00:00.000")


def test_inventaire_initial_devise_differente_du_pool_refusee(conn, ids):
    inventaire_initial(conn, ids)
    ligne_inventaire(conn, ids)
    with pytest.raises(ErreurDeviseMelangee):
        ligne_inventaire(conn, ids, cout="5 EUR/pièce", valeur="500 EUR")


def test_inventaire_initial_immuable(conn, ids):
    entete = inventaire_initial(conn, ids)
    resultat = ligne_inventaire(conn, ids)
    with pytest.raises(ErreurEnregistrementImmuable):
        base.executer(
            conn,
            "UPDATE inventaire_initial_ligne SET quantite = 1 WHERE id = ?",
            (resultat["ligne_id"],),
        )
    with pytest.raises(ErreurEnregistrementImmuable):
        base.executer(
            conn, "DELETE FROM inventaire_initial_ligne WHERE id = ?", (resultat["ligne_id"],)
        )
    with pytest.raises(ErreurEnregistrementImmuable):
        base.executer(conn, "DELETE FROM inventaire_initial WHERE id = ?", (entete,))


def test_correction_inventaire_unites_obligatoires_et_saisie_tracee(conn, ids):
    lot = receptionner(conn, ids)
    for quantite, poids in ((2, "7 kg"), ("2 pièces", 7.0), ("2 pièces", "7")):
        with pytest.raises(ErreurUniteManquante):
            stock_service.corriger_inventaire(
                conn,
                lot_id=lot["lot_id"],
                sens="NEGATIVE",
                quantite=quantite,
                poids=poids,
                emplacement=STOCK,
                motif="test",
                utilisateur_id=ids["utilisateur"],
            )
    with pytest.raises(ErreurSaisieInvalide):  # une longueur n'est pas un poids
        stock_service.corriger_inventaire(
            conn,
            lot_id=lot["lot_id"],
            sens="NEGATIVE",
            quantite="2 pièces",
            poids="7 m",
            emplacement=STOCK,
            motif="test",
            utilisateur_id=ids["utilisateur"],
        )
    assert compter(conn, "journal_audit") == 0
    mouvement_id = stock_service.corriger_inventaire(
        conn,
        lot_id=lot["lot_id"],
        sens="NEGATIVE",
        quantite="2 pièces",
        poids="0,007 t",
        emplacement=STOCK,
        motif="casse",
        utilisateur_id=ids["utilisateur"],
    )
    assert stock_repository.obtenir_mouvement(conn, mouvement_id)["poids_kg"] == 7.0
    audit_ligne = base.un_dict(conn, "SELECT valeur_apres FROM journal_audit")
    assert '"saisie": "0,007 t"' in audit_ligne["valeur_apres"]


def test_lot_exactement_une_origine(conn, ids):
    doc = bl_fournisseur_et_lot(conn, ids)
    for bl_ligne, parent in ((None, None), (doc["bl_ligne_id"], doc["lot_id"])):
        with pytest.raises(sqlite3.IntegrityError, match="CHECK"):
            conn.execute(
                "INSERT INTO lot (id, article_id, bl_fournisseur_ligne_id, lot_parent_id, "
                "finition, longueur_m, "
                "quantite_initiale, poids_initial_kg, prix_unitaire_provisoire_minor) VALUES "
                "(?,?,?,?,?,?,?,?,?)",
                (nid(), ids["article"], bl_ligne, parent, "NOIR", 6.0, 1, 3.5, 5000),
            )


# ---------------------------------------------------------------------------
# CMP après transaction, articles en lecture seule, erreurs
# ---------------------------------------------------------------------------


def test_cmp_jamais_reconstruit_pendant_une_transaction_ouverte(conn, ids):
    lot = receptionner(conn, ids)
    with pytest.raises(RuntimeError):
        with connexion.transaction(conn):
            conn.execute(
                "INSERT INTO famille_article (id, libelle) VALUES (?, ?)", (nid(), "Témoin")
            )
            stock_service.reconstruire_cmp_apres_transaction(conn)
    assert (
        compter(conn, "famille_article WHERE libelle = 'Témoin'") == 0
    )  # rollback, pas de commit intempestif
    stock_service.corriger_inventaire(
        conn,
        lot_id=lot["lot_id"],
        sens="POSITIVE",
        quantite="10 pièces",
        poids="35 kg",
        emplacement=STOCK,
        motif="pièces retrouvées",
        utilisateur_id=ids["utilisateur"],
    )
    quantite_pool = conn.execute(
        "SELECT quantite_totale FROM cmp_stock_general WHERE article_id = ?", (ids["article"],)
    ).fetchone()[0]
    assert quantite_pool == 110  # CMP reconstruit après la validation de la correction


def test_article_lecture_seule(conn, ids):
    article = stock_service.obtenir_article(conn, ids["article"])
    assert (article["designation"], article["masse_lineique_kg_m"]) == ("Tube 40x40", 3.5)
    with pytest.raises(ErreurEnregistrementIntrouvable):
        stock_service.obtenir_article(conn, "inexistant")
    from repositories import article_repository

    assert [
        nom
        for nom in dir(article_repository)
        if nom.startswith(("inserer", "modifier", "supprimer"))
    ] == []


@pytest.mark.parametrize(
    "classe",
    [
        ErreurQuantiteInvalide,
        ErreurEmplacementInvalide,
        ErreurMouvementIncoherent,
        ErreurDocumentSourceManquant,
        ErreurMouvementEnDouble,
        ErreurMotifObligatoire,
        ErreurDisponibiliteInsuffisante,
        ErreurMontantIncoherent,
        ErreurInventaireInitialInvalide,
        ErreurUniteManquante,
        ErreurSaisieInvalide,
    ],
)
def test_nouvelles_erreurs_heritent_de_erreur_metier(classe):
    assert issubclass(classe, ErreurMetier)


def test_traduction_des_vraies_erreurs_de_la_base(conn, ids):
    """
    Correction Phase 5.5 : les messages RÉELS des triggers sont reconnus
    (pas seulement leurs noms).
    """
    lot = receptionner(conn, ids, quantite=10, poids=35.0)
    with pytest.raises(ErreurStockInsuffisant):
        base.executer(
            conn,
            "INSERT INTO mouvement_stock (id, lot_id, type, quantite, poids_kg, "
            "emplacement_source, "
            "emplacement_destination, document_source_type, document_source_id, utilisateur_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                nid(),
                lot["lot_id"],
                "CORRECTION_INVENTAIRE_NEGATIVE",
                11,
                35.0,
                STOCK,
                None,
                "x",
                "x",
                ids["utilisateur"],
            ),
        )
    with pytest.raises(ErreurEnregistrementImmuable):
        base.executer(
            conn, "UPDATE mouvement_stock SET quantite = 1 WHERE id = ?", (lot["mouvement_id"],)
        )
    with pytest.raises(ErreurEnregistrementImmuable, match="suppression"):
        base.executer(conn, "DELETE FROM mouvement_stock WHERE id = ?", (lot["mouvement_id"],))
    cmd = creer_commande(conn, ids, quantite=10, finition="NOIR")
    affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 10, 35.0)
    with pytest.raises(ErreurPlafondDepasse):
        base.executer(
            conn,
            "INSERT INTO affectation_stock (id, lot_id, commande_ligne_id, type, quantite, "
            "poids_kg, utilisateur_id) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                nid(),
                lot["lot_id"],
                cmd["commande_ligne_id"],
                "SUPPLEMENT",
                1,
                3.5,
                ids["utilisateur"],
            ),
        )
    assert isinstance(
        traduire_erreur_sqlite(
            sqlite3.IntegrityError("UNIQUE constraint failed: mouvement_stock.lot_id")
        ),
        ErreurMouvementEnDouble,
    )


# ---------------------------------------------------------------------------
# Migration 0017 : données existantes conservées
# ---------------------------------------------------------------------------


def test_migration_0017_conserve_les_donnees_existantes(tmp_path, monkeypatch):
    source = pathlib.Path(migrate.MIGRATIONS_DIR)
    dossier = tmp_path / "migrations"
    dossier.mkdir()
    for fichier in sorted(source.glob("*.sql")):
        if fichier.name < "0017":
            shutil.copy(fichier, dossier / fichier.name)
    monkeypatch.setattr(migrate, "MIGRATIONS_DIR", dossier)
    db_path = tmp_path / "avant_0017.db"
    migrate.apply_migrations(db_path, fresh=True)

    c = sqlite3.connect(str(db_path))
    c.execute("PRAGMA foreign_keys = ON")
    c.row_factory = sqlite3.Row
    from tests.helpers import creer_lot_reception, envoyer_transformation

    ids = seed_referentiels(c)
    cmd = creer_commande(c, ids, quantite=100, finition="GALVA")
    lot = creer_lot_reception(c, ids, quantite=100, poids_kg=350, prix_provisoire_minor=tnd(5.0))
    affecter(c, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 30, 105.0)
    envoyer_transformation(c, ids, lot["lot_id"], 60, 210)
    avant = {
        t: compter(c, t)
        for t in ("lot", "mouvement_stock", "affectation_stock", "bon_sortie_transformation_ligne")
    }
    c.close()

    shutil.copy(source / "0017_stock_service_socle.sql", dossier / "0017_stock_service_socle.sql")
    assert migrate.apply_migrations(db_path) == ["0017_stock_service_socle.sql"]

    c = sqlite3.connect(str(db_path))
    c.execute("PRAGMA foreign_keys = ON")
    assert {t: compter(c, t) for t in avant} == avant
    assert c.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert c.execute("PRAGMA foreign_key_check").fetchall() == []
    soldes = dict(
        c.execute(
            "SELECT emplacement, quantite FROM v_solde_lot_emplacement WHERE lot_id = ?",
            (lot["lot_id"],),
        ).fetchall()
    )
    assert soldes == {STOCK: 40, chez(ids): 60}
    with pytest.raises(sqlite3.IntegrityError):  # les triggers ont bien été recréés
        c.execute("DELETE FROM mouvement_stock")
    c.close()


def test_migration_0018_reprend_les_donnees_de_l_ouverture_0017(tmp_path, monkeypatch):
    """L'ouverture modélisée en 0017 est reprise telle quelle comme inventaire initial."""
    source = pathlib.Path(migrate.MIGRATIONS_DIR)
    dossier = tmp_path / "migrations"
    dossier.mkdir()
    for fichier in sorted(source.glob("*.sql")):
        if fichier.name < "0018":
            shutil.copy(fichier, dossier / fichier.name)
    monkeypatch.setattr(migrate, "MIGRATIONS_DIR", dossier)
    db_path = tmp_path / "avant_0018.db"
    migrate.apply_migrations(db_path, fresh=True)

    c = sqlite3.connect(str(db_path))
    c.execute("PRAGMA foreign_keys = ON")
    ids = seed_referentiels(c)
    entete, ligne, lot_id, mv_id = nid(), nid(), nid(), nid()
    c.execute(
        "INSERT INTO stock_ouverture (id, annee, date_reference, cree_par) VALUES (?,?,?,?)",
        (entete, 2026, "2025-12-31", ids["utilisateur"]),
    )
    c.execute(
        "INSERT INTO stock_ouverture_ligne (id, stock_ouverture_id, article_id, finition, "
        "longueur_m, "
        "quantite, poids_kg, emplacement, cout_unitaire_minor, valeur_minor, cree_par) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (
            ligne,
            entete,
            ids["article"],
            "NOIR",
            6.0,
            10,
            35.0,
            STOCK,
            5000,
            50000,
            ids["utilisateur"],
        ),
    )
    c.execute(
        "INSERT INTO lot (id, article_id, stock_ouverture_ligne_id, finition, longueur_m, "
        "quantite_initiale, poids_initial_kg, prix_unitaire_provisoire_minor, "
        "prix_unitaire_definitif_minor) VALUES (?,?,?,?,?,?,?,?,?)",
        (lot_id, ids["article"], ligne, "NOIR", 6.0, 10, 35.0, 5000, 5000),
    )
    c.execute(
        "INSERT INTO mouvement_stock (id, lot_id, type, quantite, poids_kg, "
        "emplacement_destination, "
        "document_source_type, document_source_id, date_heure, utilisateur_id) "
        "VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            mv_id,
            lot_id,
            "ENTREE_STOCK_OUVERTURE",
            10,
            35.0,
            STOCK,
            "stock_ouverture_ligne",
            ligne,
            "2025-12-31T23:59:59.999",
            ids["utilisateur"],
        ),
    )
    c.commit()
    c.close()

    shutil.copy(
        source / "0018_inventaire_initial_demarrage.sql",
        dossier / "0018_inventaire_initial_demarrage.sql",
    )
    assert migrate.apply_migrations(db_path) == ["0018_inventaire_initial_demarrage.sql"]

    c = sqlite3.connect(str(db_path))
    c.execute("PRAGMA foreign_keys = ON")
    assert c.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    assert c.execute("PRAGMA foreign_key_check").fetchall() == []
    assert c.execute("SELECT date_heure_mise_en_service FROM inventaire_initial").fetchone() == (
        "2025-12-31T23:59:59.999",
    )
    assert c.execute(
        "SELECT json_extract(saisie_originale, '$.reconstituee_par_migration_0018') "
        "FROM inventaire_initial_ligne WHERE id = ?",
        (ligne,),
    ).fetchone() == (1,)
    assert c.execute(
        "SELECT inventaire_initial_ligne_id FROM lot WHERE id = ?", (lot_id,)
    ).fetchone() == (ligne,)
    assert c.execute(
        "SELECT type, document_source_type FROM mouvement_stock WHERE id = ?", (mv_id,)
    ).fetchone() == ("ENTREE_INVENTAIRE_INITIAL", "inventaire_initial_ligne")
    tables = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert "stock_ouverture" not in tables and "stock_ouverture_ligne" not in tables
    c.close()
