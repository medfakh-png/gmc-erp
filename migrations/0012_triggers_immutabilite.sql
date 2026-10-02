-- 0012_triggers_immutabilite.sql
-- "Aucune suppression" (convention Phase 3) + "écrasement d'un document historique"
-- interdit (règle Phase 4 étape 7). Deux niveaux :
--   (1) immuabilité totale (ni UPDATE ni DELETE) pour les tables append-only ;
--   (2) DELETE interdit pour tous les documents/entités métier (une suppression
--       doit devenir une annulation/archivage tracée dans journal_audit, jamais
--       un DELETE réel).

-- ===== (1) Immuabilité totale =====

CREATE TRIGGER trg_mouvement_stock_no_update BEFORE UPDATE ON mouvement_stock
BEGIN SELECT RAISE(ABORT, 'mouvement_stock est immuable (append-only) : aucune modification autorisée'); END;
CREATE TRIGGER trg_mouvement_stock_no_delete BEFORE DELETE ON mouvement_stock
BEGIN SELECT RAISE(ABORT, 'mouvement_stock est immuable (append-only) : aucune suppression autorisée'); END;

CREATE TRIGGER trg_taux_change_no_update BEFORE UPDATE ON taux_change
BEGIN SELECT RAISE(ABORT, 'taux_change est immuable : un taux figé ne se modifie jamais'); END;
CREATE TRIGGER trg_taux_change_no_delete BEFORE DELETE ON taux_change
BEGIN SELECT RAISE(ABORT, 'taux_change est immuable : aucune suppression autorisée'); END;

CREATE TRIGGER trg_regularisation_no_update BEFORE UPDATE ON regularisation_prix_fournisseur
BEGIN SELECT RAISE(ABORT, 'regularisation_prix_fournisseur est immuable : jamais de réécriture (§9)'); END;
CREATE TRIGGER trg_regularisation_no_delete BEFORE DELETE ON regularisation_prix_fournisseur
BEGIN SELECT RAISE(ABORT, 'regularisation_prix_fournisseur est immuable : aucune suppression autorisée'); END;

CREATE TRIGGER trg_journal_audit_no_update BEFORE UPDATE ON journal_audit
BEGIN SELECT RAISE(ABORT, 'journal_audit est immuable'); END;
CREATE TRIGGER trg_journal_audit_no_delete BEFORE DELETE ON journal_audit
BEGIN SELECT RAISE(ABORT, 'journal_audit est immuable'); END;

CREATE TRIGGER trg_cmp_historique_no_update BEFORE UPDATE ON cmp_historique
BEGIN SELECT RAISE(ABORT, 'cmp_historique est immuable'); END;
CREATE TRIGGER trg_cmp_historique_no_delete BEFORE DELETE ON cmp_historique
BEGIN SELECT RAISE(ABORT, 'cmp_historique est immuable'); END;

-- ===== (2) DELETE interdit sur tous les documents / lots / stock logique =====
-- (UPDATE reste possible : statut, prix renégocié, champs remplis progressivement, etc.
--  Le contrôle fin colonne-par-colonne reste une responsabilité applicative, Phase 5 —
--  voir docs/DATABASE.md pour la liste exacte des colonnes qui ne devraient jamais changer.)

CREATE TRIGGER trg_devis_no_delete BEFORE DELETE ON devis
BEGIN SELECT RAISE(ABORT, 'suppression interdite : annulez le devis (statut=ANNULE) au lieu de le supprimer'); END;
CREATE TRIGGER trg_devis_ligne_no_delete BEFORE DELETE ON devis_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

CREATE TRIGGER trg_commande_client_no_delete BEFORE DELETE ON commande_client
BEGIN SELECT RAISE(ABORT, 'suppression interdite : annulez la commande (statut=ANNULEE) au lieu de la supprimer'); END;
CREATE TRIGGER trg_commande_ligne_no_delete BEFORE DELETE ON commande_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
-- La quantité originale d'une ligne de commande n'est jamais modifiée après confirmation (§27.1) :
CREATE TRIGGER trg_commande_ligne_qte_immuable BEFORE UPDATE OF quantite_originale ON commande_ligne
WHEN OLD.quantite_originale != NEW.quantite_originale
BEGIN SELECT RAISE(ABORT, 'commande_ligne.quantite_originale est immuable après création (§27.1) : un écart se gère par supplément ou réaffectation, jamais par modification de la quantité initiale'); END;

CREATE TRIGGER trg_bcf_no_delete BEFORE DELETE ON bon_commande_fournisseur
BEGIN SELECT RAISE(ABORT, 'suppression interdite : annulez (statut=ANNULE)'); END;
CREATE TRIGGER trg_bcfl_no_delete BEFORE DELETE ON bon_commande_fournisseur_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

CREATE TRIGGER trg_blf_no_delete BEFORE DELETE ON bl_fournisseur
BEGIN SELECT RAISE(ABORT, 'suppression interdite : un BL validé ne se supprime jamais'); END;
CREATE TRIGGER trg_blfl_no_delete BEFORE DELETE ON bl_fournisseur_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

CREATE TRIGGER trg_ffo_no_delete BEFORE DELETE ON facture_fournisseur
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_ffl_no_delete BEFORE DELETE ON facture_fournisseur_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

CREATE TRIGGER trg_lot_no_delete BEFORE DELETE ON lot
BEGIN SELECT RAISE(ABORT, 'suppression interdite : un lot ne se supprime jamais, même épuisé'); END;
CREATE TRIGGER trg_lot_no_update_quantite BEFORE UPDATE OF quantite_initiale, poids_initial_kg ON lot
BEGIN SELECT RAISE(ABORT, 'lot.quantite_initiale et poids_initial_kg sont figés à la création'); END;

CREATE TRIGGER trg_affectation_no_delete BEFORE DELETE ON affectation_stock
BEGIN SELECT RAISE(ABORT, 'suppression interdite : clôturez (statut=CLOTUREE) ou réaffectez au lieu de supprimer'); END;
CREATE TRIGGER trg_reaffectation_no_delete BEFORE DELETE ON reaffectation
BEGIN SELECT RAISE(ABORT, 'suppression interdite : une réaffectation, une fois tracée, reste tracée'); END;

CREATE TRIGGER trg_chute_no_delete BEFORE DELETE ON chute
BEGIN SELECT RAISE(ABORT, 'suppression interdite : une chute reste dans le système même si son traitement comptable évolue'); END;

CREATE TRIGGER trg_bct_no_delete BEFORE DELETE ON bon_commande_transformation
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_bctl_no_delete BEFORE DELETE ON bon_commande_transformation_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_bst_no_delete BEFORE DELETE ON bon_sortie_transformation
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_bstl_no_delete BEFORE DELETE ON bon_sortie_transformation_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_rt_no_delete BEFORE DELETE ON reception_transformation
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_rtl_no_delete BEFORE DELETE ON reception_transformation_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

CREATE TRIGGER trg_blc_no_delete BEFORE DELETE ON bl_client
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_blcl_no_delete BEFORE DELETE ON bl_client_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_fac_no_delete BEFORE DELETE ON facture_client
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
CREATE TRIGGER trg_facl_no_delete BEFORE DELETE ON facture_client_ligne
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;

CREATE TRIGGER trg_macf_no_delete BEFORE DELETE ON macf_ligne_achat
BEGIN SELECT RAISE(ABORT, 'suppression interdite'); END;
