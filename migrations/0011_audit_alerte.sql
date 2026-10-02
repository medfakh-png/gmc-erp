-- 0011_audit_alerte.sql

CREATE TABLE journal_audit (
    id              TEXT PRIMARY KEY,
    utilisateur_id  TEXT NOT NULL REFERENCES utilisateur(id),
    date_heure      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    action          TEXT NOT NULL CHECK (action IN (
                        'REAFFECTATION','QUANTITE_SUPPLEMENTAIRE','CORRECTION_INVENTAIRE',
                        'RECEPTION_FOURNISSEUR','RECEPTION_TRANSFORMATION',
                        'SORTIE_TRANSFORMATION','SORTIE_LIVRAISON_CLIENT',
                        'MODIFICATION_PRIX','REGULARISATION_FACTURE_FOURNISSEUR',
                        'DEPASSEMENT_POIDS_VALIDATION','ARBITRAGE_PENURIE','ANNULATION_DOCUMENT'
                     )),
    entite_type     TEXT NOT NULL,
    entite_id       TEXT NOT NULL,
    affaire_id      TEXT REFERENCES commande_client(id),
    valeur_avant    TEXT,  -- JSON
    valeur_apres    TEXT,  -- JSON
    motif           TEXT
);
CREATE INDEX idx_audit_entite ON journal_audit(entite_type, entite_id);
CREATE INDEX idx_audit_date ON journal_audit(date_heure);
CREATE INDEX idx_audit_affaire ON journal_audit(affaire_id);

CREATE TABLE alerte (
    id              TEXT PRIMARY KEY,
    type            TEXT NOT NULL CHECK (type IN ('PIECES_MANQUANTES','DEPASSEMENT_POIDS_EN_ATTENTE','PENURIE_A_ARBITRER')),
    entite_type     TEXT NOT NULL,
    entite_id       TEXT NOT NULL,
    statut          TEXT NOT NULL DEFAULT 'OUVERTE' CHECK (statut IN ('OUVERTE','TRAITEE')),
    date            TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    traitee_le      TEXT,
    traitee_par     TEXT REFERENCES utilisateur(id)
);
CREATE INDEX idx_alerte_statut ON alerte(statut);
