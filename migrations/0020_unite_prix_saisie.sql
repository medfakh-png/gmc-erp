-- 0020_unite_prix_saisie.sql — Phase 5.5, dernière correction (décision
-- validée : « Proposition A — conservation de l'unité d'origine du prix »).
--
-- Règle validée : le prix unitaire est conservé dans l'unité dans laquelle il
-- a été réellement saisi, lorsque la conversion vers l'unité de valorisation
-- de l'article est une conversion physique exacte kg <-> tonne. Le prix saisi
-- n'est jamais arrondi ; le prix original et son unité d'origine sont
-- conservés ; la conversion vers l'unité de valorisation se fait uniquement
-- au moment du calcul, sans arrondi intermédiaire ; seul le montant final est
-- arrondi au millime. La représentation monétaire globale (Phase 4.1) n'est
-- PAS modifiée (Proposition B non retenue).
--
-- Exemple validé : article valorisé en DT/kg ; lot = 2 500 500 millimes par
-- TONNE (2 500,5 DT/t, exact) ; calcul : 2 500,5 / 1000 = 2,5005 DT/kg, jamais
-- 2,501 DT/kg avant le montant final.
--
-- Pourquoi une migration est nécessaire (analyse) :
--   - le trigger de 0019 imposait « unité du prix du lot = unité de
--     l'article » : il interdisait exactement le cas validé ;
--   - le lot n'avait qu'UNE colonne d'unité pour DEUX prix (BL provisoire,
--     facture définitive) : une facture saisie dans une autre unité (kg/t)
--     que le BL aurait perdu son unité d'origine ;
--   - la régularisation fournisseur ne portait aucune unité ;
--   - SQLite accepte un nombre à virgule (REAL) dans une colonne INTEGER : le
--     garde-fou « montant monétaire entier » (Phase 4.1) n'existait qu'au
--     niveau du programme (vérifié : 2500.5 était accepté en base).
--
-- Changements :
--   0. vérification préalable : la migration échoue si un montant non entier
--      existe déjà (aucune donnée corrigée en silence) ;
--   1. lot : l'unité du prix (provisoire) peut être l'unité de l'article OU,
--      pour un article valorisé au poids, l'autre unité de masse (KG <->
--      TONNE) ; + unite_prix_definitif (unité propre du prix définitif) ;
--      + unite_valorisation_article (unité de l'article à la création du lot,
--      fixée par la base puis figée) ;
--   2. inventaire_initial_ligne.unite_cout = unité du coût SAISI (même
--      compatibilité) ;
--   3. regularisation_prix_fournisseur : unité de chaque prix + unité de
--      l'écart ; écart contrôlé par conversion exacte ;
--   5. garde-fou « montant monétaire entier » sur TOUTES les colonnes *_minor
--      (28 colonnes, 19 tables) : un REAL est refusé à l'insertion et à la
--      mise à jour.
--
-- Données existantes : la base réelle ne contient aucune donnée métier.
-- Reprise des FAITS : prix définitif et écart dans l'unité du lot (une seule
-- unité existait) ; unité de l'article à la création = unité du prix pour les
-- lots créés après la définition de l'unité de l'article (0019 les imposait
-- égales), inconnue (NULL) sinon.

PRAGMA foreign_keys = OFF;

-- ═══════════════════════ 0. Vérification préalable : aucun montant non entier existant ═══════════════════════
CREATE TEMP TABLE verification_0020_montants_entiers (anomalies INTEGER NOT NULL CHECK (anomalies = 0));
INSERT INTO verification_0020_montants_entiers (anomalies) SELECT
    (SELECT COUNT(*) FROM bl_client WHERE typeof(prix_transport_reel_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM bl_client_ligne WHERE typeof(cout_cmp_total_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM bl_fournisseur_ligne WHERE typeof(prix_unitaire_provisoire_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM bon_commande_fournisseur_ligne WHERE typeof(prix_negocie_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM chute WHERE typeof(cout_cmp_total_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM cmp_historique WHERE typeof(valeur_totale_apres_minor) NOT IN ('integer','null') OR typeof(cmp_unitaire_apres_minor) NOT IN ('integer','null') OR typeof(montant_mouvement_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM cmp_stock_general WHERE typeof(valeur_totale_minor) NOT IN ('integer','null') OR typeof(cmp_unitaire_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM commande_ligne WHERE typeof(prix_negocie_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM devis_ligne WHERE typeof(prix_achat_estimatif_minor) NOT IN ('integer','null') OR typeof(prix_transport_estimatif_minor) NOT IN ('integer','null') OR typeof(prix_vente_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM facture_client WHERE typeof(montant_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM facture_client_ligne WHERE typeof(prix_applique_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM facture_fournisseur WHERE typeof(montant_total_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM facture_fournisseur_ligne WHERE typeof(prix_unitaire_definitif_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM inventaire_initial_ligne WHERE typeof(cout_unitaire_minor) NOT IN ('integer','null') OR typeof(valeur_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM lot WHERE typeof(prix_unitaire_provisoire_minor) NOT IN ('integer','null') OR typeof(prix_unitaire_definitif_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM prix_transformation WHERE typeof(prix_kg_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM regularisation_prix_fournisseur WHERE typeof(prix_provisoire_minor) NOT IN ('integer','null') OR typeof(prix_definitif_minor) NOT IN ('integer','null') OR typeof(ecart_unitaire_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM repartition_cout_transformation WHERE typeof(montant_facture_reelle_minor) NOT IN ('integer','null'))
  + (SELECT COUNT(*) FROM repartition_cout_transformation_ligne WHERE typeof(montant_reparti_minor) NOT IN ('integer','null'));
DROP TABLE verification_0020_montants_entiers;

-- ═══════════════════════ 1. lot : unité du prix saisi, prix définitif, unité de l'article ═══════════════════════
ALTER TABLE lot ADD COLUMN unite_prix_definitif TEXT
    CHECK (unite_prix_definitif IS NULL OR unite_prix_definitif IN ('KG','ML','UNITE','TONNE'));
ALTER TABLE lot ADD COLUMN unite_valorisation_article TEXT
    CHECK (unite_valorisation_article IS NULL
           OR unite_valorisation_article IN ('KG','ML','UNITE','TONNE'));
-- FAIT : jusqu'ici le prix définitif était dans la même unité que le provisoire.
UPDATE lot SET unite_prix_definitif = unite_prix WHERE prix_unitaire_definitif_minor IS NOT NULL;
-- FAIT : depuis 0019, l'unité du prix était imposée égale à l'unité de l'article.
UPDATE lot SET unite_valorisation_article = unite_prix
WHERE EXISTS (SELECT 1 FROM article_unite_valorisation a
              WHERE a.article_id = lot.article_id AND a.nature = 'DEFINITION_INITIALE'
                AND a.date_effet <= lot.cree_le);

DROP TRIGGER trg_lot_unite_prix_controle;
CREATE TRIGGER trg_lot_unite_prix_controle BEFORE INSERT ON lot
BEGIN
    SELECT RAISE(ABORT, 'lot refusé : aucune unité de valorisation définie pour cet article')
    WHERE NOT EXISTS (SELECT 1 FROM article_unite_valorisation WHERE article_id = NEW.article_id);
    SELECT RAISE(ABORT, 'lot refusé : l''unité du prix du lot doit être l''unité de valorisation de l''article ou, pour un article valorisé au poids, l''autre unité de masse (kg <-> tonne)')
    WHERE NEW.unite_prix IS NOT NULL AND NOT (NEW.unite_prix = (SELECT unite FROM article_unite_valorisation WHERE article_id = NEW.article_id ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC LIMIT 1) OR (NEW.unite_prix IN ('KG','TONNE') AND (SELECT unite FROM article_unite_valorisation WHERE article_id = NEW.article_id ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC LIMIT 1) IN ('KG','TONNE')));
    SELECT RAISE(ABORT, 'lot refusé : l''unité du prix du lot doit être l''unité de valorisation de l''article ou, pour un article valorisé au poids, l''autre unité de masse (kg <-> tonne)')
    WHERE NEW.unite_prix_definitif IS NOT NULL AND NOT (NEW.unite_prix_definitif = (SELECT unite FROM article_unite_valorisation WHERE article_id = NEW.article_id ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC LIMIT 1) OR (NEW.unite_prix_definitif IN ('KG','TONNE') AND (SELECT unite FROM article_unite_valorisation WHERE article_id = NEW.article_id ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC LIMIT 1) IN ('KG','TONNE')));
    SELECT RAISE(ABORT, 'lot refusé : un prix définitif doit porter son unité (unite_prix_definitif), et une unité de prix définitif exige un prix définitif')
    WHERE (NEW.prix_unitaire_definitif_minor IS NULL) <> (NEW.unite_prix_definitif IS NULL);
    SELECT RAISE(ABORT, 'lot refusé : unite_valorisation_article est fixée par la base (unité en vigueur de l''article)')
    WHERE NEW.unite_valorisation_article IS NOT NULL AND NEW.unite_valorisation_article <> (SELECT unite FROM article_unite_valorisation WHERE article_id = NEW.article_id ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC LIMIT 1);
END;
CREATE TRIGGER trg_lot_unite_valorisation_article_auto AFTER INSERT ON lot
WHEN NEW.unite_valorisation_article IS NULL
BEGIN
    UPDATE lot SET unite_valorisation_article = (SELECT unite FROM article_unite_valorisation WHERE article_id = NEW.article_id ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC LIMIT 1) WHERE id = NEW.id;
END;
CREATE TRIGGER trg_lot_unite_valorisation_article_figee BEFORE UPDATE OF unite_valorisation_article ON lot
WHEN OLD.unite_valorisation_article IS NOT NULL
BEGIN SELECT RAISE(ABORT, 'lot.unite_valorisation_article est figée à la création du lot'); END;
CREATE TRIGGER trg_lot_prix_definitif_unite BEFORE UPDATE OF prix_unitaire_definitif_minor, unite_prix_definitif ON lot
BEGIN
    SELECT RAISE(ABORT, 'lot refusé : un prix définitif doit porter son unité (unite_prix_definitif), et une unité de prix définitif exige un prix définitif')
    WHERE (NEW.prix_unitaire_definitif_minor IS NULL) <> (NEW.unite_prix_definitif IS NULL);
    SELECT RAISE(ABORT, 'lot refusé : le prix définitif doit être dans l''unité du prix du lot ou dans l''autre unité de masse (kg <-> tonne)')
    WHERE NEW.unite_prix_definitif IS NOT NULL AND NOT (NEW.unite_prix_definitif = NEW.unite_prix OR (NEW.unite_prix_definitif IN ('KG','TONNE') AND NEW.unite_prix IN ('KG','TONNE')));
END;

-- ═══════════════════════ 2. inventaire_initial_ligne : unité du coût saisi ═══════════════════════
CREATE TRIGGER trg_inventaire_initial_ligne_unite_cout BEFORE INSERT ON inventaire_initial_ligne
BEGIN
    SELECT RAISE(ABORT, 'lot refusé : aucune unité de valorisation définie pour cet article')
    WHERE NOT EXISTS (SELECT 1 FROM article_unite_valorisation WHERE article_id = NEW.article_id);
    SELECT RAISE(ABORT, 'ligne refusée : l''unité du coût doit être l''unité de valorisation de l''article ou, pour un article valorisé au poids, l''autre unité de masse (kg <-> tonne)')
    WHERE NOT (NEW.unite_cout = (SELECT unite FROM article_unite_valorisation WHERE article_id = NEW.article_id ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC LIMIT 1) OR (NEW.unite_cout IN ('KG','TONNE') AND (SELECT unite FROM article_unite_valorisation WHERE article_id = NEW.article_id ORDER BY CASE nature WHEN 'CHANGEMENT' THEN 1 ELSE 0 END DESC, date_effet DESC, rowid DESC LIMIT 1) IN ('KG','TONNE')));
END;

-- ═══════════════════════ 3. regularisation_prix_fournisseur : unité de chaque prix ═══════════════════════
ALTER TABLE regularisation_prix_fournisseur ADD COLUMN unite_prix_provisoire TEXT
    CHECK (unite_prix_provisoire IS NULL OR unite_prix_provisoire IN ('KG','ML','UNITE','TONNE'));
ALTER TABLE regularisation_prix_fournisseur ADD COLUMN unite_prix_definitif TEXT
    CHECK (unite_prix_definitif IS NULL OR unite_prix_definitif IN ('KG','ML','UNITE','TONNE'));
ALTER TABLE regularisation_prix_fournisseur ADD COLUMN unite_ecart TEXT
    CHECK (unite_ecart IS NULL OR unite_ecart IN ('KG','ML','UNITE','TONNE'));
-- Table immuable : reprise des FAITS existants (prix et écart dans l'unité du lot),
-- trigger d'immuabilité suspendu le temps de cette reprise puis recréé à l'identique.
DROP TRIGGER trg_regularisation_no_update;
UPDATE regularisation_prix_fournisseur
SET unite_prix_provisoire = (SELECT unite_prix FROM lot WHERE lot.id = regularisation_prix_fournisseur.lot_id),
    unite_prix_definitif  = (SELECT unite_prix FROM lot WHERE lot.id = regularisation_prix_fournisseur.lot_id),
    unite_ecart           = (SELECT unite_prix FROM lot WHERE lot.id = regularisation_prix_fournisseur.lot_id);
CREATE TRIGGER trg_regularisation_no_update BEFORE UPDATE ON regularisation_prix_fournisseur
BEGIN SELECT RAISE(ABORT, 'regularisation_prix_fournisseur est immuable : jamais de réécriture (§9)'); END;

CREATE TRIGGER trg_regularisation_unites BEFORE INSERT ON regularisation_prix_fournisseur
BEGIN
    SELECT RAISE(ABORT, 'régularisation refusée : chaque prix et l''écart doivent porter leur unité')
    WHERE NEW.unite_prix_provisoire IS NULL OR NEW.unite_prix_definitif IS NULL OR NEW.unite_ecart IS NULL;
    SELECT RAISE(ABORT, 'régularisation refusée : le prix provisoire est celui du lot, dans l''unité du prix du lot')
    WHERE NEW.unite_prix_provisoire <> (SELECT unite_prix FROM lot WHERE id = NEW.lot_id);
    SELECT RAISE(ABORT, 'régularisation refusée : unités de prix incompatibles (seule la conversion kg <-> tonne est exacte)')
    WHERE NOT (NEW.unite_prix_definitif = NEW.unite_prix_provisoire OR (NEW.unite_prix_definitif IN ('KG','TONNE') AND NEW.unite_prix_provisoire IN ('KG','TONNE')));
    SELECT RAISE(ABORT, 'régularisation refusée : l''écart s''exprime dans l''unité commune des deux prix (la tonne si l''un est au kg et l''autre à la tonne)')
    WHERE NEW.unite_ecart <> CASE WHEN NEW.unite_prix_definitif = NEW.unite_prix_provisoire
                                  THEN NEW.unite_prix_definitif ELSE 'TONNE' END;
    SELECT RAISE(ABORT, 'régularisation refusée : écart unitaire incohérent avec les deux prix (conversion exacte)')
    WHERE NEW.ecart_unitaire_minor <>
          (CASE WHEN NEW.unite_ecart = 'TONNE' AND NEW.unite_prix_definitif = 'KG'
                THEN NEW.prix_definitif_minor * 1000 ELSE NEW.prix_definitif_minor END)
        - (CASE WHEN NEW.unite_ecart = 'TONNE' AND NEW.unite_prix_provisoire = 'KG'
                THEN NEW.prix_provisoire_minor * 1000 ELSE NEW.prix_provisoire_minor END);
END;

-- ═══════════════════════ 5. Garde-fou « montant monétaire entier » (toutes les colonnes *_minor) ═══════════════════════
CREATE TRIGGER trg_bl_client_minor_entier_insert BEFORE INSERT ON bl_client
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (bl_client.prix_transport_reel_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_transport_reel_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_bl_client_minor_entier_update BEFORE UPDATE OF prix_transport_reel_minor ON bl_client
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (bl_client.prix_transport_reel_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_transport_reel_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_bl_client_ligne_minor_entier_insert BEFORE INSERT ON bl_client_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (bl_client_ligne.cout_cmp_total_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cout_cmp_total_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_bl_client_ligne_minor_entier_update BEFORE UPDATE OF cout_cmp_total_minor ON bl_client_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (bl_client_ligne.cout_cmp_total_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cout_cmp_total_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_bl_fournisseur_ligne_minor_entier_insert BEFORE INSERT ON bl_fournisseur_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (bl_fournisseur_ligne.prix_unitaire_provisoire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_unitaire_provisoire_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_bl_fournisseur_ligne_minor_entier_update BEFORE UPDATE OF prix_unitaire_provisoire_minor ON bl_fournisseur_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (bl_fournisseur_ligne.prix_unitaire_provisoire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_unitaire_provisoire_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_bon_commande_fournisseur_ligne_minor_entier_insert BEFORE INSERT ON bon_commande_fournisseur_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (bon_commande_fournisseur_ligne.prix_negocie_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_negocie_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_bon_commande_fournisseur_ligne_minor_entier_update BEFORE UPDATE OF prix_negocie_minor ON bon_commande_fournisseur_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (bon_commande_fournisseur_ligne.prix_negocie_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_negocie_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_chute_minor_entier_insert BEFORE INSERT ON chute
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (chute.cout_cmp_total_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cout_cmp_total_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_chute_minor_entier_update BEFORE UPDATE OF cout_cmp_total_minor ON chute
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (chute.cout_cmp_total_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cout_cmp_total_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_cmp_historique_minor_entier_insert BEFORE INSERT ON cmp_historique
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_historique.valeur_totale_apres_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.valeur_totale_apres_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_historique.cmp_unitaire_apres_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cmp_unitaire_apres_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_historique.montant_mouvement_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_mouvement_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_cmp_historique_minor_entier_update BEFORE UPDATE OF valeur_totale_apres_minor, cmp_unitaire_apres_minor, montant_mouvement_minor ON cmp_historique
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_historique.valeur_totale_apres_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.valeur_totale_apres_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_historique.cmp_unitaire_apres_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cmp_unitaire_apres_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_historique.montant_mouvement_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_mouvement_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_cmp_stock_general_minor_entier_insert BEFORE INSERT ON cmp_stock_general
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_stock_general.valeur_totale_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.valeur_totale_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_stock_general.cmp_unitaire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cmp_unitaire_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_cmp_stock_general_minor_entier_update BEFORE UPDATE OF valeur_totale_minor, cmp_unitaire_minor ON cmp_stock_general
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_stock_general.valeur_totale_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.valeur_totale_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (cmp_stock_general.cmp_unitaire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cmp_unitaire_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_commande_ligne_minor_entier_insert BEFORE INSERT ON commande_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (commande_ligne.prix_negocie_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_negocie_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_commande_ligne_minor_entier_update BEFORE UPDATE OF prix_negocie_minor ON commande_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (commande_ligne.prix_negocie_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_negocie_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_devis_ligne_minor_entier_insert BEFORE INSERT ON devis_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (devis_ligne.prix_achat_estimatif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_achat_estimatif_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (devis_ligne.prix_transport_estimatif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_transport_estimatif_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (devis_ligne.prix_vente_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_vente_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_devis_ligne_minor_entier_update BEFORE UPDATE OF prix_achat_estimatif_minor, prix_transport_estimatif_minor, prix_vente_minor ON devis_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (devis_ligne.prix_achat_estimatif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_achat_estimatif_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (devis_ligne.prix_transport_estimatif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_transport_estimatif_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (devis_ligne.prix_vente_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_vente_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_facture_client_minor_entier_insert BEFORE INSERT ON facture_client
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (facture_client.montant_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_facture_client_minor_entier_update BEFORE UPDATE OF montant_minor ON facture_client
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (facture_client.montant_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_facture_client_ligne_minor_entier_insert BEFORE INSERT ON facture_client_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (facture_client_ligne.prix_applique_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_applique_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_facture_client_ligne_minor_entier_update BEFORE UPDATE OF prix_applique_minor ON facture_client_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (facture_client_ligne.prix_applique_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_applique_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_facture_fournisseur_minor_entier_insert BEFORE INSERT ON facture_fournisseur
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (facture_fournisseur.montant_total_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_total_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_facture_fournisseur_minor_entier_update BEFORE UPDATE OF montant_total_minor ON facture_fournisseur
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (facture_fournisseur.montant_total_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_total_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_facture_fournisseur_ligne_minor_entier_insert BEFORE INSERT ON facture_fournisseur_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (facture_fournisseur_ligne.prix_unitaire_definitif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_unitaire_definitif_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_facture_fournisseur_ligne_minor_entier_update BEFORE UPDATE OF prix_unitaire_definitif_minor ON facture_fournisseur_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (facture_fournisseur_ligne.prix_unitaire_definitif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_unitaire_definitif_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_inventaire_initial_ligne_minor_entier_insert BEFORE INSERT ON inventaire_initial_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (inventaire_initial_ligne.cout_unitaire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cout_unitaire_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (inventaire_initial_ligne.valeur_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.valeur_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_inventaire_initial_ligne_minor_entier_update BEFORE UPDATE OF cout_unitaire_minor, valeur_minor ON inventaire_initial_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (inventaire_initial_ligne.cout_unitaire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.cout_unitaire_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (inventaire_initial_ligne.valeur_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.valeur_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_lot_minor_entier_insert BEFORE INSERT ON lot
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (lot.prix_unitaire_provisoire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_unitaire_provisoire_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (lot.prix_unitaire_definitif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_unitaire_definitif_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_lot_minor_entier_update BEFORE UPDATE OF prix_unitaire_provisoire_minor, prix_unitaire_definitif_minor ON lot
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (lot.prix_unitaire_provisoire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_unitaire_provisoire_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (lot.prix_unitaire_definitif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_unitaire_definitif_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_prix_transformation_minor_entier_insert BEFORE INSERT ON prix_transformation
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (prix_transformation.prix_kg_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_kg_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_prix_transformation_minor_entier_update BEFORE UPDATE OF prix_kg_minor ON prix_transformation
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (prix_transformation.prix_kg_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_kg_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_regularisation_prix_fournisseur_minor_entier_insert BEFORE INSERT ON regularisation_prix_fournisseur
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (regularisation_prix_fournisseur.prix_provisoire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_provisoire_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (regularisation_prix_fournisseur.prix_definitif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_definitif_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (regularisation_prix_fournisseur.ecart_unitaire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.ecart_unitaire_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_regularisation_prix_fournisseur_minor_entier_update BEFORE UPDATE OF prix_provisoire_minor, prix_definitif_minor, ecart_unitaire_minor ON regularisation_prix_fournisseur
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (regularisation_prix_fournisseur.prix_provisoire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_provisoire_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (regularisation_prix_fournisseur.prix_definitif_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.prix_definitif_minor) NOT IN ('integer','null');
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (regularisation_prix_fournisseur.ecart_unitaire_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.ecart_unitaire_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_repartition_cout_transformation_minor_entier_insert BEFORE INSERT ON repartition_cout_transformation
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (repartition_cout_transformation.montant_facture_reelle_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_facture_reelle_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_repartition_cout_transformation_minor_entier_update BEFORE UPDATE OF montant_facture_reelle_minor ON repartition_cout_transformation
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (repartition_cout_transformation.montant_facture_reelle_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_facture_reelle_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_repartition_cout_transformation_ligne_minor_entier_insert BEFORE INSERT ON repartition_cout_transformation_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (repartition_cout_transformation_ligne.montant_reparti_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_reparti_minor) NOT IN ('integer','null');
END;
CREATE TRIGGER trg_repartition_cout_transformation_ligne_minor_entier_update BEFORE UPDATE OF montant_reparti_minor ON repartition_cout_transformation_ligne
BEGIN
    SELECT RAISE(ABORT, 'montant monétaire non entier refusé (repartition_cout_transformation_ligne.montant_reparti_minor) : entier en unités monétaires minimales obligatoire')
    WHERE typeof(NEW.montant_reparti_minor) NOT IN ('integer','null');
END;

PRAGMA foreign_keys = ON;
