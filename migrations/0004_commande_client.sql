-- 0004_commande_client.sql

CREATE TABLE commande_client (
    id                  TEXT PRIMARY KEY,
    numero              TEXT NOT NULL UNIQUE,
    devis_id            TEXT NOT NULL REFERENCES devis(id),
    client_id           TEXT NOT NULL REFERENCES client(id),
    date_confirmation   TEXT NOT NULL,
    statut              TEXT NOT NULL CHECK (statut IN ('BROUILLON','CONFIRMEE','SOLDEE','ANNULEE')),
    destination         TEXT,
    incoterm            TEXT,
    compagnie_maritime  TEXT,
    cree_le             TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par            TEXT REFERENCES utilisateur(id)
);
CREATE INDEX idx_commande_client_client ON commande_client(client_id);
CREATE INDEX idx_commande_client_statut ON commande_client(statut);

CREATE TABLE commande_ligne (
    id                  TEXT PRIMARY KEY,
    commande_client_id  TEXT NOT NULL REFERENCES commande_client(id),
    article_id          TEXT NOT NULL REFERENCES article(id),
    finition            TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m          REAL NOT NULL CHECK (longueur_m > 0),
    quantite_originale  INTEGER NOT NULL CHECK (quantite_originale > 0),  -- immuable après confirmation (trigger 0012)
    prix_negocie        REAL NOT NULL CHECK (prix_negocie >= 0)          -- modifiable (renégociation §20)
);
CREATE INDEX idx_commande_ligne_commande ON commande_ligne(commande_client_id);
CREATE INDEX idx_commande_ligne_article ON commande_ligne(article_id, finition, longueur_m);
