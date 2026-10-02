-- 0002_numerotation.sql
-- Compteur de numérotation automatique, séquentiel, distinct par type de document
-- (décision technique Phase 2 n°3, préfixes confirmés par l'utilisateur en Phase 4).

CREATE TABLE compteur_numerotation (
    type_document   TEXT NOT NULL,
    annee           INTEGER NOT NULL,
    dernier_numero  INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (type_document, annee)
);

-- Préfixes de référence (documentaire uniquement — pas une contrainte de base,
-- la génération du numéro se fait côté application, voir db/numerotation.py) :
--   DEV commande? non -> DEV=Devis, CMD=Commande client, BCF=Bon commande fournisseur,
--   BLF=BL fournisseur (interne), FFO=Facture fournisseur, BCT=Bon commande transformation,
--   BST=Bon de sortie transformation, RTR=Réception transformation, BLC=BL client, FAC=Facture client
