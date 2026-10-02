-- 0008_livraison_facturation.sql

CREATE TABLE bl_client (
    id                      TEXT PRIMARY KEY,
    numero                  TEXT NOT NULL UNIQUE,
    commande_client_id      TEXT NOT NULL REFERENCES commande_client(id),
    date                    TEXT NOT NULL,
    prix_transport_reel     REAL CHECK (prix_transport_reel IS NULL OR prix_transport_reel >= 0),  -- §18 : jamais le théorique
    cree_le                 TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                TEXT REFERENCES utilisateur(id)
);
CREATE INDEX idx_blc_commande ON bl_client(commande_client_id);

CREATE TABLE bl_client_ligne (
    id                      TEXT PRIMARY KEY,
    bl_client_id             TEXT NOT NULL REFERENCES bl_client(id),
    lot_id                   TEXT NOT NULL REFERENCES lot(id),
    commande_ligne_id        TEXT NOT NULL REFERENCES commande_ligne(id),
    type                     TEXT NOT NULL CHECK (type IN ('INITIALE','SUPPLEMENT')),
    quantite                 INTEGER NOT NULL CHECK (quantite > 0),
    poids_facturable_kg      REAL NOT NULL CHECK (poids_facturable_kg > 0),
    cout_cmp_unitaire        REAL  -- rempli uniquement pour type='SUPPLEMENT' (CMP au moment de la sortie, règle Phase 4 §1.3)
);
CREATE INDEX idx_blcl_lot ON bl_client_ligne(lot_id);
CREATE INDEX idx_blcl_commande_ligne ON bl_client_ligne(commande_ligne_id);

CREATE TABLE facture_client (
    id                          TEXT PRIMARY KEY,
    numero                      TEXT NOT NULL UNIQUE,
    commande_client_id          TEXT NOT NULL REFERENCES commande_client(id),
    date                        TEXT NOT NULL,
    montant_eur                 REAL NOT NULL CHECK (montant_eur >= 0),
    cours_change_declaration    REAL CHECK (cours_change_declaration IS NULL OR cours_change_declaration > 0),
    n_declaration_douane        TEXT,
    n_titre_banque               TEXT,
    banque                      TEXT,
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                    TEXT REFERENCES utilisateur(id)
);
CREATE INDEX idx_fac_commande ON facture_client(commande_client_id);

-- Rapprochement facture client / BL client : même principe que côté fournisseur.
CREATE TABLE facture_client_ligne (
    id                      TEXT PRIMARY KEY,
    facture_client_id       TEXT NOT NULL REFERENCES facture_client(id),
    bl_client_ligne_id      TEXT NOT NULL UNIQUE REFERENCES bl_client_ligne(id),
    prix_applique            REAL NOT NULL CHECK (prix_applique >= 0)
);
CREATE INDEX idx_facl_facture ON facture_client_ligne(facture_client_id);
