"""
Fixtures minimalistes pour les tests d'intégrité de la base GMC (Phase 4 /
4.1).

Ce ne sont PAS des modules métier : juste des inserts SQL directs qui imitent,
au minimum nécessaire, ce qu'un futur service applicatif (Phase 5) écrira
dans les tables déjà en place, afin de pouvoir tester le schéma, les triggers
et le moteur de valorisation dès maintenant.

PHASE 4.1 — tous les montants passés ici sont des ENTIERS en unité monétaire
minimale (ex. 5000 = 5,000 TND ; 520 = 5,20 EUR/USD), jamais des flottants —
cf. docs/PRIX_REVIENT.md. Le paramètre `devise` par défaut 'TND' correspond
au défaut technique choisi en migration 0016.
"""
import uuid


def nid() -> str:
    return str(uuid.uuid4())


def tnd(montant_dt) -> int:
    """Convertit un montant décimal en dinars tunisiens (ex. 5.25) en
    millimes entiers (5250) — utilitaire de LISIBILITÉ pour les tests
    seulement, jamais utilisé par le moteur lui-même."""
    return round(montant_dt * 1000)


def eur_usd(montant) -> int:
    """Convertit un montant décimal en EUR/USD (ex. 5.20) en centimes
    entiers (520) — utilitaire de LISIBILITÉ pour les tests seulement."""
    return round(montant * 100)


def definir_unite_valorisation(conn, article_id, unite, utilisateur_id,
                               date_effet="2026-01-01T00:00:00.000"):
    """Définition initiale de l'unité de valorisation d'un article (INSERT direct)."""
    conn.execute(
        """INSERT INTO article_unite_valorisation
           (id, article_id, nature, unite, date_effet, cree_par) VALUES (?,?,?,?,?,?)""",
        (nid(), article_id, "DEFINITION_INITIALE", unite, date_effet, utilisateur_id),
    )


def seed_referentiels(conn):
    ids = {}

    ids["utilisateur"] = nid()
    conn.execute(
        "INSERT INTO utilisateur (id, nom, role, mot_de_passe_hash) VALUES (?,?,?,?)",
        (ids["utilisateur"], "Test User", "ADMINISTRATEUR", "hash"),
    )

    ids["famille"] = nid()
    conn.execute("INSERT INTO famille_article (id, libelle) VALUES (?,?)", (ids["famille"], "Tubes"))

    ids["article"] = nid()
    conn.execute(
        "INSERT INTO article (id, designation, famille_id, masse_lineique_kg_m) VALUES (?,?,?,?)",
        (ids["article"], "Tube 40x40", ids["famille"], 3.5),
    )
    # Phase 5.5 (migration 0019) : l'unité de valorisation d'un article est
    # obligatoire avant tout lot (aucune unité par défaut). L'article de test
    # des Phases 4/4.1 a toujours été valorisé par pièce : UNITE (DT/unité).
    # (Les tests de migration 0017/0018 alimentent un schéma antérieur à 0019.)
    if conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='article_unite_valorisation'"
    ).fetchone():
        definir_unite_valorisation(conn, ids["article"], "UNITE", ids["utilisateur"])

    ids["client"] = nid()
    conn.execute("INSERT INTO client (id, nom) VALUES (?,?)", (ids["client"], "Client Test"))

    ids["fournisseur"] = nid()
    conn.execute(
        "INSERT INTO fournisseur (id, nom, pays) VALUES (?,?,?)",
        (ids["fournisseur"], "Fournisseur Test", "Turquie"),
    )

    ids["transformateur"] = nid()
    conn.execute(
        "INSERT INTO transformateur (id, nom, type) VALUES (?,?,?)",
        (ids["transformateur"], "Galva Test", "GALVA"),
    )

    ids["taux_change"] = nid()
    conn.execute(
        "INSERT INTO taux_change (id, date, devise, taux, contexte) VALUES (?,?,?,?,?)",
        (ids["taux_change"], "2026-01-01", "EUR", 3.4, "DEVIS"),
    )

    conn.commit()
    return ids


def creer_commande(conn, ids, quantite=100, finition="GALVA", longueur_m=6.0, prix_negocie_minor=5500,
                    devise="TND"):
    devis_id = nid()
    conn.execute(
        """INSERT INTO devis (id, numero, client_id, date, date_validite, taux_change_id, statut)
           VALUES (?,?,?,?,?,?,?)""",
        (devis_id, f"DEV-2026-{nid()[:8]}", ids["client"], "2026-01-01", "2026-02-01",
         ids["taux_change"], "CONFIRME"),
    )
    commande_id = nid()
    conn.execute(
        """INSERT INTO commande_client
           (id, numero, devis_id, client_id, date_confirmation, statut)
           VALUES (?,?,?,?,?,?)""",
        (commande_id, f"CMD-2026-{nid()[:8]}", devis_id, ids["client"], "2026-01-02", "CONFIRMEE"),
    )
    ligne_id = nid()
    conn.execute(
        """INSERT INTO commande_ligne
           (id, commande_client_id, article_id, finition, longueur_m, quantite_originale,
            prix_negocie_minor, devise)
           VALUES (?,?,?,?,?,?,?,?)""",
        (ligne_id, commande_id, ids["article"], finition, longueur_m, quantite, prix_negocie_minor, devise),
    )
    conn.commit()
    return {"commande_id": commande_id, "commande_ligne_id": ligne_id}


def creer_lot_reception(conn, ids, quantite, poids_kg, prix_provisoire_minor, finition="GALVA", longueur_m=6.0,
                         commande_ligne_id=None, date_heure="2026-01-05T08:00:00.000", devise="TND"):
    """Un BL fournisseur (1 ligne) valide-> crée un lot + le mouvement d'entrée en STOCK_GMC.
    `prix_provisoire_minor` est un ENTIER en unité monétaire minimale de `devise`
    (millimes pour TND, centimes pour EUR/USD — cf. tests/helpers.py:tnd()/eur_usd())."""
    bl_id = nid()
    conn.execute(
        """INSERT INTO bl_fournisseur (id, numero, numero_origine_fournisseur, fournisseur_id, date, statut)
           VALUES (?,?,?,?,?,?)""",
        (bl_id, f"BLF-2026-{nid()[:8]}", f"ORIG-{nid()[:6]}", ids["fournisseur"], "2026-01-05", "VALIDE"),
    )
    ligne_id = nid()
    conn.execute(
        """INSERT INTO bl_fournisseur_ligne
           (id, bl_fournisseur_id, commande_ligne_id, article_id, finition, longueur_m,
            quantite, poids_kg, prix_unitaire_provisoire_minor, devise)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (ligne_id, bl_id, commande_ligne_id, ids["article"], finition, longueur_m,
         quantite, poids_kg, prix_provisoire_minor, devise),
    )
    lot_id = nid()
    conn.execute(
        """INSERT INTO lot
           (id, article_id, bl_fournisseur_ligne_id, finition, longueur_m,
            quantite_initiale, poids_initial_kg, prix_unitaire_provisoire_minor, devise)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (lot_id, ids["article"], ligne_id, finition, longueur_m, quantite, poids_kg, prix_provisoire_minor, devise),
    )
    mv_id = nid()
    conn.execute(
        """INSERT INTO mouvement_stock
           (id, lot_id, type, quantite, poids_kg, emplacement_destination,
            document_source_type, document_source_id, date_heure, utilisateur_id)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (mv_id, lot_id, "ENTREE_RECEPTION_FOURNISSEUR", quantite, poids_kg, "STOCK_GMC",
         "bl_fournisseur_ligne", ligne_id, date_heure, ids["utilisateur"]),
    )
    conn.commit()
    return {"bl_id": bl_id, "bl_ligne_id": ligne_id, "lot_id": lot_id, "mouvement_id": mv_id}


def affecter(conn, ids, lot_id, commande_ligne_id, type_, quantite, poids_kg, motif=None,
             date_heure="2026-01-06T08:00:00.000"):
    aff_id = nid()
    conn.execute(
        """INSERT INTO affectation_stock
           (id, lot_id, commande_ligne_id, type, quantite, poids_kg, utilisateur_id, date_heure, motif)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (aff_id, lot_id, commande_ligne_id, type_, quantite, poids_kg, ids["utilisateur"], date_heure, motif),
    )
    conn.commit()
    return aff_id


def livrer(conn, ids, lot_id, commande_ligne_id, affectation_id, type_, quantite, poids_kg,
           commande_client_id, date_heure="2026-01-10T08:00:00.000", bl_client_id=None,
           calculer_cout_supplement=True):
    """BL client (1 ligne) + mouvement de sortie STOCK_GMC -> LIVRE, referme l'affectation."""
    if bl_client_id is None:
        bl_client_id = nid()
        conn.execute(
            "INSERT INTO bl_client (id, numero, commande_client_id, date) VALUES (?,?,?,?)",
            (bl_client_id, f"BLC-2026-{nid()[:8]}", commande_client_id, "2026-01-10"),
        )
    ligne_id = nid()
    conn.execute(
        """INSERT INTO bl_client_ligne
           (id, bl_client_id, lot_id, commande_ligne_id, type, quantite, poids_facturable_kg)
           VALUES (?,?,?,?,?,?,?)""",
        (ligne_id, bl_client_id, lot_id, commande_ligne_id, type_, quantite, poids_kg),
    )
    mv_id = nid()
    conn.execute(
        """INSERT INTO mouvement_stock
           (id, lot_id, type, quantite, poids_kg, emplacement_source,
            document_source_type, document_source_id, date_heure, utilisateur_id)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (mv_id, lot_id, "SORTIE_LIVRAISON_CLIENT", quantite, poids_kg, "STOCK_GMC",
         "bl_client_ligne", ligne_id, date_heure, ids["utilisateur"]),
    )
    conn.execute("UPDATE affectation_stock SET mouvement_physique_id = ? WHERE id = ?", (mv_id, affectation_id))

    if calculer_cout_supplement and type_ == "SUPPLEMENT":
        from db.valorisation import cout_sortie_total_minor, reconstruire_cmp
        reconstruire_cmp(conn)
        cout_total_minor = cout_sortie_total_minor(conn, mv_id, lot_id)
        conn.execute(
            "UPDATE bl_client_ligne SET cout_cmp_total_minor = ? WHERE id = ?", (cout_total_minor, ligne_id)
        )

    conn.commit()
    return {"bl_client_id": bl_client_id, "bl_client_ligne_id": ligne_id, "mouvement_id": mv_id}


def reaffecter(conn, ids, affectation_origine_id, commande_ligne_destination_id, quantite, poids_kg,
                motif, type_="INITIALE"):
    """
    Workflow correct d'une réaffectation (cf. migration 0015) : on clôture
    l'origine AVANT de créer la destination, pour que le plafond du lot (qui
    ne compte que les affectations ACTIVES) ne soit jamais transitoirement
    dépassé par la coexistence momentanée des deux affectations.
    """
    origine = conn.execute(
        "SELECT lot_id FROM affectation_stock WHERE id=?", (affectation_origine_id,)
    ).fetchone()
    conn.execute("UPDATE affectation_stock SET statut='CLOTUREE' WHERE id=?", (affectation_origine_id,))
    destination_id = nid()
    conn.execute(
        """INSERT INTO affectation_stock
           (id, lot_id, commande_ligne_id, type, quantite, poids_kg, utilisateur_id)
           VALUES (?,?,?,?,?,?,?)""",
        (destination_id, origine["lot_id"], commande_ligne_destination_id, type_, quantite, poids_kg,
         ids["utilisateur"]),
    )
    conn.execute(
        """INSERT INTO reaffectation
           (id, affectation_origine_id, affectation_destination_id, quantite_reaffectee, motif, utilisateur_id)
           VALUES (?,?,?,?,?,?)""",
        (nid(), affectation_origine_id, destination_id, quantite, motif, ids["utilisateur"]),
    )
    conn.commit()
    return destination_id


def envoyer_transformation(conn, ids, lot_id, quantite, poids_kg, date_heure="2026-02-01T08:00:00.000"):
    bct_id = nid()
    conn.execute(
        "INSERT INTO bon_commande_transformation (id, numero, transformateur_id, date) VALUES (?,?,?,?)",
        (bct_id, f"BCT-2026-{nid()[:8]}", ids["transformateur"], "2026-02-01"),
    )
    bst_id = nid()
    conn.execute(
        """INSERT INTO bon_sortie_transformation
           (id, numero, transformateur_id, bon_commande_transformation_id, date)
           VALUES (?,?,?,?,?)""",
        (bst_id, f"BST-2026-{nid()[:8]}", ids["transformateur"], bct_id, "2026-02-01"),
    )
    bstl_id = nid()
    conn.execute(
        "INSERT INTO bon_sortie_transformation_ligne (id, bon_sortie_transformation_id, lot_id, quantite) "
        "VALUES (?,?,?,?)",
        (bstl_id, bst_id, lot_id, quantite),
    )
    mv_id = nid()
    conn.execute(
        """INSERT INTO mouvement_stock
           (id, lot_id, type, quantite, poids_kg, emplacement_source, emplacement_destination,
            document_source_type, document_source_id, date_heure, utilisateur_id)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (mv_id, lot_id, "SORTIE_TRANSFORMATION", quantite, poids_kg, "STOCK_GMC",
         f"CHEZ_TRANSFORMATEUR:{ids['transformateur']}", "bon_sortie_transformation_ligne", bstl_id,
         date_heure, ids["utilisateur"]),
    )
    conn.commit()
    return {"bct_id": bct_id, "bst_id": bst_id, "bstl_id": bstl_id, "mouvement_id": mv_id}


def recevoir_transformation(conn, ids, bst_id, bstl_id, quantite_recue, poids_recu_kg,
                             quantite_chute, poids_chute_kg, prix_lot_resultat_minor=None,
                             date_heure="2026-02-05T08:00:00.000", devise="TND", commande_client_id=None):
    orig_lot_id = conn.execute(
        "SELECT lot_id FROM bon_sortie_transformation_ligne WHERE id = ?", (bstl_id,)
    ).fetchone()[0]
    orig = conn.execute(
        "SELECT article_id, finition, longueur_m FROM lot WHERE id = ?", (orig_lot_id,)
    ).fetchone()

    rt_id = nid()
    conn.execute(
        "INSERT INTO reception_transformation (id, numero, bon_sortie_transformation_id, date) VALUES (?,?,?,?)",
        (rt_id, f"RTR-2026-{nid()[:8]}", bst_id, "2026-02-05"),
    )

    lot_resultat_id = None
    if quantite_recue > 0:
        lot_resultat_id = nid()
        conn.execute(
            """INSERT INTO lot
               (id, article_id, lot_parent_id, finition, longueur_m,
                quantite_initiale, poids_initial_kg, prix_unitaire_provisoire_minor, devise)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (lot_resultat_id, orig["article_id"], orig_lot_id, orig["finition"], orig["longueur_m"],
             quantite_recue, poids_recu_kg, prix_lot_resultat_minor, devise),
        )
        mv_retour_id = nid()
        conn.execute(
            """INSERT INTO mouvement_stock
               (id, lot_id, type, quantite, poids_kg, emplacement_destination,
                document_source_type, document_source_id, date_heure, utilisateur_id)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (mv_retour_id, lot_resultat_id, "ENTREE_RETOUR_TRANSFORMATION", quantite_recue, poids_recu_kg,
             "STOCK_GMC", "reception_transformation_ligne", rt_id, date_heure, ids["utilisateur"]),
        )

    rtl_id = nid()
    conn.execute(
        """INSERT INTO reception_transformation_ligne
           (id, reception_transformation_id, bon_sortie_transformation_ligne_id, lot_resultat_id,
            quantite_recue, poids_recu_kg, quantite_chute, poids_chute_kg)
           VALUES (?,?,?,?,?,?,?,?)""",
        (rtl_id, rt_id, bstl_id, lot_resultat_id, quantite_recue, poids_recu_kg, quantite_chute, poids_chute_kg),
    )

    chute_id = None
    if quantite_chute > 0:
        mv_chute_id = nid()
        conn.execute(
            """INSERT INTO mouvement_stock
               (id, lot_id, type, quantite, poids_kg, emplacement_source, emplacement_destination,
                document_source_type, document_source_id, date_heure, utilisateur_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (mv_chute_id, orig_lot_id, "SORTIE_CHUTE", quantite_chute, poids_chute_kg,
             f"CHEZ_TRANSFORMATEUR:{ids['transformateur']}", "CHUTES",
             "reception_transformation_ligne", rtl_id, date_heure, ids["utilisateur"]),
        )
        chute_id = nid()
        conn.execute(
            """INSERT INTO chute
               (id, lot_id, commande_client_id, transformateur_id, reception_transformation_ligne_id,
                mouvement_stock_id, quantite, poids_kg, devise, date)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (chute_id, orig_lot_id, commande_client_id, ids["transformateur"], rtl_id, mv_chute_id,
             quantite_chute, poids_chute_kg, devise, date_heure),
        )

    conn.commit()
    return {"rt_id": rt_id, "rtl_id": rtl_id, "lot_resultat_id": lot_resultat_id, "chute_id": chute_id}


def regulariser_facture_fournisseur(conn, ids, lot_id, bl_ligne_id, prix_provisoire_minor, prix_definitif_minor,
                                     lot_deja_sorti, devise="TND", date_regularisation="2026-01-20",
                                     unite_prix_definitif=None):  # noqa: E127
    """
    Imite ce qu'un futur service applicatif (Phase 5) fera à la réception
    d'une facture fournisseur : créer la facture + sa ligne (prix facturé
    définitif), puis la régularisation qui trace l'écart BL -> facture.

    Règle définitive Phase 4.1 §1 : `lot_deja_sorti` (0/1) pilote
    `impact_analytique`, EXACTEMENT comme prévu dès la Phase 4 (migration
    0009) — ce n'est pas une règle nouvelle, seule l'arithmétique (entiers +
    devise) change ici.
      - lot_deja_sorti=0 (encore totalement en stock) -> 'APPLIQUE_AU_LOT' :
        le coût réel du lot (lot.prix_unitaire_definitif_minor) est mis à
        jour avec le prix facturé -> reconstruire_cmp() recalculera le CMP du
        pool avec ce coût final, plus jamais avec le prix BL provisoire pour
        ce lot.
      - lot_deja_sorti=1 (partiellement ou totalement sorti) -> 'ECART_SEPARE' :
        lot.prix_unitaire_definitif_minor n'est PAS touché (l'historique
        physique et le CMP déjà consommé restent inchangés) ; seul l'écart
        est tracé, séparément, pour audit.
    """
    # Migration 0020 : chaque prix garde son unité d'origine. Le prix provisoire
    # est celui du lot (dans son unité) ; sauf indication contraire, la facture
    # de ces tests est libellée dans la même unité que le BL. L'écart est
    # calculé par conversion exacte (db/valorisation.py:ecart_unitaire_exact).
    from db.valorisation import ecart_unitaire_exact

    unite_prix_provisoire = conn.execute(
        "SELECT unite_prix FROM lot WHERE id = ?", (lot_id,)
    ).fetchone()[0]
    if unite_prix_definitif is None:
        unite_prix_definitif = unite_prix_provisoire
    ecart_unitaire_minor, unite_ecart = ecart_unitaire_exact(
        prix_provisoire_minor, unite_prix_provisoire, prix_definitif_minor, unite_prix_definitif
    )
    impact_analytique = "ECART_SEPARE" if lot_deja_sorti else "APPLIQUE_AU_LOT"

    facture_id = nid()
    conn.execute(
        """INSERT INTO facture_fournisseur
           (id, numero, numero_origine_fournisseur, fournisseur_id, date, montant_total_minor, devise)
           VALUES (?,?,?,?,?,?,?)""",
        (facture_id, f"FFO-2026-{nid()[:8]}", f"ORIG-FAC-{nid()[:6]}", ids["fournisseur"],
         date_regularisation, prix_definitif_minor, devise),
    )
    facture_ligne_id = nid()
    conn.execute(
        """INSERT INTO facture_fournisseur_ligne
           (id, facture_fournisseur_id, bl_fournisseur_ligne_id, prix_unitaire_definitif_minor, devise)
           VALUES (?,?,?,?,?)""",
        (facture_ligne_id, facture_id, bl_ligne_id, prix_definitif_minor, devise),
    )
    regul_id = nid()
    conn.execute(
        """INSERT INTO regularisation_prix_fournisseur
           (id, facture_fournisseur_ligne_id, lot_id, prix_provisoire_minor, prix_definitif_minor,
            ecart_unitaire_minor, devise, date_regularisation, lot_deja_sorti, impact_analytique,
            unite_prix_provisoire, unite_prix_definitif, unite_ecart)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (regul_id, facture_ligne_id, lot_id, prix_provisoire_minor, prix_definitif_minor,
         ecart_unitaire_minor, devise, date_regularisation, int(lot_deja_sorti), impact_analytique,
         unite_prix_provisoire, unite_prix_definitif, unite_ecart),
    )
    if impact_analytique == "APPLIQUE_AU_LOT":
        conn.execute(
            "UPDATE lot SET prix_unitaire_definitif_minor = ?, unite_prix_definitif = ? "
            "WHERE id = ?",
            (prix_definitif_minor, unite_prix_definitif, lot_id),
        )
    conn.commit()
    return {
        "facture_id": facture_id,
        "facture_ligne_id": facture_ligne_id,
        "regularisation_id": regul_id,
        "impact_analytique": impact_analytique,
    }
