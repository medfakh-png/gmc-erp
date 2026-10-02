# Phase 5.6 — Registre des décisions du 02/10/2026

**Statut : décisions prises par Mohamed dans la conversation du 02/10.** Ce
registre les rassemble pour qu'aucune ne reste seulement dans un message.
Analyse uniquement : aucun code, aucune migration, aucune modification de
la base. Déposé dans le dépôt le 02/10/2026, à la demande de Mohamed. Ces
décisions sont reportées dans `docs/BUSINESS_RULES.md` : §24 (12 m / 6 m),
§25 (Y6-L, Q-ANNUL, lectures L, propositions C), §26 (règles remplacées),
§27 (points ouverts).

Documents liés : `ANALYSE_PHASE_5_6_v10.md` (modèle 12 m / 6 m) et
`REVUE_PHASE_5_6_L_C.md` (tableau détaillé des 36 points, tel qu'il était
avant ces décisions).

---

## 1. Règle 12 m / 6 m

| Repère | Décision |
|---|---|
| LG1 | 1 barre de 12 m = 2 barres de 6 m pour la disponibilité commerciale. Règle de compatibilité du stock, pas une transformation ; aucun mouvement de transformation |
| LG2 | À finition identique seulement : NOIR → NOIR, GALVA → GALVA, GPP → GPP. NOIR/LAC → GALVA reste une transformation |
| LG3 | Une seule conversion : 12 m → 2 × 6 m. Aucun moteur générique |
| LG4 | Vente partielle : le reliquat de 6 m reste rattaché au lot source, devient disponible comme 6 m, n'est plus vendable comme 12 m |
| LG5 | Valorisation proportionnelle à la longueur ; pas de second CMP indépendant |
| LG6 | Sens inverse interdit : 2 × 6 m ne valent jamais 1 × 12 m |
| LG7 | Contrôle lot / ligne : article, finition, longueur, compatibilité, disponibilité |
| LG8 | K2 est remplacé par : « Un lot 12 m peut servir une ligne 6 m à finition compatible identique selon l'équivalence 1 × 12 m = 2 × 6 m. Cette compatibilité n'est pas une transformation industrielle. » |
| LG9 | Quinze tests obligatoires, listés dans la v10 (section O) |
| Q-COUPE | Oui : une ligne NOIR 6 m peut être servie par des barres NOIR de 12 m, sans opération de découpe en 5.6 |

Le texte complet de la règle définitive est dans la v10, section 0 bis.

**Source** : tes messages du 02/10. Tu les as écrites toi-même, puis tu
as validé la v10 qui repose sur elles ; je les tiens donc pour validées.
Dis-moi si l'une d'elles ne l'est plus.

## 2. Analyse v10

| Repère | Décision |
|---|---|
| V10-1 | Le reliquat de 6 m est consommé avant d'entamer une nouvelle barre. Pas un FIFO général |
| V10-2 | Une pièce de 6 m pèse la moitié d'une barre de 12 m (120 kg → 60 kg) ; aucun nouveau poids fournisseur |
| V10-3 | Valeur du reliquat calculée par différence ; valeur sortie + valeur restante = valeur initiale |
| V10-4 | Affichage « 2 barres de 12 m + 1 pièce de 6 m » ; jamais « 5 × 6 m » comme stock physique |
| V10-5 | Un reliquat de 6 m NOIR peut partir en galvanisation ou en GPP (5.8) |
| V10-6 | Migration corrective dédiée ; aucune migration maintenant ; toutes les données préservées |
| V10-7 | Ordre : documentation, tests, migration, code, tests complets, rapport |
| V10-8 | Reliquat disponible dans un autre lot : avertissement + confirmation + motif obligatoire + audit. Ni refus automatique, ni choix automatique du lot, ni FIFO |

## 3. Taux de change et bons de sortie transformation

| Repère | Décision |
|---|---|
| Y6-L | La règle écrite est la référence : tous les avenants d'une commande confirmée utilisent le taux de change du devis validé et gelé |
| Q-ANNUL | Un BST préparé et non exécuté peut être annulé par le SUPERADMIN seul : motif et audit obligatoires, historique conservé, allocations et réservations libérées explicitement, statut annulé conservé. Un BST exécuté ne s'annule pas ainsi |
| Q-BCT | **Reste en analyse.** Contrainte fixée : aucun mouvement physique sans commande de transformation |
| Q-TRF | **Reste en analyse.** Contrainte fixée : le SUPERADMIN seul crée les transformateurs ; un transformateur peut avoir plusieurs capacités ; aucune migration maintenant |

---

## 4. Lectures L-a à L-v

| Cas | Décision | Règle retenue |
|---|---|---|
| L-a | Oui | « Réservation commerciale » = réservation de devis, qui ne bloque pas le stock. « Affectation » inclut réaffectations et libérations |
| L-b | Oui, précisé | « Lot brut » = lot NOIR, c'est-à-dire l'état d'achat chez le fournisseur (NOIR ou LAC), avant toute transformation |
| L-c | Oui | Normal ou supplément : décidé dès la réservation du lot brut, puis gardé |
| L-d | Oui | Une affectation à cheval sur la quantité en vigueur est refusée ; elle se saisit en deux fois (normal, puis supplément avec motif) |
| L-e | Oui | Ligne ajoutée par avenant : valeurs d'article du jour de l'avenant ; les lignes existantes gardent les leurs |
| L-f | Oui | Le seul SUPERADMIN ne peut être ni désactivé ni changé de rôle ; son compte est créé à l'installation |
| L-f bis | Reporté | Le cas du SUPERADMIN indisponible sera décidé plus tard |
| L-g | Oui | Tout nouveau compte démarre sans aucun droit |
| L-h | **Modifié** | Le % GALVA de la fiche article est **proposé** sur la ligne ; l'utilisateur le garde ou le change ; un écart est signalé, jamais bloqué. Le % utilisé est enregistré sur la ligne, avec son auteur, et figé à la confirmation du devis |
| L-h bis | Décidé | Sur une ligne GALVA, le % est obligatoire et strictement supérieur à 0 : 0 % est interdit |
| L-i | Oui | Une réservation ne se déplace pas : libération avec motif, puis nouvelle réservation |
| L-j | Oui | Pas d'avenant sur un devis ; seulement sur une commande confirmée |
| L-k | Oui | Une barre inscrite dans un BST préparé est engagée : elle est déduite du disponible, même encore sur le parc |
| L-l | Oui, pour le moment | Seul le SUPERADMIN prépare un BST ; délégation possible plus tard |
| L-m | **Abandonnée** | Un BST n'est jamais refusé pour une question de capacité du transformateur |
| L-n | **Modifié** | Achat en excès libre. La réservation de barres avant transformation reste au plus juste (49 × 6 m → 25 barres) |
| L-o | Décidé | Tout utilisateur peut demander la création d'un article ; seul le SUPERADMIN le crée, si nécessaire |
| L-p | Oui, précisé | Seul le SUPERADMIN modifie une désignation, qu'il a confirmée et validée ; motif facultatif |
| L-q | Oui | Le devis affiche une marge prévisionnelle ; la marge réelle vient en 5.10 |
| L-r | Oui | En préparant un BST, on désigne soi-même la réservation exécutée |
| L-s | **Modifié** | Exécution partielle d'une réservation permise ; le reste demeure réservé |
| L-t | **Modifié** | Rien à faire : aucune modification exceptionnelle du taux n'est développée en 5.6. Le taux du devis validé reste la seule référence |
| L-u | Oui, précisé | La pièce en trop d'une transformation est affectable à une commande confirmée dès que le BST est préparé ; vendable seulement après la réception ; réservable à titre informatif au stade du devis |
| L-v | Oui | Un devis en cours n'est jamais recalculé tout seul quand un article change : le système signale, l'utilisateur décide |

## 5. Propositions C1 à C14

| Cas | Décision | Règle retenue |
|---|---|---|
| C1 | Oui | Commande créée seulement depuis un devis CONFIRMÉ ; quantités modifiables en brouillon, figées à la confirmation |
| C1 bis | A | Quantité modifiée en brouillon : recalcul avec les valeurs figées du devis |
| C1 ter | Décidé | Commande annulée : toutes les demandes en amont sont annulées, et on revient à la première phase : un **nouveau devis** est nécessaire. La marchandise déjà réceptionnée reste en stock. La marchandise déjà transformée chez le transformateur reste en stock. Les bons de commande restent **si la marchandise est réceptionnée** ; ceux dont rien n'est réceptionné sont annulés avec les autres demandes en amont (confirmé explicitement par Mohamed le 02/10 : « exactement ça ») |
| C2 | Oui | Unités de vente : TONNE, KG, PIÈCE, ML, M² ; liste extensible par le SUPERADMIN ; prix dans l'unité de vente |
| C3 | **Modifié** | Après la confirmation de la commande, le transport estimé n'est plus recalculé, même en cas d'avenant ; les chiffres définitifs viennent aux étapes suivantes. Pas de transport estimé sur un supplément |
| C4 | Oui | Commande annulée avec la même liste de causes que le devis ; « Autre » exige un commentaire ; un brouillon est annulé par son auteur ; un devis confirmé ne s'annule pas |
| C4 bis | Reporté | La liste des 8 causes d'annulation sera fixée plus tard |
| C5 | **Modifié** | Un devis dont la validité est dépassée n'est pas annulé ; ses réservations sont libérées. Il peut être **actualisé** plus tard : il redevient modifiable (prix, taux, quantités), l'ancien état restant dans l'historique |
| C5 bis | Décidé | Heure de référence : heure de Tunisie |
| C6 | Oui | Réservation de devis limitée au disponible ; annulée, jamais supprimée |
| C7 | Oui | Supplément possible tant que la commande est confirmée |
| C8 | Oui | Réaffectation par le SUPERADMIN, sur du non livré, même lot, même emplacement |
| C8 bis | A | Le type d'un supplément réaffecté se décide à la destination |
| C9 | Oui | Affectation faite par erreur : libérée par le SUPERADMIN avec motif |
| C10 | Oui | « Entièrement livrée » = livré ≥ quantité en vigueur et plus rien en attente ; clôture manuelle |
| C10 bis | A | Pour une ligne vendue au poids, la comparaison se fait en pièces |
| C11 | Oui | Reste à livrer = quantité en vigueur − livré. À approvisionner = quantité en vigueur − (affecté + réservé pour transformation + livré) |
| C12 | Oui | Fiche client inchangée en 5.6 ; adresse et identifiant fiscal notés pour la 5.9 |
| C13 | Déjà validé | LAC = NOIR |
| C14 | **Modifié** | La date de confirmation est enregistrée automatiquement quand la commande passe à l'état CONFIRMÉE, par le SUPERADMIN ou le commercial |

---

## 6. Règles antérieures remplacées ou modifiées par ces décisions

| Règle antérieure | Remplacée par | Conséquence |
|---|---|---|
| K2 (`BUSINESS_RULES.md` §22) : « un lot brut de 12 m n'est jamais considéré comme directement disponible en 6 m » | LG8 | Vrai seulement quand la finition change |
| v9, Q-COUPE : proposition « non » | Q-COUPE | Affectation directe acceptée |
| CT3, pour le % GALVA : valeur validée par le SUPERADMIN seul | L-h, L-h bis | Le % est saisi sur la ligne ; l'historique de validation du % devient inutile. La validation de la masse reste |
| Y1 bis (b) : « le système reprend exactement ce qui a été réservé » | L-s | Un BST peut envoyer moins que la quantité réservée ; finition et longueur attendues inchangées |
| CT5 : modification exceptionnelle du taux par le SUPERADMIN | L-t | Fonction non développée en 5.6 |
| v9, lecture L-m : BST refusé sans capacité | L-m abandonnée | Aucun contrôle de capacité à la préparation d'un BST |
| v9, lecture L-n : une seule barre en trop | L-n | Limite valable pour la réservation seulement ; achat libre |
| v9, C3 : transport recalculé sur la quantité en vigueur | C3 | Aucun recalcul après confirmation |
| v9, C5 : prolongation avant expiration seulement ; devis expiré figé | C5 | Actualisation possible après l'échéance |
| v9, C14 : date de confirmation par le client | C14 | Date automatique au passage à CONFIRMÉE |

## 7. Points encore ouverts

| N° | Point | État |
|---|---|---|
| 1 | **C4 bis** : liste des 8 causes d'annulation | À fournir plus tard |
| 2 | **L-f bis** : SUPERADMIN indisponible | À décider plus tard |
| 3 | **Q-BCT** et **Q-TRF** | En analyse |
| 4 | BST préparé et non exécuté d'une commande annulée : annulé d'office ou conservé ? | À relier à Q-ANNUL |
| 5 | Bon de commande partiellement réceptionné quand la commande client est annulée : sort de la partie non reçue | À préciser en 5.7 (achats) |
| 6 | Format du code article | Ouvert depuis la 5.5 ; n'empêche pas de coder |
| 7 | Transport estimé d'une ligne **ajoutée par avenant** (nouvel article) : calculé pour cette nouvelle ligne (K21) ou aucun transport estimé après la confirmation (C3) ? | Relevé à la relecture du 02/10, après les décisions ; à trancher |
| 8 | Validation d'ensemble de la Phase 5.6 | En attente |

## 8. Ce que ces décisions changent dans l'analyse, avant tout codage

- **Cas de test à réécrire** : M63 (exécution partielle), M68, M84, M85 (taux exceptionnel), M76 et U20 (longueurs), M88 (capacité), M13 (devis dont la validité est dépassée).
- **Migration proposée par la v9** : historique du % GALVA à retirer (DB3) ; réservation de lot brut avec conversion partielle (DB19) ; historique d'actualisation du devis (DB5) ; date de confirmation automatique (DB8).
- **Documentation** : `BUSINESS_RULES.md`, `PROJECT_STATUS.md`, `CURRENT_SESSION.md` et `CHANGELOG.md` ont été mis à jour le 02/10/2026, sur ton accord.

---

**Précisions ajoutées au report dans `BUSINESS_RULES.md` (relecture du 02/10)** : pour C11 et C10, les formules exactes de la v9 (« livré normal », « affecté normal actif non livré », « aucune affectation active non livrée ») sont rappelées comme précisions de calcul ; pour V10-4, LG3, LG6 et V10-2, le texte complet de tes messages est repris (« comme stock physique », « pour le moment », « automatiquement », portée KG / TONNE).

---

**PHASE 5.6 — V10 VALIDÉE — LECTURES L ET PROPOSITIONS C TRANCHÉES — POINTS OUVERTS LISTÉS EN SECTION 7 — AUCUN CODE**
