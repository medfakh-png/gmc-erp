"""
Les 11 tests obligatoires de la Phase 4 (section 5 du message de cadrage) :
  1-7 : les 7 scénarios anti-double-comptage du "point critique" Phase 3 §7.
  8-11 : les 4 tests de la nouvelle règle de valorisation CMP (remplace FIFO).

Chaque test construit ses propres données minimales via tests/helpers.py —
ce ne sont pas des modules métier, juste ce qu'il faut pour prouver que le
schéma + les triggers + le moteur de valorisation se comportent exactement
comme spécifié.

PHASE 4.1 — ADAPTATION (§5 du cadrage correctif) : tous les montants sont
désormais des ENTIERS en unité monétaire minimale (tnd()/eur_usd() dans
tests/helpers.py servent uniquement à écrire les montants de façon lisible,
ex. tnd(5.0) = 5000 millimes). Les comparaisons `pytest.approx(...)` sur des
montants deviennent des égalités EXACTES (`==`) — c'est précisément le gain
de précision apporté par la Phase 4.1 §2 : il n'y a plus d'arrondi flottant à
tolérer. Aucun test n'a été supprimé ; seule l'écriture des montants et les
noms des fonctions de `db/valorisation.py` ont changé (cf. CHANGELOG.md pour
le détail de chaque renommage et pourquoi).
"""
import pytest

from db.valorisation import (
    cmp_actuel_minor,
    cout_chute_total_minor,
    cout_chute_unitaire_minor,
    cout_reel_lot_minor,
    cout_sortie_minor,
    cout_sortie_total_minor,
    reconstruire_cmp,
)
from tests.helpers import (
    affecter,
    creer_commande,
    creer_lot_reception,
    envoyer_transformation,
    livrer,
    nid,
    reaffecter,
    recevoir_transformation,
    regulariser_facture_fournisseur,
    seed_referentiels,
    tnd,
)


# ───────────────────────── Test 1 ─────────────────────────
# Commande de 100, couverte par deux BL fournisseur F1=60 / F2=40 -> deux lots
# distincts. La somme ne double-compte jamais : chaque lot a sa propre ligne
# de BL, chaque affectation référence le bon lot, le total affecté = 100 pile.
def test_1_commande_100_deux_bl_60_40(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=100)

    lot_f1 = creer_lot_reception(conn, ids, quantite=60, poids_kg=60 * 3.5, prix_provisoire_minor=tnd(5.0),
                                  commande_ligne_id=cmd["commande_ligne_id"])
    lot_f2 = creer_lot_reception(conn, ids, quantite=40, poids_kg=40 * 3.5, prix_provisoire_minor=tnd(5.1),
                                  commande_ligne_id=cmd["commande_ligne_id"])

    assert lot_f1["lot_id"] != lot_f2["lot_id"]

    af1 = affecter(conn, ids, lot_f1["lot_id"], cmd["commande_ligne_id"], "INITIALE", 60, 60 * 3.5)
    af2 = affecter(conn, ids, lot_f2["lot_id"], cmd["commande_ligne_id"], "INITIALE", 40, 40 * 3.5)

    total_affecte = conn.execute(
        "SELECT SUM(quantite) FROM affectation_stock WHERE commande_ligne_id = ? AND statut='ACTIVE'",
        (cmd["commande_ligne_id"],),
    ).fetchone()[0]
    assert total_affecte == 100

    # Chaque affectation reste rattachée à SON lot d'origine (pas de mélange) :
    row1 = conn.execute("SELECT lot_id, quantite FROM affectation_stock WHERE id=?", (af1,)).fetchone()
    row2 = conn.execute("SELECT lot_id, quantite FROM affectation_stock WHERE id=?", (af2,)).fetchone()
    assert (row1["lot_id"], row1["quantite"]) == (lot_f1["lot_id"], 60)
    assert (row2["lot_id"], row2["quantite"]) == (lot_f2["lot_id"], 40)


# ───────────────────────── Test 2 ─────────────────────────
# Le même BL F1 apporte en plus 20 unités pour le stock général (alimentation
# stock, commande_ligne_id NULL) : bien séparées de la commande, disponibles
# ailleurs — pas affectées par erreur à la commande de 100.
def test_2_stock_general_20_separe_de_la_commande(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=100)

    creer_lot_reception(conn, ids, quantite=60, poids_kg=60 * 3.5, prix_provisoire_minor=tnd(5.0),
                         commande_ligne_id=cmd["commande_ligne_id"])
    lot_stock_general = creer_lot_reception(conn, ids, quantite=20, poids_kg=20 * 3.5, prix_provisoire_minor=tnd(5.0),
                                             commande_ligne_id=None)

    # Ce lot n'apparaît dans AUCUNE affectation de la commande :
    aff = conn.execute(
        "SELECT COUNT(*) FROM affectation_stock WHERE lot_id = ? AND commande_ligne_id = ?",
        (lot_stock_general["lot_id"], cmd["commande_ligne_id"]),
    ).fetchone()[0]
    assert aff == 0

    dispo = conn.execute(
        "SELECT quantite_non_affectee FROM v_stock_non_affecte_par_lot WHERE lot_id = ?",
        (lot_stock_general["lot_id"],),
    ).fetchone()[0]
    assert dispo == 20


# ───────────────────────── Test 3 ─────────────────────────
# Livraison 100 (commande) + 10 (supplément, prélevé sur le stock général de
# 20 créé au test 2) = 110 livré/facturé ; il reste 10 en stock général.
def test_3_livraison_100_plus_supplement_10_egale_110(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=100)

    lot_cmd = creer_lot_reception(conn, ids, quantite=100, poids_kg=100 * 3.5, prix_provisoire_minor=tnd(5.0),
                                   commande_ligne_id=cmd["commande_ligne_id"])
    lot_general = creer_lot_reception(conn, ids, quantite=20, poids_kg=20 * 3.5, prix_provisoire_minor=tnd(5.2),
                                       commande_ligne_id=None)

    af_initiale = affecter(conn, ids, lot_cmd["lot_id"], cmd["commande_ligne_id"], "INITIALE", 100, 350)
    af_supplement = affecter(conn, ids, lot_general["lot_id"], cmd["commande_ligne_id"], "SUPPLEMENT", 10, 35)

    livraison_1 = livrer(conn, ids, lot_cmd["lot_id"], cmd["commande_ligne_id"], af_initiale,
                          "INITIALE", 100, 350, cmd["commande_id"])
    livrer(conn, ids, lot_general["lot_id"], cmd["commande_ligne_id"], af_supplement,
           "SUPPLEMENT", 10, 35, cmd["commande_id"], bl_client_id=livraison_1["bl_client_id"])

    total_livre = conn.execute(
        "SELECT SUM(quantite) FROM bl_client_ligne WHERE commande_ligne_id = ?",
        (cmd["commande_ligne_id"],),
    ).fetchone()[0]
    assert total_livre == 110

    reste_general = conn.execute(
        "SELECT quantite_non_affectee FROM v_stock_non_affecte_par_lot WHERE lot_id = ?",
        (lot_general["lot_id"],),
    ).fetchone()[0]
    assert reste_general == 10  # 20 reçus - 10 pris en supplément


# ───────────────────────── Test 4 ─────────────────────────
# Transformation : 100 envoyés -> 95 reçus + 5 chutes. Jamais plus que ce qui
# a été envoyé (trigger trg_reception_transfo_plafond), et rien n'est perdu :
# reçu + chute = envoyé exactement.
def test_4_transformation_100_envoyes_95_recus_5_chutes(conn):
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=100, poids_kg=350, prix_provisoire_minor=tnd(5.0))

    envoi = envoyer_transformation(conn, ids, lot["lot_id"], 100, 350)
    reception = recevoir_transformation(conn, ids, envoi["bst_id"], envoi["bstl_id"],
                                         quantite_recue=95, poids_recu_kg=332.5,
                                         quantite_chute=5, poids_chute_kg=17.5,
                                         prix_lot_resultat_minor=tnd(5.3))

    row = conn.execute(
        "SELECT quantite_recue, quantite_chute FROM reception_transformation_ligne WHERE id=?",
        (reception["rtl_id"],),
    ).fetchone()
    assert row["quantite_recue"] + row["quantite_chute"] == 100

    assert reception["chute_id"] is not None
    chute_row = conn.execute("SELECT quantite FROM chute WHERE id=?", (reception["chute_id"],)).fetchone()
    assert chute_row["quantite"] == 5

    # Tentative de dépassement (encore 1 de plus, alors que le solde envoyé est épuisé) -> refusée :
    with pytest.raises(Exception):
        conn.execute(
            """INSERT INTO reception_transformation_ligne
               (id, reception_transformation_id, bon_sortie_transformation_ligne_id,
                quantite_recue, quantite_chute)
               VALUES (?,?,?,?,?)""",
            (nid(), reception["rt_id"], envoi["bstl_id"], 1, 0),
        )


# ───────────────────────── Test 5 ─────────────────────────
# Régularisation 5,00 -> 6,00 sur un lot PAS ENCORE sorti (100% en stock) :
# appliquée au lot (le coût réel du lot devient 6,00 dès maintenant), ET le
# CMP du pool est RECONSTRUIT avec ce coût FACTURÉ final — plus jamais avec le
# prix BL provisoire pour ce lot. C'est l'exemple obligatoire de la Phase 4.1
# §1 (100 unités, BL=5,00, facture=6,00, toutes encore en stock -> coût final
# du lot = 6,00, CMP reconstruit = 6,00).
def test_5_regularisation_lot_non_sorti_appliquee_au_lot_et_cmp_recalcule(conn):
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=100, poids_kg=350, prix_provisoire_minor=tnd(5.0))

    assert cout_reel_lot_minor(conn, lot["lot_id"]) == tnd(5.0)
    reconstruire_cmp(conn)
    assert cmp_actuel_minor(conn, ids["article"], "GALVA", 6.0) == tnd(5.0)

    resultat = regulariser_facture_fournisseur(
        conn, ids, lot["lot_id"], lot["bl_ligne_id"],
        prix_provisoire_minor=tnd(5.0), prix_definitif_minor=tnd(6.0), lot_deja_sorti=0,
    )
    assert resultat["impact_analytique"] == "APPLIQUE_AU_LOT"

    # Le coût réel du lot devient le prix facturé :
    assert cout_reel_lot_minor(conn, lot["lot_id"]) == tnd(6.0)

    # Le CMP du pool est RECONSTRUIT avec le coût final facturé (6,00), pas le
    # prix BL provisoire (5,00) — c'est le cœur de la correction §1.
    reconstruire_cmp(conn)
    assert cmp_actuel_minor(conn, ids["article"], "GALVA", 6.0) == tnd(6.0)


# ───────────────────────── Test 6 ─────────────────────────
# Régularisation sur un lot DÉJÀ VENDU (totalement sorti) : écart séparé,
# JAMAIS rétroactif — les mouvements physiques, le coût déjà appliqué à
# l'affaire ET le CMP historique déjà consommé ne sont pas réécrits ; seul un
# enregistrement d'écart, tracé, est ajouté.
def test_6_regularisation_lot_deja_sorti_ecart_separe_non_retroactif(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=10)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0),
                               commande_ligne_id=cmd["commande_ligne_id"])
    af = affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 10, 35)
    livrer(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], af, "INITIALE", 10, 35, cmd["commande_id"])

    cout_avant = cout_reel_lot_minor(conn, lot["lot_id"])
    mouvement_avant = dict(conn.execute(
        "SELECT quantite, poids_kg FROM mouvement_stock WHERE lot_id = ? AND type='SORTIE_LIVRAISON_CLIENT'",
        (lot["lot_id"],),
    ).fetchone())
    reconstruire_cmp(conn)
    cmp_avant = cmp_actuel_minor(conn, ids["article"], "GALVA", 6.0)

    resultat = regulariser_facture_fournisseur(
        conn, ids, lot["lot_id"], lot["bl_ligne_id"],
        prix_provisoire_minor=tnd(5.0), prix_definitif_minor=tnd(6.0), lot_deja_sorti=1,
    )
    assert resultat["impact_analytique"] == "ECART_SEPARE"

    # Rien n'a changé sur le passé :
    assert cout_reel_lot_minor(conn, lot["lot_id"]) == cout_avant
    mouvement_apres = dict(conn.execute(
        "SELECT quantite, poids_kg FROM mouvement_stock WHERE lot_id = ? AND type='SORTIE_LIVRAISON_CLIENT'",
        (lot["lot_id"],),
    ).fetchone())
    assert mouvement_apres == mouvement_avant

    # Le CMP n'est pas rétroactivement modifié par la régularisation :
    reconstruire_cmp(conn)
    assert cmp_actuel_minor(conn, ids["article"], "GALVA", 6.0) == cmp_avant

    # L'écart est bien tracé, séparément :
    regul = conn.execute(
        "SELECT ecart_unitaire_minor, impact_analytique, lot_deja_sorti FROM regularisation_prix_fournisseur "
        "WHERE id=?",
        (resultat["regularisation_id"],),
    ).fetchone()
    assert regul["ecart_unitaire_minor"] == tnd(1.0)
    assert regul["impact_analytique"] == "ECART_SEPARE"
    assert regul["lot_deja_sorti"] == 1

    # La régularisation elle-même est immuable (jamais réécrite) :
    with pytest.raises(Exception):
        conn.execute(
            "UPDATE regularisation_prix_fournisseur SET ecart_unitaire_minor = 0 WHERE id=?",
            (resultat["regularisation_id"],),
        )


# ─────────────────────── Test 6bis ────────────────────────
# Variante Phase 4.1 §1 obligatoire : lot PARTIELLEMENT sorti au moment de la
# facture (ex. 40 sur 100 déjà livrés). Même règle que le lot totalement sorti
# : écart séparé, non rétroactif — le fait que 60 unités restent encore
# physiquement en stock ne change rien, seul "sorti ou pas" (lot_deja_sorti)
# pilote la décision, exactement comme prévu dès la Phase 4 (migration 0009).
def test_6bis_regularisation_lot_partiellement_sorti_ecart_separe(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=40)
    lot = creer_lot_reception(conn, ids, quantite=100, poids_kg=350, prix_provisoire_minor=tnd(5.0))

    af = affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 40, 140)
    livrer(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], af, "INITIALE", 40, 140, cmd["commande_id"])

    # 60 unités du même lot restent en stock au moment de la facture :
    dispo = conn.execute(
        "SELECT quantite_non_affectee FROM v_stock_non_affecte_par_lot WHERE lot_id = ?", (lot["lot_id"],)
    ).fetchone()[0]
    assert dispo == 60

    cout_avant = cout_reel_lot_minor(conn, lot["lot_id"])
    resultat = regulariser_facture_fournisseur(
        conn, ids, lot["lot_id"], lot["bl_ligne_id"],
        prix_provisoire_minor=tnd(5.0), prix_definitif_minor=tnd(6.0), lot_deja_sorti=1,
    )
    assert resultat["impact_analytique"] == "ECART_SEPARE"
    # Non rétroactif, même partiellement sorti : le coût réel du lot ne bouge pas.
    assert cout_reel_lot_minor(conn, lot["lot_id"]) == cout_avant == tnd(5.0)


# ───────────────────────── Test 7 ─────────────────────────
# Réaffectation A -> B, tracée dans une table dédiée : motif obligatoire,
# l'affectation d'origine se clôture automatiquement, jamais silencieuse.
def test_7_reaffectation_a_vers_b_tracee(conn):
    ids = seed_referentiels(conn)
    cmd_a = creer_commande(conn, ids, quantite=10)
    cmd_b = creer_commande(conn, ids, quantite=10)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0),
                               commande_ligne_id=cmd_a["commande_ligne_id"])

    af_a = affecter(conn, ids, lot["lot_id"], cmd_a["commande_ligne_id"], "INITIALE", 10, 35)

    af_b_id = reaffecter(conn, ids, af_a, cmd_b["commande_ligne_id"], 10, 35,
                          motif="Client A a annulé, report sur affaire B")

    statut_a = conn.execute("SELECT statut FROM affectation_stock WHERE id=?", (af_a,)).fetchone()[0]
    statut_b = conn.execute("SELECT statut FROM affectation_stock WHERE id=?", (af_b_id,)).fetchone()[0]
    assert statut_a == "CLOTUREE"
    assert statut_b == "ACTIVE"

    reaff = conn.execute(
        "SELECT affectation_origine_id, affectation_destination_id, quantite_reaffectee, motif "
        "FROM reaffectation WHERE affectation_origine_id = ?",
        (af_a,),
    ).fetchone()
    assert reaff["affectation_destination_id"] == af_b_id
    assert reaff["quantite_reaffectee"] == 10
    assert reaff["motif"]

    # Une deuxième réaffectation de la même origine (déjà réaffectée) est refusée :
    cmd_c = creer_commande(conn, ids, quantite=10)
    with pytest.raises(Exception):
        reaffecter(conn, ids, af_a, cmd_c["commande_ligne_id"], 10, 35, motif="Tentative de double réaffectation")
    conn.rollback()


# ───────────────────────── Test 8 ─────────────────────────
# Stock général -> CMP : deux entrées à des prix différents donnent une
# moyenne pondérée EXACTE, jamais un FIFO (plus ancien épuisé en premier), et
# jamais une approximation flottante (Phase 4.1 §2 : entiers, égalité stricte).
def test_8_stock_general_cmp(conn):
    ids = seed_referentiels(conn)
    lot_a = creer_lot_reception(conn, ids, quantite=60, poids_kg=210, prix_provisoire_minor=tnd(5.0),
                                 date_heure="2026-01-01T08:00:00.000")
    lot_b = creer_lot_reception(conn, ids, quantite=40, poids_kg=140, prix_provisoire_minor=tnd(5.5),
                                 date_heure="2026-01-02T08:00:00.000")

    pools = reconstruire_cmp(conn)
    key = (ids["article"], "GALVA", 6.0)
    assert pools[key]["quantite_totale"] == 100
    assert pools[key]["valeur_totale_minor"] == 60 * tnd(5.0) + 40 * tnd(5.5)
    cmp = cmp_actuel_minor(conn, ids["article"], "GALVA", 6.0)
    assert cmp == (60 * tnd(5.0) + 40 * tnd(5.5)) // 100  # 5200 millimes, jamais 5000 (réflexe FIFO)
    assert cmp == tnd(5.20)

    # Une sortie générale (ni affectation INITIALE, ni SUPPLEMENT) consomme au CMP courant :
    cmd = creer_commande(conn, ids, quantite=20)
    af = affecter(conn, ids, lot_a["lot_id"], cmd["commande_ligne_id"], "SUPPLEMENT", 20, 70)
    sortie = livrer(conn, ids, lot_a["lot_id"], cmd["commande_ligne_id"], af, "SUPPLEMENT", 20, 70,
                     cmd["commande_id"], date_heure="2026-01-03T08:00:00.000")

    pools = reconstruire_cmp(conn)
    assert pools[key]["quantite_totale"] == 80
    assert pools[key]["valeur_totale_minor"] == 80 * cmp
    cout = cout_sortie_minor(conn, sortie["mouvement_id"], lot_a["lot_id"])
    assert cout == cmp
    # Le montant TOTAL exact facturé pour cette sortie (déjà écrit par livrer()
    # dans bl_client_ligne.cout_cmp_total_minor) est exactement 20 x le CMP :
    total_ligne = conn.execute(
        "SELECT cout_cmp_total_minor FROM bl_client_ligne WHERE id = ?", (sortie["bl_client_ligne_id"],)
    ).fetchone()[0]
    assert total_ligne == 20 * cmp
    assert cout_sortie_total_minor(conn, sortie["mouvement_id"], lot_a["lot_id"]) == total_ligne


# ───────────────────────── Test 9 ─────────────────────────
# Quantité normale affectée (INITIALE) -> coût réel du lot, jamais le CMP du
# pool — même si le pool mélange plusieurs prix très différents.
def test_9_quantite_initiale_cout_reel_du_lot(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=10)

    lot_cher = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(9.0),
                                    commande_ligne_id=cmd["commande_ligne_id"],
                                    date_heure="2026-01-01T08:00:00.000")
    # Un autre lot, moins cher, alimente le stock général du même pool -> fait
    # bouger le CMP, mais ne doit JAMAIS influencer le coût de l'affectation INITIALE :
    creer_lot_reception(conn, ids, quantite=90, poids_kg=315, prix_provisoire_minor=tnd(4.0),
                         date_heure="2026-01-02T08:00:00.000")

    af = affecter(conn, ids, lot_cher["lot_id"], cmd["commande_ligne_id"], "INITIALE", 10, 35)
    sortie = livrer(conn, ids, lot_cher["lot_id"], cmd["commande_ligne_id"], af, "INITIALE", 10, 35,
                     cmd["commande_id"], date_heure="2026-01-03T08:00:00.000")

    reconstruire_cmp(conn)
    cmp_du_pool = cmp_actuel_minor(conn, ids["article"], "GALVA", 6.0)
    assert cmp_du_pool != tnd(9.0)  # le pool est dominé par le lot à 4.0

    cout = cout_sortie_minor(conn, sortie["mouvement_id"], lot_cher["lot_id"])
    assert cout == tnd(9.0)  # coût réel du lot, pas le CMP mélangé
    assert cout == cout_reel_lot_minor(conn, lot_cher["lot_id"])


# ───────────────────────── Test 10 ─────────────────────────
# Quantité supplémentaire -> CMP AU MOMENT de la sortie : figé à cet instant,
# pas recalculé avec le CMP "actuel" si le pool évolue ensuite.
def test_10_supplement_cmp_au_moment_de_la_sortie(conn):
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=20, poids_kg=70, prix_provisoire_minor=tnd(5.0),
                               date_heure="2026-01-01T08:00:00.000")

    cmd = creer_commande(conn, ids, quantite=10)
    af = affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "SUPPLEMENT", 10, 35)
    sortie = livrer(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], af, "SUPPLEMENT", 10, 35,
                     cmd["commande_id"], date_heure="2026-01-02T08:00:00.000")

    cmp_au_moment = cout_sortie_minor(conn, sortie["mouvement_id"], lot["lot_id"])
    assert cmp_au_moment == tnd(5.0)

    # Le pool évolue ensuite avec un prix très différent :
    creer_lot_reception(conn, ids, quantite=100, poids_kg=350, prix_provisoire_minor=tnd(50.0),
                         date_heure="2026-01-03T08:00:00.000")
    reconstruire_cmp(conn)
    cmp_actuel_du_pool = cmp_actuel_minor(conn, ids["article"], "GALVA", 6.0)
    assert cmp_actuel_du_pool != cmp_au_moment  # le pool a bien bougé...

    # ...mais le coût déjà figé pour CETTE sortie ne bouge pas :
    cmp_relu = cout_sortie_minor(conn, sortie["mouvement_id"], lot["lot_id"])
    assert cmp_relu == tnd(5.0)


# ───────────────────────── Test 11 ─────────────────────────
# Chute -> CMP au moment de la sortie (= au moment où la matière a quitté
# STOCK_GMC pour la transformation), pas au moment où la chute est constatée
# au retour, et pas influencé par ce qui se passe sur le pool entre-temps.
def test_11_chute_cmp_au_moment_de_la_sortie(conn):
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=100, poids_kg=350, prix_provisoire_minor=tnd(5.0),
                               date_heure="2026-01-01T08:00:00.000")

    envoi = envoyer_transformation(conn, ids, lot["lot_id"], 100, 350, date_heure="2026-01-02T08:00:00.000")
    reconstruire_cmp(conn)
    cmp_a_lenvoi = cmp_actuel_minor(conn, ids["article"], "GALVA", 6.0)
    assert cmp_a_lenvoi == tnd(5.0)

    # Entre l'envoi et le retour de transformation, le pool général évolue fortement :
    creer_lot_reception(conn, ids, quantite=50, poids_kg=175, prix_provisoire_minor=tnd(40.0),
                         date_heure="2026-01-03T08:00:00.000")

    reception = recevoir_transformation(conn, ids, envoi["bst_id"], envoi["bstl_id"],
                                         quantite_recue=95, poids_recu_kg=332.5,
                                         quantite_chute=5, poids_chute_kg=17.5,
                                         prix_lot_resultat_minor=tnd(5.3),
                                         date_heure="2026-01-10T08:00:00.000")

    reconstruire_cmp(conn)
    cmp_maintenant = cmp_actuel_minor(conn, ids["article"], "GALVA", 6.0)
    assert cmp_maintenant != cmp_a_lenvoi  # le pool a bien changé depuis

    cout_unitaire = cout_chute_unitaire_minor(conn, reception["chute_id"])
    assert cout_unitaire == tnd(5.0)  # figé au CMP du moment de l'envoi en transformation, pas du retour

    # Le montant TOTAL de la chute = 5 unités x 5,00 = 25,00 TND, exact :
    cout_total = cout_chute_total_minor(conn, reception["chute_id"])
    assert cout_total == 5 * tnd(5.0) == tnd(25.0)
