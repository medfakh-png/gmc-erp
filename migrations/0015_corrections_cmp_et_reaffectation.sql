-- 0015_corrections_cmp_et_reaffectation.sql
-- Corrections trouvées en écrivant les 11 tests obligatoires (Phase 4 §5) —
-- ce sont des corrections techniques de cohérence interne du schéma déjà
-- livré, pas des changements de règle métier : aucune des 4 règles de
-- valorisation ni des règles A-J n'est modifiée par cette migration.

-- ───────────────────────────────────────────────────────────────────────
-- (1) cmp_historique avait été rendue immuable (migration 0012) par erreur :
-- c'est un CACHE reconstructible (cf. commentaire migration 0009 :
-- "Reconstructible intégralement... par db/valorisation.py:reconstruire_cmp()"),
-- pas un journal d'audit permanent comme journal_audit ou mouvement_stock.
-- reconstruire_cmp() a besoin de pouvoir la vider et la regénérer.
DROP TRIGGER trg_cmp_historique_no_update;
DROP TRIGGER trg_cmp_historique_no_delete;

-- ───────────────────────────────────────────────────────────────────────
-- (2) v_stock_non_affecte_par_lot double-comptait une sortie déjà livrée :
-- une affectation reste statut='ACTIVE' même après sa sortie physique réelle
-- (mouvement_physique_id renseigné) — seule une réaffectation la clôture.
-- La vue soustrayait donc deux fois la même quantité : une fois via le solde
-- physique (mouvement_stock, qui a déjà diminué le stock STOCK_GMC), une
-- fois via l'affectation encore active. Correction : ne compter, comme
-- "affecté actif", que les affectations qui n'ont PAS encore de sortie
-- physique (mouvement_physique_id IS NULL) — celles qui réservent réellement
-- une quantité encore présente en STOCK_GMC.
DROP VIEW v_stock_non_affecte_par_lot;
CREATE VIEW v_stock_non_affecte_par_lot AS
SELECT
    l.id AS lot_id, l.article_id, l.finition, l.longueur_m,
    COALESCE(s.quantite, 0) AS quantite_stock_gmc,
    COALESCE(a.quantite_affectee, 0) AS quantite_affectee_active,
    COALESCE(s.quantite, 0) - COALESCE(a.quantite_affectee, 0) AS quantite_non_affectee
FROM lot l
LEFT JOIN (SELECT lot_id, quantite FROM v_solde_lot_emplacement WHERE emplacement = 'STOCK_GMC') s ON s.lot_id = l.id
LEFT JOIN (SELECT lot_id, SUM(quantite) AS quantite_affectee FROM affectation_stock
           WHERE statut = 'ACTIVE' AND mouvement_physique_id IS NULL GROUP BY lot_id) a ON a.lot_id = l.id;

-- ───────────────────────────────────────────────────────────────────────
-- (3) et (4) trg_affectation_plafond sommait TOUTES les affectations (actives
-- ou clôturées) d'un lot. Cela empêchait mécaniquement toute réaffectation à
-- 100% d'un lot déjà entièrement affecté : impossible de créer la nouvelle
-- affectation de destination tant que l'ancienne (origine) compte encore
-- dans le plafond, alors qu'elle est en train d'être remplacée par la même
-- quantité chez le même lot. Correction : ne compter, pour le plafond,
-- QUE les affectations encore ACTIVES (une affectation CLOTUREE — donc déjà
-- réaffectée ailleurs — ne doit plus bloquer de nouvelle affectation sur ce
-- lot, sinon la capacité apparente du lot rétrécirait à chaque réaffectation).
--
-- Cela impose un nouvel ordre d'opérations pour une réaffectation (cf.
-- tests/helpers.py:reaffecter, docs/DATABASE.md) : (a) clôturer l'origine
-- (UPDATE statut='CLOTUREE'), (b) créer l'affectation de destination
-- (passe désormais le plafond, l'origine ne comptant plus), (c) insérer la
-- ligne reaffectation qui relie les deux (le AFTER INSERT qui re-clôture
-- l'origine devient une simple confirmation idempotente).
--
-- En contrepartie, trg_reaffectation_origine_active ne peut plus s'appuyer
-- sur "l'origine doit être encore ACTIVE" (elle est déjà clôturée à l'étape
-- (a), volontairement). La protection contre une réaffectation silencieuse
-- ou incohérente est assurée autrement, et de façon plus précise qu'avant :
--   - on ne peut jamais réaffecter une affectation déjà physiquement
--     consommée (mouvement_physique_id IS NOT NULL) — la marchandise est
--     déjà partie, il n'y a plus rien à réaffecter ;
--   - on ne peut jamais réaffecter deux fois la même affectation d'origine
--     (une ligne dans reaffectation existe déjà pour elle) — sinon la même
--     quantité se retrouverait comptée sur plusieurs destinations à la fois.
DROP TRIGGER trg_affectation_plafond;
CREATE TRIGGER trg_affectation_plafond BEFORE INSERT ON affectation_stock
BEGIN
    SELECT CASE WHEN (
        COALESCE((SELECT SUM(quantite) FROM affectation_stock WHERE lot_id = NEW.lot_id AND statut = 'ACTIVE'), 0)
        + NEW.quantite
    ) > (SELECT quantite_initiale FROM lot WHERE id = NEW.lot_id)
    THEN RAISE(ABORT, 'affectation refusée : dépasse la quantité disponible du lot')
    END;
END;

DROP TRIGGER trg_reaffectation_origine_active;
CREATE TRIGGER trg_reaffectation_origine_active BEFORE INSERT ON reaffectation
BEGIN
    SELECT CASE WHEN (SELECT mouvement_physique_id FROM affectation_stock WHERE id = NEW.affectation_origine_id) IS NOT NULL
    THEN RAISE(ABORT, 'réaffectation refusée : cette affectation a déjà été physiquement livrée/consommée')
    END;
    SELECT CASE WHEN EXISTS (SELECT 1 FROM reaffectation WHERE affectation_origine_id = NEW.affectation_origine_id)
    THEN RAISE(ABORT, 'réaffectation refusée : cette affectation a déjà été réaffectée')
    END;
    SELECT CASE WHEN NEW.quantite_reaffectee > (SELECT quantite FROM affectation_stock WHERE id = NEW.affectation_origine_id)
    THEN RAISE(ABORT, 'réaffectation refusée : quantité supérieure à l''affectation d''origine')
    END;
END;
-- trg_reaffectation_cloture_origine (0013) est inchangé : il reste une
-- confirmation idempotente (l'origine est déjà CLOTUREE à ce stade).
