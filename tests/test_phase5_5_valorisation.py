"""
Tests Phase 5.5 (finalisation) — règle définitive « unité du CMP / coût de
revient ».

Règle validée testée : le CMP n'est PAS systématiquement en DT/kg ; il est
exprimé dans l'unité de valorisation de l'article (DT/kg, DT/ml, DT/unité,
DT/tonne), qui dépend de l'article ; aucune unité par défaut ; changement
d'unité tracé (ancienne unité conservée, date, utilisateur) sans réécriture
des historiques de coûts ; règles Phase 4.1 conservées (coût réel du lot,
CMP, chutes au CMP figé à l'envoi, régularisation fournisseur, pas de FIFO).

Tous les montants attendus sont calculés à la main dans les commentaires.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import sqlite3

import pytest

from core.configuration import configuration_test
from core.erreurs import (
    ErreurEnregistrementImmuable,
    ErreurMontantIncoherent,
    ErreurMotifObligatoire,
    ErreurUniteValorisation,
    traduire_erreur_sqlite,
)
from db import connexion, migrate, valorisation
from repositories import stock_repository
from services import inventaire_initial_service, stock_service, unite_valorisation_service
from tests.helpers import (
    creer_lot_reception,
    envoyer_transformation,
    nid,
    recevoir_transformation,
    regulariser_facture_fournisseur,
    seed_referentiels,
)

STOCK = stock_service.STOCK_GMC


# ---------------------------------------------------------------------------
# Fixtures et constructeurs
# ---------------------------------------------------------------------------


@pytest.fixture()
def conn(tmp_path):
    db_path = tmp_path / "gmc_valorisation_5_5.db"
    migrate.apply_migrations(db_path, fresh=True)
    c = connexion.get_connection(configuration_test(db_path))
    c.row_factory = sqlite3.Row  # tests/helpers.py lit les colonnes par leur nom
    yield c
    connexion.fermer(c)


@pytest.fixture()
def ids(conn):
    return seed_referentiels(conn)  # article de base : valorisé en UNITE


def nouvel_article(conn, ids, unite, designation=None) -> str:
    """Article de test (INSERT minimal) + définition initiale de son unité par le service."""
    article_id = nid()
    conn.execute(
        "INSERT INTO article (id, designation, famille_id, masse_lineique_kg_m) VALUES (?,?,?,?)",
        (article_id, designation or f"Article {unite} {article_id[:4]}", ids["famille"], 10.0),
    )
    conn.commit()
    if unite is not None:
        unite_valorisation_service.definir_unite_valorisation(
            conn, article_id=article_id, unite=unite, utilisateur_id=ids["utilisateur"]
        )
    return article_id


def pour(ids, article_id) -> dict:
    """Identifiants de test où l'article courant est `article_id` (pour tests/helpers.py)."""
    return dict(ids, article=article_id)


def reception(conn, ids, article_id, quantite, poids, prix, date_heure, longueur=6.0):
    """BL fournisseur + lot (unité fixée par la base) + entrée via le Stock Service."""
    bl_id, ligne_id, lot_id = nid(), nid(), nid()
    conn.execute(
        "INSERT INTO bl_fournisseur (id, numero, numero_origine_fournisseur, fournisseur_id, "
        "date, statut) VALUES (?,?,?,?,?,?)",
        (bl_id, f"BLF-2026-{nid()[:8]}", "ORIG", ids["fournisseur"], "2026-01-05", "VALIDE"),
    )
    conn.execute(
        "INSERT INTO bl_fournisseur_ligne (id, bl_fournisseur_id, article_id, finition, "
        "longueur_m, quantite, poids_kg, prix_unitaire_provisoire_minor, devise) "
        "VALUES (?,?,?,?,?,?,?,?,?)",
        (ligne_id, bl_id, article_id, "NOIR", longueur, quantite, poids, prix, "TND"),
    )
    stock_repository.inserer_lot(
        conn,
        id=lot_id,
        article_id=article_id,
        finition="NOIR",
        longueur_m=longueur,
        quantite_initiale=quantite,
        poids_initial_kg=poids,
        prix_unitaire_provisoire_minor=prix,
        prix_unitaire_definitif_minor=None,
        devise="TND",
        bl_fournisseur_ligne_id=ligne_id,
    )
    conn.commit()
    with connexion.transaction(conn):
        mouvement_id = stock_service.enregistrer_mouvement(
            conn,
            lot_id=lot_id,
            type_mouvement="ENTREE_RECEPTION_FOURNISSEUR",
            quantite=quantite,
            poids_kg=poids,
            emplacement_source=None,
            emplacement_destination=STOCK,
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_fournisseur_ligne",
            document_source_id=ligne_id,
            date_heure=date_heure,
        )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    return {"lot_id": lot_id, "mouvement_id": mouvement_id}


def sortie(conn, ids, lot_id, pieces, kg, date_heure) -> str:
    """Sortie de STOCK_GMC (correction d'inventaire négative, motivée)."""
    return stock_service.corriger_inventaire(
        conn,
        lot_id=lot_id,
        sens="NEGATIVE",
        quantite=f"{pieces} pièces",
        poids=f"{kg} kg",
        emplacement=STOCK,
        motif="Test de valorisation",
        utilisateur_id=ids["utilisateur"],
        date_heure=date_heure,
    )


def cmp(conn, article_id, longueur=6.0, finition="NOIR") -> dict:
    detail = valorisation.cmp_actuel(conn, article_id, finition, longueur)
    assert detail is not None
    return detail


def lignes_historique(conn, article_id) -> dict:
    return {
        ligne["mouvement_stock_id"]: dict(ligne)
        for ligne in conn.execute(
            "SELECT mouvement_stock_id, unite_valorisation, quantite_totale_apres, "
            "quantite_valorisation_apres, valeur_totale_apres_minor, cmp_unitaire_apres_minor, "
            "montant_mouvement_minor, devise, date_heure FROM cmp_historique "
            "WHERE article_id = ?",
            (article_id,),
        )
    }


# ---------------------------------------------------------------------------
# CMP dans chacune des quatre unités de valorisation
# ---------------------------------------------------------------------------


def test_cmp_en_dt_par_kg(conn, ids):
    article = nouvel_article(conn, ids, "KG")
    lot_a = reception(conn, ids, article, 10, 1000.0, 2000, "2026-01-05T08:00:00")  # 2,000 DT/kg
    reception(conn, ids, article, 10, 1050.0, 2100, "2026-01-06T08:00:00")  # 2,100 DT/kg
    # Valeur = 1 000 kg × 2 000 + 1 050 kg × 2 100 = 2 000 000 + 2 205 000 = 4 205 000 millimes
    # CMP = 4 205 000 / 2 050 kg = 2 051,2195… -> 2 051 millimes/kg (2,051 DT/kg)
    etat = cmp(conn, article)
    assert (etat["unite_valorisation"], etat["cmp_unitaire_minor"]) == ("KG", 2051)
    assert (etat["valeur_totale_minor"], etat["quantite_valorisation"]) == (4_205_000, 2050.0)
    assert etat["cmp_unitaire_minor"] != 4_205_000 // 20  # jamais un CMP par pièce

    # Sortie de 5 pièces pesant 510 kg : retrait AU POIDS
    # 4 205 000 × 510 / 2 050 = 1 046 121,95 -> 1 046 122 (par pièce : 1 051 250)
    mouvement = sortie(conn, ids, lot_a["lot_id"], 5, 510, "2026-01-10T08:00:00")
    assert valorisation.montant_mouvement_minor(conn, mouvement) == -1_046_122
    etat = cmp(conn, article)
    assert (etat["valeur_totale_minor"], etat["quantite_valorisation"]) == (3_158_878, 1540.0)
    assert etat["cmp_unitaire_minor"] == 2051  # une sortie au CMP ne change pas le CMP


def test_cmp_en_dt_par_tonne(conn, ids):
    article = nouvel_article(conn, ids, "TONNE")
    lot_a = reception(conn, ids, article, 10, 1000.0, 2_000_000, "2026-01-05T08:00:00")
    reception(conn, ids, article, 10, 1050.0, 2_100_000, "2026-01-06T08:00:00")
    # 1 t × 2 000 000 + 1,05 t × 2 100 000 = 4 205 000 ; CMP = 4 205 000 / 2,05 t
    # = 2 051 219,51 -> 2 051 220 millimes/tonne (2 051,220 DT/t)
    etat = cmp(conn, article)
    assert (etat["unite_valorisation"], etat["cmp_unitaire_minor"]) == ("TONNE", 2_051_220)
    assert (etat["valeur_totale_minor"], etat["quantite_valorisation"]) == (4_205_000, 2.05)
    # Même sortie qu'au kg : 0,51 t -> même montant exact (1 t = 1 000 kg)
    mouvement = sortie(conn, ids, lot_a["lot_id"], 5, 510, "2026-01-10T08:00:00")
    assert valorisation.montant_mouvement_minor(conn, mouvement) == -1_046_122


def test_cmp_en_dt_par_ml(conn, ids):
    article = nouvel_article(conn, ids, "ML")
    lot_a = reception(conn, ids, article, 10, 60.0, 1500, "2026-01-05T08:00:00")  # 1,5 DT/ml
    reception(conn, ids, article, 20, 130.0, 1800, "2026-01-06T08:00:00")  # 1,8 DT/ml
    # Barres de 6 m : 10 × 6 × 1 500 + 20 × 6 × 1 800 = 90 000 + 216 000 = 306 000
    # CMP = 306 000 / 180 ml = 1 700 millimes/ml (1,700 DT/ml)
    etat = cmp(conn, article)
    assert (etat["unite_valorisation"], etat["cmp_unitaire_minor"]) == ("ML", 1700)
    assert etat["quantite_valorisation"] == 180.0
    # Sortie de 3 barres (18 ml, 20 kg) : 18 × 1 700 = 30 600 (au poids : 32 210,5)
    mouvement = sortie(conn, ids, lot_a["lot_id"], 3, 20, "2026-01-10T08:00:00")
    assert valorisation.montant_mouvement_minor(conn, mouvement) == -30_600


def test_cmp_en_dt_par_unite(conn, ids):
    article = ids["article"]  # valorisé en UNITE
    lot_a = reception(conn, ids, article, 100, 350.0, 5000, "2026-01-05T08:00:00")
    reception(conn, ids, article, 100, 380.0, 6000, "2026-01-06T08:00:00")
    # (100 × 5 000 + 100 × 6 000) / 200 unités = 5 500 millimes/unité
    etat = cmp(conn, article)
    assert (etat["unite_valorisation"], etat["cmp_unitaire_minor"]) == ("UNITE", 5500)
    mouvement = sortie(conn, ids, lot_a["lot_id"], 10, 35, "2026-01-10T08:00:00")
    assert valorisation.montant_mouvement_minor(conn, mouvement) == -55_000  # 10 × 5 500


def test_articles_d_unites_differentes_valorises_chacun_dans_la_sienne(conn, ids):
    article_kg = nouvel_article(conn, ids, "KG")
    article_ml = nouvel_article(conn, ids, "ML")
    reception(conn, ids, article_kg, 10, 1000.0, 2000, "2026-01-05T08:00:00")
    reception(conn, ids, article_ml, 10, 60.0, 1500, "2026-01-05T09:00:00")
    reception(conn, ids, ids["article"], 10, 35.0, 5000, "2026-01-05T10:00:00")
    unites_cache = dict(
        conn.execute("SELECT article_id, unite_valorisation FROM cmp_stock_general").fetchall()
    )
    assert unites_cache == {article_kg: "KG", article_ml: "ML", ids["article"]: "UNITE"}
    assert (
        cmp(conn, article_kg)["cmp_unitaire_minor"],
        cmp(conn, article_ml)["cmp_unitaire_minor"],
    ) == (
        2000,
        1500,
    )
    for article, unite in unites_cache.items():
        assert {
            ligne["unite_valorisation"] for ligne in lignes_historique(conn, article).values()
        } == {unite}


# ---------------------------------------------------------------------------
# Changement d'unité : historique, non-réécriture, traçabilité
# ---------------------------------------------------------------------------


def _pool_unite_puis_kg(conn, ids):
    article = nouvel_article(conn, ids, "UNITE")
    lot_a = reception(conn, ids, article, 10, 1000.0, 200_000, "2026-01-05T08:00:00")
    lot_b = reception(conn, ids, article, 10, 1050.0, 220_500, "2026-01-06T08:00:00")
    # 10 × 200 000 + 10 × 220 500 = 4 205 000 ; CMP = 210 250 millimes/unité
    sortie_1 = sortie(conn, ids, lot_a["lot_id"], 5, 510, "2026-01-10T08:00:00")
    # Par pièce : 4 205 000 × 5 / 20 = 1 051 250 -> reste 3 153 750, 15 pièces, 1 540 kg
    return article, lot_a, lot_b, sortie_1


def test_changement_d_unite_trace_et_historique_non_reecrit(conn, ids):
    article, lot_a, lot_b, sortie_1 = _pool_unite_puis_kg(conn, ids)
    avant = lignes_historique(conn, article)
    assert avant[sortie_1]["montant_mouvement_minor"] == -1_051_250
    assert {ligne["unite_valorisation"] for ligne in avant.values()} == {"UNITE"}

    changement_id = unite_valorisation_service.changer_unite_valorisation(
        conn,
        article_id=article,
        nouvelle_unite="KG",
        utilisateur_id=ids["utilisateur"],
        motif="Dérogation Mohamed : article désormais valorisé au kg",
        date_heure="2026-02-01T00:00:00",
    )
    # Historique : l'ancienne unité est conservée, la nouvelle enregistrée, date et utilisateur.
    historique = unite_valorisation_service.historique_unite_valorisation(conn, article)
    assert [(h["nature"], h["unite"], h["unite_precedente"]) for h in historique] == [
        ("DEFINITION_INITIALE", "UNITE", None),
        ("CHANGEMENT", "KG", "UNITE"),
    ]
    changement = historique[1]
    assert changement["id"] == changement_id
    assert changement["date_effet"] == "2026-02-01T00:00:00.000"
    assert changement["cree_par"] == ids["utilisateur"] and changement["cree_le"]
    assert changement["motif"].startswith("Dérogation")
    # Conversion explicite tracée : 3 153 750 / 15 = 210 250 /unité ; / 1 540 kg = 2 047,89 -> 2 048
    (pool,) = changement["detail_cmp"]["pools"]
    assert pool["cmp_avant"] == {"unite": "UNITE", "cmp_unitaire_minor": 210_250}
    assert pool["cmp_apres"] == {"unite": "KG", "cmp_unitaire_minor": 2048}
    assert pool["valeur_totale_minor"] == 3_153_750  # la valeur ne change pas

    # Cache : lignes antérieures identiques (toujours en UNITE), état actuel en KG.
    assert {k: v for k, v in lignes_historique(conn, article).items() if k in avant} == avant
    assert cmp(conn, article)["unite_valorisation"] == "KG"
    assert cmp(conn, article)["cmp_unitaire_minor"] == 2048

    # Après la date d'effet, les sorties se valorisent au poids :
    # 3 153 750 × 520 / 1 540 = 1 064 902,6 -> 1 064 903 (par pièce : 1 051 250)
    sortie_2 = sortie(conn, ids, lot_b["lot_id"], 5, 520, "2026-02-10T08:00:00")
    apres = lignes_historique(conn, article)
    assert apres[sortie_2]["unite_valorisation"] == "KG"
    assert apres[sortie_2]["montant_mouvement_minor"] == -1_064_903
    assert {k: v for k, v in apres.items() if k in avant} == avant  # toujours pas réécrites
    # Les lots créés avant le changement gardent l'unité (et le prix) de leur création.
    assert valorisation.unite_prix_lot(conn, lot_a["lot_id"]) == "UNITE"
    assert valorisation.cout_reel_lot_minor(conn, lot_a["lot_id"]) == 200_000


def test_lot_cree_apres_changement_prend_la_nouvelle_unite(conn, ids):
    article, _, _, _ = _pool_unite_puis_kg(conn, ids)
    unite_valorisation_service.changer_unite_valorisation(
        conn,
        article_id=article,
        nouvelle_unite="KG",
        utilisateur_id=ids["utilisateur"],
        motif="Dérogation",
        date_heure="2026-02-01T00:00:00",
    )
    lot_c = reception(conn, ids, article, 5, 500.0, 2100, "2026-02-15T08:00:00")  # 2,100 DT/kg
    assert valorisation.unite_prix_lot(conn, lot_c["lot_id"]) == "KG"
    # 3 153 750 + 500 × 2 100 = 4 203 750 ; 1 540 + 500 = 2 040 kg -> 2 060,66 -> 2 061
    assert cmp(conn, article)["cmp_unitaire_minor"] == 2061


def test_changement_d_unite_refuse_sans_motif_ou_retroactif(conn, ids):
    article, _, _, _ = _pool_unite_puis_kg(conn, ids)
    arguments = {"article_id": article, "utilisateur_id": ids["utilisateur"]}
    with pytest.raises(ErreurMotifObligatoire):
        unite_valorisation_service.changer_unite_valorisation(
            conn, nouvelle_unite="KG", motif="  ", **arguments
        )
    with pytest.raises(ErreurUniteValorisation, match="déjà valorisé"):
        unite_valorisation_service.changer_unite_valorisation(
            conn, nouvelle_unite="UNITE", motif="x", **arguments
        )
    with pytest.raises(ErreurUniteValorisation, match="inconnue"):
        unite_valorisation_service.changer_unite_valorisation(
            conn, nouvelle_unite="M2", motif="x", **arguments
        )
    # Un mouvement est daté du 10/01 : un changement au 09/01 le réécrirait.
    with pytest.raises(ErreurUniteValorisation, match="rétroactivement"):
        unite_valorisation_service.changer_unite_valorisation(
            conn, nouvelle_unite="KG", motif="x", date_heure="2026-01-09T00:00:00", **arguments
        )
    with pytest.raises(ErreurUniteValorisation, match="futur"):
        unite_valorisation_service.changer_unite_valorisation(
            conn, nouvelle_unite="KG", motif="x", date_heure="2099-01-01T00:00:00", **arguments
        )
    with pytest.raises(ErreurUniteValorisation, match="déjà définie"):
        unite_valorisation_service.definir_unite_valorisation(
            conn, article_id=article, unite="KG", utilisateur_id=ids["utilisateur"]
        )
    assert len(unite_valorisation_service.historique_unite_valorisation(conn, article)) == 1


def test_historique_d_unite_immuable_et_controle_en_base(conn, ids):
    article, _, _, _ = _pool_unite_puis_kg(conn, ids)
    for requete in (
        "UPDATE article_unite_valorisation SET unite = 'KG' WHERE article_id = ?",
        "DELETE FROM article_unite_valorisation WHERE article_id = ?",
    ):
        with pytest.raises(sqlite3.IntegrityError) as exc:
            conn.execute(requete, (article,))
        assert isinstance(traduire_erreur_sqlite(exc.value), ErreurEnregistrementImmuable)
    conn.rollback()
    # Même en contournant le service, la base refuse un changement rétroactif.
    with pytest.raises(sqlite3.IntegrityError, match="réécriture"):
        conn.execute(
            "INSERT INTO article_unite_valorisation (id, article_id, nature, unite, "
            "unite_precedente, date_effet, motif, cree_par) VALUES (?,?,?,?,?,?,?,?)",
            (
                nid(),
                article,
                "CHANGEMENT",
                "KG",
                "UNITE",
                "2026-01-09T00:00:00.000",
                "x",
                ids["utilisateur"],
            ),
        )
    conn.rollback()


# ---------------------------------------------------------------------------
# Régularisation fournisseur, reconstruction, chutes
# ---------------------------------------------------------------------------


def test_regularisation_fournisseur_dans_l_unite_du_lot(conn, ids):
    """Cas A (lot encore en stock) : le prix facturé au kg remplace le prix BL au kg."""
    article = nouvel_article(conn, ids, "KG")
    lot = creer_lot_reception(conn, pour(ids, article), 10, 1000.0, 2000, finition="NOIR")
    stock_service.reconstruire_cmp_apres_transaction(conn)
    assert cmp(conn, article)["cmp_unitaire_minor"] == 2000
    assert valorisation.unite_prix_lot(conn, lot["lot_id"]) == "KG"
    regul = regulariser_facture_fournisseur(
        conn, ids, lot["lot_id"], lot["bl_ligne_id"], 2000, 2200, lot_deja_sorti=0
    )
    assert regul["impact_analytique"] == "APPLIQUE_AU_LOT"
    stock_service.reconstruire_cmp_apres_transaction(conn)
    etat = cmp(conn, article)
    # 1 000 kg × 2 200 = 2 200 000 ; CMP = 2 200 millimes/kg (jamais plus 2 000)
    assert (
        etat["unite_valorisation"],
        etat["cmp_unitaire_minor"],
        etat["valeur_totale_minor"],
    ) == (
        "KG",
        2200,
        2_200_000,
    )


def test_regularisation_lot_deja_sorti_ecart_separe_non_retroactif(conn, ids):
    """Cas B (lot déjà sorti) : écart tracé à part, CMP déjà consommé inchangé."""
    article = nouvel_article(conn, ids, "KG")
    lot = creer_lot_reception(conn, pour(ids, article), 10, 1000.0, 2000, finition="NOIR")
    sortie(conn, ids, lot["lot_id"], 5, 500, "2026-01-10T08:00:00")  # 500 × 2 000 = 1 000 000
    avant = lignes_historique(conn, article)
    regul = regulariser_facture_fournisseur(
        conn, ids, lot["lot_id"], lot["bl_ligne_id"], 2000, 2200, lot_deja_sorti=1
    )
    assert regul["impact_analytique"] == "ECART_SEPARE"
    stock_service.reconstruire_cmp_apres_transaction(conn)
    assert lignes_historique(conn, article) == avant
    assert valorisation.cout_reel_lot_minor(conn, lot["lot_id"]) == 2000
    ligne = conn.execute(
        "SELECT prix_provisoire_minor, prix_definitif_minor, ecart_unitaire_minor "
        "FROM regularisation_prix_fournisseur WHERE lot_id = ?",
        (lot["lot_id"],),
    ).fetchone()
    assert tuple(ligne) == (2000, 2200, 200)  # par kg : l'unité des prix du lot


def test_reconstruction_cmp_multi_unites_idempotente(conn, ids):
    articles = {unite: nouvel_article(conn, ids, unite) for unite in ("KG", "TONNE", "ML")}
    lots = {
        "KG": reception(conn, ids, articles["KG"], 10, 1000.0, 2000, "2026-01-05T08:00:00"),
        "TONNE": reception(
            conn, ids, articles["TONNE"], 10, 1000.0, 2_000_000, "2026-01-05T09:00:00"
        ),
        "ML": reception(conn, ids, articles["ML"], 10, 60.0, 1500, "2026-01-05T10:00:00"),
        "UNITE": reception(conn, ids, ids["article"], 10, 35.0, 5000, "2026-01-05T11:00:00"),
    }
    for i, lot in enumerate(lots.values()):
        sortie(conn, ids, lot["lot_id"], 3, 7, f"2026-01-1{i}T08:00:00")

    def instantane():
        general = conn.execute(
            "SELECT article_id, finition, longueur_m, unite_valorisation, quantite_totale, "
            "poids_total_kg, quantite_valorisation, valeur_totale_minor, cmp_unitaire_minor, "
            "devise FROM cmp_stock_general ORDER BY article_id"
        ).fetchall()
        historique = conn.execute(
            "SELECT mouvement_stock_id, unite_valorisation, quantite_totale_apres, "
            "poids_total_apres_kg, quantite_valorisation_apres, valeur_totale_apres_minor, "
            "cmp_unitaire_apres_minor, montant_mouvement_minor, devise, date_heure "
            "FROM cmp_historique ORDER BY mouvement_stock_id"
        ).fetchall()
        return [tuple(r) for r in general], [tuple(r) for r in historique]

    reference = instantane()
    assert len(reference[0]) == 4 and len(reference[1]) == 8
    stock_service.reconstruire_cmp_apres_transaction(conn)
    assert instantane() == reference
    conn.execute("DELETE FROM cmp_historique")
    conn.execute("DELETE FROM cmp_stock_general")
    conn.commit()
    valorisation.calculer_pools(conn)  # calcul pur : n'écrit rien
    assert conn.execute("SELECT COUNT(*) FROM cmp_stock_general").fetchone()[0] == 0
    stock_service.reconstruire_cmp_apres_transaction(conn)
    assert instantane() == reference


def test_chute_valorisee_dans_l_unite_du_pool_au_depart(conn, ids):
    # Article au kg : CMP 2 000 millimes/kg au départ chez le transformateur.
    article_kg = nouvel_article(conn, ids, "KG")
    ids_kg = pour(ids, article_kg)
    lot = creer_lot_reception(conn, ids_kg, 10, 1000.0, 2000, finition="NOIR")
    envoi = envoyer_transformation(conn, ids_kg, lot["lot_id"], 4, 400.0)
    retour = recevoir_transformation(
        conn,
        ids_kg,
        envoi["bst_id"],
        envoi["bstl_id"],
        3,
        315.0,
        1,
        90.0,
        prix_lot_resultat_minor=2000,
    )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    detail = valorisation.cout_chute_detail(conn, retour["chute_id"])
    assert (detail["unite_valorisation"], detail["cmp_unitaire_minor"]) == ("KG", 2000)
    # Chute de 1 pièce pesant 90 kg : 90 × 2 000 = 180 000 (par pièce : 200 000)
    assert valorisation.cout_chute_total_minor(conn, retour["chute_id"]) == 180_000

    # Article au ml : 6 m × 1 700 = 10 200 pour une barre de chute.
    article_ml = nouvel_article(conn, ids, "ML")
    ids_ml = pour(ids, article_ml)
    lot_ml = creer_lot_reception(conn, ids_ml, 10, 60.0, 1700, finition="NOIR")
    envoi_ml = envoyer_transformation(conn, ids_ml, lot_ml["lot_id"], 4, 24.0)
    retour_ml = recevoir_transformation(
        conn,
        ids_ml,
        envoi_ml["bst_id"],
        envoi_ml["bstl_id"],
        3,
        18.0,
        1,
        6.0,
        prix_lot_resultat_minor=1700,
    )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    assert valorisation.cout_chute_detail(conn, retour_ml["chute_id"])["unite_valorisation"] == "ML"
    assert valorisation.cout_chute_total_minor(conn, retour_ml["chute_id"]) == 10_200


def test_cout_reel_d_une_affectation_initiale_dans_l_unite_du_lot(conn, ids):
    from tests.helpers import affecter, creer_commande, livrer

    article = nouvel_article(conn, ids, "KG")
    ids_kg = pour(ids, article)
    commande = creer_commande(conn, ids_kg, quantite=10, finition="NOIR")
    lot = creer_lot_reception(conn, ids_kg, 10, 1000.0, 2000, finition="NOIR")
    affectation = affecter(
        conn, ids_kg, lot["lot_id"], commande["commande_ligne_id"], "INITIALE", 4, 410.0
    )
    livraison = livrer(
        conn,
        ids_kg,
        lot["lot_id"],
        commande["commande_ligne_id"],
        affectation,
        "INITIALE",
        4,
        410.0,
        commande["commande_id"],
    )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    detail = valorisation.cout_sortie_detail(conn, livraison["mouvement_id"], lot["lot_id"])
    assert detail == {"cout_unitaire_minor": 2000, "unite": "KG"}
    # Coût réel du lot : 410 kg × 2 000 = 820 000 (jamais 4 pièces × un prix par pièce)
    assert (
        valorisation.cout_sortie_total_minor(conn, livraison["mouvement_id"], lot["lot_id"])
        == 820_000
    )


# ---------------------------------------------------------------------------
# Inventaire initial dans l'unité de l'article
# ---------------------------------------------------------------------------


def _inventaire(conn, ids):
    inventaire_initial_service.creer_inventaire_initial(
        conn,
        date_heure_mise_en_service="2026-01-01T08:00:00+01:00",
        utilisateur_id=ids["utilisateur"],
    )


def _ligne(conn, ids, article, quantite, poids, cout, valeur, longueur="6 m"):
    return inventaire_initial_service.ajouter_ligne_inventaire_initial(
        conn,
        article_id=article,
        finition="NOIR",
        longueur=longueur,
        quantite=quantite,
        poids=poids,
        emplacement=STOCK,
        cout_unitaire=cout,
        valeur=valeur,
        utilisateur_id=ids["utilisateur"],
    )


def test_inventaire_initial_dans_l_unite_de_valorisation_de_l_article(conn, ids):
    _inventaire(conn, ids)
    article_kg = nouvel_article(conn, ids, "KG")
    article_t = nouvel_article(conn, ids, "TONNE")
    article_ml = nouvel_article(conn, ids, "ML")
    # KG : 1 000 kg × 2,5 DT/kg = 2 500 DT
    kg = _ligne(conn, ids, article_kg, "10 pièces", "1 000 kg", "2,5 DT/kg", "2 500 DT")
    # TONNE : 1 t × 2 500 DT/tonne = 2 500 DT
    _ligne(conn, ids, article_t, "10 pièces", "1 t", "2 500 DT/tonne", "2 500 DT")
    # ML : 10 barres × 6 m = 60 ml × 12 DT/ml = 720 DT
    _ligne(conn, ids, article_ml, "10 pièces", "60 kg", "12 DT/ml", "720 DT")
    # UNITE : 20 unités × 5 DT/unité = 100 DT
    _ligne(conn, ids, ids["article"], "20 unités", "70 kg", "5 DT/unité", "100 DT")

    lignes = {
        ligne["article_id"]: ligne
        for ligne in inventaire_initial_service.lignes_inventaire_initial(conn)
    }
    assert {
        a: (lg["unite_cout"], lg["cout_unitaire_minor"], lg["valeur_minor"])
        for a, lg in lignes.items()
    } == {
        article_kg: ("KG", 2500, 2_500_000),
        article_t: ("TONNE", 2_500_000, 2_500_000),
        article_ml: ("ML", 12_000, 720_000),
        ids["article"]: ("UNITE", 5000, 100_000),
    }
    assert valorisation.unite_prix_lot(conn, kg["lot_id"]) == "KG"
    assert (
        cmp(conn, article_kg)["unite_valorisation"],
        cmp(conn, article_kg)["cmp_unitaire_minor"],
    ) == ("KG", 2500)
    assert cmp(conn, article_t)["cmp_unitaire_minor"] == 2_500_000
    assert cmp(conn, article_ml)["cmp_unitaire_minor"] == 12_000
    assert cmp(conn, ids["article"])["cmp_unitaire_minor"] == 5000


def test_inventaire_initial_cout_conserve_dans_son_unite_et_trace(conn, ids):
    """
    Adapté à la décision « Proposition A » : le coût saisi « 2 500 DT/tonne »
    pour un article en DT/kg est CONSERVÉ dans son unité (et non plus converti
    à l'enregistrement) ; la conversion exacte n'a lieu qu'au calcul.
    """
    _inventaire(conn, ids)
    article_kg = nouvel_article(conn, ids, "KG")
    resultat = _ligne(conn, ids, article_kg, "10 pièces", "1 000 kg", "2 500 DT/tonne", "2 500 DT")
    (ligne,) = inventaire_initial_service.lignes_inventaire_initial(conn)
    assert (ligne["unite_cout"], ligne["cout_unitaire_minor"]) == ("TONNE", 2_500_000)
    saisie = json.loads(ligne["saisie_originale"])
    assert saisie["cout_unitaire"]["saisie"] == "2 500 DT/tonne"
    assert (saisie["unite_prix_saisi"], saisie["unite_valorisation"]) == ("TONNE", "KG")
    assert saisie["prix_en_unite_valorisation_exact_minor"] == "2500"
    assert valorisation.unite_prix_lot(conn, resultat["lot_id"]) == "TONNE"
    assert cmp(conn, article_kg)["cmp_unitaire_minor"] == 2500  # CMP en DT/kg


def test_inventaire_initial_refuse_une_autre_unite_ou_une_valeur_incoherente(conn, ids):
    _inventaire(conn, ids)
    article_kg = nouvel_article(conn, ids, "KG")
    article_ml = nouvel_article(conn, ids, "ML")
    sans_unite = nouvel_article(conn, ids, None)
    with pytest.raises(ErreurUniteValorisation, match="aucune conversion implicite"):
        _ligne(conn, ids, article_kg, "10 pièces", "1 000 kg", "250 DT/pièce", "2 500 DT")
    with pytest.raises(ErreurUniteValorisation, match="aucune conversion implicite"):
        _ligne(conn, ids, article_ml, "10 pièces", "60 kg", "2 DT/kg", "120 DT")
    with pytest.raises(ErreurUniteValorisation, match="Aucune unité de valorisation"):
        _ligne(conn, ids, sans_unite, "10 pièces", "60 kg", "2 DT/pièce", "20 DT")
    with pytest.raises(ErreurMontantIncoherent, match="Valeur incohérente"):
        _ligne(conn, ids, article_kg, "10 pièces", "1 000 kg", "2,5 DT/kg", "25 DT")
    assert inventaire_initial_service.lignes_inventaire_initial(conn) == []


def test_inventaire_initial_valeur_arrondie_au_millime_une_seule_fois(conn, ids):
    """1 000,5 kg × 2,501 DT/kg = 2 502,2505 DT -> valeur enregistrée 2 502,251 DT."""
    _inventaire(conn, ids)
    article_kg = nouvel_article(conn, ids, "KG")
    with pytest.raises(ErreurMontantIncoherent, match="2502251"):  # 2 502,250 : pas l'arrondi
        _ligne(conn, ids, article_kg, "10 pièces", "1 000,5 kg", "2,501 DT/kg", "2 502,250 DT")
    _ligne(conn, ids, article_kg, "10 pièces", "1 000,5 kg", "2,501 DT/kg", "2 502,251 DT")
    (ligne,) = inventaire_initial_service.lignes_inventaire_initial(conn)
    assert (ligne["cout_unitaire_minor"], ligne["valeur_minor"]) == (2501, 2_502_251)
    # Le moteur CMP retrouve exactement la même valeur d'entrée (même règle, même arrondi).
    etat = cmp(conn, article_kg)
    assert etat["valeur_totale_minor"] == 2_502_251
    assert etat["cmp_unitaire_minor"] == 2501  # 2 502 251 / 1 000,5 = 2 501,0005 -> 2 501


# ---------------------------------------------------------------------------
# Aucune conversion implicite, aucune unité par défaut, aucun arrondi silencieux
# ---------------------------------------------------------------------------


def test_aucune_unite_par_defaut_ni_conversion_implicite(conn, ids):
    sans_unite = nouvel_article(conn, ids, None)
    with pytest.raises(ErreurUniteValorisation):
        unite_valorisation_service.unite_valorisation(conn, sans_unite)
    with pytest.raises(ErreurUniteValorisation):  # aucun lot sans unité définie
        stock_repository.inserer_lot(
            conn,
            id=nid(),
            article_id=sans_unite,
            finition="NOIR",
            longueur_m=6.0,
            quantite_initiale=1,
            poids_initial_kg=1.0,
            prix_unitaire_provisoire_minor=1,
            prix_unitaire_definitif_minor=None,
            devise="TND",
            lot_parent_id=None,
            bl_fournisseur_ligne_id=None,
            inventaire_initial_ligne_id=nid(),
        )
    conn.rollback()
    with pytest.raises(ErreurUniteValorisation):
        unite_valorisation_service.changer_unite_valorisation(
            conn,
            article_id=sans_unite,
            nouvelle_unite="KG",
            utilisateur_id=ids["utilisateur"],
            motif="x",
        )
    article_kg = nouvel_article(conn, ids, "KG")
    with pytest.raises(ErreurUniteValorisation, match="unité de valorisation en vigueur"):
        stock_repository.inserer_lot(  # un lot au prix « par unité » pour un article au kg
            conn,
            id=nid(),
            article_id=article_kg,
            finition="NOIR",
            longueur_m=6.0,
            quantite_initiale=1,
            poids_initial_kg=1.0,
            prix_unitaire_provisoire_minor=1,
            prix_unitaire_definitif_minor=None,
            devise="TND",
            unite_prix="UNITE",
            inventaire_initial_ligne_id=nid(),
        )
    conn.rollback()
    lot = creer_lot_reception(conn, pour(ids, article_kg), 10, 1000.0, 2000, finition="NOIR")
    with pytest.raises(sqlite3.IntegrityError, match="figée"):
        conn.execute("UPDATE lot SET unite_prix = 'UNITE' WHERE id = ?", (lot["lot_id"],))
    conn.rollback()


# ---------------------------------------------------------------------------
# Arrondi au millime, une seule fois, sur le montant final (règle validée)
# ---------------------------------------------------------------------------


def test_arrondi_entree_de_lot_une_seule_fois(conn, ids):
    article = nouvel_article(conn, ids, "KG")
    # 1 000,5 kg × 2 501 millimes/kg = 2 502 250,5 -> 2 502 251 (0,5 vers le haut)
    lot = reception(conn, ids, article, 10, 1000.5, 2501, "2026-01-05T08:00:00")
    assert valorisation.montant_mouvement_minor(conn, lot["mouvement_id"]) == 2_502_251
    assert cmp(conn, article)["valeur_totale_minor"] == 2_502_251


def _pool_4001_sur_4_kg(conn, ids):
    """Deux lots au kg : 3 kg × 1 000 + 1 kg × 1 001 = 4 001 millimes pour 4 kg."""
    article = nouvel_article(conn, ids, "KG")
    lot_a = reception(conn, ids, article, 3, 3.0, 1000, "2026-01-05T08:00:00")
    reception(conn, ids, article, 1, 1.0, 1001, "2026-01-06T08:00:00")
    return article, lot_a


def test_arrondi_du_cmp_et_d_une_sortie_demi_millime_vers_le_haut(conn, ids):
    article, lot_a = _pool_4001_sur_4_kg(conn, ids)
    assert cmp(conn, article)["cmp_unitaire_minor"] == 1000  # 4 001 / 4 = 1 000,25 -> 1 000
    # Sortie de 2 kg : 4 001 × 2 / 4 = 2 000,5 -> 2 001 (0,5 vers le haut, une seule fois)
    mouvement = sortie(conn, ids, lot_a["lot_id"], 2, 2, "2026-01-10T08:00:00")
    assert valorisation.montant_mouvement_minor(conn, mouvement) == -2001
    assert cmp(conn, article)["valeur_totale_minor"] == 2000  # 4 001 - 2 001, jamais de dérive
    # CMP exactement à mi-chemin : (1 000 + 1 001) / 2 kg = 1 000,5 -> 1 001
    autre = nouvel_article(conn, ids, "KG")
    reception(conn, ids, autre, 1, 1.0, 1000, "2026-01-05T08:00:00")
    reception(conn, ids, autre, 1, 1.0, 1001, "2026-01-06T08:00:00")
    assert cmp(conn, autre)["cmp_unitaire_minor"] == 1001


def test_chute_au_cmp_exact_arrondie_une_seule_fois(conn, ids):
    article, lot_a = _pool_4001_sur_4_kg(conn, ids)
    ids_kg = pour(ids, article)
    envoi = envoyer_transformation(conn, ids_kg, lot_a["lot_id"], 3, 3.0)
    retour = recevoir_transformation(
        conn,
        ids_kg,
        envoi["bst_id"],
        envoi["bstl_id"],
        1,
        1.0,
        2,
        2.0,
        prix_lot_resultat_minor=1000,
    )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    # CMP affiché au départ : 1 000,25 -> 1 000 ; CMP exact conservé : 4 001 / 4
    assert valorisation.cout_chute_unitaire_minor(conn, retour["chute_id"]) == 1000
    # Chute de 2 kg : 2 × 4 001 / 4 = 2 000,5 -> 2 001 (et non 2 × 1 000 = 2 000,
    # qui arrondirait le CMP avant le montant final)
    assert valorisation.cout_chute_total_minor(conn, retour["chute_id"]) == 2001


def test_arrondi_du_cout_reel_d_une_affaire(conn, ids):
    from tests.helpers import affecter, creer_commande, livrer

    article = nouvel_article(conn, ids, "KG")
    ids_kg = pour(ids, article)
    commande = creer_commande(conn, ids_kg, quantite=10, finition="NOIR")
    lot = creer_lot_reception(conn, ids_kg, 10, 1000.5, 2001, finition="NOIR")
    affectation = affecter(
        conn, ids_kg, lot["lot_id"], commande["commande_ligne_id"], "INITIALE", 4, 410.5
    )
    livraison = livrer(
        conn,
        ids_kg,
        lot["lot_id"],
        commande["commande_ligne_id"],
        affectation,
        "INITIALE",
        4,
        410.5,
        commande["commande_id"],
    )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    # 410,5 kg × 2 001 = 821 410,5 -> 821 411
    assert (
        valorisation.cout_sortie_total_minor(conn, livraison["mouvement_id"], lot["lot_id"])
        == 821_411
    )


def test_arrondi_apres_regularisation_fournisseur(conn, ids):
    article = nouvel_article(conn, ids, "KG")
    lot = creer_lot_reception(conn, pour(ids, article), 10, 1000.5, 2501, finition="NOIR")
    stock_service.reconstruire_cmp_apres_transaction(conn)
    assert cmp(conn, article)["valeur_totale_minor"] == 2_502_251  # 2 502 250,5 -> 2 502 251
    regulariser_facture_fournisseur(
        conn, ids, lot["lot_id"], lot["bl_ligne_id"], 2501, 2503, lot_deja_sorti=0
    )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    # 1 000,5 kg × 2 503 = 2 504 251,5 -> 2 504 252 ; CMP 2 503,0005 -> 2 503
    etat = cmp(conn, article)
    assert (etat["valeur_totale_minor"], etat["cmp_unitaire_minor"]) == (2_504_252, 2503)


# ---------------------------------------------------------------------------
# Migration 0019 sur une base contenant déjà des données
# ---------------------------------------------------------------------------


def test_migration_0019_n_invente_aucune_unite_d_article(tmp_path, monkeypatch):
    source = pathlib.Path(migrate.MIGRATIONS_DIR)
    dossier = tmp_path / "migrations"
    dossier.mkdir()
    for fichier in source.glob("*.sql"):
        if fichier.name < "0019":
            shutil.copy(fichier, dossier / fichier.name)
    monkeypatch.setattr(migrate, "MIGRATIONS_DIR", dossier)
    db_path = tmp_path / "avant_0019.db"
    migrate.apply_migrations(db_path, fresh=True)
    brut = sqlite3.connect(str(db_path))
    brut.row_factory = sqlite3.Row
    brut.execute("PRAGMA foreign_keys = ON")
    ids = seed_referentiels(brut)  # schéma antérieur : aucune unité d'article
    lot = creer_lot_reception(brut, ids, 100, 350.0, 5000, finition="NOIR")
    brut.close()

    # Le code courant exige le schéma complet : 0019 puis 0020 sont appliquées
    # ensemble sur la base déjà alimentée (adapté lors de l'ajout de 0020).
    for fichier in ("0019_unite_valorisation_article.sql", "0020_unite_prix_saisie.sql"):
        shutil.copy(source / fichier, dossier / fichier)
    assert migrate.apply_migrations(db_path) == [
        "0019_unite_valorisation_article.sql",
        "0020_unite_prix_saisie.sql",
    ]
    conn = connexion.get_connection(configuration_test(db_path))
    try:
        # FAIT repris : le lot existant était valorisé par pièce.
        assert valorisation.unite_prix_lot(conn, lot["lot_id"]) == "UNITE"
        # Aucune unité d'article inventée, cache vidé (reconstructible).
        assert conn.execute("SELECT COUNT(*) FROM article_unite_valorisation").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM cmp_stock_general").fetchone()[0] == 0
        with pytest.raises(ErreurUniteValorisation, match="non définie"):
            stock_service.reconstruire_cmp_apres_transaction(conn)
        unite_valorisation_service.definir_unite_valorisation(
            conn, article_id=ids["article"], unite="UNITE", utilisateur_id=ids["utilisateur"]
        )
        stock_service.reconstruire_cmp_apres_transaction(conn)
        etat = valorisation.cmp_actuel(conn, ids["article"], "NOIR", 6.0)
        assert etat is not None
        assert (etat["unite_valorisation"], etat["cmp_unitaire_minor"]) == ("UNITE", 5000)
        assert conn.execute("PRAGMA foreign_key_check").fetchall() == []
    finally:
        connexion.fermer(conn)
