"""
Tests Phase 5.5 (dernière correction) — décision validée « Proposition A » :
le prix unitaire est conservé dans l'unité où il a été réellement saisi
lorsque la conversion vers l'unité de valorisation est physique et exacte
(kg <-> tonne) ; le prix saisi n'est jamais arrondi ; la conversion n'a lieu
qu'au moment du calcul, sans arrondi intermédiaire ; seul le montant final
est arrondi au millime. Représentation monétaire globale inchangée.

Cas obligatoire : article en DT/kg, prix fournisseur 2 500,5 DT/t, 1 000,3 kg
-> 1 000,3 × 2,5005 = 2 501,25015 DT -> 2 501,250 DT (et non 2 501,750 DT,
résultat d'une conversion prématurée en 2,501 DT/kg).

Montants attendus calculés à la main dans les commentaires (millimes).
"""

from __future__ import annotations

import fractions
import json
import pathlib
import shutil
import sqlite3

import pytest

from core import unites
from core.configuration import configuration_test
from core.erreurs import (
    ErreurEnregistrementImmuable,
    ErreurMontantIncoherent,
    ErreurUniteValorisation,
    traduire_erreur_sqlite,
)
from db import connexion, migrate, valorisation
from repositories import stock_repository
from services import inventaire_initial_service, stock_service, unite_valorisation_service
from tests.helpers import (
    affecter,
    creer_commande,
    envoyer_transformation,
    livrer,
    nid,
    recevoir_transformation,
    regulariser_facture_fournisseur,
    seed_referentiels,
)

F = fractions.Fraction
STOCK = stock_service.STOCK_GMC
MESSAGE_PRIX = (
    "Un prix unitaire n'est jamais arrondi. Saisissez le prix avec une précision "
    "représentable dans son unité d'origine."
)


@pytest.fixture()
def conn(tmp_path):
    db_path = tmp_path / "gmc_prix_saisis.db"
    migrate.apply_migrations(db_path, fresh=True)
    c = connexion.get_connection(configuration_test(db_path))
    c.row_factory = sqlite3.Row
    yield c
    connexion.fermer(c)


@pytest.fixture()
def ids(conn):
    return seed_referentiels(conn)


def article(conn, ids, unite) -> str:
    article_id = nid()
    conn.execute(
        "INSERT INTO article (id, designation, famille_id, masse_lineique_kg_m) VALUES (?,?,?,?)",
        (article_id, f"Article {unite} {article_id[:4]}", ids["famille"], 10.0),
    )
    conn.commit()
    unite_valorisation_service.definir_unite_valorisation(
        conn, article_id=article_id, unite=unite, utilisateur_id=ids["utilisateur"]
    )
    return article_id


def reception(conn, ids, article_id, quantite, poids, prix, unite_prix, date_heure):
    """BL + lot au prix saisi dans `unite_prix` + entrée via le Stock Service."""
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
        (ligne_id, bl_id, article_id, "NOIR", 6.0, quantite, poids, prix, "TND"),
    )
    stock_repository.inserer_lot(
        conn,
        id=lot_id,
        article_id=article_id,
        finition="NOIR",
        longueur_m=6.0,
        quantite_initiale=quantite,
        poids_initial_kg=poids,
        prix_unitaire_provisoire_minor=prix,
        prix_unitaire_definitif_minor=None,
        devise="TND",
        bl_fournisseur_ligne_id=ligne_id,
        unite_prix=unite_prix,
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
    return {"lot_id": lot_id, "bl_ligne_id": ligne_id, "mouvement_id": mouvement_id}


def lot_2500_5_par_tonne(conn, ids):
    """Cas obligatoire : article en DT/kg, lot de 1 000,3 kg à 2 500,5 DT/t."""
    article_kg = article(conn, ids, "KG")
    lot = reception(conn, ids, article_kg, 10, 1000.3, 2_500_500, "TONNE", "2026-01-05T08:00:00")
    return article_kg, lot


def etat_cmp(conn, article_id) -> dict:
    etat = valorisation.cmp_actuel(conn, article_id, "NOIR", 6.0)
    assert etat is not None
    return etat


# ---------------------------------------------------------------------------
# Cas obligatoire et conversions kg <-> tonne
# ---------------------------------------------------------------------------


def test_cas_obligatoire_2500_5_dt_par_tonne_article_au_kg(conn, ids):
    article_kg, lot = lot_2500_5_par_tonne(conn, ids)
    # Le lot conserve le prix saisi, son unité d'origine et l'unité de l'article.
    donnees = stock_repository.obtenir_lot(conn, lot["lot_id"])
    assert donnees["prix_unitaire_provisoire_minor"] == 2_500_500
    assert donnees["unite_prix"] == "TONNE"
    assert donnees["unite_valorisation_article"] == "KG"
    # Conversion au calcul : 2 500,5 DT/t ÷ 1000 = 2,5005 DT/kg, exactement.
    assert valorisation.cout_reel_lot_exact(conn, lot["lot_id"], "KG") == F("2500.5")
    # 1 000,3 × 2 500,5 = 2 501 250,15 millimes -> 2 501 250 (2 501,250 DT)
    assert valorisation.montant_mouvement_minor(conn, lot["mouvement_id"]) == 2_501_250
    assert etat_cmp(conn, article_kg)["valeur_totale_minor"] == 2_501_250
    assert etat_cmp(conn, article_kg)["unite_valorisation"] == "KG"  # CMP en DT/kg
    # Conversion prématurée en 2,501 DT/kg : 2 501 750,3 -> 2 501 750 (0,500 DT d'écart)
    assert valorisation.montant_arrondi_minor(F("1000.3"), 2501) == 2_501_750


def test_conversion_exacte_dans_les_deux_sens(conn, ids):
    # tonne -> kg et kg -> tonne, sans arrondi
    assert valorisation.convertir_prix_exact(2_500_500, "TONNE", "KG") == F("2500.5")
    assert valorisation.convertir_prix_exact(F("2500.5"), "KG", "TONNE") == 2_500_500
    assert valorisation.convertir_prix_exact(2501, "KG", "TONNE") == 2_501_000
    # même unité : aucune conversion
    assert valorisation.convertir_prix_exact(2_500_500, "TONNE", "TONNE") == 2_500_500
    assert valorisation.convertir_prix_exact(2501, "KG", "KG") == 2501
    with pytest.raises(valorisation.UniteValorisationError, match="implicite"):
        valorisation.convertir_prix_exact(5000, "UNITE", "KG")
    # Article en DT/tonne, prix saisi au kg (2,501 DT/kg, exact dans son unité)
    article_t = article(conn, ids, "TONNE")
    lot = reception(conn, ids, article_t, 10, 1000.3, 2501, "KG", "2026-01-05T08:00:00")
    assert stock_repository.obtenir_lot(conn, lot["lot_id"])["unite_prix"] == "KG"
    assert valorisation.cout_reel_lot_exact(conn, lot["lot_id"], "TONNE") == 2_501_000
    # 1 000,3 × 2 501 = 2 501 750,3 -> 2 501 750 ; CMP 2 501 750 / 1,0003 t -> 2 501 000
    assert valorisation.montant_mouvement_minor(conn, lot["mouvement_id"]) == 2_501_750
    etat = etat_cmp(conn, article_t)
    assert (etat["unite_valorisation"], etat["cmp_unitaire_minor"]) == ("TONNE", 2_501_000)


def test_prix_saisi_conserve_dans_son_unite_jamais_arrondi():
    assert unites.prix_saisi(unites.lire("2 500,5 DT/tonne")) == (2_500_500, "TONNE")
    assert unites.prix_saisi(unites.lire("2,80 DT/kg")) == (2800, "KG")
    assert unites.prix_saisi(unites.lire("1,50 DT/ml")) == (1500, "ML")
    assert unites.prix_saisi(unites.lire("5 DT/unité")) == (5000, "UNITE")
    # tonne -> tonne, kg -> kg : aucune conversion ; kg <-> tonne : compatibles
    for unite_prix, unite_article, compatible in (
        ("TONNE", "TONNE", True),
        ("KG", "KG", True),
        ("TONNE", "KG", True),
        ("KG", "TONNE", True),
        ("UNITE", "KG", False),
        ("ML", "TONNE", False),
        ("KG", "ML", False),
    ):
        assert unites.unites_de_prix_compatibles(unite_prix, unite_article) is compatible


def test_prix_plus_fin_que_le_millime_dans_sa_propre_unite_refuse():
    # 2 500,5005 DT/t n'est pas représentable en millimes par tonne : refusé, jamais arrondi
    with pytest.raises(ErreurMontantIncoherent) as exc:
        unites.prix_saisi(unites.lire("2 500,5005 DT/t"))
    assert MESSAGE_PRIX in str(exc.value)
    assert "aucune règle d'arrondi n'est validée" not in str(exc.value)  # message obsolète retiré
    # 2,5005 DT/kg saisi au kg : même situation (2 500,5 millimes/kg) ; saisi à la tonne,
    # le même prix (2 500,5 DT/t) est représentable et accepté.
    with pytest.raises(ErreurMontantIncoherent, match="jamais arrondi"):
        unites.prix_saisi(unites.lire("2,5005 DT/kg"))
    assert unites.prix_saisi(unites.lire("2 500,5 DT/t")) == (2_500_500, "TONNE")


# ---------------------------------------------------------------------------
# CMP, régularisation, coût d'affaire, chute, vente
# ---------------------------------------------------------------------------


def test_cmp_en_dt_par_kg_avec_des_lots_de_prix_en_tonne_et_en_kg(conn, ids):
    article_kg, lot_a = lot_2500_5_par_tonne(conn, ids)
    reception(conn, ids, article_kg, 5, 500.0, 2400, "KG", "2026-01-06T08:00:00")
    # 2 501 250 + 500 × 2 400 = 3 701 250 pour 1 500,3 kg -> 2 466,99… -> 2 467 millimes/kg
    etat = etat_cmp(conn, article_kg)
    assert (etat["unite_valorisation"], etat["valeur_totale_minor"]) == ("KG", 3_701_250)
    assert etat["cmp_unitaire_minor"] == 2467
    # Sortie de 300,3 kg : 3 701 250 × 300,3 / 1 500,3 = 740 842,08 -> 740 842
    mouvement = stock_service.corriger_inventaire(
        conn,
        lot_id=lot_a["lot_id"],
        sens="NEGATIVE",
        quantite="3 pièces",
        poids="300,3 kg",
        emplacement=STOCK,
        motif="Test",
        utilisateur_id=ids["utilisateur"],
        date_heure="2026-01-10T08:00:00",
    )
    assert valorisation.montant_mouvement_minor(conn, mouvement) == -740_842


def test_regularisation_prix_dans_leur_unite_d_origine(conn, ids):
    article_kg, lot = lot_2500_5_par_tonne(conn, ids)
    # BL 2 500,5 DT/t, facture 2 600,5 DT/t : les deux prix restent à la tonne
    regulariser_facture_fournisseur(
        conn, ids, lot["lot_id"], lot["bl_ligne_id"], 2_500_500, 2_600_500, lot_deja_sorti=0
    )
    ligne = conn.execute(
        "SELECT prix_provisoire_minor, unite_prix_provisoire, prix_definitif_minor, "
        "unite_prix_definitif, ecart_unitaire_minor, unite_ecart "
        "FROM regularisation_prix_fournisseur WHERE lot_id = ?",
        (lot["lot_id"],),
    ).fetchone()
    assert tuple(ligne) == (2_500_500, "TONNE", 2_600_500, "TONNE", 100_000, "TONNE")
    donnees = stock_repository.obtenir_lot(conn, lot["lot_id"])
    assert (donnees["prix_unitaire_definitif_minor"], donnees["unite_prix_definitif"]) == (
        2_600_500,
        "TONNE",
    )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    # 1,0003 t × 2 600 500 = 2 601 280,15 -> 2 601 280
    assert etat_cmp(conn, article_kg)["valeur_totale_minor"] == 2_601_280


def test_regularisation_facture_dans_une_autre_unite_de_masse(conn, ids):
    article_kg, lot = lot_2500_5_par_tonne(conn, ids)
    # BL 2 500,5 DT/t, facture 2,601 DT/kg : chaque prix garde son unité ; écart exact à la
    # tonne (seule unité où les deux sont entiers) : 2 601 000 - 2 500 500 = 100 500 /t
    regulariser_facture_fournisseur(
        conn,
        ids,
        lot["lot_id"],
        lot["bl_ligne_id"],
        2_500_500,
        2601,
        lot_deja_sorti=0,
        unite_prix_definitif="KG",
    )
    ligne = conn.execute(
        "SELECT unite_prix_provisoire, unite_prix_definitif, ecart_unitaire_minor, unite_ecart "
        "FROM regularisation_prix_fournisseur WHERE lot_id = ?",
        (lot["lot_id"],),
    ).fetchone()
    assert tuple(ligne) == ("TONNE", "KG", 100_500, "TONNE")
    stock_service.reconstruire_cmp_apres_transaction(conn)
    # 1 000,3 kg × 2 601 = 2 601 780,3 -> 2 601 780
    assert etat_cmp(conn, article_kg)["valeur_totale_minor"] == 2_601_780
    # La base refuse un écart incohérent ou des unités incompatibles.
    facture_ligne = conn.execute(
        "SELECT facture_fournisseur_ligne_id FROM regularisation_prix_fournisseur"
    ).fetchone()[0]
    for unite_def, ecart, unite_ecart in (("KG", 100, "KG"), ("UNITE", 0, "UNITE")):
        with pytest.raises(sqlite3.IntegrityError, match="régularisation refusée"):
            conn.execute(
                "INSERT INTO regularisation_prix_fournisseur (id, facture_fournisseur_ligne_id, "
                "lot_id, prix_provisoire_minor, prix_definitif_minor, ecart_unitaire_minor, "
                "lot_deja_sorti, impact_analytique, unite_prix_provisoire, unite_prix_definitif, "
                "unite_ecart) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    nid(),
                    facture_ligne + "x",
                    lot["lot_id"],
                    2_500_500,
                    2601,
                    ecart,
                    1,
                    "ECART_SEPARE",
                    "TONNE",
                    unite_def,
                    unite_ecart,
                ),
            )
    conn.rollback()


def test_cout_d_affaire_converti_exactement_puis_arrondi(conn, ids):
    article_kg, lot = lot_2500_5_par_tonne(conn, ids)
    ids_kg = dict(ids, article=article_kg)
    commande = creer_commande(conn, ids_kg, quantite=10, finition="NOIR")
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
    detail = valorisation.cout_sortie_detail(conn, livraison["mouvement_id"], lot["lot_id"])
    assert detail == {"cout_unitaire_minor": 2_500_500, "unite": "TONNE"}
    # 410,5 kg × 2,5005 DT/kg = 1 026,45525 DT -> 1 026,455 DT (prématuré : 1 026,661 DT)
    assert (
        valorisation.cout_sortie_total_minor(conn, livraison["mouvement_id"], lot["lot_id"])
        == 1_026_455
    )
    assert valorisation.montant_arrondi_minor(F("410.5"), 2501) == 1_026_661


def test_chute_au_cmp_exact_avec_un_lot_prix_a_la_tonne(conn, ids):
    article_kg, lot = lot_2500_5_par_tonne(conn, ids)
    ids_kg = dict(ids, article=article_kg)
    envoi = envoyer_transformation(conn, ids_kg, lot["lot_id"], 6, 600.18)
    retour = recevoir_transformation(
        conn,
        ids_kg,
        envoi["bst_id"],
        envoi["bstl_id"],
        1,
        99.88,
        5,
        500.3,
        prix_lot_resultat_minor=2500,
    )
    stock_service.reconstruire_cmp_apres_transaction(conn)
    cmp_exact, unite = valorisation.cmp_exact_au_moment_du_mouvement(conn, envoi["mouvement_id"])
    assert (cmp_exact, unite) == (F(2_501_250) / F("1000.3"), "KG")
    # 500,3 kg × 2 501 250 / 1 000,3 = 1 250 999,87 -> 1 251 000
    assert valorisation.cout_chute_total_minor(conn, retour["chute_id"]) == 1_251_000
    # Le CMP affiché (arrondi) n'est jamais réutilisé : il aurait donné 1 250 750
    affiche = valorisation.cout_chute_unitaire_minor(conn, retour["chute_id"])
    assert valorisation.montant_arrondi_minor(F("500.3"), affiche) == 1_250_750


def test_vente_au_poids_arrondie_une_seule_fois():
    prix = unites.lire("2 500,5 DT/tonne")
    for masse in ("1 000,3 kg", "1,0003 t"):
        assert unites.montant_minor_masse_prix(unites.lire(masse), prix) == 2_501_250
    assert unites.montant_minor_masse_prix(
        unites.lire("1 000,3 kg"), unites.lire("2,501 DT/kg")
    ) == (2_501_750)


# ---------------------------------------------------------------------------
# Inventaire initial
# ---------------------------------------------------------------------------


def test_inventaire_initial_prix_2500_5_par_tonne_article_au_kg(conn, ids):
    inventaire_initial_service.creer_inventaire_initial(
        conn,
        date_heure_mise_en_service="2026-01-01T08:00:00+01:00",
        utilisateur_id=ids["utilisateur"],
    )
    article_kg = article(conn, ids, "KG")
    arguments = {
        "article_id": article_kg,
        "finition": "NOIR",
        "longueur": "6 m",
        "quantite": "10 pièces",
        "poids": "1 000,3 kg",
        "emplacement": STOCK,
        "cout_unitaire": "2 500,5 DT/tonne",
        "utilisateur_id": ids["utilisateur"],
    }
    # 2 501,750 DT serait le résultat d'une conversion prématurée en 2,501 DT/kg : refusé.
    with pytest.raises(ErreurMontantIncoherent, match="Valeur incohérente"):
        inventaire_initial_service.ajouter_ligne_inventaire_initial(
            conn, valeur="2 501,750 DT", **arguments
        )
    resultat = inventaire_initial_service.ajouter_ligne_inventaire_initial(
        conn, valeur="2 501,250 DT", **arguments
    )
    (ligne,) = inventaire_initial_service.lignes_inventaire_initial(conn)
    assert (ligne["cout_unitaire_minor"], ligne["unite_cout"], ligne["valeur_minor"]) == (
        2_500_500,
        "TONNE",
        2_501_250,
    )
    saisie = json.loads(ligne["saisie_originale"])
    assert saisie["cout_unitaire"]["saisie"] == "2 500,5 DT/tonne"  # valeur et unité saisies
    assert (saisie["unite_prix_saisi"], saisie["prix_saisi_minor"]) == ("TONNE", 2_500_500)
    assert saisie["unite_valorisation"] == "KG"
    assert saisie["conversion"] == "TONNE -> KG (÷ 1000, exacte)"
    assert saisie["prix_en_unite_valorisation_exact_minor"] == "2500.5"  # jamais 2501
    assert saisie["valeur_calculee_exacte_minor"] == "2501250.15"
    assert saisie["valeur_arrondie_minor"] == 2_501_250
    donnees = stock_repository.obtenir_lot(conn, resultat["lot_id"])
    assert (donnees["unite_prix"], donnees["unite_prix_definitif"]) == ("TONNE", "TONNE")
    assert donnees["unite_valorisation_article"] == "KG"
    assert etat_cmp(conn, article_kg)["valeur_totale_minor"] == 2_501_250


def test_inventaire_initial_sans_conversion_et_conversion_implicite_refusee(conn, ids):
    inventaire_initial_service.creer_inventaire_initial(
        conn,
        date_heure_mise_en_service="2026-01-01T08:00:00+01:00",
        utilisateur_id=ids["utilisateur"],
    )
    article_t = article(conn, ids, "TONNE")
    communs = {
        "finition": "NOIR",
        "longueur": "6 m",
        "quantite": "10 pièces",
        "emplacement": STOCK,
        "utilisateur_id": ids["utilisateur"],
    }
    # tonne -> tonne : aucune conversion
    inventaire_initial_service.ajouter_ligne_inventaire_initial(
        conn,
        article_id=article_t,
        poids="1 t",
        cout_unitaire="2 500,5 DT/t",
        valeur="2 500,500 DT",
        **communs,
    )
    saisie = json.loads(
        inventaire_initial_service.lignes_inventaire_initial(conn)[0]["saisie_originale"]
    )
    assert saisie["conversion"] == "aucune"
    # pièce -> kg : conversion implicite, refusée
    with pytest.raises(ErreurUniteValorisation, match="aucune conversion implicite"):
        inventaire_initial_service.ajouter_ligne_inventaire_initial(
            conn,
            article_id=article(conn, ids, "KG"),
            poids="60 kg",
            cout_unitaire="25 DT/pièce",
            valeur="250 DT",
            **communs,
        )


# ---------------------------------------------------------------------------
# Modèle du lot et garde-fou « montant monétaire entier » (migration 0020)
# ---------------------------------------------------------------------------


def test_lot_conserve_ses_unites_et_refuse_une_unite_incompatible(conn, ids):
    article_kg, lot = lot_2500_5_par_tonne(conn, ids)
    with pytest.raises(sqlite3.IntegrityError) as exc:
        conn.execute(
            "UPDATE lot SET unite_valorisation_article = 'TONNE' WHERE id = ?", (lot["lot_id"],)
        )
    assert isinstance(traduire_erreur_sqlite(exc.value), ErreurEnregistrementImmuable)
    with pytest.raises(sqlite3.IntegrityError, match="doit porter son unité"):
        conn.execute(
            "UPDATE lot SET prix_unitaire_definitif_minor = 2600500 WHERE id = ?", (lot["lot_id"],)
        )
    conn.rollback()
    with pytest.raises(ErreurUniteValorisation):
        stock_repository.inserer_lot(
            conn,
            id=nid(),
            article_id=article_kg,
            finition="NOIR",
            longueur_m=6.0,
            quantite_initiale=1,
            poids_initial_kg=1.0,
            prix_unitaire_provisoire_minor=1500,
            prix_unitaire_definitif_minor=None,
            devise="TND",
            unite_prix="ML",
            inventaire_initial_ligne_id=nid(),
        )
    conn.rollback()


def test_garde_fou_montant_monetaire_entier(conn, ids):
    article_kg, lot = lot_2500_5_par_tonne(conn, ids)
    # Vérifié avant 0020 : 2500.5 était accepté (stocké en REAL). Désormais refusé.
    with pytest.raises(sqlite3.IntegrityError, match="montant monétaire non entier") as exc:
        conn.execute(
            "INSERT INTO lot (id, article_id, inventaire_initial_ligne_id, finition, longueur_m, "
            "quantite_initiale, poids_initial_kg, prix_unitaire_provisoire_minor, devise) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (nid(), article_kg, nid(), "NOIR", 6.0, 10, 1000.3, 2500.5, "TND"),
        )
    assert isinstance(traduire_erreur_sqlite(exc.value), ErreurMontantIncoherent)
    with pytest.raises(sqlite3.IntegrityError, match="montant monétaire non entier"):
        conn.execute(
            "UPDATE lot SET prix_unitaire_definitif_minor = 2600.5, unite_prix_definitif = 'TONNE' "
            "WHERE id = ?",
            (lot["lot_id"],),
        )
    with pytest.raises(sqlite3.IntegrityError, match="montant monétaire non entier"):
        conn.execute(
            "UPDATE bl_fournisseur_ligne SET prix_unitaire_provisoire_minor = 2500.5 WHERE id = ?",
            (lot["bl_ligne_id"],),
        )
    conn.rollback()
    # Un entier écrit sous forme 2500.0 reste un entier (conversion sans perte par SQLite).
    conn.execute(
        "UPDATE bl_fournisseur_ligne SET prix_unitaire_provisoire_minor = 2500500.0 WHERE id = ?",
        (lot["bl_ligne_id"],),
    )
    conn.rollback()


def test_toutes_les_colonnes_monetaires_sont_protegees(conn):
    declencheurs = "\n".join(
        sql for (sql,) in conn.execute("SELECT sql FROM sqlite_master WHERE type = 'trigger'")
    )
    colonnes = [
        (table, colonne)
        for (table,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
        for colonne in (r[1] for r in conn.execute(f"PRAGMA table_info('{table}')"))
        if colonne.endswith("_minor")
    ]
    assert len(colonnes) == 28
    for table, colonne in colonnes:
        for moment in ("insert", "update"):
            assert f"trg_{table}_minor_entier_{moment}" in declencheurs, (table, moment)
        assert f"typeof(NEW.{colonne})" in declencheurs, (table, colonne)


# ---------------------------------------------------------------------------
# Migration 0020 sur une base contenant déjà des données
# ---------------------------------------------------------------------------


def _base_avant_0020(tmp_path, monkeypatch):
    source = pathlib.Path(migrate.MIGRATIONS_DIR)
    dossier = tmp_path / "migrations"
    dossier.mkdir()
    for fichier in source.glob("*.sql"):
        if fichier.name < "0020":
            shutil.copy(fichier, dossier / fichier.name)
    monkeypatch.setattr(migrate, "MIGRATIONS_DIR", dossier)
    db_path = tmp_path / "avant_0020.db"
    migrate.apply_migrations(db_path, fresh=True)
    brut = sqlite3.connect(str(db_path))
    brut.row_factory = sqlite3.Row
    brut.execute("PRAGMA foreign_keys = ON")
    return source, dossier, db_path, brut


def _lot_brut(brut, ids, prix):
    lot_id = nid()
    brut.execute(
        "INSERT INTO lot (id, article_id, inventaire_initial_ligne_id, finition, longueur_m, "
        "quantite_initiale, poids_initial_kg, prix_unitaire_provisoire_minor, "
        "prix_unitaire_definitif_minor, devise) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (lot_id, ids["article"], nid(), "NOIR", 6.0, 10, 35.0, prix, prix, "TND"),
    )
    return lot_id


def test_migration_0020_reprend_les_faits_existants(tmp_path, monkeypatch):
    source, dossier, db_path, brut = _base_avant_0020(tmp_path, monkeypatch)
    ids = seed_referentiels(brut)  # article de test valorisé en UNITE
    brut.execute("PRAGMA foreign_keys = OFF")
    lot_id = _lot_brut(brut, ids, 5000)
    brut.commit()
    brut.close()
    shutil.copy(source / "0020_unite_prix_saisie.sql", dossier / "0020_unite_prix_saisie.sql")
    assert migrate.apply_migrations(db_path) == ["0020_unite_prix_saisie.sql"]
    conn = connexion.get_connection(configuration_test(db_path))
    try:
        donnees = stock_repository.obtenir_lot(conn, lot_id)
        assert (donnees["unite_prix"], donnees["unite_prix_definitif"]) == ("UNITE", "UNITE")
        assert donnees["unite_valorisation_article"] == "UNITE"
    finally:
        connexion.fermer(conn)


def test_migration_0020_refuse_une_base_contenant_un_prix_non_entier(tmp_path, monkeypatch):
    source, dossier, db_path, brut = _base_avant_0020(tmp_path, monkeypatch)
    ids = seed_referentiels(brut)
    brut.execute("PRAGMA foreign_keys = OFF")
    _lot_brut(brut, ids, 2500.5)  # accepté avant 0020 (REAL dans une colonne INTEGER)
    brut.commit()
    brut.close()
    shutil.copy(source / "0020_unite_prix_saisie.sql", dossier / "0020_unite_prix_saisie.sql")
    with pytest.raises(SystemExit, match="CHECK constraint failed"):
        migrate.apply_migrations(db_path)
    verification = sqlite3.connect(str(db_path))
    try:
        appliquees = {r[0] for r in verification.execute("SELECT filename FROM schema_migrations")}
        assert "0020_unite_prix_saisie.sql" not in appliquees
        colonnes = {r[1] for r in verification.execute("PRAGMA table_info('lot')")}
        assert "unite_prix_definitif" not in colonnes  # rien n'a été modifié
    finally:
        verification.close()
