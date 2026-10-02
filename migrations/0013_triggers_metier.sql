-- 0013_triggers_metier.sql
-- Contraintes d'intégrité métier (Phase 4 étape 7) qui ne peuvent pas s'exprimer
-- comme une simple CHECK/UNIQUE parce qu'elles portent sur un agrégat d'autres lignes.

-- (a) "mouvement impossible ou incohérent" : un mouvement ne peut retirer d'un
-- emplacement plus que ce que le lot y possède réellement (solde dérivé des
-- mouvements déjà enregistrés). Couvre aussi, par construction, "réception
-- transformation sans stock GMC reçu" et "livraison dépassant le stock disponible" :
-- toute sortie de STOCK_GMC (transformation ou livraison) passe par cette même vérification.
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

-- (b) "affectation dépassant les quantités disponibles" / "double consommation
-- d'une même quantité" : la somme de TOUTES les affectations (actives ou déjà
-- clôturées par une sortie physique) d'un lot ne dépasse jamais sa quantité initiale.
CREATE TRIGGER trg_affectation_plafond BEFORE INSERT ON affectation_stock
BEGIN
    SELECT CASE WHEN (
        COALESCE((SELECT SUM(quantite) FROM affectation_stock WHERE lot_id = NEW.lot_id), 0) + NEW.quantite
    ) > (SELECT quantite_initiale FROM lot WHERE id = NEW.lot_id)
    THEN RAISE(ABORT, 'affectation refusée : dépasse la quantité disponible du lot')
    END;
END;

-- (c) une livraison ne peut jamais dépasser ce qui a été réellement affecté
-- (actif) à cette ligne de commande sur ce lot, moins ce qui a déjà été livré dessus.
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

-- (d) réaffectation : jamais silencieuse. L'affectation d'origine doit être active,
-- la quantité réaffectée ne peut dépasser celle de l'affectation d'origine, et
-- l'affectation d'origine est automatiquement clôturée par la réaffectation elle-même.
CREATE TRIGGER trg_reaffectation_origine_active BEFORE INSERT ON reaffectation
BEGIN
    SELECT CASE WHEN (SELECT statut FROM affectation_stock WHERE id = NEW.affectation_origine_id) != 'ACTIVE'
    THEN RAISE(ABORT, 'réaffectation refusée : l''affectation d''origine n''est plus active')
    END;
    SELECT CASE WHEN NEW.quantite_reaffectee > (SELECT quantite FROM affectation_stock WHERE id = NEW.affectation_origine_id)
    THEN RAISE(ABORT, 'réaffectation refusée : quantité supérieure à l''affectation d''origine')
    END;
END;

CREATE TRIGGER trg_reaffectation_cloture_origine AFTER INSERT ON reaffectation
BEGIN
    UPDATE affectation_stock SET statut = 'CLOTUREE' WHERE id = NEW.affectation_origine_id;
END;

-- (e) réception transformation : quantité reçue + chute, cumulées sur toutes les
-- lignes de réception d'une même ligne de sortie, ne dépasse jamais ce qui a été envoyé.
CREATE TRIGGER trg_reception_transfo_plafond BEFORE INSERT ON reception_transformation_ligne
BEGIN
    SELECT CASE WHEN (
        COALESCE((SELECT SUM(quantite_recue + quantite_chute) FROM reception_transformation_ligne
                  WHERE bon_sortie_transformation_ligne_id = NEW.bon_sortie_transformation_ligne_id), 0)
        + NEW.quantite_recue + NEW.quantite_chute
    ) > (SELECT quantite FROM bon_sortie_transformation_ligne WHERE id = NEW.bon_sortie_transformation_ligne_id)
    THEN RAISE(ABORT, 'réception de transformation refusée : dépasse la quantité envoyée')
    END;
END;

-- (f) double rattachement financier : une ligne de BL (fournisseur ou client)
-- n'est facturée qu'une fois. Déjà garanti par les contraintes UNIQUE des
-- migrations 0005/0008/0009/0010 (facture_fournisseur_ligne.bl_fournisseur_ligne_id,
-- facture_client_ligne.bl_client_ligne_id, regularisation_prix_fournisseur.facture_fournisseur_ligne_id,
-- macf_ligne_achat.bl_fournisseur_ligne_id) : aucun trigger supplémentaire nécessaire.
