"""
Tests obligatoires ADDITIONNELS de la Phase 4.1 (§2 et §3 du cadrage
correctif) : représentation monétaire sur les 3 devises, et règle définitive
des chutes (valorisées au CMP, exclues de la marge individuelle, consolidées
dans un bilan annuel).

Les tests de régularisation fournisseur (§1 : lot totalement en stock / lot
partiellement sorti / lot totalement sorti / vérification du CMP) sont dans
tests/test_scenarios.py (tests 5, 6bis, 6) — ils prolongent directement les
11 tests obligatoires de la Phase 4 et n'ont pas été dupliqués ici.
"""
import sqlite3

import pytest

from db.valorisation import cout_chute_total_minor, reconstruire_cmp
from tests.helpers import (
    creer_commande,
    creer_lot_reception,
    envoyer_transformation,
    eur_usd,
    nid,
    recevoir_transformation,
    seed_referentiels,
    tnd,
)


# ═══════════════════════ § 2 — Les 3 devises ═══════════════════════

def test_tnd_stocke_en_millimes(conn):
    """TND : unité minimale = millime (1/1000). 5,250 TND -> 5250 millimes,
    round-trip exact."""
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.250),
                               devise="TND")
    row = conn.execute(
        "SELECT prix_unitaire_provisoire_minor, devise FROM lot WHERE id = ?", (lot["lot_id"],)
    ).fetchone()
    assert row["prix_unitaire_provisoire_minor"] == 5250
    assert row["devise"] == "TND"


def test_eur_stocke_en_centimes(conn):
    """EUR : unité minimale = centime (1/100). 5,20 EUR -> 520 centimes,
    round-trip exact."""
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=eur_usd(5.20),
                               devise="EUR")
    row = conn.execute(
        "SELECT prix_unitaire_provisoire_minor, devise FROM lot WHERE id = ?", (lot["lot_id"],)
    ).fetchone()
    assert row["prix_unitaire_provisoire_minor"] == 520
    assert row["devise"] == "EUR"


def test_usd_stocke_en_cents(conn):
    """USD : unité minimale = cent (1/100). 5,20 USD -> 520 cents, round-trip
    exact."""
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=eur_usd(5.20),
                               devise="USD")
    row = conn.execute(
        "SELECT prix_unitaire_provisoire_minor, devise FROM lot WHERE id = ?", (lot["lot_id"],)
    ).fetchone()
    assert row["prix_unitaire_provisoire_minor"] == 520
    assert row["devise"] == "USD"


def test_devise_invalide_refusee(conn):
    """La colonne devise est verrouillée aux 3 devises supportées (CHECK) —
    impossible d'insérer une 4e devise par erreur."""
    ids = seed_referentiels(conn)
    with pytest.raises(sqlite3.IntegrityError):
        creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0), devise="MAD")


def test_facture_client_devise_eur_par_defaut(conn):
    """facture_client reste en EUR par défaut (contexte douane/MACF déjà
    validé), montant stocké en centimes entiers."""
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=10)
    facture_id = nid()
    conn.execute(
        "INSERT INTO facture_client (id, numero, commande_client_id, date, montant_minor) VALUES (?,?,?,?,?)",
        (facture_id, f"FAC-2026-{nid()[:8]}", cmd["commande_id"], "2026-01-15", eur_usd(550.25)),
    )
    row = conn.execute("SELECT montant_minor, devise FROM facture_client WHERE id=?", (facture_id,)).fetchone()
    assert row["montant_minor"] == 55025
    assert row["devise"] == "EUR"


def test_pool_cmp_refuse_le_melange_de_devises(conn):
    """
    Garde-fou technique (Phase 4.1 §2, pas une nouvelle règle métier) : un
    pool CMP (article, finition, longueur) est mono-devise. Si deux lots du
    même pool physique portaient des devises différentes, reconstruire_cmp()
    refuse plutôt que d'additionner silencieusement des montants dans des
    devises différentes — cf. db/valorisation.py, note de module.
    """
    ids = seed_referentiels(conn)
    creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0), devise="TND",
                         date_heure="2026-01-01T08:00:00.000")
    creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=eur_usd(5.0), devise="EUR",
                         date_heure="2026-01-02T08:00:00.000")
    with pytest.raises(ValueError, match="[Dd]evise"):
        reconstruire_cmp(conn)


# ═══════════════════════ § 3 — Règle définitive des chutes ═══════════════════════

def _chute_pour_affaire(conn, ids, commande_client_id, quantite_envoyee, quantite_chute, prix_unitaire_minor,
                         date_heure):
    """Construit une transformation complète pour UNE affaire donnée et
    renvoie le chute_id, avec cout_cmp_total_minor déjà calculé et écrit
    (ce que fera le futur service applicatif de la Phase 5)."""
    lot = creer_lot_reception(conn, ids, quantite=quantite_envoyee, poids_kg=quantite_envoyee * 3.5,
                               prix_provisoire_minor=prix_unitaire_minor, date_heure=date_heure)
    envoi = envoyer_transformation(conn, ids, lot["lot_id"], quantite_envoyee, quantite_envoyee * 3.5,
                                    date_heure=date_heure)
    reconstruire_cmp(conn)
    reception = recevoir_transformation(
        conn, ids, envoi["bst_id"], envoi["bstl_id"],
        quantite_recue=quantite_envoyee - quantite_chute, poids_recu_kg=(quantite_envoyee - quantite_chute) * 3.5,
        quantite_chute=quantite_chute, poids_chute_kg=quantite_chute * 3.5,
        prix_lot_resultat_minor=prix_unitaire_minor, date_heure=date_heure,
        commande_client_id=commande_client_id,
    )
    cout_total = cout_chute_total_minor(conn, reception["chute_id"])
    conn.execute("UPDATE chute SET cout_cmp_total_minor = ? WHERE id = ?", (cout_total, reception["chute_id"]))
    conn.commit()
    return reception["chute_id"], cout_total


def test_chute_valorisee_au_cmp_et_sort_du_stock_normal(conn):
    """La chute est valorisée au CMP du moment, et la quantité correspondante
    a bien quitté STOCK_GMC (le pool général diminue de la quantité totale
    envoyée en transformation, chute comprise)."""
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=100, poids_kg=350, prix_provisoire_minor=tnd(5.0),
                               date_heure="2026-01-01T08:00:00.000")
    envoi = envoyer_transformation(conn, ids, lot["lot_id"], 100, 350, date_heure="2026-01-02T08:00:00.000")
    pools_avant = reconstruire_cmp(conn)
    key = (ids["article"], "GALVA", 6.0)
    assert pools_avant[key]["quantite_totale"] == 0  # tout envoyé en transformation, plus rien en STOCK_GMC

    reception = recevoir_transformation(conn, ids, envoi["bst_id"], envoi["bstl_id"],
                                         quantite_recue=95, poids_recu_kg=332.5,
                                         quantite_chute=5, poids_chute_kg=17.5,
                                         prix_lot_resultat_minor=tnd(5.3),
                                         date_heure="2026-01-10T08:00:00.000")
    cout_total = cout_chute_total_minor(conn, reception["chute_id"])
    assert cout_total == 5 * tnd(5.0)  # valorisée au CMP du moment de l'envoi (5,00), pas du retour (5,30)


def test_chute_tracable_par_affaire_article_transformation_date(conn):
    """La chute reste traçable par affaire (commande_client_id), par article
    (via le lot), par transformation (transformateur_id) et par date."""
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=100)
    chute_id, _ = _chute_pour_affaire(conn, ids, cmd["commande_id"], quantite_envoyee=100, quantite_chute=5,
                                       prix_unitaire_minor=tnd(5.0), date_heure="2026-03-01T08:00:00.000")
    row = conn.execute(
        """SELECT c.commande_client_id, c.transformateur_id, c.date, l.article_id
           FROM chute c JOIN lot l ON l.id = c.lot_id WHERE c.id = ?""",
        (chute_id,),
    ).fetchone()
    assert row["commande_client_id"] == cmd["commande_id"]
    assert row["transformateur_id"] == ids["transformateur"]
    assert row["article_id"] == ids["article"]
    assert row["date"].startswith("2026-03-01")


def test_chute_sans_impact_immediat_sur_marge_individuelle(conn):
    """
    Le coût de chute n'est PAS intégré automatiquement à la marge de
    l'affaire : impact_marge_valide reste à 0 par défaut (jamais mis à 1 par
    le moteur lui-même), et aucune autre table (notamment commande_client, qui
    ne porte d'ailleurs aucune colonne de marge) n'est modifiée par la
    création ou la valorisation d'une chute.
    """
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=100)
    avant = dict(conn.execute("SELECT * FROM commande_client WHERE id = ?", (cmd["commande_id"],)).fetchone())

    chute_id, cout_total = _chute_pour_affaire(conn, ids, cmd["commande_id"], quantite_envoyee=100,
                                                quantite_chute=5, prix_unitaire_minor=tnd(5.0),
                                                date_heure="2026-03-01T08:00:00.000")
    assert cout_total > 0

    impact = conn.execute("SELECT impact_marge_valide FROM chute WHERE id = ?", (chute_id,)).fetchone()[0]
    assert impact == 0

    apres = dict(conn.execute("SELECT * FROM commande_client WHERE id = ?", (cmd["commande_id"],)).fetchone())
    assert avant == apres  # rien n'a changé sur l'affaire elle-même


def test_bilan_consolide_annuel_des_chutes(conn):
    """
    §3 — exemple du cadrage (proportions identiques, échelle x10 pour rester
    en quantités entières) : trois affaires, trois chutes valorisées au CMP,
    même prix unitaire (1,000 TND) pour isoler le calcul de consolidation :
      Affaire A : 25 unités de chute -> 25,000 TND
      Affaire B : 12 unités de chute -> 12,000 TND
      Affaire C :  8 unités de chute ->  8,000 TND
      Bilan consolidé annuel 2026    -> 45,000 TND (= 25+12+8, comme
                                          2500+1200+800=4500 dans le cadrage)
    v_bilan_chutes_annuel (migration 0016) permet de produire ce total à tout
    moment, sans jamais toucher à la marge d'aucune affaire individuelle.
    """
    ids = seed_referentiels(conn)
    cmd_a = creer_commande(conn, ids, quantite=100)
    cmd_b = creer_commande(conn, ids, quantite=100)
    cmd_c = creer_commande(conn, ids, quantite=100)

    prix = tnd(1.0)  # 1,000 TND/unité, identique pour les 3 -> isole la consolidation de tout effet CMP
    _, cout_a = _chute_pour_affaire(conn, ids, cmd_a["commande_id"], 100, 25, prix, "2026-01-05T08:00:00.000")
    _, cout_b = _chute_pour_affaire(conn, ids, cmd_b["commande_id"], 100, 12, prix, "2026-04-10T08:00:00.000")
    _, cout_c = _chute_pour_affaire(conn, ids, cmd_c["commande_id"], 100, 8, prix, "2026-09-20T08:00:00.000")

    assert (cout_a, cout_b, cout_c) == (25 * prix, 12 * prix, 8 * prix)

    bilan = conn.execute(
        "SELECT nombre_chutes, quantite_totale, cout_total_minor FROM v_bilan_chutes_annuel "
        "WHERE annee = '2026' AND devise = 'TND'"
    ).fetchone()
    assert bilan["nombre_chutes"] == 3
    assert bilan["quantite_totale"] == 25 + 12 + 8
    assert bilan["cout_total_minor"] == cout_a + cout_b + cout_c == 45 * prix

    # Aucune affaire individuelle n'a été modifiée par cette consolidation :
    for cmd_id in (cmd_a["commande_id"], cmd_b["commande_id"], cmd_c["commande_id"]):
        statut = conn.execute("SELECT statut FROM commande_client WHERE id=?", (cmd_id,)).fetchone()[0]
        assert statut == "CONFIRMEE"
