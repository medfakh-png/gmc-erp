# Phase 5.6 — Analyse consolidée : les AFFAIRES (version 9)

**Statut : ANALYSE CONSOLIDÉE — en attente de validation avant codage.**

- Aucun code, aucune migration (la **0021 n'est pas créée**), aucune
  table, aucun service, aucun repository, aucun test existant modifié,
  base inchangée.
- Ce fichier est **nouveau**. La v7, la v8 et tous les documents
  existants restent tels quels.
- La v5 n'existe que comme fichier remis dans notre conversation : les
  passages de la v5 dont dépend cette analyse sont **cités en toutes
  lettres**.
- Date : 02/10/2026.
- Sources :
  - v5, v6, v7 et v8 ;
  - règles validées des Phases 1 à 5.5 (`docs/BUSINESS_RULES.md`, notées
    « BR § ») ;
  - D1 à D6, N1 à N15, K1 à K22, O1 à O9, C1 à C14, X1 à X9 ;
  - tes réponses à Y1 à Y5 (30/09, 23 h 06) ;
  - ta précision sur le GPP (30/09, 23 h 21) : « le GPP c'est exactement
    similaire à la galvanisation dans le process sauf % est fixe » ;
  - **tes décisions CT1 à CT21 et Y1 bis** (message du 01/10, 12 h 13) ;
  - **tes décisions P-MULT, Y6, P-BST, P-ART, P-RET et P-KG-TR** (message
    du 02/10, 09 h 27) ;
  - l'état réel du projet et de la base, vérifié en lecture seule.

**Ce qui change dans la v9** (détail au §0 ter) :

- **P-MULT** : approvisionnement par excès (49 × 6 m → 25 × 12 m →
  50 × 6 m ; 49 affectés ; 1 restant, stock GMC réel, jamais attribué
  automatiquement).
- **Y6** : tous les avenants gardent le taux du devis validé ; la
  modification exceptionnelle est seulement historisée et auditée.
  *Écart de libellé à confirmer : tu écris « Y6 = A », mais ta règle
  correspond à l'option (b) de la v8 (§22, Y6-L).*
- **P-BST** : la 5.6 **prépare** le bon de sortie transformation (lot,
  disponibilité, résultat attendu, comparaison, conversion de la
  réservation, document) ; la 5.8 **exécute** la sortie physique, le
  mouvement, la transformation, le lot transformé et la réception.
- **P-ART** : création d'article par le SUPERADMIN seul ; demande de
  création par les utilisateurs ; modification à impact métier = nouvelle
  version ; correction administrative auditée ; commande confirmée
  jamais modifiée.
- **P-RET** : deux transformations seulement, GALVANISATION → GALVA et
  GPP → GPP ; le type choisi dans le BST fixe la finition de retour.
- **P-KG-TR** : ligne en KG → KG ÷ 1 000 × EUR/T ; prix de vente, coût
  d'achat, coût de transformation et transport toujours séparés.
- **15 contradictions** relevées entre la v8 et ces décisions (§22) : 13
  corrigées, 2 signalées et laissées ouvertes (Q-BCT, Q-COUPE) ;
  registre complété (§26).
- **Tests** : 210 cas proposés (174 en v8), dont 36 nouveaux (§12).
- **Plan de développement** proposé (§29).
- **Restent ouverts** (§22, §23) : la confirmation du libellé de Y6 ;
  quatre questions apparues en intégrant tes décisions (Q-COUPE, Q-BCT,
  Q-ANNUL, Q-TRF) ; les lectures L-a à L-v ; les propositions C.

**Ce qui changeait dans la v8** (détail au §0 bis, registre des décisions
remplacées au §26) :

- **CT1 à CT21** sont validés, avec tes précisions sur CT1, CT10 et
  CT18.
- **Y1 bis** est validé : réservation bloquante, conversion au bon de
  sortie transformation, « confirmation client » = commande confirmée,
  SUPERADMIN seul, affectation liée créée à la conversion.
- **Y5 bis** est tranché par CT10 : correction d'une erreur de prix par
  le SUPERADMIN, avec motif.
- **Y4 bis** est tranché pour l'essentiel, par CT3, CT7 et CT20 :
  GALVA et GPP en KG ou TONNE, poids calculé, valeurs article validées
  en 5.6.
- **GPP** : même parcours que le GALVA, avec un taux global fixe (CT4).
- **L1** est réglé par ton périmètre du 01/10.
- **17 contradictions** entre l'ancienne analyse et tes décisions sont
  corrigées (§22) ; chaque ancienne règle reste écrite, marquée
  « SUPERSEDED PAR … » (registre au §26).
- **Nouveaux contrôles** : modèle conceptuel (§27), chronologie et
  dépendances 5.6 à 5.10 (§28).
- **Tests** : 174 cas proposés (142 en v7), dont 32 nouveaux (§12).
- *Restaient ouverts dans la v8 : Y6 ; P-BST, P-ART, P-RET, P-KG-TR,
  P-MULT ; les lectures L-a à L-j ; les propositions C. Les six premiers
  sont décidés le 02/10 (§0 ter).*

Légende :

- **[V]** : décision validée par toi (source citée).
- **[CT]** : choix technique. **Depuis le 01/10, CT1 à CT21 sont
  validés** (§21).
- **[PROP]** : proposition métier de ma part (issue des C), **non
  validée**.
- **[Y…]**, **[P-…]** : points des versions précédentes, présentés en
  FACT → PROPOSITION → IMPACT → POINT À VALIDER (§22). Y6 et les cinq P-
  sont **décidés le 02/10**.
- **[Q-…]** : question nouvelle de la v9, encore ouverte (§22). Je n'en
  tranche aucune.
- **[L-…]** : lecture d'une de tes décisions là où elle ne dit pas tout ;
  appliquée dans l'analyse, à confirmer (§22).
- **SUPERSEDED PAR …** : règle ancienne conservée pour l'historique et
  remplacée par la décision citée (§26).
- **FACT** : constaté dans le schéma, le code ou les documents.
- **Allocation** et **affectation** désignent la même chose : une
  quantité d'un lot attribuée à une ligne de commande. Ton message du
  02/10 dit « allocation » ; les décisions précédentes disaient
  « affectation ».

---

## 0. Tes réponses du 30/09 (23 h 06) et leur intégration

| Point | Ta réponse (tes mots) | Intégration | Reste à confirmer |
|---|---|---|---|
| Y1 | « il peut être réservé dès la confirmation client et avec la transformation il sera automatiquement affecté » | **VALIDÉ dans son principe.** Un lot brut encore chez GMC peut être **réservé** pour une ligne d'un autre état dès la confirmation du client. La transformation prévue est déclarée à la réservation. La réservation devient **automatiquement** une affectation « avec la transformation » (§6.3 bis). | Y1 bis (§22) : réservation bloquante ou non, moment exact de l'affectation automatique, qui réserve, sens de « confirmation client ». |
| Y2 (X2) | Transport hors tonne prévisionnel « saisi manuellement lors de l'établissement du devis ainsi que le poids de la ligne », parce que le poids servira ensuite au calcul des marges. Le montant final du transport, « mentionné après facturation », sera réparti par poids pour la marge par article, dans les résultats et le tableau de bord. | **VALIDÉ.** Option (a) : montant total estimé en EUR et poids de la ligne saisis sur la ligne du devis. La répartition du transport réel par poids relève de la 5.9/5.10 (§7.2). | — |
| Y3 (X5) | « le commercial saisit TND pour 1 euro » | **VALIDÉ.** Option (a) : taux en TND pour 1 EUR (ex. 3,40) ; coût EUR = montant TND ÷ taux, calculé exactement. Le R de X5 vaut donc 1 ÷ taux saisi. Les exemples restent 726,47 EUR et 4 499,41 EUR. | — |
| Y4 | « la galvanisation sera effectuée que sur un article dont son unité de vente soit kg ou tonne » | **VALIDÉ dans son principe.** Une vente GALVA se fait uniquement en KG ou en TONNE. Il n'y a donc plus de vente GALVA hors poids, et le cas X8 « GALVA hors tonne » ne se présente plus (§6.9). | Y4 bis (§22) : unité de la ligne ou de l'article ; la vente en KG se traite-t-elle comme la tonne ; le référentiel article minimal est-il en 5.6 (question Y4 initiale, restée sans réponse). |
| Y5 | « pas de renégociation de prix de vente. Commande confirmée prix de vente confirmé. La renégociation sera avant validation si il existe. » | **VALIDÉ.** **Remplace X1** et la partie « renégociation après confirmation » de K10 et d'O8. Le prix de vente se négocie au stade du devis, puis est figé à la confirmation (§6.7). | Y5 bis (§22) : correction d'une erreur de saisie du prix après confirmation. |
| Y6 | (pas de réponse) | — | Toujours ouvert (§22). |
| L1 | (pas de réponse) | — | Toujours ouvert (§22). |


Le tableau ci-dessus est conservé tel qu'il était le 30/09. Les colonnes
« Reste à confirmer » sont réglées au §0 bis, sauf Y6, décidé le 02/10
(§0 ter). En particulier,
pour Y1 : « dès la confirmation du client » se lit « dès la commande
confirmée » (Y1 bis (c)), et « la réservation devient automatiquement
une affectation » est **SUPERSEDED PAR Y1 bis (mécanisme)** : la
réservation est conservée et une affectation liée est créée au BST.

---

## 0 bis. Tes décisions du 01/10 (CT1 à CT21, Y1 bis) et leur intégration

### Choix techniques CT1 à CT21 — tous VALIDÉS

| CT | Décision | Contenu retenu (tes mots ou leur résumé fidèle) | Intégré dans |
|---|---|---|---|
| CT1 | OUI | **Exactement un seul SUPERADMIN**, imposé par l'application et par la base. « Le contrôle doit empêcher la création d'un deuxième SUPERADMIN. » | §6.19, DB1, P08, P17, I05, E10 ; lecture L-f |
| CT2 | OUI | Structures de comptes, permissions, modules et droits par compte et par module créées dès la 5.6. Droits initiaux = situation actuelle. Aucune délégation supplémentaire active ; architecture prête pour une délégation future sans refonte. Le rôle « commercial » ne donne pas automatiquement tous les droits commerciaux. Les opérations sensibles restent soumises à des permissions explicites. | §6.19, DB2, P01 à P06, P18, I08, E07, E10 ; lecture L-g |
| CT3 | OK | Historique dédié, jamais modifié, des validations des valeurs article (article, paramètre, méthode de poids, valeur, unité, % GALVA, sources affichées, validé par, date/heure, motif). La dernière validation est en vigueur. La masse actuelle de la fiche = « valeur MV à vérifier », jamais considérée comme validée. Une vente à poids calculé ne peut pas utiliser une masse non validée. Méthodes kg/ml, kg/m², kg/pièce, autre méthode validée ; liste extensible. % GALVA : non renseigné / 0 % / x %, jamais 0 automatique. SUPERADMIN seul. Une nouvelle validation ne modifie jamais un devis ou une commande confirmés. | §6.9, DB3, U05, M02, M03, M04, M05, M67, P19, R10, I16, I21 ; lecture L-h |
| CT4 | A | GPP = **réglage unique en base**, actuellement 2 %, commun à tous les articles, modifiable par le SUPERADMIN seul, avec date d'effet, historisé, sans nouvelle version du logiciel. Les devis et commandes confirmés gardent le taux utilisé. Pas de % GPP par article. GALVA et GPP suivent le même parcours ; GALVA = % article validé, GPP = taux global. | §6.9, DB3, U03, U23, M66, P20, R11, I17 |
| CT5 | OK | Taux saisi à la main en TND pour 1 EUR (3,40 = 1 EUR pour 3,40 TND) ; TND → EUR = division ; chaque saisie = nouvelle valeur, jamais modifiée ni supprimée, avec auteur et date ; le devis pointe vers son taux ; commande et avenants utilisent celui du devis, figé à la confirmation ; modification exceptionnelle par le SUPERADMIN = nouveau taux, motif obligatoire, audit complet ; taux conservé tel que saisi, jamais arrondi. **Effet d'une modification exceptionnelle sur les avenants futurs : Y6, toujours ouvert.** | §6.2, DB4, DB5, U24, M06, M07, M08, M24, M68, P12, I12 ; **Y6** (§22) |
| CT6 | OK | Calcul sur le total de la ligne ; chaque prix garde son unité ; un seul arrondi final au centime EUR ; revient unitaire affiché = total ÷ quantité (ex. 4 499,41 ÷ 4,32 = 1 041,53 EUR/t). **Photo complète et figée** à la confirmation (achat, transformation, transport, poids, taux, résultat, autres valeurs du calcul). | §6.2, DB6, U11, U12, U13, U25, M69 |
| CT7 | OK | « Transformation prévue : OUI / NON » sur chaque ligne de devis ; si OUI, coût obligatoire (0 seulement s'il est saisi) ; si NON, aucun coût. GALVA et GPP imposent une vente en KG ou TONNE. | §6.2, §6.9, DB6, M10, M64 |
| CT8 | OK | Unité du coût de transformation conservée avec le coût : TND/t, TND/kg, TND/pièce, TND/ml, montant total de la ligne. | §6.2, DB6, U26, M10 |
| CT9 | OK | Coûts estimés (achat, transformation) recopiés du devis vers la commande ; saisis dans l'avenant pour un article ajouté ; jamais pré-remplis depuis un ancien achat ; prévision commerciale ≠ coût réel. | §6.4, §6.6, DB9, M12, M22, M71 |
| CT10 | OK | Une seule table d'avenants, append-only ; ancienne et nouvelle valeur, motif, auteur, date/heure, impact quantitatif et financier avant/après. Même mécanique pour les interventions exceptionnelles du SUPERADMIN sur une commande confirmée. Aucun avenant de prix après confirmation. **Erreur de prix après confirmation : correction SUPERADMIN, motif obligatoire, audit complet, « ce n'est PAS une nouvelle négociation commerciale ».** Ligne au poids : un avenant de quantité recalcule le poids par la méthode validée. | §6.6, §6.7, DB10, DB11, M20, M23, M27, M65, P10, P21, I06, I07 |
| CT11 | OK | Aucun mouvement physique ne fait passer le stock disponible sous l'affecté ou le bloqué ; contrôle dans l'application et dans la base ; envoi en transformation, chute, correction, retour ; livraisons complétées en 5.9. | §6.10, DB12, DB19, M58, M59, M72, I13 |
| CT12 | OK | Marchandise envoyée en transformation et non réceptionnée, calculée à partir du stock physique chez les transformateurs ; distinguer stock GMC, stock chez le transformateur, affecté, envoyé/non réceptionné, disponible. Bons et transformation physique en 5.8. | §6.16, M55 |
| CT13 | OK | Lot brut non réservé : signal « utilisable après transformation », informatif seulement (ni réservation, ni affectation, ni mouvement, ni mise en vente). | §6.3 bis, M73 |
| CT14 | OK | Correction d'inventaire : référence et date du PV signé par la Direction Générale, auteur, date/heure, audit complet ; SUPERADMIN obligatoire dans l'application et dans la base. | §6.19, DB15, M56, M57, P13, I14 |
| CT15 | OK | Migration 0021 transactionnelle, tout ou rien, additive, sans suppression ni réécriture destructrice, données reprises, contrôles protégés en base, valeurs par défaut pour préserver les tests existants ; intégrité, clés étrangères, tests existants et nouveaux cohérents après migration. | §11, I01, I02, I03, I18 |
| CT16 | OK | Ligne ajoutée par avenant marquée AVENANT, quantité initiale 0, quantité venant de l'avenant ; la situation montre « 0 initial + X ajouté » ; l'avenant permet de retrouver l'origine de la ligne. | §6.5, DB9, M22 |
| CT17 | OK | Type fixé à la création : NORMALE ou SUPPLÉMENT. Normale tant que le cumul normal ne dépasse pas la quantité en vigueur ; au-delà, SUPPLÉMENT + motif ; jamais requalifié. X9 maintenu. | §6.13, M34 à M37, M74, I19 ; lecture L-d |
| CT18 | OK, **avec précision** | Résultat attendu renseigné **à l'établissement du bon de sortie transformation (BST)**. L'état de retour n'est pas libre : galvanisateur → GALVA ; transformation GPP → GPP. Longueur et quantité attendues définies selon la transformation prévue et les règles de conversion (25 × 12 m → 50 × 6 m, conversion exacte). Le résultat doit correspondre à une **éventuelle** réservation préalable ; il est figé dès qu'une affectation s'y rattache. Transformation réelle, lot transformé et réception en 5.8 ; livraison interdite avant réception (5.9). | §6.11, DB17, U20, M40, M41, M60, M63, M70, E09 ; périmètre : **P-BST** ; DEBIT/AUTRE : **P-RET** (§22) |
| CT19 | OK | Clôture avec reliquat : statut SOLDÉE (pas de statut supplémentaire) ; motif obligatoire (reliquat annulé par le client, reliquat devenu inutile, commande abandonnée, AUTRE + commentaire) ; reliquat conservé ligne par ligne ; affectations et réservations affichées puis libérées selon la procédure explicite ; aucun choix silencieux. | §6.17, DB8, DB13, M48 à M52, E05 |
| CT20 | OK | Chaque ligne garde poids, unité et origine. CALCULÉ (méthode, valeur utilisée, % GALVA ou règle GPP) ; DÉCLARÉ seulement quand une déclaration manuelle est permise, c'est-à-dire aujourd'hui **NOIR/LAC hors vente au poids**. GALVA et GPP = KG ou TONNE, poids toujours calculé. Poids figé dans la photo à la confirmation. | §6.9, DB6, U08, U09, U10, U21, U22, M03, M05, M11, M69, M75 ; transport en KG : **P-KG-TR** |
| CT21 | OK | Réservation d'un lot brut pour transformation : détails fonctionnels au §6.3 bis (enregistrement, contrôles, effets, conversion au BST, libération, audit, situation). | §6.3 bis, DB12, DB19, U18, M43, M61 à M63, M72, M76 à M78, P16, R12, I20, E04, E09 ; lectures L-b, L-c, L-i ; P-MULT |

### Y1 bis — VALIDÉ

| Y1 bis | Décision | Contenu |
|---|---|---|
| (a) | OUI | La réservation bloque réellement le disponible du lot : 100 barres physiques, 25 réservées → disponible commercial 75, stock physique toujours 100. Aucun mouvement. Personne d'autre ne peut réserver ni affecter cette quantité. |
| (b) | AU BON DE SORTIE TRANSFORMATION | À l'établissement du BST, le système compare le résultat prévu à la réservation : identique → conversion automatique ; différent → BST refusé. Aucun choix automatique : le système reprend exactement ce qui a été réservé. |
| (c) | OUI | « Confirmation client » = commande client confirmée. |
| (d) | OUI | Seul le SUPERADMIN peut réserver. |
| Mécanisme | Nouvelle affectation liée + réservation conservée | La réservation reste dans l'historique ; une nouvelle affectation liée est créée ; le lien réservation → affectation est traçable. |

### Autres points réglés par ces décisions

| Point | Réglé par | Résultat |
|---|---|---|
| Y4 bis (i) — unité de la ligne ou de l'article | CT7 (« GALVA et GPP imposent une vente en KG ou TONNE » sur la ligne de devis) | Contrôle sur l'**unité de vente de la ligne**. |
| Y4 bis (ii) — vente en KG | CT20, règles « GALVA / GPP » du 01/10 | Le KG est une vente au poids, comme la tonne : poids calculé par la méthode validée. Le **transport** d'une ligne en KG n'est pas tranché : **P-KG-TR** (§22). |
| Y4 bis (iii) — référentiel en 5.6 | CT3 | Le mécanisme de validation des valeurs article est créé en 5.6 : sans lui, aucune vente au poids n'est possible (« une vente nécessitant un poids calculé ne peut utiliser une masse non validée »). Reste ouvert : **création d'article et contrôle du changement d'unité** (§22, P-ART). |
| Y5 bis — erreur de prix après confirmation | CT10 | Option (b) : correction par le SUPERADMIN, motif obligatoire, audit complet, pas une renégociation. |
| GPP | Précision du 30/09 + CT4, CT7, CT18, CT20 | Même parcours que le GALVA ; taux global 2 % ; vente KG ou TONNE seulement. |
| L1 — cas A d'O8 | Ton périmètre du 01/10 (« 5.6 : … affectations » ; « 5.7 = achats / commandes fournisseurs / réceptions ») | L'affectation d'un lot existant est en 5.6 ; tout le côté fournisseur est en 5.7. |
| Y6 | — | **POINT MÉTIER ENCORE OUVERT**, comme tu l'as demandé (« ne pas inventer sa réponse ») : aucune décision explicite n'est enregistrée. |

*Les tableaux de ce §0 bis sont conservés tels qu'ils étaient le 01/10.
Les points qu'ils citent comme ouverts (Y6, P-BST, P-RET, P-KG-TR, P-ART,
P-MULT) sont décidés le 02/10 : voir §0 ter.*

---

## 0 ter. Tes décisions du 02/10 et leur intégration

Ton message du 02/10 (09 h 27) dit : « Les décisions ouvertes précédemment
dans l'analyse v8 sont maintenant VALIDÉES », puis détaille six points.
Je les ai intégrés **d'après ton texte**. Deux de tes libellés
(« Y6 = A », « P-ART = B ») ne correspondent pas aux lettres de la v8 :
c'est signalé ci-dessous.

| Point | Ta décision (tes mots ou leur résumé fidèle) | Intégré dans | Remarque |
|---|---|---|---|
| **P-MULT** | Quantité commerciale en barres de 6 m : approvisionnement possible en barres de 12 m ; 1 × 12 m = 2 × 6 m ; **calculé par excès**. 49 × 6 m → 25 × 12 m → 50 × 6 m ; 49 affectés/vendus ; 1 restant, qui peut être vendu plus tard à une autre affaire **ou** rester en stock GMC. Le système ne choisit jamais. Le reliquat de conversion est un stock GMC réel, traçable et disponible ; ce n'est pas une perte. | §6.3 bis, §6.8, §6.12, §6.16, DB19, U20, U27, U28, M76, M81 à M83, E11 | C'est l'option (a) de la v8. Une question reste : ce passage 12 m → 6 m **sans** galvanisation ni GPP (**Q-COUPE**, §22). Lectures L-n, L-u. |
| **Y6** | « Y6 = A ». Le taux du devis à sa validation est la référence de l'affaire ; **tous les avenants futurs utilisent le même taux que le devis initial**. Une modification exceptionnelle par le SUPERADMIN est historisée et auditée ; elle ne modifie pas le taux applicable aux avenants, ne recalcule ni les anciennes lignes ni les avenants déjà enregistrés. Le taux des avenants reste celui de la photo du devis validé. | §6.2, §6.6, M08, M24, M68, M84, M85, P12 | **Écart de libellé (Y6-L, §22)** : dans la v8, l'option (a) était « le nouveau taux sert aux avenants suivants » et l'option (b) « les avenants gardent toujours le taux figé ». Ta règle écrite est celle de (b). J'ai intégré **ta règle écrite**, répétée trois fois dans ton message. À confirmer d'un mot. Lecture L-t : à quoi sert alors le taux modifié ? |
| **P-BST** | Responsabilités strictement séparées. **5.6** : sélectionne le lot brut, vérifie sa disponibilité, définit la transformation prévue et le résultat attendu, vérifie la compatibilité, compare avec la réservation, convertit la réservation en nouvelle allocation liée au BST, génère/prépare le document BST ; **aucun mouvement, aucun lot transformé**. **5.8** : sortie physique, mouvement, transformation, nouveau lot, résultat réel, réception, disponibilité après réception GMC. « BST commercial ≠ mouvement physique » ; « allocation ≠ mouvement physique ». | §2, §3, §6.3 bis, §6.11, **§6.11 bis**, §7.2, §8, DB17, M60, M61, M63, M70, M86 à M88, S05, S07, S08, P23, R13, E04, E09, E11 | Remplace ma proposition v8 (fonction 5.6 appelée par la 5.8 dans la même opération que l'envoi) et précise ta liste du 01/10 (« 5.8 = … bons de sortie »). Questions restantes : **Q-BCT**, **Q-ANNUL** ; lectures L-k, L-l, L-r, L-s. |
| **P-ART** | « P-ART = B ». Création d'article par le **SUPERADMIN uniquement** ; les utilisateurs opérationnels sélectionnent un article existant ou **demandent** une création. Modification à **impact métier** (masse, poids, % GALVA, unité de valorisation, caractéristiques de calcul, règles techniques) : **nouvelle version historisée**, ancien état conservé, aucun recalcul silencieux. **Correction administrative** (libellé, faute de frappe) : sans nouvelle version, mais auditée (ancienne et nouvelle valeur, utilisateur, date/heure, motif si nécessaire). Une commande confirmée garde les caractéristiques de sa confirmation. | **§6.21**, §6.9, §6.19, DB21, P22, P24, M89 à M94, I22, R14, E12 | La v8 ne proposait pas d'option « B » pour P-ART ; j'ai intégré ton texte. Les règles sont dans les tests de la 5.6, donc la création d'article est **dans la 5.6**. Lectures L-o, L-p, L-v. |
| **P-RET** | Deux types de transformation seulement : **GALVANISATION** → finition de retour **GALVA**, automatiquement ; **GPP** → **GPP**, automatiquement. L'utilisateur ne choisit pas une autre finition. Un même transformateur peut avoir les deux capacités. Le **type choisi dans le BST** détermine le résultat. Longueur et quantité attendues définies dans le BST. Nouveau lot en 5.8 seulement. Pas de type AUTRE, découpe, perçage. | §6.11, §6.11 bis, DB17, DB20, M60, M76, M79, M95 à M98, I23, E09 | Remplace mes propositions v8 (état de retour déduit du type du transformateur ; DEBIT ; AUTRE). FACT : la base classe un transformateur par un seul type et connaît DEBIT et AUTRE (DB20). Lecture L-m ; question **Q-TRF** (qui crée les transformateurs et leurs capacités). |
| **P-KG-TR** | Le transport est un composant du prix de revient, indépendant du prix de vente et du coût d'achat. Prix de vente → CA ; coût d'achat ; coût de transformation ; transport ; total → prix de revient ; CA − prix de revient → marge. Ligne en KG avec transport en EUR/T : **KG ÷ 1 000 = tonnes ; tonnes × EUR/T**. Exemple : 5 000 kg, 100 EUR/T → 500 EUR. Ne modifie ni le prix de vente, ni le prix d'achat, ni la quantité. Autres unités : pas de conversion inventée. Le transport réel final reste distinct. | §6.2, §6.7, `core/prix_revient.py`, M80, U15, U29 à U31 | C'est l'option (a) de la v8. Lecture L-q (affichage d'une marge prévisionnelle). |

**Ce que ton message ne détaille pas.** Les lectures **L-a à L-j** et les
propositions **C** de la v8 ne sont pas citées dans ton message. Je ne
les ai **pas** considérées comme validées (§22, §23). Si ta phrase
d'introduction les couvrait, dis-le-moi : je les passerai en VALIDÉ.

---

## Sommaire

0. Tes réponses du 30/09 (23 h 06) et leur intégration
0 bis. Tes décisions du 01/10 (CT1 à CT21, Y1 bis) et leur intégration
0 ter. Tes décisions du 02/10 (P-MULT, Y6, P-BST, P-ART, P-RET, P-KG-TR)
1. Objet de la Phase 5.6
2. Périmètre inclus
3. Hors périmètre
4. État réel du projet avant la Phase 5.6
5. Architecture concernée
6. Modèle métier consolidé
   - 6.1 à 6.6 : clients, devis, réservations (dont 6.3 bis :
     réservation d'un lot brut, Y1, Y1 bis, CT21), commandes, lignes,
     avenants
   - 6.7 à 6.9 : prix de vente, quantités, poids
   - 6.10 à 6.17 : affectations, bon de sortie transformation (6.11 bis),
     compatibilité, suppléments, réaffectations, situation, clôture
   - 6.18 à 6.21 : statuts, permissions, historisation, articles
7. Impacts base de données
8. Impacts services
9. Impacts repositories
10. Impacts tests
11. Migration 0021 — proposition uniquement
12. Tests proposés
13. Non-régression
14. N1 à N15
15. K1 à K22
16. O1 à O9
17. C1 à C14
18. X1 à X9
19. Règles existantes à préserver (contrôle)
20. Matrice de traçabilité
21. CT1 à CT21
22. Contradictions résiduelles et précisions à confirmer
23. Points nécessitant encore une validation humaine
24. Contrôles finaux
25. Checklist finale avant codage
26. Registre des décisions remplacées (SUPERSEDED)
27. Vérification du modèle conceptuel
28. Chronologie et dépendances entre phases
29. Plan de développement proposé (après validation)

---

## 1. Objet de la Phase 5.6

Mettre en place, dans le backend (services Python, sans API HTTP ni
interface), la gestion commerciale des **affaires** :

- clients, devis, réservations commerciales (informatives, au stade du
  devis) ;
- réservation d'un lot brut pour une transformation, dès la commande
  confirmée (Y1, Y1 bis, CT21) ;
- commandes, lignes de commande, avenants, prix de vente ;
- affectations commerciales de lots (y compris chez un transformateur),
  suppléments, réaffectations ;
- **préparation commerciale du bon de sortie transformation** (BST) :
  lot, résultat attendu, conversion de la réservation, document — sans
  aucun mouvement (P-BST, P-RET) ;
- clôture avec reliquat ;
- situation calculée de l'affaire ;
- **articles** : création par le SUPERADMIN, demandes de création,
  versions, corrections (P-ART) ; valeurs article validées et réglage
  GPP (CT3, CT4), sans lesquels aucune vente au poids n'est possible ;
- comptes, modules et permissions (CT1, CT2).

**Aucune opération de la Phase 5.6 ne crée de mouvement physique de
stock** [V ton message §2].

---

## 2. Périmètre inclus [V]

**Ta liste du 01/10 (12 h 13)** :

- clients ;
- devis ;
- réservations commerciales ;
- commandes clients ;
- lignes de commande ;
- affectations ;
- réservations de lots bruts pour transformation ;
- suppléments ;
- avenants ;
- situations d'affaire ;
- clôture avec reliquat.

*Liste de la v7, conservée pour l'historique — **SUPERSEDED PAR ta liste
du 01/10*** : clients ; devis ; réservations informatives ; commandes
clients et lignes de commande ; affectations commerciales, dont celles
sur marchandise chez un transformateur (X3) ; suppléments ;
réaffectations ; avenants ; statuts ; situation calculée de l'affaire ;
clôture avec reliquat. Les sujets sont les mêmes ; la réservation de lots
bruts y est désormais nommée.

Ma lecture de deux termes de ta liste (lecture L-a, §22) :

- « réservations commerciales » = les réservations **informatives** du
  devis (§6.3), distinctes des réservations de lots bruts (§6.3 bis) ;
- « affectations » comprend les affectations sur marchandise chez un
  transformateur (X3), les réaffectations, les libérations et les statuts
  de ces objets.

Éléments nécessaires à ce périmètre (avec la source) :

- **Comptes, modules et permissions** (O5, X4 ; **CT1, CT2 validés**) :
  chaque opération ci-dessus contrôle les droits.
- **Poids de vente et prix de revient estimé du devis** (N1 à N5, K4,
  O7, X8, Y2, Y3, Y4 ; **CT6, CT7, CT8, CT20**) : ils font partie du
  devis. Le coût réel, la répartition du transport réel par poids et la
  marge restent en 5.9/5.10 (Y2).
- **Valeurs article validées** (historique, **CT3**) et **réglage GPP**
  (**CT4**) : sans eux, aucune vente au poids n'est possible (« une vente
  nécessitant un poids calculé ne peut utiliser une masse non
  validée »).
- **Réservation d'un lot brut pour transformation** (Y1, **Y1 bis,
  CT21**) : création, contrôles, blocage, libération, situation.
- **Contrôles ajoutés à deux fonctions existantes du Stock Service
  (5.5)**. La 5.6 ne crée aucune nouvelle écriture de stock ; elle
  ajoute seulement des contrôles :
  - `corriger_inventaire` : SUPERADMIN + PV (K17, **CT14**) ;
  - garde-fou (N13, K12, **CT11**) : aucun mouvement ne fait passer le
    disponible sous l'affecté ou le bloqué, réservations comprises.
- **Préparation commerciale du bon de sortie transformation** (CT18,
  Y1 bis (b), **P-BST et P-RET décidés le 02/10**) : la 5.6 sélectionne
  le lot, vérifie, définit le résultat attendu, compare, convertit la
  réservation et prépare le document ; elle ne crée ni mouvement ni lot
  transformé (§6.11 bis).
  - *v8 : « le bon de sortie est établi en 5.8 (ta liste). Ce que la 5.6
    code de ce mécanisme est à confirmer : P-BST » — **SUPERSEDED PAR
    P-BST (02/10)**.*
- **Articles** (**P-ART décidé le 02/10**) : création par le SUPERADMIN,
  demandes de création, versions pour les modifications à impact métier,
  corrections administratives auditées, contrôle du changement d'unité
  de valorisation (§6.21).
  - *v8 : « non tranchés par CT3, P-ART » — **SUPERSEDED PAR P-ART
    (02/10)**.*
- **Approvisionnement par excès** (P-MULT) : la 5.6 calcule le nombre de
  barres à réserver et le reliquat de conversion ; l'achat lui-même
  reste en 5.7.

---

## 3. Hors périmètre [V]

| Sujet | Phase |
|---|---|
| Achats, commandes fournisseurs, réceptions fournisseurs, **partie fournisseur d'O8** | 5.7 |
| Transformations : **exécution physique** du BST préparé en 5.6 (sortie, mouvement), transformation, résultat réel, **lot transformé**, **réception de transformation**, **rattachement d'une affectation au lot résultant** (X3) | 5.8 |
| Autres transformations (découpe, perçage, type AUTRE) | Hors périmètre actuel (P-RET) |
| BL client, facturation client ; interdiction de livrer avant réception du lot transformé (CT18) ; garde-fou sur les livraisons (CT11) | 5.9 |
| Coûts réels et marge | 5.10 |
| Interface | 6 |

Source : ta liste du 01/10 (« 5.7 = achats / commandes fournisseurs /
réceptions ; 5.8 = transformations / bons de sortie et réception de
transformation ; 5.9 = BL client / facturation ; 5.10 = coûts réels /
marge ; 6 = UI »). **Précisé par P-BST (02/10)** : pour le bon de
sortie, la 5.6 prépare le document et la 5.8 exécute la sortie
physique.

Ce qui est préparé seulement (architecture), **sans migration
anticipée**, est listé au §7.2.

---

## 4. État réel du projet avant la Phase 5.6 (FACT, lecture seule)

| Élément | État |
|---|---|
| Base `db/gmc.db` | 20 migrations ; 47 tables, 4 vues, 94 triggers, 52 index ; `integrity_check` = ok ; aucune anomalie de clé étrangère ; **aucune donnée métier** ; empreinte du schéma `89e3225d…ab718e4`. |
| Technologie | Python 3.11 + `sqlite3`, **aucun ORM** (pas de SQLAlchemy dans le projet). |
| Code existant | `core/` (arrondi, audit, configuration, erreurs, masses validées, numérotation, unités) ; `repositories/` (article en lecture, audit, inventaire initial, numérotation, stock, unité de valorisation) ; `services/` (stock, inventaire initial, unité de valorisation). Aucun service d'affaires. **Aucun code applicatif ne crée de document de transformation** (bon de commande, bon de sortie, réception) : seuls les tests en insèrent. |
| Tests | 293 tests collectés (212 fonctions, certaines paramétrées) dans 10 fichiers ; l'utilisateur de test a le rôle ADMINISTRATEUR. |
| Tables d'affaires | `client`, `devis`, `devis_ligne`, `reservation_devis`, `commande_client`, `commande_ligne`, `affectation_stock`, `reaffectation` existent depuis la Phase 4, sans les règles 5.6. |
| Utilisateurs | Rôles COMMERCIAL, MAGASINIER, COMPTABILITE, DIRECTION, ADMINISTRATEUR ; **pas de SUPERADMIN** ; aucune table de permissions. **Aucun compte** dans la base (0 ligne). Les tests créent **un seul** utilisateur par base, de rôle ADMINISTRATEUR. |
| Taux | `taux_change` : colonne `taux REAL > 0`, immuable (triggers), sans auteur. Le schéma ne fixe pas le sens de lecture. Les tests enregistrent `devise='EUR', taux=3.4`, ce qui correspond au sens que tu as validé en Y3 : **TND pour 1 EUR**. La colonne est un nombre à virgule binaire : **le texte saisi (ex. « 3,40 ») n'est pas conservé tel quel** (utile pour CT5). |
| Lots | `finition` ∈ NOIR, GALVA, GPP (pas de valeur LAC ni BRUT) ; quantité en **pièces** (`quantite_initiale` entière) ; `longueur_m`. L'emplacement d'un lot se lit dans le registre des mouvements. |
| Transformateurs | `transformateur.type` ∈ GALVA, GPP, DEBIT, AUTRE : **un seul type par transformateur** (la base ne sait pas dire qu'un transformateur fait GALVA **et** GPP). Un bon de sortie par transformateur, rattaché à un bon de commande de transformation (qui peut porter une commande client). Aucun transformateur, aucun article dans la base (0 ligne). |
| Bon de sortie transformation | En-tête : numéro, transformateur, **bon de commande de transformation obligatoire**, date ; **aucun statut**, **aucun type de transformation**. Ligne : lot + quantité. Les tests créent le bon et son mouvement ensemble ; le mouvement physique porte la référence de la ligne du bon. |
| Articles (suite) | Aucune notion de version ; aucune demande de création ; `unite_valorisation_service` enregistre déjà l'historique des unités (immuable) mais ne contrôle pas le rôle. |
| Devises | `devis_ligne.devise` et `commande_ligne.devise` : une seule devise par ligne, **TND par défaut** ; `tests/helpers.py` crée des commandes en TND (contraire à K22 pour le prix de vente). |
| Audit | 12 actions (`core.audit.ACTIONS_VALIDES`, synchronisé par test avec le CHECK de la base). |
| Commande | `devis_id` obligatoire mais non unique ; `date_confirmation` obligatoire (même en BROUILLON) ; `quantite_originale` figée dès la création (trigger, quel que soit le statut) ; statuts BROUILLON / CONFIRMEE / SOLDEE / ANNULEE. |
| Devis | Statuts EN_COURS / CONFIRME / EXPIRE / ANNULE ; `poids_theorique_kg` obligatoire ; `pct_transformation` et `marge_pct` sans règle écrite. |
| Affectation | Types INITIALE / SUPPLEMENT (BR §1 : INITIALE = **quantité normale** ; les tests existants utilisent « INITIALE ») ; statut ACTIVE / CLOTUREE ; « non livrée » = active sans `mouvement_physique_id`. Plafond en base = quantité initiale du lot. `quantite_affectable_lot` ne compte que STOCK_GMC. L'affecté non sorti est calculé **par lot et par pool, jamais par emplacement**. |
| Réaffectation | Un trigger clôture **toute** l'affectation d'origine ; une origine ne peut être réaffectée qu'une fois. Un « reste » (ex. 70 sur 100) doit donc être recréé explicitement. |
| Livraison | `trg_bl_client_ligne_plafond` : livraison ≤ affecté non livré, par lot, ligne et type. |
| Transformation | Ligne de bon de sortie = lot + quantité, sans lien vers la ligne du bon de commande de transformation. Celle-ci ne porte que `finition_demandee`, un `format_debit` en texte libre (« 2x6m ») et `quantite_prevue`. Coupe 1 → N bloquée jusqu'à la 5.8. `enregistrer_retour_transformation` ignore les affectations. |
| Achats | Prix négocié par ligne de commande fournisseur, modifiable (aucun trigger) ; `v_approvisionnement_ligne` calcule sur la quantité originale. |
| Article | `masse_lineique_kg_m` obligatoire (> 0), sans trace de validation ; `pct_galva` facultatif ; aucun service de création d'article ; `unite_valorisation_service` (changement d'unité d'un article) ne vérifie que l'existence de l'utilisateur, alors que BR §11 et §16 en font une dérogation de Mohamed. |
| Client | Aucune protection contre la suppression, aucun audit. |

---

## 5. Architecture concernée

Architecture validée (M.1, M.2) :

- services Python indépendants de toute API HTTP ;
- dossiers `core/`, `repositories/` (SQL sans logique métier),
  `services/` (règles), `db/`, `tests/`.

Chaque opération métier s'exécute :

- dans **une seule transaction** (`db.connexion.transaction`) ;
- avec des erreurs françaises (`core.erreurs`) ;
- avec une ligne d'audit (`core.audit`) pour toute opération sensible.

Règles d'accès au stock et aux montants :

- le Stock Service reste la **seule voie d'écriture** dans
  `mouvement_stock` ; la 5.6 n'y écrit pas ;
- les montants sont des entiers en unité minimale, avec un seul arrondi
  final (`core/arrondi.py`) ;
- les unités sont obligatoires à la saisie (`core/unites.py`).

---

## 6. Modèle métier consolidé

### 6.1 Clients

- Création et modification réservées au SUPERADMIN (« Mohamed seul »
  dans le cahier) ; audit ; jamais supprimés [V cahier].
- Destination et incoterm par défaut, repris sur le devis [PROP C12].

### 6.2 Devis

- Préparé par un utilisateur ayant la permission (O5).
- **Taux de change de l'affaire** [V K5, O2, O3, X5, X7 ; **CT5**] :
  - saisi à la main par le commercial lors de la préparation ;
    convention **TND pour 1 EUR** (3,40 = 1 EUR pour 3,40 TND) ;
    TND → EUR = division par le taux [Y3, CT5] ;
  - historisé : **chaque saisie crée une nouvelle valeur**, jamais
    modifiée ni supprimée, avec auteur et date [CT5] ;
  - conservé **exactement tel que saisi**, jamais arrondi [CT5]. Choix
    technique qui en découle (signalé) : le texte saisi est enregistré à
    côté de la colonne numérique existante, et les calculs partent de ce
    texte (DB4) ;
  - **le devis pointe vers son taux** ; la commande et les avenants
    n'ont pas de taux propre : ils utilisent celui du devis [CT5] ;
  - figé pour l'affaire à la validation de l'offre, qui est le passage
    du devis à CONFIRMÉ ;
  - jamais remplacé à chaque avenant ;
  - modification exceptionnelle par le SUPERADMIN seul : **crée un
    nouveau taux, motif obligatoire, audit complet** [CT5]. Elle ne
    modifie pas la photo du devis confirmé (CT6).
  - **Y6 décidé le 02/10** : « tous les avenants futurs utilisent le même
    taux de change que le devis initial ». La modification
    exceptionnelle est historisée et auditée ; elle **ne modifie pas** le
    taux applicable aux avenants de l'affaire, **ne recalcule pas** les
    anciennes lignes ni les avenants déjà enregistrés. « Le taux utilisé
    par les avenants reste celui du snapshot du devis lors de sa
    validation. »
    - Lecture L-t (§22) : avec CT6 et Y6, je ne vois plus **aucun calcul
      de la 5.6** que le taux modifié changerait (ni la photo du devis,
      ni les lignes, ni les avenants). Il reste une trace datée, motivée
      et auditée, rattachée au devis ; le devis continue de pointer vers
      le taux de sa validation. À quoi ce taux modifié doit-il servir
      (par exemple en 5.10) ? Ton message ne le dit pas : je te pose la
      question.
    - Mise en œuvre [CT] : un avenant lit le taux dans la photo du devis
      validé, jamais dans le dernier taux enregistré.
    - *v8 : « son effet sur les avenants suivants : Y6, POINT MÉTIER
      ENCORE OUVERT » — **SUPERSEDED PAR Y6 (02/10)**. Libellé à
      confirmer : Y6-L (§22).*
- **Devises imposées** [V K22] : vente EUR, achat matière TND,
  transformation TND, transport EUR ; pré-remplissables, pas librement
  modifiables.
- **Prix de revient estimé** [V K4] : « (PRIX ACHAT MATIÈRE TND + PRIX
  TRANSFORMATION TND) / TAUX DE CHANGE PRÉVISIONNEL + TRANSPORT
  ESTIMATIF EUR ».
  - Exemple validé : 726,47 EUR.
  - **Transformation prévue : OUI / NON** sur chaque ligne de devis
    [CT7]. Si OUI : coût de transformation obligatoire, 0 seulement s'il
    est saisi, aucun zéro automatique. Si NON : aucun coût demandé.
  - Unité du coût de transformation conservée avec le coût : TND/t,
    TND/kg, TND/pièce, TND/ml ou montant total de la ligne [CT8].
  - **Calcul sur le total de la ligne** ; chaque prix garde son unité ;
    chaque quantité est appliquée dans sa propre unité ; **un seul
    arrondi final**, au centime EUR [CT6].
  - Le prix de revient unitaire affiché = total ÷ quantité (ex. 4,32 t →
    4 499,41 EUR ; 4 499,41 ÷ 4,32 = 1 041,53 EUR/t). Il sert à
    l'affichage et à l'analyse, jamais à refaire le total [CT6].
  - **Photo complète figée à la confirmation** [CT6] : achat,
    transformation, transport, poids, taux, résultat et autres valeurs du
    calcul (dont la valeur article validée et le taux GPP utilisés, CT3,
    CT4, CT20). Un changement ultérieur de masse, de taux ou de paramètre
    article ne modifie jamais un devis confirmé.
  - *v7 (§21, CT6 « proposé ») : « instantané enregistré à CONFIRMÉ »
    — désormais **VALIDÉ** par CT6.*
  - **Y3 validé** : le commercial saisit le taux en **TND pour 1 EUR**
    (ex. 3,40). Coût EUR = montant TND ÷ taux, calculé exactement, sans
    arrondi intermédiaire. Ta formule X5 « coût EUR = Y (TND) × R » s'y
    retrouve avec R = 1 ÷ taux saisi. R n'est jamais saisi ni arrondi.
- **Composants toujours séparés** [V P-KG-TR, 02/10] :
  - prix de vente → chiffre d'affaires ;
  - coût d'achat matière → coût matière ;
  - coût de transformation → coût transformation ;
  - transport → coût transport ;
  - total des trois coûts → **prix de revient** ;
  - chiffre d'affaires − prix de revient → **marge**.
  - Le transport est un composant du prix de revient ; il est
    indépendant du prix de vente et du coût d'achat, et ne modifie ni
    l'un, ni l'autre, ni la quantité commerciale.
  - C'est la formule K4, dont chaque composant est conservé à part dans
    la photo (CT6). Précision technique [CT] : les composants sont
    conservés en valeur exacte ; le seul arrondi reste celui du total
    (CT6). Un composant affiché arrondi peut donc différer d'un centime
    de la somme : c'est un affichage, jamais un second calcul.
  - Lecture L-q (§22) : une marge **prévisionnelle** (chiffre d'affaires
    prévu − prix de revient prévisionnel) peut être affichée en 5.6 ; la
    marge réelle reste en 5.10.
- Transport [V X2, Y2, P-KG-TR] : voir 6.7.
- Cycle EN_COURS → CONFIRMÉ / EXPIRÉ / ANNULÉ [V cahier] :
  - annulation par le SUPERADMIN (« Mohamed seul »), avec une cause
    parmi 8 [V cahier] ;
  - validité et prolongation [PROP C5].

### 6.3 Réservations commerciales — informatives (devis)

- Ce sont, à ma lecture (L-a), les « réservations commerciales » de ta
  liste du 01/10.
- Manuelles, optionnelles, informatives ; jamais un mouvement ni une
  affectation [V cahier]. Elles ne bloquent rien : elles sont distinctes
  des réservations de lots bruts (§6.3 bis), qui bloquent.
- Plafond = disponible réel à l'emplacement visé ; annulation, jamais
  suppression [PROP C6].

### 6.3 bis Réservation d'un lot brut pour une transformation [V Y1, Y1 bis, CT21, CT18 ; P-MULT, P-BST, P-RET]

- **Ta décision du 30/09** : « il peut être réservé dès la confirmation
  client et avec la transformation il sera automatiquement affecté ».
- **Tes précisions du 01/10 — toutes VALIDÉES** :
  - **Y1 bis (a) — bloquante** : la réservation bloque réellement le
    disponible du lot. Exemple : 100 barres physiques, 25 réservées →
    disponible commercial 75, stock physique toujours 100. Aucun
    mouvement. Personne d'autre ne peut réserver ni affecter cette
    quantité.
  - **Y1 bis (b) — conversion au BON DE SORTIE TRANSFORMATION (BST)** :
    à l'établissement du BST, le système compare le résultat prévu du
    BST avec la réservation. Identique → conversion automatique.
    Différent → BST refusé. Aucun choix automatique : le système reprend
    exactement ce qui a été réservé.
  - **Y1 bis (c)** : « confirmation client » = **commande client
    confirmée**. La réservation peut être créée dès la confirmation de
    la commande.
  - **Y1 bis (d)** : **seul le SUPERADMIN** peut réserver.
  - **Mécanisme** : la réservation initiale reste conservée dans
    l'historique ; à la conversion, une **nouvelle affectation liée** est
    créée ; la relation réservation → affectation est traçable.
- **Ce que contient une réservation** [CT21] :
  - le lot brut ;
  - la ligne de commande ;
  - la quantité réservée, en **pièces du lot brut** ;
  - le résultat attendu (finition, longueur) ;
  - la quantité attendue, en **pièces de la ligne** ;
  - [P-MULT] la quantité qui couvre la ligne (ex. 49) et, par différence,
    le **reliquat de conversion** (ex. 1) ;
  - le type de transformation prévu : GALVANISATION ou GPP [P-RET] ;
  - l'auteur et la date ;
  - un statut : **ACTIVE**, **CONVERTIE**, **LIBÉRÉE**.
- **Contrôles** [CT21] :
  - commande **confirmée** ;
  - **SUPERADMIN** ;
  - **lot brut**. Ma lecture (L-b) : lot de finition NOIR. FACT : le
    schéma ne connaît que NOIR, GALVA et GPP ; LAC = NOIR (C13) ;
  - lot **chez GMC** (pas chez un transformateur : ce cas relève de X3,
    §6.11) ;
  - **même article** ;
  - **transformation possible** [V **P-RET**, 02/10] : seulement une
    **GALVANISATION** (NOIR/LAC → GALVA) ou un **GPP** (NOIR/LAC → GPP),
    avec ou sans longueur ramenée à un sous-multiple exact (D1, K2).
    Une réservation pour une **coupe seule** (NOIR 12 m → NOIR 6 m) est
    refusée dans cette analyse, parce que la découpe n'est pas une
    transformation du périmètre actuel (P-RET). C'est une **application
    provisoire de ma proposition** : ce que devient une ligne NOIR 6 m
    servie par des barres de 12 m reste ouvert (**Q-COUPE**, §22) ;
    - *v8 : « une réservation pour une coupe seule n'est pas tranchée :
      P-RET » — **SUPERSEDED PAR P-RET (02/10)**.*
  - **longueur compatible selon multiple exact** : longueur du lot =
    n × longueur de la ligne, n entier ;
  - **quantité attendue compatible avec la quantité réservée** : avec ta
    règle « 12 m → 6 m … cette conversion doit rester exacte »,
    quantité attendue = quantité réservée × n, exactement (25 × 12 m →
    50 × 6 m ; 49 ou 51 **pièces attendues** sont refusés) ;
  - [V **P-MULT**, 02/10] la quantité qui **couvre la ligne** peut être
    inférieure à la quantité attendue : besoin de 49 × 6 m → 25 × 12 m
    réservées (calcul **par excès**) → 50 × 6 m attendues → 49 pour la
    ligne, **1 de reliquat de conversion**. Lecture L-n (§22) : « par
    excès » = la barre entière supérieure, pas davantage ; le reliquat
    est donc toujours inférieur à n pièces ;
  - ligne **GALVA ou GPP** : vendue uniquement en **KG ou TONNE** (CT7) ;
  - quantité réservée ≤ **disponible réel** du lot chez GMC = stock
    physique − affecté − réservé − engagé dans un BST préparé (L-k).
- **Effets** [CT21] :
  - aucun mouvement, aucun nouveau lot, emplacement inchangé ;
  - disponible commercial du lot diminué, en **pièces du lot** (25
    barres) ;
  - aucune autre affectation ni réservation sur la quantité bloquée ;
  - pendant la réservation, cette quantité ne peut être **ni envoyée vers
    une autre transformation, ni vendue brute**.
- **Conversion au BST** [Y1 bis (b), mécanisme, CT18 ; **P-BST**,
  02/10] :
  - elle a lieu **en 5.6**, quand le BST est **préparé** (§6.11 bis) ;
    aucun mouvement physique, aucun lot transformé ;
  - résultat attendu du BST comparé à celui de la réservation :
    identique → conversion ; différent → BST refusé ;
  - la réservation passe à **CONVERTIE** et reste dans l'historique ;
  - une **nouvelle allocation liée au BST** est créée : même lot, même
    ligne de commande, résultat attendu, quantité qui couvre la ligne
    (49 dans l'exemple P-MULT), avec le lien vers la réservation ;
  - le reliquat de conversion (1 dans l'exemple) n'est affecté à
    personne : **le système ne choisit jamais** [P-MULT] ;
  - audit CONVERSION_RESERVATION_AFFECTATION.
  - Lectures à confirmer (§22) : **L-r** — la ligne du BST désigne la
    réservation qu'elle exécute ; **L-s** — une exécution partielle
    (moins que la quantité réservée) est refusée, puisque « le système
    reprend exactement ce qui a été réservé ».
  - *v8, P-BST (iii) « la conversion n'a lieu qu'à l'établissement du
    BST » : confirmé par P-BST (02/10), l'établissement étant la
    préparation en 5.6. P-BST (iv) « elle précède le contrôle du
    garde-fou dans la même opération » — **SUPERSEDED PAR P-BST
    (02/10)** : la préparation ne contient plus aucun envoi physique.*
- **Unités** [CT, signalé] : le blocage du lot se compte en **pièces du
  lot brut** (25 barres de 12 m) ; la couverture de la ligne, en **pièces
  de la ligne** (50 barres de 6 m). L'affectation créée à la conversion
  est rattachée au résultat attendu de la ligne du BST et plafonnée par
  sa quantité attendue, comme toute affectation X3 (option A de la v5 :
  « plafonnée par la quantité attendue moins ce qui est déjà affecté »).
- **Reliquat de conversion** [V **P-MULT**, 02/10] : la pièce restante
  (1 × 6 m) « peut être vendue ultérieurement à une autre affaire OU
  rester en stock GMC » ; « le système ne choisit jamais automatiquement
  entre ces deux possibilités » ; c'est « un stock GMC réel, traçable et
  disponible », pas une perte.
  - Lecture L-u (§22), pour accorder « stock réel et disponible » avec
    « rien n'est vendable avant la réception » (O4, K1, P-BST) :
    - à la réservation, le reliquat n'est qu'un **nombre calculé** (1) ;
      les 25 barres sont bloquées en entier et le reliquat ne peut être
      attribué à personne ;
    - une fois le BST préparé, c'est une **quantité attendue non
      affectée** de la ligne du BST : le SUPERADMIN peut l'affecter à une
      autre affaire (X3), par une décision explicite ;
    - à la réception (5.8), il devient une pièce physique du lot
      transformé ; non affecté, il est alors du stock GMC disponible.
  - Ce n'est ni une chute (pas de perte), ni un « reliquat de commande »
    (§6.17) : deux notions différentes, deux noms différents.
  - *v8 : « quantité de ligne qui n'est pas un multiple exact : P-MULT »
    — **SUPERSEDED PAR P-MULT (02/10)** ; les options (b) et (c) de la
    v8 ne sont pas retenues.*
- **Type de l'affectation créée** (lecture L-c, §22) : CT17 fixe le type
  à la création et interdit toute requalification. Ma proposition : le
  type (NORMALE ou SUPPLÉMENT + motif) est fixé **à la réservation**,
  compte dans le cumul de la ligne dès ce moment, et est repris tel quel
  à la conversion.
- **Libération** [CT21] — statut **LIBÉRÉE**, audit
  LIBERATION_AFFECTATION :
  - annulation de la commande ;
  - clôture avec reliquat (la réservation est listée, §6.17) ;
  - diminution de commande, avec choix explicite (N7) ;
  - libération par le SUPERADMIN, **motif obligatoire**.
  - CT21 ne dit rien du déplacement d'une réservation vers une autre
    commande. Ma lecture (L-i, §22) : pas de déplacement direct ; on la
    libère (avec motif) puis on en crée une nouvelle.
- **Audit** [CT21] : RESERVATION_LOT_BRUT ;
  CONVERSION_RESERVATION_AFFECTATION ; LIBERATION_AFFECTATION.
- **Situation** [CT21] : « réservé pour transformation », par ligne et par
  lot ; **disponible GMC = stock physique − affecté − réservé** [CT21],
  moins la quantité engagée dans un BST préparé (L-k) (§6.16).
- **Phases** [V P-BST, 02/10] : création, contrôles, blocage,
  libération, situation, **préparation du BST, comparaison et
  conversion** en 5.6. La sortie physique, le mouvement, la
  transformation, le lot transformé et la réception sont en 5.8.
  - *v8 : « l'établissement du BST est en 5.8 … P-BST » — **SUPERSEDED
    PAR P-BST (02/10)**.*
- **Lot brut non réservé** : signal « utilisable après transformation »,
  **informatif seulement** [CT13] : ni réservation, ni affectation, ni
  mouvement, ni mise en vente du produit transformé.
- **Historique (v7)** :
  - ma proposition v7 (a) à (g) : (a), (c) et (d) **validés** tels
    quels ; (b) **validé** « au bon de sortie » ; l'autre possibilité
    v7 « à la réception (5.8) » est **SUPERSEDED PAR Y1 bis (b)** ;
    (e), (f) et (g) sont repris dans CT21 ;
  - la v7 disait que la réservation « devient » une affectation et
    laissait ouvert « même ligne ou ligne liée » (CT21 v7) : **SUPERSEDED
    PAR Y1 bis (mécanisme)** — la réservation est conservée, une
    affectation **liée** est créée ;
  - la v7 disait « dès la confirmation du client » : précisé par
    **Y1 bis (c)** (commande confirmée).

### 6.4 Commandes clients

- Un devis → une commande [V cahier].
- Commande créée seulement depuis un devis CONFIRMÉ, avec les détails
  de C1 [PROP C1].
- Cycle BROUILLON → CONFIRMÉE → SOLDÉE [V cahier] :
  - annulation d'une commande confirmée par le SUPERADMIN (« Mohamed
    seul »), refusée si déjà livrée [V cahier] ;
  - clôture avec reliquat (6.17).
- Date de confirmation = date de confirmation par le client [PROP C14].
  FACT : la colonne est obligatoire même en brouillon.
- Aucun taux propre : la commande utilise le taux du devis [CT5].
- Coûts estimés (achat, transformation) **recopiés du devis** [CT9].
- Dès que la commande est **CONFIRMÉE**, le SUPERADMIN peut réserver un
  lot brut pour une de ses lignes [Y1 bis (c), (d)].
- Interventions exceptionnelles du SUPERADMIN sur une commande
  confirmée : par la table d'avenants [CT10] (§6.6).

### 6.5 Lignes de commande

- Origine **DEVIS** (ligne issue du devis) ou **AVENANT** (nouvel article,
  cas 2) [V K21, O1].
- [CT16 VALIDÉ] Ligne ajoutée par avenant : marquée **AVENANT**, quantité
  initiale **0**, quantité venant de l'avenant ; la situation montre
  « 0 initial + X ajouté par avenant » ; l'avenant permet de retrouver
  l'origine de la ligne.
- Chaque ligne porte : unité de vente, **poids, unité et origine du
  poids** [CT20], prix de vente **en EUR** (FACT : TND par défaut
  aujourd'hui), transport, transformation prévue OUI/NON et son coût
  [CT7, CT8], coûts estimés recopiés du devis [V K22 ; CT9].
- Aucun taux propre à la ligne : le taux est celui de l'affaire [V O2,
  X7].

### 6.6 Avenants [V K9, K21, O1, D4]

- Toute modification après validation de la commande = avenant,
  **SUPERADMIN** [V K9, X4].
- [CT10 VALIDÉ] **Une seule table d'avenants, append-only** : jamais de
  modification ni de suppression d'un avenant historique.
- Contenu [CT10] : ancienne valeur, nouvelle valeur, motif, auteur,
  date/heure, **impact quantitatif avant/après**, **impact financier
  avant/après**.
- La même table sert aux **interventions exceptionnelles du SUPERADMIN
  sur une commande confirmée** [CT10], dont la correction d'une erreur
  de prix (§6.7).
- **Aucun avenant de prix** après confirmation [CT10, Y5] : le prix ne se
  renégocie pas. La correction d'une **erreur** de prix (§6.7) est
  enregistrée dans le même registre, mais ce n'est pas un avenant de
  prix.
- Ligne vendue au poids (KG ou TONNE) : un avenant de quantité
  **recalcule le poids** selon la méthode validée ; **aucune saisie libre
  du nouveau poids** [CT10]. Ma lecture, cohérente avec CT3, CT4, CT6 et
  K21 cas 1 : pour une ligne existante, le recalcul reprend la méthode,
  la valeur et le taux GPP figés dans la photo de la ligne.
- *v7 (§21) : CT10 servait « aussi pour une intervention sur devis
  CONFIRMÉ ».* Ta décision CT10 du 01/10 nomme la commande confirmée,
  sans exclure le devis. Ma lecture (L-j, §22) : la table d'avenants
  sert à la commande ; sur un devis confirmé, la seule intervention
  définie est la modification exceptionnelle du taux (CT5 : nouveau
  taux, motif, audit).
- **Taux des avenants** [V O2, X7, CT5, **Y6 (02/10)**] : tous les
  avenants utilisent le taux de la photo du devis validé, même après une
  modification exceptionnelle du taux par le SUPERADMIN ; aucun avenant
  déjà enregistré n'est recalculé.
- **Cas 1** — article déjà dans la première version : règles existantes
  de la ligne, sans refaire inutilement la logique de la commande.
- **Cas 2** — nouvel article : nouvelle ligne complète (article,
  finition, longueur, unité, quantité, poids, prix, coût matière, coût de
  transformation, transport, **taux de l'affaire**, autres données).
  - Coûts estimés **saisis dans l'avenant**, jamais pré-remplis depuis un
    ancien achat [CT9].
  - Valeur article validée et taux GPP utilisés pour cette nouvelle
    ligne : ma lecture (L-e, §22) = ceux en vigueur à la date de
    l'avenant, figés dans l'avenant.
- L'ancienne commande reste historiquement intacte.

### 6.7 Prix de vente et transport

- Prix de vente en **EUR** [V D3, K22].
- Ligne identique (article, finition, longueur, unité de vente, autres
  caractéristiques nécessaires) → prix applicable de la commande ; une
  nouvelle ligne ne modifie jamais automatiquement un prix existant
  [V K10].
- **Y5** [V] : « pas de renégociation de prix de vente. Commande
  confirmée prix de vente confirmé. La renégociation sera avant validation
  si il existe. »
  - Le prix de vente se négocie **au stade du devis** (EN_COURS). Chaque
    changement est tracé (MODIFICATION_PRIX).
  - À la confirmation, il est **figé**. Aucune renégociation n'est
    possible ensuite, pas même par avenant.
  - **X1 — SUPERSEDED PAR Y5** : « le nouveau prix s'applique à toutes
    les lignes identiques » est sans objet, puisqu'il n'y a plus de
    nouveau prix après confirmation. **K10, partie « renégociation »**
    (« nouveau prix historisé ; date d'effet ») — **SUPERSEDED PAR Y5**.
    **O8, phrase « si une nouvelle négociation commerciale avec le client
    est nécessaire… »** — **SUPERSEDED PAR Y5**.
  - Ce qui reste de K10 : une nouvelle ligne identique ajoutée par
    avenant reprend le prix confirmé ; aucune ligne ne modifie le prix
    d'une autre.
  - Ma lecture de K21 cas 2 : le prix d'un **nouvel article** ajouté par
    avenant est fixé dans l'avenant. Ce n'est pas une renégociation d'un
    prix déjà confirmé.
  - **Correction d'une erreur de prix après confirmation — Y5 bis réglé
    par CT10** : correction par le **SUPERADMIN**, **motif obligatoire**,
    **audit complet** ; « ce n'est PAS une nouvelle négociation
    commerciale ».
    - Mise en œuvre [CT, signalé] : le prix confirmé de la ligne n'est
      jamais réécrit (DB11 reste strict, sans exception) ; la correction
      est un enregistrement de la table d'avenants, de nature
      « correction d'une erreur de prix (SUPERADMIN) », avec ancienne et
      nouvelle valeur et impact financier ; audit
      CORRECTION_ERREUR_PRIX. Le **prix en vigueur** se calcule : dernier
      prix corrigé, sinon prix confirmé (comme V = O + A).
    - Option (a) de la v7 (« aucune modification ; annulation puis
      nouveau devis ») : **non retenue** (SUPERSEDED PAR CT10).
- Le prix de vente confirmé n'est jamais modifié parce qu'un coût d'achat
  change [V O8].
- Une autre commande peut avoir un autre prix [V N8].
- **Transport** [V X2, Y2] :
  - saisi dans le devis en **EUR/T** ;
  - ligne vendue en TONNE : transport EUR = EUR/T × quantité en tonnes
    (ex. 4,32 t × 85,50 = 369,36 EUR) ;
  - ligne vendue en **KG** [V **P-KG-TR**, 02/10] : le système convertit
    automatiquement **KG ÷ 1 000 = tonnes**, puis **tonnes × EUR/T =
    transport prévisionnel en EUR**. Exemple : 5 000 kg, 100 EUR/T →
    5 t → **500 EUR**. Ce calcul ne concerne que le transport : il ne
    modifie ni le prix de vente, ni le prix d'achat, ni la quantité
    commerciale. La conversion kg → t est exacte et affichée ;
    - *v8 : « non tranché, P-KG-TR » ; option (b) « montant total saisi
      pour une ligne en KG » — **SUPERSEDED PAR P-KG-TR (02/10)**.*
  - unité hors poids (PIÈCE, ML, M², autre) : **aucun poids implicite**,
    aucune conversion cachée en tonnes. Le **montant total estimé** en
    EUR est saisi manuellement sur la **ligne du devis**, en même temps
    que le **poids de la ligne** (Y2), qui est un poids DÉCLARÉ, possible
    seulement en NOIR/LAC (CT20). La saisie est obligatoire ; 0 seulement
    s'il est saisi (BR §19). « Pour les autres unités de vente, ne pas
    inventer une conversion en tonnes » [P-KG-TR] ;
  - le transport prévisionnel entre dans le prix de revient prévisionnel
    de l'affaire ; le transport **réel** final sera traité plus tard et
    restera distinct du prévisionnel [P-KG-TR, Y2].
  - Plus tard (5.9/5.10) [V Y2] : le montant **final** du transport est
    saisi après facturation, puis réparti **au poids** entre les articles
    pour calculer la marge par article, dans les résultats et le tableau
    de bord. En 5.6, cela impose seulement de conserver un poids pour
    chaque ligne, avec son unité et son origine (CALCULÉ ou DÉCLARÉ)
    [CT20].

### 6.8 Quantités [V N6, K3, K13, K15, O1] ; formules [CT]

| Grandeur | Définition |
|---|---|
| O — originale | Fixe dans l'historique, jamais écrasée [V] ; figée à la confirmation, libre en brouillon [PROP C1] ; 0 pour une ligne créée par avenant [CT16] |
| A — avenants | Ajouts et diminutions, historiquement identifiables [V O1] |
| V — en vigueur | O + A (100 + 20 = 120) ; les 100 ne deviennent jamais 120 [V] |
| Normal | Toute quantité jusqu'à V, avenants compris : **quantité normale** [V O1]. Cumul normal (CT17) = quantité affectée en NORMALE, livrée ou non, hors affectations libérées ou réaffectées [CT] ; + quantité **qui couvre la ligne** dans les réservations actives (49 dans l'exemple P-MULT, pas les 50 pièces attendues), selon la lecture L-c |
| Supplément | Quantité réellement livrée/facturée **au-delà de V** [V O1, O8 §4] ; reste un supplément [V X9] |
| Livré | Lignes de BL (5.9), normal et supplément séparés |
| Reste à livrer | V − livré normal [CT] |
| Réservé pour transformation | Par ligne : quantité qui couvre la ligne (pièces de la ligne) dans les réservations ACTIVES [CT21, P-MULT] ; ex. 49, même si 50 pièces sont attendues. Par lot : quantité réservée (pièces du lot), qui entre dans le disponible du lot |
| Reliquat de conversion | Pièces attendues − pièces qui couvrent la ligne (ex. 50 − 49 = 1) [V P-MULT]. Jamais attribué automatiquement ; stock GMC réel après réception (5.8) ; ni chute, ni reliquat de commande |
| Barres à approvisionner | Pour un besoin exprimé en longueur plus courte : besoin ÷ n, **arrondi par excès** (49 ÷ 2 → 25 barres de 12 m) [V P-MULT] ; l'achat reste en 5.7 |
| À approvisionner | V − (affecté normal actif non livré + **réservé pour transformation** + livré normal) [CT] ; alimente la 5.7 (« manques → approvisionnement », cahier). *v7 : sans le réservé — complété en v8, sinon un lot brut réservé serait aussi racheté.* |
| Reliquat (de commande) | V − livré normal au moment d'une clôture avec reliquat [V X6 ; CT19] |

- Diminution autorisée, jamais sous le livré [V K13].
- Une diminution sous l'affecté exige la désignation **explicite** des
  affectations à réduire ou libérer [V N7].
- La marchandise libérée reste stock GMC disponible selon son emplacement
  et son état [V N7, K13].

### 6.9 Poids [V N1 à N4, K6, K7, K18 à K20, O7, X8, Y2, Y4 ; CT3, CT4, CT7, CT20]

- **Vente au poids = KG ou TONNE** [CT20, règles du 01/10] : poids
  **calculé** par la méthode validée de l'article (CT3) ; aucune saisie
  manuelle arbitraire.
  - *v7 : « Vente en TONNE (et en KG si Y4 bis le confirme) » —
    **SUPERSEDED PAR CT20** et tes règles « GALVA / GPP » du 01/10 : le KG
    est une vente au poids, comme la tonne.*
  - Valeur non validée → la vente au poids est refusée, avec la demande
    de faire valider la valeur [CT3 : « une vente nécessitant un poids
    calculé ne peut utiliser une masse non validée »].
  - GALVA : masse de base × (1 + % GALVA validé ÷ 100).
  - GPP : masse de base × (1 + taux GPP global ÷ 100), soit × 1,02
    aujourd'hui [CT4].
  - GALVA et GPP ne se cumulent jamais.
  - Exemples : 48,6 / 51,516 / 49,572 kg ; 100 barres GALVA = 5,1516 t.
  - Méthode ou valeur manquante → le système demande de compléter le
    référentiel [N2, K18].
- **Valeurs article validées** [CT3 VALIDÉ] :
  - historique **dédié et jamais modifié** ; chaque validation conserve :
    article, paramètre, méthode de poids, valeur, unité, % GALVA s'il est
    concerné, **sources affichées au moment de la décision**, validé par,
    date/heure, motif ;
  - la dernière validation est la valeur en vigueur ; les anciennes
    restent consultables ;
  - méthodes : kg/ml, kg/m², kg/pièce, autre méthode validée ; **liste
    extensible** ;
  - **seul le SUPERADMIN** valide ;
  - une nouvelle validation ne modifie **jamais** un devis ou une
    commande déjà confirmés.
  - **La masse actuelle de la fiche article n'est pas validée** : c'est
    une « **valeur MV à vérifier** », affichée comme source, jamais
    utilisée pour une vente au poids.
  - Ma lecture (L-h, §22) : le % GALVA actuellement porté par la fiche
    (`article.pct_galva`) est lui aussi une simple source à vérifier
    (CT3 : « x % = valeur explicitement validée »). FACT : la base ne
    contient aucun article.
- **% GALVA** [CT3, K20] : **non renseigné** (état distinct, jamais lu
  comme 0) ; **0 %** explicitement validé ; **x %** explicitement validé.
- **Réglage GPP** [CT4 VALIDÉ, option A] : un réglage **unique** en base,
  actuellement **2 %**, commun à tous les articles ; modifiable par le
  SUPERADMIN seul ; avec date d'effet ; historisé ; sans nouvelle version
  du logiciel. **Pas de % GPP par article.** Les devis et commandes
  confirmés gardent le taux utilisé à leur confirmation (photo CT6).
- **GALVA et GPP suivent le même parcours** de transformation ; seule la
  règle de pourcentage diffère [CT4] : GALVA = % article validé ; GPP =
  taux global.
- **Hors poids** (PIÈCE, ML, M², autre unité autorisée) — **NOIR/LAC
  seulement** [CT20, CT7] :
  - poids **déclaré obligatoire**, saisi sur la ligne du devis (Y2) =
    **poids final** de la commande ; origine DÉCLARÉ ;
  - jamais majoré (O7) ;
  - la quantité et l'unité de vente restent les données commerciales
    principales ;
  - pas d'intervention automatique sur le dossier à cause du seul poids.
  - *v7 : « aucun +2 % GPP réappliqué ; pas de GALVA hors poids (Y4) » —
    la partie GPP est **SUPERSEDED PAR ta précision GPP du 30/09 (23 h 21)
    et CT7, CT20** : il n'existe plus de GPP hors poids.*
- Usages du poids déclaré [V O7, « notamment »] :
  - le poids final de la commande ;
  - le **prix de revient estimatif** : un prix au poids se multiplie par
    le poids déclaré, par exemple 2 800,5 TND/t × 0,5 t = 1 400,25 TND ;
  - le transport « lorsque celui-ci est exprimé en EUR/T » : **remplacé
    par X2 et Y2** (hors poids, montant total saisi, aucune conversion) ;
  - plus tard (5.9/5.10), la **répartition au poids du transport réel**
    pour la marge par article (Y2).
- **Origine du poids** [CT20 VALIDÉ] : chaque ligne conserve poids, unité
  et origine.
  - **CALCULÉ** : méthode, valeur utilisée, % GALVA si applicable, règle
    GPP (taux) si applicable.
  - **DÉCLARÉ** : seulement quand une déclaration manuelle est permise,
    c'est-à-dire aujourd'hui **NOIR/LAC hors vente au poids**.
  - GALVA et GPP : vente uniquement en KG ou TONNE, donc poids toujours
    calculé.
  - À la confirmation, le poids utilisé est **figé dans la photo** du
    calcul (CT6) [V cahier : poids de vente figé à la confirmation].
- **Y4** [V] : « la galvanisation sera effectuée que sur un article dont
  son unité de vente soit kg ou tonne ».
  - Une ligne GALVA vendue en PIÈCE, ML, M² ou autre unité est
    **refusée**. **Il en va de même pour une ligne GPP** (précision du
    30/09, CT7).
  - **Y4 bis réglé** (§0 bis) : (i) contrôle sur l'**unité de vente de la
    ligne** (CT7) ; (ii) le **KG** est une vente au poids (CT20) ; (iii)
    le mécanisme de validation des valeurs article est en 5.6 (CT3) ;
    la création d'article et le changement d'unité sont décidés par
    **P-ART** (02/10, §6.21).
  - *v7 : « Précisions à confirmer (Y4 bis) : unité de la ligne ou de
    l'article ; la vente en KG se traite-t-elle comme la tonne ? » —
    **SUPERSEDED PAR CT7 et CT20**.*
  - Un envoi en galvanisation **ou en GPP** ne concerne que ces articles
    vendus au poids. *(v8 : « pour la 5.8 » — précisé par P-BST : voir
    §6.11 bis.)*
- **X8 = B** [V] : le % GALVA reste obligatoire dans la référence article
  pour vendre en GALVA (option (b) de la v5 : « toute vente GALVA exige
  un % renseigné, même hors tonne, pour compléter le référentiel, sans
  l'appliquer »).
  - Avec Y4, il n'y a plus de vente GALVA hors poids. La partie « hors
    tonne » de X8 ne se présente plus (**SUPERSEDED PAR Y4**, sans
    objet). Le % reste obligatoire pour toute vente GALVA ; il doit être
    **validé** (CT3).
  - Les trois états (défini, 0 % = brut, non renseigné) sont conservés.
  - Un % non renseigné n'est jamais converti en 0 [V K20, CT3].
  - Le référentiel se construit progressivement (K7) ; une vente GALVA
    sur un article sans % validé déclenche la demande de compléter.
- **GPP** — *v7 : « pas concerné par Y4. Une vente GPP hors poids reste
  possible, avec le poids déclaré tel quel, sans +2 % (O7). »* —
  **SUPERSEDED PAR ta précision du 30/09 (23 h 21) : « le GPP c'est
  exactement similaire à la galvanisation dans le process sauf % est
  fixe », puis CT4, CT7 et CT20.** Le GPP suit le même parcours que le
  GALVA ; vente en KG ou TONNE seulement ; poids toujours calculé ; une
  ligne GPP hors poids est refusée. C'était une erreur de ma part dans
  la v7.
- Référentiel : comparer, présenter, ne jamais choisir silencieusement,
  validation SUPERADMIN, historique [V N1, K7 ; CT3]. Mécanisme de
  validation en 5.6 (CT3) ; création d'article, versions et changement
  d'unité : **P-ART décidé le 02/10** (§6.21). Une validation CT3 d'une
  masse ou d'un % GALVA est une « modification à impact métier » : elle
  crée une nouvelle version de l'article (P-ART).

### 6.10 Affectations commerciales [V D5, N10, N11, N13, K11, K12]

- Par le **SUPERADMIN seul** pour le moment [V N10] ; choix **manuel**
  du lot ; aucun FIFO ; le système ne choisit jamais.
- Une affectation n'est **jamais un mouvement physique** et ne change
  jamais la localisation.
- Contrôles :
  - disponibilité réelle par (lot, emplacement) = stock physique −
    affecté − **réservé** [CT21] − quantité engagée dans un BST préparé
    et non encore sorti (lecture L-k) ;
  - aucune double affectation incompatible ;
  - aucune allocation au-delà du disponible ;
  - aucun mouvement incompatible avec l'affecté.
- **Garde-fou [CT11 VALIDÉ]** : aucun mouvement physique ne fait passer
  le stock disponible sous la quantité **affectée ou bloquée**
  (réservations comprises). Contrôle dans l'application **et** dans la
  base. Concerne notamment l'envoi en transformation, la chute, la
  correction et le retour. Le contrôle des livraisons sera complété en
  5.9.
- **Type fixé à la création** [CT17] : NORMALE ou SUPPLÉMENT (§6.13).
- Valorisation (5.10) : quantité normale → coût réel du lot ; supplément
  → CMP à la sortie [V BR §1].
- **O8 cas A** [V] : un ajout couvert par le stock GMC disponible → lot
  existant affecté manuellement, coût réel de ce lot, aucune commande
  fournisseur. Lot, allocation, utilisateur et date sont tracés.
  - Ma lecture v7 (**L1**) : **l'affectation** utilisée dans ce cas est
    celle de la 5.6 ; le choix « stock disponible → lot existant /
    indisponible → achat » et tout le côté fournisseur restent en 5.7.
    **L1 est réglé par ton périmètre du 01/10** (« 5.6 : … affectations »
    ; « 5.7 = achats / commandes fournisseurs / réceptions »).

### 6.11 Affectations sur marchandise chez un transformateur [V O4, X3]

- **X3 = A.** Tes mots : l'affectation commerciale est créée « en
  Phase 5.6 : sur le besoin client identifié ; sur la marchandise
  identifiée ; même lorsque cette marchandise a déjà été envoyée au
  transformateur » (100 × 12 m NOIR au galvaniseur ; 60 affectées).
- **Option A de la v5, que tu as choisie** (citée) :
  - « Au bon de sortie, l'utilisateur saisit pour chaque ligne le
    résultat prévu : finition, longueur, quantité attendue en pièces.
    Tout est saisi, rien n'est déduit du texte « 2x6m ». »
  - « L'affectation commerciale se fait dans l'état prévu, en pièces
    attendues, plafonnée par la quantité attendue moins ce qui est déjà
    affecté. »
  - « Toute livraison ou vente est refusée avant réception. »
  - « Le transfert de l'affectation vers le lot transformé à la
    réception, et les écarts … relèvent de la 5.8. »
  - « Jusque-là, le retour d'un lot portant une telle affectation est
    refusé avec un message clair. »
  - IMPACT annoncé : colonnes sur `bon_sortie_transformation_ligne` et
    `affectation_stock` dans la 0021.

  La v6 reprend cette option **telle quelle** : DB12, DB17 et CT18. Le
  premier jet de la v6 l'avait simplifiée ; c'est corrigé.
- **CT18 VALIDÉ (01/10), avec ta précision** :
  - le résultat attendu est renseigné **au moment de l'établissement du
    BON DE SORTIE TRANSFORMATION** ;
  - exemple : commande 50 IPE120 GALVA × 6 m ; stock GMC 25 IPE120 brut ×
    12 m ; au BST : article de départ IPE120, état de départ BRUT,
    quantité de départ 25 barres, longueur de départ 12 m,
    transformateur galvanisateur, état de retour attendu GALVA, longueur
    de retour attendue 6 m, quantité de retour attendue 50 pièces ;
  - **l'état de retour n'est pas libre** : galvanisateur → retour
    **GALVA** obligatoire ; transformation GPP → retour **GPP**
    obligatoire ; même parcours pour GALVA et GPP.
  - **P-RET décidé le 02/10** : GMC n'a que deux transformations,
    GALVANISATION et GPP ; GALVANISATION → GALVA automatiquement ; GPP →
    GPP automatiquement ; l'utilisateur ne peut pas choisir une autre
    finition ; un même transformateur peut avoir les deux capacités ;
    **le type de transformation choisi dans le BST** détermine le
    résultat attendu (§6.11 bis).
    - *v8 : « ma lecture : galvanisateur = transformateur de type
      GALVA ; « transformation GPP » = transformateur de type GPP. Pour
      DEBIT et AUTRE … P-RET » — **SUPERSEDED PAR P-RET (02/10)** : ce
      n'est pas le type du transformateur qui décide, c'est le type de
      transformation du BST ; DEBIT et AUTRE sont hors périmètre.*
  - longueur et quantité attendues définies au BST selon la
    transformation prévue et les règles de conversion, **exactement**
    (25 × 12 m → 50 × 6 m) ;
  - le résultat attendu doit correspondre à une éventuelle réservation
    préalable (sinon BST refusé, Y1 bis (b)) ;
  - **figé dès qu'une affectation commerciale s'y rattache** ;
  - transformation réelle, lot transformé et réception transformée en
    5.8 ; livraison interdite avant réception du lot transformé (5.9).
  - *v8 : « contrôle proposé (P-RET (iv)) : état de retour = finition
    demandée de la ligne du bon de commande de transformation » — non
    repris : ta décision P-RET ne le prévoit pas, et la place du bon de
    commande de transformation est une question ouverte (**Q-BCT**,
    §22).*
- Option A de la v5, point « Au bon de sortie, l'utilisateur saisit … le
  résultat prévu » : **confirmé par CT18**.
- La 5.6 **ne crée pas** le lot transformé et **ne crée aucun
  mouvement**.
- En **5.8**, à la réception de transformation :
  - le lot résultant est créé ;
  - l'affectation existante lui est **rattachée** ;
  - la traçabilité besoin client → affectation → lot initial → lot
    résultant est conservée.
- Vendable dans l'état transformé seulement après bon de réception →
  réception GMC → lot transformé [V O4, K1].
- Quatre notions distinctes [V O4] : localisation physique,
  transformation prévue (résultat déclaré sur la ligne du bon de sortie),
  affectation commerciale, disponibilité commerciale réelle.
- FACT : aucun code ne crée encore de bon de sortie. (P-BST : la 5.6
  codera sa préparation, la 5.8 son exécution physique.)
  - *v7 : « En 5.6, le résultat prévu se déclare sur une ligne de bon de
    sortie existante, par une fonction SUPERADMIN tracée [CT18]. En 5.8,
    il se saisira à la création du bon. »* — **SUPERSEDED PAR CT18
    (01/10)** : le résultat attendu est renseigné **à l'établissement du
    BST**, pas déclaré après coup. **P-BST décidé le 02/10** : cet
    établissement est la **préparation commerciale** du BST, en 5.6
    (§6.11 bis) ; la 5.8 exécute la sortie physique.
- Cohérence du résultat attendu [V D1 ; CT18, CT21] : même article ;
  longueur égale ou sous-multiple exact (12 m → 6 m) ; **quantité attendue
  = quantité envoyée × (longueur d'origine ÷ longueur attendue),
  exactement**. Tout autre cas est refusé.
  - *v7 : « quantité attendue **≤** quantité envoyée × … » — **SUPERSEDED
    PAR CT18 et ta règle « 12 m → 6 m » du 01/10** (« cette conversion
    doit rester exacte »).*
- Lot brut encore **chez GMC** (pas encore envoyé) pour une ligne d'un
  autre état : **réservation** dès la **commande confirmée** [V Y1 ; Y1
  bis (c)] ; voir §6.3 bis. Au BST, le résultat attendu doit être
  identique à celui de la réservation : identique → conversion en
  affectation liée ; différent → BST refusé [Y1 bis (b)].

### 6.11 bis Bon de sortie transformation — préparation commerciale [V P-BST, P-RET, CT18, Y1 bis (b)]

**Règle fondamentale** (tes mots) : « BST commercial ≠ mouvement
physique » et « allocation ≠ mouvement physique ». « Le lot transformé
n'existe qu'au niveau physique après le traitement de la
transformation/réception en Phase 5.8. »

| Phase 5.6 — le module commercial **prépare** | Phase 5.8 — le module transformation **exécute** |
|---|---|
| sélectionne le lot brut | exécute la sortie physique |
| vérifie sa disponibilité | enregistre le mouvement physique |
| définit la transformation prévue | gère la transformation |
| définit le résultat attendu | crée le nouveau lot transformé |
| vérifie la compatibilité | enregistre le résultat réel |
| compare le résultat attendu avec la réservation | gère la réception de transformation |
| convertit la réservation en nouvelle allocation liée au BST | rend le lot transformé physiquement disponible après réception GMC |
| génère/prépare le document BST | |

- **La 5.6 ne crée aucun mouvement physique et aucun lot transformé**
  [V P-BST].
- **Type de transformation** [V P-RET] :
  - deux types seulement : **GALVANISATION** et **GPP** ;
  - GALVANISATION → finition de retour **GALVA**, fixée automatiquement ;
  - GPP → finition de retour **GPP**, fixée automatiquement ;
  - l'utilisateur ne peut pas choisir une autre finition ; une finition
    incohérente est refusée ;
  - aucun type AUTRE, découpe ou perçage dans cette phase ;
  - un même transformateur peut avoir les deux capacités ; c'est le type
    choisi dans le BST qui détermine le résultat.
  - FACT : la base ne donne qu'un seul type à un transformateur, et
    connaît aussi DEBIT et AUTRE. Proposition technique [CT] : ajouter
    les capacités du transformateur (GALVANISATION, GPP) sans supprimer
    l'existant (DB20) ; les types DEBIT et AUTRE restent dans la base,
    inutilisés par la 5.6.
  - Lecture L-m (§22) : un BST d'un type donné est refusé si le
    transformateur n'a pas cette capacité.
- **Résultat attendu** [V CT18, P-RET] : finition fixée par le type ;
  longueur et quantité attendues **définies dans le BST**, par
  conversion exacte (25 × 12 m → 50 × 6 m) ; figé dès qu'une allocation
  s'y rattache.
- **Comparaison avec la réservation** [V Y1 bis (b)] : identique →
  réservation CONVERTIE et nouvelle allocation liée au BST ; différent →
  BST refusé, rien n'est écrit.
- **Quantités non réservées** : une ligne de BST peut porter une quantité
  que personne n'a réservée (les 40 barres de l'exemple X3, ou le
  reliquat de conversion de P-MULT). Elle reste affectable ensuite, sur
  le résultat attendu, par une décision explicite du SUPERADMIN (X3).
  Rien n'est attribué automatiquement.
- **Blocage** (lecture L-k, §22) : la quantité d'une ligne de BST préparé
  reste physiquement chez GMC jusqu'à la sortie (5.8), mais elle est
  **engagée** : elle ne peut plus être réservée, affectée brute, ni
  placée dans un autre BST.
  - Pas de double compte : le lot brut est bloqué par la quantité
    engagée, en barres du lot (25) ; les allocations liées se comptent
    sur la quantité attendue de la ligne du BST, en pièces attendues
    (49 sur 50). Une allocation liée n'est donc pas comptée une seconde
    fois dans l'« affecté » du lot brut.
- **Unité de vente** [Y4, CT7] : une allocation sur un résultat attendu
  GALVA ou GPP vise une ligne vendue en KG ou TONNE, ce que CT7 garantit
  déjà sur la ligne. Une quantité non réservée n'a pas encore de ligne :
  le contrôle se fera au moment de son allocation.
  - *v8 (§6.9, §7.2) : « pour la 5.8 : un envoi en galvanisation ou en
    GPP ne concerne que ces articles vendus au poids » — précisé par
    P-BST : le contrôle se fait à l'allocation, en 5.6.*
- **Document** : numéro (numérotation existante), transformateur, type de
  transformation, date, lignes (lot, quantité, résultat attendu),
  préparé par, date/heure. État [CT] : **PRÉPARÉ** en 5.6 ; l'exécution
  est enregistrée par la 5.8.
- **Qui** (lecture L-l, §22) : le SUPERADMIN, puisque la préparation crée
  une allocation (N10).
- **Audit** : PREPARATION_BST ; CONVERSION_RESERVATION_AFFECTATION pour
  chaque réservation convertie.
- **Deux questions ouvertes** (§22) :
  - **Q-BCT** — la base exige aujourd'hui un bon de commande de
    transformation pour tout BST ; ta décision ne parle que du BST ;
  - **Q-ANNUL** — annulation d'un BST préparé avant sa sortie physique.
- **Ce que la 5.8 trouvera** : un BST préparé, ses lignes, leur résultat
  attendu et les allocations liées. FACT : le mouvement de sortie porte
  déjà la référence de la ligne du BST ; la 5.8 exécutera donc la sortie
  **de cette ligne**. Le garde-fou CT11 laisse passer la sortie qui
  exécute une ligne de BST préparé, et refuse toute autre sortie d'une
  quantité engagée.
- *v8 (P-BST, proposition) : « la 5.6 code une fonction … la 5.8
  l'appellera en établissant les BST, dans la même opération que l'envoi
  physique » — **SUPERSEDED PAR P-BST (02/10)** : la préparation (5.6)
  et la sortie physique (5.8) sont deux opérations distinctes.*

### 6.12 Compatibilité [V D1, K2, O4, X3]

- Même article ; même finition ; même longueur : compatibilité
  **directe** d'un lot déjà dans l'état commercial demandé.
- Exceptions de D1, préservées et rappelées par toi le 01/10 :
  - même finition, sauf NOIR/LAC → GALVA/GPP ;
  - même longueur, sauf multiple exact : 12 m → 2 × 6 m ; « cette
    conversion doit rester exacte » (25 × 12 m → 50 × 6 m) ;
  - LAC = NOIR.
- « Une transformation nécessaire signifie que le lot brut n'est pas
  directement compatible avec la ligne transformée » [V 01/10].
- Elles passent **par une transformation** : « le lot brut 12 m ne doit
  jamais être considéré directement disponible comme 6 m » [K2]. Elles
  deviennent affectables dès que la marchandise est chez le
  transformateur avec son résultat attendu (X3, CT18). Avant l'envoi,
  elles sont réservables dès la commande confirmée (Y1, Y1 bis (c),
  §6.3 bis).
- [V **P-RET**, 02/10] Les seules transformations sont la GALVANISATION
  et le GPP. Le passage 12 m → 6 m se fait donc **à l'intérieur** d'une
  galvanisation ou d'un GPP (ton exemple CT18 : le galvanisateur rend des
  barres GALVA de 6 m). Le même passage **sans** changement de finition
  (NOIR 12 m → NOIR 6 m) n'a pas de transformation dans le périmètre
  actuel : **Q-COUPE** (§22).
- [V **P-MULT**, 02/10] 1 × 12 m = 2 × 6 m ; approvisionnement calculé
  **par excès** ; 49 × 6 m → 25 × 12 m → 50 × 6 m → 49 affectés, 1
  restant, jamais attribué automatiquement (§6.3 bis).
- Pas de FIFO : le système ne choisit jamais le lot ; le SUPERADMIN
  choisit [V D5, rappel du 01/10].
- [CT] L'état se compare sur article, finition, longueur.

### 6.13 Suppléments [V O1, X9, cahier, BR §4]

- Supplément = au-delà de la quantité en vigueur ; motif obligatoire ;
  affectation par le SUPERADMIN ; prélevé sur du stock réellement
  disponible et non affecté ailleurs.
- **X9 = A** : un supplément enregistré **reste un supplément**. Aucune
  modification ultérieure de la commande ne le requalifie, ni
  automatiquement ni rétroactivement. Son historique est conservé.
- **CT17 VALIDÉ** :
  - le type d'affectation est **fixé à la création** ;
  - deux types : **NORMALE** et **SUPPLÉMENT** ;
  - la quantité est normale tant que le cumul normal ne dépasse pas la
    quantité en vigueur V ; au-delà : SUPPLÉMENT + motif obligatoire ;
  - une affectation n'est **jamais** requalifiée automatiquement après sa
    création ; **X9 est maintenu**.
  - FACT : la base enregistre ce type sous le code **INITIALE** (BR §1 :
    « quantité normale affectée (affectation de type INITIALE) ») ; les
    tests existants l'utilisent. Choix technique (signalé) : le code
    stocké INITIALE est conservé et affiché « NORMALE » ; aucun test
    existant n'est touché.
  - Demande à cheval sur V (ex. cumul normal 110, V = 120, demande de 15)
    : ma lecture (L-d, §22) = refusée, avec l'indication du découpage
    possible (10 NORMALE + 5 SUPPLÉMENT avec motif) ; aucun découpage
    automatique.

### 6.14 Réaffectations [V BR §7, cahier ; PROP C8]

- Tracée, motif obligatoire, partie non livrée seulement.
- Reste conservé : 30 sur 100 → reste 70 [V cahier].
  - FACT : le trigger clôture toute l'origine.
  - [CT] Le reste de 70 est donc recréé explicitement, même lot, même
    emplacement, **même type que l'origine** (X9, CT17 : un supplément
    reste un supplément).
- [PROP C8] SUPERADMIN ; à la **destination** (autre affaire), typage
  selon la quantité en vigueur restante de la destination : INITIALE dans
  la limite de V, sinon SUPPLÉMENT. Ce n'est pas une requalification de
  l'origine, mais une nouvelle affectation d'une autre affaire.
  - Point à confirmer avec C8 : un supplément déplacé peut-il devenir
    NORMALE (INITIALE) à la destination ?
- Réservation de lot brut : CT21 ne prévoit pas de réaffectation ; ma
  lecture (L-i, §22) : libération avec motif, puis nouvelle réservation
  (§6.3 bis).

### 6.15 Libérations [V N7, X6 ; PROP C9]

- Libération explicite en cas de diminution (N7) et à la clôture (X6).
- [PROP C9] Libération pour erreur : SUPERADMIN, motif, tracée.
- **Réservation de lot brut** [CT21 VALIDÉ] : libérée par l'annulation de
  la commande, la clôture avec reliquat, une diminution de commande avec
  choix explicite, ou le SUPERADMIN avec motif obligatoire → statut
  LIBÉRÉE ; audit LIBERATION_AFFECTATION. Le système ne choisit jamais
  seul ce qu'il libère [CT19].

### 6.16 Situation de l'affaire [V K15, O1, O4, D5]

Calculée, jamais saisie :

- par ligne : O (« 0 initial » pour une ligne AVENANT, CT16), A, V,
  normal affecté, supplément, **réservé pour transformation** (CT21),
  livré, reste, à approvisionner, reliquat ;
- par lot : affecté, **réservé pour transformation** (pièces du lot,
  CT21), **engagé dans un BST préparé** (L-k), disponible ;
- par ligne de BST : quantité attendue, quantité affectée, quantité
  attendue non affectée, dont le **reliquat de conversion** d'une
  réservation convertie (P-MULT) ;
- stock par emplacement, catégories A à F de D5 :

| D5 | Contenu | Calcul [CT] |
|---|---|---|
| A. Disponible chez GMC | stock physique GMC − affecté non livré − **réservé** [CT21] − engagé dans un BST préparé non sorti (L-k) | 5.6 |
| B. Chez le galvanisateur | stock physique chez chaque transformateur | 5.6 |
| C, D. Chez lui, affecté / non affecté | par emplacement | 5.6 |
| E. Envoyé, en attente de réception | calculé à partir du stock physique réellement présent chez les transformateurs (K1) [**CT12 VALIDÉ**] | 5.6 |
| F. Transformé ou à transformer, chez lui | représenté par le **résultat prévu** de la ligne du bon de sortie. Pas de lot transformé avant la réception (K1). Affectable (X3), non vendable. | 5.6 (lot en 5.8) |
| (en plus) Lots bruts réservés chez GMC | « réservé pour transformation », par ligne et par lot ; **déduit du disponible** [Y1 bis (a), CT21] | 5.6 |
| (en plus) BST préparé, marchandise encore chez GMC | quantité engagée par un BST préparé en 5.6 et pas encore sortie (5.8) ; résultat attendu affectable, non vendable [P-BST ; L-k] | 5.6 |
| (en plus) Reliquat de conversion | pièces attendues − pièces qui couvrent la ligne, pour une réservation (§6.8) ; jamais attribuées automatiquement [P-MULT]. Les autres quantités attendues non affectées d'un BST (ex. les 40 barres de X3) sont affichées à part, comme « quantité attendue non affectée » | 5.6 (stock réel en 5.8) |

- [CT12] La situation distingue : stock GMC ; stock chez le
  transformateur ; affecté ; envoyé/non réceptionné ; disponible. La
  transformation physique et les bons restent en 5.8 — *précisé par
  P-BST (02/10) : le BST est préparé en 5.6 ; sa sortie physique et la
  réception restent en 5.8.*
- Les quatre notions d'O4 sont affichées.
- Formules [CT] au §6.8.

### 6.17 Clôture avec reliquat [V C10, X6]

Opération contrôlée **unique** :

1. le SUPERADMIN demande la clôture ;
2. le système calcule et affiche le reliquat (ex. 100 commandées,
   70 livrées → 30 ; « les 30 peuvent encore être affectées à
   différentes allocations ») ;
3. le système affiche les affectations encore présentes sur ce reliquat,
   ainsi que les réservations de lots bruts actives (CT19, CT21) ;
4. le SUPERADMIN confirme ;
5. ces affectations et réservations sont libérées dans le cadre de la
   clôture (réservations → LIBÉRÉE) ;
6. motif obligatoire [**CT19 VALIDÉ**] : reliquat annulé par le client ;
   reliquat devenu inutile ; commande abandonnée ; AUTRE + commentaire
   obligatoire ;
7. la commande passe au statut **SOLDÉE**, reliquat conservé **ligne par
   ligne**, historique conservé.

Règles associées :

- Le système ne choisit jamais seul les affectations à libérer en dehors
  de cette opération confirmée.
- Le reliquat n'est **jamais transformé en livraison**.
- La marchandise présente reste du stock GMC selon sa localisation et son
  état.
- Représentation [CT19 VALIDÉ] : statut **SOLDÉE** ; pas de statut
  supplémentaire « CLÔTURÉE AVEC RELIQUAT ». *v7 (§21) : « SOLDÉE ou
  statut propre » — l'option « statut propre » est **SUPERSEDED PAR
  CT19**.*
- Signal « entièrement livrée » [V cahier] ; définition [PROP C10].

### 6.18 Statuts

| Document | Statuts (FACT) | Transitions |
|---|---|---|
| Devis | EN_COURS, CONFIRME, EXPIRE, ANNULE | [V cahier] ; contrôle en base [CT] |
| Commande | BROUILLON, CONFIRMEE, SOLDEE, ANNULEE | [V cahier] ; clôture avec reliquat → SOLDÉE + reliquat + motif [CT19 VALIDÉ] |
| Affectation | ACTIVE, CLOTUREE | + raison de clôture : réaffectation, libération, réduction, clôture de commande [CT] ; type NORMALE (code INITIALE) / SUPPLÉMENT fixé à la création [CT17] ; lien éventuel vers la réservation convertie [Y1 bis] |
| Réservation de devis | (aucun aujourd'hui) | active / annulée [PROP C6] |
| Réservation de lot brut (Y1) | nouvelle | **ACTIVE → CONVERTIE** (à la préparation du BST en 5.6, allocation liée créée) **ou ACTIVE → LIBÉRÉE** [CT21 VALIDÉ] ; aucun retour en arrière depuis CONVERTIE ou LIBÉRÉE [CT] |
| Bon de sortie transformation | (aucun statut aujourd'hui) | **PRÉPARÉ** par la 5.6 [P-BST ; CT] ; exécution physique enregistrée par la 5.8 ; annulation avant sortie : Q-ANNUL |
| Article | (aucune version aujourd'hui) | versions successives, la dernière en vigueur ; anciennes conservées [P-ART] |
| Demande de création d'article | nouvelle | en attente → acceptée / refusée (lecture L-o) |

### 6.19 Permissions [V O5, X4, N10, N14, K8, K16]

- **CT1 VALIDÉ — un seul SUPERADMIN** : le système impose **exactement
  un** SUPERADMIN, dans l'application **et** dans la base. La création
  d'un deuxième SUPERADMIN est refusée, que le premier soit actif ou non.
  - *v7 (§21, CT1) : « un seul SUPERADMIN **actif** ; transmission =
    désactiver l'un, activer l'autre »* — **SUPERSEDED PAR CT1** : le
    contrôle porte sur tous les comptes SUPERADMIN, actifs ou non ; la
    transmission par « désactiver puis activer » n'est plus possible.
  - Conséquences que je propose (lecture L-f, §22, à confirmer) : le seul
    SUPERADMIN ne peut être ni désactivé ni changé de rôle (sinon plus
    personne ne pourrait gérer les comptes) ; FACT : la base ne contient
    aucun compte, donc le premier compte SUPERADMIN est créé par la
    procédure d'installation ; une transmission future à une autre
    personne sera une opération unique et auditée, décidée le moment
    venu (rien en 5.6).
- **CT2 VALIDÉ — comptes, permissions, modules** : les structures
  (comptes, permissions, modules, droits par compte et par module) sont
  créées dès la 5.6. Les droits initiaux correspondent à la situation
  actuelle ; aucune délégation supplémentaire n'est active ;
  l'architecture permet une délégation future sans refonte majeure.
  - Ma lecture de « situation actuelle » (L-g, §22) : le SUPERADMIN a tous les
    droits ; tout autre compte n'a **aucune** permission tant que le
    SUPERADMIN ne la lui attribue pas (FACT : aucun compte n'existe
    aujourd'hui).
- Le SUPERADMIN crée les comptes et définit les accès : utilisateur par
  utilisateur, module par module, permission par permission si
  nécessaire.
- Le rôle COMMERCIAL ne donne pas automatiquement tous les droits
  commerciaux. Les opérations sensibles restent soumises à des
  permissions **explicites** [CT2] : une permission d'un module ne donne
  pas les opérations sensibles de ce module.
- Droits liés au **compte utilisateur et à son rôle/ses permissions**,
  jamais au nom affiché. Aucune règle ne s'appuie sur le nom « Mohamed »
  [V X4].
- **Opérations réservées au SUPERADMIN** [V] :
  - avenants ;
  - corrections sensibles, dont les corrections d'inventaire (K17) ;
  - modifications stratégiques, dont l'intervention sur un devis
    CONFIRMÉ et la modification exceptionnelle du taux (O3, X7, CT5) ;
  - interventions exceptionnelles sur une commande confirmée, dont la
    correction d'une erreur de prix (CT10) ;
  - clôture avec reliquat ;
  - gestion des droits (X4) ;
  - affectations, suppléments compris, et réservations de lots bruts,
    y compris leur libération pour motif (N10 ; Y1 bis (d) ; CT21) ;
  - clients ;
  - annulation d'un devis ;
  - annulation d'une commande confirmée (cahier) ;
  - validation des valeurs article (CT3) et modification du réglage GPP
    (CT4) ;
  - correction d'inventaire, avec PV (CT14) ;
  - **création d'article** [V **P-ART**, 02/10 ; BR §11] : SUPERADMIN
    uniquement. Les utilisateurs opérationnels sélectionnent un article
    existant ou **demandent** une création ; ils ne créent jamais
    directement ;
  - modification d'article à impact métier (nouvelle version) et
    correction administrative : SUPERADMIN (BR §11 ; lecture L-p) ;
  - préparation d'un bon de sortie transformation (lecture L-l : elle
    crée une allocation, N10).
  - *v7 : « déclaration du résultat prévu d'une transformation (CT18) »*
    — **SUPERSEDED PAR CT18 (01/10)** : le résultat attendu est renseigné
    à l'établissement du BST.
  - *v8 : « qui peut établir un BST relève de la 5.8 » ; « création
    d'article … périmètre 5.6 : P-ART » — **SUPERSEDED PAR P-BST et
    P-ART (02/10)**.*
- Permissions attribuables (non réservées), par module [CT2] : préparer
  un devis, consulter, etc.
- **Demander la création d'un article** : ouvert aux utilisateurs
  opérationnels [V P-ART : « les utilisateurs opérationnels peuvent …
  demander la création d'un article »]. Lecture L-o (§22) : tout compte
  actif peut demander, sans permission particulière ; dis-moi si tu
  préfères que ce soit une permission à attribuer.
- Délégation future prévue ; **aucune délégation supplémentaire active**
  [V X4, K8].
- Mécanisme [CT2 VALIDÉ] : catalogue de permissions par module dont les
  opérations réservées sont marquées « réservé SUPERADMIN » (non
  attribuables tant que tu n'as pas décidé une délégation). Le marquage
  est une donnée, levable sans reprogrammer : c'est ce qui permet la
  délégation future « sans refonte majeure ».

### 6.20 Historisation / audit

- Jamais d'écrasement : quantités, prix (négociés au stade du devis,
  figés à la confirmation : Y5 ; erreur corrigée par avenant de
  correction : CT10), taux (X7, CT5), avenants (CT10), valeurs article
  validées (CT3), réglage GPP (CT4), photo du devis confirmé (CT6),
  réservations (CT21), affectations, clôtures et reliquats (CT19),
  droits (CT2).
- Audit : 12 actions aujourd'hui → **39 proposées** [CT] :
  - les 12 existantes, dont REAFFECTATION, QUANTITE_SUPPLEMENTAIRE,
    MODIFICATION_PRIX, ANNULATION_DOCUMENT, CORRECTION_INVENTAIRE ;
  - 27 nouvelles : CREATION_CLIENT, MODIFICATION_CLIENT, CREATION_COMPTE,
    MODIFICATION_COMPTE, ATTRIBUTION_PERMISSION, RETRAIT_PERMISSION,
    VALIDATION_REFERENTIEL_ARTICLE, **MODIFICATION_REGLAGE_GPP** (CT4),
    SAISIE_TAUX_DEVIS, CONFIRMATION_DEVIS, INTERVENTION_DEVIS_CONFIRME,
    PROLONGATION_DEVIS, RESERVATION, ANNULATION_RESERVATION,
    CONFIRMATION_COMMANDE, AVENANT_COMMANDE, **CORRECTION_ERREUR_PRIX**
    (CT10), AFFECTATION, LIBERATION_AFFECTATION, CLOTURE_COMMANDE,
    PREPARATION_BST, RESERVATION_LOT_BRUT,
    CONVERSION_RESERVATION_AFFECTATION, **CREATION_ARTICLE**,
    **DEMANDE_CREATION_ARTICLE**, **NOUVELLE_VERSION_ARTICLE**,
    **CORRECTION_ADMINISTRATIVE_ARTICLE** (P-ART).
  - v7 : 33 (34) ; v8 : 35 (36) ; **v9 : 39** = 35 + les quatre actions
    d'article de P-ART (dont CREATION_ARTICLE, que la v8 comptait « en
    plus si P-ART »).
  - PREPARATION_BST (nom v7 : DECLARATION_RESULTAT_PREVU ; nom v8 :
    ENREGISTREMENT_RESULTAT_ATTENDU) trace la préparation commerciale
    d'un BST, résultat attendu compris (P-BST, CT18). Renommée parce que
    la 5.6 prépare désormais le document entier.
  - Une validation CT3 reste tracée par VALIDATION_REFERENTIEL_ARTICLE ;
    la nouvelle version d'article qu'elle crée est tracée par
    NOUVELLE_VERSION_ARTICLE.
  - Les trois actions exigées par CT21 sont présentes :
    RESERVATION_LOT_BRUT, CONVERSION_RESERVATION_AFFECTATION,
    LIBERATION_AFFECTATION (qui trace aussi la libération d'une
    réservation).
  - Les changements de prix au stade du devis sont tracés avec l'action
    existante MODIFICATION_PRIX (Y5).
  - La modification exceptionnelle du taux d'un devis confirmé est
    tracée par INTERVENTION_DEVIS_CONFIRME, avec le motif (CT5) ; elle
    ne change ni le taux des avenants, ni les lignes, ni les avenants
    déjà enregistrés (Y6).
  - La correction d'inventaire garde CORRECTION_INVENTAIRE, avec la
    référence et la date du PV (CT14).

### 6.21 Articles [V P-ART (02/10), BR §11, BR §16, CT3]

- **Création** [V P-ART] : les nouveaux articles sont créés
  **uniquement par le SUPERADMIN**. Les utilisateurs opérationnels
  peuvent sélectionner un article existant et **demander** la création
  d'un article ; ils ne peuvent pas en créer un directement.
  - FACT : aucun service de création d'article n'existe aujourd'hui ;
    BR §11 réservait déjà la création à Mohamed.
  - Demande de création (lecture L-o, §22) : un enregistrement tracé
    (demandeur, description de l'article demandé, date ; en attente,
    puis acceptée ou refusée par le SUPERADMIN). Tout utilisateur
    opérationnel actif peut la faire. La demande ne crée aucun article
    par elle-même.
  - À la création, le SUPERADMIN peut valider dans la même opération la
    méthode et la masse (CT3) [CT] ; sinon l'article existe mais ne peut
    pas être vendu au poids tant que sa valeur n'est pas validée (CT3).
  - FACT : le format du code article n'est toujours pas décidé (depuis
    la 5.5) ; l'identifiant technique actuel est conservé. Ce point
    n'empêche pas de coder la 5.6.
- **Modification ayant un impact métier** [V P-ART] — masse, poids,
  % GALVA, unité de valorisation, caractéristiques influençant les
  calculs, règles techniques :
  - elle crée une **nouvelle version historisée** de l'article ;
  - l'ancien état reste conservé ;
  - aucun calcul historique n'est recalculé silencieusement.
  - Mise en œuvre [CT] : une version = numéro, date et heure
    d'enregistrement, auteur, motif et valeurs ; elle est en vigueur dès
    son enregistrement (ni version antidatée, ni version future). Les validations CT3 (méthode, masse, % GALVA) et
    le changement d'unité de valorisation (historique déjà immuable
    depuis la 5.5, BR §16) créent chacun une nouvelle version.
  - Le changement d'unité de valorisation reste fait par le service
    existant de la 5.5 ; la 5.6 y ajoute le contrôle SUPERADMIN (BR §11,
    §16 ; FACT : aujourd'hui il ne vérifie que l'existence de
    l'utilisateur).
- **Correction purement administrative** [V P-ART] — libellé, faute de
  frappe :
  - sans nouvelle version métier ;
  - mais **auditée** : ancienne valeur, nouvelle valeur, utilisateur,
    date/heure, motif lorsque nécessaire.
  - Lecture L-p (§22) : seule la désignation (le libellé) est traitée
    comme administrative ; tout autre champ est traité comme ayant un
    impact métier ; la correction est faite par le SUPERADMIN (BR §11 :
    « modification uniquement par dérogation auditée »).
- **Commandes confirmées** [V P-ART, CT3, CT6] : « une commande confirmée
  conserve les caractéristiques utilisées lors de sa confirmation » ;
  « une nouvelle version de l'article ne doit pas modifier
  rétroactivement une commande confirmée ».
  - Mise en œuvre [CT] : la photo du calcul (CT6) garde les valeurs
    utilisées et le numéro de la version d'article.
  - Lecture L-v (§22), pour les cas que ta décision ne cite pas :
    - **devis encore EN_COURS** quand une nouvelle version apparaît : il
      n'est pas recalculé en silence ; le système signale qu'une version
      plus récente existe, et l'utilisateur décide de recalculer ;
    - **commande pas encore confirmée** : elle reprend la photo du devis
      confirmé (CT9), même si une version plus récente est créée avant
      sa propre confirmation.
- **Lots** : FACT (5.5) — chaque lot garde l'unité de l'article en
  vigueur à sa création, et chaque mouvement est valorisé dans l'unité
  en vigueur à sa date. Une nouvelle version d'article ne réécrit donc
  ni les lots, ni les mouvements.
- **Audit** : CREATION_ARTICLE, DEMANDE_CREATION_ARTICLE,
  NOUVELLE_VERSION_ARTICLE, CORRECTION_ADMINISTRATIVE_ARTICLE.
- *v8 (P-ART) : « création d'article et contrôle du changement d'unité
  en 5.6, oui ou non ? » — **SUPERSEDED PAR P-ART (02/10)**.*

---

## 7. Impacts base de données

### 7.1 Créé en 5.6 (dans la future 0021) — voir §11

### 7.2 Préparé seulement (aucune colonne créée en 5.6)

| Pour | Élément | Raison |
|---|---|---|
| 5.7 | Prix négocié d'une commande fournisseur confirmée historisé, jamais écrasé ; statut « confirmée » ; historique des négociations ; `v_approvisionnement_ligne` sur V (FACT : utilise la quantité originale) ; « à approvisionner » tient compte du réservé pour transformation (§6.8) ; **achat par excès en barres de 12 m** pour un besoin en 6 m (P-MULT : 49 × 6 m → 25 × 12 m), avec la fonction de calcul de la 5.6 | O8 fournisseur ; CT21 ; P-MULT |
| 5.8 | **Exécution** du BST préparé en 5.6 : sortie physique, mouvement (rattaché à la ligne du BST), transformation, **résultat réel**, **nouveau lot transformé**, **réception** ; rattachement des allocations au lot résultant (X3) ; le reliquat de conversion non affecté devient du stock GMC disponible ; garde-fou CT11 à la sortie ; levée du blocage du retour ; retour en plus de pièces qu'à l'envoi (1 → N, bloqué aujourd'hui) ; écarts reçu/attendu. *v8 : « établissement du BST … envoi physique » dans la même opération — SUPERSEDED PAR P-BST (02/10).* | X3, Y1 bis, CT11, CT18, P-BST, P-RET, P-MULT |
| 5.9 | Livraison interdite avant réception du lot transformé (CT18) ; vente brute d'une quantité réservée interdite (CT21) ; garde-fou CT11 sur les livraisons ; facturation au **prix en vigueur** (prix confirmé ou corrigé, CT10) ; reliquat jamais livré (X6) ; saisie du montant final du transport après facturation (Y2) | X3, X6, Y2, CT10, CT11, CT18, CT21 |
| 5.10 | Coût réel, marge ; comparaison avec la **photo figée** du devis (CT6) ; **répartition du transport final au poids entre les articles** pour la marge par article, dans les résultats et le tableau de bord (Y2), à partir du poids de chaque ligne (CT20) ; **transport réel** distinct du prévisionnel ; marge = chiffre d'affaires − prix de revient (P-KG-TR) ; coût du **reliquat de conversion**, qui reste du stock GMC et n'est pas une perte (P-MULT) : règle de coût à écrire en 5.10 | Y2, CT6, CT20, P-KG-TR |
| Plus tard | Autres emplacements (O9) ; import de la MV | O9 |

---

## 8. Impacts services

| Service | Nouveau / modifié | Contenu |
|---|---|---|
| `droits_service` | Nouveau | Comptes (SUPERADMIN seul) ; **un seul SUPERADMIN** : second refusé (CT1) ; seul SUPERADMIN ni désactivé ni changé de rôle et premier compte créé par la procédure d'installation (lecture L-f) ; catalogue de permissions **par module** (CT2) ; attribution/retrait, audités ; vérification compte actif + permission explicite ; opérations réservées. |
| `client_service` | Nouveau | Créer/modifier (SUPERADMIN), audit, jamais de suppression. |
| `referentiel_article_service` | Nouveau (**CT3, CT4, P-ART**) | Valeurs candidates présentées sans choisir (dont la masse « MV à vérifier ») ; validation SUPERADMIN dans un historique dédié (méthode, valeur, unité, % GALVA à trois états, sources affichées, motif) ; valeur en vigueur = dernière validation ; **réglage GPP** : taux en vigueur à une date, modification SUPERADMIN historisée avec date d'effet. ; **articles (P-ART)** : création par le SUPERADMIN ; demandes de création par les utilisateurs opérationnels, traitées par le SUPERADMIN (L-o) ; modification à impact métier = nouvelle version historisée ; correction administrative auditée (L-p). |
| `core/poids_vente.py` | Nouveau | **Vente au poids (KG ou TONNE)** : valeur validée × facteur de finition (NOIR 1 ; GALVA 1 + % validé/100 ; GPP 1 + taux global/100) ; **hors poids (NOIR/LAC seulement)** : poids déclaré obligatoire, jamais majoré ; GALVA et GPP refusés hors KG/TONNE (Y4, CT7) ; % GALVA validé exigé (X8, CT3) ; origine du poids (CT20). |
| `core/prix_revient.py` | Nouveau | TND → EUR : montant TND ÷ taux, à partir du **texte saisi**, calcul exact (Y3, CT5) ; calcul au total de la ligne, chaque prix et quantité dans son unité, un seul arrondi au centime EUR (CT6) ; coût de transformation dans son unité (CT8) ; prix au poids × poids déclaré hors poids (O7) ; transport : EUR/T × tonnes en TONNE ; **KG ÷ 1 000 × EUR/T en KG** (P-KG-TR : 5 000 kg × 100 EUR/T = 500 EUR) ; montant total saisi hors poids (X2, Y2) ; **quatre composants conservés séparément** (vente, achat, transformation, transport) ; prix de revient = achat + transformation + transport ; marge prévisionnelle = chiffre d'affaires − prix de revient (L-q) ; unitaire affiché = total ÷ quantité. |
| `devis_service` | Nouveau | Préparation (permission) ; taux saisi en TND pour 1 EUR, nouvelle valeur à chaque saisie, devis pointant vers son taux (CT5) ; devises imposées ; transformation prévue OUI/NON et coût (CT7, CT8) ; poids ; transport ; prix de revient ; **négociation du prix au stade du devis, tracée** (Y5) ; réservations informatives ; confirmation : taux, prix, conditions et **photo complète** figés (CT6) ; modification exceptionnelle du taux par le SUPERADMIN : nouveau taux, motif, audit (CT5) ; **sans effet sur le taux des avenants, les anciennes lignes ni les avenants enregistrés** (Y6, 02/10 ; usage du taux modifié : L-t) ; expiration, prolongation ; annulation (SUPERADMIN). |
| `commande_service` | Nouveau | Création depuis le devis (coûts estimés recopiés, CT9) ; brouillon ; confirmation ; avenants (table unique append-only, impacts avant/après, CT10 ; ligne AVENANT à 0, CT16 ; **taux lu dans la photo du devis validé**, Y6 ; poids recalculé, CT10 ; cas 1/cas 2, prix confirmé repris ; nouveau prix seulement pour un nouvel article) ; **aucune renégociation du prix après confirmation** (Y5) ; **correction d'une erreur de prix par le SUPERADMIN**, avec motif (CT10) ; diminution (N7, K13) ; annulation ; clôture avec reliquat : SOLDÉE, motif CT19, reliquat ligne par ligne, affectations et réservations listées puis libérées. |
| `affectation_service` | Nouveau | SUPERADMIN ; lot choisi à la main ; état identique ou résultat attendu (X3, CT18) ; type fixé à la création (CT17) ; **réservation d'un lot brut** : contrôles et effets (CT21), calcul par excès et reliquat de conversion (P-MULT) ; conversion d'une réservation en allocation liée (appelée par `bst_service`) ; libération des réservations (CT21) ; affectation explicite d'un reliquat de conversion à une autre affaire (P-MULT) ; réaffectation avec reste recréé ; libération ; plafonds par emplacement, réservations et quantités engagées comprises. *v8 : conversion « appelée par la 5.8, P-BST » — SUPERSEDED PAR P-BST (02/10).* |
| `bst_service` | **Nouveau (P-BST, P-RET)** | **Préparation commerciale** du bon de sortie transformation : sélection du lot brut, disponibilité, type de transformation (GALVANISATION ou GPP), finition de retour automatique, longueur et quantité attendues (conversion exacte), compatibilité, comparaison avec la réservation, conversion, document (numéro, état PRÉPARÉ). **N'appelle aucune écriture du Stock Service ; ne crée aucun lot.** |
| `core/conversion_longueur.py` | **Nouveau** | Multiple exact (12 m → 2 × 6 m) ; pièces attendues = barres × n ; barres nécessaires = besoin ÷ n arrondi par excès ; reliquat de conversion (P-MULT, CT18). |
| `situation_service` | Nouveau, lecture seule | §6.16 (CT12 ; réservé pour transformation, CT21). |
| `stock_service` | Modifié | `corriger_inventaire` : SUPERADMIN + PV, référence **et date** (K17, CT14) ; quantité affectable par emplacement ; **garde-fou CT11** (affecté + réservé + engagé dans un BST préparé) sur l'envoi, la chute, la correction et le retour ; une quantité **engagée** dans un BST préparé ne peut sortir que par l'exécution de la ligne de ce BST (la 5.8 fournira cette référence) ; les sorties de quantités non engagées gardent leur comportement actuel ; retour de transformation refusé si le lot porte une affectation sur résultat attendu, jusqu'à la 5.8 (CT18). **Aucune nouvelle écriture de stock.** |
| `unite_valorisation_service` | Modifié (**P-ART**) | Changement d'unité d'un article réservé au SUPERADMIN (BR §11, §16) ; il crée une nouvelle version de l'article ; historique existant conservé. |
| `core/audit.py` | Modifié | 39 actions (§6.20). |

---

## 9. Impacts repositories

| Repository | Nouveau / modifié |
|---|---|
| `client_repository`, `utilisateur_repository`, `permission_repository` | Nouveaux |
| `devis_repository` (devis, lignes, taux, photo du calcul), `reservation_repository` (réservations informatives) | Nouveaux |
| `commande_repository`, `avenant_repository` (avenants, interventions et corrections d'erreur de prix ; prix en vigueur) | Nouveaux |
| `affectation_repository` (affecté actif non livré par lot, emplacement, ligne, type ; résultat attendu ; **réservations de lots bruts** actives par lot, emplacement et ligne ; lien réservation → affectation) | Nouveau |
| `situation_repository` (lectures agrégées, livré par ligne et type) | Nouveau |
| `referentiel_article_repository` | Nouveau : historique des valeurs validées (CT3) ; réglage GPP historisé (CT4) ; **versions d'article et demandes de création** (P-ART) |
| `stock_repository` | Modifié : affecté non livré **par emplacement** (FACT : aujourd'hui par lot et par pool seulement) |
| `article_repository` | Modifié : lecture des paramètres validés ; **écriture** : création et correction de désignation (P-ART) |
| `bst_repository` | **Nouveau** : BST préparés, lignes, résultat attendu, allocations liées, quantité engagée par lot ; capacités des transformateurs (P-BST, P-RET) |

---

## 10. Impacts tests

- **210 cas proposés** (§12) : les 174 de la v8, + 36 pour tes
  décisions du 02/10 (dont M79 et M80, réservés en v8 et désormais
  définis). Aucun cas n'est supprimé.
- **293 tests existants conservés** (§13), avec des adaptations limitées
  et listées. **Exécutés le 02/10 : 293 réussis.**
- Les tests qui dépendent d'un point encore ouvert portent son repère
  (Y6-L, Q-COUPE, Q-BCT, Q-ANNUL, Q-TRF, L-a à L-v, C).
- **Aucun des 210 cas n'est exécuté** : ils seront écrits et exécutés au
  codage, après ta validation.

---

## 11. Migration 0021 — proposition uniquement

**Migration 0021 : à créer lors du CODAGE de la Phase 5.6, après
validation finale de l'analyse.** Elle n'existe pas. [**CT15 VALIDÉ**]
Elle sera transactionnelle, tout ou rien, additive uniquement : aucune
suppression de données existantes, aucune réécriture destructrice
(les tables reconstruites sont recopiées en entier), données existantes
reprises, nouveaux contrôles également protégés en base, valeurs par
défaut si nécessaire pour préserver les tests existants. Après
migration : intégrité, clés étrangères, tests existants et nouveaux
cohérents.

| # | Table | Contenu proposé | Source |
|---|---|---|---|
| DB1 | `utilisateur` | Rôle SUPERADMIN (reconstruction de la table : le CHECK change, toutes les lignes recopiées) ; **un seul SUPERADMIN, actif ou non** : index unique partiel sur le rôle, sans condition sur `actif` ; triggers : seul SUPERADMIN ni désactivé ni changé de rôle (L-f). *v7 : « un seul SUPERADMIN actif » — SUPERSEDED PAR CT1.* | [V N14] ; CT1 |
| DB2 | `module`, `permission`, `utilisateur_permission` (nouvelles) | Catalogue module/opération + marque « réservé SUPERADMIN » (donnée, levable sans reprogrammer) ; attributions par compte (par, le), retraits tracés, jamais supprimés | [V O5, X4] ; CT2 |
| DB3 | Valeurs article validées et réglage GPP (nouvelles) | **Valeurs article validées**, append-only : article, paramètre, méthode (liste extensible), valeur, unité, % GALVA à trois états, sources affichées, validé par (SUPERADMIN, contrôlé en base), date/heure, motif ; masse linéique actuelle lue comme « valeur MV à vérifier ». **Réglage GPP**, append-only : taux (2 % aujourd'hui), date d'effet, saisi par (SUPERADMIN), date. *v7 : « paramètre GPP 1,02 » ; « selon Y4 bis » — SUPERSEDED PAR CT3 et CT4.* Chaque validation crée une nouvelle version d'article (DB21, P-ART). | [V N1, N3, N4, K7, K20, X8] ; CT3, CT4 ; P-ART |
| DB4 | `taux_change` | + auteur ; + **texte saisi** (taux « exactement tel que saisi ») ; + motif pour une modification exceptionnelle | [V K5, X7, Y3] ; CT5 |
| DB5 | `devis` | Destination, incoterm ; annulation (cause, commentaire) ; confirmé par/le ; prolongation ; transitions contrôlées ; **référence du taux** (le devis pointe vers son taux) | [V cahier, O3] ; C4, C5 ; CT5 |
| DB6 | `devis_ligne` | Unité et quantité de vente (dont **KG**) ; poids (valeur, unité, origine CALCULÉ/DÉCLARÉ, méthode, valeur, % GALVA ou taux GPP utilisés) ; DÉCLARÉ seulement en NOIR/LAC hors poids ; une devise par prix, **vente EUR imposée** ; contrôle « **GALVA et GPP** seulement en KG ou TONNE » ; transformation prévue OUI/NON, coût et unité (5 unités) ; transport (EUR/t en tonne, montant total EUR hors poids ; **KG ÷ 1 000 × EUR/T en KG**, P-KG-TR) ; les quatre composants du calcul conservés séparément dans la photo ; **photo complète du calcul à CONFIRMÉ, immuable**. *v7 : « + KG selon Y4 bis » ; « GALVA seulement » — SUPERSEDED PAR CT7, CT20.* | [V K4, K22, O7, X2, X8, Y2, Y4, cahier] ; CT6, CT7, CT8, CT20 ; P-KG-TR |
| DB7 | `reservation_devis` | Emplacement, auteur, annulation | [V cahier] ; C6 |
| DB8 | `commande_client` | Un devis → une commande (index unique) ; annulation ; clôture avec reliquat : statut SOLDÉE, motif parmi 4 (AUTRE + commentaire obligatoire), par, le ; `date_confirmation` facultative en brouillon si C14 l'exige | [V cahier, X6] ; C1, C14, CT19 |
| DB9 | `commande_ligne` | Lien ligne de devis ; origine DEVIS/AVENANT (AVENANT : quantité initiale 0) ; unité, poids et origine (photo), prix EUR imposé, transport, transformation prévue et coût, coûts estimés recopiés ; **aucune colonne de taux** | [V O1, O2, K21, K22, X7] ; CT7, CT9, CT16, CT20 |
| DB9b | `commande_ligne` (trigger) | Quantité originale libre en brouillon puis figée (remplace `trg_commande_ligne_qte_immuable`) | [PROP C1] |
| DB10 | `avenant` (nouvelle) | **Table unique, append-only** : nature (quantité, nouvel article, intervention exceptionnelle du SUPERADMIN, dont **correction d'une erreur de prix**), cible, ancienne et nouvelle valeur, motif, auteur, date/heure, **impact quantitatif et financier avant/après** ; UPDATE et DELETE refusés | [V K9, O1] ; CT10 |
| DB11 | `commande_ligne` (trigger) | **Prix de vente figé à la confirmation** : toute modification refusée ensuite, **sans exception** (Y5). La correction d'une erreur passe par DB10 ; le prix en vigueur se calcule. Plus de table d'historique des prix (DB11 de la v6, lié à X1). Les changements au stade du devis sont tracés dans l'audit. *v7 (Y5 bis, IMPACT) : « exception éventuelle dans le trigger DB11 » — SUPERSEDED PAR CT10.* | [V Y5, K10] ; CT10 |
| DB12 | `affectation_stock` | Emplacement ; référence de la ligne de BST et état attendu pour une affectation sur transformation ; **lien vers la réservation convertie** ; raison de clôture ; type non modifiable (CT17) ; plafond par emplacement (trigger remplacé), **réservations actives comprises**, en pièces du lot (CT11, CT21), ainsi que les quantités engagées dans un BST préparé (L-k) ; une affectation sur résultat attendu est plafonnée par la quantité attendue de la ligne du BST. *v7 : « nature « réservation de lot brut » » dans cette table — remplacé par DB19 (choix technique, signalé).* | [V N11, X3, Y1] ; CT11, CT17, CT18, CT21 |
| DB13 | Reliquat de clôture (nouvelle) | Par ligne : V, livré normal, reliquat à la clôture ; immuable | [V X6] ; CT19 |
| DB14 | `journal_audit` | CHECK étendu à 39 actions ; reconstruction, audit recopié | [V] ; CT |
| DB15 | Corrections d'inventaire | SUPERADMIN exigé en base ; **référence et date du PV** enregistrées avec la correction (colonnes ajoutées ou table liée, au codage) et dans l'audit, exigées par trigger | [V K17] ; CT14 |
| DB16 | `client` | Anti-suppression | [V cahier] |
| DB17 | `bon_sortie_transformation` et sa ligne | **En-tête** : type de transformation (GALVANISATION ou GPP seulement), état PRÉPARÉ (l'exécution sera enregistrée par la 5.8), préparé par, date/heure ; lien vers le bon de commande de transformation : **Q-BCT**. **Ligne** : résultat attendu — finition **fixée par le type** (GALVANISATION → GALVA ; GPP → GPP ; contrôlée en base), longueur, quantité attendue en pièces (= quantité × n, exacte) ; référence de la réservation exécutée (L-r) ; **figé dès qu'une allocation s'y rattache**. Les lignes créées avant la 0021 restent valides (valeurs facultatives pour elles). *v8 : finition « imposée : galvanisateur → GALVA … correspondance avec le type du transformateur, DEBIT/AUTRE … P-RET » ; « saisi à l'établissement du BST » en 5.8 — SUPERSEDED PAR P-RET et P-BST (02/10).* | [V X3 = option A de la v5, D1] ; CT18, Y1 bis, P-BST, P-RET |
| DB18 | `reaffectation` | Reste explicite recréé ; même lot, même emplacement ; type d'origine conservé pour le reste | [V BR §7, cahier, X9] ; C8 |
| DB19 | `reservation_lot_brut` (**nouvelle**) | Lot ; ligne de commande ; quantité réservée (pièces du lot) ; finition et longueur attendues ; quantité attendue (pièces de la ligne) ; **quantité qui couvre la ligne** (≤ quantité attendue ; la différence est le reliquat de conversion, P-MULT) ; type de transformation prévu (GALVANISATION ou GPP, P-RET) ; type (L-c) ; auteur, date ; **statut ACTIVE / CONVERTIE / LIBÉRÉE** (transitions contrôlées par trigger) ; libération (voie, motif, par, le) ; lien vers l'affectation créée ; jamais supprimée ; principaux contrôles CT21 doublés en base (CT15). Choix technique (signalé) : une table dédiée plutôt qu'une « nature » dans `affectation_stock` (v7), pour garder séparés le cycle de la réservation et celui de l'affectation ; les deux options respectent tes décisions. | [V Y1, Y1 bis] ; CT21, P-MULT, P-RET |
| DB20 | Capacités des transformateurs (**nouvelle**) | Pour chaque transformateur : GALVANISATION, GPP, ou les deux (P-RET : « un même transformateur peut éventuellement avoir les deux capacités »). La colonne `type` existante et ses valeurs DEBIT et AUTRE sont conservées telles quelles (CT15 : rien n'est supprimé), inutilisées par la 5.6 ; pour un transformateur qui a les deux capacités, la colonne `type` garde une seule valeur et la table des capacités fait foi. Qui crée les transformateurs et déclare leurs capacités : **Q-TRF**. | [V P-RET] ; L-m ; Q-TRF |
| DB21 | Articles : versions et demandes (**nouvelles**) | **Versions d'article**, append-only : article, numéro, date et heure d'enregistrement, auteur, motif, valeurs (méthode, masse, % GALVA, unité de valorisation…) ; création et nouvelle version réservées au SUPERADMIN, contrôlées en base. **Demandes de création** : demandeur, description, date, état, traitée par, le (L-o). La correction de désignation ne crée pas de version : elle est tracée dans l'audit avec l'ancienne et la nouvelle valeur. | [V P-ART, BR §11] ; L-o, L-p |

**Non inclus dans la 0021** : tout le §7.2.

---

## 12. Tests proposés

Nombres vérifiés contre la v5 : ses 57 points regroupaient souvent
plusieurs vérifications. La v6 les découpe en **cas individuels**, chacun
rattaché à une règle de la matrice (§20). Aucun cas n'est ajouté pour
atteindre un total.

- Passage de la v6 (136) à la v7 (142) : +6 cas pour Y1 et Y4 (U22,
  P16, M61 à M64). Les cas liés à X1 (M27, M28, I07, E06) sont
  **redéfinis** selon Y5, sans changer leur nombre.
- **Passage de la v7 (142) à la v8 (174)** : **+32 cas** pour CT1 à CT21
  et Y1 bis (U23 à U26, R11, R12, P17 à P21, M65 à M78, I17 à I21, E09,
  E10). Aucun cas de la v7 n'est supprimé ; ceux que tes décisions
  modifient sont **redéfinis** et marqués « v8 » (liste au tableau
  « Cas redéfinis » ci-dessous).
- *v7 : « le nombre baissera de 3 si le référentiel article n'est pas
  en 5.6 (Y4 bis : R10, M02, I16) » — **SUPERSEDED PAR CT3** : le
  mécanisme de validation est en 5.6 ; ces 3 cas restent.* *(v8 : « si
  P-ART place la création d'article en 5.6 : +2 cas » — décidé le 02/10 :
  11 cas, voir plus bas.)*
- *v8 : « deux cas sont réservés, non comptés, en attente de ta
  décision : M79 (P-RET) et M80 (P-KG-TR) » — tes décisions du 02/10
  permettent de les définir ; ils sont désormais comptés.*
- **Passage de la v8 (174) à la v9 (210)** : **+36 cas** pour tes
  décisions du 02/10 (U27 à U31, R13, R14, S07, S08, P22 à P24, M79 à
  M98, I22, I23, E11, E12). Aucun cas de la v8 n'est supprimé ; ceux que
  tes décisions modifient sont **redéfinis** et marqués « v9 ».
- **Aucun de ces 210 cas n'est écrit ni exécuté à ce stade.** Ce sont
  des tests **proposés** pour le codage. Seuls les 293 tests existants
  ont été exécutés (§13).

| Catégorie | v8 | v9 |
|---|---|---|
| Unitaires (U) | 26 | 31 |
| Repository (R) | 12 | 14 |
| Services — contrat technique (S) | 6 | 8 |
| Permissions (P) | 21 | 24 |
| Métier (M) | 78 | 98 |
| Intégrité (I) | 21 | 23 |
| E2E (E) | 10 | 12 |
| **Total proposés** | **174** | **210** |
| Non-régression | 293 existants + 3 contrôles (§13) |

**Unitaires (U)**

- U01 IPE100 6 m NOIR = 48,6 kg [N1, N2].
- U02 GALVA 6 % = 51,516 kg [N3].
- U03 GPP = 49,572 kg [N4, K19].
- U04 GALVA 0 % défini = 48,6 kg [K20].
- U05 % GALVA non renseigné → demande de compléter, jamais 0 [K20, X8].
- U06 GPP jamais cumulé avec GALVA [K19].
- U07 100 barres GALVA = 5,1516 t [N3].
- U08 **v8** Hors poids (**NOIR/LAC**) : poids déclaré rendu tel quel,
  aucune majoration [O7 ; CT20]. *(v7 : « NOIR ou GPP » — GPP retiré,
  SUPERSEDED PAR CT7 et CT20.)*
- U09 **v8** Hors poids (NOIR/LAC en PIÈCE, ML, M²…) : poids déclaré
  absent → refus [O7 ; CT20]. *(v7 : « hors tonne » — le KG est
  désormais une vente au poids, CT20.)*
- U10 **v8** Vente au poids (TONNE **ou KG**) : poids manuel refusé
  [K18 ; CT20].
- U11 Exemple K4 : achat 2 000 TND, transformation 300 TND, taux 3,40
  (TND pour 1 EUR), transport 50 EUR → 726,47 EUR [K4, X5, Y3].
- U12 Ligne 4,32 t : achat 2 800,5 TND/t, transformation 450 TND/t, taux
  3,40, transport 85,50 EUR/t → 4 499,41 EUR (1 041,53 EUR/t) [K4, X5,
  Y3 ; CT6].
- U13 Un seul arrondi final, aucun arrondi intermédiaire [K13, BR §17].
- U14 Transport tonne : 4,32 t × 85,50 = 369,36 EUR [X2].
- U15 **v9** Transport hors poids (PIÈCE, ML, M²…) = montant total EUR
  saisi sur la ligne du devis ; **aucune conversion fictive en tonnes**
  pour une unité non pondérale [X2, Y2 ; P-KG-TR]. La ligne en KG est
  couverte par M80.
- U16 V = O + avenants (100 + 20 = 120) [K3, O1].
- U17 Reste à livrer = V − livré normal [K15 ; CT].
- U18 **v8** À approvisionner = V − (affecté normal actif non livré +
  réservé pour transformation + livré normal) [CT ; CT21].
- U19 Reliquat 100 / 70 → 30 [X6].
- U20 **v9** Conversion exacte : 25 × 12 m → **exactement** 50 × 6 m
  **attendues** (49 ou 51 pièces attendues refusées) ; 12 m → 12 m :
  25 → 25 ; 12 m → 5 m (pas un multiple exact) refusé [D1 ; CT18,
  CT21]. La quantité qui couvre la ligne peut être inférieure : U27.
  *(v7 : « au plus 200 × 6 m » — SUPERSEDED PAR CT18.)*
- U21 **v8** Hors poids (NOIR/LAC) : prix au poids × poids déclaré
  (2 800,5 TND/t × 0,5 t = 1 400,25 TND) [O7 ; CT20].
- U22 **v8** Ligne GALVA vendue en KG : poids calculé × (1 + % ÷ 100),
  comme la tonne [Y4 ; Y4 bis (ii) réglé par CT20].
- U23 GPP : poids = masse validée × (1 + taux GPP en vigueur ÷ 100) ;
  2 % → 49,572 kg ; aucune valeur GPP par article n'est lue [CT4].
- U24 Taux saisi « 3,40 » relu à l'identique ; 2 300 TND ÷ 3,40 calculé
  exactement à partir du texte saisi ; le taux n'est jamais arrondi
  [CT5].
- U25 Revient unitaire affiché = total ÷ quantité (4 499,41 ÷ 4,32 =
  1 041,53 EUR/t) ; le total n'est jamais recalculé à partir de
  l'unitaire [CT6].
- U26 Coût de transformation en TND/t, TND/kg, TND/pièce, TND/ml ou
  montant total : chacun appliqué dans sa propre unité, un seul arrondi
  final [CT8].
- U27 P-MULT : besoin de 49 × 6 m → **25 barres de 12 m** (arrondi par
  excès) → 50 × 6 m attendues → reliquat de conversion 1.
- U28 P-MULT : besoin de 50 × 6 m → **25 barres de 12 m** → reliquat 0
  (et 51 × 6 m → 26 barres, reliquat 1).
- U29 P-KG-TR : transport séparé du **prix de vente** : changer le
  transport ne change ni le prix de vente ni le chiffre d'affaires de la
  ligne.
- U30 P-KG-TR : transport séparé du **coût d'achat** : changer le
  transport ne change ni le coût d'achat ni le coût de transformation.
- U31 P-KG-TR : transport intégré au **prix de revient prévisionnel** :
  prix de revient = achat + transformation + transport (exemple CT6 :
  4 130,05 EUR hors transport + 369,36 EUR de transport → 4 499,41
  EUR) ; marge prévisionnelle = chiffre d'affaires − prix de revient
  [P-KG-TR ; L-q].

**Repository (R)**

- R01 Client : créer, modifier, lire ; aucune suppression.
- R02 Utilisateur : créer, lire, activer/désactiver.
- R03 Permissions : attribuer, retirer (tracé), droits effectifs.
- R04 Devis : devis, lignes et taux, lecture complète.
- R05 Réservations : créer, annuler, lister les actives par emplacement.
- R06 Commande : depuis le devis, lignes avec origine.
- R07 Avenants : insertion, lecture
  chronologique.
- R08 Affectations : affecté actif non livré par lot, emplacement, ligne
  et type ; résultat prévu.
- R09 Situation : livré par ligne et type.
- R10 **v8** Valeurs article validées : historique complet ; valeur en
  vigueur = dernière validation [CT3].
- R11 Réglage GPP : taux en vigueur à une date donnée ; historique
  complet [CT4].
- R12 Réservations de lots bruts : actives par lot, emplacement et
  ligne ; lien réservation → affectation [CT21].
- R13 BST préparés : lignes, résultat attendu, allocations liées,
  quantité engagée par lot ; capacités d'un transformateur [P-BST,
  P-RET].
- R14 Versions d'article : version en vigueur à une date, historique
  complet ; demandes de création [P-ART].

**Services — contrat technique (S)**

- S01 Une transaction par opération : un échec n'écrit rien (ex. avenant
  + audit).
- S02 Chaque opération sensible écrit une ligne d'audit avec avant/après
  et motif.
- S03 Erreurs métier en français (`core.erreurs`).
- S04 **v9** Numérotation DEV/CMD séquentielle par année ; numéro du BST
  préparé attribué par la numérotation documentaire existante [P-BST].
- S05 **v9** Aucune opération 5.6, **préparation du BST comprise**,
  n'écrit dans le registre des mouvements, dans le CMP ni dans la table
  des lots [P-BST].
- S06 Les lectures (situation, disponibilité) n'écrivent rien.
- S07 Séparation des responsabilités : le module de préparation du BST
  (5.6) n'appelle aucune fonction d'écriture du Stock Service (contrôle
  du code) ; **le mouvement physique relève de la 5.8** [P-BST].
- S08 Séparation des responsabilités : aucune fonction de la 5.6 ne crée
  de lot ; **le nouveau lot transformé relève de la 5.8** [P-BST].

**Permissions (P)**

- P01 Seul le SUPERADMIN crée un compte.
- P02 Seul le SUPERADMIN attribue ou retire une permission ; audité.
- P03 Compte COMMERCIAL sans permission : préparer un devis refusé [O5 ;
  CT2 : le rôle ne donne pas automatiquement tous les droits ; lecture
  L-g : aucune permission tant qu'elle n'est pas attribuée].
- P04 Après attribution de « préparer un devis » : accepté ; après
  retrait : refusé.
- P05 « Consulter » requis pour lire la situation [O5].
- P06 Permission réservée non attribuable à un autre compte [X4 ; CT2].
- P07 Compte nommé « Mohamed » sans rôle SUPERADMIN : refusé [K16, X4].
- P08 **v8** (a) Compte désactivé : toute opération refusée ; (b)
  désactivation ou changement de rôle du **seul** SUPERADMIN refusés
  [CT1 ; L-f]. *(v7 : « SUPERADMIN désactivé : refusé » — avec CT1, le
  seul SUPERADMIN ne peut plus être désactivé.)*
- P09 Affectation refusée à un non-SUPERADMIN, même avec toutes les
  permissions attribuables [N10].
- P10 Avenant refusé à un non-SUPERADMIN [K9, X4].
- P11 Clôture avec reliquat refusée à un non-SUPERADMIN [X4, X6].
- P12 **v9** Modification exceptionnelle du taux d'un devis CONFIRMÉ :
  refusée au commercial, acceptée au SUPERADMIN avec motif, tracée et
  auditée [O3, X7 ; CT5 ; Y6]. Les avenants suivants gardent le taux
  initial : M84. *(v8 : « pas testé tant que Y6 est ouvert » —
  SUPERSEDED PAR Y6.)*
- P13 Correction d'inventaire refusée à un non-SUPERADMIN [K17].
- P14 Annulation d'un devis ou d'une commande confirmée refusée à un
  non-SUPERADMIN [cahier].
- P15 Création ou modification d'un client refusée à un non-SUPERADMIN
  [cahier].
- P16 Réservation d'un lot brut refusée à un non-SUPERADMIN [N10 ; Y1 bis
  (d)].
- P17 Création d'un **deuxième** SUPERADMIN refusée par le service, même
  demandée par le SUPERADMIN [CT1].
- P18 Une permission d'un module ne donne pas ses opérations sensibles
  (ex. « préparer un devis » ne permet ni d'annuler un devis ni de
  modifier un taux confirmé) [CT2].
- P19 Validation d'une valeur article refusée à un non-SUPERADMIN [CT3].
- P20 Modification du réglage GPP refusée à un non-SUPERADMIN [CT4].
- P21 Correction d'une erreur de prix après confirmation refusée à un
  non-SUPERADMIN [CT10].
- P22 Création d'article refusée à un utilisateur opérationnel, même avec
  toutes les permissions attribuables ; il peut sélectionner un article
  existant [P-ART].
- P23 Préparation d'un BST refusée à un non-SUPERADMIN [P-BST ; L-l].
- P24 Nouvelle version d'article, changement d'unité de valorisation et
  correction administrative refusés à un non-SUPERADMIN [P-ART ; L-p].

**Métier (M)**

*Clients et référentiel*

- M01 Client créé ou modifié par le SUPERADMIN, audité ; suppression
  refusée [cahier].
- M02 **v8** Valeurs candidates présentées (dont la masse « MV à
  vérifier »), aucune choisie ; validation SUPERADMIN avec sources
  affichées, motif, auteur, date ; historique [N1, K7 ; CT3].
- M03 **v8** Vente au poids (TONNE ou KG) sans valeur validée → demande
  de compléter [K18 ; CT3, CT20].
- M04 Vente GALVA (au poids) sur un article sans % → demande de
  compléter [X8, Y4].
- M05 **v8** Article sans valeur validée : vente hors poids (NOIR/LAC en
  PIÈCE, ML, M²…) possible, projet non bloqué ; vente en KG ou TONNE
  refusée [K7 ; CT3, CT20].

*Devis*

- M06 Taux saisi à la main, historisé avec auteur [K5 ; CT5].
- M07 Avant CONFIRMÉ : nouveau taux possible, ancien conservé [K5 ;
  CT5].
- M08 **v9** CONFIRMÉ fige taux et conditions : le taux du devis validé
  devient la référence de l'affaire ; modification refusée à
  l'utilisateur opérationnel [O3, X7 ; Y6].
- M09 Devises imposées (vente EUR…) ; toute autre refusée [K22].
- M10 **v8** Transformation prévue OUI : coût obligatoire, 0 seulement
  s'il est saisi, unité obligatoire ; NON : aucun coût demandé [K4 ;
  CT7, CT8].
- M11 **v8** Transport obligatoire sur la ligne du devis, poids de la
  ligne obligatoire hors poids (NOIR/LAC) ; 0 seulement s'il est saisi
  [BR §19, Y2 ; CT20].
- M12 Estimation jamais pré-remplie depuis un achat [O8 ; CT9].
- M13 Devis expiré ni confirmé, ni prolongé ; prolongation avant
  expiration [PROP C5].
- M14 Annulation d'un devis : SUPERADMIN, une cause parmi 8 [cahier] ;
  « Autre » avec commentaire [PROP C4].

*Réservations*

- M15 Réservation informative, non déduite [cahier] ; plafonnée au
  disponible de l'emplacement [PROP C6].
- M16 Réservation annulée, jamais supprimée [PROP C6].

*Commandes*

- M17 Une seule commande par devis [cahier] ; seulement depuis un devis
  CONFIRMÉ [PROP C1].
- M18 Brouillon : sous-ensemble de lignes, quantité libre ; la
  confirmation fige O [PROP C1].
- M19 Annulation d'une commande confirmée : SUPERADMIN, refusée si déjà
  livrée [cahier].

*Avenants et quantités*

- M20 **v8** Avenant +20 : O = 100 inchangée, V = 120, avenant complet
  (ancienne/nouvelle valeur, auteur, date/heure, motif, impact
  quantitatif et financier avant/après) [K3, K9, O1 ; CT10].
- M21 Les 20 d'avenant sont affectables en INITIALE (quantité normale)
  [O1].
- M22 **v8** Cas 2 : ligne AVENANT, O = 0, V = quantité, taux de
  l'affaire, estimations saisies dans l'avenant ; la situation affiche
  « 0 initial + X ajouté par avenant » [K21, O2, X7 ; CT9, CT16].
- M23 **v8** Cas 1 sur une ligne vendue au poids (KG ou TONNE) : poids
  recalculé avec la méthode, la valeur et le taux GPP figés de la ligne ;
  saisie libre du poids refusée [K21 ; CT10 ; L-e].
- M24 **v9** Avenant : aucun nouveau taux demandé ; il utilise le taux de
  la photo du devis validé [O2, X7 ; CT5, Y6].
- M25 Diminution sous le livré refusée [K13].
- M26 Diminution sous l'affecté : désignation explicite des affectations
  à libérer [N7].

*Prix de vente*

- M27 **v8** Y5 : après confirmation, toute modification du prix de
  vente d'une ligne de commande est refusée, y compris par avenant ; seule
  existe la correction d'erreur par le SUPERADMIN (M65) [Y5 ; CT10].
  *(v7 : « sauf décision contraire en Y5 bis » — Y5 bis réglé par
  CT10.)*
- M28 Y5 : au stade du devis (EN_COURS), le prix de vente peut être
  renégocié ; chaque changement est tracé ; il est figé à CONFIRMÉ.
- M29 Une nouvelle ligne identique reprend le prix applicable et ne
  modifie aucun prix existant [K10].
- M30 Prix de vente jamais modifié par un coût d'achat [O8].

*Affectations*

- M31 Lot en état identique chez GMC : accepté, aucun mouvement [N11].
- M32 Lot en état identique chez un transformateur : accepté,
  localisation conservée [N11, K11].
- M33 Plafond = disponible réel par (lot, emplacement) ; double
  affectation refusée [K12, N13].
- M34 **v8** INITIALE (= NORMALE, CT17) jusqu'à V ; au-delà, SUPPLÉMENT avec
  motif obligatoire [O1, cahier ; CT17].
- M35 SUPPLÉMENT refusé tant que le normal n'atteint pas V [O1 ; CT17].
- M36 X9 : supplément enregistré puis avenant +20 → reste SUPPLÉMENT ;
  20 INITIALE supplémentaires possibles.
- M37 X9 : aucune opération ne requalifie un supplément (avenant,
  diminution, clôture, reste d'une réaffectation).
- M38 X3 : 60 affectées sur 100 NOIR 12 m chez le galvanisateur, résultat
  prévu GALVA 12 m, pour une ligne GALVA 12 m → accepté ; aucun lot
  créé, aucun mouvement.
- M39 X3 : les 40 restantes affectables à une autre affaire ; plafond =
  quantité attendue.
- M40 X3 : résultat prévu GALVA 6 m, 200 pièces attendues → 60 pièces
  de 6 m affectées sur une ligne GALVA 6 m ; plafond 200 [CT18].
- M41 X3 : état de la ligne différent du résultat prévu → refusé
  [CT18].
- M42 X3 : retour de transformation d'un lot portant une affectation sur
  résultat prévu → refusé jusqu'à la 5.8 [CT18, CT11].
- M43 **v8** Y1 : lot NOIR 12 m de 100 barres chez GMC ; commande
  CONFIRMÉE ; 25 barres réservées par le SUPERADMIN pour une ligne GALVA
  6 m vendue en KG, 50 pièces attendues → disponible commercial 75,
  stock physique 100 ; aucun mouvement, aucun lot, emplacement inchangé ;
  audit RESERVATION_LOT_BRUT [Y1 ; Y1 bis (a), (c) ; CT21]. (Le signal
  CT13 a désormais son propre cas : M73.)
- M44 Réaffectation 30 sur 100 : origine clôturée, reste de 70 recréé
  (même lot, même emplacement, même type) [cahier, X9] ; typage à la
  destination [PROP C8].
- M45 Libération pour erreur : SUPERADMIN, motif [PROP C9].
- M46 O8 cas A : ajout couvert par un lot existant, affecté à la main ;
  aucune commande fournisseur ; traçabilité [L1].
- M47 Aucune fonction ne choisit un lot (lot obligatoire dans chaque
  appel) [D5].

*Clôture*

- M48 X6 : la demande calcule le reliquat (100 / 70 → 30) et liste les
  affectations ; rien n'est modifié avant la confirmation.
- M49 **v8** X6 : la confirmation libère les affectations et les
  réservations listées (tracées), passe la commande en **SOLDÉE** (aucun
  autre statut), enregistre le reliquat **ligne par ligne** [X6 ; CT19].
- M50 **v8** X6 : motif obligatoire parmi les 4 de CT19 ; « AUTRE » sans
  commentaire refusé [CT19].
- M51 X6 : reliquat jamais converti en livraison (livré reste 70, aucune
  ligne de BL créée).
- M52 X6 : historique des quantités intact ; marchandise libérée = stock
  GMC à son emplacement.
- M53 Signal « entièrement livrée » [cahier ; PROP C10].

*Situation, stock et transformation prévue*

- M54 Situation : O, A, V, supplément, livré, reste, à approvisionner,
  reliquat [K15].
- M55 **v8** Stock A à F par emplacement (F = résultat attendu,
  affectable, non vendable) ; la situation distingue stock GMC, stock
  chez le transformateur, affecté, envoyé/non réceptionné, disponible ;
  quatre notions d'O4 [D5, O4 ; CT12].
- M56 Correction d'inventaire sans PV refusée [K17].
- M57 **v8** Correction avec PV : référence **et date** du PV, auteur,
  date/heure dans l'audit ; PV sans date refusé ; aucun mouvement
  antérieur modifié [K17 ; CT14].
- M58 **v9** Garde-fou : envoi en transformation sous l'affecté, le
  réservé ou l'engagé refusé ; un envoi qui n'exécute pas une ligne de
  BST préparé est refusé pour toute quantité engagée [N13 ; CT11 ;
  P-BST ; L-k].
- M59 Garde-fou : chute ou correction sous l'affecté refusée [N13 ;
  CT11].
- M60 **v9** Préparation d'un BST en 5.6 : lot brut sélectionné,
  disponibilité vérifiée, type de transformation choisi, **résultat
  attendu enregistré** (finition fixée automatiquement, longueur et
  quantité attendues saisies, jamais déduites de « 2x6m »), document
  numéroté à l'état PRÉPARÉ, audit PREPARATION_BST [CT18 ; P-BST,
  P-RET ; lien avec le bon de commande de transformation : Q-BCT]. *(v8 : « à l'établissement d'un BST (BST de test) …
  correspondance avec le type du transformateur : P-RET » — SUPERSEDED
  PAR P-BST et P-RET. v7 : « déclaration … par le SUPERADMIN » sur un
  bon existant — SUPERSEDED PAR CT18.)*
- M61 **v9** Y1 bis (b) et mécanisme : **à la préparation du BST (5.6)**,
  résultat identique → réservation **CONVERTIE** et **conservée dans
  l'historique** ; **nouvelle allocation liée au BST** (même lot, même
  ligne, résultat attendu, quantité qui couvre la ligne, type repris
  selon L-c) ; lien traçable ; audit CONVERSION_RESERVATION_AFFECTATION ;
  aucun lot choisi par le système [CT21 ; P-BST ; L-r].
- M62 **v8** Libération de la réservation par chacune des 4 voies
  (annulation de commande ; clôture avec reliquat ; diminution avec choix
  explicite ; SUPERADMIN avec motif — sans motif refusé) → **LIBÉRÉE**,
  disponible restauré ; audit LIBERATION_AFFECTATION [CT21].
- M63 **v9** Y1 bis (b) : BST dont le résultat attendu diffère de la
  réservation (finition, longueur ou quantité) → **BST refusé**, rien
  n'est écrit [CT18, CT21 ; P-BST ; exécution partielle : L-s].
- M64 **v8** Y4 : ligne **GALVA ou GPP** vendue en PIÈCE, ML ou M² →
  refusée ; en KG ou TONNE → acceptée [Y4 ; CT7 ; précision GPP du
  30/09].
- M65 Correction d'une erreur de prix par le SUPERADMIN : sans motif
  refusée ; prix confirmé jamais réécrit ; enregistrement dans la table
  d'avenants (ancienne et nouvelle valeur, impact financier) ; prix en
  vigueur = prix corrigé ; audit CORRECTION_ERREUR_PRIX [CT10, Y5].
- M66 Réglage GPP : nouveau taux avec date d'effet ; l'ancien reste
  consultable ; un devis EN_COURS calculé après la date d'effet utilise
  le nouveau ; un devis confirmé avant garde l'ancien [CT4].
- M67 Masse « MV à vérifier » : vente au poids refusée, avec demande de
  validation ; après validation SUPERADMIN : acceptée ; % GALVA non
  renseigné jamais lu comme 0 ; 0 % validé accepté [CT3, K20].
- M68 **v9** Modification exceptionnelle du taux d'un devis confirmé : sans
  motif refusée ; avec motif → nouveau taux créé, ancien intact, photo
  du devis inchangée, modification **historisée et auditée**, sans effet
  sur le taux des avenants ni sur les lignes [CT5, CT6 ; Y6].
- M69 Photo complète figée à la confirmation (achat, transformation,
  transport, poids, taux, taux GPP, valeur article, résultat) ; après une
  nouvelle validation de masse, un nouveau taux GPP ou un nouveau taux
  de change, la photo est identique [CT6, CT3, CT4, CT20].
- M70 Résultat attendu d'une ligne de BST figé dès qu'une affectation s'y
  rattache : modification refusée, par l'application et par la base
  [CT18 ; P-BST].
- M71 Coûts estimés recopiés à l'identique du devis vers la commande ;
  aucun pré-remplissage depuis un ancien achat [CT9].
- M72 Garde-fou, réservations comprises : envoi en transformation, chute,
  correction ou retour qui ferait passer le disponible sous l'affecté +
  le réservé → refusé, par l'application et par la base [CT11, CT21].
- M73 Signal « utilisable après transformation » sur un lot brut non
  réservé : ne crée ni réservation, ni affectation, ni mouvement, et ne
  rend pas le produit transformé vendable [CT13].
- M74 Demande d'affectation à cheval sur V : refusée avec l'indication du
  découpage ; aucune affectation créée [CT17 ; L-d].
- M75 Origine du poids enregistrée par ligne : CALCULÉ (méthode, valeur,
  % GALVA ou taux GPP) ; DÉCLARÉ seulement en NOIR/LAC hors poids ;
  DÉCLARÉ refusé pour une vente au poids [CT20].
- M76 **v9** Contrôles de la réservation, un refus par cas : commande non
  confirmée (BROUILLON) ; lot non brut (GALVA) ; lot chez un
  transformateur ; autre article ; aucune transformation nécessaire
  (même état) ; **coupe seule (NOIR 12 m → NOIR 6 m)** ; longueur non
  multiple ; pièces attendues différentes de barres × n ; ligne GALVA ou
  GPP hors KG/TONNE ; quantité supérieure au disponible réel [CT21 ;
  Y1 bis (c) ; P-RET ; « lot brut » : L-b ; refus de la coupe seule :
  application provisoire, à confirmer avec Q-COUPE]. Une quantité de
  ligne non multiple n'est **pas** un refus : M81 (P-MULT).
- M77 **v9** Pendant la réservation : préparation d'un autre BST sur la
  quantité réservée refusée ; affectation de la quantité bloquée à une
  ligne NOIR (vente brute) ou à une autre affaire refusée ; seconde
  réservation au-delà du disponible refusée [CT21 ; Y1 bis (a)].
- M78 Situation : « réservé pour transformation » par ligne (pièces de la
  ligne) et par lot (pièces du lot) ; disponible GMC = physique − affecté
  − réservé, en pièces du lot (100 − 25 = 75) ; « à approvisionner »
  tient compte du réservé [CT21 ; §6.8].
- M79 P-RET : BST de type **GALVANISATION** → finition de retour **GALVA**
  fixée automatiquement ; l'utilisateur ne peut pas en choisir une autre.
  *(Réservé en v8, défini en v9.)*
- M80 P-KG-TR : ligne vendue en KG, **5 000 kg**, transport **100
  EUR/T** → 5 t → **500 EUR** ; prix de vente, prix d'achat et quantité
  commerciale inchangés. *(Réservé en v8, défini en v9.)*
- M81 P-MULT : ligne de 49 × 6 m GALVA ; 25 barres de 12 m réservées ; à
  la préparation du BST : 50 pièces attendues, 49 allouées à la ligne,
  **1 de reliquat de conversion** non affectée et visible dans la
  situation ; rien d'autre n'est créé. (Son entrée réelle en stock GMC à
  la réception : 5.8.) [P-MULT ; L-n, L-u]
- M82 P-MULT : le reliquat de 1 × 6 m est **affecté ultérieurement** à
  une autre affaire, par décision explicite du SUPERADMIN (allocation
  sur le résultat attendu, X3) [P-MULT ; L-k, L-u].
- M83 P-MULT : **aucun choix automatique** : après la conversion, le
  reliquat n'est attribué à personne ; aucune fonction ne l'affecte sans
  désignation explicite de la ligne ; il n'est compté ni comme chute ni
  comme reliquat de commande [P-MULT ; L-u].
- M84 Y6 : après une modification exceptionnelle du taux par le
  SUPERADMIN, **l'avenant suivant utilise toujours le taux initial** du
  devis validé.
- M85 Y6 : **aucun recalcul rétroactif** : anciennes lignes, avenants
  déjà enregistrés et photo du devis strictement identiques avant et
  après la modification.
- M86 P-BST : la préparation d'un BST **ne crée aucun mouvement
  physique** : registre des mouvements, emplacement du lot et stock
  physique inchangés.
- M87 P-BST : la préparation d'un BST **ne crée aucun lot** : nombre de
  lots inchangé ; le résultat attendu n'est pas un lot.
- M88 P-BST : contrôles de la préparation, un refus par cas : lot non
  brut ; quantité supérieure au disponible ou déjà engagée ; longueur
  non multiple ; article différent de la ligne ; transformateur sans la
  capacité demandée [P-BST ; L-k, L-m].
- M89 P-ART : création d'un article par le SUPERADMIN : article créé,
  première version enregistrée, audit CREATION_ARTICLE.
- M90 P-ART : un utilisateur opérationnel enregistre une
  **demande** de création ; aucun article n'est créé ; le SUPERADMIN
  l'accepte (article créé) ou la refuse ; tout est tracé [L-o].
- M91 P-ART : modification à impact métier (masse, % GALVA, unité de
  valorisation) → **nouvelle version historisée** ; l'ancienne reste
  consultable ; audit NOUVELLE_VERSION_ARTICLE.
- M92 P-ART : correction administrative de la désignation → aucune
  nouvelle version ; **audit** avec ancienne valeur, nouvelle valeur,
  utilisateur, date/heure, motif éventuel [L-p].
- M93 P-ART : une commande confirmée **conserve sa photo** : après une
  nouvelle version de l'article, son poids, ses coûts et ses
  caractéristiques sont inchangés.
- M94 P-ART : une nouvelle version d'article **ne recalcule rien dans
  l'historique** : devis confirmés, avenants enregistrés, lots et
  mouvements identiques avant et après ; un devis créé ensuite utilise
  la nouvelle version.
- M95 P-RET : BST de type **GPP** → finition de retour **GPP** fixée
  automatiquement.
- M96 P-RET : transformateur ayant **les deux capacités** : un BST
  GALVANISATION donne GALVA, un BST GPP donne GPP, chez le même
  transformateur.
- M97 P-RET : **finition incohérente refusée** (BST GALVANISATION avec
  une finition GPP ou NOIR ; BST GPP avec GALVA).
- M98 P-RET : **aucun autre type** : un BST de type AUTRE, découpe ou
  perçage est refusé, par l'application et par la base.

**Intégrité (I)**

- I01 21 migrations ; `--fresh` deux fois, empreintes identiques.
- I02 `integrity_check` = ok ; clés étrangères sans anomalie.
- I03 0021 atomique : sur anomalie préalable, rien n'est appliqué
  [CT15].
- I04 REAL refusé dans les nouvelles colonnes `*_minor`.
- I05 **v8** Second SUPERADMIN refusé par la base, **que le premier soit
  actif ou non** [CT1]. *(v7 : « second SUPERADMIN actif » —
  SUPERSEDED PAR CT1.)*
- I06 Avenant immuable (UPDATE, DELETE refusés) [K9 ; CT10].
- I07 Prix de vente d'une ligne de commande confirmée immuable en base
  [Y5 ; DB11].
- I08 Attribution de permission jamais supprimée, retrait tracé [CT2].
- I09 Quantité originale libre en brouillon, figée après confirmation
  [PROP C1].
- I10 Un devis → une commande, contrôlé par la base [cahier].
- I11 Client non supprimable [cahier].
- I12 **v8** Taux immuable (existant) avec auteur obligatoire et texte
  saisi conservé à l'identique [K5 ; CT5].
- I13 Plafond d'affectation par emplacement contrôlé aussi en base
  [K12 ; CT11].
- I14 Correction d'inventaire refusée par la base sans SUPERADMIN [K17 ;
  CT14].
- I15 **v9** `core.audit.ACTIONS_VALIDES` synchronisé avec le CHECK de la
  base (39 actions) [CT].
- I16 **v8** Historique des valeurs article validées immuable (UPDATE,
  DELETE refusés) [CT3].
- I17 Historique du réglage GPP immuable (UPDATE, DELETE refusés) [CT4].
- I18 0021 appliquée à une base contenant des données 5.5 (jeu de
  test) : toutes les lignes existantes reprises, comptages identiques
  avant et après, aucune suppression [CT15].
- I19 Type d'une affectation non modifiable en base (UPDATE refusé)
  [CT17, X9].
- I20 Réservation : jamais supprimée ; transitions limitées à ACTIVE →
  CONVERTIE et ACTIVE → LIBÉRÉE ; une réservation CONVERTIE a exactement
  une affectation liée [CT21].
- I21 Validation d'une valeur article par un non-SUPERADMIN refusée par
  la base [CT3, CT15].
- I22 P-ART : versions d'article immuables (UPDATE, DELETE refusés) ;
  création d'article et nouvelle version par un non-SUPERADMIN refusées
  par la base.
- I23 P-RET, P-BST : en base, type de transformation d'un BST préparé
  limité à GALVANISATION et GPP ; finition attendue cohérente avec le
  type ; ligne figée dès qu'une allocation s'y rattache.

**E2E (E)**

Les livraisons sont simulées par insertion directe de lignes de BL, car
la 5.9 n'est pas codée. Les bons de sortie sont **préparés par le
service de la 5.6** (P-BST) ; seule leur sortie physique, qui relève de
la 5.8, n'est pas jouée. *(v8 : « les bons de sortie sont créés de la
même façon, car la 5.8 n'est pas codée » — SUPERSEDED PAR P-BST.)*

- E01 Devis → CONFIRMÉ → commande → avenant +20 → 120 INITIALE + 5
  SUPPLÉMENT → situation [O1, X9].
- E02 Avenant nouvel article (cas 2) avec le taux de l'affaire [O2, X7].
- E03 O8 cas A : ajout couvert par le stock existant [L1].
- E04 **v9** Y1 + X3 : lot de 100 barres NOIR 12 m chez GMC ; 60 barres
  réservées dès la **commande confirmée** (résultat GALVA 12 m) → BST
  GALVANISATION **préparé en 5.6** avec deux lignes : une ligne de 60
  barres qui désigne la réservation, même résultat attendu → réservation
  CONVERTIE, allocation liée créée ; une ligne de 40 barres non
  réservées, résultat GALVA 12 m → affectées ensuite à une deuxième
  affaire (X3) ; **aucun mouvement, aucun lot** créé par la 5.6 ; les
  100 barres restent physiquement chez GMC [Y1 bis ; CT18, CT21 ;
  P-BST ; L-k, L-r, L-s].
- E05 X6 : clôture complète 100 / 70 / 30.
- E06 **v8** Y5 : prix négocié au stade du devis → CONFIRMÉ → commande
  → avenant +20 au même prix ; toute tentative de modifier le prix est
  refusée ; une erreur de prix est corrigée par le SUPERADMIN avec motif,
  le prix confirmé restant intact dans l'historique [Y5 ; CT10].
- E07 Droits : création de compte → permissions → devis accepté →
  affectation refusée [O5, X4].
- E08 X9 : supplément puis avenant, supplément conservé.
- E09 **v9** CT18 (ton exemple) : commande 50 IPE120 GALVA × 6 m, vendue
  en KG, confirmée ; lot 25 IPE120 NOIR × 12 m chez GMC réservé (50
  pièces attendues) ; BST GALVANISATION **préparé en 5.6** : 25 barres
  12 m → GALVA 6 m automatiquement, 50 pièces → conversion, allocation
  liée ; une finition GPP ou 49 pièces **attendues** sont refusées ;
  aucun mouvement, aucun lot créé par la 5.6 [CT18, CT21, Y1 bis ;
  P-BST, P-RET].
- E10 CT1 + CT2 : installation (premier compte SUPERADMIN) → deuxième
  SUPERADMIN refusé → compte commercial sans aucune permission →
  attribution « préparer un devis » → devis accepté, annulation refusée
  [CT1, CT2 ; L-f].
- E11 P-MULT + P-BST + P-RET : commande confirmée de **49** IPE120 GALVA ×
  6 m, vendue en KG ; lot de **25 × 12 m** NOIR réservé (calcul par
  excès) ; BST GALVANISATION préparé : 50 pièces attendues, 49
  allouées, **1 de reliquat** ; le SUPERADMIN affecte ensuite ce
  reliquat à une deuxième affaire ; à chaque étape : aucun mouvement,
  aucun lot, 25 barres de 12 m toujours physiquement chez GMC [L-k,
  L-u].
- E12 P-ART : demande de création par un commercial → création par le
  SUPERADMIN → validation de la masse → devis → commande confirmée →
  nouvelle version (nouvelle masse) → commande inchangée ; un nouveau
  devis utilise la nouvelle version.

**Tests X1 à X9 et Y1 à Y5 (renvois, identiques dans §18 et §20)**

| Décision | Tests |
|---|---|
| X1 (remplacé par Y5) | voir Y5 |
| X2 + Y2 | U14, U15, M11 |
| X3 | U20, M38 à M42, M60, M70, E04, E09 |
| X4 | P06, P07, P09 à P16, P19 à P21, E07 |
| X5 + Y3 | U11, U12, U24 |
| X6 | U19, M48 à M52, M62, P11, E05 |
| X7 | M08, M24, M68, P12, E02 |
| X8 | U05, M04, M67 |
| X9 | M36, M37, M44, I19, E01, E08 |
| Y1 | M43, M61, M62, M63, M76, M77, M78, P16, E04, E09 |
| Y4 | U22, M04, M64 |
| Y5 | M27, M28, M29, M65, P21, I07, E06 |

**Tests CT1 à CT21 et Y1 bis (renvois, identiques au §0 bis)**

| Décision | Tests |
|---|---|
| CT1 | P08, P17, I05, E10 |
| CT2 | P01 à P06, P18, I08, E07, E10 |
| CT3 | U05, M02, M03, M04, M05, M67, P19, R10, I16, I21 |
| CT4 | U03, U23, M66, P20, R11, I17 |
| CT5 | U24, M06, M07, M08, M24, M68, P12, I12 |
| CT6 | U11, U12, U13, U25, M69 |
| CT7 | M10, M64 |
| CT8 | U26, M10 |
| CT9 | M12, M22, M71 |
| CT10 | M20, M23, M27, M65, P10, P21, I06, I07 |
| CT11 | M58, M59, M72, I13 |
| CT12 | M55 |
| CT13 | M73 |
| CT14 | M56, M57, P13, I14 |
| CT15 | I01, I02, I03, I18 |
| CT16 | M22 |
| CT17 | M34 à M37, M74, I19 |
| CT18 | U20, M40, M41, M60, M63, M70, E09 |
| CT19 | M48 à M52, E05 |
| CT20 | U08, U09, U10, U21, U22, M03, M05, M11, M69, M75 |
| CT21 | U18, M43, M61 à M63, M72, M76 à M78, P16, R12, I20, E04, E09 |
| Y1 bis (a) | M43, M77 |
| Y1 bis (b) | M61, M63, E09 |
| Y1 bis (c) | M43, M76 |
| Y1 bis (d) | P16 |
| Y1 bis — mécanisme | M61, I20 |

**Tests des décisions du 02/10 (renvois, identiques au §0 ter et au
§20)**

| Décision | Tests |
|---|---|
| P-MULT | U20, U27, U28, M76, M81, M82, M83, E11 |
| Y6 | M08, M24, M68, M84, M85, P12 |
| P-BST | M60, M61, M63, M70, M86, M87, M88, S05, S07, S08, P23, R13, E04, E09, E11 |
| P-ART | P22, P24, M89 à M94, I22, R14, E12 |
| P-RET | M60, M76, M79, M95 à M98, I23, E09 |
| P-KG-TR | U15, U29, U30, U31, M80 |

**Ta liste minimale du 02/10, point par point**

| Ton point | Test |
|---|---|
| P-MULT — 49 × 6 m → 25 × 12 m | U27 |
| P-MULT — 50 × 6 m → 25 × 12 m | U28 |
| P-MULT — reliquat 1 × 6 m conservé en stock | M81 (entrée réelle en stock : 5.8) |
| P-MULT — reliquat 1 × 6 m affecté ultérieurement | M82, E11 |
| P-MULT — aucun choix automatique du système | M83 |
| Y6 — taux du devis figé | M08 (existant, adapté) |
| Y6 — avenant utilisant le taux initial | M24 (existant, adapté) |
| Y6 — modification exceptionnelle SUPERADMIN auditée | M68, P12 (existants, adaptés) |
| Y6 — avenant suivant utilisant toujours le taux initial | M84 |
| Y6 — absence de recalcul rétroactif | M85 |
| P-BST — BST prépare sans mouvement physique | M86, S05 |
| P-BST — BST ne crée pas de nouveau lot | M87 |
| P-BST — résultat attendu enregistré | M60 (existant, adapté) |
| P-BST — réservation → nouvelle allocation | M61 (existant, adapté) |
| P-BST — réservation conservée dans l'historique | M61, I20 (existants) |
| P-BST — BST refusé si résultat attendu différent de la réservation | M63 (existant, adapté) |
| P-BST — 5.8 responsable du mouvement physique | S07 (côté 5.6) ; le mouvement lui-même : test de la 5.8 |
| P-BST — 5.8 responsable du nouveau lot | S08 (côté 5.6) ; la création du lot : test de la 5.8 |
| P-ART — création article SUPERADMIN uniquement | M89, I22 |
| P-ART — utilisateur opérationnel ne peut pas créer directement | P22 |
| P-ART — demande de création possible | M90 |
| P-ART — modification métier → nouvelle version | M91 |
| P-ART — correction administrative → audit | M92 |
| P-ART — commande confirmée conserve son snapshot | M93 |
| P-ART — nouvelle version article ne recalcule pas l'historique | M94 |
| P-RET — GALVANISATION → GALVA | M79 |
| P-RET — GPP → GPP | M95 |
| P-RET — transformateur avec GALVA + GPP | M96 |
| P-RET — finition incohérente refusée | M97 |
| P-RET — pas de transformation AUTRE | M98, I23 |
| P-KG-TR — 5 000 KG × 100 EUR/T → 500 EUR | M80 |
| P-KG-TR — transport séparé du prix de vente | U29 |
| P-KG-TR — transport séparé du coût d'achat | U30 |
| P-KG-TR — transport intégré au prix de revient prévisionnel | U31 |
| P-KG-TR — pas de conversion fictive pour une unité non pondérale | U15 (existant, adapté) |

Huit de tes 35 points étaient déjà couverts par un cas de la v8, qui est
adapté ; les autres donnent les 36 cas nouveaux, avec quelques cas
d'accompagnement (droits, base, lecture, scénarios).

**Cas redéfinis en v8** (même numéro, contenu adapté ; aucun supprimé) :
U08, U09, U10, U15, U18, U20, U21, U22, R10, P08, P12, M02, M03, M05,
M10, M11, M20, M22, M23, M27, M34, M43, M49, M50, M55, M57, M60, M61,
M62, M63, M64, I05, I12, I15, I16, E04, E06.

**Cas redéfinis en v9** (même numéro, contenu adapté ; aucun supprimé) :
U15, U20, S04, S05, P12, M08, M24, M58, M60, M61, M63, M68, M76, M77,
I15, E04, E09.

**Trois catégories à ne pas confondre**

| Catégorie | Contenu | État |
|---|---|---|
| Tests existants | Les 293 tests des Phases 1 à 5.5 | **Exécutés le 02/10 : 293 réussis** (commande réelle, §13) |
| Tests proposés pour la 5.6 | Les 210 cas ci-dessus | **Non écrits, non exécutés** : aucun n'est exécutable avant le codage de la 5.6 |
| Tests impossibles même après le codage de la 5.6 | Liste ci-dessous | Ils demandent le développement de la 5.7, 5.8, 5.9 ou 5.10 |

**Tests impossibles avant la 5.8, la 5.9 ou la 5.10** (préparés
seulement) :

- sortie physique d'un BST préparé : mouvement, changement
  d'emplacement, garde-fou à la sortie (5.8) ;
- transformation, résultat réel, **création du lot transformé**,
  réception, rattachement de l'allocation au lot résultant, écarts
  reçu/attendu, levée du blocage du retour (5.8) ;
- entrée réelle du **reliquat de conversion** en stock GMC disponible,
  après la réception (5.8) ;
- livraison interdite avant réception du lot transformé, garde-fou sur
  les livraisons, facturation au prix en vigueur corrigé (5.9) ;
- transport réel, répartition du transport final au poids, marge réelle
  (5.10) ;
- achat effectif des 25 barres de 12 m (5.7).

*v8 : « établissement réel du BST appelant la conversion, dans le flux
de la 5.8 (en 5.6 : BST de test…) » et « effet d'une modification
exceptionnelle du taux … après ta décision sur Y6 » — SUPERSEDED PAR
P-BST et Y6 (02/10) : ces deux tests deviennent possibles en 5.6 (M61,
M84).*

---

## 13. Non-régression

- **NR00 — Exécution réelle du 02/10** : les 293 tests existants ont été
  exécutés tels quels (`pytest tests/ -q`), **293 réussis** en 68
  secondes. Aucun fichier de code ni la base n'ont été modifiés ; cette
  exécution vérifie seulement que le point de départ est sain avant le
  codage. Aucun test de la 5.6 n'existe encore.
- **NR01** — Les 293 tests existants sont conservés et doivent passer.
  - Adaptations prévues, chacune listée au codage, **sans changer une
    seule assertion** :
    - `tests/helpers.py` : l'utilisateur de test devient SUPERADMIN
      (FACT : rôle ADMINISTRATEUR aujourd'hui). FACT vérifié : chaque base
      de test ne crée **qu'un seul** utilisateur, ce qui reste compatible
      avec CT1 (un seul SUPERADMIN) ;
    - les **13 appels** de `corriger_inventaire` (3 fichiers : 11 dans
      `test_phase5_5_stock.py`, 1 dans `test_phase5_5_prix_saisis.py`, 1
      dans `test_phase5_5_valorisation.py`) reçoivent une référence **et
      une date** de PV (K17, CT14) ;
    - CT17 : le code stocké INITIALE est conservé, donc **aucune**
      adaptation des tests qui l'utilisent ;
    - P-ART : le changement d'unité de valorisation devient réservé au
      SUPERADMIN. FACT : les deux fichiers de test qui l'appellent
      (`test_phase5_5_prix_saisis.py`, `test_phase5_5_valorisation.py`)
      utilisent l'utilisateur de test commun, qui devient SUPERADMIN :
      aucune autre adaptation attendue ;
    - P-BST, P-RET : les tests existants créent directement des bons de
      sortie sans type de transformation ni état. La 0021 laisse ces
      colonnes facultatives pour les lignes créées hors du service de la
      5.6 : aucune adaptation attendue, à vérifier au codage ;
    - si la 0021 impose l'EUR au prix de vente (K22) :
      `creer_commande` passe de TND à EUR. FACT vérifié : aucune
      assertion existante ne porte sur la devise d'une ligne de
      commande.
  - Les autres insertions directes des tests restent valides si la 0021
    donne des valeurs par défaut aux nouvelles colonnes. C'est à vérifier
    au codage ; toute adaptation supplémentaire sera signalée. Insertions
    concernées : commande, lignes, affectations, BL, devis, réservation,
    bon de sortie.
- **NR02** — ruff, flake8, mypy (sur le code) sans erreur.
- **NR03** — Comportement 5.5 inchangé hors K17/CT14, garde-fou CT11
  (réservations comprises) et retour bloqué d'un lot portant une
  affectation sur résultat attendu.
- **NR04** — Après la 0021 : intégrité, clés étrangères, 293 tests
  existants et 210 nouveaux cohérents [CT15].

---

## 14. N1 à N15 — définitifs [V]

| N | Règle | Sources |
|---|---|---|
| N1 | Méthode de poids validée par article (kg/ml, kg/m², kg/pièce, autre validée) ; MV = base à vérifier ; comparer, ne jamais choisir silencieusement, validation SUPERADMIN, historique ; progressif, projet non bloqué. **Précisé par CT3** (historique dédié, sources, motif ; masse actuelle = « MV à vérifier »). | N1, K7, CT3 |
| N2 | Tonne : poids calculé ; aucune saisie arbitraire ; méthode manquante → demande de compléter. **Étendu au KG par CT20** (vente au poids). | N2, K18, CT20 |
| N3 | GALVA : poids brut × (1 + %/100) ; trois états ; % obligatoire (et validé, CT3) pour vendre en GALVA ; vente GALVA seulement en KG ou TONNE. | N3, K20, O7, X8, Y4, CT3, CT7 |
| N4 | GPP × 1,02, fixe actuellement, jamais cumulé ; jamais appliqué au poids déclaré. **Précisé par CT4** : le 2 % est un réglage global historisé (date d'effet, SUPERADMIN), sans % par article. « Jamais appliqué au poids déclaré » : **sans objet** depuis la précision GPP du 30/09 et CT7/CT20 (plus de GPP hors poids). | N4, K19, O7, CT4, CT7, CT20 |
| N5 | Devises imposées ; taux saisi par le commercial en TND pour 1 EUR, historisé, figé à CONFIRMÉ, référence de l'affaire et de ses avenants, modifiable exceptionnellement par le SUPERADMIN ; coût EUR = TND ÷ taux ; transport : EUR/t en tonne, montant total EUR saisi sur la ligne du devis hors tonne, avec le poids de la ligne. *(Depuis CT20, « hors tonne » se lit « hors poids » pour le poids : une ligne en KG a un poids calculé.)* **Précisé par CT5** (nouvelle valeur à chaque saisie, auteur, texte exact, devis → taux, motif pour la modification exceptionnelle). **Y6 décidé le 02/10** : les avenants gardent le taux du devis validé, même après une modification exceptionnelle. **P-KG-TR décidé le 02/10** : ligne en KG → KG ÷ 1 000 × EUR/T. | N5, K4, K5, K22, O2, O3, X2, X5, X7, Y2, Y3, CT5 |
| N6 | Quantité originale fixe ; avenants par le SUPERADMIN ; quantité d'avenant = normale ; supplément = au-delà de V, conservé comme supplément. | N6, K3, K15, O1, X9 |
| N7 | Diminution jamais sous le livré ; libération explicite ; marchandise = stock GMC disponible. | N7, K13 |
| N8 | Ligne identique = prix confirmé de la commande ; **aucune renégociation après confirmation**, la négociation se fait au stade du devis ; prix de vente jamais modifié par un coût d'achat ; autre commande = autre prix possible. Erreur de prix après confirmation : correction SUPERADMIN avec motif, pas une renégociation (CT10). | N8, K10, O8, Y5 (X1 SUPERSEDED PAR Y5), CT10 |
| N9 | Réservés au SUPERADMIN et audités : comptes, rôles, droits, permissions ; modifications stratégiques, corrections ; codage, versions, améliorations ; validation des évolutions importantes ; avenants ; clôture avec reliquat. | N9, K9, X4, X6, CT10, CT14 |
| N10 | Affectations et réservations de lots bruts : SUPERADMIN seul pour le moment ; accès définis par compte, module, permission ; rôle COMMERCIAL sans tous les droits automatiquement ; délégation prévue, aucune active. | N10, K8, O5, X4, Y1, Y1 bis (d), CT2 |
| N11 | GMC et transformateurs ; autres emplacements au besoin ; localisation ≠ affectation ; une allocation n'est jamais un mouvement. | N11, K11, O9 |
| N12 | Bon de sortie → situation chez le transformateur → bon de réception → lot transformé ; réservation d'un lot brut dès la confirmation du client, puis affectation automatique avec la transformation (Y1) ; affectation sur résultat prévu dès la 5.6 (X3) ; lot transformé et rattachement en 5.8. **Précisé par Y1 bis et CT18** : dès la commande confirmée ; conversion au BST en affectation liée ; résultat attendu saisi au BST, état de retour imposé. **Précisé par P-BST et P-RET (02/10)** : le BST est préparé en 5.6 sans mouvement, exécuté physiquement en 5.8 ; GALVANISATION → GALVA, GPP → GPP. | N12, K1, O4, X3, Y1, Y1 bis, CT18, CT21, P-BST, P-RET |
| N13 | Disponibilité réelle ; refus des doubles affectations, des dépassements et des mouvements sous l'affecté ; jamais de choix automatique. **Précisé par CT11 et CT21** : affecté **et réservé** ; contrôle en base. | N13, K12, CT11, CT21 |
| N14 | Un seul SUPERADMIN actuellement ; droits par compte et rôle/permission, non simplement par le nom affiché ; délégation future prévue. **Précisé par CT1** : exactement un SUPERADMIN, imposé par l'application et la base. | N14, K16, O5, X4, CT1 |
| N15 | Transformation et changement d'état : nouveau lot à caractéristiques propres ; lot d'origine traçable ; vendable après réception. **Confirmé par P-BST** : le lot transformé n'existe qu'après la transformation/réception en 5.8. | N15, K2, O4, P-BST |

---

## 15. K1 à K22 — définitifs [V]

| K | Règle | Complétée par |
|---|---|---|
| K1 | Flux bon de sortie → situation calculée → bon de réception → stock GMC. | O4, X3, P-BST (préparation en 5.6, sortie physique en 5.8) |
| K2 | Compatibilité directe d'un lot déjà dans l'état demandé ; chemin par transformation ; 12 m jamais directement 6 m. | O4, X3, Y1 |
| K3 | Quantité originale fixe ; avenants ; six grandeurs. | O1 |
| K4 | Prix de revient estimé ; transformation saisie par ligne ; estimation ≠ coût réel. | O7, X5, Y2, Y3 (taux en TND pour 1 EUR, division) |
| K5 | Taux saisi à la main, historisé, figé à la validation de l'offre. | O3, X7, CT5, Y6 (décidé le 02/10) |
| K6 | Hors tonne : poids manuel. | O7 (déclaré, final) ; depuis CT20 : **hors poids** seulement (le KG est au poids), NOIR/LAC |
| K7 | Référentiel progressif, projet non bloqué. | X8, CT3, P-ART (décidé le 02/10) |
| K8 | SUPERADMIN = Mohamed actuellement ; délégation prévue ; aucune active. | O5, X4 |
| K9 | Avenants SUPERADMIN, historisés, avec impact. | O1, X4 |
| K10 | Ligne identique = même prix. Sa partie « renégociation datée » est **SUPERSEDED PAR Y5** (pas de renégociation après confirmation). | Y5, CT10 |
| K11 | Emplacements ; localisation ≠ affectation. | O9 |
| K12 | Contrôles de disponibilité ; aucun choix automatique. | X3, CT11, CT21 |
| K13 | TND millimes, EUR centimes ; arrondi final ; diminution ≥ livré. | — |
| K14 | Aucun nouveau point métier à ouvrir. | Les Y et les points P- (décidés depuis), puis les questions Q- et les lectures L- (§22), sont signalés comme contradictions, lacunes ou lectures à confirmer, sans être tranchés par moi. |
| K15 | Six grandeurs de situation. | O1, X9 |
| K16 | Droits par compte et rôle/permission, non simplement par le nom affiché. | X4 |
| K17 | Corrections d'inventaire : SUPERADMIN, PV signé par la Direction Générale dans l'audit. | X4, CT14 |
| K18 | Tonne : poids calculé. | CT20 (KG aussi) |
| K19 | GPP × 1,02, jamais cumulé. | O7, CT4 (réglage global) |
| K20 | % GALVA : trois états, jamais 0 automatique. | X8, Y4, CT3 |
| K21 | Avenant cas 1 / cas 2 ; ancienne commande intacte. | O1, O2, X7 |
| K22 | Devises imposées. | X5 |

---

## 16. O1 à O9 — définitifs

| O | Statut | Règle |
|---|---|---|
| O1 | VALIDÉ | Quantité d'avenant = quantité normale, identifiable ; supplément = au-delà de V. |
| O2 | VALIDÉ | Avenant = taux de la préparation du devis initial ; aucun nouveau taux. **Confirmé par Y6 (02/10)**, y compris après une modification exceptionnelle du taux. |
| O3 | VALIDÉ | Validation de l'offre = CONFIRMÉ ; taux et conditions figés ; SUPERADMIN seul ensuite. |
| O4 | VALIDÉ | Affectation commerciale possible chez le transformateur ; vendable après réception ; quatre notions. Mise en œuvre : X3. |
| O5 | VALIDÉ | Comptes et accès définis par le SUPERADMIN, par utilisateur, module, permission si nécessaire ; rôle COMMERCIAL sans tous les droits automatiquement. |
| O6 | Supprimé | Devenu CT7. |
| O7 | VALIDÉ | Hors tonne (depuis CT20 : **hors poids**, le KG étant une vente au poids) : poids déclaré obligatoire (saisi au devis, Y2), final, jamais majoré ; sert au poids final, au prix de revient estimatif et, plus tard, à la répartition du transport réel (Y2) ; clause transport EUR/T remplacée par X2/Y2 ; pas de GALVA hors poids (Y4). **Partie GPP (« pas de +2 % » sur un poids déclaré) : sans objet, SUPERSEDED PAR la précision GPP du 30/09 et CT7/CT20** ; poids déclaré seulement en NOIR/LAC (CT20). |
| O8 | VALIDÉ ; partie fournisseur **HORS PÉRIMÈTRE 5.6 (5.7)** | Cas A : lot existant, coût réel, aucun achat (affectation 5.6 ; L1 réglé par ton périmètre du 01/10). Cas B : nouvelle commande fournisseur, nouvelle négociation, nouveau lot et coût ; prix initial jamais écrasé ; prix de vente non modifié. Sa phrase sur une nouvelle négociation client est **SUPERSEDED PAR Y5**. |
| O9 | VALIDÉ | GMC et transformateurs ; autres emplacements au besoin réel. |

---

## 17. C1 à C14

Statuts : **VALIDÉ** ; **VALIDÉ EN PARTIE** (le reste est une [PROP] à
valider) ; **À VALIDER**.

| C | Sujet | Statut | Validé | Reste [PROP] |
|---|---|---|---|---|
| C1 | Devis → commande | VALIDÉ EN PARTIE | Un devis → une commande (cahier) | Seulement depuis un devis CONFIRMÉ ; une seule même si annulée ; lignes d'origine issues du devis (sauf avenant) ; sous-ensemble ; quantité libre en brouillon puis figée. **Question ajoutée en v8** (§28) : si la quantité change en brouillon, poids et estimations recalculés avec les valeurs figées du devis ou celles en vigueur à la confirmation de la commande ? |
| C2 | Unités de vente | VALIDÉ EN PARTIE | Pièces + unité ; TONNE, PIÈCE, ML, M², autres autorisées (K6, O7) ; **KG = vente au poids** (Y4 ; CT20) ; GALVA et GPP seulement en KG ou TONNE (CT7) | Liste initiale TONNE, KG, PIÈCE, ML, M², extensible par le SUPERADMIN ; ML = pièces × longueur ; M² saisi ; prix dans l'unité de vente |
| C3 | Transport | VALIDÉ EN PARTIE | Obligatoire, 0 saisi (BR §19) ; EUR ; EUR/T en tonne, montant total saisi sur la ligne du devis hors tonne, avec le poids (X2, Y2) — hors poids depuis CT20 ; transport final réparti au poids en 5.10 (Y2) | [CT] recalcul sur V (cas 1) ; [PROP] pas de transport estimé sur un supplément. (Ligne en KG : décidé par P-KG-TR le 02/10.) |
| C4 | Annulations | VALIDÉ EN PARTIE | Devis : SUPERADMIN, 8 causes ; commande confirmée : SUPERADMIN, refusée si livrée | Même liste pour la commande ; « Autre » + commentaire ; brouillon annulé par son auteur ; devis confirmé non annulable |
| C5 | Validité du devis | VALIDÉ EN PARTIE | Cycle EN_COURS → CONFIRMÉ / EXPIRÉ / ANNULÉ | Jusqu'à la fin de la date incluse ; prolongation avant expiration ; devis expiré figé |
| C6 | Réservations | VALIDÉ EN PARTIE | Manuelles, optionnelles, informatives | Plafond au disponible de l'emplacement ; annulation, pas de suppression |
| C7 | Suppléments | VALIDÉ EN PARTIE | Au-delà de V (O1) ; motif (cahier) ; SUPERADMIN (N10) ; jamais requalifié (X9) ; type fixé à la création (CT17) | Possible à tout moment tant que la commande est confirmée |
| C8 | Réaffectation | VALIDÉ EN PARTIE | Tracée, motif, reste conservé ; reste du même type (X9) | SUPERADMIN ; typage à la destination selon son V (un supplément déplacé peut y devenir INITIALE ?) ; même lot, même emplacement ; non livré seulement |
| C9 | Libération | VALIDÉ EN PARTIE | Explicite (N7) ; à la clôture (X6) ; réservation de lot brut : 4 voies dont SUPERADMIN avec motif (CT21) | Libération d'une **affectation** pour erreur : SUPERADMIN, motif |
| C10 | Clôture | VALIDÉ EN PARTIE | Signalement « entièrement livrée », SOLDÉE manuelle (cahier) ; clôture avec reliquat X6 : SOLDÉE + motif, reliquat ligne par ligne (CT19) | Définition du signal : livré ≥ V et aucune affectation active non livrée |
| C11 | Situation | VALIDÉ EN PARTIE | Catégories (K15, O1, O4, D5) | Formules [CT] §6.8 |
| C12 | Fiche client | VALIDÉ EN PARTIE | Clients : SUPERADMIN, audit, jamais supprimés | La fiche actuelle suffit ; destination et incoterm repris sur le devis |
| C13 | LAC | VALIDÉ | LAC = NOIR | — |
| C14 | Date de confirmation | À VALIDER | — | Date de confirmation par le client ; validation interne tracée à part |

---

## 18. X1 à X9 — décisions intégrées [V]

| X | Décision | Où c'est intégré | Tests |
|---|---|---|---|
| X1 | **SUPERSEDED PAR Y5** (30/09, 23 h 06) : « pas de renégociation de prix de vente ; commande confirmée, prix de vente confirmé ; la renégociation sera avant validation si elle existe ». Erreur de prix : CT10. | §6.7, DB11 | voir Y5 : M27, M28, M29, M65, P21, I07, E06 |
| X2 | Transport saisi en EUR/T ; tonne : EUR/T × t ; autre unité : aucun poids implicite, montant total EUR saisi manuellement ; aucune conversion cachée. **Précisé par Y2** : saisie sur la ligne du devis, avec le poids de la ligne ; transport final réparti au poids en 5.10. **Complété par P-KG-TR (02/10)** : ligne en KG → KG ÷ 1 000 × EUR/T (M80, U29 à U31). | §6.7, §7.2, DB6 | U14, U15, M11 |
| X3 | A : affectation en 5.6 sur besoin et marchandise identifiés, même chez le transformateur ; aucun lot transformé en 5.6 ; rattachement au lot résultant en 5.8 ; jamais un mouvement. Option A de la v5 reprise telle quelle. **Complété par Y1, Y1 bis et CT18** (réservation d'un lot brut dès la commande confirmée ; résultat attendu saisi au BST, état de retour imposé, conversion exacte). **Précisé par P-BST, P-RET et P-MULT (02/10)** : BST préparé en 5.6, finition fixée par le type de transformation, reliquat de conversion. | §6.3 bis, §6.11, §6.11 bis, DB12, DB17, DB19, DB20, CT18, CT21 | U20, M38 à M42, M60, M70, E04, E09 |
| X4 | Opérations stratégiques de la 5.6 réservées au SUPERADMIN ; délégation future prévue, aucune supplémentaire active ; droits liés au compte et aux permissions, pas au nom. **Précisé par CT1 et CT2.** | §6.19, DB1, DB2 | P06, P07, P09 à P16, P19 à P21, E07 |
| X5 | « coût EUR = Y (TND) × R (taux de change) » ; taux de l'affaire, saisi par le commercial, historisé, modifiable exceptionnellement par le SUPERADMIN ; aucun nouveau taux. **Précisé par Y3** : taux saisi en TND pour 1 EUR, donc R = 1 ÷ taux (division exacte). **Et par CT5** (taux conservé tel que saisi). | §6.2, `core/prix_revient.py` | U11, U12, U24 |
| X6 | A : clôture avec reliquat en une opération contrôlée (demande, calcul, affichage, confirmation, libération, motif) ; reliquat jamais converti en livraison. **Précisé par CT19** (SOLDÉE, 4 motifs, reliquat ligne par ligne). | §6.17, DB8, DB13 | U19, M48 à M52, M62, P11, E05 |
| X7 | Taux saisi, historisé, figé pour l'affaire, utilisé pour les avenants ; jamais remplacé à chaque avenant ; modification exceptionnelle par le SUPERADMIN. **Précisé par CT5** (nouveau taux + motif + audit). **Y6 décidé le 02/10** : la modification exceptionnelle ne change pas le taux des avenants (M84, M85). | §6.2, §6.6, DB4 | M08, M24, M68, P12, E02 |
| X8 | B : % GALVA obligatoire dans la référence article ; hors tonne, poids déclaré final, pas de réapplication ; tonne inchangée. Avec **Y4**, il n'y a plus de GALVA hors poids : la partie « hors tonne » ne se présente plus (**SUPERSEDED PAR Y4**, sans objet). Le % doit être validé (CT3). | §6.9, DB3 | U05, M04, M67 |
| X9 | A : un supplément reste un supplément ; jamais requalifié automatiquement ni rétroactivement ; historique conservé. **Maintenu par CT17.** | §6.13, §6.14, CT17, DB18 | M36, M37, M44, I19, E01, E08 |

Correspondance avec la v5 : tes X1 à X9 répondent aux X1 à X9 de la v5.

- Exception : ton X5 porte sur la **conversion TND/EUR**, alors que le X5
  de la v5 portait sur l'exemple O8 « 10 DT/pièce ». Celui-ci est réglé
  par ta règle « prix de vente conservé en EUR » (§4 de ton message) :
  l'exemple se lit en EUR.
- Le point P1 de la v5 (O8 fournisseur en 5.7) est réglé par ton §5.

**Réponses Y1 à Y5 (30/09, 23 h 06)** : voir §0. Y2 et Y3 sont intégrés
dans X2 et X5 ci-dessus ; Y5 remplace X1 ; Y1 complète X3 ; Y4 complète
X8. **Décisions du 01/10** (CT1 à CT21, Y1 bis) : voir §0 bis et §21.
**Décisions du 02/10** (P-MULT, Y6, P-BST, P-ART, P-RET, P-KG-TR) : voir
§0 ter.

---

## 19. Règles existantes à préserver (contrôle point par point)

| Règle (ton §4) | Préservée dans |
|---|---|
| Absence de FIFO ; affectation manuelle ; aucun choix automatique du lot | §6.10, M47 |
| Localisation physique ≠ affectation ; aucune affectation n'est un mouvement | §6.10, §6.11, M31, M38, S05 |
| Disponibilité réelle calculée | §6.10, M33 |
| Compatibilités article, finition, longueur ; exceptions NOIR/LAC → GALVA/GPP et 12 m → 2 × 6 m | §6.12 (exceptions via transformation, K2 ; réservation Y1), U20, M43 |
| Réception de transformation obligatoire avant disponibilité commerciale du produit transformé | §6.11, §6.16 (F) |
| Vente EUR ; matière TND ; transformation TND ; transport selon X2 | §6.2, §6.7 (X2, Y2) |
| Prix, quantités et avenants historisés ; quantité originale jamais écrasée ; V calculée | §6.6, §6.7 (prix figé à la confirmation, Y5), §6.8, DB9 à DB11 |
| Diminution jamais sous le livré ; libération explicite ; marchandise vers stock GMC | §6.8, M25, M26 |
| Supplément conservé comme supplément | §6.13, §6.14 (X9) |
| Aucune décision automatique | §6.10, §6.17 |
| Clôture avec reliquat ; droits SUPERADMIN ; délégation future | §6.17, §6.19 |
| Aucune modification physique de stock par la 5.6 | §1, S05 |

**Règles que tu as rappelées le 01/10 (« à ne pas oublier »)**

| Règle (tes mots) | Préservée dans |
|---|---|
| Compatibilité : même article ; même finition, sauf NOIR/LAC → GALVA/GPP ; même longueur, sauf multiple exact ; 12 m → 2 × 6 m ; transformation nécessaire = lot brut non directement compatible | §6.12, §6.3 bis, U20, M76 |
| GALVA / GPP : même parcours ; GALVA = masse × (1 + % validé) ; GPP = masse × 1,02 actuellement ; pas de cumul ; KG ou TONNE seulement ; poids calculé selon la méthode validée | §6.9, U02, U03, U06, U23, M64, M67 |
| Réservation ≠ mouvement physique : bloque commercialement ; ne diminue pas le stock physique ; ne change pas l'emplacement ; ne crée pas de lot | §6.3 bis, M43, S05 |
| Affectation ≠ mouvement physique : commerciale ; mouvement physique seulement par les mécanismes des phases correspondantes | §6.10, §6.11, M31, M38, S05 |
| Pas de FIFO : le système ne choisit jamais le lot ; le SUPERADMIN choisit | §6.10, §6.12, M47 |
| 12 m → 6 m : 25 × 12 m peuvent donner 50 × 6 m selon la transformation prévue ; conversion exacte | §6.11, §6.3 bis, U20, E09 |
| Vente confirmée : prix confirmé ; pas de renégociation ; correction d'erreur de saisie par le SUPERADMIN seul, motif, audit complet ; pas de nouvelle négociation | §6.7, DB10, DB11, M27, M65, P21 |

**Règles que tu as posées le 02/10**

| Règle (tes mots) | Préservée dans |
|---|---|
| « BST commercial ≠ mouvement physique » ; « allocation ≠ mouvement physique » | §6.11 bis, M86, S05, S07 |
| « Le lot transformé n'existe qu'au niveau physique après le traitement de la transformation/réception en Phase 5.8 » | §6.11 bis, §28, M87, S08 |
| Reliquat de conversion : « le système ne choisit jamais automatiquement » ; « stock GMC réel, traçable et disponible » ; pas une perte | §6.3 bis, §6.8, M81, M82, M83 |
| Article : « aucun calcul historique ne doit être recalculé silencieusement » ; une commande confirmée garde ses caractéristiques | §6.21, M93, M94 |
| Taux : le taux du devis validé est la référence de l'affaire et de tous ses avenants ; aucun recalcul rétroactif | §6.2, §6.6, M24, M84, M85 |
| Prix de vente, coût d'achat, coût de transformation et transport séparés ; total = prix de revient ; CA − prix de revient = marge | §6.2, §6.7, U29, U30, U31 |
| Deux transformations seulement : GALVANISATION → GALVA ; GPP → GPP | §6.11 bis, M79, M95, M97, M98 |

---

## 20. Matrice de traçabilité

Modules : Cl clients ; Dv devis ; Rs réservations ; Cm commandes ;
Av avenants ; Af affectations ; Si situation ; Dr droits ; Po poids ;
St stock.

Statuts : **VALIDÉ**, **À VALIDER**, **HORS PÉRIMÈTRE** uniquement. Pour
une C « validée en partie » (§17), le statut est À VALIDER tant que sa
[PROP] n'est pas validée.

| ID | Règle (résumé) | Source | Module | Impact DB | Impact service | Tests | Phase | Statut |
|---|---|---|---|---|---|---|---|---|
| D1 | Compatibilité directe ; exceptions via transformation | D1, K2 | Af | DB12, DB17 | affectation | M31, M40, U20 | 5.6 | VALIDÉ |
| D2 | Poids commercial tonne / hors tonne | D2 | Po | DB6 | poids_vente | U01 à U10 | 5.6 | VALIDÉ |
| D3 | Devises par type de prix | D3 | Dv | DB6, DB9 | devis | M09 | 5.6 | VALIDÉ |
| D4 | Modification historisée (avenants) | D4 | Av | DB10 | commande | M20 | 5.6 | VALIDÉ |
| D5 | Lots manuels, pas de FIFO, catégories A à F | D5 | Af, Si | DB12, DB17 | affectation, situation | M47, M55 | 5.6 | VALIDÉ |
| D6 | SUPERADMIN par compte | D6 | Dr | DB1 | droits | P07 | 5.6 | VALIDÉ |
| N1 | Méthode de poids validée, progressive | N1, CT3 | Po | DB3 | référentiel | M02, M05, M67 | 5.6 | VALIDÉ |
| N2 | Tonne = calcul | N2 | Po | DB6 | poids_vente | U10, M03 | 5.6 | VALIDÉ |
| N3 | GALVA % validé ; GALVA seulement au poids | N3, Y4, CT3, CT7 | Po | DB3, DB6 | poids_vente | U02, U04, U05, M64 | 5.6 | VALIDÉ |
| N4 | GPP : réglage global, 2 % aujourd'hui ; seulement au poids | N4, CT4, CT7 | Po | DB3 | poids_vente | U03, U06, U23, M66 | 5.6 | VALIDÉ |
| N5 | Devises, taux, transport | N5 | Dv | DB4, DB6 | devis | M06 à M11 | 5.6 | VALIDÉ |
| N6 | Quantités, avenants, supplément | N6 | Cm, Av | DB9, DB10 | commande | U16, M20, M21 | 5.6 | VALIDÉ |
| N7 | Diminution, libération explicite | N7 | Cm, Af | DB12 | commande, affectation | M25, M26 | 5.6 | VALIDÉ |
| N8 | Prix des lignes identiques ; pas de renégociation après confirmation | N8, Y5 | Cm | DB11 | commande | M27 à M30 | 5.6 | VALIDÉ |
| N9 | Opérations sensibles SUPERADMIN | N9 | Dr | DB2 | droits | P01 à P15 | 5.6 | VALIDÉ |
| N10 | Affectations et réservations SUPERADMIN ; accès par permission | N10, Y1 | Af, Dr | DB2 | droits, affectation | P09, P16 | 5.6 | VALIDÉ |
| N11 | Localisation ≠ affectation | N11 | Af | DB12 | affectation | M31, M32 | 5.6 | VALIDÉ |
| N12 | Flux de transformation ; réservation d'un lot brut | N12, Y1, Y1 bis | Af, St | DB12, DB17, DB19 | affectation, stock | M38, M42, M43, M60, M61 | 5.6 / 5.8 | VALIDÉ |
| N13 | Garde-fou (affecté + réservé) | N13, CT11 | St, Af | DB12, DB15, DB19 | stock | M58, M59, M72, I13 | 5.6 | VALIDÉ |
| N14 | Un seul SUPERADMIN, par compte | N14, CT1 | Dr | DB1 | droits | P07, P08, P17, I05 | 5.6 | VALIDÉ |
| N15 | Nouveau lot après transformation | N15 | St | — | (5.8) | M38 | 5.8 | VALIDÉ |
| K1 | Bon de sortie → réception | K1 | St | DB17 | stock | M42, M55 | 5.6 / 5.8 | VALIDÉ |
| K2 | Compatibilité directe | K2 | Af | DB12 | affectation | M43 | 5.6 | VALIDÉ |
| K3 | Grandeurs de quantité | K3 | Cm | DB9, DB10 | commande | U16 | 5.6 | VALIDÉ |
| K4 | Prix de revient estimé | K4 | Dv | DB6 | prix_revient | U11, U12, U21 | 5.6 | VALIDÉ |
| K5 | Taux saisi, figé | K5 | Dv | DB4 | devis | M06, M07, M08 | 5.6 | VALIDÉ |
| K6 | Poids manuel hors tonne | K6 | Po | DB6 | poids_vente | U08 | 5.6 | VALIDÉ |
| K7 | Référentiel progressif | K7, CT3 | Po | DB3 | référentiel | M05, I16 | 5.6 | VALIDÉ |
| K8 | Délégation prévue, aucune active | K8 | Dr | DB2 | droits | P06 | 5.6 | VALIDÉ |
| K9 | Avenants SUPERADMIN | K9 | Av | DB10 | commande | M20, P10, I06 | 5.6 | VALIDÉ |
| K10 | Ligne identique = même prix (renégociation remplacée par Y5) | K10, Y5 | Cm | DB11 | commande | M29 | 5.6 | VALIDÉ |
| K11 | Emplacements | K11 | Af | DB12 | affectation | M32 | 5.6 | VALIDÉ |
| K12 | Contrôles de disponibilité | K12 | Af | DB12 | affectation | M33, I13 | 5.6 | VALIDÉ |
| K13 | Monnaies ; diminution ≥ livré | K13 | Dv, Cm | — | prix_revient, commande | U13, M25 | 5.6 | VALIDÉ |
| K14 | Aucun nouveau point métier | K14 | — | — | — | — | — | VALIDÉ |
| K15 | Situation, six grandeurs | K15 | Si | — | situation | M54 | 5.6 | VALIDÉ |
| K16 | Droits par compte et rôle/permission | K16 | Dr | DB2 | droits | P07 | 5.6 | VALIDÉ |
| K17 | Corrections d'inventaire + PV | K17 | St | DB15 | stock | M56, M57, P13, I14 | 5.6 | VALIDÉ |
| K18 | Tonne = calcul | K18 | Po | DB6 | poids_vente | U10, M03 | 5.6 | VALIDÉ |
| K19 | GPP non cumulé | K19 | Po | DB3 | poids_vente | U06 | 5.6 | VALIDÉ |
| K20 | % GALVA trois états | K20 | Po | DB3 | poids_vente | U04, U05 | 5.6 | VALIDÉ |
| K21 | Avenant cas 1 / cas 2 | K21 | Av | DB9, DB10 | commande | M22, M23 | 5.6 | VALIDÉ |
| K22 | Devises imposées | K22 | Dv | DB6, DB9 | devis | M09 | 5.6 | VALIDÉ |
| O1 | Avenant = quantité normale | O1 | Cm, Af | DB9, DB12 | commande, affectation | M20, M21, M34 | 5.6 | VALIDÉ |
| O2 | Taux du devis initial pour les avenants | O2 | Av | DB9 | commande | M22, M24 | 5.6 | VALIDÉ |
| O3 | Validation de l'offre = CONFIRMÉ | O3 | Dv | DB5 | devis | M08, P12 | 5.6 | VALIDÉ |
| O4 | Affectation avant réception | O4 | Af | DB12, DB17 | affectation | M38, M39, M55 | 5.6 | VALIDÉ |
| O5 | Droits par compte, module, permission | O5 | Dr | DB2 | droits | P03 à P05, E07 | 5.6 | VALIDÉ |
| O6 | Supprimé (devenu CT7) | — | — | — | — | — | — | HORS PÉRIMÈTRE |
| O7 | Poids déclaré final ; sert au prix de revient et à la répartition du transport | O7, Y2 | Po | DB6 | poids_vente, prix_revient | U08, U09, U21 | 5.6 (répartition 5.10) | VALIDÉ |
| O8 | Fournisseur : nouveau lot, prix jamais écrasé ; cas A = affectation d'un lot existant | O8 | Af (cas A) ; achats | — (5.7) | affectation (cas A) ; achat (5.7) | M12, M30, M46, E03 | 5.7 (cas A : 5.6, L1) | HORS PÉRIMÈTRE (partie fournisseur) |
| O9 | Emplacements au besoin | O9 | Af | — | — | — | plus tard | VALIDÉ |
| C1 | Devis → commande | C1 | Cm | DB8, DB9b | commande | M17, M18, I09, I10 | 5.6 | À VALIDER |
| C2 | Unités de vente (reste [PROP]) | C2, Y4, CT7, CT20 | Dv | DB6 | devis | M64, U22 | 5.6 | À VALIDER |
| C3 | Transport (reste [PROP]) | C3, X2 | Dv | DB6 | devis | M11 | 5.6 | À VALIDER |
| C4 | Annulations | C4 | Dv, Cm | DB5, DB8 | devis, commande | M14, M19, P14 | 5.6 | À VALIDER |
| C5 | Validité du devis | C5 | Dv | DB5 | devis | M13 | 5.6 | À VALIDER |
| C6 | Réservations | C6 | Rs | DB7 | devis | M15, M16 | 5.6 | À VALIDER |
| C7 | Suppléments | C7 | Af | DB12 | affectation | M34 à M37 | 5.6 | À VALIDER |
| C8 | Réaffectation | C8 | Af | DB18 | affectation | M44 | 5.6 | À VALIDER |
| C9 | Libération | C9 | Af | DB12 | affectation | M45 | 5.6 | À VALIDER |
| C10 | Clôture | C10, X6 | Cm | DB8, DB13 | commande | M48 à M53 | 5.6 | À VALIDER |
| C11 | Formules de situation | C11 | Si | — | situation | U17, U18, M54 | 5.6 | À VALIDER |
| C12 | Fiche client | C12 | Cl | DB16 | client | M01 | 5.6 | À VALIDER |
| C13 | LAC = NOIR | D1 | Af | — | affectation | — | 5.6 | VALIDÉ |
| C14 | Date de confirmation | C14 | Cm | DB8 | commande | — | 5.6 | À VALIDER |
| X1 | Renégociation → lignes identiques : **remplacé par Y5**, sans objet | X1 | — | — | — | (voir Y5) | — | HORS PÉRIMÈTRE |
| X2 | Transport EUR/T ; hors poids montant total (ligne en KG : P-KG-TR) | X2, Y2 | Dv | DB6 | devis, prix_revient | U14, U15, M11 | 5.6 | VALIDÉ |
| X3 | Affectation chez le transformateur (option A v5) | X3, Y1, CT18 | Af | DB12, DB17 | affectation, stock | U20, M38 à M42, M60, M70, E04, E09 | 5.6 + rattachement 5.8 | VALIDÉ |
| X4 | Opérations réservées SUPERADMIN | X4 | Dr | DB1, DB2 | droits | P06, P07, P09 à P16, P19 à P21, E07 | 5.6 | VALIDÉ |
| X5 | Coût EUR = Y × R, avec R = 1 ÷ taux (TND pour 1 EUR) | X5, Y3 | Dv | DB4 | prix_revient | U11, U12, U24 | 5.6 | VALIDÉ |
| X6 | Clôture avec reliquat | X6 | Cm | DB8, DB13 | commande | U19, M48 à M52, M62, P11, E05 | 5.6 | VALIDÉ |
| X7 | Taux figé pour l'affaire | X7 | Dv, Av | DB4 | devis, commande | M08, M24, M68, P12, E02 | 5.6 | VALIDÉ |
| X8 | % GALVA obligatoire ; pas de réapplication | X8, Y4 | Po | DB3 | poids_vente | U05, M04, M67 | 5.6 | VALIDÉ |
| X9 | Supplément conservé | X9 | Af | DB12, DB18 | affectation | M36, M37, M44, I19, E01, E08 | 5.6 | VALIDÉ |
| Y1 | Lot brut réservé dès la confirmation client, affecté automatiquement avec la transformation (précisé par Y1 bis : dès la commande confirmée ; affectation liée créée au BST, réservation conservée) | Y1 | Af | DB12, DB19 | affectation | M43, M61, M62, M63, M76, M77, M78, P16, E04, E09 | 5.6 (+ 5.8) | VALIDÉ |
| Y1 bis | (a) bloquante ; (b) conversion au BST ; (c) commande confirmée ; (d) SUPERADMIN seul ; affectation liée, réservation conservée | Y1 bis (01/10) | Af | DB12, DB19 | affectation | M43, M61, M63, M76, M77, P16, I20, E09 | 5.6 (+ 5.8, P-BST) | VALIDÉ |
| Y2 | Transport hors poids et poids saisis sur la ligne du devis (ligne en KG : P-KG-TR) ; transport final réparti au poids | Y2 | Dv | DB6 | devis | U15, M11 | 5.6 (répartition 5.9/5.10) | VALIDÉ |
| Y3 | Taux saisi en TND pour 1 EUR ; coût EUR = TND ÷ taux | Y3 | Dv | DB4 | prix_revient | U11, U12 | 5.6 | VALIDÉ |
| Y4 | GALVA seulement pour une vente en KG ou TONNE | Y4 | Po | DB6 | poids_vente, devis | U22, M04, M64 | 5.6 (+ 5.8) | VALIDÉ |
| Y4 bis | (i) unité de la ligne ; (ii) KG = vente au poids ; (iii) validation des valeurs article en 5.6 | CT3, CT7, CT20 | Po | DB3, DB6 | référentiel, poids_vente | R10, M02, I16, U22, M64, M75 | 5.6 | VALIDÉ |
| Y5 | Pas de renégociation après confirmation ; négociation au stade du devis | Y5 | Dv, Cm | DB11 | devis, commande | M27, M28, M29, M65, P21, I07, E06 | 5.6 | VALIDÉ |
| Y5 bis | Erreur de prix après confirmation : correction SUPERADMIN, motif, audit | CT10 | Cm | DB10, DB11 | commande | M65, P21 | 5.6 | VALIDÉ |
| Y6 | Tous les avenants gardent le taux du devis validé ; modification exceptionnelle historisée et auditée, sans effet sur le taux des avenants, les lignes ni les avenants enregistrés (libellé à confirmer : Y6-L) | Y6 (02/10) | Dv, Av | DB4, DB6 | devis, commande | M08, M24, M68, M84, M85, P12 | 5.6 | VALIDÉ |
| L1 | Cas A d'O8 = affectation 5.6 | périmètre du 01/10 | Af | — | affectation | M46, E03 | 5.6 | VALIDÉ |
| CT1 | Exactement un SUPERADMIN (application + base) | CT1 | Dr | DB1 | droits | P08, P17, I05, E10 | 5.6 | VALIDÉ |
| CT2 | Comptes, modules, permissions ; délégation future | CT2 | Dr | DB2 | droits | P01 à P06, P18, I08, E07, E10 | 5.6 | VALIDÉ |
| CT3 | Historique dédié des valeurs article ; MV à vérifier | CT3 | Po | DB3 | référentiel | U05, M02, M03, M04, M05, M67, P19, R10, I16, I21 | 5.6 | VALIDÉ |
| CT4 | Réglage GPP global historisé (2 %) | CT4 | Po | DB3 | référentiel, poids_vente | U03, U23, M66, P20, R11, I17 | 5.6 | VALIDÉ |
| CT5 | Taux : nouvelle valeur à chaque saisie, exact, devis → taux | CT5 | Dv | DB4, DB5 | devis, prix_revient | U24, M06, M07, M08, M24, M68, P12, I12 | 5.6 | VALIDÉ |
| CT6 | Calcul au total, un arrondi ; photo figée | CT6 | Dv | DB6 | prix_revient, devis | U11, U12, U13, U25, M69 | 5.6 | VALIDÉ |
| CT7 | Transformation prévue OUI/NON ; GALVA/GPP en KG ou TONNE | CT7 | Dv | DB6 | devis, poids_vente | M10, M64 | 5.6 | VALIDÉ |
| CT8 | Unité du coût de transformation | CT8 | Dv | DB6 | prix_revient | U26, M10 | 5.6 | VALIDÉ |
| CT9 | Coûts estimés recopiés ; jamais depuis un achat | CT9 | Cm | DB9 | commande | M12, M22, M71 | 5.6 | VALIDÉ |
| CT10 | Avenants append-only ; correction d'erreur de prix SUPERADMIN | CT10 | Av, Cm | DB10, DB11 | commande | M20, M23, M27, M65, P10, P21, I06, I07 | 5.6 | VALIDÉ |
| CT11 | Garde-fou affecté/bloqué (application + base) | CT11 | St | DB12, DB19 | stock | M58, M59, M72, I13 | 5.6 (livraisons 5.9) | VALIDÉ |
| CT12 | Envoyé non réceptionné, depuis le stock chez les transformateurs | CT12 | Si | — | situation | M55 | 5.6 | VALIDÉ |
| CT13 | Signal « utilisable après transformation », informatif | CT13 | Si | — | situation | M73 | 5.6 | VALIDÉ |
| CT14 | Correction d'inventaire : PV (référence, date), SUPERADMIN | CT14 | St | DB15 | stock | M56, M57, P13, I14 | 5.6 | VALIDÉ |
| CT15 | 0021 transactionnelle, additive, données reprises | CT15 | — | toutes | — | I01, I02, I03, I18 | 5.6 | VALIDÉ |
| CT16 | Ligne AVENANT, quantité initiale 0 | CT16 | Cm, Av | DB9 | commande | M22 | 5.6 | VALIDÉ |
| CT17 | Type NORMALE/SUPPLÉMENT fixé à la création | CT17 | Af | DB12 | affectation | M34 à M37, M74, I19 | 5.6 | VALIDÉ |
| CT18 | Résultat attendu au BST ; état de retour imposé ; conversion exacte ; figé | CT18 | Af, St | DB17 | affectation | U20, M40, M41, M60, M63, M70, E09 | 5.6 (exécution 5.8) | VALIDÉ |
| CT19 | Clôture : SOLDÉE + motif ; reliquat par ligne | CT19 | Cm | DB8, DB13 | commande | M48 à M52, E05 | 5.6 | VALIDÉ |
| CT20 | Poids, unité, origine par ligne ; DÉCLARÉ = NOIR/LAC hors poids | CT20 | Po | DB6, DB9 | poids_vente | U08, U09, U10, U21, U22, M03, M05, M11, M69, M75 | 5.6 | VALIDÉ |
| CT21 | Réservation d'un lot brut : contenu, contrôles, effets, conversion, libération, audit, situation | CT21 | Af, Si | DB12, DB19 | affectation, situation | U18, M43, M61 à M63, M72, M76 à M78, P16, R12, I20, E04, E09 | 5.6 (+ 5.8) | VALIDÉ |
| P-BST | La 5.6 prépare le BST (lot, résultat attendu, comparaison, conversion, document) ; la 5.8 exécute (sortie physique, mouvement, lot transformé, réception) | P-BST (02/10) | Af, St | DB17, DB19 | bst, affectation | M60, M61, M63, M70, M86, M87, M88, S05, S07, S08, P23, R13, E04, E09, E11 | 5.6 (exécution 5.8) | VALIDÉ |
| P-ART | Création d'article par le SUPERADMIN ; demande de création ; version pour toute modification à impact métier ; correction administrative auditée ; commande confirmée inchangée | P-ART (02/10) | Po | DB21, DB3 | référentiel, unité | P22, P24, M89 à M94, I22, R14, E12 | 5.6 | VALIDÉ |
| P-RET | Deux transformations : GALVANISATION → GALVA, GPP → GPP ; le type choisi dans le BST fixe la finition ; un transformateur peut avoir les deux capacités | P-RET (02/10) | Af | DB17, DB20 | bst | M60, M76, M79, M95 à M98, I23, E09 | 5.6 | VALIDÉ |
| P-KG-TR | Ligne en KG : KG ÷ 1 000 × EUR/T ; composants du prix de revient séparés | P-KG-TR (02/10) | Dv | DB6 | prix_revient | U15, U29, U30, U31, M80 | 5.6 | VALIDÉ |
| P-MULT | Approvisionnement par excès (49 × 6 m → 25 × 12 m) ; reliquat de conversion jamais attribué automatiquement | P-MULT (02/10) | Af | DB19 | affectation, conversion_longueur | U20, U27, U28, M76, M81, M82, M83, E11 | 5.6 (achat 5.7, stock réel 5.8) | VALIDÉ |
| Y6-L | Libellé « Y6 = A » : la règle écrite correspond à l'option (b) de la v8 | §22 | Dv | — | — | M84 | 5.6 | À VALIDER |
| Q-COUPE | 12 m → 6 m sans galvanisation ni GPP (ligne NOIR 6 m) | §22 | Af | DB19 | affectation | M76 | 5.6 ? | À VALIDER |
| Q-BCT | Bon de commande de transformation exigé par la base pour tout BST | §22 | Af | DB17 | bst | M60 | 5.6 / 5.8 | À VALIDER |
| Q-ANNUL | Annulation d'un BST préparé avant sa sortie physique | §22 | Af | DB17 | bst | (à écrire après décision) | 5.6 | À VALIDER |
| Q-TRF | Création des transformateurs et de leurs capacités | §22 | Af | DB20 | bst | M88, M96 (+2 si oui) | 5.6 ? | À VALIDER |
| L-a à L-v | Lectures dérivées de tes décisions (§22) | §22 | divers | divers | divers | P03, P08, P23, P24, M23, M61, M63, M74, M76, M81 à M83, M88, M90, M92, E04, E10, E11… | 5.6 | À VALIDER |

---

## 21. CT1 à CT21 — tous VALIDÉS (01/10)

*Titre v7 : « CT1 à CT21 — aucun validé » — SUPERSEDED PAR tes décisions
du 01/10.*

Le contenu détaillé de chaque décision est au §0 bis. Ce tableau garde la
proposition de la v7 pour l'historique et indique ce que ta décision a
changé.

| CT | Ta décision (01/10) | Proposition de la v7 (historique) | Ce qui change |
|---|---|---|---|
| CT1 | OUI : exactement un SUPERADMIN, application + base ; deuxième refusé | Un seul SUPERADMIN **actif** ; transmission = désactiver l'un, activer l'autre | **SUPERSEDED PAR CT1** : contrôle sur tous les SUPERADMIN, actifs ou non ; plus de transmission « désactiver/activer » ; conséquences proposées en L-f |
| CT2 | OUI | Catalogue, attributions, rôle sans permission automatique, marque « réservé » | Validé, avec les modules, les droits initiaux = situation actuelle et la délégation future sans refonte |
| CT3 | OK | Historique immuable des paramètres ; dépendait de Y4 bis (iii) | Validé et précisé : sources affichées, motif, méthode extensible, « MV à vérifier », trois états du % GALVA, SUPERADMIN, jamais rétroactif |
| CT4 | A | « GPP 1,02 = paramètre historisé » | Validé : réglage unique 2 %, date d'effet, SUPERADMIN, pas de % par article ; GALVA et GPP même parcours |
| CT5 | OK | Ligne immuable avec auteur ; nouveau taux avant CONFIRMÉ ; commande sans taux propre ; modification exceptionnelle : Y6 | Validé et précisé : convention TND pour 1 EUR, taux exact, devis → taux, motif ; Y6 restait ouvert le 01/10, **décidé le 02/10** (§0 ter) |
| CT6 | OK | Calcul exact au total ; instantané à CONFIRMÉ « proposé » | Validé : photo complète figée ; unitaire affiché = total ÷ quantité |
| CT7 | OK | Indicateur « transformation prévue » ; jamais de 0 implicite | Validé ; **en plus** : GALVA et GPP imposent KG ou TONNE |
| CT8 | OK | Unité du coût obligatoire ; liste d'unités à fixer | Validé : TND/t, TND/kg, TND/pièce, TND/ml, montant total |
| CT9 | OK | Tel quel | Validé |
| CT10 | OK | Table d'avenants unique, immuable ; « aussi pour une intervention sur devis CONFIRMÉ » ; plus d'avenant de prix | Validé et précisé : impacts avant/après ; interventions sur **commande** confirmée ; correction d'erreur de prix SUPERADMIN ; poids recalculé. Pour le devis CONFIRMÉ : lecture **L-j** (le taux du devis suit CT5) |
| CT11 | OK | Garde-fou N13 sur tous les mouvements ; livraison en 5.9 | Validé : affecté **ou bloqué** ; application + base ; envoi, chute, correction, retour |
| CT12 | OK | Situation E calculée en 5.6 | Validé : cinq notions distinguées |
| CT13 | OK | Signal informatif pour un lot brut non réservé | Validé : ne crée rien, ne rend rien vendable |
| CT14 | OK | Référence et date du PV ; SUPERADMIN service + base | Validé : + auteur, date/heure, audit complet ; aucune modification directe du stock |
| CT15 | OK | 0021 atomique, additive, valeurs par défaut | Validé et précisé : données reprises, contrôles en base, cohérence après migration |
| CT16 | OK | Ligne AVENANT, O = 0 | Validé : affichage « 0 initial + X ajouté » |
| CT17 | OK | INITIALE jusqu'à V, sinon SUPPLÉMENT ; jamais requalifié | Validé : type fixé à la création ; X9 maintenu ; libellé NORMALE (code INITIALE conservé) |
| CT18 | OK, avec précision | Résultat prévu sur la ligne de bon de sortie, « déclaré par une fonction SUPERADMIN tant que la 5.8 ne crée pas les bons » ; quantité attendue « ≤ » | **SUPERSEDED PAR CT18** : résultat attendu renseigné **à l'établissement du BST** ; état de retour imposé (GALVA, GPP) ; conversion **exacte** ; répartition 5.6/5.8 : P-BST, **décidé le 02/10** (préparation en 5.6, sortie physique en 5.8) ; finition fixée par le type de transformation (P-RET) |
| CT19 | OK | « SOLDÉE ou statut propre » | **SUPERSEDED PAR CT19** : SOLDÉE, pas de statut propre ; 4 motifs |
| CT20 | OK | Origine DÉCLARÉ/CALCULÉ, unité, méthode et % | Validé et précisé : DÉCLARÉ seulement en NOIR/LAC hors poids ; GALVA/GPP toujours calculés |
| CT21 | OK | Ligne d'`affectation_stock` de nature « réservation » ; conversion « même ligne ou ligne liée » | Validé avec Y1 bis : **ligne liée** (SUPERSEDED PAR Y1 bis, mécanisme) ; statuts ACTIVE / CONVERTIE / LIBÉRÉE ; stockage en table dédiée (DB19, choix technique signalé) |

Aucun CT n'est supprimé.

---

## 22. Contradictions résiduelles et précisions à confirmer

**Situation au 02/10.**

- Décidés le 02/10 (§0 ter) : **P-MULT, Y6, P-BST, P-ART, P-RET,
  P-KG-TR**. Leurs blocs de la v8 sont **conservés ci-dessous pour
  l'historique**, chacun précédé de ta décision.
- **Restent ouverts** — de vrais points non décidés :
  - **Y6-L** : confirmation du libellé de Y6 (ta règle écrite correspond
    à l'option (b) de la v8, pas à (a)) ;
  - **Q-COUPE** : passer de 12 m à 6 m sans galvanisation ni GPP ;
  - **Q-BCT** : le bon de commande de transformation que la base exige
    pour tout BST ;
  - **Q-ANNUL** : annulation d'un BST préparé avant sa sortie physique ;
  - **Q-TRF** : qui crée les transformateurs et déclare leurs capacités ;
  - les **lectures L-a à L-v** : L-a à L-j viennent de la v8 et ne sont
    pas citées dans ton message du 02/10 ; L-k à L-v sont nouvelles ;
  - les propositions **C** (§17), elles non plus pas citées le 02/10.
- Comme toujours, je ne tranche rien ; pour chaque point ouvert, ma
  proposition figure en premier.

*Situation au 01/10 (v8), conservée pour l'historique :*

- Réglés le 30/09 : Y2, Y3 ; Y1, Y4, Y5 dans leur principe.
- Réglés le 01/10 : **Y1 bis** (toutes ses précisions), **Y4 bis** (i) et
  (ii) par CT7/CT20, (iii) par CT3 pour la validation, **Y5 bis** par
  CT10, **L1** par ton périmètre, et **CT1 à CT21**.
- Les blocs Y1 bis, Y4 bis, Y5 bis et L1 de la v7 sont **conservés
  ci-dessous pour l'historique**, chacun précédé de sa décision.
- **Restent ouverts** :
  - **Y6 — POINT MÉTIER ENCORE OUVERT** (tu m'as demandé de ne pas
    choisir à ta place) ;
  - cinq points apparus en intégrant tes décisions : **P-BST, P-ART,
    P-RET, P-KG-TR, P-MULT** ;
  - des **lectures dérivées** (L-a à L-j) : je les propose, tu les
    confirmes ou les corriges ;
  - les propositions **C** (§17).
- Comme toujours, je ne tranche rien ; pour chaque point ouvert, ma
  proposition figure en premier, **sauf pour Y6**, où les deux options
  sont présentées sans préférence.

**Y1 bis — Réservation d'un lot brut : quatre précisions — RÉGLÉ LE
01/10** : (a) OUI ; (b) au BON DE SORTIE TRANSFORMATION ; (c) OUI ; (d)
OUI ; mécanisme : nouvelle affectation liée + réservation conservée.
L'autre possibilité de (b) (« à la réception ») est **SUPERSEDED PAR Y1
bis (b)**. *Texte v7 conservé :*

- **FACT.**
  - Ta décision : « il peut être réservé dès la confirmation client et
    avec la transformation il sera automatiquement affecté ».
  - Règles à respecter :
    - « aucune décision automatique du système » (ton §4 de la v6) ;
    - « le système ne choisit jamais automatiquement les lots » (K12,
      D5) ;
    - « seul le SUPERADMIN effectue les affectations » (N10).
  - La seule « réservation » existante est celle du devis, **informative**
    (cahier).
  - Aucun code ne crée encore de bon de sortie : ce sera la 5.8.
- **PROPOSITION.**
  - (a) La réservation est **bloquante**, déduite du disponible. Sinon, un
    autre usage du lot pourrait rendre l'affectation automatique
    impossible.
  - (b) « Avec la transformation » = **au bon de sortie**, quand la ligne
    du bon reçoit un résultat prévu identique à la réservation (cohérent
    avec X3). Autre possibilité : à la réception de transformation
    (5.8) ; dans ce cas, la réservation reste une réservation jusqu'à la
    5.8.
  - (c) « Confirmation client » = commande **CONFIRMÉE**.
  - (d) Réservation posée par le **SUPERADMIN**, comme une affectation.
  - Compatibilité avec « aucune décision automatique » : le lot et la
    quantité sont choisis par l'humain au moment de la réservation. La
    conversion ne choisit rien : même lot, même quantité, même état
    prévu, et elle est tracée.
- **IMPACT.** CT21, DB12, M43, M61 à M63, P16, E04. Si (b) = réception,
  la conversion se code en 5.8.
- **POINT À VALIDER.** Mohamed :
  - la réservation bloque-t-elle le lot (a) ?
  - l'affectation automatique se fait-elle au bon de sortie ou à la
    réception (b) ?
  - « confirmation client » veut-il dire commande confirmée (c) ?
  - la réservation est-elle réservée au SUPERADMIN (d) ?

**Y4 bis — Galvanisation en KG ou TONNE : trois précisions — RÉGLÉ LE
01/10** : (i) unité de vente de la ligne (CT7 ; l'autre possibilité,
l'unité de valorisation de l'article, est **SUPERSEDED PAR CT7**) ; (ii)
KG = vente au poids (CT20) ; (iii) validation des valeurs article en 5.6
(CT3) — reste P-ART. *Texte v7 conservé :*

- **FACT.**
  - Ta décision : « la galvanisation sera effectuée que sur un article
    dont son unité de vente soit kg ou tonne ».
  - Dans le logiciel, l'article porte une **unité de valorisation** (KG,
    ML, UNITE, TONNE ; BR §16), pas une unité de vente. L'unité de vente
    se choisit **sur chaque ligne** de devis (C2).
  - Les unités de vente citées jusqu'ici sont TONNE, PIÈCE, ML et M² ; le
    KG n'y figurait pas. BR §15 : « tonnes pour les ventes au poids ».
  - Ta question Y4 initiale (référentiel article minimal en 5.6) n'a pas
    reçu de réponse.
- **PROPOSITION.**
  - (i) La règle se contrôle sur l'**unité de vente de la ligne** : une
    ligne GALVA doit être vendue en KG ou en TONNE. Autre possibilité :
    sur l'unité de valorisation de l'article.
  - (ii) Une vente en **KG** est une vente au poids, comme la tonne : poids
    calculé par la méthode, jamais saisi ; prix au kg, avec conversion
    exacte kg ↔ t (BR §18).
  - (iii) Le **référentiel article minimal** est dans la 5.6 : création
    d'article par le SUPERADMIN ; méthode de poids et % GALVA validés
    avec historique ; contrôle du changement d'unité. Sans lui, aucune
    vente en tonne ni en GALVA n'est possible.
- **IMPACT.** DB6, C2, U22, M64. Le point (iii) touche DB3,
  `referentiel_article_service`, R10, M02, I16 ; s'il est refusé, −3
  tests.
- **POINT À VALIDER.** Mohamed : (i) ligne ou article ? (ii) le KG se
  traite-t-il comme la tonne ? (iii) le référentiel minimal est-il en
  5.6 ?

**Y5 bis — Erreur de saisie du prix après confirmation — RÉGLÉ LE 01/10
PAR CT10** : option (b), correction par le SUPERADMIN, motif obligatoire,
audit complet, « ce n'est PAS une nouvelle négociation commerciale ».
L'option (a) est **SUPERSEDED PAR CT10**. L'IMPACT annoncé (« exception
éventuelle dans le trigger DB11 ») n'est plus nécessaire : la correction
passe par la table d'avenants (DB10), DB11 reste strict. *Texte v7
conservé :*

- **FACT.**
  - Y5 : « commande confirmée prix de vente confirmé ».
  - N9 réserve les « corrections » au SUPERADMIN.
  - Cahier : une commande confirmée ne s'annule que par le SUPERADMIN, et
    jamais si elle est déjà livrée.
- **PROPOSITION.** Deux options :
  - (a) Aucune modification possible. Une erreur se corrige par
    l'annulation de la commande (si rien n'est livré), puis un nouveau
    devis.
  - (b) Le SUPERADMIN peut corriger une **erreur de saisie**. Ce n'est pas
    une renégociation : motif obligatoire, ancienne valeur conservée,
    tracé comme un avenant de correction.
- **IMPACT.** Exception éventuelle dans le trigger DB11 ; test M27.
- **POINT À VALIDER.** Mohamed, une erreur de prix constatée après
  confirmation : (a) annulation et nouveau devis, ou (b) correction par
  le SUPERADMIN avec motif ?

**Y6 — DÉCIDÉ LE 02/10** : « tous les avenants futurs utilisent le même
taux de change que le devis initial » ; la modification exceptionnelle
est historisée et auditée, ne modifie pas le taux des avenants et ne
recalcule rien. C'est le contenu de l'option (b) ci-dessous ; l'option
(a) est **SUPERSEDED PAR Y6 (02/10)**. Le libellé « Y6 = A » de ton
message est à confirmer : **Y6-L** plus bas. *Texte v8 conservé :*

**Y6 — Effet d'une modification exceptionnelle du taux — POINT MÉTIER
ENCORE OUVERT** *(titre de la v8)*

- **FACT.**
  - X7 : le taux est « figé pour l'affaire ; utilisé pour les avenants et
    calculs futurs … Seul le SUPERADMIN peut effectuer une modification
    exceptionnelle ».
  - CT5 (01/10) : « Les avenants utilisent ce même taux » (celui figé à
    la confirmation) ; « Une modification exceptionnelle par SUPERADMIN :
    crée un nouveau taux ; exige un motif obligatoire ; est auditée
    complètement » ; et : « Le point Y6 … reste à identifier comme point
    ouvert si aucune décision explicite n'a encore été enregistrée. Ne pas
    inventer sa réponse. »
  - CT6 (01/10) : « Un changement futur de masse, taux ou paramètre
    article ne doit pas modifier le devis confirmé. » Donc, quelle que
    soit ta réponse, **la photo du devis confirmé garde l'ancien taux**.
  - O2 : « avenant = taux de la préparation du devis initial ; aucun
    nouveau taux » (à revoir si tu choisis (a)).
  - Aucune décision explicite sur Y6 n'est enregistrée : pas de réponse
    le 30/09 ; point laissé ouvert le 01/10.
- **PROPOSITION** (deux options, **présentées sans ordre de
  préférence** ; je ne choisis pas) :
  - (a) le nouveau taux, historisé avec motif et date, sert aux avenants
    **postérieurs** à la modification ; la photo du devis confirmé garde
    l'ancien (CT6). C'est la proposition déjà formulée : « le nouveau taux
    vaut pour la suite, tandis que l'offre confirmée conserve
    l'ancien » ;
  - (b) les avenants gardent **toujours** le taux figé à la confirmation ;
    la modification exceptionnelle est enregistrée et tracée seulement.
    *La v7 décrivait (b) comme servant « à corriger l'offre elle-même » ;
    avec CT6, la photo de l'offre confirmée ne change pas : sous (b), la
    modification n'aurait donc d'effet sur aucun calcul.*
- **IMPACT.** CT5 ; O2 (sous (a)) ; lien devis → taux (DB4, DB5) : sous
  (a), un avenant postérieur utilise le nouveau taux ; sous (b), toujours
  celui de la confirmation ; `devis_service`, `commande_service` ; test
  P12 (sa partie Y6 n'est pas écrite).
- **POINT À VALIDER.** Mohamed, après une modification exceptionnelle du
  taux par le SUPERADMIN, les avenants suivants utilisent-ils (a) le
  nouveau taux, ou (b) toujours le taux figé à la confirmation ?

**L1 — Cas A d'O8 — RÉGLÉ LE 01/10** par ton périmètre (« 5.6 : …
affectations » ; « 5.7 = achats / commandes fournisseurs / réceptions »).
*Texte v7 conservé :*

- **FACT.** Ton §5 de la v6 range « si article disponible dans le stock
  GMC : utiliser le stock existant et son lot » dans la partie
  fournisseur d'O8, en 5.7.
- **PROPOSITION.** L'**affectation** d'un lot existant, utilisée dans ce
  cas, est celle de la 5.6, déjà dans le périmètre. Le choix « stock
  disponible → lot existant / indisponible → achat » et tout le côté
  fournisseur restent en 5.7.
- **IMPACT.** M46, E03.
- **POINT À VALIDER.** Mohamed, confirmes-tu cette lecture ?

**P-BST — DÉCIDÉ LE 02/10** : responsabilités strictement séparées. La
5.6 sélectionne le lot, vérifie, définit le résultat attendu, compare,
convertit la réservation et prépare le document ; elle ne crée ni
mouvement ni lot transformé. La 5.8 exécute la sortie physique, le
mouvement, la transformation, le lot transformé et la réception. Ma
proposition v8 (« fonction codée en 5.6, appelée par la 5.8 dans la même
opération que l'envoi physique ») et son autre possibilité (« tout en
5.8 ») sont **SUPERSEDED PAR P-BST (02/10)**. Les lectures (i) et (ii)
deviennent L-r et L-s ; (iii) est confirmée ; (iv) est sans objet.
*Texte v8 conservé :*

**P-BST — Ce que la 5.6 code du mécanisme du bon de sortie
transformation (périmètre)**

- **FACT.**
  - CT18 : « Le résultat attendu est renseigné au moment de
    l'établissement du BON DE SORTIE TRANSFORMATION. »
  - Y1 bis (b) : « Lorsque le BST est établi : le système compare le
    résultat prévu du BST avec la réservation ; si identique : conversion
    automatique ; si différent : BST refusé. »
  - Ta liste du 01/10 : « 5.8 = transformations / bons de sortie et
    réception de transformation ».
  - Aucun code ne crée de BST aujourd'hui ; seuls les tests en insèrent.
    La base ne contient aucune donnée.
  - X3 = A (validé) : l'affectation sur marchandise chez un transformateur
    se fait en 5.6, sur le résultat attendu d'une ligne de BST.
- **PROPOSITION.**
  - La 5.6 crée les structures (DB17, DB19) et code, dans
    `affectation_service`, une fonction qui enregistre le résultat
    attendu d'une ligne de BST, le contrôle (état de retour imposé,
    conversion exacte), le compare à la réservation et convertit. Elle
    est testée avec des BST de test. La 5.8 l'appellera en établissant
    les BST, dans la même opération que l'envoi physique.
  - Lectures liées : (i) la ligne du BST **désigne** la réservation
    qu'elle exécute (rien n'est déduit) ; (ii) une exécution **partielle**
    d'une réservation est refusée (« le système reprend exactement ce qui
    a été réservé ») : pour envoyer moins, le SUPERADMIN libère la
    réservation avec motif et en crée une nouvelle ; (iii) la fonction ne
    s'utilise **qu'au moment où la ligne du BST est établie**, jamais
    après coup (sinon on retrouverait la « déclaration après coup »
    remplacée par CT18) ; (iv) dans cette opération unique, la
    réservation exécutée est convertie **avant** le contrôle du
    garde-fou CT11, qui ne la compte donc pas deux fois.
  - Autre possibilité : tout le mécanisme en 5.8. La 5.6 ne ferait alors
    ni la conversion, ni l'affectation X3 sur résultat attendu, qui
    passerait elle aussi en 5.8.
- **IMPACT.** §2, §6.3 bis, §6.11, §7.2, DB17, DB19, `affectation_service`
  ; M60, M61, M63, M70, E04, E09. Avec l'autre possibilité, ces cas
  passent en 5.8 et X3 (validé en 5.6) est à revoir.
- **POINT À VALIDER.** Mohamed : la fonction de comparaison et de
  conversion est-elle codée en 5.6 et appelée par la 5.8 ? Confirmes-tu
  (i) à (iv) ?

**P-ART — DÉCIDÉ LE 02/10** (« P-ART = B ») : création par le SUPERADMIN
uniquement ; demande de création par les utilisateurs ; modification à
impact métier = nouvelle version historisée ; correction administrative
auditée ; commande confirmée inchangée (§6.21). La v8 n'avait pas
d'option « B » ; j'ai intégré ton texte, dont les tests sont dans la
5.6. *Texte v8 conservé :*

**P-ART — Création d'article et changement d'unité d'article
(périmètre)**

- **FACT.** BR §11 : création d'article réservée à Mohamed (Phase 5.5).
  Aucun service de création d'article n'existe.
  `unite_valorisation_service` ne vérifie que l'existence de
  l'utilisateur, alors que BR §11 et §16 font du changement d'unité une
  dérogation de Mohamed. La base ne contient aucun article, et un devis
  a besoin d'articles. CT3 règle la **validation** des valeurs article,
  pas la création ni le changement d'unité. Ta liste du 01/10 ne cite pas
  les articles.
- **PROPOSITION.** En 5.6 : création d'article par le SUPERADMIN (audit
  CREATION_ARTICLE) et contrôle SUPERADMIN du changement d'unité. Autre
  possibilité : dans une phase que tu choisiras.
- **IMPACT.** +1 action d'audit (36) ; +2 cas de test ;
  `referentiel_article_service`, `unite_valorisation_service`.
- **POINT À VALIDER.** Mohamed : création d'article et contrôle du
  changement d'unité en 5.6, oui ou non ?

**P-RET — DÉCIDÉ LE 02/10** : deux transformations seulement ;
GALVANISATION → GALVA ; GPP → GPP ; finition fixée automatiquement par
le type choisi dans le BST ; un transformateur peut avoir les deux
capacités ; aucun type AUTRE, découpe ou perçage. Mes propositions v8
(i) à (iv) sont **SUPERSEDED PAR P-RET (02/10)** : (i) ce n'est pas le
type du transformateur qui décide ; (ii) et (iii) DEBIT et AUTRE sont
hors périmètre ; (iv) n'est pas repris (Q-BCT). *Texte v8 conservé :*

**P-RET — État de retour attendu : cas que CT18 ne couvre pas**

- **FACT.**
  - CT18 : « L'état de retour n'est pas libre. Si transformateur =
    galvanisateur : retour obligatoire = GALVA. Si transformation GPP :
    retour obligatoire = GPP. »
  - Le schéma classe les transformateurs en GALVA, GPP, DEBIT et AUTRE
    (`transformateur.type`). CT18 ne dit rien pour DEBIT et AUTRE, ni pour
    un même transformateur qui ferait GALVA et GPP.
  - CT21 parle de « transformation possible » sans dire si une **coupe
    seule** (NOIR 12 m → NOIR 6 m) en fait partie.
  - La ligne du bon de commande de transformation porte déjà une
    « finition demandée » (FACT, schéma).
- **PROPOSITION.**
  - (i) Galvanisateur = transformateur de type GALVA ; « transformation
    GPP » = transformateur de type GPP.
  - (ii) DEBIT : état de retour = finition de départ (seule la longueur
    change, en multiple exact) ; une réservation pour une coupe seule est
    donc possible.
  - (iii) AUTRE : aucun état de retour défini, donc ni réservation ni
    affectation sur résultat attendu tant que tu n'as pas défini sa
    règle.
  - (iv) L'état de retour attendu du BST est égal à la finition demandée
    de la ligne du bon de commande de transformation liée.
- **IMPACT.** DB17 ; contrôles CT21 ; M60 ; M79 (réservé).
- **POINT À VALIDER.** Mohamed : confirmes-tu (i) à (iv) ? En
  particulier : une coupe seule peut-elle être réservée, et ton
  galvanisateur fait-il aussi le GPP ?

**P-KG-TR — DÉCIDÉ LE 02/10** : KG ÷ 1 000 = tonnes ; tonnes × EUR/T =
transport prévisionnel (5 000 kg, 100 EUR/T → 500 EUR) ; composants du
prix de revient séparés. C'est l'option (a) ; l'option (b) est
**SUPERSEDED PAR P-KG-TR (02/10)**. *Texte v8 conservé :*

**P-KG-TR — Transport d'une ligne vendue en KG**

- **FACT.** X2 : « tonne : EUR/T × t ; autre unité : aucun poids
  implicite, montant total EUR saisi manuellement ; aucune conversion
  cachée ». Y2 : hors tonne, montant total **et poids de la ligne**
  saisis. CT20 et tes règles du 01/10 : le KG est une vente au poids,
  poids calculé. Pour une ligne en KG, le poids est donc calculé (CT20,
  plus récent et plus précis, l'emporte sur la saisie du poids de Y2 :
  contradiction n° 2 ci-dessous), mais **le transport n'est pas
  tranché**.
- **PROPOSITION.** (a) Comme la tonne : transport = EUR/T × (poids en kg ÷
  1 000), conversion exacte et affichée. (b) Comme les autres unités :
  montant total EUR saisi sur la ligne.
- **IMPACT.** `core/prix_revient.py`, DB6, M80 (réservé).
- **POINT À VALIDER.** Mohamed : pour une ligne vendue en KG, (a) ou (b) ?

**P-MULT — DÉCIDÉ LE 02/10** : approvisionnement par excès ; 49 × 6 m →
25 × 12 m → 50 × 6 m ; 49 affectés ; 1 restant, stock GMC réel, jamais
attribué automatiquement. C'est l'option (a) ; les options (b) et (c)
sont **SUPERSEDED PAR P-MULT (02/10)**. *Texte v8 conservé :*

**P-MULT — Quantité de ligne qui n'est pas un multiple exact**

- **FACT.** La conversion est exacte : une barre de 12 m donne exactement
  deux barres de 6 m (ta règle « 12 m → 6 m », CT18, CT21). Une ligne
  peut demander un nombre impair de barres de 6 m (ex. 49). CT17 : au-delà
  de la quantité en vigueur, SUPPLÉMENT + motif. Ni CT18 ni CT21 ne disent
  ce que devient la pièce en trop.
- **PROPOSITION.**
  - (a) Réserver 25 barres (50 pièces attendues) : 49 couvrent la ligne ;
    la 50e n'est affectée à personne et devient, après la réception
    (5.8), du stock GMC disponible. C'est ma proposition.
  - (b) Réserver 24 barres (48 pièces) ; la 49e vient d'un autre lot.
  - (c) Réserver 25 barres ; la 50e est affectée à la ligne en
    SUPPLÉMENT, avec motif.
- **IMPACT.** Contrôle « quantité attendue compatible » (CT21) ; L-c ;
  M76.
- **POINT À VALIDER.** Mohamed : (a), (b) ou (c) ?

**Y6-L — Libellé « Y6 = A » : à confirmer**

- **FACT.**
  - Dans la v8, l'option (a) de Y6 était : « le nouveau taux … sert aux
    avenants postérieurs à la modification » ; l'option (b) : « les
    avenants gardent toujours le taux figé à la confirmation ».
  - Ton message du 02/10 dit « Y6 = A », puis écrit la règle : « tous les
    avenants futurs utilisent le même taux de change que le devis
    initial » ; la modification exceptionnelle « ne modifie pas le taux
    applicable aux avenants de cette affaire ». C'est le contenu de (b).
  - Cette règle écrite est répétée dans ta vérification de cohérence
    (« tous les avenants utilisent ce taux ») et dans ta liste de tests
    (« avenant suivant utilisant toujours le taux initial »).
- **PROPOSITION.** J'ai intégré la **règle écrite**, qui est détaillée et
  répétée trois fois ; je lis la lettre « A » comme un simple libellé.
- **IMPACT.** Si tu voulais au contraire l'option (a) de la v8 : §6.2,
  §6.6, M24, M84 et M85 sont à inverser.
- **POINT À VALIDER.** Mohamed : confirmes-tu que la règle est bien « tous
  les avenants gardent le taux du devis validé, même après une
  modification exceptionnelle » ?

**Q-COUPE — Passer de 12 m à 6 m sans galvanisation ni GPP**

- **FACT.**
  - P-RET : « GMC n'a actuellement que deux types de transformation :
    GALVANISATION, GPP » ; « ne pas introduire de type AUTRE, découpe,
    perçage ou autre transformation dans cette phase ».
  - P-MULT : « lorsqu'une quantité commerciale est exprimée en barres de
    6 m, l'approvisionnement peut être réalisé en barres de 12 m », sans
    préciser la finition.
  - Ton exemple CT18 fait le passage 12 m → 6 m **chez le galvanisateur**.
  - K2 : « le lot brut 12 m ne doit jamais être considéré directement
    disponible comme 6 m ».
  - Une ligne GALVA ou GPP porte un nombre de barres même quand elle est
    vendue en KG ou TONNE (C2 ; ton exemple « 50 IPE120 GALVA × 6 m ») :
    P-MULT s'y applique sans difficulté. La question ne concerne que les
    lignes **NOIR ou LAC**.
  - Pour une ligne **NOIR 6 m** servie par des barres NOIR de 12 m, aucune
    transformation du périmètre actuel ne fait la coupe.
- **PROPOSITION.** En 5.6, P-MULT s'applique quand le passage 12 m → 6 m
  se fait dans une GALVANISATION ou un GPP. Une ligne NOIR 6 m ne reçoit
  que des lots NOIR 6 m (compatibilité directe). La coupe seule reste
  hors périmètre, comme tu l'as décidé.
- **Autre possibilité.** Tu me dis comment se fait cette coupe (par qui,
  avec quel document), et je l'ajoute à l'analyse.
- **IMPACT.** §6.3 bis, §6.12, M76.
- **POINT À VALIDER.** Mohamed : une ligne NOIR 6 m peut-elle être servie
  par des barres NOIR de 12 m, et si oui, comment ?

**Q-BCT — Bon de commande de transformation**

- **FACT.** Dans la base actuelle, tout bon de sortie transformation doit
  être rattaché à un **bon de commande de transformation** (lien
  obligatoire), et ce bon de commande peut porter une commande client.
  Aucun code ne crée ce bon de commande aujourd'hui. Ta décision P-BST ne
  cite que le BST.
- **PROPOSITION.**
  - (a) En 5.6, le BST est préparé **sans** bon de commande de
    transformation. En pratique : la commande passée au transformateur
    serait émise plus tard, en 5.8, au moment de l'envoi. C'est ma
    proposition : elle n'ajoute rien à la 5.6 au-delà de ta décision.
  - (b) La 5.6 prépare aussi le bon de commande de transformation, en
    même temps que le BST.
- **IMPACT.** Avec (a), la base doit accepter un BST sans bon de
  commande (DB17 : le lien devient facultatif, sans rien supprimer) ;
  `bst_service` ; M60.
- **POINT À VALIDER.** Mohamed : (a) ou (b) ?

**Q-ANNUL — Annulation d'un BST préparé avant sa sortie physique**

- **FACT.** P-BST sépare la préparation (5.6) de la sortie physique
  (5.8). Entre les deux, un BST préparé peut devenir faux (erreur de
  lot, commande annulée ou clôturée). Aucun document n'est jamais
  supprimé (règle existante). Le résultat attendu est figé dès qu'une
  allocation s'y rattache (CT18). Une réservation CONVERTIE ne revient
  pas en arrière.
- **PROPOSITION.** Tant que la sortie physique n'a pas eu lieu, le
  SUPERADMIN peut **annuler** un BST préparé, avec motif. Ses allocations
  sont libérées explicitement et tracées ; la quantité engagée redevient
  disponible ; la réservation reste CONVERTIE dans l'historique ; pour
  recommencer, on crée une nouvelle réservation ou un nouveau BST. Si la
  commande est annulée ou clôturée avec reliquat, les allocations du BST
  figurent dans la liste à libérer (X6).
- **IMPACT.** DB17 (état « annulé »), `bst_service`, audit existant
  ANNULATION_DOCUMENT, cas de test à écrire après ta décision.
- **POINT À VALIDER.** Mohamed : un BST préparé et non sorti peut-il être
  annulé par le SUPERADMIN, avec motif, en libérant ses allocations ?

**Q-TRF — Transformateurs et leurs capacités**

- **FACT.** P-RET : « un même transformateur peut éventuellement avoir les
  deux capacités ». La base ne contient aucun transformateur, et aucun
  code ne permet d'en créer un ni de dire ce qu'il sait faire. Or un BST
  ne peut pas être préparé sans transformateur.
- **PROPOSITION.** En 5.6, le SUPERADMIN crée les transformateurs et
  déclare leurs capacités (GALVANISATION, GPP ou les deux) ; chaque
  création ou modification est auditée.
- **Autre possibilité.** Cette gestion est placée en 5.8 ; la 5.6 ne
  pourrait alors préparer un BST que lorsque la 5.8 existera.
- **IMPACT.** DB20 ; une action d'audit de plus (40) ; deux cas de test
  de plus ; M88, M96.
- **POINT À VALIDER.** Mohamed : la création des transformateurs et de
  leurs capacités est-elle faite en 5.6, par le SUPERADMIN ?

**Lectures dérivées de tes décisions (L-a à L-v)** — ce ne sont pas des
règles nouvelles mais ma façon d'appliquer tes décisions là où elles ne
disent pas tout. Je les applique dans l'analyse ; tu les confirmes ou
les corriges. **L-a à L-j** viennent de la v8 : ton message du 02/10 ne
les cite pas, je ne les ai donc pas passées en VALIDÉ. **L-k à L-v**
sont nouvelles.

| Repère | Où | Ma lecture (proposition) | Pourquoi |
|---|---|---|---|
| L-a | §2, §6.3 | « Réservations commerciales » = réservations informatives du devis ; « affectations » comprend les affectations chez un transformateur (X3), les réaffectations, les libérations et leurs statuts | La première est la seule réservation non bloquante qui existe ; la seconde reprend le contenu de la liste v7 |
| L-b | §6.3 bis | « Lot brut » = lot de finition NOIR (LAC = NOIR) | Le schéma ne connaît que NOIR, GALVA, GPP |
| L-c | §6.3 bis, §6.8 | Type NORMALE/SUPPLÉMENT fixé à la réservation, compté dans le cumul de la ligne, repris à la conversion | CT17 (type fixé à la création, jamais requalifié) ; « le système reprend exactement ce qui a été réservé » |
| L-d | §6.13 | Demande d'affectation à cheval sur V refusée, avec le découpage indiqué ; aucun découpage automatique | CT17 ; « aucune décision automatique » |
| L-e | §6.6 | Ligne ajoutée par avenant : valeur article et taux GPP en vigueur à la date de l'avenant, figés dans l'avenant ; ligne existante : valeurs figées de la ligne | CT3, CT4, CT6 (rien de rétroactif) ; CT9 (coûts saisis dans l'avenant) |
| L-f | §6.19 | Le seul SUPERADMIN ne peut être ni désactivé ni changé de rôle ; premier compte créé par la procédure d'installation ; transmission future = opération unique auditée, décidée plus tard | CT1 « exactement un » ; la base ne contient aucun compte |
| L-g | §6.19 | « Droits initiaux = situation actuelle » : le SUPERADMIN a tout ; tout autre compte n'a aucune permission tant qu'elle ne lui est pas attribuée | CT2 ; aucun compte n'existe |
| L-h | §6.9 | Le % GALVA actuel de la fiche article est une source à vérifier, comme la masse | CT3 « x % = valeur explicitement validée » |
| L-i | §6.3 bis, §6.14 | Une réservation ne se déplace pas directement vers une autre commande : libération avec motif, puis nouvelle réservation | CT21 liste les libérations, pas de déplacement |
| L-j | §6.6 | La table d'avenants sert à la commande confirmée ; sur un devis confirmé, la seule intervention définie est la modification exceptionnelle du taux (CT5) | CT10 nomme la commande confirmée ; CT5 traite le taux |
| L-k | §6.10, §6.11 bis, §6.16 | La quantité d'une ligne de BST préparé est **engagée** chez GMC jusqu'à la sortie physique (5.8) ; une ligne de BST peut porter une quantité non réservée | P-BST : la 5.6 « vérifie sa disponibilité » — sinon la sortie pourrait devenir impossible ; X3 et P-MULT supposent des quantités non affectées |
| L-l | §6.11 bis, §6.19 | La préparation d'un BST est réservée au SUPERADMIN | Elle crée une allocation (N10 : SUPERADMIN seul) |
| L-m | §6.11 bis | Un BST est refusé si le transformateur n'a pas la capacité du type choisi | P-RET : « un même transformateur peut éventuellement avoir les deux capacités » |
| L-n | §6.3 bis | « Par excès » = la barre entière supérieure, pas davantage ; le reliquat de conversion est toujours inférieur à n pièces | P-MULT : 49 → 25 barres, pas 26 |
| L-o | §6.19, §6.21 | La demande de création d'article est un enregistrement tracé (demandeur, description, date ; en attente, acceptée ou refusée), traité par le SUPERADMIN ; tout utilisateur opérationnel actif peut la faire, sans permission particulière | P-ART : « les utilisateurs opérationnels peuvent … demander la création d'un article » |
| L-p | §6.21 | Seule la désignation est « administrative » ; tout autre champ a un impact métier ; la correction est faite par le SUPERADMIN ; le motif est facultatif | P-ART (exemples : libellé, faute de frappe ; « motif lorsque nécessaire ») ; BR §11 |
| L-q | §6.2 | Une marge **prévisionnelle** peut être affichée en 5.6 ; la marge réelle reste en 5.10 | P-KG-TR : « CA − prix de revient → marge » ; ta liste : « 5.10 = coûts réels / marge » |
| L-r | §6.3 bis | La ligne du BST désigne la réservation qu'elle exécute (ancien P-BST (i)) | « Aucun choix automatique » |
| L-s | §6.3 bis | L'exécution partielle d'une réservation est refusée (ancien P-BST (ii)) | « Le système reprend exactement ce qui a été réservé » |
| L-t | §6.2 | Après une modification exceptionnelle du taux, le devis continue de pointer vers le taux de sa validation ; le taux modifié est une trace rattachée au devis, sans effet sur les calculs de la 5.6. **Question : à quoi doit-il servir ?** | Y6 exclut trois effets (taux des avenants, anciennes lignes, avenants enregistrés) ; CT6 fige la photo ; rien ne dit à quoi sert le taux modifié |
| L-u | §6.3 bis | Reliquat de conversion : simple nombre calculé à la réservation ; quantité attendue non affectée, affectable par décision explicite, une fois le BST préparé ; stock GMC réel et disponible à la réception (5.8) | P-MULT : « stock GMC réel, traçable et disponible » ; O4, K1, P-BST : rien n'est vendable avant la réception |
| L-v | §6.21 | Un devis EN_COURS n'est jamais recalculé en silence quand une nouvelle version d'article apparaît : le système le signale et l'utilisateur décide ; une commande pas encore confirmée reprend la photo du devis confirmé | P-ART : « aucun calcul historique ne doit être recalculé silencieusement » ; CT6, CT9 |

**Contradictions détectées en intégrant tes décisions du 02/10, et
correction appliquée dans la v9**

| N° | Contradiction | Ancienne règle (où) | Nouvelle règle | Correction v9 |
|---|---|---|---|---|
| 1 | Phase du bon de sortie | Ta liste du 01/10 : « 5.8 = … bons de sortie » ; v8 §2, §6.3 bis : BST établi en 5.8 | P-BST : la 5.6 prépare le document, la 5.8 exécute | §2, §3, §6.3 bis, §6.11 bis, §28 ; SUPERSEDED marqué |
| 2 | Conversion et envoi physique | v8 P-BST (iv), §28 : une seule opération | P-BST : « BST commercial ≠ mouvement physique » | Deux opérations distinctes ; S05, S07, M86 |
| 3 | Qui fixe la finition de retour | v8 (lecture) : le type du transformateur | P-RET : le type de transformation choisi dans le BST ; un transformateur peut faire les deux | §6.11, §6.11 bis, DB17, DB20 ; M96 |
| 4 | Coupe seule et autres transformations | v8 P-RET (ii), (iii) : DEBIT → finition de départ, coupe seule réservable, AUTRE bloqué | P-RET : deux transformations seulement | Types DEBIT et AUTRE refusés (M98) ; coupe seule refusée à titre provisoire (M76), la suite étant ouverte : Q-COUPE |
| 5 | Types de transformateur dans la base | FACT : un seul type par transformateur ; DEBIT et AUTRE existent | P-RET | DB20 (capacités) ; anciens types conservés, inutilisés |
| 6 | Taux des avenants après modification exceptionnelle | v8 option (a) : nouveau taux pour les avenants suivants | Y6 (règle écrite) : toujours le taux du devis validé | §6.2, §6.6 ; M84, M85 ; libellé : Y6-L |
| 7 | Transport d'une ligne en KG | v8 : non tranché ; option (b) montant saisi ; U15 | P-KG-TR : KG ÷ 1 000 × EUR/T | §6.7 ; U15 adapté ; M80 |
| 8 | Quantité non multiple | v8 §6.3 bis : « 49 ou 51 sont refusés » pouvait se lire comme un refus de la ligne de 49 | P-MULT : 49 pour la ligne, 50 attendues, 1 de reliquat | L'exactitude porte sur les pièces **attendues** (barres × n) ; la ligne peut en prendre moins (§6.3 bis, M81) |
| 9 | Articles | v8 : « 36 actions si P-ART », « +2 tests si P-ART », service d'unité « selon P-ART » | P-ART | §6.21, DB21 ; 39 actions ; 11 cas |
| 10 | BST « de test » | v8 M60, E04, E09 : BST créés par les tests | P-BST : la 5.6 prépare le BST | Tests redéfinis |
| 11 | BST sans bon de commande ni état | FACT : la base exige un bon de commande de transformation et n'a pas d'état | P-BST | DB17 (état) ; Q-BCT (ouvert) |
| 12 | P-MULT et P-RET entre eux | P-MULT : « barres de 6 m … approvisionnement en 12 m », sans finition | P-RET : pas de découpe | Signalé, non tranché : Q-COUPE |
| 13 | Deux « reliquats » | « Reliquat » = non livré à la clôture (X6) | P-MULT : « reliquat de conversion » | Deux noms distincts (§6.8, §6.3 bis) |
| 14 | Reliquat « disponible » | O4, K1, P-BST : rien n'est vendable avant la réception | P-MULT : « stock GMC réel, traçable et disponible » | Avant la réception : quantité attendue non affectée, affectable par décision explicite ; après (5.8) : stock réel (§6.3 bis) |
| 15 | Nom de l'action d'audit | v8 : ENREGISTREMENT_RESULTAT_ATTENDU | P-BST : la 5.6 prépare le document entier | Renommée PREPARATION_BST (choix technique) |

**Contradictions détectées en intégrant tes décisions du 01/10, et
correction appliquée dans la v8**

| N° | Contradiction | Ancienne règle (où) | Nouvelle règle | Correction v8 |
|---|---|---|---|---|
| 1 | GPP hors poids | v7 §6.9 : « GPP pas concerné par Y4 ; vente GPP hors poids possible » ; U08 « NOIR ou GPP » ; O7 « pas de +2 % GPP » | Précision GPP du 30/09 ; CT7, CT20 : GPP = parcours GALVA, KG ou TONNE seulement | SUPERSEDED marqué (§6.9, §14 N4, §16 O7) ; U08 et M64 redéfinis |
| 2 | Poids d'une ligne en KG | Y2, O7, K6, N2, N5 : « hors tonne », poids de la ligne saisi (le KG était alors une « autre unité ») ; v7 « KG si Y4 bis le confirme » | CT20 : KG = vente au poids, poids calculé ; DÉCLARÉ seulement NOIR/LAC hors poids | « Hors tonne » se lit « hors poids » (§6.7, §6.9, §14 N2 et N5, §15 K6, §16 O7, §17 C3) ; U09, U10, U15, U21, M03, M05, M11 redéfinis ; transport du KG laissé ouvert : P-KG-TR |
| 3 | Unité contrôlée pour le GALVA | v7 Y4 bis (i) : ligne ou article | CT7 : unité de vente de la ligne | §6.9, §22 |
| 4 | SUPERADMIN « actif » ou unique | v7 CT1, DB1, I05, P08 : un seul SUPERADMIN actif ; transmission désactiver/activer | CT1 : exactement un ; deuxième refusé | DB1 sans condition sur `actif` ; I05, P08 redéfinis ; P17 ajouté ; L-f |
| 5 | Moment de saisie du résultat attendu | v7 §6.11, §6.19, CT18 : déclaré après coup par une fonction SUPERADMIN | CT18 : à l'établissement du BST | SUPERSEDED marqué ; M60 redéfini ; P-BST |
| 6 | Quantité attendue | v7 §6.11 : « ≤ quantité envoyée × … » ; U20 « au plus » | CT18 et règle 12 m → 6 m : conversion exacte | « = » partout ; U20 redéfini ; M76 |
| 7 | Réservation → affectation | v7 : la réservation « devient » une affectation ; CT21 v7 « même ligne ou ligne liée » ; DB12 « nature réservation » | Y1 bis, mécanisme : réservation conservée + affectation liée | §6.3 bis ; DB12 modifié ; DB19 ajouté ; M61 redéfini ; I20 |
| 8 | Moment de la conversion | v7 : au bon de sortie **ou** à la réception (5.8) | Y1 bis (b) : au BST | §6.3 bis ; §22 |
| 9 | Erreur de prix après confirmation | v7 Y5 bis (a)/(b) ; M27 « sauf Y5 bis » ; DB11 « exception éventuelle » | CT10 : correction SUPERADMIN, motif, audit, pas une renégociation | §6.7 ; DB10 (nature « correction ») ; DB11 strict ; M27 redéfini ; M65, P21 |
| 10 | Avenant pour une intervention sur devis CONFIRMÉ | v7 CT10 : « aussi pour une intervention sur devis CONFIRMÉ » | CT10 nomme la commande confirmée (sans exclure le devis) ; CT5 : taux par nouveau taux + motif | Pas tranché par moi : lecture L-j (§6.6, §21, §22) |
| 11 | Statut de clôture | v7 CT19 : « SOLDÉE ou statut propre » | CT19 : SOLDÉE | §6.17, §6.18, M49 |
| 12 | Libellé du type d'affectation | CT17 : NORMALE / SUPPLÉMENT ; base et BR §1 : INITIALE / SUPPLEMENT | Même sens (BR §1 : INITIALE = quantité normale) | Pas une contradiction de fond : code INITIALE conservé, affiché NORMALE (choix technique signalé) |
| 13 | « À approvisionner » | v7 §6.8 : sans le réservé | CT21 : la réservation couvre le besoin de la ligne | Réservé ajouté à la formule [CT] (§6.8) |
| 14 | Taux « exactement tel que saisi » | FACT : colonne `taux REAL` | CT5 | Texte saisi conservé (DB4), calcul à partir de ce texte |
| 15 | Disponible commercial | v7 §6.16 A : stock GMC − affecté ; réservé déduit « si Y1 bis (a) » | Y1 bis (a), CT21 : physique − affecté − réservé | §6.10, §6.16, M78 |
| 16 | GPP en constante | N4, K19 « × 1,02 » ; DB3 v7 « paramètre GPP 1,02 » | CT4 : réglage global historisé | Précision (même valeur aujourd'hui) : §6.9, §14, §15, DB3 |
| 17 | Masse de la fiche article | v7 : masse linéique obligatoire, sans distinction validée/non validée | CT3 : « valeur MV à vérifier », jamais validée automatiquement | §6.9 ; M67 |

**Recherche systématique que tu as demandée le 01/10** *(tableau de la v8, conservé ; les points P- qu'il cite sont décidés le 02/10)*

| Recherche | Résultat dans la v8 |
|---|---|
| Anciennes règles contredites par Y4 bis | Contradictions 2 et 3 ; tout texte « KG selon Y4 bis » est marqué SUPERSEDED |
| Anciennes règles GALVA hors KG/TONNE | Plus aucune règle active ; X8 « hors tonne » marqué SUPERSEDED PAR Y4 (sans objet) |
| Anciennes règles GPP | Contradictions 1 et 16 |
| Logique X1 de renégociation après confirmation | X1, K10 (partie), O8 (phrase) marqués SUPERSEDED PAR Y5 (§6.7, §14 à §18, §20) ; erreur de prix : CT10 |
| Poids déclaré GALVA/GPP | Plus aucun : DÉCLARÉ seulement NOIR/LAC hors poids (CT20) ; contradiction 1 |
| Réservation / affectation | Contradictions 7, 8, 13, 15 |
| BST | Contradictions 5 et 6 ; périmètre P-BST ; DEBIT/AUTRE : P-RET |
| 12 m → 6 m | Contradiction 6 ; « exacte » partout (§6.3 bis, §6.11, §6.12, U20) |
| SUPERADMIN | Contradiction 4 ; L-f |
| Taux | Contradiction 14 ; Y6 ouvert |
| Avenants | Contradiction 9 ; point 10 laissé en lecture L-j |
| CT17 | Contradiction 12 ; L-c, L-d |
| CT21 | Contradictions 7, 13, 15 ; L-b, L-c ; P-BST |

*Vérifications de la v7 (30/09), conservées pour l'historique ; une ligne
est SUPERSEDED :*

- Y5 et X1, K10, O8 : Y5 **remplace** X1, la partie « renégociation
  datée » de K10 et la phrase d'O8 sur une nouvelle négociation client.
  Ces remplacements sont signalés partout (§6.7, §14 à §18, §20). Ce qui
  reste valide : une nouvelle ligne identique reprend le prix confirmé
  (K10), et le prix de vente n'est jamais modifié par un coût d'achat
  (O8).
- Y4 et X8 : cohérents. Le % GALVA reste obligatoire ; le cas « GALVA hors
  tonne » de X8 ne se présente plus.
- ~~Y4 et O7 : cohérents. Le GPP hors poids reste possible, avec le poids
  déclaré tel quel.~~ **SUPERSEDED PAR la précision GPP du 30/09 et
  CT7/CT20** (contradiction n° 1).
- Y2 et BR §19, O7 : cohérents. Montant total et poids saisis sur la
  ligne du devis, sans conversion. La répartition au poids du transport
  réel est en 5.10.
- Y3 et X5, K4 : réconciliés. Taux en TND pour 1 EUR ; R = 1 ÷ taux ;
  exemples inchangés.
- Y1 et K2/D1 : une réservation n'est pas une compatibilité directe. La
  vente reste possible seulement après la réception (O4).
- Y1 et X6 : les réservations sont listées et libérées à la clôture
  avec reliquat.
- Y1 et « aucune décision automatique » : traité en Y1 bis.

---

## 23. Points nécessitant encore une validation humaine

*Liste de la v8, conservée pour l'historique : 1. Y6 ; 2. P-BST ;
3. P-ART ; 4. P-RET ; 5. P-KG-TR ; 6. P-MULT ; 7. lectures L-a à L-j ;
8. propositions C ; 9. validation de la v8. Les points 1 à 6 sont
décidés le 02/10 (§0 ter).*

**Pour pouvoir coder la 5.6** (ma proposition entre parenthèses) :

1. **Y6-L** : confirmer que la règle de Y6 est bien « tous les avenants
   gardent le taux du devis validé » (oui : c'est ce que tu as écrit).
2. **Q-COUPE** : une ligne NOIR 6 m peut-elle être servie par des barres
   NOIR de 12 m ? (non en 5.6 : pas de découpe dans le périmètre
   actuel).
3. **Q-BCT** : BST préparé sans bon de commande de transformation (a),
   ou avec (b) ? (a).
4. **Q-ANNUL** : un BST préparé et non sorti peut-il être annulé par le
   SUPERADMIN avec motif, en libérant ses allocations ? (oui).
5. **Q-TRF** : les transformateurs et leurs capacités sont-ils créés en
   5.6, par le SUPERADMIN ? (oui).
6. **Lectures L-a à L-v** (§22) : confirmation en bloc, ou correction de
   celles qui ne te conviennent pas. L-t contient une question : à quoi
   doit servir un taux modifié à titre exceptionnel ?
7. **[PROP] des C** : restes de C1 à C12 et C14 (§17), dont la question
   C8 (un supplément déplacé peut-il devenir NORMALE à la destination ?)
   et la question de C1 (valeurs à utiliser si la quantité change en
   brouillon).
8. **Validation explicite de la v9.**

Point connu, qui n'empêche pas de coder : le **format du code article**
n'est pas décidé depuis la 5.5 ; l'identifiant technique actuel est
conservé.

**Si tu acceptes mes propositions en bloc** (points 1 à 7), l'analyse est
prête pour ta validation finale.

---

## 24. Contrôles finaux

| Contrôle | Résultat |
|---|---|
| P-MULT, Y6, P-BST, P-ART, P-RET, P-KG-TR intégrés partout où nécessaire | Oui : §0 ter (avec renvois), §1 à §3, §6.2, §6.3 bis, §6.6 à §6.12, §6.16 à §6.21, §7.2, §8, §9, §11, §12, §14 à §22, §26 à §29 |
| CT1 à CT21, Y1 bis, X1 à X9, Y1 à Y5 toujours intégrés | Oui : renvois de tests identiques dans §0 bis, §12, §18 et §20 |
| Décisions remplacées conservées et marquées | Oui : mention « SUPERSEDED PAR … » à l'endroit de chaque ancienne règle, et registre complet au §26 (H1 à H40) |
| **Aucune confusion allocation / mouvement** | Oui : réservation, allocation et BST préparé ne créent aucun mouvement (§6.3 bis, §6.10, §6.11 bis) ; M43, M61, M86, S05, S07 |
| **Aucune création prématurée de lot transformé** | Oui : aucun lot créé en 5.6 ; le lot transformé naît à la réception en 5.8 (§6.11 bis, §28) ; M87, S08 |
| **Aucune réécriture historique** | Oui : registres jamais modifiés (avenants, taux, valeurs et versions d'article, réglage GPP, réservations, reliquats, photos) ; M85, M94, I06, I12, I16, I17, I20, I22 |
| **Aucune modification rétroactive des commandes** | Oui : photo figée (CT6), nouvelle version d'article sans effet (P-ART), taux inchangé (Y6), prix confirmé jamais réécrit (CT10) ; M69, M85, M93, I07 |
| **Séparation prix de vente / coût d'achat / transport / prix de revient** | Oui : quatre composants conservés à part (§6.2, DB6) ; U29, U30, U31, M80 |
| **Taux de change du devis correctement figé** | Oui : figé à la validation du devis, lu dans la photo par tous les avenants, non modifié par une modification exceptionnelle (§6.2, §6.6) ; M08, M24, M84, M85 |
| Aucune règle métier inventée | Les compléments nécessaires sont présentés comme questions ouvertes (Y6-L, Q-COUPE, Q-BCT, Q-ANNUL, Q-TRF) ou comme lectures à confirmer (L-a à L-v) ; les choix purement techniques sont signalés [CT] |
| Conversion 12 m → 6 m exacte, approvisionnement par excès | Oui : §6.3 bis, §6.12, U20, U27, U28, M81 |
| GALVA et GPP seulement en KG ou TONNE, poids calculé | Oui : §6.9, DB6, M64, M75 |
| X6 ne transforme pas un reliquat en livraison | Oui : §6.17, M51 |
| Formule X5 selon la convention validée | Oui : R = 1 ÷ taux saisi en TND pour 1 EUR (Y3, CT5) ; 726,47 et 4 499,41 inchangés |
| X9 / CT17 ne requalifient jamais un supplément | Oui : §6.13, §6.14, M36, M37, M44, I19 |
| Dépendances 5.6 à 5.10 cohérentes | Oui : §28 ; trois questions touchent la frontière 5.6 / 5.8 : Q-BCT, Q-ANNUL et Q-TRF |
| Modèle conceptuel complet | Oui : §27 (17 notions, chacune représentée) |
| Tests existants | **Exécutés le 02/10 : 293 réussis** (`pytest tests/ -q`) |
| Tests proposés pour la 5.6 | 210 cas ; **aucun n'est écrit ni exécuté** |
| Base inchangée | Vérifié par commande le 02/10, après l'exécution des tests : empreinte du schéma `89e3225d…ab718e4` identique ; 20 migrations ; fichier `gmc.db` toujours daté du 30/09 à 09 h 55 |
| Code inchangé | Vérifié par commande : aucun fichier de `core/`, `db/` (hors fichier technique `gmc.db-shm`), `repositories/`, `services/`, `tests/`, `migrations/` n'a changé ; v7 et v8 identiques octet pour octet ; seul ce document est créé |
| `docs/BUSINESS_RULES.md` (gelé) | Contient encore des textes à reporter après validation : §21 N6 ; §20 introduction et note sous D5 ; §22 K3, K5, K10. Aucune de O1 à O9, X1 à X9, Y1 à Y6, Y1 bis, CT1 à CT21 ni des six décisions du 02/10 n'y figure encore. |

---

## 25. Checklist finale avant codage

- [x] Y2, Y3 : validés.
- [x] Y1, Y4, Y5 : validés dans leur principe.
- [x] Y1 bis, Y4 bis, Y5 bis, L1 : réglés le 01/10.
- [x] CT1 à CT21 : validés le 01/10.
- [x] P-MULT, Y6, P-BST, P-ART, P-RET, P-KG-TR : décidés le 02/10.
- [ ] Confirmation du libellé de Y6 (**Y6-L**).
- [ ] Réponses à **Q-COUPE, Q-BCT, Q-ANNUL, Q-TRF**.
- [ ] Confirmation (ou correction) des lectures **L-a à L-v**.
- [ ] Validation (ou correction) des [PROP] restantes des C1 à C12 et C14.
- [ ] **Validation humaine explicite de la v9.**
- [ ] Puis, avant la première ligne de code, sur ton accord (ces
      documents sont aujourd'hui gelés) :
  - reporter dans `docs/BUSINESS_RULES.md` O1 à O9, C10, X1 à X9, Y1 à
    Y6, Y1 bis, CT1 à CT21, les six décisions du 02/10 et les réponses
    restantes, en corrigeant les textes listés au §24 ;
  - archiver les analyses v5 à v9 dans `docs/` et dans le projet ;
  - mettre à jour le suivi.
- [ ] Puis seulement : suivre le plan du §29 (migration 0021, code,
      tests, rapport).

*Checklist de la v8 : ses cases « Y6 » et « P-BST, P-ART, P-RET,
P-KG-TR, P-MULT » sont cochées par tes décisions du 02/10.*

---

## 26. Registre des décisions remplacées (SUPERSEDED)

Chaque ancienne règle reste écrite à sa place, marquée « SUPERSEDED PAR
… ». Ce registre les rassemble.

| N° | Ancienne règle (version, endroit) | Remplacée par | Explication courte |
|---|---|---|---|
| H1 | X1 : un nouveau prix négocié s'applique à toutes les lignes identiques (v6) | **Y5** | Plus de renégociation après confirmation, donc plus de nouveau prix à propager |
| H2 | K10, partie « renégociation datée » | **Y5** | Idem ; le reste de K10 (ligne identique = même prix) est maintenu |
| H3 | O8, phrase « si une nouvelle négociation commerciale avec le client est nécessaire… » | **Y5** | Idem ; le prix de vente n'est jamais modifié par un coût d'achat |
| H4 | Y5 bis, option (a) « annulation + nouveau devis » (v7) | **CT10** | L'erreur de prix se corrige par le SUPERADMIN, avec motif |
| H5 | DB11 v7 : « exception éventuelle dans le trigger » ; M27 « sauf Y5 bis » | **CT10** | La correction passe par la table d'avenants ; DB11 reste strict |
| H6 | X8, partie « GALVA hors tonne : poids déclaré » | **Y4** | Plus de vente GALVA hors poids (sans objet) |
| H7 | O7, clause « transport EUR/T × poids déclaré » (v5) | **X2, Y2** | Hors tonne, montant total saisi (déjà en v6) |
| H8 | v7 §6.9 : « GPP pas concerné par Y4 ; GPP hors poids possible » ; U08 « NOIR ou GPP » ; O7 « pas de +2 % GPP » | **Précision GPP du 30/09 + CT7, CT20** (règlement de Y4 bis) | GPP = même parcours que le GALVA, KG ou TONNE seulement ; erreur de ma part dans la v7 |
| H9 | v7 : « vente en TONNE (et en KG si Y4 bis le confirme) » ; Y2 « poids de la ligne saisi » appliqué au KG | **Y4 BIS, réglé par CT20** | Le KG est une vente au poids : poids calculé |
| H10 | v7 Y4 bis (i), autre possibilité « unité de valorisation de l'article » | **CT7** | Le contrôle porte sur l'unité de vente de la ligne |
| H11 | v7 Y4 bis : « référentiel article minimal en 5.6 ? » ; « −3 tests s'il n'y est pas » | **CT3** | La validation des valeurs article est en 5.6 ; reste P-ART |
| H12 | N4, K19 : GPP « × 1,02 » comme constante ; DB3 v7 « paramètre GPP 1,02 » | **CT4** | Réglage global historisé (2 % aujourd'hui) ; même valeur |
| H13 | v7 CT1, DB1, I05, P08 : un seul SUPERADMIN **actif** ; transmission désactiver/activer | **CT1** | Exactement un SUPERADMIN, actif ou non ; deuxième refusé |
| H14 | v7 Y1 bis (b), autre possibilité « à la réception (5.8) » | **Y1 bis (b)** | Conversion au BON DE SORTIE TRANSFORMATION |
| H15 | v7 : la réservation « devient » une affectation ; CT21 v7 « même ligne ou ligne liée » ; DB12 « nature réservation » | **Y1 bis (mécanisme)** | Réservation conservée, nouvelle affectation liée (stockage DB19, choix technique) |
| H16 | v7 : réservation « dès la confirmation du client » | **Y1 bis (c)** | « Confirmation client » = commande client confirmée |
| H17 | v7 §6.11 : résultat prévu « déclaré sur un BST existant par une fonction SUPERADMIN » ; §6.19 « déclaration du résultat prévu » réservée | **CT18** | Renseigné à l'établissement du BST ; P-BST |
| H18 | v7 §6.11 : quantité attendue « ≤ … » ; U20 « au plus 200 × 6 m » | **CT18 + règle 12 m → 6 m** | Conversion exacte |
| H19 | v7 CT19 : « SOLDÉE ou statut propre » | **CT19** | SOLDÉE, sans statut « clôturée avec reliquat » |
| H20 | v7 CT10 : « aussi pour une intervention sur devis CONFIRMÉ » | *Non remplacé : lecture L-j à confirmer* | CT10 nomme la commande confirmée sans exclure le devis ; le taux du devis suit CT5 |
| H21 | v5 CT6 : prix de revient « jamais stocké » ; v7 : instantané « proposé » | **CT6** | Photo complète figée à la confirmation |
| H22 | v7 §2 : liste du périmètre | **Ta liste du 01/10** | Mêmes sujets, réservation de lots bruts nommée |
| H23 | v7 L1 : lecture « à confirmer » | **Périmètre du 01/10** | Affectation en 5.6, fournisseur en 5.7 |
| H24 | N6 (v3) : supplément « au-delà de la quantité originale » | **O1** | Au-delà de la quantité en vigueur V (déjà en v6) |
| H25 | « Mohamed désigne le taux » (v4) | **K5, X5** | Le commercial saisit le taux (déjà en v6) |
| H26 | v7 Y6 option (b) : « corriger l'offre elle-même » | **CT6** (pour la photo seulement) | La photo de l'offre confirmée ne change jamais ; Y6 restait ouvert sur les avenants (décidé le 02/10 : H33) |
| H27 | v7 §21 : titre « CT1 à CT21 — aucun validé » ; v7 §23 et §25 (listes de points ouverts) | **Décisions du 01/10** | Tous les CT validés ; restent Y6, P-, L-, C |
| H28 | Ta liste du 01/10 : « 5.8 = … bons de sortie » ; v8 §2, §6.3 bis : BST établi en 5.8 | **P-BST (02/10)** | La 5.6 prépare le document ; la 5.8 exécute la sortie physique |
| H29 | v8 P-BST (proposition) : fonction de la 5.6 appelée par la 5.8, dans la même opération que l'envoi ; (iv) conversion avant le garde-fou ; autre possibilité « tout en 5.8 » | **P-BST (02/10)** | Préparation et sortie physique sont deux opérations distinctes |
| H30 | v8 P-RET (i) et DB17 v8 : la finition de retour dépend du type du transformateur | **P-RET (02/10)** | Elle dépend du type de transformation choisi dans le BST ; un transformateur peut avoir les deux capacités |
| H31 | v8 P-RET (ii), (iii) : DEBIT → finition de départ ; coupe seule réservable ; AUTRE bloqué | **P-RET (02/10)** | Deux transformations seulement : GALVANISATION et GPP |
| H32 | v8 P-RET (iv) : finition de retour = finition demandée du bon de commande de transformation | *Non repris : Q-BCT ouvert* | Ta décision ne prévoit pas ce contrôle |
| H33 | v8 Y6, option (a) : le nouveau taux sert aux avenants suivants | **Y6 (02/10)** | Tous les avenants gardent le taux du devis validé (libellé à confirmer : Y6-L) |
| H34 | v8 P-KG-TR, option (b) : montant total saisi pour une ligne en KG | **P-KG-TR (02/10)** | KG ÷ 1 000 × EUR/T |
| H35 | v8 P-MULT, options (b) et (c) : 24 barres + un autre lot ; pièce en trop en SUPPLÉMENT | **P-MULT (02/10)** | Par excès ; le reliquat de conversion reste libre |
| H36 | v8 P-ART : « en 5.6, oui ou non ? » ; « autre possibilité : une phase que tu choisiras » ; « 36 actions si P-ART » | **P-ART (02/10)** | Création, demandes, versions et corrections en 5.6 ; 39 actions |
| H37 | v8 §6.19 : « qui peut établir un BST relève de la 5.8 » | **P-BST (02/10)** | La préparation est en 5.6 (SUPERADMIN : lecture L-l) |
| H38 | v8 : action ENREGISTREMENT_RESULTAT_ATTENDU ; tests M60, E04, E09 sur des « BST de test » | **P-BST (02/10)** | Action PREPARATION_BST ; BST préparé par la 5.6 |
| H39 | v8 : M79 et M80 « réservés, non comptés » ; test de l'effet de Y6 « impossible avant ta décision » | **Décisions du 02/10** | Définis et comptés (M79, M80, M84, M85) |
| H40 | v8 §23, §25 et verdict : listes de points ouverts (Y6, P-BST, P-ART, P-RET, P-KG-TR, P-MULT) | **Décisions du 02/10** | Restent Y6-L, Q-COUPE, Q-BCT, Q-ANNUL, Q-TRF, lectures L-, propositions C |

---

## 27. Vérification du modèle conceptuel

Pour chaque notion que tu as citée : ce qu'elle est en mots simples,
comment l'analyse la représente, et dans quelle phase elle est créée ou
utilisée. Aucune n'est absente ; aucune ne se confond avec une autre.

| Notion | En mots simples | Représentation dans le logiciel | Créée / utilisée |
|---|---|---|---|
| **Réservation** (de lot brut) | Des barres brutes mises de côté chez GMC pour une commande, en vue d'une transformation | Table dédiée (DB19) : lot, ligne, quantité réservée, résultat et quantité attendus, statut ACTIVE / CONVERTIE / LIBÉRÉE ; bloque le disponible ; jamais un mouvement. *Distincte de la réservation informative du devis (DB7), qui ne bloque rien.* | 5.6, conversion comprise (à la préparation du BST, P-BST) |
| **Affectation** | Une quantité précise d'un lot précis attribuée à une ligne de commande | `affectation_stock` (DB12) : lot, ligne, type NORMALE/SUPPLÉMENT fixé, emplacement, résultat attendu éventuel, lien vers la réservation convertie ; jamais un mouvement | 5.6 ; rattachée au lot résultant en 5.8 ; livrée en 5.9 |
| **Lot** | Un ensemble de barres identiques, avec une origine et un coût | `lot` (existant) : article, finition, longueur, pièces, origine unique (réception, transformation, inventaire) ; non modifié par la 5.6 | 4 / 5.5 ; nouveaux lots en 5.7 et 5.8 |
| **Stock physique** | Ce qui est réellement là, où que ce soit | Registre des mouvements (seule source de vérité, jamais modifié) ; soldes calculés | 5.5 ; la 5.6 lit seulement |
| **Stock chez le transformateur** | Les barres de GMC qui sont chez le galvanisateur ou un autre sous-traitant | Même registre ; le transformateur est un emplacement du stock GMC ; situation B, C, D, E | 5.5 ; affiché en 5.6 (CT12) |
| **Transformation prévue** | Ce qu'on compte faire faire à la marchandise pour la vendre | Ligne de devis puis de commande : OUI/NON + coût et unité (CT7, CT8) ; réservation : résultat attendu (CT21) | 5.6 |
| **Résultat attendu** | Ce qui doit revenir du transformateur (finition, longueur, nombre de pièces) | Ligne du BST (DB17) : finition fixée par le type de transformation (P-RET), longueur, quantité attendue exacte ; figé dès qu'une allocation s'y rattache (CT18). Ce n'est pas un lot. | **5.6** (préparation du BST, P-BST) |
| **Bon de sortie transformation (commercial)** | Le document qui prépare l'envoi d'un lot brut chez le transformateur | BST à l'état PRÉPARÉ (DB17) : transformateur, type GALVANISATION ou GPP, lignes, résultat attendu, allocations liées. « BST commercial ≠ mouvement physique » | **5.6** : préparation ; **5.8** : sortie physique |
| **Reliquat de conversion** | La barre de 6 m en trop quand 25 barres de 12 m servent une commande de 49 | Pièces attendues − pièces qui couvrent la ligne, pour une réservation (§6.8) ; jamais attribué automatiquement ; ni chute, ni reliquat de commande (P-MULT) | 5.6 (calcul, affichage, affectation explicite après la préparation du BST) ; stock réel à la réception (5.8) |
| **Version d'article** | L'état d'un article à une date, gardé pour toujours | Registre des versions (DB21) : numéro, date d'enregistrement, auteur, motif, valeurs ; la photo d'un devis ou d'une commande garde la version utilisée (P-ART) | 5.6 |
| **Transformation réelle** | Ce qui a été réellement envoyé, transformé et rendu | Exécution du BST préparé : mouvement de sortie rattaché à la ligne du BST, transformation, résultat réel, bon de réception (tables existantes depuis la Phase 4) | 5.8 |
| **Lot transformé** | Le nouveau lot qui revient (ex. GALVA 6 m), avec son lien vers le lot d'origine | Nouveau `lot` rattaché à son lot parent ; caractéristiques propres (N15) | 5.8 |
| **Livraison** | La marchandise qui part chez le client | Bons de livraison client (existants) ; plafond = affecté non livré ; interdite avant réception (CT18) | 5.9 |
| **Reliquat de commande** | Ce qui ne sera pas livré quand on clôture une commande | Table de reliquat (DB13), ligne par ligne, jamais modifiée ; commande SOLDÉE + motif (CT19) | 5.6 ; jamais livré (X6) |
| **Avenant** | Une modification de la commande après sa confirmation | Registre unique des avenants (DB10), jamais modifié : quantités, nouvel article, interventions du SUPERADMIN, corrections d'erreur de prix ; quantité en vigueur et prix en vigueur calculés | 5.6 |
| **Supplément** | Une quantité livrée au-delà de la quantité en vigueur | Affectation de type SUPPLÉMENT + motif, jamais requalifiée (CT17, X9) ; valorisée au CMP | 5.6 ; valorisation en 5.10 |
| **Historique** | La trace de tout ce qui a été fait, par qui, quand et pourquoi | Journal d'audit (39 actions) ; registres jamais modifiés : avenants, taux, valeurs et versions d'article, réglage GPP, réservations, reliquats, photos de devis, droits | 5.6 (et phases suivantes) |

Chaîne de traçabilité complète : besoin client (ligne de commande) →
réservation (5.6) → BST préparé et allocation liée (5.6) → sortie
physique du lot d'origine (5.8) → lot transformé (5.8) → livraison (5.9)
→ coût réel et marge (5.10).

*v8 : 14 notions ; la v9 en ajoute trois (bon de sortie commercial,
reliquat de conversion, version d'article).*

---

## 28. Chronologie et dépendances entre phases

**Chronologie cible** (vérifiée étape par étape, avec tes décisions du
02/10) :

| Étape | Ce qui se passe | Phase | Ce qui est figé ou contrôlé |
|---|---|---|---|
| 1. DEVIS (EN_COURS) | Article existant sélectionné ; taux saisi ; prix négocié ; transformation prévue et coût ; poids calculé (KG/TONNE) ou déclaré (NOIR/LAC hors poids) ; transport ; prix de revient | 5.6 | Valeur article validée obligatoire pour le poids calculé (CT3) ; composants du prix de revient séparés (P-KG-TR) |
| 2. Confirmation du devis | Passage à CONFIRMÉ | 5.6 | **Taux figé comme référence de l'affaire** (Y6) ; prix, conditions et **photo complète** figés (CT5, CT6, CT4, CT20, Y5), version d'article comprise (P-ART) |
| 3. COMMANDE CONFIRMÉE | Commande créée depuis le devis (coûts recopiés, CT9), puis confirmée | 5.6 | Quantité originale et prix figés ; la commande garde les caractéristiques de sa confirmation (P-ART). Question rattachée à C1 : valeurs à utiliser si la quantité change en brouillon |
| 4. Réservation éventuelle d'un lot brut | SUPERADMIN ; contrôles CT21 ; calcul par excès (P-MULT) ; disponible diminué | 5.6 | Possible seulement à partir de l'étape 3 (Y1 bis (c)) ; aucun mouvement |
| 5. **Préparation du BST** | Lot brut, type de transformation, résultat attendu (finition automatique, longueur, quantité), document à l'état PRÉPARÉ | **5.6** | Résultat ≠ réservation → BST refusé (Y1 bis (b)) ; **aucun mouvement, aucun lot** (P-BST) |
| 6. Conversion réservation → allocation | Réservation CONVERTIE et conservée ; nouvelle allocation liée au BST ; reliquat de conversion laissé libre | **5.6**, dans l'opération de l'étape 5 | Rien n'est choisi par le système ; résultat attendu figé (CT18) |
| 7. **Sortie physique** | La marchandise part chez le transformateur ; mouvement enregistré | **5.8** | Garde-fou CT11 : une quantité engagée ne sort que par l'exécution de son BST |
| 8. Transformation | Chez le transformateur | 5.8 | Situation « envoyé, non réceptionné » (CT12) |
| 9. Réception du lot transformé | **Nouveau lot** ; résultat réel ; allocation rattachée au lot résultant ; écarts ; le reliquat de conversion non affecté devient du stock GMC disponible | 5.8 | Le lot transformé n'existe qu'à partir d'ici ; vendable seulement après cette étape (O4, K1, P-BST) |
| 10. Livraison / facturation | BL ≤ affecté non livré ; prix en vigueur | 5.9 | Livraison avant l'étape 9 refusée (CT18) ; reliquat de commande jamais livré (X6) |
| 11. Coûts réels / marge | Comparaison avec la photo ; transport réel, distinct du prévisionnel, réparti au poids ; marge = CA − prix de revient | 5.10 | Supplément au CMP ; chutes hors marge individuelle |

Résultat : la chronologie est cohérente. Trois remarques :

- les étapes 5 et 6 forment **une seule opération, en 5.6** ; l'étape 7
  est une **autre** opération, en 5.8 ;
  - *v8 : « établissement du BST … envoi physique » en 5.8, conversion
    « dans la même opération » — **SUPERSEDED PAR P-BST (02/10)**.*
- entre les étapes 6 et 7, la marchandise est toujours chez GMC, mais
  engagée (lecture L-k) ; l'annulation d'un BST à ce moment-là est une
  question ouverte (Q-ANNUL) ;
- l'étape 3 dépend de C1 (encore [PROP]) pour une commande dont les
  quantités diffèrent du devis.

**Vérification des sept interactions que tu as demandées**

| Interaction | Ce que tu as demandé | Vérifié dans l'analyse | Tests |
|---|---|---|---|
| Article → commande → lot | Une nouvelle version d'article ne modifie pas une commande confirmée | La photo garde les valeurs et la version utilisées (§6.21, CT6) ; les lots et mouvements gardent l'unité en vigueur à leur date (FACT 5.5) | M93, M94, M69, I22 |
| Commande → réservation → BST → allocation | La réservation est conservée dans l'historique ; au BST : réservation → nouvelle allocation liée au BST | Réservation CONVERTIE jamais supprimée ; allocation créée à la préparation du BST, avec le lien (§6.3 bis, §6.11 bis, DB12, DB19) | M61, I20, E04, E09 |
| BST → transformation | La 5.6 prépare ; la 5.8 exécute physiquement | Tableau des responsabilités du §6.11 bis ; aucune écriture de stock en 5.6 | M86, S05, S07 |
| Transformation → nouveau lot | Le nouveau lot n'existe qu'après transformation/réception en 5.8 | Le résultat attendu n'est pas un lot ; aucune fonction 5.6 ne crée de lot (§6.11 bis) | M87, S08 |
| 12 m → 6 m | 49 × 6 m → 25 × 12 m → 50 × 6 m → 49 affectés → 1 restant, en stock ou vendu plus tard selon la décision de l'utilisateur | Calcul par excès ; reliquat de conversion jamais attribué automatiquement (§6.3 bis, §6.8). Le mot « achetés » concerne la 5.7 ; la coupe sans galvanisation ni GPP : Q-COUPE | U27, U28, M81, M82, M83, E11 |
| Taux de change | Devis confirmé → taux figé → tous les avenants utilisent ce taux | Taux lu dans la photo du devis validé ; modification exceptionnelle sans effet sur le taux des avenants ni sur les lignes (§6.2, §6.6) | M08, M24, M84, M85 |
| Transport | KG ÷ 1 000 → tonnes → × EUR/T → transport prévisionnel → composant du prix de revient | §6.2, §6.7, `core/prix_revient.py` | M80, U29, U30, U31, U15 |

**Dépendances entre phases**

| De → vers | Ce que la phase suivante attend | Statut |
|---|---|---|
| 5.6 → 5.7 | « À approvisionner » par ligne (réservé compris) ; barres à acheter calculées par excès (P-MULT) ; O8 côté fournisseur ; `v_approvisionnement_ligne` à recalculer sur V | Cohérent (§6.8, §7.2) |
| 5.6 → 5.8 | BST préparés, avec leurs lignes, leur résultat attendu et leurs allocations ; quantité engagée ; garde-fou CT11 ; blocage du retour à lever à la réception | Cohérent ; trois questions à la frontière : **Q-BCT**, **Q-ANNUL**, **Q-TRF** |
| 5.6 → 5.9 | Allocations (normal / supplément) ; résultat attendu non rattaché = non livrable ; prix en vigueur (CT10) ; reliquat de commande non livrable ; garde-fou sur les livraisons | Cohérent (§7.2) |
| 5.6 → 5.10 | Photo figée du devis, composants séparés (CT6, P-KG-TR) ; poids de chaque ligne (CT20) ; type d'allocation pour la valorisation | Cohérent (§7.2) |
| 5.7 → 5.6 | Aucune : la 5.6 n'attend rien de la 5.7 | — |
| 5.8 → 5.6 | Aucune : la 5.6 prépare seule ses BST | — |

Aucune dépendance circulaire. La 5.6 peut être codée seule ; la 5.8
exécutera ce que la 5.6 aura préparé.

---

## 29. Plan de développement proposé (après validation)

**Rien de ce plan ne commence avant ta validation explicite de la v9.**
Il indique seulement dans quel ordre je coderais la 5.6, pour que chaque
étape s'appuie sur une étape déjà testée.

Règles valables pour chaque étape (j'écris « étape » et non « lot »,
pour ne pas confondre avec un lot de barres) :

- je code **uniquement** ce qui est validé dans cette analyse ;
- chaque étape livre son code **et** ses tests ; les 293 tests existants
  sont relancés à chaque étape ;
- une étape ne commence que si la précédente est entièrement réussie ;
- toute nouvelle décision métier qui apparaît : **STOP**, puis FACT /
  PROPOSITION / IMPACT / POINT À VALIDER ;
- à la fin de chaque étape : un court rapport, avec les commandes réelles
  et leurs résultats ;
- la Phase 5.7 n'est pas lancée.

| Étape | Contenu | Tests principaux | Dépend de |
|---|---|---|---|
| 0. Préalable (sur ton accord) | Reporter les décisions dans `docs/BUSINESS_RULES.md` ; archiver les analyses ; mettre à jour le suivi | — | Validation de la v9 |
| 1. Base de données | Migration 0021 complète (DB1 à DB21), appliquée deux fois depuis zéro, données existantes reprises | Intégrité (I) ; non-régression avec les adaptations listées au §13 | Étape 0 ; **toutes les réponses** : Y6-L, Q-COUPE, Q-BCT, Q-ANNUL, Q-TRF, lectures L-a à L-v, propositions C (une migration appliquée ne se modifie plus) |
| 2. Calculs | Poids de vente, prix de revient et transport, conversion de longueur et calcul par excès, 39 actions d'audit | Unitaires (U) | Étape 1 |
| 3. Comptes et droits | Un seul SUPERADMIN, modules, permissions, attributions | Permissions (P) de base ; E10 | Étape 1 |
| 4. Articles et référentiel | Création, demandes, versions, corrections ; validation des valeurs ; réglage GPP ; contrôle du changement d'unité | Cas P-ART, CT3, CT4 | Étapes 2, 3 |
| 5. Clients et devis | Clients ; devis, taux, poids, transport, prix de revient, photo à la confirmation | Cas devis, CT5 à CT8, P-KG-TR | Étapes 2 à 4 |
| 6. Commandes et avenants | Commande, confirmation, avenants, taux de la photo, correction d'erreur de prix | Cas commande, CT9, CT10, CT16, Y5, Y6 | Étape 5 |
| 7. Affectations et réservations | Affectations, suppléments, réaffectations, libérations ; réservation de lot brut, calcul par excès | Cas CT17, CT21, Y1 bis, P-MULT | Étape 6 |
| 8. Bon de sortie transformation (préparation) | Préparation commerciale, type de transformation, résultat attendu, comparaison, conversion ; **aucun mouvement, aucun lot** | Cas P-BST, P-RET, CT18 ; S07, S08 ; E04, E09, E11 | Étape 7 |
| 9. Clôture et situation | Clôture avec reliquat ; situation de l'affaire et du stock | Cas X6, CT19, CT12 | Étapes 7, 8 |
| 10. Contrôles ajoutés au Stock Service | Correction d'inventaire avec PV ; garde-fou sur les mouvements existants | Cas CT11, CT14 ; adaptation des 13 appels de test | Étapes 7, 8 |
| 11. Bout en bout et rapport | Scénarios complets ; contrôle technique du code ; rapport final de la 5.6 | E2E (E), S01 à S08, non-régression | Toutes |

Les étapes 3 à 10 suivent l'ordre des dépendances du §8. **Aucune étape
ne commence tant qu'il reste un point ouvert** : la base est créée en
une fois à l'étape 1, et plusieurs questions et lectures en fixent la
forme (types de transformation, état du BST, réservations, versions
d'article, capacités des transformateurs).

---

**Verdict de préparation : NON PRÊT POUR LE CODAGE — POINTS À VALIDER :
Y6-L (libellé de Y6), Q-COUPE, Q-BCT, Q-ANNUL, Q-TRF, lectures L-a à
L-v, propositions C ; puis validation explicite de la v9.**

*Verdict de la v8 (« Y6, P-BST, P-ART, P-RET, P-KG-TR, P-MULT, lectures
L-a à L-j, propositions C ») : ses six premiers points sont SUPERSEDED
PAR tes décisions du 02/10.*

*Verdict de la v7 (« Y1 bis, Y4 bis, Y5 bis, Y6, L1, puis les
propositions C et CT1 à CT21 ») : SUPERSEDED PAR tes décisions du 01/10.*

La Phase 5.6 n'est pas considérée comme validée tant que tu n'as pas
validé explicitement la v9. Aucun module métier n'est codé, aucune
migration n'est créée, la base n'est pas modifiée, la Phase 5.7 n'est
pas lancée.

**PHASE 5.6 — ANALYSE CONSOLIDÉE — EN ATTENTE DE VALIDATION AVANT
CODAGE**
