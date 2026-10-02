-- 0005_achats_fournisseurs.sql

CREATE TABLE bon_commande_fournisseur (
    id              TEXT PRIMARY KEY,
    numero          TEXT NOT NULL UNIQUE,
    fournisseur_id  TEXT NOT NULL REFERENCES fournisseur(id),
    date            TEXT NOT NULL,
    origine         TEXT NOT NULL CHECK (origine IN ('AFFAIRE','ALIMENTATION_STOCK')),
    statut          TEXT NOT NULL CHECK (statut IN ('ENVOYE','PARTIELLEMENT_RECU','SOLDE','ANNULE')),
    cree_le         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par        TEXT REFERENCES utilisateur(id)
);
CREATE INDEX idx_bcf_fournisseur ON bon_commande_fournisseur(fournisseur_id);

CREATE TABLE bon_commande_fournisseur_ligne (
    id                              TEXT PRIMARY KEY,
    bon_commande_fournisseur_id     TEXT NOT NULL REFERENCES bon_commande_fournisseur(id),
    article_id                      TEXT NOT NULL REFERENCES article(id),
    commande_ligne_id               TEXT REFERENCES commande_ligne(id),  -- NULL = alimentation stock générale
    quantite_commandee              INTEGER NOT NULL CHECK (quantite_commandee > 0),
    prix_negocie                    REAL NOT NULL CHECK (prix_negocie >= 0)
);
CREATE INDEX idx_bcfl_commande_ligne ON bon_commande_fournisseur_ligne(commande_ligne_id);
CREATE INDEX idx_bcfl_bcf ON bon_commande_fournisseur_ligne(bon_commande_fournisseur_id);

CREATE TABLE bl_fournisseur (
    id                          TEXT PRIMARY KEY,
    numero                      TEXT NOT NULL UNIQUE,          -- numéro interne GMC
    numero_origine_fournisseur  TEXT NOT NULL,                 -- n° BL réel du fournisseur, jamais remplacé
    fournisseur_id              TEXT NOT NULL REFERENCES fournisseur(id),
    date                        TEXT NOT NULL,
    statut                      TEXT NOT NULL CHECK (statut IN ('BROUILLON','VALIDE')),
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                    TEXT REFERENCES utilisateur(id)
);
CREATE INDEX idx_blf_fournisseur ON bl_fournisseur(fournisseur_id);

CREATE TABLE bl_fournisseur_ligne (
    id                                  TEXT PRIMARY KEY,
    bl_fournisseur_id                   TEXT NOT NULL REFERENCES bl_fournisseur(id),
    bon_commande_fournisseur_ligne_id   TEXT REFERENCES bon_commande_fournisseur_ligne(id),
    commande_ligne_id                   TEXT REFERENCES commande_ligne(id),  -- NULL = stock général
    article_id                          TEXT NOT NULL REFERENCES article(id),
    finition                            TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m                          REAL NOT NULL CHECK (longueur_m > 0),
    quantite                            INTEGER NOT NULL CHECK (quantite > 0),
    poids_kg                            REAL NOT NULL CHECK (poids_kg > 0),
    prix_unitaire_provisoire            REAL NOT NULL CHECK (prix_unitaire_provisoire >= 0)
    -- Le lot créé à la validation référence CETTE ligne via lot.bl_fournisseur_ligne_id
    -- (migration 0006) — relation 1:1 portée dans un seul sens pour éviter une
    -- dépendance circulaire entre les deux tables ; retrouver le lot d'une ligne
    -- de BL : SELECT * FROM lot WHERE bl_fournisseur_ligne_id = <cette ligne>.
);
CREATE INDEX idx_blfl_commande_ligne ON bl_fournisseur_ligne(commande_ligne_id);
CREATE INDEX idx_blfl_bcfl ON bl_fournisseur_ligne(bon_commande_fournisseur_ligne_id);

CREATE TABLE facture_fournisseur (
    id                          TEXT PRIMARY KEY,
    numero                      TEXT NOT NULL UNIQUE,
    numero_origine_fournisseur  TEXT NOT NULL,
    fournisseur_id              TEXT NOT NULL REFERENCES fournisseur(id),
    date                        TEXT NOT NULL,
    montant_total                REAL NOT NULL CHECK (montant_total >= 0),
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                    TEXT REFERENCES utilisateur(id)
);
CREATE INDEX idx_ffo_fournisseur ON facture_fournisseur(fournisseur_id);

-- Rapprochement BL / facture (point 13 de la Phase 3) : une ligne de BL n'est
-- facturée qu'une fois (UNIQUE) ; plusieurs lignes -> plusieurs BL différents
-- peuvent référencer la même facture_fournisseur_id, ce qui réalise nativement
-- le regroupement "plusieurs BL -> une facture de fin de mois".
CREATE TABLE facture_fournisseur_ligne (
    id                          TEXT PRIMARY KEY,
    facture_fournisseur_id      TEXT NOT NULL REFERENCES facture_fournisseur(id),
    bl_fournisseur_ligne_id     TEXT NOT NULL UNIQUE REFERENCES bl_fournisseur_ligne(id),
    prix_unitaire_definitif     REAL NOT NULL CHECK (prix_unitaire_definitif >= 0)
);
CREATE INDEX idx_ffl_facture ON facture_fournisseur_ligne(facture_fournisseur_id);
