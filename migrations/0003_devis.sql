-- 0003_devis.sql

CREATE TABLE devis (
    id              TEXT PRIMARY KEY,
    numero          TEXT NOT NULL UNIQUE,
    client_id       TEXT NOT NULL REFERENCES client(id),
    date            TEXT NOT NULL,
    date_validite   TEXT NOT NULL,
    taux_change_id  TEXT NOT NULL REFERENCES taux_change(id),
    statut          TEXT NOT NULL CHECK (statut IN ('EN_COURS','CONFIRME','EXPIRE','ANNULE')),
    cree_le         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par        TEXT REFERENCES utilisateur(id),
    CHECK (date_validite >= date)
);
CREATE INDEX idx_devis_client ON devis(client_id);
CREATE INDEX idx_devis_validite ON devis(date_validite);

CREATE TABLE devis_ligne (
    id                      TEXT PRIMARY KEY,
    devis_id                TEXT NOT NULL REFERENCES devis(id),
    article_id              TEXT NOT NULL REFERENCES article(id),
    finition                TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m              REAL NOT NULL CHECK (longueur_m > 0),
    quantite                INTEGER NOT NULL CHECK (quantite > 0),
    pct_transformation      REAL NOT NULL DEFAULT 0 CHECK (pct_transformation >= 0),
    poids_theorique_kg      REAL NOT NULL CHECK (poids_theorique_kg > 0),  -- calculé côté application
    fournisseur_pressenti_id TEXT REFERENCES fournisseur(id),
    prix_achat_estimatif    REAL NOT NULL CHECK (prix_achat_estimatif >= 0),
    prix_transport_estimatif REAL CHECK (prix_transport_estimatif IS NULL OR prix_transport_estimatif >= 0),
    marge_pct               REAL,
    prix_vente              REAL NOT NULL CHECK (prix_vente >= 0)
);
CREATE INDEX idx_devis_ligne_devis ON devis_ligne(devis_id);

-- Badge "réservé" — molle, §23.1 : lecture seule pour affichage, n'intervient
-- dans aucun calcul de disponibilité (aucune contrainte de blocage ici, volontairement).
CREATE TABLE reservation_devis (
    id              TEXT PRIMARY KEY,
    devis_ligne_id  TEXT NOT NULL REFERENCES devis_ligne(id),
    article_id      TEXT NOT NULL REFERENCES article(id),
    finition        TEXT NOT NULL,
    longueur_m      REAL NOT NULL,
    quantite        INTEGER NOT NULL,
    expire_le       TEXT NOT NULL
);
CREATE INDEX idx_reservation_article ON reservation_devis(article_id, finition, longueur_m, expire_le);
