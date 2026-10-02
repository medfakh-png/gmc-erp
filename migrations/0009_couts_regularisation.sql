-- 0009_couts_regularisation.sql

-- Écart BL provisoire -> facture définitive (§9 Phase 2, décision Phase 2 n°1,
-- confirmée en Phase 4 §1) : jamais rétroactif, toujours une ligne séparée.
CREATE TABLE regularisation_prix_fournisseur (
    id                          TEXT PRIMARY KEY,
    facture_fournisseur_ligne_id TEXT NOT NULL UNIQUE REFERENCES facture_fournisseur_ligne(id),
    lot_id                      TEXT NOT NULL REFERENCES lot(id),
    prix_provisoire             REAL NOT NULL CHECK (prix_provisoire >= 0),
    prix_definitif               REAL NOT NULL CHECK (prix_definitif >= 0),
    ecart_unitaire               REAL NOT NULL,  -- = prix_definitif - prix_provisoire (signé)
    date_regularisation          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    lot_deja_sorti                INTEGER NOT NULL CHECK (lot_deja_sorti IN (0,1)),
    impact_analytique             TEXT NOT NULL CHECK (impact_analytique IN ('APPLIQUE_AU_LOT','ECART_SEPARE'))
);
CREATE INDEX idx_regul_lot ON regularisation_prix_fournisseur(lot_id);

-- Clé de répartition mensuelle d'une facture de transformateur entre articles (§16).
CREATE TABLE repartition_cout_transformation (
    id                          TEXT PRIMARY KEY,
    transformateur_id           TEXT NOT NULL REFERENCES transformateur(id),
    periode                     TEXT NOT NULL,  -- format 'AAAA-MM'
    facture_fournisseur_id      TEXT REFERENCES facture_fournisseur(id),  -- si la transfo est facturée comme un fournisseur
    montant_facture_reelle      REAL NOT NULL CHECK (montant_facture_reelle >= 0),
    UNIQUE (transformateur_id, periode)
);

CREATE TABLE repartition_cout_transformation_ligne (
    id                                  TEXT PRIMARY KEY,
    repartition_cout_transformation_id  TEXT NOT NULL REFERENCES repartition_cout_transformation(id),
    reception_transformation_ligne_id   TEXT NOT NULL REFERENCES reception_transformation_ligne(id),
    montant_reparti                     REAL NOT NULL CHECK (montant_reparti >= 0)
);
CREATE INDEX idx_rctl_repartition ON repartition_cout_transformation_ligne(repartition_cout_transformation_id);

-- Cache du Coût Moyen Pondéré du stock général NON AFFECTÉ, par pool
-- (article, finition, longueur) — nouvelle règle de valorisation Phase 4 (remplace
-- le FIFO du Phase 2/3). Reconstructible intégralement depuis mouvement_stock +
-- affectation_stock par db/valorisation.py:reconstruire_cmp() — ne fait jamais foi
-- seul (décision technique Phase 2 n°4, confirmée Phase 4 §2).
CREATE TABLE cmp_stock_general (
    article_id          TEXT NOT NULL REFERENCES article(id),
    finition             TEXT NOT NULL,
    longueur_m           REAL NOT NULL,
    quantite_totale      INTEGER NOT NULL DEFAULT 0,
    valeur_totale        REAL NOT NULL DEFAULT 0,
    cmp_unitaire          REAL NOT NULL DEFAULT 0,
    derniere_maj          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    PRIMARY KEY (article_id, finition, longueur_m)
);

-- Historique des mouvements de CMP (facultatif mais utile pour l'audit et pour
-- vérifier "CMP applicable au moment de la sortie" a posteriori sans recalcul complet).
CREATE TABLE cmp_historique (
    id                  TEXT PRIMARY KEY,
    article_id          TEXT NOT NULL REFERENCES article(id),
    finition             TEXT NOT NULL,
    longueur_m           REAL NOT NULL,
    mouvement_stock_id   TEXT NOT NULL REFERENCES mouvement_stock(id),
    quantite_totale_apres INTEGER NOT NULL,
    valeur_totale_apres   REAL NOT NULL,
    cmp_unitaire_apres    REAL NOT NULL,
    date_heure            TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);
CREATE INDEX idx_cmp_hist_pool ON cmp_historique(article_id, finition, longueur_m, date_heure);
