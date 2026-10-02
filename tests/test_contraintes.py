"""
Tests de contraintes d'intégrité (complément aux 11 tests obligatoires,
demandé par la description de la tâche « écrire et exécuter les 11 tests » :
stock négatif, double facturation, réaffectation sans motif, etc.)
Chaque cas doit être REFUSÉ par la base elle-même (trigger / UNIQUE / NOT NULL /
CHECK), jamais seulement par du code applicatif qui n'existe pas encore.

PHASE 4.1 — montants adaptés à la représentation entière (unité monétaire
minimale) : `prix_provisoire=5.0` -> `prix_provisoire_minor=tnd(5.0)` (=5000
millimes), etc. Aucun de ces tests ne change de comportement testé, seule
l'écriture des montants change (cf. CHANGELOG.md).
"""
import sqlite3

import pytest

from tests.helpers import affecter, creer_commande, creer_lot_reception, eur_usd, livrer, nid, seed_referentiels, tnd


def test_stock_negatif_refuse(conn):
    """Une sortie qui dépasse le solde réel du lot à cet emplacement est bloquée."""
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO mouvement_stock
               (id, lot_id, type, quantite, poids_kg, emplacement_source,
                document_source_type, document_source_id, utilisateur_id)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (nid(), lot["lot_id"], "SORTIE_LIVRAISON_CLIENT", 11, 38.5, "STOCK_GMC",
             "test", "test", ids["utilisateur"]),
        )


def test_affectation_depasse_le_lot_refusee(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=10)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0),
                               commande_ligne_id=cmd["commande_ligne_id"])
    affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 7, 24.5)
    with pytest.raises(sqlite3.IntegrityError):
        affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "SUPPLEMENT", 4, 14.0)  # 7+4 > 10


def test_livraison_depasse_affectation_refusee(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=10)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0),
                               commande_ligne_id=cmd["commande_ligne_id"])
    af = affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 5, 17.5)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO bl_client_ligne
               (id, bl_client_id, lot_id, commande_ligne_id, type, quantite, poids_facturable_kg)
               VALUES (?,?,?,?,?,?,?)""",
            (nid(), _bl_client_bidon(conn, cmd), lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 6, 21.0),
        )
    _ = af  # l'affectation existe bien mais ne couvre que 5, pas 6


def test_double_facturation_refusee(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=10)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0),
                               commande_ligne_id=cmd["commande_ligne_id"])
    af = affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 10, 35)
    livraison = livrer(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], af, "INITIALE", 10, 35, cmd["commande_id"])

    facture_id = nid()
    conn.execute(
        "INSERT INTO facture_client (id, numero, commande_client_id, date, montant_minor) VALUES (?,?,?,?,?)",
        (facture_id, f"FAC-2026-{nid()[:8]}", cmd["commande_id"], "2026-01-15", eur_usd(550.0)),
    )
    conn.execute(
        "INSERT INTO facture_client_ligne (id, facture_client_id, bl_client_ligne_id, prix_applique_minor) "
        "VALUES (?,?,?,?)",
        (nid(), facture_id, livraison["bl_client_ligne_id"], eur_usd(5.5)),
    )
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO facture_client_ligne (id, facture_client_id, bl_client_ligne_id, prix_applique_minor) "
            "VALUES (?,?,?,?)",
            (nid(), facture_id, livraison["bl_client_ligne_id"], eur_usd(5.5)),
        )


def test_reaffectation_sans_motif_refusee(conn):
    ids = seed_referentiels(conn)
    cmd_a = creer_commande(conn, ids, quantite=10)
    cmd_b = creer_commande(conn, ids, quantite=10)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0),
                               commande_ligne_id=cmd_a["commande_ligne_id"])
    af_a = affecter(conn, ids, lot["lot_id"], cmd_a["commande_ligne_id"], "INITIALE", 10, 35)
    # Workflow correct (migration 0015) : l'origine se clôture avant que la
    # destination ne soit créée, pour ne jamais dépasser transitoirement le
    # plafond du lot.
    conn.execute("UPDATE affectation_stock SET statut='CLOTUREE' WHERE id=?", (af_a,))
    af_b = nid()
    conn.execute(
        """INSERT INTO affectation_stock
           (id, lot_id, commande_ligne_id, type, quantite, poids_kg, utilisateur_id)
           VALUES (?,?,?,?,?,?,?)""",
        (af_b, lot["lot_id"], cmd_b["commande_ligne_id"], "INITIALE", 10, 35, ids["utilisateur"]),
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """INSERT INTO reaffectation
               (id, affectation_origine_id, affectation_destination_id, quantite_reaffectee, motif, utilisateur_id)
               VALUES (?,?,?,?,?,?)""",
            (nid(), af_a, af_b, 10, None, ids["utilisateur"]),
        )
    conn.rollback()


def test_document_historique_non_supprimable(conn):
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM bl_fournisseur WHERE id = ?", (lot["bl_id"],))


def test_mouvement_stock_immuable_update_refuse(conn):
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE mouvement_stock SET quantite = 5 WHERE id = ?", (lot["mouvement_id"],))


def test_mouvement_stock_immuable_delete_refuse(conn):
    ids = seed_referentiels(conn)
    lot = creer_lot_reception(conn, ids, quantite=10, poids_kg=35, prix_provisoire_minor=tnd(5.0))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("DELETE FROM mouvement_stock WHERE id = ?", (lot["mouvement_id"],))


def test_commande_ligne_quantite_originale_immuable(conn):
    ids = seed_referentiels(conn)
    cmd = creer_commande(conn, ids, quantite=10)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "UPDATE commande_ligne SET quantite_originale = 99 WHERE id = ?", (cmd["commande_ligne_id"],)
        )


def _bl_client_bidon(conn, cmd):
    bl_id = nid()
    conn.execute(
        "INSERT INTO bl_client (id, numero, commande_client_id, date) VALUES (?,?,?,?)",
        (bl_id, f"BLC-2026-{nid()[:8]}", cmd["commande_id"], "2026-01-10"),
    )
    return bl_id
