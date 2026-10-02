-- 0001_referentiels.sql
-- Tables de référence communes (Phase 3 §B.1). Aucune ne porte de numéro humain
-- (ce ne sont pas des documents), toutes ont un id UUID (TEXT) en clé primaire.

CREATE TABLE utilisateur (
    id              TEXT PRIMARY KEY,
    nom             TEXT NOT NULL,
    role            TEXT NOT NULL CHECK (role IN ('COMMERCIAL','MAGASINIER','COMPTABILITE','DIRECTION','ADMINISTRATEUR')),
    mot_de_passe_hash TEXT NOT NULL,
    actif           INTEGER NOT NULL DEFAULT 1 CHECK (actif IN (0,1)),
    cree_le         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);

CREATE TABLE famille_article (
    id              TEXT PRIMARY KEY,
    libelle         TEXT NOT NULL UNIQUE
);

CREATE TABLE article (
    id                  TEXT PRIMARY KEY,
    designation         TEXT NOT NULL,
    famille_id          TEXT REFERENCES famille_article(id),
    masse_lineique_kg_m REAL NOT NULL CHECK (masse_lineique_kg_m > 0),
    pct_galva           REAL CHECK (pct_galva IS NULL OR pct_galva >= 0),
    cree_le             TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);
CREATE INDEX idx_article_famille ON article(famille_id);

CREATE TABLE client (
    id                  TEXT PRIMARY KEY,
    nom                 TEXT NOT NULL,
    destination_defaut  TEXT,
    incoterm_defaut     TEXT,
    cree_le             TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);

CREATE TABLE fournisseur (
    id      TEXT PRIMARY KEY,
    nom     TEXT NOT NULL,
    pays    TEXT NOT NULL,   -- obligatoire : source du pays d'origine pour le module MACF
    cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);

CREATE TABLE transformateur (
    id      TEXT PRIMARY KEY,
    nom     TEXT NOT NULL,
    type    TEXT NOT NULL CHECK (type IN ('GALVA','GPP','DEBIT','AUTRE')),
    cree_le TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);

-- Prix au kg par article pour un transformateur (§16 analyse fonctionnelle) :
-- utilisé pour (a) le prix de revient prévisionnel dès le devis, (b) la clé de
-- répartition de la facture mensuelle réelle (table repartition_cout_transformation, migration 0009).
CREATE TABLE prix_transformation (
    id                  TEXT PRIMARY KEY,
    transformateur_id   TEXT NOT NULL REFERENCES transformateur(id),
    article_id          TEXT NOT NULL REFERENCES article(id),
    prix_kg             REAL NOT NULL CHECK (prix_kg >= 0),
    date_effet          TEXT NOT NULL,
    UNIQUE (transformateur_id, article_id, date_effet)
);

-- Taux de change : append-only (voir migration 0012 pour le trigger d'immuabilité).
CREATE TABLE taux_change (
    id          TEXT PRIMARY KEY,
    date        TEXT NOT NULL,
    devise      TEXT NOT NULL,
    taux        REAL NOT NULL CHECK (taux > 0),
    contexte    TEXT NOT NULL CHECK (contexte IN ('DEVIS','DECLARATION_DOUANE')),
    cree_le     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);
