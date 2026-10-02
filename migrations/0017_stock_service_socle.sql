-- 0017_stock_service_socle.sql — Phase 5.5 (Stock Service), autorisée par la
-- validation officielle de l'analyse Phase 5.5 (points M1, M2, M3).
--
-- Aucune règle métier nouvelle n'est inventée ici : chaque modification
-- traduit une décision validée par l'utilisateur.
--
-- M2 — Retour de transformation (décision validée « transformations — stock
--      physique réel ») : nouveau type de mouvement CONSOMMATION_TRANSFORMATION.
--      Au retour d'une transformation, la quantité reçue quitte l'emplacement
--      CHEZ_TRANSFORMATEUR:<id> du lot d'origine (source = chez le
--      transformateur, aucune destination : la matière est devenue le lot
--      résultat), en même temps que le lot résultat entre en STOCK_GMC
--      (ENTREE_RETOUR_TRANSFORMATION). Sans cela, la quantité revenue restait
--      affichée chez le transformateur (stock fantôme, sonde E1 de l'analyse).
--      Le type TRANSFERT n'est volontairement PAS détourné pour cet usage.
--
-- M3 — Stock d'ouverture (décision validée « stock d'ouverture N = stock de
--      clôture N-1 ») : origine de stock spécifique, JAMAIS un achat.
--        * tables stock_ouverture (en-tête, une par année) et
--          stock_ouverture_ligne (article, finition, longueur, pièces, poids,
--          emplacement réel, coût unitaire validé, valeur, devise, créateur) ;
--        * nouveau type de mouvement ENTREE_STOCK_OUVERTURE ;
--        * lot : 3e origine possible (stock_ouverture_ligne_id), en plus de la
--          réception fournisseur et de la transformation — exactement une
--          origine par lot. Aucun faux BL fournisseur, aucune écriture dans
--          les tables d'achat : les statistiques achats/MACF ne sont pas
--          touchées.
--
-- M1 — Garde-fous anti-double-comptage en base (en complément des contrôles
--      du Stock Service) :
--        * une seule entrée d'origine par lot (réception fournisseur, retour
--          de transformation ou ouverture) — sonde E2 ;
--        * un seul mouvement d'un type donné par ligne de document source
--          (ex. une seule sortie par ligne de BL client — sonde E4).
--
-- Technique : identique à la migration 0016 (reconstruction de table :
-- nouvelle table -> copie des données -> suppression -> renommage, index et
-- triggers recréés à l'identique). La base ne contient aujourd'hui aucune
-- donnée métier, mais la migration copie les données existantes pour rester
-- correcte le jour où il y en aura. Les triggers sont recréés APRÈS la copie
-- des données (sinon le contrôle de solde serait rejoué ligne par ligne).

PRAGMA foreign_keys = OFF;
PRAGMA legacy_alter_table = ON;

-- ═══════════════════════ 1. Stock d'ouverture (M3) ═══════════════════════
CREATE TABLE stock_ouverture (
    id              TEXT PRIMARY KEY,
    annee           INTEGER NOT NULL UNIQUE CHECK (annee BETWEEN 2000 AND 2100),
    -- Date de référence du stock réel : 31/12 de l'année précédente
    -- (stock d'ouverture N = stock de clôture N-1).
    date_reference  TEXT NOT NULL CHECK (date_reference = printf('%04d-12-31', annee - 1)),
    observation     TEXT,
    cree_le         TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par        TEXT NOT NULL REFERENCES utilisateur(id)
);

CREATE TABLE stock_ouverture_ligne (
    id                  TEXT PRIMARY KEY,
    stock_ouverture_id  TEXT NOT NULL REFERENCES stock_ouverture(id),
    article_id          TEXT NOT NULL REFERENCES article(id),
    finition            TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m          REAL NOT NULL CHECK (longueur_m > 0),
    quantite            INTEGER NOT NULL CHECK (quantite > 0),
    poids_kg            REAL NOT NULL CHECK (poids_kg > 0),
    -- Emplacement réel du stock au 31/12 : le stock GMC comprend STOCK_GMC et
    -- chaque transformateur (décision validée Phase 5.5). CHUTES et LIVRE ne
    -- sont pas du stock.
    emplacement         TEXT NOT NULL CHECK (
                            emplacement = 'STOCK_GMC'
                            OR emplacement LIKE 'CHEZ_TRANSFORMATEUR:_%'
                        ),
    -- Coût unitaire déjà calculé et validé manuellement, PAR PIÈCE (même
    -- unité que lot.prix_unitaire_*_minor, utilisée par le moteur CMP), en
    -- unité monétaire minimale de `devise`.
    cout_unitaire_minor INTEGER NOT NULL CHECK (cout_unitaire_minor >= 0),
    valeur_minor        INTEGER NOT NULL CHECK (valeur_minor = quantite * cout_unitaire_minor),
    devise              TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    cree_le             TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par            TEXT NOT NULL REFERENCES utilisateur(id)
);
CREATE INDEX idx_stock_ouverture_ligne_entete ON stock_ouverture_ligne(stock_ouverture_id);
CREATE INDEX idx_stock_ouverture_ligne_article ON stock_ouverture_ligne(article_id);

-- Une ouverture validée ne se modifie ni ne se supprime : une erreur se
-- corrige par une correction d'inventaire tracée (mouvement + audit).
CREATE TRIGGER trg_stock_ouverture_no_delete BEFORE DELETE ON stock_ouverture
BEGIN SELECT RAISE(ABORT, 'suppression interdite : un stock d''ouverture ne se supprime jamais'); END;
CREATE TRIGGER trg_stock_ouverture_no_update BEFORE UPDATE ON stock_ouverture
BEGIN SELECT RAISE(ABORT, 'stock_ouverture est immuable : une erreur se corrige par une correction d''inventaire'); END;
CREATE TRIGGER trg_stock_ouverture_ligne_no_delete BEFORE DELETE ON stock_ouverture_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite : une ligne de stock d''ouverture ne se supprime jamais'); END;
CREATE TRIGGER trg_stock_ouverture_ligne_no_update BEFORE UPDATE ON stock_ouverture_ligne
BEGIN SELECT RAISE(ABORT, 'stock_ouverture_ligne est immuable : une erreur se corrige par une correction d''inventaire'); END;

-- ═══════════════════════ 2. lot : 3e origine (M3) ═══════════════════════
CREATE TABLE lot__new (
    id                          TEXT PRIMARY KEY,
    article_id                  TEXT NOT NULL REFERENCES article(id),
    bl_fournisseur_ligne_id     TEXT UNIQUE REFERENCES bl_fournisseur_ligne(id),
    lot_parent_id               TEXT REFERENCES lot(id),
    stock_ouverture_ligne_id    TEXT UNIQUE REFERENCES stock_ouverture_ligne(id),
    finition                    TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m                  REAL NOT NULL CHECK (longueur_m > 0),
    quantite_initiale           INTEGER NOT NULL CHECK (quantite_initiale > 0),
    poids_initial_kg            REAL NOT NULL CHECK (poids_initial_kg > 0),
    prix_unitaire_provisoire_minor INTEGER NOT NULL CHECK (prix_unitaire_provisoire_minor >= 0),
    prix_unitaire_definitif_minor  INTEGER CHECK (prix_unitaire_definitif_minor IS NULL OR prix_unitaire_definitif_minor >= 0),
    devise                      TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    -- Exactement UNE origine : réception fournisseur, transformation, ou
    -- stock d'ouverture — jamais deux, jamais aucune.
    CHECK (
        (bl_fournisseur_ligne_id IS NOT NULL)
        + (lot_parent_id IS NOT NULL)
        + (stock_ouverture_ligne_id IS NOT NULL) = 1
    )
);
INSERT INTO lot__new (id, article_id, bl_fournisseur_ligne_id, lot_parent_id, stock_ouverture_ligne_id,
                      finition, longueur_m, quantite_initiale, poids_initial_kg,
                      prix_unitaire_provisoire_minor, prix_unitaire_definitif_minor, devise, cree_le)
SELECT id, article_id, bl_fournisseur_ligne_id, lot_parent_id, NULL,
       finition, longueur_m, quantite_initiale, poids_initial_kg,
       prix_unitaire_provisoire_minor, prix_unitaire_definitif_minor, devise, cree_le
FROM lot;
DROP TABLE lot;
ALTER TABLE lot__new RENAME TO lot;
CREATE INDEX idx_lot_article ON lot(article_id);
CREATE INDEX idx_lot_parent ON lot(lot_parent_id);
CREATE TRIGGER trg_lot_no_delete BEFORE DELETE ON lot
BEGIN SELECT RAISE(ABORT, 'suppression interdite : un lot ne se supprime jamais, même épuisé'); END;
CREATE TRIGGER trg_lot_no_update_quantite BEFORE UPDATE OF quantite_initiale, poids_initial_kg ON lot
BEGIN SELECT RAISE(ABORT, 'lot.quantite_initiale et poids_initial_kg sont figés à la création'); END;

-- ═══════════════════════ 3. mouvement_stock : nouveaux types (M2, M3) + garde-fous (M1) ═══════════════════════
CREATE TABLE mouvement_stock__new (
    id                      TEXT PRIMARY KEY,
    lot_id                  TEXT NOT NULL REFERENCES lot(id),
    type                    TEXT NOT NULL CHECK (type IN (
                                'ENTREE_RECEPTION_FOURNISSEUR',
                                'SORTIE_TRANSFORMATION',
                                'ENTREE_RETOUR_TRANSFORMATION',
                                'CONSOMMATION_TRANSFORMATION',
                                'SORTIE_CHUTE',
                                'SORTIE_LIVRAISON_CLIENT',
                                'TRANSFERT',
                                'CORRECTION_INVENTAIRE_POSITIVE',
                                'CORRECTION_INVENTAIRE_NEGATIVE',
                                'ENTREE_STOCK_OUVERTURE'
                             )),
    quantite                INTEGER NOT NULL CHECK (quantite > 0),
    poids_kg                REAL NOT NULL CHECK (poids_kg > 0),
    emplacement_source      TEXT,
    emplacement_destination TEXT,
    document_source_type    TEXT NOT NULL,
    document_source_id      TEXT NOT NULL,
    date_heure              TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    utilisateur_id          TEXT NOT NULL REFERENCES utilisateur(id),
    motif                   TEXT,
    CHECK (emplacement_source IS NOT NULL OR emplacement_destination IS NOT NULL)
);
INSERT INTO mouvement_stock__new (id, lot_id, type, quantite, poids_kg, emplacement_source, emplacement_destination,
                                  document_source_type, document_source_id, date_heure, utilisateur_id, motif)
SELECT id, lot_id, type, quantite, poids_kg, emplacement_source, emplacement_destination,
       document_source_type, document_source_id, date_heure, utilisateur_id, motif
FROM mouvement_stock
ORDER BY rowid;
DROP TABLE mouvement_stock;
ALTER TABLE mouvement_stock__new RENAME TO mouvement_stock;
CREATE INDEX idx_mouvement_lot ON mouvement_stock(lot_id);
CREATE INDEX idx_mouvement_date ON mouvement_stock(date_heure);
CREATE INDEX idx_mouvement_type ON mouvement_stock(type);
CREATE INDEX idx_mouvement_source ON mouvement_stock(document_source_type, document_source_id);

-- M1 : une seule entrée d'origine par lot (un lot naît une seule fois).
CREATE UNIQUE INDEX ux_mouvement_entree_origine_par_lot ON mouvement_stock(lot_id)
WHERE type IN ('ENTREE_RECEPTION_FOURNISSEUR', 'ENTREE_RETOUR_TRANSFORMATION', 'ENTREE_STOCK_OUVERTURE');

-- M1 : un seul mouvement d'un type donné par ligne de document source
-- (une ligne de BL client = une seule sortie de livraison, etc.).
CREATE UNIQUE INDEX ux_mouvement_type_par_document ON mouvement_stock(type, document_source_type, document_source_id)
WHERE type IN ('ENTREE_RECEPTION_FOURNISSEUR', 'SORTIE_TRANSFORMATION', 'ENTREE_RETOUR_TRANSFORMATION',
               'CONSOMMATION_TRANSFORMATION', 'SORTIE_CHUTE', 'SORTIE_LIVRAISON_CLIENT',
               'ENTREE_STOCK_OUVERTURE');

CREATE TRIGGER trg_mouvement_solde_source BEFORE INSERT ON mouvement_stock
WHEN NEW.emplacement_source IS NOT NULL
BEGIN
    SELECT CASE WHEN (
        COALESCE((SELECT SUM(quantite) FROM mouvement_stock WHERE lot_id = NEW.lot_id AND emplacement_destination = NEW.emplacement_source), 0)
        - COALESCE((SELECT SUM(quantite) FROM mouvement_stock WHERE lot_id = NEW.lot_id AND emplacement_source = NEW.emplacement_source), 0)
    ) < NEW.quantite
    THEN RAISE(ABORT, 'mouvement impossible : solde insuffisant du lot à cet emplacement source')
    END;
END;
CREATE TRIGGER trg_mouvement_stock_no_delete BEFORE DELETE ON mouvement_stock
BEGIN SELECT RAISE(ABORT, 'mouvement_stock est immuable (append-only) : aucune suppression autorisée'); END;
CREATE TRIGGER trg_mouvement_stock_no_update BEFORE UPDATE ON mouvement_stock
BEGIN SELECT RAISE(ABORT, 'mouvement_stock est immuable (append-only) : aucune modification autorisée'); END;

PRAGMA legacy_alter_table = OFF;
PRAGMA foreign_keys = ON;
