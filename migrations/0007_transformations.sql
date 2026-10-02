-- 0007_transformations.sql

CREATE TABLE bon_commande_transformation (
    id                      TEXT PRIMARY KEY,
    numero                  TEXT NOT NULL UNIQUE,
    transformateur_id       TEXT NOT NULL REFERENCES transformateur(id),
    commande_client_id      TEXT REFERENCES commande_client(id),  -- NULL = alimentation stock
    date                    TEXT NOT NULL,
    cree_le                 TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                TEXT REFERENCES utilisateur(id)
);

CREATE TABLE bon_commande_transformation_ligne (
    id                              TEXT PRIMARY KEY,
    bon_commande_transformation_id  TEXT NOT NULL REFERENCES bon_commande_transformation(id),
    article_id                      TEXT NOT NULL REFERENCES article(id),
    finition_demandee               TEXT NOT NULL CHECK (finition_demandee IN ('NOIR','GALVA','GPP')),
    format_debit                    TEXT,  -- ex. "2x6m" — nullable, seulement si débit demandé
    quantite_prevue                 INTEGER NOT NULL CHECK (quantite_prevue > 0)
);
CREATE INDEX idx_bct_ligne_bct ON bon_commande_transformation_ligne(bon_commande_transformation_id);

CREATE TABLE bon_sortie_transformation (
    id                              TEXT PRIMARY KEY,
    numero                          TEXT NOT NULL UNIQUE,
    transformateur_id               TEXT NOT NULL REFERENCES transformateur(id),  -- un bon par transformateur
    bon_commande_transformation_id  TEXT NOT NULL REFERENCES bon_commande_transformation(id),
    date                            TEXT NOT NULL,
    cree_le                         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                        TEXT REFERENCES utilisateur(id)
);

-- Origine = Stock GMC exclusivement (§25-A) — vérifié par trigger (migration 0013),
-- pas seulement par la FK, car "être en Stock GMC" est un état dérivé des mouvements.
CREATE TABLE bon_sortie_transformation_ligne (
    id                              TEXT PRIMARY KEY,
    bon_sortie_transformation_id    TEXT NOT NULL REFERENCES bon_sortie_transformation(id),
    lot_id                          TEXT NOT NULL REFERENCES lot(id),
    quantite                        INTEGER NOT NULL CHECK (quantite > 0)
);
CREATE INDEX idx_bst_ligne_bst ON bon_sortie_transformation_ligne(bon_sortie_transformation_id);
CREATE INDEX idx_bst_ligne_lot ON bon_sortie_transformation_ligne(lot_id);

CREATE TABLE reception_transformation (
    id                              TEXT PRIMARY KEY,
    numero                          TEXT NOT NULL UNIQUE,
    bon_sortie_transformation_id    TEXT NOT NULL REFERENCES bon_sortie_transformation(id),
    date                            TEXT NOT NULL,
    cree_le                         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                        TEXT REFERENCES utilisateur(id)
);

CREATE TABLE reception_transformation_ligne (
    id                                      TEXT PRIMARY KEY,
    reception_transformation_id             TEXT NOT NULL REFERENCES reception_transformation(id),
    bon_sortie_transformation_ligne_id      TEXT NOT NULL REFERENCES bon_sortie_transformation_ligne(id),
    lot_resultat_id                         TEXT REFERENCES lot(id),  -- NULL si entièrement chute
    quantite_recue                          INTEGER NOT NULL DEFAULT 0 CHECK (quantite_recue >= 0),
    poids_recu_kg                           REAL NOT NULL DEFAULT 0 CHECK (poids_recu_kg >= 0),
    quantite_chute                          INTEGER NOT NULL DEFAULT 0 CHECK (quantite_chute >= 0),
    poids_chute_kg                          REAL NOT NULL DEFAULT 0 CHECK (poids_chute_kg >= 0),
    CHECK (quantite_recue > 0 OR quantite_chute > 0)
);
CREATE INDEX idx_rtl_reception ON reception_transformation_ligne(reception_transformation_id);
CREATE INDEX idx_rtl_bstl ON reception_transformation_ligne(bon_sortie_transformation_ligne_id);
