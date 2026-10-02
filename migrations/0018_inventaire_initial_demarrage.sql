-- 0018_inventaire_initial_demarrage.sql — Phase 5.5, corrections validées par
-- l'utilisateur après le code de la Phase 5.5 (règle « démarrage du système
-- en 2026 » et règle transversale « unité obligatoire à la saisie »).
--
-- Règle validée : GMC ERP démarre en 2026 par un INVENTAIRE INITIAL DE
-- DÉMARRAGE, réalisé à l'instant exact de mise en service. Il devient le
-- stock initial du système ; ce n'est ni un achat, ni un BL fournisseur, ni
-- une réception, et il n'alimente pas les statistiques d'achat. Le stock du
-- 31/12/2025 n'est PAS l'ouverture automatique de 2026. Ensuite, chaque fin
-- d'année : inventaire théorique, inventaire physique, rapprochement,
-- correction/validation ; l'inventaire validé devient le stock d'ouverture
-- de l'année suivante (par corrections tracées dans le registre, jamais par
-- une nouvelle entrée de stock — module annuel développé ultérieurement).
--
-- La migration 0017 modélisait une « ouverture » datée du 31/12 de N-1
-- (tables stock_ouverture / stock_ouverture_ligne, type
-- ENTREE_STOCK_OUVERTURE). Elle n'est pas modifiée (une migration appliquée
-- ne se modifie jamais) : cette migration la remplace par :
--
--   * inventaire_initial        : en-tête UNIQUE (un seul inventaire de
--                                 démarrage), avec l'instant exact de mise en
--                                 service (horodatage du registre, UTC) ;
--   * inventaire_initial_ligne  : article, finition, longueur, pièces, poids,
--                                 emplacement réel, coût unitaire validé,
--                                 valeur, devise, créateur, et la SAISIE
--                                 D'ORIGINE avec ses unités (JSON) — règle
--                                 « l'unité saisie est conservée » ;
--   * lot.inventaire_initial_ligne_id (remplace stock_ouverture_ligne_id) ;
--   * type de mouvement ENTREE_INVENTAIRE_INITIAL (remplace
--     ENTREE_STOCK_OUVERTURE).
--
-- Choix technique (pas une règle métier) : renommer plutôt que réutiliser
-- « stock_ouverture », pour qu'aucun code futur ne confonde l'inventaire de
-- démarrage (seule création de stock sans document d'achat) avec le stock
-- d'ouverture des années suivantes (qui résulte du rapprochement annuel).
--
-- Données existantes : recopiées (horodatage = date de référence 0017 à
-- 23:59:59.999, saisie d'origine reconstituée et marquée comme telle). La
-- base ne contient aujourd'hui aucune donnée métier. Même technique de
-- reconstruction que les migrations 0016 et 0017.

PRAGMA foreign_keys = OFF;
PRAGMA legacy_alter_table = ON;

-- ═══════════════════════ 1. Inventaire initial de démarrage ═══════════════════════
CREATE TABLE inventaire_initial (
    id                          TEXT PRIMARY KEY,
    -- Un seul inventaire initial de démarrage dans le système.
    unique_demarrage            INTEGER NOT NULL DEFAULT 1 UNIQUE CHECK (unique_demarrage = 1),
    -- Instant exact de mise en service, au format du registre des mouvements.
    date_heure_mise_en_service  TEXT NOT NULL CHECK (
                                    date_heure_mise_en_service
                                    = strftime('%Y-%m-%dT%H:%M:%f', date_heure_mise_en_service)
                                ),
    observation                 TEXT,
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                    TEXT NOT NULL REFERENCES utilisateur(id)
);
INSERT INTO inventaire_initial (id, unique_demarrage, date_heure_mise_en_service, observation, cree_le, cree_par)
SELECT id, 1, date_reference || 'T23:59:59.999', observation, cree_le, cree_par
FROM stock_ouverture;

CREATE TABLE inventaire_initial_ligne (
    id                      TEXT PRIMARY KEY,
    inventaire_initial_id   TEXT NOT NULL REFERENCES inventaire_initial(id),
    article_id              TEXT NOT NULL REFERENCES article(id),
    finition                TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m              REAL NOT NULL CHECK (longueur_m > 0),
    quantite                INTEGER NOT NULL CHECK (quantite > 0),
    poids_kg                REAL NOT NULL CHECK (poids_kg > 0),
    emplacement             TEXT NOT NULL CHECK (
                                emplacement = 'STOCK_GMC'
                                OR emplacement LIKE 'CHEZ_TRANSFORMATEUR:_%'
                            ),
    cout_unitaire_minor     INTEGER NOT NULL CHECK (cout_unitaire_minor >= 0),
    valeur_minor            INTEGER NOT NULL CHECK (valeur_minor = quantite * cout_unitaire_minor),
    devise                  TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    -- Valeurs et unités telles que saisies (traçabilité), en JSON.
    saisie_originale        TEXT NOT NULL CHECK (json_valid(saisie_originale)),
    cree_le                 TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                TEXT NOT NULL REFERENCES utilisateur(id)
);
INSERT INTO inventaire_initial_ligne
    (id, inventaire_initial_id, article_id, finition, longueur_m, quantite, poids_kg, emplacement,
     cout_unitaire_minor, valeur_minor, devise, saisie_originale, cree_le, cree_par)
SELECT id, stock_ouverture_id, article_id, finition, longueur_m, quantite, poids_kg, emplacement,
       cout_unitaire_minor, valeur_minor, devise,
       json_object('reconstituee_par_migration_0018', 1,
                   'longueur', longueur_m || ' m', 'quantite', quantite || ' pièces',
                   'poids', poids_kg || ' kg'),
       cree_le, cree_par
FROM stock_ouverture_ligne;
CREATE INDEX idx_inventaire_initial_ligne_entete ON inventaire_initial_ligne(inventaire_initial_id);
CREATE INDEX idx_inventaire_initial_ligne_article ON inventaire_initial_ligne(article_id);

DROP TABLE stock_ouverture_ligne;
DROP TABLE stock_ouverture;

CREATE TRIGGER trg_inventaire_initial_no_delete BEFORE DELETE ON inventaire_initial
BEGIN SELECT RAISE(ABORT, 'suppression interdite : l''inventaire initial ne se supprime jamais'); END;
CREATE TRIGGER trg_inventaire_initial_no_update BEFORE UPDATE ON inventaire_initial
BEGIN SELECT RAISE(ABORT, 'inventaire_initial est immuable : une erreur se corrige par une correction d''inventaire'); END;
CREATE TRIGGER trg_inventaire_initial_ligne_no_delete BEFORE DELETE ON inventaire_initial_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite : une ligne d''inventaire initial ne se supprime jamais'); END;
CREATE TRIGGER trg_inventaire_initial_ligne_no_update BEFORE UPDATE ON inventaire_initial_ligne
BEGIN SELECT RAISE(ABORT, 'inventaire_initial_ligne est immuable : une erreur se corrige par une correction d''inventaire'); END;

-- ═══════════════════════ 2. lot : origine « inventaire initial » ═══════════════════════
CREATE TABLE lot__new (
    id                          TEXT PRIMARY KEY,
    article_id                  TEXT NOT NULL REFERENCES article(id),
    bl_fournisseur_ligne_id     TEXT UNIQUE REFERENCES bl_fournisseur_ligne(id),
    lot_parent_id               TEXT REFERENCES lot(id),
    inventaire_initial_ligne_id TEXT UNIQUE REFERENCES inventaire_initial_ligne(id),
    finition                    TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m                  REAL NOT NULL CHECK (longueur_m > 0),
    quantite_initiale           INTEGER NOT NULL CHECK (quantite_initiale > 0),
    poids_initial_kg            REAL NOT NULL CHECK (poids_initial_kg > 0),
    prix_unitaire_provisoire_minor INTEGER NOT NULL CHECK (prix_unitaire_provisoire_minor >= 0),
    prix_unitaire_definitif_minor  INTEGER CHECK (prix_unitaire_definitif_minor IS NULL OR prix_unitaire_definitif_minor >= 0),
    devise                      TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    -- Exactement UNE origine : réception fournisseur, transformation, ou
    -- inventaire initial de démarrage.
    CHECK (
        (bl_fournisseur_ligne_id IS NOT NULL)
        + (lot_parent_id IS NOT NULL)
        + (inventaire_initial_ligne_id IS NOT NULL) = 1
    )
);
INSERT INTO lot__new (id, article_id, bl_fournisseur_ligne_id, lot_parent_id, inventaire_initial_ligne_id,
                      finition, longueur_m, quantite_initiale, poids_initial_kg,
                      prix_unitaire_provisoire_minor, prix_unitaire_definitif_minor, devise, cree_le)
SELECT id, article_id, bl_fournisseur_ligne_id, lot_parent_id, stock_ouverture_ligne_id,
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

-- ═══════════════════════ 3. mouvement_stock : ENTREE_INVENTAIRE_INITIAL ═══════════════════════
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
                                'ENTREE_INVENTAIRE_INITIAL'
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
SELECT id, lot_id,
       CASE WHEN type = 'ENTREE_STOCK_OUVERTURE' THEN 'ENTREE_INVENTAIRE_INITIAL' ELSE type END,
       quantite, poids_kg, emplacement_source, emplacement_destination,
       CASE WHEN document_source_type = 'stock_ouverture_ligne' THEN 'inventaire_initial_ligne'
            ELSE document_source_type END,
       document_source_id, date_heure, utilisateur_id, motif
FROM mouvement_stock
ORDER BY rowid;
DROP TABLE mouvement_stock;
ALTER TABLE mouvement_stock__new RENAME TO mouvement_stock;
CREATE INDEX idx_mouvement_lot ON mouvement_stock(lot_id);
CREATE INDEX idx_mouvement_date ON mouvement_stock(date_heure);
CREATE INDEX idx_mouvement_type ON mouvement_stock(type);
CREATE INDEX idx_mouvement_source ON mouvement_stock(document_source_type, document_source_id);

CREATE UNIQUE INDEX ux_mouvement_entree_origine_par_lot ON mouvement_stock(lot_id)
WHERE type IN ('ENTREE_RECEPTION_FOURNISSEUR', 'ENTREE_RETOUR_TRANSFORMATION', 'ENTREE_INVENTAIRE_INITIAL');

CREATE UNIQUE INDEX ux_mouvement_type_par_document ON mouvement_stock(type, document_source_type, document_source_id)
WHERE type IN ('ENTREE_RECEPTION_FOURNISSEUR', 'SORTIE_TRANSFORMATION', 'ENTREE_RETOUR_TRANSFORMATION',
               'CONSOMMATION_TRANSFORMATION', 'SORTIE_CHUTE', 'SORTIE_LIVRAISON_CLIENT',
               'ENTREE_INVENTAIRE_INITIAL');

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
