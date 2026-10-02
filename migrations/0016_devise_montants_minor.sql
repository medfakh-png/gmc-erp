-- 0016_devise_montants_minor.sql — Phase 4.1, correction n°2
--
-- Tous les MONTANTS FINANCIERS passent de REAL à INTEGER (unité monétaire
-- minimale : millimes pour TND, centimes pour EUR, cents pour USD), chaque
-- montant étant désormais associé explicitement à une colonne `devise`
-- (TND/EUR/USD). Ceci élimine tout risque d'erreur d'arrondi en virgule
-- flottante sur les montants (ce que REAL/FLOAT ne garantit jamais).
--
-- Conversion : TND → ×1000 (5,250 TND = 5250 millimes) ; EUR/USD → ×100
-- (5,20 = 520). La base ne contient aujourd'hui AUCUNE ligne de donnée
-- métier (vérifié : 0 ligne sur toutes les tables avant cette migration) —
-- la conversion ci-dessous est donc sans perte par construction, mais est
-- écrite comme une vraie migration de données (SELECT ... FROM table),
-- pas comme une simple recréation de schéma, pour rester correcte le jour
-- où la base contiendra de vraies données.
--
-- Défaut de devise : 'TND' (devise d'exploitation locale de GMC), sauf
-- pour `facture_client` où le nom d'origine de la colonne (`montant_eur`)
-- et le contexte MACF/douane déjà validé (taux_change.contexte =
-- 'DECLARATION_DOUANE') établissent sans ambiguïté que la facturation
-- client se fait en EUR. Ce défaut TND est un choix TECHNIQUE de bascule
-- documenté ici, pas une règle métier : chaque ligne reste libre de porter
-- sa propre devise via la colonne `devise`, à choisir par le futur code
-- métier (Phase 5) au moment de la saisie réelle.
--
-- Colonnes explicitement laissées en REAL (pas des montants financiers) :
--   - taux_change.taux, facture_client.cours_change_declaration : un TAUX
--     DE CHANGE est un ratio, pas un montant dans une devise donnée.
--   - macf_ligne_achat.see_reelle, valeur_defaut_utilisee : émissions CO2
--     (tCO2e), une quantité physique/environnementale, pas monétaire.
--   - Toutes les colonnes de poids (poids_kg...), longueur_m, pct_galva,
--     pct_transformation, marge_pct : quantités physiques ou pourcentages.
--
-- SQLite ne permet pas de changer le type d'une colonne existante : chaque
-- table concernée est reconstruite (nouvelle table -> copie -> suppression
-- de l'ancienne -> renommage), avec ses index et triggers recréés à
-- l'identique. Les vues ne référencent que des colonnes non monétaires de
-- ces tables et continuent de fonctionner sans modification.

PRAGMA foreign_keys = OFF;

-- legacy_alter_table=ON désactive la validation croisée que SQLite (>=3.25)
-- effectue normalement lors d'un ALTER TABLE ... RENAME TO : par défaut,
-- SQLite tente de revalider TOUTES les vues/triggers du schéma à chaque
-- renommage, et échoue dès qu'une vue référence une table momentanément
-- absente (le cas ici : plusieurs vues référencent des tables en cours de
-- reconstruction dans CETTE même migration). Comme les tables sont
-- reconstruites sous leur nom d'origine (pas de vrai renommage sémantique),
-- ce mode « historique » est sûr : les vues continueront de référencer le
-- même nom de table, simplement sans la revalidation immédiate inutile.
PRAGMA legacy_alter_table = ON;

-- ═══════════════════════ 1. prix_transformation ═══════════════════════
CREATE TABLE prix_transformation__new (
    id                  TEXT PRIMARY KEY,
    transformateur_id   TEXT NOT NULL REFERENCES transformateur(id),
    article_id          TEXT NOT NULL REFERENCES article(id),
    prix_kg_minor       INTEGER NOT NULL CHECK (prix_kg_minor >= 0),
    devise              TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    date_effet          TEXT NOT NULL,
    UNIQUE (transformateur_id, article_id, date_effet)
);
INSERT INTO prix_transformation__new (id, transformateur_id, article_id, prix_kg_minor, devise, date_effet)
SELECT id, transformateur_id, article_id, CAST(ROUND(prix_kg * 1000) AS INTEGER), 'TND', date_effet
FROM prix_transformation;
DROP TABLE prix_transformation;
ALTER TABLE prix_transformation__new RENAME TO prix_transformation;

-- ═══════════════════════ 2. commande_ligne ═══════════════════════
CREATE TABLE commande_ligne__new (
    id                  TEXT PRIMARY KEY,
    commande_client_id  TEXT NOT NULL REFERENCES commande_client(id),
    article_id          TEXT NOT NULL REFERENCES article(id),
    finition            TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m          REAL NOT NULL CHECK (longueur_m > 0),
    quantite_originale  INTEGER NOT NULL CHECK (quantite_originale > 0),
    prix_negocie_minor  INTEGER NOT NULL CHECK (prix_negocie_minor >= 0),
    devise              TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD'))
);
INSERT INTO commande_ligne__new (id, commande_client_id, article_id, finition, longueur_m, quantite_originale, prix_negocie_minor, devise)
SELECT id, commande_client_id, article_id, finition, longueur_m, quantite_originale, CAST(ROUND(prix_negocie * 1000) AS INTEGER), 'TND'
FROM commande_ligne;
DROP TABLE commande_ligne;
ALTER TABLE commande_ligne__new RENAME TO commande_ligne;
CREATE INDEX idx_commande_ligne_commande ON commande_ligne(commande_client_id);
CREATE INDEX idx_commande_ligne_article ON commande_ligne(article_id, finition, longueur_m);
CREATE TRIGGER trg_commande_ligne_no_delete BEFORE DELETE ON commande_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_commande_ligne_qte_immuable BEFORE UPDATE OF quantite_originale ON commande_ligne
WHEN OLD.quantite_originale != NEW.quantite_originale
BEGIN SELECT RAISE(ABORT, 'commande_ligne.quantite_originale est immuable après création (§27.1) : un écart se gère par supplément ou réaffectation, jamais par modification de la quantité initiale'); END;

-- ═══════════════════════ 3. bon_commande_fournisseur_ligne ═══════════════════════
CREATE TABLE bon_commande_fournisseur_ligne__new (
    id                              TEXT PRIMARY KEY,
    bon_commande_fournisseur_id     TEXT NOT NULL REFERENCES bon_commande_fournisseur(id),
    article_id                      TEXT NOT NULL REFERENCES article(id),
    commande_ligne_id               TEXT REFERENCES commande_ligne(id),
    quantite_commandee              INTEGER NOT NULL CHECK (quantite_commandee > 0),
    prix_negocie_minor              INTEGER NOT NULL CHECK (prix_negocie_minor >= 0),
    devise                          TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD'))
);
INSERT INTO bon_commande_fournisseur_ligne__new (id, bon_commande_fournisseur_id, article_id, commande_ligne_id, quantite_commandee, prix_negocie_minor, devise)
SELECT id, bon_commande_fournisseur_id, article_id, commande_ligne_id, quantite_commandee, CAST(ROUND(prix_negocie * 1000) AS INTEGER), 'TND'
FROM bon_commande_fournisseur_ligne;
DROP TABLE bon_commande_fournisseur_ligne;
ALTER TABLE bon_commande_fournisseur_ligne__new RENAME TO bon_commande_fournisseur_ligne;
CREATE INDEX idx_bcfl_commande_ligne ON bon_commande_fournisseur_ligne(commande_ligne_id);
CREATE INDEX idx_bcfl_bcf ON bon_commande_fournisseur_ligne(bon_commande_fournisseur_id);
CREATE TRIGGER trg_bcfl_no_delete BEFORE DELETE ON bon_commande_fournisseur_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

-- ═══════════════════════ 4. bl_fournisseur_ligne ═══════════════════════
CREATE TABLE bl_fournisseur_ligne__new (
    id                                  TEXT PRIMARY KEY,
    bl_fournisseur_id                   TEXT NOT NULL REFERENCES bl_fournisseur(id),
    bon_commande_fournisseur_ligne_id   TEXT REFERENCES bon_commande_fournisseur_ligne(id),
    commande_ligne_id                   TEXT REFERENCES commande_ligne(id),
    article_id                          TEXT NOT NULL REFERENCES article(id),
    finition                            TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m                          REAL NOT NULL CHECK (longueur_m > 0),
    quantite                            INTEGER NOT NULL CHECK (quantite > 0),
    poids_kg                            REAL NOT NULL CHECK (poids_kg > 0),
    prix_unitaire_provisoire_minor      INTEGER NOT NULL CHECK (prix_unitaire_provisoire_minor >= 0),
    devise                              TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD'))
);
INSERT INTO bl_fournisseur_ligne__new (id, bl_fournisseur_id, bon_commande_fournisseur_ligne_id, commande_ligne_id, article_id, finition, longueur_m, quantite, poids_kg, prix_unitaire_provisoire_minor, devise)
SELECT id, bl_fournisseur_id, bon_commande_fournisseur_ligne_id, commande_ligne_id, article_id, finition, longueur_m, quantite, poids_kg, CAST(ROUND(prix_unitaire_provisoire * 1000) AS INTEGER), 'TND'
FROM bl_fournisseur_ligne;
DROP TABLE bl_fournisseur_ligne;
ALTER TABLE bl_fournisseur_ligne__new RENAME TO bl_fournisseur_ligne;
CREATE INDEX idx_blfl_commande_ligne ON bl_fournisseur_ligne(commande_ligne_id);
CREATE INDEX idx_blfl_bcfl ON bl_fournisseur_ligne(bon_commande_fournisseur_ligne_id);
CREATE TRIGGER trg_blfl_no_delete BEFORE DELETE ON bl_fournisseur_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

-- ═══════════════════════ 5. facture_fournisseur ═══════════════════════
CREATE TABLE facture_fournisseur__new (
    id                          TEXT PRIMARY KEY,
    numero                      TEXT NOT NULL UNIQUE,
    numero_origine_fournisseur  TEXT NOT NULL,
    fournisseur_id              TEXT NOT NULL REFERENCES fournisseur(id),
    date                        TEXT NOT NULL,
    montant_total_minor         INTEGER NOT NULL CHECK (montant_total_minor >= 0),
    devise                      TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                    TEXT REFERENCES utilisateur(id)
);
INSERT INTO facture_fournisseur__new (id, numero, numero_origine_fournisseur, fournisseur_id, date, montant_total_minor, devise, cree_le, cree_par)
SELECT id, numero, numero_origine_fournisseur, fournisseur_id, date, CAST(ROUND(montant_total * 1000) AS INTEGER), 'TND', cree_le, cree_par
FROM facture_fournisseur;
DROP TABLE facture_fournisseur;
ALTER TABLE facture_fournisseur__new RENAME TO facture_fournisseur;
CREATE INDEX idx_ffo_fournisseur ON facture_fournisseur(fournisseur_id);
CREATE TRIGGER trg_ffo_no_delete BEFORE DELETE ON facture_fournisseur
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

-- ═══════════════════════ 6. facture_fournisseur_ligne ═══════════════════════
CREATE TABLE facture_fournisseur_ligne__new (
    id                          TEXT PRIMARY KEY,
    facture_fournisseur_id      TEXT NOT NULL REFERENCES facture_fournisseur(id),
    bl_fournisseur_ligne_id     TEXT NOT NULL UNIQUE REFERENCES bl_fournisseur_ligne(id),
    prix_unitaire_definitif_minor REAL NOT NULL,
    devise                      TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD'))
);
-- (prix_unitaire_definitif_minor corrigé en INTEGER juste après — voir note technique)
DROP TABLE facture_fournisseur_ligne__new;
CREATE TABLE facture_fournisseur_ligne__new (
    id                          TEXT PRIMARY KEY,
    facture_fournisseur_id      TEXT NOT NULL REFERENCES facture_fournisseur(id),
    bl_fournisseur_ligne_id     TEXT NOT NULL UNIQUE REFERENCES bl_fournisseur_ligne(id),
    prix_unitaire_definitif_minor INTEGER NOT NULL CHECK (prix_unitaire_definitif_minor >= 0),
    devise                      TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD'))
);
INSERT INTO facture_fournisseur_ligne__new (id, facture_fournisseur_id, bl_fournisseur_ligne_id, prix_unitaire_definitif_minor, devise)
SELECT id, facture_fournisseur_id, bl_fournisseur_ligne_id, CAST(ROUND(prix_unitaire_definitif * 1000) AS INTEGER), 'TND'
FROM facture_fournisseur_ligne;
DROP TABLE facture_fournisseur_ligne;
ALTER TABLE facture_fournisseur_ligne__new RENAME TO facture_fournisseur_ligne;
CREATE INDEX idx_ffl_facture ON facture_fournisseur_ligne(facture_fournisseur_id);
CREATE TRIGGER trg_ffl_no_delete BEFORE DELETE ON facture_fournisseur_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

-- ═══════════════════════ 7. devis_ligne ═══════════════════════
CREATE TABLE devis_ligne__new (
    id                      TEXT PRIMARY KEY,
    devis_id                TEXT NOT NULL REFERENCES devis(id),
    article_id              TEXT NOT NULL REFERENCES article(id),
    finition                TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m              REAL NOT NULL CHECK (longueur_m > 0),
    quantite                INTEGER NOT NULL CHECK (quantite > 0),
    pct_transformation      REAL NOT NULL DEFAULT 0 CHECK (pct_transformation >= 0),
    poids_theorique_kg      REAL NOT NULL CHECK (poids_theorique_kg > 0),
    fournisseur_pressenti_id TEXT REFERENCES fournisseur(id),
    prix_achat_estimatif_minor    INTEGER NOT NULL CHECK (prix_achat_estimatif_minor >= 0),
    prix_transport_estimatif_minor INTEGER CHECK (prix_transport_estimatif_minor IS NULL OR prix_transport_estimatif_minor >= 0),
    marge_pct               REAL,
    prix_vente_minor        INTEGER NOT NULL CHECK (prix_vente_minor >= 0),
    devise                  TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD'))
);
INSERT INTO devis_ligne__new (id, devis_id, article_id, finition, longueur_m, quantite, pct_transformation, poids_theorique_kg, fournisseur_pressenti_id, prix_achat_estimatif_minor, prix_transport_estimatif_minor, marge_pct, prix_vente_minor, devise)
SELECT id, devis_id, article_id, finition, longueur_m, quantite, pct_transformation, poids_theorique_kg, fournisseur_pressenti_id,
       CAST(ROUND(prix_achat_estimatif * 1000) AS INTEGER),
       CASE WHEN prix_transport_estimatif IS NULL THEN NULL ELSE CAST(ROUND(prix_transport_estimatif * 1000) AS INTEGER) END,
       marge_pct, CAST(ROUND(prix_vente * 1000) AS INTEGER), 'TND'
FROM devis_ligne;
DROP TABLE devis_ligne;
ALTER TABLE devis_ligne__new RENAME TO devis_ligne;
CREATE INDEX idx_devis_ligne_devis ON devis_ligne(devis_id);
CREATE TRIGGER trg_devis_ligne_no_delete BEFORE DELETE ON devis_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

-- ═══════════════════════ 8. lot ═══════════════════════
CREATE TABLE lot__new (
    id                          TEXT PRIMARY KEY,
    article_id                  TEXT NOT NULL REFERENCES article(id),
    bl_fournisseur_ligne_id     TEXT UNIQUE REFERENCES bl_fournisseur_ligne(id),
    lot_parent_id                TEXT REFERENCES lot(id),
    finition                    TEXT NOT NULL CHECK (finition IN ('NOIR','GALVA','GPP')),
    longueur_m                  REAL NOT NULL CHECK (longueur_m > 0),
    quantite_initiale           INTEGER NOT NULL CHECK (quantite_initiale > 0),
    poids_initial_kg            REAL NOT NULL CHECK (poids_initial_kg > 0),
    prix_unitaire_provisoire_minor INTEGER NOT NULL CHECK (prix_unitaire_provisoire_minor >= 0),
    prix_unitaire_definitif_minor  INTEGER CHECK (prix_unitaire_definitif_minor IS NULL OR prix_unitaire_definitif_minor >= 0),
    devise                       TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    CHECK (
        (bl_fournisseur_ligne_id IS NOT NULL AND lot_parent_id IS NULL)
        OR (bl_fournisseur_ligne_id IS NULL AND lot_parent_id IS NOT NULL)
    )
);
INSERT INTO lot__new (id, article_id, bl_fournisseur_ligne_id, lot_parent_id, finition, longueur_m, quantite_initiale, poids_initial_kg, prix_unitaire_provisoire_minor, prix_unitaire_definitif_minor, devise, cree_le)
SELECT id, article_id, bl_fournisseur_ligne_id, lot_parent_id, finition, longueur_m, quantite_initiale, poids_initial_kg,
       CAST(ROUND(prix_unitaire_provisoire * 1000) AS INTEGER),
       CASE WHEN prix_unitaire_definitif IS NULL THEN NULL ELSE CAST(ROUND(prix_unitaire_definitif * 1000) AS INTEGER) END,
       'TND', cree_le
FROM lot;
DROP TABLE lot;
ALTER TABLE lot__new RENAME TO lot;
CREATE INDEX idx_lot_article ON lot(article_id);
CREATE INDEX idx_lot_parent ON lot(lot_parent_id);
CREATE TRIGGER trg_lot_no_delete BEFORE DELETE ON lot
BEGIN SELECT RAISE(ABORT, 'suppression interdite : un lot ne se supprime jamais, même épuisé'); END;
CREATE TRIGGER trg_lot_no_update_quantite BEFORE UPDATE OF quantite_initiale, poids_initial_kg ON lot
BEGIN SELECT RAISE(ABORT, 'lot.quantite_initiale et poids_initial_kg sont figés à la création'); END;

-- ═══════════════════════ 9. chute ═══════════════════════
-- cout_cmp_unitaire (par unité) -> cout_cmp_total_minor (montant TOTAL exact
-- pour la quantité de cette chute). Renommage délibéré (Phase 4.1) : un CMP
-- par unité stocké en entier arrondi, puis multiplié par la quantité,
-- réintroduirait une dérive d'arrondi à chaque calcul — exactement ce que
-- cette phase corrective doit éliminer. Le TOTAL exact est calculé une
-- seule fois par db/valorisation.py (voir docs/PRIX_REVIENT.md) et c'est
-- lui qui a un sens pour la consolidation annuelle (§3 du cadrage).
CREATE TABLE chute__new (
    id                                  TEXT PRIMARY KEY,
    lot_id                              TEXT NOT NULL REFERENCES lot(id),
    commande_client_id                  TEXT REFERENCES commande_client(id),
    transformateur_id                   TEXT NOT NULL REFERENCES transformateur(id),
    reception_transformation_ligne_id   TEXT NOT NULL REFERENCES reception_transformation_ligne(id),
    mouvement_stock_id                  TEXT NOT NULL REFERENCES mouvement_stock(id),
    quantite                            INTEGER NOT NULL CHECK (quantite > 0),
    poids_kg                            REAL NOT NULL CHECK (poids_kg > 0),
    observation                         TEXT,
    cout_cmp_total_minor                INTEGER,
    devise                              TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    impact_marge_valide                 INTEGER NOT NULL DEFAULT 0 CHECK (impact_marge_valide IN (0,1)),
    date                                TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);
INSERT INTO chute__new (id, lot_id, commande_client_id, transformateur_id, reception_transformation_ligne_id, mouvement_stock_id, quantite, poids_kg, observation, cout_cmp_total_minor, devise, impact_marge_valide, date)
SELECT id, lot_id, commande_client_id, transformateur_id, reception_transformation_ligne_id, mouvement_stock_id, quantite, poids_kg, observation,
       CASE WHEN cout_cmp_unitaire IS NULL THEN NULL ELSE CAST(ROUND(cout_cmp_unitaire * quantite * 1000) AS INTEGER) END,
       'TND', impact_marge_valide, date
FROM chute;
DROP TABLE chute;
ALTER TABLE chute__new RENAME TO chute;
CREATE INDEX idx_chute_lot ON chute(lot_id);
CREATE INDEX idx_chute_affaire ON chute(commande_client_id);
CREATE TRIGGER trg_chute_no_delete BEFORE DELETE ON chute
BEGIN SELECT RAISE(ABORT, 'suppression interdite : une chute reste dans le système même si son traitement comptable évolue'); END;

-- ═══════════════════════ 10. bl_client ═══════════════════════
CREATE TABLE bl_client__new (
    id                      TEXT PRIMARY KEY,
    numero                  TEXT NOT NULL UNIQUE,
    commande_client_id      TEXT NOT NULL REFERENCES commande_client(id),
    date                    TEXT NOT NULL,
    prix_transport_reel_minor INTEGER CHECK (prix_transport_reel_minor IS NULL OR prix_transport_reel_minor >= 0),
    devise                  TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    cree_le                 TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                TEXT REFERENCES utilisateur(id)
);
INSERT INTO bl_client__new (id, numero, commande_client_id, date, prix_transport_reel_minor, devise, cree_le, cree_par)
SELECT id, numero, commande_client_id, date,
       CASE WHEN prix_transport_reel IS NULL THEN NULL ELSE CAST(ROUND(prix_transport_reel * 1000) AS INTEGER) END,
       'TND', cree_le, cree_par
FROM bl_client;
DROP TABLE bl_client;
ALTER TABLE bl_client__new RENAME TO bl_client;
CREATE INDEX idx_blc_commande ON bl_client(commande_client_id);
CREATE TRIGGER trg_blc_no_delete BEFORE DELETE ON bl_client
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

-- ═══════════════════════ 11. bl_client_ligne ═══════════════════════
-- Même renommage/raisonnement que pour chute (montant TOTAL exact, pas un
-- prix unitaire arrondi) : cout_cmp_unitaire -> cout_cmp_total_minor.
CREATE TABLE bl_client_ligne__new (
    id                      TEXT PRIMARY KEY,
    bl_client_id             TEXT NOT NULL REFERENCES bl_client(id),
    lot_id                   TEXT NOT NULL REFERENCES lot(id),
    commande_ligne_id        TEXT NOT NULL REFERENCES commande_ligne(id),
    type                     TEXT NOT NULL CHECK (type IN ('INITIALE','SUPPLEMENT')),
    quantite                 INTEGER NOT NULL CHECK (quantite > 0),
    poids_facturable_kg      REAL NOT NULL CHECK (poids_facturable_kg > 0),
    cout_cmp_total_minor     INTEGER,
    devise                   TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD'))
);
INSERT INTO bl_client_ligne__new (id, bl_client_id, lot_id, commande_ligne_id, type, quantite, poids_facturable_kg, cout_cmp_total_minor, devise)
SELECT id, bl_client_id, lot_id, commande_ligne_id, type, quantite, poids_facturable_kg,
       CASE WHEN cout_cmp_unitaire IS NULL THEN NULL ELSE CAST(ROUND(cout_cmp_unitaire * quantite * 1000) AS INTEGER) END,
       'TND'
FROM bl_client_ligne;
DROP TABLE bl_client_ligne;
ALTER TABLE bl_client_ligne__new RENAME TO bl_client_ligne;
CREATE INDEX idx_blcl_lot ON bl_client_ligne(lot_id);
CREATE INDEX idx_blcl_commande_ligne ON bl_client_ligne(commande_ligne_id);
CREATE TRIGGER trg_blcl_no_delete BEFORE DELETE ON bl_client_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_bl_client_ligne_plafond BEFORE INSERT ON bl_client_ligne
BEGIN
    SELECT CASE WHEN (
        COALESCE((SELECT SUM(quantite) FROM affectation_stock
                  WHERE lot_id = NEW.lot_id AND commande_ligne_id = NEW.commande_ligne_id
                    AND type = NEW.type AND statut = 'ACTIVE'), 0)
        - COALESCE((SELECT SUM(quantite) FROM bl_client_ligne
                  WHERE lot_id = NEW.lot_id AND commande_ligne_id = NEW.commande_ligne_id
                    AND type = NEW.type), 0)
    ) < NEW.quantite
    THEN RAISE(ABORT, 'livraison refusée : dépasse la quantité affectée et non encore livrée')
    END;
END;

-- ═══════════════════════ 12. facture_client ═══════════════════════
-- montant_eur -> montant_minor + devise explicite (déjà 'EUR' par nature du
-- nom d'origine et du contexte douane/MACF déjà validé) : voir note en tête
-- de fichier.
CREATE TABLE facture_client__new (
    id                          TEXT PRIMARY KEY,
    numero                      TEXT NOT NULL UNIQUE,
    commande_client_id          TEXT NOT NULL REFERENCES commande_client(id),
    date                        TEXT NOT NULL,
    montant_minor                INTEGER NOT NULL CHECK (montant_minor >= 0),
    devise                       TEXT NOT NULL DEFAULT 'EUR' CHECK (devise IN ('TND','EUR','USD')),
    cours_change_declaration    REAL CHECK (cours_change_declaration IS NULL OR cours_change_declaration > 0),
    n_declaration_douane        TEXT,
    n_titre_banque               TEXT,
    banque                      TEXT,
    cree_le                     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    cree_par                    TEXT REFERENCES utilisateur(id)
);
INSERT INTO facture_client__new (id, numero, commande_client_id, date, montant_minor, devise, cours_change_declaration, n_declaration_douane, n_titre_banque, banque, cree_le, cree_par)
SELECT id, numero, commande_client_id, date, CAST(ROUND(montant_eur * 100) AS INTEGER), 'EUR', cours_change_declaration, n_declaration_douane, n_titre_banque, banque, cree_le, cree_par
FROM facture_client;
DROP TABLE facture_client;
ALTER TABLE facture_client__new RENAME TO facture_client;
CREATE INDEX idx_fac_commande ON facture_client(commande_client_id);
CREATE TRIGGER trg_fac_no_delete BEFORE DELETE ON facture_client
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

-- ═══════════════════════ 13. facture_client_ligne ═══════════════════════
CREATE TABLE facture_client_ligne__new (
    id                      TEXT PRIMARY KEY,
    facture_client_id       TEXT NOT NULL REFERENCES facture_client(id),
    bl_client_ligne_id      TEXT NOT NULL UNIQUE REFERENCES bl_client_ligne(id),
    prix_applique_minor      INTEGER NOT NULL CHECK (prix_applique_minor >= 0),
    devise                   TEXT NOT NULL DEFAULT 'EUR' CHECK (devise IN ('TND','EUR','USD'))
);
INSERT INTO facture_client_ligne__new (id, facture_client_id, bl_client_ligne_id, prix_applique_minor, devise)
SELECT id, facture_client_id, bl_client_ligne_id, CAST(ROUND(prix_applique * 100) AS INTEGER), 'EUR'
FROM facture_client_ligne;
DROP TABLE facture_client_ligne;
ALTER TABLE facture_client_ligne__new RENAME TO facture_client_ligne;
CREATE INDEX idx_facl_facture ON facture_client_ligne(facture_client_id);
CREATE TRIGGER trg_facl_no_delete BEFORE DELETE ON facture_client_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

-- ═══════════════════════ 14. regularisation_prix_fournisseur ═══════════════════════
CREATE TABLE regularisation_prix_fournisseur__new (
    id                          TEXT PRIMARY KEY,
    facture_fournisseur_ligne_id TEXT NOT NULL UNIQUE REFERENCES facture_fournisseur_ligne(id),
    lot_id                      TEXT NOT NULL REFERENCES lot(id),
    prix_provisoire_minor       INTEGER NOT NULL CHECK (prix_provisoire_minor >= 0),
    prix_definitif_minor         INTEGER NOT NULL CHECK (prix_definitif_minor >= 0),
    ecart_unitaire_minor         INTEGER NOT NULL,
    devise                       TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    date_regularisation          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    lot_deja_sorti                INTEGER NOT NULL CHECK (lot_deja_sorti IN (0,1)),
    impact_analytique             TEXT NOT NULL CHECK (impact_analytique IN ('APPLIQUE_AU_LOT','ECART_SEPARE'))
);
INSERT INTO regularisation_prix_fournisseur__new (id, facture_fournisseur_ligne_id, lot_id, prix_provisoire_minor, prix_definitif_minor, ecart_unitaire_minor, devise, date_regularisation, lot_deja_sorti, impact_analytique)
SELECT id, facture_fournisseur_ligne_id, lot_id, CAST(ROUND(prix_provisoire * 1000) AS INTEGER), CAST(ROUND(prix_definitif * 1000) AS INTEGER), CAST(ROUND(ecart_unitaire * 1000) AS INTEGER), 'TND', date_regularisation, lot_deja_sorti, impact_analytique
FROM regularisation_prix_fournisseur;
DROP TABLE regularisation_prix_fournisseur;
ALTER TABLE regularisation_prix_fournisseur__new RENAME TO regularisation_prix_fournisseur;
CREATE INDEX idx_regul_lot ON regularisation_prix_fournisseur(lot_id);
CREATE TRIGGER trg_regularisation_no_update BEFORE UPDATE ON regularisation_prix_fournisseur
BEGIN SELECT RAISE(ABORT, 'regularisation_prix_fournisseur est immuable : jamais de réécriture (§9)'); END;
CREATE TRIGGER trg_regularisation_no_delete BEFORE DELETE ON regularisation_prix_fournisseur
BEGIN SELECT RAISE(ABORT, 'regularisation_prix_fournisseur est immuable : aucune suppression autorisée'); END;

-- ═══════════════════════ 15. repartition_cout_transformation ═══════════════════════
CREATE TABLE repartition_cout_transformation__new (
    id                          TEXT PRIMARY KEY,
    transformateur_id           TEXT NOT NULL REFERENCES transformateur(id),
    periode                     TEXT NOT NULL,
    facture_fournisseur_id      TEXT REFERENCES facture_fournisseur(id),
    montant_facture_reelle_minor INTEGER NOT NULL CHECK (montant_facture_reelle_minor >= 0),
    devise                       TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    UNIQUE (transformateur_id, periode)
);
INSERT INTO repartition_cout_transformation__new (id, transformateur_id, periode, facture_fournisseur_id, montant_facture_reelle_minor, devise)
SELECT id, transformateur_id, periode, facture_fournisseur_id, CAST(ROUND(montant_facture_reelle * 1000) AS INTEGER), 'TND'
FROM repartition_cout_transformation;
DROP TABLE repartition_cout_transformation;
ALTER TABLE repartition_cout_transformation__new RENAME TO repartition_cout_transformation;

-- ═══════════════════════ 16. repartition_cout_transformation_ligne ═══════════════════════
CREATE TABLE repartition_cout_transformation_ligne__new (
    id                                  TEXT PRIMARY KEY,
    repartition_cout_transformation_id  TEXT NOT NULL REFERENCES repartition_cout_transformation(id),
    reception_transformation_ligne_id   TEXT NOT NULL REFERENCES reception_transformation_ligne(id),
    montant_reparti_minor               INTEGER NOT NULL CHECK (montant_reparti_minor >= 0),
    devise                               TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD'))
);
INSERT INTO repartition_cout_transformation_ligne__new (id, repartition_cout_transformation_id, reception_transformation_ligne_id, montant_reparti_minor, devise)
SELECT id, repartition_cout_transformation_id, reception_transformation_ligne_id, CAST(ROUND(montant_reparti * 1000) AS INTEGER), 'TND'
FROM repartition_cout_transformation_ligne;
DROP TABLE repartition_cout_transformation_ligne;
ALTER TABLE repartition_cout_transformation_ligne__new RENAME TO repartition_cout_transformation_ligne;
CREATE INDEX idx_rctl_repartition ON repartition_cout_transformation_ligne(repartition_cout_transformation_id);

-- ═══════════════════════ 17. cmp_stock_general ═══════════════════════
CREATE TABLE cmp_stock_general__new (
    article_id          TEXT NOT NULL REFERENCES article(id),
    finition             TEXT NOT NULL,
    longueur_m           REAL NOT NULL,
    quantite_totale      INTEGER NOT NULL DEFAULT 0,
    valeur_totale_minor  INTEGER NOT NULL DEFAULT 0,
    cmp_unitaire_minor    INTEGER NOT NULL DEFAULT 0,
    devise                TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    derniere_maj          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now')),
    PRIMARY KEY (article_id, finition, longueur_m)
);
INSERT INTO cmp_stock_general__new (article_id, finition, longueur_m, quantite_totale, valeur_totale_minor, cmp_unitaire_minor, devise, derniere_maj)
SELECT article_id, finition, longueur_m, quantite_totale, CAST(ROUND(valeur_totale * 1000) AS INTEGER), CAST(ROUND(cmp_unitaire * 1000) AS INTEGER), 'TND', derniere_maj
FROM cmp_stock_general;
DROP TABLE cmp_stock_general;
ALTER TABLE cmp_stock_general__new RENAME TO cmp_stock_general;

-- ═══════════════════════ 18. cmp_historique ═══════════════════════
-- + montant_mouvement_minor : montant EXACT (signé, + = entrée, - = sortie)
-- imputé par CE mouvement précis, pour que cout_sortie()/cout_chute()
-- puissent lire un total exact sans jamais recalculer quantite × un
-- cmp_unitaire arrondi (source possible de dérive, voir docs/PRIX_REVIENT.md).
CREATE TABLE cmp_historique__new (
    id                      TEXT PRIMARY KEY,
    article_id              TEXT NOT NULL REFERENCES article(id),
    finition                 TEXT NOT NULL,
    longueur_m               REAL NOT NULL,
    mouvement_stock_id       TEXT NOT NULL REFERENCES mouvement_stock(id),
    quantite_totale_apres    INTEGER NOT NULL,
    valeur_totale_apres_minor INTEGER NOT NULL,
    cmp_unitaire_apres_minor  INTEGER NOT NULL,
    montant_mouvement_minor  INTEGER NOT NULL,
    devise                    TEXT NOT NULL DEFAULT 'TND' CHECK (devise IN ('TND','EUR','USD')),
    date_heure                TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%f','now'))
);
INSERT INTO cmp_historique__new (id, article_id, finition, longueur_m, mouvement_stock_id, quantite_totale_apres, valeur_totale_apres_minor, cmp_unitaire_apres_minor, montant_mouvement_minor, devise, date_heure)
SELECT id, article_id, finition, longueur_m, mouvement_stock_id, quantite_totale_apres, CAST(ROUND(valeur_totale_apres * 1000) AS INTEGER), CAST(ROUND(cmp_unitaire_apres * 1000) AS INTEGER), 0, 'TND', date_heure
FROM cmp_historique;
DROP TABLE cmp_historique;
ALTER TABLE cmp_historique__new RENAME TO cmp_historique;
CREATE INDEX idx_cmp_hist_pool ON cmp_historique(article_id, finition, longueur_m, date_heure);

PRAGMA legacy_alter_table = OFF;
PRAGMA foreign_keys = ON;

-- ═══════════════════════ Vue de consolidation annuelle des chutes (§3) ═══════════════════════
-- Le coût d'une chute n'entre jamais dans la marge individuelle d'une
-- affaire (impact_marge_valide reste à 0, définitivement — ce n'est plus un
-- point ouvert, cf. cadrage Phase 4.1 §3). Cette vue permet de produire à
-- tout moment le bilan consolidé annuel demandé, par devise (des chutes
-- dans des devises différentes ne se somment jamais entre elles).
CREATE VIEW v_bilan_chutes_annuel AS
SELECT
    substr(date, 1, 4) AS annee,
    devise,
    COUNT(*) AS nombre_chutes,
    SUM(quantite) AS quantite_totale,
    SUM(poids_kg) AS poids_total_kg,
    SUM(cout_cmp_total_minor) AS cout_total_minor
FROM chute
WHERE cout_cmp_total_minor IS NOT NULL
GROUP BY substr(date, 1, 4), devise;
