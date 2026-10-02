-- 0019_unite_valorisation_article.sql — Phase 5.5, finalisation (règle
-- définitive validée par l'utilisateur : « unité du CMP / coût de revient »).
--
-- Règle validée : le CMP n'est PAS systématiquement calculé en DT/kg. Il
-- est toujours exprimé dans l'UNITÉ DE VALORISATION de l'article : DT/KG,
-- DT/ML, DT/UNITE ou DT/TONNE. Cette unité dépend automatiquement de
-- l'unité de produit définie pour l'article ; le système n'en impose ni
-- n'en choisit aucune par défaut. Elle peut être changée selon les règles
-- de modification d'un article déjà validées (dérogation de Mohamed) :
-- l'ancienne unité est conservée dans l'historique, la nouvelle est
-- enregistrée, avec la date et l'utilisateur ; les historiques de coûts
-- précédents ne sont jamais réécrits silencieusement.
--
-- Pourquoi une migration est nécessaire (constat de l'analyse) : le schéma
-- n'avait aucune place pour une unité de valorisation. Les prix de lot, le
-- cache CMP et l'inventaire initial étaient implicitement « par pièce »
-- (le moteur multipliait toujours un nombre de pièces par un prix).
--
--   1. article_unite_valorisation : historique IMMUABLE de l'unité de
--      valorisation de chaque article (définition initiale, puis
--      changements datés, motivés, avec l'utilisateur) ;
--   2. lot.unite_prix : unité dans laquelle sont exprimés les prix du lot
--      (provisoire, définitif, régularisation), fixée automatiquement à la
--      création du lot = unité de valorisation de l'article à cet instant,
--      puis figée. Les lots déjà existants reçoivent 'UNITE' : c'est un
--      FAIT (le moteur précédent les valorisait par pièce), pas un choix
--      d'unité par défaut. Aucun article existant ne reçoit d'unité : elle
--      devra être définie par Mohamed avant toute nouvelle valorisation ;
--   3. inventaire_initial_ligne : ajout de unite_cout ; la contrainte
--      « valeur = pièces × coût » ne vaut plus que pour un coût à l'unité
--      (elle bloquait un coût au kg, au ml ou à la tonne) ;
--   4. cmp_stock_general / cmp_historique : ajout de l'unité de valorisation,
--      de la quantité dans cette unité et du poids. Ce sont des CACHES
--      reconstructibles (jamais source de vérité) : ils sont recréés vides
--      et régénérés par db/valorisation.py:reconstruire_cmp().
--
-- La base réelle ne contient aujourd'hui aucune donnée métier. Même
-- technique de reconstruction que les migrations 0016 à 0018.

PRAGMA foreign_keys = OFF;
PRAGMA legacy_alter_table = ON;

-- ═══════════════════════ 1. Historique de l'unité de valorisation ═══════════════════════
CREATE TABLE article_unite_valorisation (
    id                  TEXT PRIMARY KEY,
    article_id          TEXT NOT NULL REFERENCES article(id),
    -- DEFINITION_INITIALE : unité de l'article depuis son origine (une seule
    -- par article) ; CHANGEMENT : nouvelle unité à partir de date_effet.
    nature              TEXT NOT NULL CHECK (nature IN ('DEFINITION_INITIALE','CHANGEMENT')),
    unite               TEXT NOT NULL CHECK (unite IN ('KG','ML','UNITE','TONNE')),
    unite_precedente    TEXT CHECK (unite_precedente IS NULL
                                    OR unite_precedente IN ('KG','ML','UNITE','TONNE')),
    -- Instant (format du registre des mouvements, UTC) à partir duquel
    -- l'unité s'applique. Pour une définition initiale : instant de saisie
    -- (l'unité vaut alors depuis l'origine de l'article).
    date_effet          TEXT NOT NULL CHECK (date_effet = strftime('%Y-%m-%dT%H:%M:%f', date_effet)),
    -- Motif de la dérogation (obligatoire pour un changement).
    motif               TEXT,
    -- CMP de chaque pool de l'article au moment du changement, dans
    -- l'ancienne et dans la nouvelle unité (trace explicite de la conversion).
    detail_cmp          TEXT CHECK (detail_cmp IS NULL OR json_valid(detail_cmp)),
    cree_le             TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par            TEXT NOT NULL REFERENCES utilisateur(id),
    CHECK (
        (nature = 'DEFINITION_INITIALE' AND unite_precedente IS NULL)
        OR (nature = 'CHANGEMENT' AND unite_precedente IS NOT NULL
            AND unite_precedente <> unite AND motif IS NOT NULL AND trim(motif) <> '')
    )
);
CREATE UNIQUE INDEX ux_article_unite_definition_initiale
    ON article_unite_valorisation(article_id) WHERE nature = 'DEFINITION_INITIALE';
CREATE INDEX idx_article_unite_valorisation ON article_unite_valorisation(article_id, date_effet);

CREATE TRIGGER trg_article_unite_valorisation_no_update BEFORE UPDATE ON article_unite_valorisation
BEGIN SELECT RAISE(ABORT, 'historique d''unité de valorisation immuable : un changement s''enregistre par une nouvelle ligne'); END;
CREATE TRIGGER trg_article_unite_valorisation_no_delete BEFORE DELETE ON article_unite_valorisation
BEGIN SELECT RAISE(ABORT, 'suppression interdite : l''historique d''unité de valorisation se conserve'); END;

CREATE TRIGGER trg_article_unite_valorisation_controle BEFORE INSERT ON article_unite_valorisation
BEGIN
    SELECT RAISE(ABORT, 'unité de valorisation refusée : date d''effet dans le futur')
    WHERE NEW.date_effet > strftime('%Y-%m-%dT%H:%M:%f', 'now');
    SELECT RAISE(ABORT, 'changement d''unité refusé : aucune unité de valorisation définie pour cet article')
    WHERE NEW.nature = 'CHANGEMENT'
      AND NOT EXISTS (SELECT 1 FROM article_unite_valorisation WHERE article_id = NEW.article_id);
    SELECT RAISE(ABORT, 'changement d''unité refusé : l''unité précédente n''est pas l''unité en vigueur')
    WHERE NEW.nature = 'CHANGEMENT'
      AND NEW.unite_precedente <> (
          SELECT unite FROM article_unite_valorisation
          WHERE article_id = NEW.article_id
          ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC
          LIMIT 1);
    SELECT RAISE(ABORT, 'changement d''unité refusé : date d''effet antérieure au dernier changement')
    WHERE NEW.nature = 'CHANGEMENT'
      AND EXISTS (SELECT 1 FROM article_unite_valorisation
                  WHERE article_id = NEW.article_id AND nature = 'CHANGEMENT'
                    AND date_effet >= NEW.date_effet);
    SELECT RAISE(ABORT, 'changement d''unité refusé : des mouvements de stock de cet article sont datés après la date d''effet (réécriture de l''historique des coûts)')
    WHERE NEW.nature = 'CHANGEMENT'
      AND EXISTS (SELECT 1 FROM mouvement_stock m JOIN lot l ON l.id = m.lot_id
                  WHERE l.article_id = NEW.article_id AND m.date_heure >= NEW.date_effet);
END;

-- ═══════════════════════ 2. lot.unite_prix ═══════════════════════
ALTER TABLE lot ADD COLUMN unite_prix TEXT
    CHECK (unite_prix IS NULL OR unite_prix IN ('KG','ML','UNITE','TONNE'));
-- FAIT : tous les prix de lot existants étaient valorisés par pièce.
UPDATE lot SET unite_prix = 'UNITE' WHERE unite_prix IS NULL;

CREATE TRIGGER trg_lot_unite_prix_controle BEFORE INSERT ON lot
BEGIN
    SELECT RAISE(ABORT, 'lot refusé : aucune unité de valorisation définie pour cet article')
    WHERE NOT EXISTS (SELECT 1 FROM article_unite_valorisation WHERE article_id = NEW.article_id);
    SELECT RAISE(ABORT, 'lot refusé : l''unité du prix du lot doit être l''unité de valorisation en vigueur de l''article')
    WHERE NEW.unite_prix IS NOT NULL
      AND NEW.unite_prix <> (
          SELECT unite FROM article_unite_valorisation
          WHERE article_id = NEW.article_id
          ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC
          LIMIT 1);
END;
-- Unité fixée automatiquement à la création si elle n'est pas fournie.
CREATE TRIGGER trg_lot_unite_prix_auto AFTER INSERT ON lot WHEN NEW.unite_prix IS NULL
BEGIN
    UPDATE lot SET unite_prix = (
        SELECT unite FROM article_unite_valorisation
        WHERE article_id = NEW.article_id
        ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC
        LIMIT 1)
    WHERE id = NEW.id;
END;
CREATE TRIGGER trg_lot_unite_prix_figee BEFORE UPDATE OF unite_prix ON lot
WHEN OLD.unite_prix IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'lot.unite_prix est figée à la création du lot'); END;

-- ═══════════════════════ 3. inventaire_initial_ligne.unite_cout ═══════════════════════
CREATE TABLE inventaire_initial_ligne__new (
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
    -- Coût unitaire validé, exprimé dans unite_cout (= unité de valorisation
    -- de l'article) ; valeur = quantité dans cette unité × coût, exacte
    -- (contrôlée par le service ; contrainte directe pour l'unité).
    cout_unitaire_minor     INTEGER NOT NULL CHECK (cout_unitaire_minor >= 0),
    unite_cout              TEXT NOT NULL CHECK (unite_cout IN ('KG','ML','UNITE','TONNE')),
    valeur_minor            INTEGER NOT NULL CHECK (valeur_minor >= 0),
    devise                  TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    saisie_originale        TEXT NOT NULL CHECK (json_valid(saisie_originale)),
    cree_le                 TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                TEXT NOT NULL REFERENCES utilisateur(id),
    CHECK (unite_cout <> 'UNITE' OR valeur_minor = quantite * cout_unitaire_minor)
);
-- FAIT : jusqu'ici seul un coût par pièce était accepté.
INSERT INTO inventaire_initial_ligne__new
    (id, inventaire_initial_id, article_id, finition, longueur_m, quantite, poids_kg, emplacement,
     cout_unitaire_minor, unite_cout, valeur_minor, devise, saisie_originale, cree_le, cree_par)
SELECT id, inventaire_initial_id, article_id, finition, longueur_m, quantite, poids_kg, emplacement,
       cout_unitaire_minor, 'UNITE', valeur_minor, devise, saisie_originale, cree_le, cree_par
FROM inventaire_initial_ligne;
DROP TABLE inventaire_initial_ligne;
ALTER TABLE inventaire_initial_ligne__new RENAME TO inventaire_initial_ligne;
CREATE INDEX idx_inventaire_initial_ligne_entete ON inventaire_initial_ligne(inventaire_initial_id);
CREATE INDEX idx_inventaire_initial_ligne_article ON inventaire_initial_ligne(article_id);
CREATE TRIGGER trg_inventaire_initial_ligne_no_delete BEFORE DELETE ON inventaire_initial_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite : une ligne d''inventaire initial ne se supprime jamais'); END;
CREATE TRIGGER trg_inventaire_initial_ligne_no_update BEFORE UPDATE ON inventaire_initial_ligne
BEGIN SELECT RAISE(ABORT, 'inventaire_initial_ligne est immuable : une erreur se corrige par une correction d''inventaire'); END;

-- ═══════════════════════ 4. Cache CMP avec unité de valorisation ═══════════════════════
DROP TABLE cmp_historique;
DROP TABLE cmp_stock_general;

CREATE TABLE cmp_stock_general (
    article_id              TEXT NOT NULL REFERENCES article(id),
    finition                TEXT NOT NULL,
    longueur_m              REAL NOT NULL,
    -- Unité de valorisation en vigueur de l'article (à la dernière reconstruction).
    unite_valorisation      TEXT NOT NULL CHECK (unite_valorisation IN ('KG','ML','UNITE','TONNE')),
    quantite_totale         INTEGER NOT NULL DEFAULT 0,   -- pièces physiquement en STOCK_GMC
    poids_total_kg          REAL NOT NULL DEFAULT 0,
    quantite_valorisation   REAL NOT NULL DEFAULT 0,      -- dans unite_valorisation
    valeur_totale_minor     INTEGER NOT NULL DEFAULT 0,
    cmp_unitaire_minor      INTEGER NOT NULL DEFAULT 0,   -- par unite_valorisation (arrondi)
    devise                  TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    derniere_maj            TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    PRIMARY KEY (article_id, finition, longueur_m)
);

CREATE TABLE cmp_historique (
    id                          TEXT PRIMARY KEY,
    article_id                  TEXT NOT NULL REFERENCES article(id),
    finition                    TEXT NOT NULL,
    longueur_m                  REAL NOT NULL,
    mouvement_stock_id          TEXT NOT NULL REFERENCES mouvement_stock(id),
    -- Unité de valorisation en vigueur à la date du mouvement : un
    -- changement d'unité ne réécrit jamais les lignes antérieures.
    unite_valorisation          TEXT NOT NULL CHECK (unite_valorisation IN ('KG','ML','UNITE','TONNE')),
    quantite_totale_apres       INTEGER NOT NULL,
    poids_total_apres_kg        REAL NOT NULL,
    quantite_valorisation_apres REAL NOT NULL,
    valeur_totale_apres_minor   INTEGER NOT NULL,
    cmp_unitaire_apres_minor    INTEGER NOT NULL,
    montant_mouvement_minor     INTEGER NOT NULL,
    devise                      TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    date_heure                  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);
CREATE INDEX idx_cmp_hist_pool ON cmp_historique(article_id, finition, longueur_m, date_heure);

PRAGMA legacy_alter_table = OFF;
PRAGMA foreign_keys = ON;
