-- 0010_macf.sql

CREATE TABLE macf_ligne_achat (
    id                          TEXT PRIMARY KEY,
    bl_fournisseur_ligne_id     TEXT NOT NULL UNIQUE REFERENCES bl_fournisseur_ligne(id),
    pays_origine                TEXT NOT NULL,
    see_reelle                  REAL,
    valeur_defaut_utilisee      REAL,
    statut                      TEXT NOT NULL CHECK (statut IN ('VERT','ORANGE','ROUGE')),
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);
CREATE INDEX idx_macf_statut ON macf_ligne_achat(statut);
