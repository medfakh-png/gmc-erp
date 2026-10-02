-- 0014_vues.sql
-- Vues calculées — jamais de table stockée pour une donnée dérivable (§3.1 Phase 2).

-- Solde d'un lot par emplacement, dérivé exclusivement du registre de mouvements.
-- C'est la brique de base utilisée pour vérifier la disponibilité avant tout
-- nouveau mouvement (voir aussi le trigger trg_mouvement_solde_source, 0013).
CREATE VIEW v_solde_lot_emplacement AS
SELECT lot_id, emplacement, SUM(delta_qte) AS quantite, SUM(delta_poids) AS poids_kg
FROM (
    SELECT lot_id, emplacement_destination AS emplacement, quantite AS delta_qte, poids_kg AS delta_poids
    FROM mouvement_stock WHERE emplacement_destination IS NOT NULL
    UNION ALL
    SELECT lot_id, emplacement_source AS emplacement, -quantite AS delta_qte, -poids_kg AS delta_poids
    FROM mouvement_stock WHERE emplacement_source IS NOT NULL
) t
GROUP BY lot_id, emplacement;

-- "Approvisionnements" (point 3 de la liste Phase 3, §B.4 : vue plutôt que table,
-- pour ne rien dupliquer). Par ligne de commande client.
CREATE VIEW v_approvisionnement_ligne AS
SELECT
    cl.id AS commande_ligne_id,
    cl.quantite_originale AS commande,
    COALESCE(bcf.qte_commandee, 0) AS commande_fournisseur,
    COALESCE(blf.qte_receptionnee, 0) AS receptionne,
    cl.quantite_originale - COALESCE(blf.qte_receptionnee, 0) AS reste_a_approvisionner
FROM commande_ligne cl
LEFT JOIN (SELECT commande_ligne_id, SUM(quantite_commandee) AS qte_commandee
           FROM bon_commande_fournisseur_ligne WHERE commande_ligne_id IS NOT NULL
           GROUP BY commande_ligne_id) bcf ON bcf.commande_ligne_id = cl.id
LEFT JOIN (SELECT commande_ligne_id, SUM(quantite) AS qte_receptionnee
           FROM bl_fournisseur_ligne WHERE commande_ligne_id IS NOT NULL
           GROUP BY commande_ligne_id) blf ON blf.commande_ligne_id = cl.id;

-- Stock non affecté par pool (article, finition, longueur) — le pool sur lequel
-- s'applique le CMP (§1 Phase 4). = solde en STOCK_GMC des lots dont la somme des
-- affectations est inférieure à leur quantité initiale, au prorata du reliquat non affecté.
CREATE VIEW v_stock_non_affecte_par_lot AS
SELECT
    l.id AS lot_id, l.article_id, l.finition, l.longueur_m,
    COALESCE(s.quantite, 0) AS quantite_stock_gmc,
    COALESCE(a.quantite_affectee, 0) AS quantite_affectee_active,
    COALESCE(s.quantite, 0) - COALESCE(a.quantite_affectee, 0) AS quantite_non_affectee
FROM lot l
LEFT JOIN (SELECT lot_id, quantite FROM v_solde_lot_emplacement WHERE emplacement = 'STOCK_GMC') s ON s.lot_id = l.id
LEFT JOIN (SELECT lot_id, SUM(quantite) AS quantite_affectee FROM affectation_stock WHERE statut = 'ACTIVE' GROUP BY lot_id) a ON a.lot_id = l.id;
-- Note : cette vue sert à l'inspection manuelle et au moteur de valorisation ;
-- le calcul du CMP proprement dit (db/valorisation.py) rejoue l'historique
-- complet mouvement par mouvement pour rester exact à tout instant (voir DATABASE.md).
