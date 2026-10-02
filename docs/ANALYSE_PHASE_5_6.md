# Phase 5.6 — Analyse technique : les AFFAIRES (version 4)

**Statut : ANALYSE UNIQUEMENT.** Aucun code, aucune migration créée,
aucune modification de la base. Seuls ce document, les règles métier et
le suivi du projet sont mis à jour.

- Version 4 du 30/09/2026 : intègre tes « réponses définitives aux
  questions K1 à K22 ». Ces réponses remplacent toute interprétation
  précédente contraire.
- Versions précédentes : cahier 5.6 (v1), D1 à D6 (v2), N1 à N15 (v3).

Légende :

- **[V]** : DÉCISION VALIDÉE, écrite par toi. La source est citée.
- **[CT]** : CHOIX TECHNIQUE, c'est-à-dire ma proposition de mise en
  œuvre. Selon ta consigne, **aucun [CT] n'est considéré comme validé**
  sans ton accord.
- **[O…]** : décision encore ouverte (§5.2).
- **FACT** : constaté dans le schéma, le code ou les documents.

Avant livraison, un relecteur indépendant a comparé cette version à tes
messages. Il a relevé 40 écarts : mots durcis ou omis, choix techniques
présentés comme validés, renvois inexacts. Tous sont corrigés ici.

---

## 0. En bref (langage clair)

- Tes réponses K1 à K22 tranchent l'essentiel. Restent **9 décisions
  ouvertes** (O1 à O9, §5.2), **10 confirmations C** encore partiellement
  sans réponse (§5.3) et la **liste des choix techniques** à valider
  (§5.4).
- **Trois de mes propositions sont remplacées** par tes décisions :
  - le lot transformé naît au **bon de réception de transformation**,
    dans le stock GMC, et non chez le galvanisateur (K1) ;
  - le taux est **saisi à la main** par le commercial pour chaque devis,
    et non choisi dans une liste du SUPERADMIN (K5) ;
  - **aucune délégation** n'est active ; seule l'architecture la prévoit
    (K8, K16).
- Nouveautés :
  - la **formule du prix de revient estimé** du devis (K4) ;
  - le **coût de transformation saisi à la main** sur chaque ligne
    concernée (K4) ;
  - les **corrections d'inventaire** réservées au SUPERADMIN, avec **PV
    obligatoire signé par la Direction Générale** (K17). Cela modifie un
    service validé en 5.5 ;
  - trois cas distincts pour le **% GALVA** : défini, 0 % (état brut), non
    renseigné (K20).
- Base inchangée : empreinte du schéma vérifiée. Rien ne sera codé avant
  ta validation finale.

---

## 1. Règles D1 à D6 (rappel, lecture définitive)

- **D1** — Compatibilité **directe** uniquement pour un lot **déjà dans
  l'état commercial demandé** [V K2]. NOIR 12 m n'est pas directement
  compatible avec GALVA 6 m.
  - Le chemin NOIR 12 m → transformation → GALVA 6 m est autorisé si la
    transformation prévue permet réellement cette transformation.
  - Le lot brut est l'**origine traçable** ; le lot transformé devient un
    **nouveau lot commercialement compatible après réception** [V K2].
  - Le lot brut de 12 m n'est jamais considéré directement disponible
    comme 6 m [V K2].
  - [CT] L'« état commercial » se compare sur trois critères : article,
    finition, longueur.
- **D2** — Poids : vente en tonne → méthode validée de la fiche article
  [V N2, K18] ; autres unités → poids déterminé manuellement [V K6] ; un
  article vendu GALVA intègre le % GALVA [V D2, N3, K20], un article vendu
  GPP est majoré de 2 % [V N4, K19]. Pour un poids saisi à la main, voir
  O7.
- **D3** — Devises imposées selon le type de prix, pré-remplissables, pas
  librement modifiables : vente EUR, achat TND, transformation TND,
  transport EUR [V K22].
- **D4** — Commande confirmée : modifications **historisées comme
  avenants**, réservées au SUPERADMIN [V K9].
- **D5** — Disponibilité réelle calculée ; lots choisis **manuellement** ;
  aucun FIFO ; localisation physique ≠ affectation commerciale [V K11,
  K12].
- **D6** — **Actuellement** un seul SUPERADMIN, Mohamed. Droits déterminés
  par le compte et le rôle ou la permission, **et non simplement par le
  nom affiché** [V K16].

---

## 2. N1 à N15 — version définitive (textes validés)

| N | Règle définitive [V] | Sources |
|---|---|---|
| N1 | Chaque article a une méthode de poids unitaire validée : kg/ml, kg/m², kg/pièce ou autre méthode explicitement validée dans la fiche article. La MV est la base de départ, mais ses masses sont **à vérifier**. Pour un article : comparer les valeurs existantes, ne jamais choisir silencieusement, présenter les références disponibles, faire valider par le SUPERADMIN, enregistrer la valeur retenue et son historique. Le référentiel se construit **progressivement** par l'usage réel, jusqu'à une version complète et fiable. Le projet n'est **pas** bloqué en attendant que toutes les masses soient validées. | N1, K7 |
| N2 | Vente en **TONNE** : poids calculé automatiquement selon la méthode validée de la fiche article. Aucune saisie manuelle arbitraire ne remplace cette méthode. Si la méthode manque, le système **demande** de compléter et valider le référentiel article. | N2, K18 |
| N3 | **GALVA** : % saisi manuellement pour chaque article. Poids GALVA = poids brut × (1 + % GALVA ÷ 100). Exemple : IPE100 6 m = 8,1 × 6 = 48,6 kg ; à 6 % : 51,516 kg. Trois cas distincts : % défini, 0 % défini (= état brut de la matière), % non renseigné. Un % non renseigné n'est jamais transformé automatiquement en 0 %. Pour une vente GALVA sans % renseigné et validé, le système demande de compléter le référentiel. | N3, K20 |
| N4 | **GPP** : finition distincte de GALVA. Poids GPP = poids brut × 1,02, majoration fixe **actuellement**. Jamais cumulée avec le % GALVA. | N4, K19 |
| N5 | **Devises imposées** selon le type de prix, pré-remplissables et pas librement modifiables : vente EUR, achat matière TND, transformation TND, transport EUR. **Transport** : vente en tonne → EUR/t × poids vendu en tonnes ; pièce, ML, M² ou autre unité → montant total du transport saisi directement en EUR, sans conversion cachée en tonnes. **Taux prévisionnel** : un utilisateur commercial autorisé le saisit à la main lors de chaque préparation de devis ; c'est le taux qu'il décide d'utiliser ce jour-là ; il est historisé avec le devis. Après validation de l'offre, le taux est figé, l'utilisateur commercial ne peut plus le modifier, et seul le SUPERADMIN **peut** intervenir selon les règles de modification stratégique. Pas de sélection obligatoire d'un taux prédéfini. **Prix de revient estimé (EUR) = (achat matière TND + transformation TND) ÷ taux prévisionnel + transport EUR.** Coût de transformation saisi à la main par article, devant chaque ligne concernée, sans grille automatique obligatoire. Pas d'arrondi intermédiaire inutile ; arrondi final selon la devise. Cette méthode ne remplace pas le coût réel ni la marge analytique (phases ultérieures). | N5, K4, K5, K13, K22 |
| N6 | La quantité originale reste **fixe** dans l'historique, jamais écrasée, jamais transformée rétroactivement (100 ne devient jamais 120). Pendant l'exécution et le suivi d'avancement, le SUPERADMIN **peut** modifier la quantité à livrer par avenant. On distingue : quantité originale ; quantité actuellement demandée ou en vigueur ; quantités ajoutées ou diminuées par avenant ; quantités déjà livrées ; reste à livrer ; supplément éventuel. Exemple : 100 initiales + 20 par avenant = 120 en vigueur. Ce qui dépasse la quantité originale « reste identifié comme supplément et suit la règle CMP » (N6). La valorisation des quantités ajoutées par avenant est encore ouverte (O1). | N6, K3, K15 |
| N7 | La diminution est autorisée, jamais sous la quantité déjà livrée. Une marchandise reçue qui devient inutile reste propriété et stock GMC, disponible pour une future vente selon son emplacement et son état. Si elle est affectée, l'utilisateur choisit **explicitement** l'affectation à réduire ou libérer ; le système ne choisit jamais. Tout est historisé et audité. | N7, K13 |
| N8 | Ligne identique = mêmes caractéristiques commerciales pertinentes : article, finition, longueur, unité de vente, autres caractéristiques nécessaires. Une nouvelle ligne identique conserve le prix applicable à la commande. Une nouvelle ligne ne provoque jamais automatiquement la modification du prix d'une ligne existante. Une nouvelle négociation donne un nouveau prix historisé, avec sa date d'effet, et l'ancienne condition est conservée. À la facturation, les lignes compatibles peuvent être regroupées sans perdre l'historique. Pour une autre commande client, le prix peut être différent. | N8, K10 |
| N9 | Décisions stratégiques et opérations sensibles réservées au SUPERADMIN et toujours auditées : comptes utilisateurs, rôles et droits, tâches et permissions, modifications stratégiques, codage, corrections, mises à jour de version, améliorations, validation des évolutions importantes. Les **avenants** sont réservés au SUPERADMIN ; chacun garde ancienne valeur, nouvelle valeur, utilisateur, date et heure, motif, **impact**, historique. | N9, K9 |
| N10 | **Pour le moment, seul le SUPERADMIN effectue les affectations.** Le mécanisme doit permettre de déléguer plus tard ; **aucune délégation actuellement**. Le rôle COMMERCIAL n'est pas imposé dès maintenant pour les affectations. | N10, K8 |
| N11 | Emplacements : GMC, chaque transformateur ou galvanisateur, autres emplacements nécessaires. On distingue **localisation physique** et **affectation commerciale** : une marchandise peut être physiquement chez le galvanisateur et commercialement affectée à une affaire. Une allocation n'est jamais un mouvement physique et ne change jamais la localisation. | N11, K11 |
| N12 | Flux obligatoire : bon de sortie GMC → transformateur ; marchandises physiquement chez le transformateur ; préparation et réception prévues selon les quantités attendues ; **bon de réception transformation** → retour dans le stock GMC. Le lot transformé n'est **pas** physiquement revenu chez GMC avant ce bon. Entre les deux, le système représente **virtuellement** la situation chez le transformateur : les quantités prévues et réceptionnables se calculent à partir du stock physique qui s'y trouve. Cette situation est traçable et calculable, mais ce n'est pas une réception GMC. À la réception : réception conforme, nouvelles caractéristiques, création et entrée du lot transformé dans le stock GMC. La logique complète de transformation est développée en 5.8 ; la 5.6 n'invente pas la logique détaillée de réception et de transformation. | N12, K1 |
| N13 | Le système calcule la disponibilité réelle. Il empêche les doubles affectations incompatibles, les allocations dépassant les quantités réellement disponibles et les mouvements incompatibles avec les quantités déjà affectées. Il calcule et contrôle ; il ne choisit jamais automatiquement les lots. | N13, K12 |
| N14 | **Actuellement**, un seul SUPERADMIN : Mohamed. Droits déterminés par le compte et le rôle ou la permission, et **non simplement** par le nom affiché. L'architecture doit permettre une future transmission ou délégation des pouvoirs. | N14, K16 |
| N15 | **Transformation et changement d'état.** Un lot brut peut devenir un nouveau lot après transformation : NOIR 12 m → bon de sortie GMC → transformateur → transformation → bon de réception transformation → GALVA 6 m. Le nouveau lot a ses propres caractéristiques, quantité, longueur, poids, finition, localisation et traçabilité. Le lot d'origine reste historiquement traçable. | N15, K2 |

---

## 3. K1 à K22 — version définitive

| K | Ta décision [V] | Effet sur mes propositions précédentes |
|---|---|---|
| K1 | Flux bon de sortie → situation virtuelle chez le transformateur, calculée à partir du stock physique qui s'y trouve → bon de réception → lot transformé créé et entré dans le stock GMC | **Remplace** ma proposition « lot né chez G ». FACT : compatible avec la règle 5.5 existante (le retour fait entrer le lot résultat en STOCK_GMC). |
| K2 | D1 = compatibilité directe d'un lot déjà dans l'état demandé ; le chemin par transformation est autorisé si la transformation prévue le permet ; une transformation peut changer finition, longueur, quantité, poids, état commercial ; le lot brut est l'origine traçable ; le lot transformé est un nouveau lot compatible **après réception** ; 12 m n'est jamais disponible directement comme 6 m | Affectation seulement sur un état identique. |
| K3 | Quantité originale fixe ; le SUPERADMIN **peut** modifier par avenant la quantité à livrer ; six grandeurs distinctes (voir N6) | Intégré ; valorisation : O1. |
| K4 | Formule du prix de revient estimé ; transformation saisie par ligne concernée ; pas de grille imposée | Nouveau : champ de coût de transformation et calcul. |
| K5 | Taux saisi à la main par un commercial autorisé, historisé, figé après validation de l'offre ; ensuite, seul le SUPERADMIN peut intervenir selon les règles de modification stratégique | **Remplace** ma proposition « taux créé par le SUPERADMIN ». |
| K6 | Pour PIÈCE, ML, M² et autres unités autorisées, le poids peut être déterminé manuellement selon les règles validées | Majoration sur un poids manuel : O7. |
| K7 | Référentiel construit progressivement (N1) ; projet non bloqué | Pas d'exigence de complétude. |
| K8 | SUPERADMIN = Mohamed actuellement ; délégation future prévue dans l'architecture ; **aucune délégation** actuellement | Aucune fonction de délégation en 5.6. |
| K9 | Avenants historisés, réservés au SUPERADMIN, avec impact | Ajout de l'« impact ». |
| K10 | Voir N8 | Portée d'une renégociation : O8. |
| K11 | Voir N11 | Autres emplacements : O9. |
| K12 | Voir N13 | [CT] le contrôle s'applique aussi aux livraisons (§5.4). |
| K13 | TND en millimes, EUR en centimes ; précision complète ; arrondi final seulement. Diminution jamais sous le livré ; marchandise inutile = stock GMC disponible | Intégré. |
| K14 | « Aucun nouveau point métier à ouvrir. Les règles déjà validées doivent simplement être intégrées dans les services et tests correspondants. » | Les points O ci-dessous ne sont que des trous d'application, pas de nouvelles règles. |
| K15 | La situation distingue toujours : quantité originale, en vigueur, ajoutées, supplément, livré, reste à livrer | Catégories intégrées ; formules [CT] (§4.3). |
| K16 | Voir N14 | — |
| K17 | Corrections d'inventaire réservées au SUPERADMIN ; justifiées, auditées, traçables ; **obligatoirement** accompagnées d'un PV signé par la Direction Générale, dont la référence ou la trace est conservée dans l'audit ; jamais de modification silencieuse de l'historique physique | Modifie `stock_service.corriger_inventaire` (5.5). |
| K18 | Voir N2 | — |
| K19 | Voir N4 ; NOIR/LAC → GPP = +2 % ; NOIR/LAC → GALVA = % GALVA ; jamais +2 % puis % GALVA | — |
| K20 | Voir N3 | Portée hors vente en tonne : O7. |
| K21 | **Cas 1**, article déjà présent dans la première version de la commande : aucune intervention particulière sur la méthode de calcul de la ligne ; le système applique les règles existantes, sans refaire **inutilement** toute la logique de la commande. **Cas 2**, nouvel article : la nouvelle ligne complète est recalculée (article, finition, longueur, unité, quantité, poids, prix, coût matière, coût de transformation, transport, taux de change du devis ou de la commande selon son contexte, autres données). L'ancienne commande reste historiquement intacte. | O1 (valorisation), O2 (taux). |
| K22 | Voir N5 (devises) | — |

---

## 4. Modèle logique

Les décisions sont marquées [V], mes choix de mise en œuvre [CT].

### 4.1 Flux de transformation [V K1, N12, N15]

```
  STOCK_GMC                        CHEZ_TRANSFORMATEUR:G                    STOCK_GMC
  ┌─────────────────┐ BON DE      ┌──────────────────────────────────┐ BON DE      ┌──────────────────┐
  │ lot L NOIR 12 m │ SORTIE GMC  │ lot L NOIR 12 m, toujours brut   │ RÉCEPTION   │ NOUVEAU lot L'   │
  │ GMC −100        │───────────► │ G +100 (stock physique)          │ TRANSFO     │ GALVA 6 m, ses   │
  └─────────────────┘             │ situation VIRTUELLE : quantités  │───────────► │ quantité, poids, │
                                  │ prévues/réceptionnables calculées│             │ finition ;       │
                                  │ à partir de ce stock physique    │             │ parent = L       │
                                  │ (pas une réception GMC)          │             └──────────────────┘
                                  └──────────────────────────────────┘
                                          + chutes → CHUTES ; consommation de L chez G
```

FACT : la sortie, le retour (entrée du lot résultat en STOCK_GMC et
consommation chez le transformateur) et les chutes existent depuis la 5.5.
Les documents de transformation (bon de commande avec finition demandée,
format de débit et quantité prévue ; bon de sortie ; réception) existent
en base et seront exploités en 5.8.

### 4.2 Couche commerciale — aucun mouvement [V N11, K11, K12]

- **Affectation** [V N10, K2] : lot **déjà dans l'état demandé**, par le
  SUPERADMIN, choix manuel. [CT] Elle mémorise l'**emplacement** des
  pièces (GMC ou un transformateur).
- **Réservation** (devis) : informative. [CT] Même règle d'état et
  d'emplacement que l'affectation.
- **Lot brut pour une ligne dans un autre état** : pas d'affectation
  directe [V K2]. [CT] La proposition d'affectation le signale
  « utilisable après transformation », en lecture seule.
- **Production attendue d'une transformation en cours** (ton exemple
  obligatoire 100 envoyées, 60 affectées, 40 libres) : voir O4.

### 4.3 Quantités d'une ligne — catégories [V K3, K15], formules [CT]

| Grandeur | Définition |
|---|---|
| O — originale | Figée à la confirmation, jamais modifiée [V] |
| Δ — avenants | Ajouts et diminutions historisés [V] |
| V — en vigueur | O + Δ, calculée [V : catégorie ; CT : calcul] |
| Livré, reste à livrer | Catégories [V] ; reste = V + supplément hors avenant − livré [CT] |
| Supplément | Au-delà de O, règle CMP [V N6] ; traitement des quantités d'avenant : O1 |
| Affecté initial | ≤ le plus petit de O et V [CT] |
| À approvisionner | V − ce qui est déjà affecté pour couvrir V [CT] |

### 4.4 Stock par emplacement [V D5, K1, K11]

| Catégorie | Calcul [CT] | Phase |
|---|---|---|
| A. Disponible chez GMC | physique STOCK_GMC − affecté non livré en STOCK_GMC | 5.6 |
| B. Chez chaque transformateur | physique chez ce transformateur | 5.6 |
| C, D. Chez le transformateur, affecté / libre | par emplacement | 5.6 |
| E. Réceptionnable (situation virtuelle, K1) | calculé à partir du stock physique chez le transformateur, par lot, dans son état actuel | 5.6 : oui [CT] |
| F. Production attendue, dans le nouvel état | nécessite la transformation prévue (bon de commande de transformation : finition demandée, format de débit) | O4 |

### 4.5 Prix de revient estimé [V K4 formule ; CT niveau de calcul]

- Exemple validé : (2 000 + 300) ÷ 3,40 + 50 = 726,470588… →
  **726,47 EUR**.
- [CT] Calcul au **total de la ligne**, car le transport d'une ligne hors
  tonne est un montant total ; chaque prix est multiplié par la quantité
  dans son unité. Arithmétique exacte, **un seul arrondi au centime**.
  Revient par unité (ex. EUR/t) = revient exact ÷ quantité commerciale,
  arrondi au centime pour l'affichage.
- Exemple : 4,32 t ; achat 2 800,5 TND/t ; transformation 450 TND/t ;
  taux 3,40 ; transport 85,50 EUR/t.
  - Achat : 12 098,16 TND.
  - Transformation : 1 944 TND.
  - Transport : 369,36 EUR.
  - Revient : 4 499,407058… → **4 499,41 EUR** (1 041,53 EUR/t).

---

## 5. Contradictions, décisions ouvertes, choix à valider

### 5.1 Contradictions apparentes et leur traitement

| # | Contradiction | Traitement |
|---|---|---|
| R1 | N6 (« au-delà de l'originale = supplément CMP ») et K3/K15 (« quantités ajoutées par avenant » distinctes du « supplément ») | **Non tranché** → O1. |
| R2 | Cahier §3 et §6 (devis confirmé figé, jamais écrasé) et K5 (le SUPERADMIN peut intervenir après validation) | [V D4, K9] toute intervention est historisée, la valeur d'origine conservée. Moment et support : O3. |
| R3 | D5 (les 40 pièces « peuvent être réservées/allouées à une nouvelle affaire même avant leur réception physique chez GMC ») et K2 (« nouveau lot commercialement compatible **après réception** ») | **Non tranché** → O4. |
| R4 | Règles §17 et §19 « au millime » et K13 (EUR en centimes) | Tranché par K13 (règles métier mises à jour). |
| R5 | `corriger_inventaire` (5.5 : aucun contrôle de rôle, motif simple) et K17 | Tranché par K17 : service modifié. |
| R6 | Cahier §7 (poids manuel sans formule) et N2/K18 | Tranché par K18. |
| R7 | C2 (liste d'unités fermée) et « autres unités autorisées » (K6) | C2 reste ouvert. |
| R8 | N10 (« ne pas imposer le rôle COMMERCIAL » pour les affectations) et K5 (« utilisateur commercial autorisé » pour les devis) | Pas contradictoire (opérations différentes), mais la définition de « commercial autorisé » est ouverte → O5. |
| R9 | D2/K20 (« une vente GALVA intègre le % GALVA ») et K6 (« poids déterminé manuellement » hors tonne) | **Non tranché** → O7. |

### 5.2 Décisions encore ouvertes

| # | Question | Ma proposition |
|---|---|---|
| **O1** | **Valorisation des quantités ajoutées par avenant.** Cas 1 (même article, ex. 100 + 20) : les 20 sont-elles un **supplément** au CMP (lecture littérale de N6 : « au-delà de l'originale = supplément ») ou une quantité normale au coût réel du lot ? Cas 2 (nouvel article) : même question pour toute la ligne. | Cas 1 : supplément au CMP (N6). Cas 2 : quantité originale propre de la nouvelle ligne, donc coût réel du lot (la ligne a ses propres coûts estimés). |
| **O2** | Taux d'une ligne ajoutée par avenant (cas 2, « selon son contexte ») : taux du devis d'origine, ou nouveau taux prévisionnel saisi à la date de l'avenant ? | Nouveau taux saisi dans l'avenant et historisé ; les lignes d'origine gardent le taux du devis. |
| **O3** | « Validation de l'offre » = passage du devis à **CONFIRMÉ** ? | Oui : c'est aussi le moment où le devis est figé (cahier §3). |
| **O4** | Ton exemple obligatoire : 100 pièces chez le galvanisateur, 60 affectées, 40 affectables à une nouvelle affaire avant réception, alors que le lot transformé n'est compatible qu'après réception (K2). Faut-il pouvoir affecter la **production attendue** d'une transformation en cours ? | Oui, en **5.8**, en s'appuyant sur la transformation prévue (bon de commande de transformation). En 5.6 : affectation des lots déjà dans l'état demandé, à GMC ou chez un transformateur. |
| **O5** | Définition de l'« utilisateur commercial autorisé » (K5), qui prépare un devis, saisit son taux, réserve, crée et confirme une commande sans choisir de lots. Rôle COMMERCIAL, ou permission donnée compte par compte par le SUPERADMIN ? Et la création des comptes avec leur rôle (SUPERADMIN, N9) entre-t-elle dans la 5.6 ? | Rôle COMMERCIAL (N10 ne vise que les affectations) ; création minimale des comptes et de leur rôle par le SUPERADMIN, tracée. |
| **O6** | Supprimée : c'était un choix technique, déplacé en §5.4 (CT7). | — |
| **O7** | Article vendu GALVA ou GPP **hors tonne** (poids manuel, K6) : le poids saisi est-il le poids **final**, ou le poids **brut**, auquel le système applique le % GALVA (qui doit alors être renseigné, K20) ou les 2 % GPP (D2) ? | Poids saisi = poids commercial final, sans majoration automatique. |
| **O8** | **Renégociation de prix** (K10) : le nouveau prix s'applique-t-il à la seule ligne visée, ou à toutes les lignes identiques de la commande ? | À toutes les lignes identiques de la commande, pour garder un seul « prix applicable ». |
| **O9** | « Autres emplacements nécessaires » (K11) : la 5.6 gère GMC et chaque transformateur, comme aujourd'hui. Faut-il un référentiel d'emplacements (ex. second dépôt) dès la 5.6, ou au premier besoin réel ? | Au premier besoin réel ; en 5.6, GMC et transformateurs. |

### 5.3 Confirmations C encore sans réponse

La partie déjà couverte par le cahier ou par tes réponses est indiquée ;
seul le reste attend ta réponse.

| C | Déjà validé | Reste à confirmer (ma proposition) |
|---|---|---|
| C1 | Un devis donne au maximum une commande (cahier §3, §6). | Même si la commande est annulée ; lignes d'origine issues du devis (les lignes d'avenant font exception) ; sous-ensemble de lignes permis ; quantité libre en brouillon. |
| C2 | Unités PIÈCE, ML, M², TONNE citées ; « autres unités autorisées » (K6). | Liste initiale TONNE, PIÈCE, ML, M², extensible par une évolution validée par le SUPERADMIN ; ML = pièces × longueur ; M² saisi ; prix dans l'unité de vente, ou au kg pour une vente à la tonne. |
| C3 | Transport (§19, N5, K22). | [CT] Transport recalculé sur la quantité en vigueur selon les règles de la ligne (K21, cas 1). |
| C4 | Causes normalisées ; cause obligatoire ; commande confirmée annulée par le SUPERADMIN (cahier §4, §10). | Même liste pour la commande ; commentaire obligatoire pour « Autre » ; brouillon annulé par son auteur ; un devis confirmé ne s'annule pas. |
| C5 | Cycle du devis (cahier §3). | Valable jusqu'à la fin de la date de validité ; prolongation possible avant expiration ; un devis expiré n'est ni confirmé, ni annulé, ni prolongé. |
| C6 | Réservation manuelle, optionnelle, informative (cahier §5). | Plafond = disponible réel à l'emplacement visé ; annulation, jamais de suppression. |
| C7 | Supplément au-delà de l'originale, au CMP (N6). | Lien avec les avenants : O1. |
| C8 | Réaffectation tracée ; le reste de 70 conservé (cahier §17). | Réservée au SUPERADMIN ; INITIALE dans la limite restante de la destination, sinon SUPPLÉMENT ; même lot et même emplacement ; partie non livrée seulement. |
| C9 | — | Libération manuelle en cas d'erreur : SUPERADMIN, motif, tracée. |
| C10 | Signalement « entièrement livrée », clôture manuelle par Mohamed (cahier §19). | Définition : livré ≥ V + suppléments hors avenant, et plus d'affectation active non livrée. Clôture avec reliquat (motif) : **autorisée ou interdite** ? |
| C11 | Catégories de la situation (K15, cahier §18). | Formules du §4.3 [CT]. |
| C12 | — | La fiche client actuelle suffit ; destination et incoterm repris sur le devis. |
| C13 | LAC = NOIR (D1). | — |
| C14 | — | `date_confirmation` = date de confirmation par le client. |

### 5.4 Choix techniques à valider [CT]

Aucun n'est considéré comme validé.

- **CT1** — Un seul SUPERADMIN actif, contrôlé aussi par la base. Une
  transmission future reste possible : désactiver l'un, activer l'autre.
- **CT2** — Tables de permissions créées **vides** et consultées par les
  contrôles, pour qu'une délégation future n'exige pas de migration.
  Aucune fonction de délégation.
- **CT3** — Référentiel article : historique immuable des paramètres
  validés (méthode de poids, surface d'une pièce pour le kg/m², % GALVA),
  avec les sources présentées. Masse linéique de la fiche facultative,
  lue comme « valeur MV à vérifier ». Liste de méthodes extensible.
- **CT4** — Majoration GPP de 2 % : paramètre validé historisé (plutôt
  qu'une constante du programme), puisqu'elle est fixe « actuellement »
  (K19).
- **CT5** — Taux : chaque saisie crée une ligne immuable avec son auteur ;
  un devis en cours peut pointer vers un nouveau taux, l'ancien restant
  en historique.
- **CT6** — Prix de revient calculé au total de la ligne, jamais stocké,
  un seul arrondi.
- **CT7** — Ligne sans transformation : indicateur « transformation
  prévue : oui / non ». Si oui, coût obligatoire (0 seulement s'il est
  saisi). Si non, aucun coût. Jamais de 0 implicite.
- **CT8** — Unité du coût de transformation : obligatoire (règle §15), au
  choix TND/t, TND/kg, TND/pièce, TND/ml ou montant total de la ligne.
- **CT9** — Coûts estimés (achat, transformation) copiés sur chaque ligne
  de commande (lignes d'origine), et saisis pour une ligne d'avenant.
- **CT10** — Une seule table d'avenants, immuable, pour la commande (et le
  devis confirmé si O3 le demande). « Impact » stocké en quantités et
  montants avant et après. Un avenant de poids d'une ligne en tonne ne
  fait qu'un **recalcul** par la méthode, jamais une valeur libre (K18).
- **CT11** — Garde-fou N13 appliqué à **tous** les mouvements, livraisons
  comprises. Une livraison ne consomme que des pièces affectées à la ligne
  livrée (FACT : le trigger existant `trg_bl_client_ligne_plafond` l'impose
  déjà).
- **CT12** — Situation virtuelle E (§4.4) calculée en 5.6 à partir du
  stock physique chez chaque transformateur.
- **CT13** — Proposition d'affectation « utilisable après transformation »
  : lecture seule.
- **CT14** — Référence du PV de la Direction Générale : texte obligatoire
  (référence et date du PV), versé dans l'audit de la correction ; le
  service et la base exigent le rôle SUPERADMIN.
- **CT15** — Migration 0021 atomique, additive, anciennes lignes reprises,
  contrôles doublés en base.

---

## 6. Impacts sur le modèle de données (migration 0021 proposée, NON créée)

| Table | Changement | Source |
|---|---|---|
| `utilisateur` | Rôle SUPERADMIN ; un seul actif | [V N14] ; CT1 |
| `permission`, `utilisateur_permission` | Tables vides | CT2 |
| `article` + `article_parametre_valide` | Référentiel progressif ; % GALVA à trois états | [V N1, N3, K7, K20] ; CT3 |
| `parametre_valide` (ou table générale) | Majoration GPP 2 % historisée | [V N4] ; CT4 |
| `taux_change` | + `cree_par` ; saisie par le commercial ; figé à la validation | [V K5] ; CT5 ; O3, O5 |
| `devis` | Destination, incoterm, annulation, transitions, figé une fois confirmé | [V cahier §3, §4] |
| `devis_ligne` | Poids de vente (unité, origine, trace) ; unités ; M² ; **devises imposées** ; **coût de transformation** (TND + unité, indicateur) ; transport + unité | [V K4, K22, §15] ; CT7, CT8 |
| `reservation_devis` | Emplacement, auteur, annulation, contrôles | [V cahier §5] ; C6 |
| `commande_client` | Annulation, solde, une commande par devis, transitions | [V cahier] ; C1, C4 |
| `commande_ligne` | Lien devis ; unités ; poids ; prix et transport EUR ; coûts estimés ; taux d'une ligne d'avenant ; quantité originale figée ; garde-fou « montant entier » étendu | [V K21, K22] ; CT9 ; O2 |
| `avenant` (nouvelle) | Immuable ; SUPERADMIN ; ancienne et nouvelle valeur, motif, impact | [V K9] ; CT10 ; O3, O8 |
| `affectation_stock` | Emplacement ; état identique ; plafonds ; auteur SUPERADMIN ; clôtures ; motif d'un supplément | [V N10, K2, cahier §16] ; CT ; O1 |
| `reaffectation` | Reste explicite ; même lot et même emplacement | [V cahier §17] ; C8 |
| `mouvement_stock` | Garde-fou ; correction = SUPERADMIN | [V N13, K12, K17] ; CT11, CT14 |
| `journal_audit` | Environ 28 actions, dont avenant, référentiel, affectation, correction avec PV, attribution de rôle (si O5) | [V] ; CT |
| Références | Causes d'annulation (validées) ; unités (C2) ; méthodes de poids (CT3) | — |
| Hors 0021 | Production attendue (O4) ; référentiel d'emplacements (O9) ; import MV | — |

---

## 7. Impacts sur les services

| Service | Contenu |
|---|---|
| `droits_service` | Droits = compte actif + rôle (+ permissions, CT2) ; jamais par le nom ; aucune délégation. Si O5 : création des comptes et rôles par le SUPERADMIN. |
| `referentiel_article_service` (nouveau) | Créer ou compléter un article ; **présenter** les valeurs candidates et leurs sources sans rien choisir ; validation par le SUPERADMIN (méthode, % GALVA) avec historique ; progressif (N1, K7). |
| `core/poids_vente.py` | Vente en tonne : méthode validée × facteur de finition (NOIR 1 ; GALVA 1 + %/100 ; GPP selon CT4 ; jamais cumulés). Méthode ou % absent → le système **demande de compléter** le référentiel. Hors tonne : poids manuel (O7). |
| `devis_service` | Préparation par un commercial autorisé (O5) ; **taux saisi à la main** et historisé ; devises imposées ; coût de transformation par ligne concernée ; **prix de revient estimé** ; réservations ; confirmation (le taux est figé, O3) ; expiration ; annulation (SUPERADMIN) ; KPI. |
| `commande_service` | Création depuis le devis ; brouillon ; confirmation (les lots ne sont choisis que par le SUPERADMIN) ; **avenants** SUPERADMIN (cas 1 et cas 2, O1, O2, O8) ; prix des lignes identiques ; annulation ; clôture (C10). |
| `affectation_service` | SUPERADMIN seul (N10) ; état identique, par emplacement ; signalement « après transformation » (CT13) ; supplément ; réaffectation (C8) ; libération (C9, N7) ; jamais de choix automatique. |
| `situation_service` | O, Δ, V, ajoutées, supplément, livré, reste (K15) ; stock A à E par emplacement (CT12). |
| `stock_service` (5.5, modifié) | `corriger_inventaire` : SUPERADMIN + PV de la Direction Générale obligatoire, dans l'audit (K17, CT14) ; disponibilité par emplacement ; garde-fou en base (CT11). |

**Matrice des droits**

| Action | SUPERADMIN | Commercial autorisé | Source |
|---|---|---|---|
| Créer ou modifier un client | ✔ | — | [V cahier §2] |
| Préparer un devis et saisir son taux | ✔ | ✔ | [V K5] (définition du commercial : O5) |
| Réserver (informatif) | ✔ | ✔ | proposé (O5) |
| Confirmer un devis ; créer et confirmer une commande sans lots | ✔ | ✔ | proposé (O5) |
| Annuler un devis ou une commande confirmée | ✔ | — | [V cahier §4, §10] |
| Affecter, y compris un supplément | ✔ | — | [V N10] |
| Réaffecter ; libérer après une erreur | ✔ | — | proposé (C8, C9) |
| Avenants ; intervention après validation de l'offre | ✔ | — | [V K9, K5] |
| Corrections d'inventaire avec PV de la Direction Générale | ✔ | — | [V K17] |
| Valider une masse ou une méthode de poids | ✔ | — | [V N1, K7] |
| Modifier le % GALVA d'un article | ✔ | — | proposé (modification d'un article, §11) |
| Clôture SOLDÉE | ✔ | — | [V cahier §19] |

---

## 8. Tests définitifs à prévoir

Chaque test cite sa source. Un test qui dépend d'un point ouvert ou d'un
choix technique porte son repère.

**Migration**

- 21 migrations ; nombres mesurés.
- Reconstruction reproductible ; intégrité ; clés étrangères = 0.
- Audit recopié et immuable.
- Échec atomique en cas d'anomalie préalable [CT15].
- REAL refusé sur les nouvelles colonnes `*_minor`.
- Références immuables.
- Un seul SUPERADMIN [CT1].
- Tables de permissions vides [CT2].

**Poids et référentiel** [V N1 à N4, K7, K18 à K20]

- IPE100 6 m : 48,6 kg ; GALVA 6 % : 51,516 kg ; GPP : 49,572 kg ; 100
  barres GALVA : 5,1516 t.
- GALVA avec 0 % défini = 48,6 kg (état brut).
- GALVA avec % non renseigné → le système demande de compléter ; jamais
  de 0 automatique.
- GPP jamais cumulé avec GALVA.
- Vente en tonne sans méthode validée → demande de compléter.
- Poids manuel refusé pour une vente en tonne.
- Hors tonne : poids manuel avec unité ; comportement GALVA et GPP selon
  [O7].
- Valeurs candidates présentées, aucune choisie ; validation par le
  SUPERADMIN seul ; historique conservé [CT3].
- Un article sans méthode n'empêche pas une vente hors tonne (projet non
  bloqué).

**Devis** [V N5, K4, K5, K22]

- Préparation par un commercial autorisé [O5].
- Taux saisi à la main et historisé ; changement avant validation
  [CT5] ; changement refusé au commercial après validation [O3].
- Devises imposées : aucune autre devise acceptée.
- Coût de transformation sur la ligne concernée, avec son unité [CT7,
  CT8] ; aucune grille imposée.
- Prix de revient : **726,47 EUR** (exemple validé) ; ligne de 4,32 t :
  **4 499,41 EUR** [CT6].
- Transport : 369,36 EUR ; hors tonne : montant EUR saisi, jamais
  converti.
- Confirmation, expiration, annulation par le SUPERADMIN avec cause ; KPI.

**Commande, quantités, avenants** [V N6 à N9, K3, K9, K10, K13, K15, K21]

- Une commande par devis.
- Quantité originale figée ; « 100 + 20 = 120 », les 100 jamais
  modifiés ; valorisation des 20 [O1].
- Diminution : refusée sous le livré ; libération seulement des
  affectations désignées ; marchandise disponible à son emplacement et
  dans son état ; aucun mouvement.
- Cas 1 : règles de la ligne appliquées sans refaire la logique de la
  commande [CT : tonne recalculée, hors tonne ressaisie].
- Cas 2 : ligne complète ; ancienne commande intacte [O1, O2].
- Ligne identique : prix applicable repris ; une nouvelle ligne ne change
  aucun prix existant ; renégociation avec date d'effet, ancienne
  condition conservée [portée : O8].
- Avenant : ancienne et nouvelle valeur, utilisateur, date, motif, impact ;
  immuable ; refusé à tout autre compte que le SUPERADMIN.
- Situation : O, V, ajoutées, supplément, livré, reste [K15 ; formules
  CT].

**Affectations et stock** [V N10 à N13, K2, K11, K12]

- Affectation refusée à tout autre compte que le SUPERADMIN (service et
  base).
- Lot NOIR 12 m pour une ligne GALVA 6 m : refusé [V K2] ; signalé
  « utilisable après transformation » [CT13].
- Lot dans l'état identique : accepté, chez GMC ou chez un transformateur.
- Stock chez un transformateur : physiquement chez lui, affecté ou libre,
  **aucun mouvement** et aucune réception lors d'une affectation [V N11].
- Exemple obligatoire 100 / 60 / 40 dans l'état transformé [O4].
- Aucune affectation au-delà du disponible réel ; aucune double
  affectation.
- Garde-fou : envoi, chute ou correction sous l'affecté → refusé ;
  livraison des pièces de la ligne livrée → acceptée [CT11].
- Réaffectation partielle 30 sur 100 : reste 70 [V cahier §17] ; réservée
  au SUPERADMIN [C8].
- Aucune fonction ne choisit un lot automatiquement.

**Transformation** [V K1, N12, N15]

- Après un bon de sortie : GMC −100, transformateur +100 ; lot brut ; il
  ne compte pas comme revenu chez GMC.
- Situation virtuelle (réceptionnable) calculée à partir de ce stock
  [CT12].
- Après la réception (fonction 5.5) : nouveau lot en STOCK_GMC, relié à
  son lot d'origine.

**Corrections d'inventaire** [V K17]

- Refusée à tout autre compte que le SUPERADMIN (service et base).
- Refusée sans PV.
- Acceptée avec PV : référence dans l'audit ; aucun mouvement antérieur
  modifié [CT14].

**SUPERADMIN** [V N14, K16]

- Droits par compte et rôle : un compte nommé « Mohamed » sans le rôle est
  refusé.
- Un second SUPERADMIN actif est refusé [CT1].
- Un SUPERADMIN désactivé est refusé.

**Non-régression**

- 293 tests existants, avec ces adaptations :
  - compte SUPERADMIN dans les outils de test ;
  - 13 appels de `corriger_inventaire` complétés d'une référence de PV ;
  - commandes en brouillon puis confirmées ;
  - motif des suppléments ;
  - emplacement des affectations ;
  - réservations du test 5.5.

  Chaque adaptation sera listée.
- ruff, flake8, mypy.
- `--fresh` deux fois.

---

## 9. Vérifications faites (FACT)

| Vérification | Résultat |
|---|---|
| Base `db/gmc.db` | Empreinte du schéma `89e3225d…ab718e4` identique ; 20 migrations ; aucune donnée métier. |
| Documents de transformation | `bon_commande_transformation_ligne` : `finition_demandee`, `format_debit` (ex. « 2x6m »), `quantite_prevue` ; bon de sortie : lot + quantité ; réception : lot résultat, reçu, chute. |
| Retour de transformation | `stock_service.enregistrer_retour_transformation` : lot résultat en STOCK_GMC, consommation chez le transformateur. |
| Corrections d'inventaire | `stock_service.corriger_inventaire` : aucun contrôle de rôle ; 13 appels dans 3 fichiers de test. |
| `devis_ligne` | `pct_transformation` et `marge_pct` existent sans règle écrite ; ils ne sont **pas** réutilisés pour le coût de transformation. |
| Relecture indépendante | 40 écarts relevés sur le premier jet de cette version ; tous corrigés ; tous les calculs vérifiés exacts (726,47 ; 4 499,41 ; 1 041,53 ; 48,6 / 51,516 / 49,572). |

---

## Annexe — constats de départ (FACT, versions 1 à 3) et traitement proposé

| Constat | Traitement proposé |
|---|---|
| Un devis peut donner plusieurs commandes | Une seule (cahier ; C1) |
| Quantité de commande figée dès la création | Figée à la confirmation ; avenants |
| Une réaffectation partielle efface le reste | Reste explicite |
| Plafond d'affectation = quantité initiale du lot ; emplacement ignoré | Disponibilité par (lot, emplacement) + garde-fou |
| Poids « théorique » obligatoire ; aucun poids sur la commande | Poids de vente, méthode validée |
| Prix sans unité ; une devise pour trois prix | Unités ; devises imposées |
| Transport sans unité, absent de la commande | EUR/t ou montant total EUR |
| Pas de destination ni d'incoterm sur le devis | Ajoutés |
| Client supprimable ; aucun audit client | Anti-suppression + audit |
| Aucun contrôle d'annulation ni de statut | Colonnes + transitions |
| Journal limité à 12 actions | Environ 28 actions |
| Réservation sans contrôle ni auteur | Contrôles, auteur, emplacement |
| Supplément sans motif | Motif obligatoire |
| `v_approvisionnement_ligne` ignore le stock affecté | Non utilisée ; 5.7 |
| SUPERADMIN absent ; taux sans auteur | Ajoutés |
| Aucune migration atomique (pré-existant) | 0021 atomique (CT15) |
| Corrections d'inventaire sans contrôle de rôle | SUPERADMIN + PV (K17) |

---

**PHASE 5.6 — ANALYSE TECHNIQUE EN ATTENTE DE VALIDATION FINALE HUMAINE**
(aucune implémentation avant ta validation ; les choix techniques [CT]
ne sont pas considérés comme validés)
