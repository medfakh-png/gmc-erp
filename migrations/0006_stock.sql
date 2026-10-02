-- 0006_stock.sql — le cœur du système (Phase 3 §B.5)

CREATE TABLE lot (
    id                          TEXT PRIMARY KEY,
    article_id                  TEXT NOT NULL REFERENCES article(id),
    bl_fournisseur_ligne_id     TEXT UNIQUE REFERENCES bl_fournisseur_ligne(id),  -- rempli si origine = réception directe
    lot_parent_id                TEXT REFERENCES lot(id),                         -- rempli si origine = transformation
    finition                    TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m                  REAL NOT NULL CHECK (longueur_m > 0),
    quantite_initiale           INTEGER NOT NULL CHECK (quantite_initiale > 0),  -- fixée à la création, ne change jamais
    poids_initial_kg            REAL NOT NULL CHECK (poids_initial_kg > 0),
    prix_unitaire_provisoire    REAL NOT NULL CHECK (prix_unitaire_provisoire >= 0),
    prix_unitaire_definitif     REAL CHECK (prix_unitaire_definitif IS NULL OR prix_unitaire_definitif >= 0),
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    -- Un lot vient soit directement d'une réception fournisseur, soit d'une transformation --
    -- jamais des deux, jamais d'aucun des deux :
    CHECK (
        (bl_fournisseur_ligne_id IS NOT NULL AND lot_parent_id IS NULL)
        OR (bl_fournisseur_ligne_id IS NULL AND lot_parent_id IS NOT NULL)
    )
);
CREATE INDEX idx_lot_article ON lot(article_id);
CREATE INDEX idx_lot_parent ON lot(lot_parent_id);

-- Registre append-only : la seule source de vérité du stock physique (§3.1 Phase 2,
-- décision technique n°4 Phase 2, confirmée absolue en Phase 4 §2/§C).
-- quantite et poids_kg sont toujours POSITIFS ; la direction est portée par
-- emplacement_source (si non NULL, on retire de cet emplacement) et
-- emplacement_destination (si non NULL, on ajoute à cet emplacement).
-- Emplacements possibles : 'STOCK_GMC', 'CHEZ_TRANSFORMATEUR:<id>', 'CHUTES', 'LIVRE'.
CREATE TABLE mouvement_stock (
    id                      TEXT PRIMARY KEY,
    lot_id                  TEXT NOT NULL REFERENCES lot(id),
    type                    TEXT NOT NULL CHECK (type IN (
                                'ENTREE_RECEPTION_FOURNISSEUR',
                                'SORTIE_TRANSFORMATION',
                                'ENTREE_RETOUR_TRANSFORMATION',
                                'SORTIE_CHUTE',
                                'SORTIE_LIVRAISON_CLIENT',
                                'TRANSFERT',
                                'CORRECTION_INVENTAIRE_POSITIVE',
                                'CORRECTION_INVENTAIRE_NEGATIVE'
                             )),
    quantite                INTEGER NOT NULL CHECK (quantite > 0),
    poids_kg                REAL NOT NULL CHECK (poids_kg > 0),
    emplacement_source      TEXT,
    emplacement_destination TEXT,
    document_source_type    TEXT NOT NULL,  -- référence polymorphe : nom de la table du document déclencheur
    document_source_id      TEXT NOT NULL,
    date_heure              TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    utilisateur_id          TEXT NOT NULL REFERENCES utilisateur(id),
    motif                   TEXT,  -- obligatoire côté application pour une correction d'inventaire
    CHECK (emplacement_source IS NOT NULL OR emplacement_destination IS NOT NULL)
);
CREATE INDEX idx_mouvement_lot ON mouvement_stock(lot_id);
CREATE INDEX idx_mouvement_date ON mouvement_stock(date_heure);
CREATE INDEX idx_mouvement_type ON mouvement_stock(type);
CREATE INDEX idx_mouvement_source ON mouvement_stock(document_source_type, document_source_id);

-- Affectation d'un lot (ou d'une quantité d'un lot) à une ligne de commande.
-- Ne crée JAMAIS de mouvement par elle-même (§27.1, §4 Phase 2).
CREATE TABLE affectation_stock (
    id                      TEXT PRIMARY KEY,
    lot_id                  TEXT NOT NULL REFERENCES lot(id),
    commande_ligne_id       TEXT NOT NULL REFERENCES commande_ligne(id),
    type                    TEXT NOT NULL CHECK (type IN ('INITIALE','SUPPLEMENT')),
    quantite                INTEGER NOT NULL CHECK (quantite > 0),
    poids_kg                REAL NOT NULL CHECK (poids_kg > 0),
    statut                  TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (statut IN ('ACTIVE','CLOTUREE')),
    utilisateur_id          TEXT NOT NULL REFERENCES utilisateur(id),
    date_heure              TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    motif                   TEXT,
    mouvement_physique_id   TEXT REFERENCES mouvement_stock(id)  -- rempli seulement à la sortie physique réelle
);
CREATE INDEX idx_affectation_lot ON affectation_stock(lot_id, statut);
CREATE INDEX idx_affectation_commande_ligne ON affectation_stock(commande_ligne_id);

-- Réaffectation : table dédiée, distincte de l'affectation (cas 7, décision Phase 3 §B.5/§G.2).
CREATE TABLE reaffectation (
    id                          TEXT PRIMARY KEY,
    affectation_origine_id      TEXT NOT NULL REFERENCES affectation_stock(id),
    affectation_destination_id  TEXT NOT NULL REFERENCES affectation_stock(id),
    quantite_reaffectee         INTEGER NOT NULL CHECK (quantite_reaffectee > 0),
    motif                       TEXT NOT NULL,   -- OBLIGATOIRE — jamais de réaffectation silencieuse (règle I, Phase 4)
    utilisateur_id              TEXT NOT NULL REFERENCES utilisateur(id),
    date_heure                  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);
CREATE INDEX idx_reaffectation_origine ON reaffectation(affectation_origine_id);

-- Chutes : rubrique séparée, jamais supprimée (règle H, Phase 4). Valorisation
-- CMP au moment de la sortie (nouvelle règle Phase 4) conservée en mémoire ;
-- impact_marge_valide reste à 0 tant que le traitement comptable n'est pas tranché (§25-C).
CREATE TABLE chute (
    id                                  TEXT PRIMARY KEY,
    lot_id                              TEXT NOT NULL REFERENCES lot(id),
    commande_client_id                  TEXT REFERENCES commande_client(id),
    transformateur_id                   TEXT NOT NULL REFERENCES transformateur(id),
    reception_transformation_ligne_id   TEXT NOT NULL REFERENCES reception_transformation_ligne(id),
    mouvement_stock_id                  TEXT NOT NULL REFERENCES mouvement_stock(id),
    quantite                            INTEGER NOT NULL CHECK (quantite > 0),
    poids_kg                            REAL NOT NULL CHECK (poids_kg > 0),
    observation                         TEXT,
    cout_cmp_unitaire                   REAL,   -- CMP au moment de la sortie (renseigné par db/valorisation.py)
    impact_marge_valide                 INTEGER NOT NULL DEFAULT 0 CHECK (impact_marge_valide IN (0,1)),
    date                                TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);
CREATE INDEX idx_chute_lot ON chute(lot_id);
CREATE INDEX idx_chute_affaire ON chute(commande_client_id);
