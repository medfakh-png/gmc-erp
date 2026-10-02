# Phase 5.6 — Analyse consolidée : les AFFAIRES (version 7)

**Statut : ANALYSE UNIQUEMENT — en attente de validation humaine finale.**

- Aucun code, aucune migration (la **0021 n'est pas créée**), aucune
  table, aucun service, aucun repository, aucun test existant modifié,
  base inchangée.
- Ce fichier est **nouveau**. Les documents existants (analyses v4 et v6,
  règles métier, suivi) restent tels quels.
- La v5 n'existe que comme fichier remis dans notre conversation : elle
  n'est ni dans `docs/` ni dans le projet claude.ai. Les passages de la
  v5 dont dépend cette analyse sont donc **cités ici en toutes lettres**.
- Date : 30/09/2026.
- Sources :
  - v5 et v6 ;
  - règles validées des Phases 1 à 5.5 (`docs/BUSINESS_RULES.md`, notées
    « BR § ») ;
  - D1 à D6, N1 à N15, K1 à K22, O1 à O9, C1 à C14 ;
  - tes décisions X1 à X9 (message « Consolidation finale de l'analyse
    v6 ») ;
  - **tes réponses à Y1 à Y5** (message du 30/09 à 23 h 06) ;
  - l'état réel du projet et de la base, vérifié en lecture seule.
- La v6 a été relue par un relecteur indépendant, qui a relevé 21 écarts ;
  tous étaient corrigés.

**Ce qui change dans la v7** (détail au §0) :

- **Y2** et **Y3** sont validés.
- **Y5** remplace **X1** : plus aucune renégociation du prix de vente
  après confirmation.
- **Y1** et **Y4** sont validés dans leur principe, avec quelques
  précisions à confirmer.
- **Y6** et **L1** restent ouverts.

Légende :

- **[V]** : décision validée par toi (source citée).
- **[CT]** : choix technique proposé, **non validé**.
- **[PROP]** : proposition métier de ma part (issue des C), **non
  validée**.
- **[Y…]** : contradiction ou point laissé ouvert, présenté en FACT →
  PROPOSITION → IMPACT → POINT À VALIDER (§22). Je ne tranche aucun Y.
- **FACT** : constaté dans le schéma, le code ou les documents.

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

---

## Sommaire

0. Tes réponses du 30/09 (23 h 06) et leur intégration
1. Objet de la Phase 5.6
2. Périmètre inclus
3. Hors périmètre
4. État réel du projet avant la Phase 5.6
5. Architecture concernée
6. Modèle métier consolidé
   - 6.1 à 6.6 : clients, devis, réservations (dont 6.3 bis :
     réservation d'un lot brut, Y1), commandes, lignes, avenants
   - 6.7 à 6.9 : prix de vente, quantités, poids
   - 6.10 à 6.17 : affectations, compatibilité, suppléments,
     réaffectations, situation, clôture
   - 6.18 à 6.20 : statuts, permissions, historisation
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

---

## 1. Objet de la Phase 5.6

Mettre en place, dans le backend (services Python, sans API HTTP ni
interface), la gestion commerciale des **affaires** :

- clients, devis, réservations informatives ;
- réservation d'un lot brut pour une transformation, dès la confirmation
  du client (Y1) ;
- commandes, avenants, prix de vente ;
- affectations commerciales de lots (y compris chez un transformateur),
  suppléments, réaffectations ;
- clôture avec reliquat ;
- situation calculée de l'affaire ;
- droits par compte et permission.

**Aucune opération de la Phase 5.6 ne crée de mouvement physique de
stock** [V ton message §2].

---

## 2. Périmètre inclus [V]

- clients ;
- devis ;
- réservations informatives ;
- commandes clients et lignes de commande ;
- affectations commerciales, dont celles sur marchandise chez un
  transformateur (X3) ;
- suppléments ;
- réaffectations ;
- avenants ;
- statuts ;
- situation calculée de l'affaire ;
- clôture avec reliquat.

Éléments nécessaires à ce périmètre (ma lecture, avec la source) :

- **Permissions** par compte et module (O5, X4) : chaque opération
  ci-dessus doit contrôler les droits.
- **Poids de vente et prix de revient estimé du devis** (N1 à N5, K4,
  O7, X8, Y2, Y3, Y4) : ils font partie du devis. Le coût réel, la
  répartition du transport réel par poids et la marge restent en 5.9/5.10
  (Y2).
- **Réservation d'un lot brut dès la confirmation du client**, puis
  affectation automatique « avec la transformation » (Y1) : c'est une
  forme d'affectation commerciale, donc dans le périmètre.
  Précisions : **Y1 bis**.
- **Contrôles ajoutés à deux fonctions existantes du Stock Service
  (5.5)**. La 5.6 ne crée aucune nouvelle écriture de stock ; elle
  ajoute seulement des contrôles :
  - `corriger_inventaire` : SUPERADMIN + PV (K17). Base : ton X4 range les
    « corrections sensibles » parmi les « opérations stratégiques de
    Phase 5.6 » ;
  - garde-fou N13 : K12 demande d'empêcher « les mouvements
    incompatibles avec les quantités déjà affectées », donc dès que les
    affectations de la 5.6 existent.
- **Référentiel article minimal** et contrôle des changements d'unité
  d'article : périmètre à confirmer, **Y4 bis**.

---

## 3. Hors périmètre [V]

| Sujet | Phase |
|---|---|
| Achats fournisseurs, réceptions fournisseurs, **partie fournisseur d'O8** | 5.7 |
| Transformations : création des documents de transformation, du lot transformé, **rattachement d'une affectation au lot résultant** (X3) | 5.8 |
| BL client, facturation client | 5.9 |
| Coûts réels et marge | 5.10 |
| Interface | 6 |

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
| Utilisateurs | Rôles COMMERCIAL, MAGASINIER, COMPTABILITE, DIRECTION, ADMINISTRATEUR ; **pas de SUPERADMIN** ; aucune table de permissions. |
| Taux | `taux_change` : colonne `taux REAL > 0`, immuable (triggers), sans auteur. Le schéma ne fixe pas le sens de lecture. Les tests enregistrent `devise='EUR', taux=3.4`, ce qui correspond au sens que tu as validé en Y3 : **TND pour 1 EUR**. |
| Devises | `devis_ligne.devise` et `commande_ligne.devise` : une seule devise par ligne, **TND par défaut** ; `tests/helpers.py` crée des commandes en TND (contraire à K22 pour le prix de vente). |
| Audit | 12 actions (`core.audit.ACTIONS_VALIDES`, synchronisé par test avec le CHECK de la base). |
| Commande | `devis_id` obligatoire mais non unique ; `date_confirmation` obligatoire (même en BROUILLON) ; `quantite_originale` figée dès la création (trigger, quel que soit le statut) ; statuts BROUILLON / CONFIRMEE / SOLDEE / ANNULEE. |
| Devis | Statuts EN_COURS / CONFIRME / EXPIRE / ANNULE ; `poids_theorique_kg` obligatoire ; `pct_transformation` et `marge_pct` sans règle écrite. |
| Affectation | Types INITIALE / SUPPLEMENT ; statut ACTIVE / CLOTUREE ; « non livrée » = active sans `mouvement_physique_id`. Plafond en base = quantité initiale du lot. `quantite_affectable_lot` ne compte que STOCK_GMC. L'affecté non sorti est calculé **par lot et par pool, jamais par emplacement**. |
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
- **Taux de change de l'affaire** [V K5, O2, O3, X5, X7] :
  - saisi à la main par le commercial lors de la préparation ;
  - historisé ;
  - figé à la validation de l'offre, qui est le passage à CONFIRMÉ ;
  - référence de toute l'affaire, avenants compris ;
  - jamais remplacé à chaque avenant ;
  - modification exceptionnelle par le SUPERADMIN seul (effet : **Y6**).
- **Devises imposées** [V K22] : vente EUR, achat matière TND,
  transformation TND, transport EUR ; pré-remplissables, pas librement
  modifiables.
- **Prix de revient estimé** [V K4] : « (PRIX ACHAT MATIÈRE TND + PRIX
  TRANSFORMATION TND) / TAUX DE CHANGE PRÉVISIONNEL + TRANSPORT
  ESTIMATIF EUR ».
  - Exemple validé : 726,47 EUR.
  - Coût de transformation saisi à la main sur chaque ligne concernée.
  - Un seul arrondi final.
  - **Y3 validé** : le commercial saisit le taux en **TND pour 1 EUR**
    (ex. 3,40). Coût EUR = montant TND ÷ taux, calculé exactement, sans
    arrondi intermédiaire. Ta formule X5 « coût EUR = Y (TND) × R » s'y
    retrouve avec R = 1 ÷ taux saisi. R n'est jamais saisi ni arrondi.
- Transport [V X2] : voir 6.7.
- Cycle EN_COURS → CONFIRMÉ / EXPIRÉ / ANNULÉ [V cahier] :
  - annulation par le SUPERADMIN (« Mohamed seul »), avec une cause
    parmi 8 [V cahier] ;
  - validité et prolongation [PROP C5].

### 6.3 Réservations informatives (devis)

- Manuelles, optionnelles, informatives ; jamais un mouvement ni une
  affectation [V cahier].
- Plafond = disponible réel à l'emplacement visé ; annulation, jamais
  suppression [PROP C6].

### 6.3 bis Réservation d'un lot brut pour une transformation [V Y1 ; précisions Y1 bis]

- **Ta décision** : « il peut être réservé dès la confirmation client et
  avec la transformation il sera automatiquement affecté ».
- **Ce qui est validé** :
  - un lot brut encore chez GMC, pas encore envoyé (ex. NOIR 12 m), peut
    être **réservé** pour une ligne de commande d'un autre état (GALVA,
    GPP, 6 m…), dès la confirmation du client ;
  - « avec la transformation », cette réservation devient
    **automatiquement** une affectation.
- **Différence avec la réservation du devis (6.3)** : celle-ci porte sur
  un lot précis, pour une commande, en vue d'une transformation. Ce n'est
  pas un simple repère informatif.
- **Ma proposition de mise en œuvre** (à confirmer, **Y1 bis**) :
  - (a) La réservation est **bloquante** : déduite du disponible, elle
    empêche toute autre affectation ou réservation du même lot. Sinon,
    l'affectation automatique pourrait devenir impossible.
  - (b) « Avec la transformation » = **au bon de sortie**, quand la ligne
    du bon de sortie reçoit un résultat prévu identique à la réservation.
    C'est cohérent avec X3 : une marchandise chez le transformateur est
    affectable. Autre possibilité : à la réception (5.8).
  - (c) « Confirmation client » = commande **CONFIRMÉE**.
  - (d) La réservation est posée par le **SUPERADMIN** (N10, comme une
    affectation).
  - (e) Le lot et la quantité sont **choisis à la main** au moment de la
    réservation. La conversion automatique ne choisit rien : même lot,
    même quantité, même état prévu, et elle est tracée. Elle respecte donc
    « le système ne choisit jamais le lot ».
  - (f) La transformation prévue (finition, longueur, quantité attendue en
    pièces) est **déclarée à la réservation**. En 5.8, le bon de sortie
    devra la respecter. Tant que la réservation existe, le lot ne peut
    être ni envoyé vers une autre transformation, ni vendu brut.
  - (g) La réservation se libère :
    - par l'annulation de la commande ;
    - par la clôture avec reliquat (elle figure dans la liste X6) ;
    - par une diminution (choix explicite, N7) ;
    - ou par le SUPERADMIN, avec un motif.
- Pour un lot brut **non réservé**, le signal « utilisable après
  transformation » reste proposé (CT13).

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

### 6.5 Lignes de commande

- Origine **DEVIS** (ligne issue du devis) ou **AVENANT** (nouvel article,
  cas 2) [V K21, O1] ; représentation [CT16].
- Chaque ligne porte : unité de vente, poids, prix de vente **en EUR**
  (FACT : TND par défaut aujourd'hui), transport, coûts estimés [V K22 ;
  CT9].
- Aucun taux propre à la ligne : le taux est celui de l'affaire [V O2,
  X7].

### 6.6 Avenants [V K9, K21, O1, D4]

- Toute modification après validation de la commande = avenant,
  **SUPERADMIN** [V K9, X4].
- Contenu : ancienne valeur, nouvelle valeur, utilisateur, date/heure,
  motif, impact, historique.
- **Cas 1** — article déjà dans la première version : règles existantes
  de la ligne, sans refaire inutilement la logique de la commande.
- **Cas 2** — nouvel article : nouvelle ligne complète (article,
  finition, longueur, unité, quantité, poids, prix, coût matière, coût de
  transformation, transport, **taux de l'affaire**, autres données).
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
  - **Y5 remplace X1** : « le nouveau prix s'applique à toutes les lignes
    identiques » est sans objet. Y5 remplace aussi la partie
    « renégociation » de K10 (« nouveau prix historisé ; date d'effet ») et
    la phrase d'O8 « si une nouvelle négociation commerciale avec le client
    est nécessaire… ».
  - Ce qui reste de K10 : une nouvelle ligne identique ajoutée par
    avenant reprend le prix confirmé ; aucune ligne ne modifie le prix
    d'une autre.
  - Ma lecture de K21 cas 2 : le prix d'un **nouvel article** ajouté par
    avenant est fixé dans l'avenant. Ce n'est pas une renégociation d'un
    prix déjà confirmé.
  - Correction d'une erreur de saisie après confirmation : **Y5 bis**.
- Le prix de vente confirmé n'est jamais modifié parce qu'un coût d'achat
  change [V O8].
- Une autre commande peut avoir un autre prix [V N8].
- **Transport** [V X2, Y2] :
  - saisi dans le devis en **EUR/T** ;
  - ligne vendue en TONNE : transport EUR = EUR/T × quantité en tonnes
    (ex. 4,32 t × 85,50 = 369,36 EUR) ;
  - autre unité : **aucun poids implicite**, aucune conversion cachée en
    tonnes. Le **montant total estimé** en EUR est saisi manuellement sur
    la **ligne du devis**, en même temps que le **poids de la ligne**
    (Y2). La saisie est obligatoire ; 0 seulement s'il est saisi (BR §19).
  - Plus tard (5.9/5.10) [V Y2] : le montant **final** du transport est
    saisi après facturation, puis réparti **au poids** entre les articles
    pour calculer la marge par article, dans les résultats et le tableau
    de bord. En 5.6, cela impose seulement de conserver un poids pour
    chaque ligne (calculé ou déclaré).

### 6.8 Quantités [V N6, K3, K13, K15, O1] ; formules [CT]

| Grandeur | Définition |
|---|---|
| O — originale | Fixe dans l'historique, jamais écrasée [V] ; figée à la confirmation, libre en brouillon [PROP C1] ; 0 pour une ligne créée par avenant [CT16] |
| A — avenants | Ajouts et diminutions, historiquement identifiables [V O1] |
| V — en vigueur | O + A (100 + 20 = 120) ; les 100 ne deviennent jamais 120 [V] |
| Normal | Toute quantité jusqu'à V, avenants compris : **quantité normale** [V O1] |
| Supplément | Quantité réellement livrée/facturée **au-delà de V** [V O1, O8 §4] ; reste un supplément [V X9] |
| Livré | Lignes de BL (5.9), normal et supplément séparés |
| Reste à livrer | V − livré normal [CT] |
| À approvisionner | V − (affecté normal actif non livré + livré normal) [CT] ; alimente la 5.7 (« manques → approvisionnement », cahier) |
| Reliquat | V − livré normal au moment d'une clôture avec reliquat [V X6 ; CT19] |

- Diminution autorisée, jamais sous le livré [V K13].
- Une diminution sous l'affecté exige la désignation **explicite** des
  affectations à réduire ou libérer [V N7].
- La marchandise libérée reste stock GMC disponible selon son emplacement
  et son état [V N7, K13].

### 6.9 Poids [V N1 à N4, K6, K7, K18 à K20, O7, X8, Y2, Y4]

- **Vente en TONNE** (et en KG si Y4 bis le confirme) : poids calculé
  par la méthode validée de la fiche article ; aucune saisie manuelle
  arbitraire.
  - Méthode manquante → le système demande de compléter le référentiel.
  - GALVA : poids brut × (1 + % ÷ 100). GPP : poids brut × 1,02. Jamais
    cumulés.
  - Exemples : 48,6 / 51,516 / 49,572 kg ; 100 barres GALVA = 5,1516 t.
- **Hors tonne** (PIÈCE, ML, M², autre unité autorisée) :
  - poids **déclaré obligatoire**, saisi sur la ligne du devis (Y2) =
    **poids final** de la commande ;
  - aucun +2 % GPP réappliqué ; pas de GALVA hors poids (Y4) ;
  - la quantité et l'unité de vente restent les données commerciales
    principales ;
  - pas d'intervention automatique sur le dossier à cause du seul poids.
- Usages du poids déclaré [V O7, « notamment »] :
  - le poids final de la commande ;
  - le **prix de revient estimatif** : un prix au poids se multiplie par
    le poids déclaré, par exemple 2 800,5 TND/t × 0,5 t = 1 400,25 TND ;
  - le transport « lorsque celui-ci est exprimé en EUR/T » : **remplacé
    par X2 et Y2** (hors tonne, montant total saisi, aucune conversion) ;
  - plus tard (5.9/5.10), la **répartition au poids du transport réel**
    pour la marge par article (Y2).
- Poids de vente figé à la confirmation [V cahier].
- **Y4** [V] : « la galvanisation sera effectuée que sur un article dont
  son unité de vente soit kg ou tonne ».
  - Une ligne GALVA vendue en PIÈCE, ML, M² ou autre unité est
    **refusée**.
  - Toute vente GALVA est donc une vente au poids : poids brut calculé
    × (1 + % ÷ 100).
  - Précisions à confirmer (**Y4 bis**) : unité de la ligne ou de
    l'article ; la vente en KG se traite-t-elle comme la tonne ?
  - Pour la 5.8 : un envoi en galvanisation ne concerne que ces articles.
- **X8 = B** [V] : le % GALVA reste obligatoire dans la référence article
  pour vendre en GALVA (option (b) de la v5 : « toute vente GALVA exige
  un % renseigné, même hors tonne, pour compléter le référentiel, sans
  l'appliquer »).
  - Avec Y4, il n'y a plus de vente GALVA hors poids. La partie « hors
    tonne » de X8 ne se présente donc plus. Le % reste obligatoire pour
    toute vente GALVA.
  - Les trois états (défini, 0 % = brut, non renseigné) sont conservés.
  - Un % non renseigné n'est jamais converti en 0 [V K20].
  - Le référentiel se construit progressivement (K7) ; une vente GALVA
    sur un article sans % déclenche la demande de compléter.
- **GPP** : pas concerné par Y4. Une vente GPP hors poids reste possible,
  avec le poids déclaré tel quel, sans +2 % (O7).
- Référentiel : comparer, présenter, ne jamais choisir silencieusement,
  validation SUPERADMIN, historique [V N1, K7] ; périmètre **Y4 bis**.

### 6.10 Affectations commerciales [V D5, N10, N11, N13, K11, K12]

- Par le **SUPERADMIN seul** pour le moment [V N10] ; choix **manuel**
  du lot ; aucun FIFO ; le système ne choisit jamais.
- Une affectation n'est **jamais un mouvement physique** et ne change
  jamais la localisation.
- Contrôles :
  - disponibilité réelle par (lot, emplacement) ;
  - aucune double affectation incompatible ;
  - aucune allocation au-delà du disponible ;
  - aucun mouvement incompatible avec l'affecté.
- Valorisation (5.10) : quantité normale → coût réel du lot ; supplément
  → CMP à la sortie [V BR §1].
- **O8 cas A** [V] : un ajout couvert par le stock GMC disponible → lot
  existant affecté manuellement, coût réel de ce lot, aucune commande
  fournisseur. Lot, allocation, utilisateur et date sont tracés.
  - Ma lecture (**L1**, à confirmer) : ton §5 range le cas A dans « la
    partie fournisseur … Phase 5.7 ». Je lis que **l'affectation**
    utilisée dans ce cas est celle de la 5.6, déjà dans le périmètre.
    Le choix « stock disponible → lot existant / indisponible → achat »
    et tout le côté fournisseur restent en 5.7.

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
- FACT : aucun code ne crée encore de bon de sortie (5.8). En 5.6, le
  résultat prévu se déclare sur une ligne de bon de sortie existante,
  par une fonction SUPERADMIN tracée [CT18]. En 5.8, il se saisira à la
  création du bon.
- Cohérence du résultat prévu [V D1] : même article ; longueur égale ou
  sous-multiple exact (12 m → 6 m) ; quantité attendue ≤ quantité
  envoyée × (longueur d'origine ÷ longueur prévue). Tout autre cas est
  refusé.
- Lot brut encore **chez GMC** (pas encore envoyé) pour une ligne d'un
  autre état : **réservation** dès la confirmation du client, qui devient
  une affectation avec la transformation [V Y1] ; voir §6.3 bis et Y1 bis.
  Au bon de sortie, le résultat prévu déclaré doit être identique à celui
  de la réservation.

### 6.12 Compatibilité [V D1, K2, O4, X3]

- Même article ; même finition ; même longueur : compatibilité
  **directe** d'un lot déjà dans l'état commercial demandé.
- Exceptions de D1, préservées :
  - NOIR/LAC → GALVA/GPP ;
  - 12 m → 2 × 6 m (multiples exacts) ;
  - LAC = NOIR.
- Elles passent **par une transformation** : « le lot brut 12 m ne doit
  jamais être considéré directement disponible comme 6 m » [K2]. Elles
  deviennent affectables dès que la marchandise est chez le
  transformateur avec son résultat prévu (X3). Avant l'envoi, elles sont
  réservables dès la confirmation du client (Y1, §6.3 bis).
- [CT] L'état se compare sur article, finition, longueur.

### 6.13 Suppléments [V O1, X9, cahier, BR §4]

- Supplément = au-delà de la quantité en vigueur ; motif obligatoire ;
  affectation par le SUPERADMIN ; prélevé sur du stock réellement
  disponible et non affecté ailleurs.
- **X9 = A** : un supplément enregistré **reste un supplément**. Aucune
  modification ultérieure de la commande ne le requalifie, ni
  automatiquement ni rétroactivement. Son historique est conservé.
- [CT17] Tant que le normal n'atteint pas V, une nouvelle affectation est
  INITIALE.

### 6.14 Réaffectations [V BR §7, cahier ; PROP C8]

- Tracée, motif obligatoire, partie non livrée seulement.
- Reste conservé : 30 sur 100 → reste 70 [V cahier].
  - FACT : le trigger clôture toute l'origine.
  - [CT] Le reste de 70 est donc recréé explicitement, même lot, même
    emplacement, **même type que l'origine** (X9 : un supplément reste
    un supplément).
- [PROP C8] SUPERADMIN ; à la **destination** (autre affaire), typage
  selon la quantité en vigueur restante de la destination : INITIALE dans
  la limite de V, sinon SUPPLÉMENT. Ce n'est pas une requalification de
  l'origine, mais une nouvelle affectation d'une autre affaire.
  - Point à confirmer avec C8 : un supplément déplacé peut-il devenir
    INITIALE à la destination ?

### 6.15 Libérations [V N7, X6 ; PROP C9]

- Libération explicite en cas de diminution (N7) et à la clôture (X6).
- [PROP C9] Libération pour erreur : SUPERADMIN, motif, tracée.

### 6.16 Situation de l'affaire [V K15, O1, O4, D5]

Calculée, jamais saisie :

- par ligne : O, A, V, normal affecté, supplément, livré, reste,
  à approvisionner, reliquat ;
- stock par emplacement, catégories A à F de D5 :

| D5 | Contenu | Calcul [CT] |
|---|---|---|
| A. Disponible chez GMC | STOCK_GMC − affecté non livré | 5.6 |
| B. Chez le galvanisateur | stock physique chez chaque transformateur | 5.6 |
| C, D. Chez lui, affecté / non affecté | par emplacement | 5.6 |
| E. Envoyé, en attente de réception | calculé à partir du stock physique chez lui (K1) [CT12] | 5.6 |
| F. Transformé ou à transformer, chez lui | représenté par le **résultat prévu** de la ligne du bon de sortie. Pas de lot transformé avant la réception (K1). Affectable (X3), non vendable. | 5.6 (lot en 5.8) |
| (en plus) Lots bruts réservés chez GMC | réservations pour transformation (Y1), déduites du disponible si Y1 bis (a) | 5.6 |

- Les quatre notions d'O4 sont affichées.
- Formules [CT] au §6.8.

### 6.17 Clôture avec reliquat [V C10, X6]

Opération contrôlée **unique** :

1. le SUPERADMIN demande la clôture ;
2. le système calcule et affiche le reliquat (ex. 100 commandées,
   70 livrées → 30 ; « les 30 peuvent encore être affectées à
   différentes allocations ») ;
3. le système affiche les affectations encore présentes sur ce reliquat,
   ainsi que les réservations de lots bruts (Y1) ;
4. le SUPERADMIN confirme ;
5. ces affectations sont libérées dans le cadre de la clôture ;
6. motif obligatoire (ex. reliquat annulé par le client, devenu inutile,
   commande abandonnée, autre motif justifié) ;
7. la commande est clôturée, reliquat et historique conservés.

Règles associées :

- Le système ne choisit jamais seul les affectations à libérer en dehors
  de cette opération confirmée.
- Le reliquat n'est **jamais transformé en livraison**.
- La marchandise présente reste du stock GMC selon sa localisation et son
  état.
- Représentation [CT19].
- Signal « entièrement livrée » [V cahier] ; définition [PROP C10].

### 6.18 Statuts

| Document | Statuts (FACT) | Transitions |
|---|---|---|
| Devis | EN_COURS, CONFIRME, EXPIRE, ANNULE | [V cahier] ; contrôle en base [CT] |
| Commande | BROUILLON, CONFIRMEE, SOLDEE, ANNULEE | [V cahier] ; clôture avec reliquat → SOLDÉE + reliquat + motif [CT19] |
| Affectation | ACTIVE, CLOTUREE | + raison de clôture : réaffectation, libération, réduction, clôture de commande [CT] |
| Réservation de devis | (aucun aujourd'hui) | active / annulée [PROP C6] |
| Réservation de lot brut (Y1) | nouvelle | active → convertie en affectation / libérée [CT21] |

### 6.19 Permissions [V O5, X4, N10, N14, K8, K16]

- Le SUPERADMIN crée les comptes et définit les accès : utilisateur par
  utilisateur, module par module, permission par permission si
  nécessaire.
- Le rôle COMMERCIAL ne donne pas automatiquement tous les droits
  commerciaux.
- Droits liés au **compte utilisateur et à son rôle/ses permissions**,
  jamais au nom affiché. Aucune règle ne s'appuie sur le nom « Mohamed »
  [V X4].
- **Opérations réservées au SUPERADMIN** [V] :
  - avenants ;
  - corrections sensibles, dont les corrections d'inventaire (K17) ;
  - modifications stratégiques, dont l'intervention sur un devis
    CONFIRMÉ et le taux (O3, X7) ;
  - clôture avec reliquat ;
  - gestion des droits (X4) ;
  - affectations, suppléments compris, et réservations de lots bruts
    (N10 ; Y1 bis (d)) ;
  - clients ;
  - annulation d'un devis ;
  - annulation d'une commande confirmée (cahier) ;
  - création d'article et validation du référentiel (BR §11, K7) ;
  - déclaration du résultat prévu d'une transformation (CT18).
- Délégation future prévue ; **aucune délégation supplémentaire active**
  [V X4, K8].
- Mécanisme [CT2] : catalogue de permissions dont les opérations
  réservées sont marquées « réservé SUPERADMIN » (non attribuables tant
  que tu n'as pas décidé une délégation). Le marquage est une donnée,
  levable sans reprogrammer.

### 6.20 Historisation / audit

- Jamais d'écrasement : quantités, prix (négociés au stade du devis,
  figés à la confirmation : Y5), taux (X7), avenants, réservations,
  affectations, clôtures, droits.
- Audit : 12 actions aujourd'hui → **33 proposées** (34 si le référentiel
  article est en 5.6, avec CREATION_ARTICLE, Y4 bis) [CT] :
  - les 12 existantes, dont REAFFECTATION, QUANTITE_SUPPLEMENTAIRE,
    MODIFICATION_PRIX, ANNULATION_DOCUMENT, CORRECTION_INVENTAIRE ;
  - 21 nouvelles : CREATION_CLIENT, MODIFICATION_CLIENT, CREATION_COMPTE,
    MODIFICATION_COMPTE, ATTRIBUTION_PERMISSION, RETRAIT_PERMISSION,
    VALIDATION_REFERENTIEL_ARTICLE, SAISIE_TAUX_DEVIS, CONFIRMATION_DEVIS,
    INTERVENTION_DEVIS_CONFIRME, PROLONGATION_DEVIS, RESERVATION,
    ANNULATION_RESERVATION, CONFIRMATION_COMMANDE, AVENANT_COMMANDE,
    AFFECTATION, LIBERATION_AFFECTATION, CLOTURE_COMMANDE,
    DECLARATION_RESULTAT_PREVU, RESERVATION_LOT_BRUT,
    CONVERSION_RESERVATION_AFFECTATION.
  - Les changements de prix au stade du devis sont tracés avec l'action
    existante MODIFICATION_PRIX (Y5).

---

## 7. Impacts base de données

### 7.1 Créé en 5.6 (dans la future 0021) — voir §11

### 7.2 Préparé seulement (aucune colonne créée en 5.6)

| Pour | Élément | Raison |
|---|---|---|
| 5.7 | Prix négocié d'une commande fournisseur confirmée historisé, jamais écrasé ; statut « confirmée » ; historique des négociations ; `v_approvisionnement_ligne` sur V (FACT : utilise la quantité originale) | O8 fournisseur |
| 5.8 | Création des documents de transformation (dont la saisie du résultat prévu à la création du bon de sortie, identique à celui d'une réservation Y1) ; envoi galvanisation limité aux articles vendus au poids (Y4) ; lien affectation → lot résultant ; coupe 1 → N ; écarts reçu/prévu | X3, Y1, Y4 |
| 5.9 | Interdiction de livrer une affectation sur transformation non rattachée, et de vendre brut un lot réservé ; saisie du montant final du transport après facturation (Y2) | X3, Y1, Y2 |
| 5.10 | Coût réel, marge ; **répartition du transport final au poids entre les articles** pour la marge par article, dans les résultats et le tableau de bord (Y2) | Y2 |
| Plus tard | Autres emplacements (O9) ; import de la MV | O9 |

---

## 8. Impacts services

| Service | Nouveau / modifié | Contenu |
|---|---|---|
| `droits_service` | Nouveau | Comptes (SUPERADMIN seul) ; attribution/retrait de permissions, audités ; vérification compte actif + permission ; opérations réservées. |
| `client_service` | Nouveau | Créer/modifier (SUPERADMIN), audit, jamais de suppression. |
| `referentiel_article_service` | Nouveau (selon **Y4 bis**) | Création d'article (SUPERADMIN) ; valeurs candidates présentées sans choisir ; validation SUPERADMIN (méthode, % GALVA) avec historique. |
| `core/poids_vente.py` | Nouveau | Tonne (et KG selon Y4 bis) : méthode × facteur de finition (NOIR 1 ; GALVA 1 + %/100 ; GPP 1,02) ; hors tonne : poids déclaré obligatoire, jamais majoré ; GALVA seulement en vente au poids (Y4) ; % GALVA exigé pour une vente GALVA (X8). |
| `core/prix_revient.py` | Nouveau | Conversion TND → EUR : montant TND ÷ taux (TND pour 1 EUR, Y3) ; prix au poids × poids déclaré hors tonne (O7) ; prix de revient exact, un seul arrondi ; transport selon X2/Y2. |
| `devis_service` | Nouveau | Préparation (permission) ; taux saisi en TND pour 1 EUR et historisé ; devises imposées ; coûts ; poids ; transport ; prix de revient ; **négociation du prix au stade du devis, tracée** (Y5) ; réservations informatives ; confirmation (taux, prix et conditions figés) ; intervention SUPERADMIN (Y6) ; expiration, prolongation ; annulation (SUPERADMIN). |
| `commande_service` | Nouveau | Création depuis le devis ; brouillon ; confirmation ; avenants cas 1/cas 2 (prix confirmé repris ; nouveau prix seulement pour un nouvel article) ; **aucune renégociation du prix après confirmation** (Y5) ; diminution (N7, K13) ; annulation ; clôture avec reliquat X6 (affectations et réservations listées). |
| `affectation_service` | Nouveau | SUPERADMIN ; lot choisi à la main ; état identique ou résultat prévu (X3) ; déclaration du résultat prévu (CT18) ; **réservation d'un lot brut et conversion automatique en affectation** (Y1, CT21) ; INITIALE / SUPPLÉMENT (O1, X9) ; réaffectation avec reste recréé ; libération ; plafonds par emplacement. |
| `situation_service` | Nouveau, lecture seule | §6.16. |
| `stock_service` | Modifié | `corriger_inventaire` : SUPERADMIN + PV (K17) ; quantité affectable par emplacement ; garde-fou N13 sur tous les mouvements ; retour de transformation refusé si le lot porte une affectation sur résultat prévu, jusqu'à la 5.8 (CT18). |
| `unite_valorisation_service` | Modifié (selon **Y4 bis**) | Changement d'unité d'un article réservé au SUPERADMIN (BR §11, §16). |
| `core/audit.py` | Modifié | 33 actions (34 selon Y4 bis) (§6.20). |

---

## 9. Impacts repositories

| Repository | Nouveau / modifié |
|---|---|
| `client_repository`, `utilisateur_repository`, `permission_repository` | Nouveaux |
| `devis_repository` (devis, lignes, taux), `reservation_repository` | Nouveaux |
| `commande_repository`, `avenant_repository` (avenants) | Nouveaux |
| `affectation_repository` (affecté actif non livré par lot, emplacement, ligne, type ; résultat prévu ; réservations de lots bruts) | Nouveau |
| `situation_repository` (lectures agrégées, livré par ligne et type) | Nouveau |
| `referentiel_article_repository` | Nouveau (selon Y4 bis) |
| `stock_repository` | Modifié : affecté non livré **par emplacement** (FACT : aujourd'hui par lot et par pool seulement) |
| `article_repository` | Modifié : lecture des paramètres validés |

---

## 10. Impacts tests

- **142 nouveaux cas** proposés (§12).
- **293 tests existants conservés** (§13), avec des adaptations limitées
  et listées.
- Les tests qui dépendent d'un point encore ouvert portent son repère
  (Y1 bis, Y4 bis, Y5 bis, Y6, L1, C, CT).

---

## 11. Migration 0021 — proposition uniquement

**Migration 0021 : à créer lors du CODAGE de la Phase 5.6, après
validation finale de l'analyse.** Elle n'existe pas. Elle serait atomique
et additive [CT15] : anciennes lignes reprises, contrôles doublés en
base, valeurs par défaut pour que les insertions existantes restent
valides dans la mesure du possible.

| # | Table | Contenu proposé | Source |
|---|---|---|---|
| DB1 | `utilisateur` | Rôle SUPERADMIN (reconstruction de la table : le CHECK change) ; un seul SUPERADMIN actif (index unique partiel) | [V N14] ; CT1 |
| DB2 | `permission`, `utilisateur_permission` (nouvelles) | Catalogue module/opération + marque « réservé SUPERADMIN » ; attributions (par, le), retraits tracés, jamais supprimés | [V O5, X4] ; CT2 |
| DB3 | Référentiel article (selon Y4 bis) | Paramètres validés et historisés : méthode de poids, valeur et unité, % GALVA à trois états, sources, validé par/le ; paramètre GPP 1,02 ; masse linéique actuelle lue comme « valeur MV à vérifier » | [V N1, N3, N4, K7, K20, X8] ; CT3, CT4 |
| DB4 | `taux_change` | + auteur ; + motif pour une modification exceptionnelle | [V K5, X7] ; CT5 |
| DB5 | `devis` | Destination, incoterm ; annulation (cause, commentaire) ; confirmé par/le ; prolongation ; transitions contrôlées | [V cahier, O3] ; C4, C5 |
| DB6 | `devis_ligne` | Unité et quantité de vente (+ KG selon Y4 bis) ; poids (valeur, unité, origine CALCULÉ/DÉCLARÉ, méthode et % utilisés) ; une devise par prix, **vente EUR imposée** ; contrôle « GALVA seulement en KG ou TONNE » ; coût de transformation (indicateur, montant, unité) ; transport (EUR/t en tonne, montant total EUR hors tonne) ; instantané du prix de revient à CONFIRMÉ | [V K4, K22, O7, X2, X8, Y2, Y4, cahier] ; CT6, CT7, CT8, CT20 |
| DB7 | `reservation_devis` | Emplacement, auteur, annulation | [V cahier] ; C6 |
| DB8 | `commande_client` | Un devis → une commande (index unique) ; annulation ; clôture (motif, commentaire, par, le) ; `date_confirmation` facultative en brouillon si C14 l'exige | [V cahier, X6] ; C1, C14, CT19 |
| DB9 | `commande_ligne` | Lien ligne de devis ; origine DEVIS/AVENANT ; unité, poids, prix EUR imposé, transport, coûts estimés ; **aucune colonne de taux** | [V O1, O2, K21, K22, X7] ; CT9, CT16 |
| DB9b | `commande_ligne` (trigger) | Quantité originale libre en brouillon puis figée (remplace `trg_commande_ligne_qte_immuable`) | [PROP C1] |
| DB10 | `avenant` (nouvelle) | Type, cible, valeurs avant/après, motif, impact, auteur, date ; immuable | [V K9, O1] ; CT10 |
| DB11 | `commande_ligne` (trigger) | **Prix de vente figé à la confirmation** : toute modification refusée ensuite (Y5). Plus de table d'historique des prix, ce qui remplace le DB11 de la v6 lié à X1. Les changements au stade du devis sont tracés dans l'audit. | [V Y5, K10] ; Y5 bis |
| DB12 | `affectation_stock` | Emplacement ; référence de la ligne de bon de sortie et état prévu pour une affectation sur transformation ; **nature « réservation de lot brut »** (lot, quantité, état prévu, quantité attendue) et trace de sa conversion en affectation ; raison de clôture ; plafond par emplacement (trigger remplacé), réservations comprises | [V N11, X3, Y1] ; CT11, CT17, CT18, CT21 |
| DB13 | Reliquat de clôture (nouvelle) | Par ligne : V, livré normal, reliquat à la clôture ; immuable | [V X6] ; CT19 |
| DB14 | `journal_audit` | CHECK étendu à 33 actions (34 selon Y4 bis) ; reconstruction, audit recopié | [V] ; CT |
| DB15 | Corrections d'inventaire | SUPERADMIN exigé en base ; référence et date du PV dans l'audit | [V K17] ; CT14 |
| DB16 | `client` | Anti-suppression | [V cahier] |
| DB17 | `bon_sortie_transformation_ligne` | Résultat prévu **saisi** : finition, longueur, quantité attendue en pièces + lien vers la ligne du bon de commande de transformation ; déclarant, date ; figé dès qu'une affectation s'y rattache | [V X3 = option A de la v5, D1] ; CT18 |
| DB18 | `reaffectation` | Reste explicite recréé ; même lot, même emplacement ; type d'origine conservé pour le reste | [V BR §7, cahier, X9] ; C8 |

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
- Le nombre baissera de 3 si le référentiel article n'est pas en 5.6
  (Y4 bis : R10, M02, I16).

| Catégorie | Nombre |
|---|---|
| Unitaires (U) | 22 |
| Repository (R) | 10 |
| Services — contrat technique (S) | 6 |
| Permissions (P) | 16 |
| Métier (M) | 64 |
| Intégrité (I) | 16 |
| E2E (E) | 8 |
| **Total nouveaux** | **142** |
| Non-régression | 293 existants + 3 contrôles (§13) |

**Unitaires (U)**

- U01 IPE100 6 m NOIR = 48,6 kg [N1, N2].
- U02 GALVA 6 % = 51,516 kg [N3].
- U03 GPP = 49,572 kg [N4, K19].
- U04 GALVA 0 % défini = 48,6 kg [K20].
- U05 % GALVA non renseigné → demande de compléter, jamais 0 [K20, X8].
- U06 GPP jamais cumulé avec GALVA [K19].
- U07 100 barres GALVA = 5,1516 t [N3].
- U08 Hors tonne (NOIR ou GPP) : poids déclaré rendu tel quel, aucune
  majoration (pas de +2 % GPP) [O7].
- U09 Hors tonne : poids déclaré absent → refus [O7].
- U10 Tonne : poids manuel refusé [K18].
- U11 Exemple K4 : achat 2 000 TND, transformation 300 TND, taux 3,40
  (TND pour 1 EUR), transport 50 EUR → 726,47 EUR [K4, X5, Y3].
- U12 Ligne 4,32 t : achat 2 800,5 TND/t, transformation 450 TND/t, taux
  3,40, transport 85,50 EUR/t → 4 499,41 EUR (1 041,53 EUR/t) [K4, X5,
  Y3 ; CT6].
- U13 Un seul arrondi final, aucun arrondi intermédiaire [K13, BR §17].
- U14 Transport tonne : 4,32 t × 85,50 = 369,36 EUR [X2].
- U15 Transport hors tonne = montant total EUR saisi sur la ligne du
  devis, jamais converti [X2, Y2].
- U16 V = O + avenants (100 + 20 = 120) [K3, O1].
- U17 Reste à livrer = V − livré normal [K15 ; CT].
- U18 À approvisionner = V − (affecté normal actif non livré + livré
  normal) [CT].
- U19 Reliquat 100 / 70 → 30 [X6].
- U20 Cohérence du résultat prévu : 100 × 12 m → au plus 200 × 6 m ;
  12 m → 5 m (pas un multiple exact) refusé [D1 ; CT18].
- U21 Hors tonne : prix au poids × poids déclaré (2 800,5 TND/t × 0,5 t
  = 1 400,25 TND) [O7].
- U22 Ligne GALVA vendue en KG : poids calculé × (1 + % ÷ 100), comme la
  tonne [Y4 ; Y4 bis].

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
- R10 Référentiel article : historique des paramètres [Y4 bis].

**Services — contrat technique (S)**

- S01 Une transaction par opération : un échec n'écrit rien (ex. avenant
  + audit).
- S02 Chaque opération sensible écrit une ligne d'audit avec avant/après
  et motif.
- S03 Erreurs métier en français (`core.erreurs`).
- S04 Numérotation DEV/CMD séquentielle par année.
- S05 Aucune opération 5.6 n'écrit dans le registre ni dans le CMP.
- S06 Les lectures (situation, disponibilité) n'écrivent rien.

**Permissions (P)**

- P01 Seul le SUPERADMIN crée un compte.
- P02 Seul le SUPERADMIN attribue ou retire une permission ; audité.
- P03 Compte COMMERCIAL sans permission : préparer un devis refusé [O5 ;
  CT2 : le rôle ne donne aucune permission automatiquement].
- P04 Après attribution de « préparer un devis » : accepté ; après
  retrait : refusé.
- P05 « Consulter » requis pour lire la situation [O5].
- P06 Permission réservée non attribuable à un autre compte [X4 ; CT2].
- P07 Compte nommé « Mohamed » sans rôle SUPERADMIN : refusé [K16, X4].
- P08 SUPERADMIN désactivé : refusé [CT1].
- P09 Affectation refusée à un non-SUPERADMIN, même avec toutes les
  permissions attribuables [N10].
- P10 Avenant refusé à un non-SUPERADMIN [K9, X4].
- P11 Clôture avec reliquat refusée à un non-SUPERADMIN [X4, X6].
- P12 Intervention sur un devis CONFIRMÉ (taux) : refusée au commercial,
  acceptée au SUPERADMIN et tracée [O3, X7 ; Y6].
- P13 Correction d'inventaire refusée à un non-SUPERADMIN [K17].
- P14 Annulation d'un devis ou d'une commande confirmée refusée à un
  non-SUPERADMIN [cahier].
- P15 Création ou modification d'un client refusée à un non-SUPERADMIN
  [cahier].
- P16 Réservation d'un lot brut refusée à un non-SUPERADMIN [N10 ; Y1 bis
  (d)].

**Métier (M)**

*Clients et référentiel*

- M01 Client créé ou modifié par le SUPERADMIN, audité ; suppression
  refusée [cahier].
- M02 Valeurs candidates présentées, aucune choisie ; validation
  SUPERADMIN ; historique [N1, K7 ; CT3 ; Y4 bis].
- M03 Vente en tonne sans méthode validée → demande de compléter [K18].
- M04 Vente GALVA (au poids) sur un article sans % → demande de
  compléter [X8, Y4].
- M05 Article sans méthode : vente hors tonne possible, projet non
  bloqué [K7].

*Devis*

- M06 Taux saisi à la main, historisé avec auteur [K5 ; CT5].
- M07 Avant CONFIRMÉ : nouveau taux possible, ancien conservé [K5 ;
  CT5].
- M08 CONFIRMÉ fige taux et conditions ; modification refusée à
  l'utilisateur opérationnel [O3, X7].
- M09 Devises imposées (vente EUR…) ; toute autre refusée [K22].
- M10 Coût de transformation obligatoire si une transformation est
  prévue ; 0 seulement s'il est saisi [K4 ; CT7, CT8].
- M11 Transport obligatoire sur la ligne du devis, poids de la ligne
  obligatoire hors tonne ; 0 seulement s'il est saisi [BR §19, Y2].
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

- M20 Avenant +20 : O = 100 inchangée, V = 120, avenant complet
  (ancienne/nouvelle valeur, utilisateur, date, motif, impact) [K3, K9,
  O1].
- M21 Les 20 d'avenant sont affectables en INITIALE (quantité normale)
  [O1].
- M22 Cas 2 : ligne AVENANT, O = 0, V = quantité, taux de l'affaire,
  estimations saisies [K21, O2, X7 ; CT16].
- M23 Cas 1 : méthode de la ligne inchangée ; poids en tonne recalculé
  par la méthode [K21 ; CT10].
- M24 Aucun nouveau taux demandé pour un avenant [O2, X7].
- M25 Diminution sous le livré refusée [K13].
- M26 Diminution sous l'affecté : désignation explicite des affectations
  à libérer [N7].

*Prix de vente*

- M27 Y5 : après confirmation, toute modification du prix de vente
  d'une ligne de commande est refusée, y compris par avenant (sauf
  décision contraire en Y5 bis).
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
- M34 INITIALE jusqu'à V ; au-delà, SUPPLÉMENT avec motif obligatoire
  [O1, cahier].
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
- M43 Y1 : lot NOIR 12 m encore chez GMC réservé pour une ligne GALVA
  6 m dès la confirmation du client, avec la transformation prévue
  déclarée ; la réservation est déduite du disponible [Y1 ; Y1 bis (a),
  (c) ; CT21]. Un lot non réservé reste seulement signalé « utilisable
  après transformation » [CT13].
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
- M49 X6 : la confirmation libère les affectations listées (tracées),
  clôture la commande, enregistre le reliquat.
- M50 X6 : motif obligatoire ; « Autre » sans commentaire refusé [CT19].
- M51 X6 : reliquat jamais converti en livraison (livré reste 70, aucune
  ligne de BL créée).
- M52 X6 : historique des quantités intact ; marchandise libérée = stock
  GMC à son emplacement.
- M53 Signal « entièrement livrée » [cahier ; PROP C10].

*Situation, stock et transformation prévue*

- M54 Situation : O, A, V, supplément, livré, reste, à approvisionner,
  reliquat [K15].
- M55 Stock A à F par emplacement (F = résultat prévu, affectable, non
  vendable) et quatre notions d'O4 [D5, O4 ; CT12].
- M56 Correction d'inventaire sans PV refusée [K17].
- M57 Correction avec PV : référence dans l'audit, aucun mouvement
  antérieur modifié [K17 ; CT14].
- M58 Garde-fou : envoi en transformation sous l'affecté refusé [N13 ;
  CT11].
- M59 Garde-fou : chute ou correction sous l'affecté refusée [N13 ;
  CT11].
- M60 X3 : déclaration du résultat prévu d'une ligne de bon de sortie
  (finition, longueur, quantité attendue) par le SUPERADMIN ; saisi,
  jamais déduit de « 2x6m » ; tracée ; figée dès qu'une affectation s'y
  rattache [CT18].
- M61 Y1 : la réservation devient automatiquement une affectation au
  moment convenu (Y1 bis (b)) : même lot, même quantité, même état
  prévu ; conversion tracée ; aucun lot choisi par le système [CT21].
- M62 Y1 : la réservation est libérée par l'annulation de la commande,
  par la clôture avec reliquat (listée) ou par le SUPERADMIN avec motif ;
  chaque libération est tracée [Y1 bis (g) ; CT21].
- M63 Y1 : résultat prévu d'un bon de sortie différent de celui de la
  réservation du même lot → refusé [Y1 bis (f) ; CT18, CT21].
- M64 Y4 : ligne GALVA vendue en PIÈCE, ML ou M² → refusée ; en TONNE
  (ou KG selon Y4 bis) → acceptée.

**Intégrité (I)**

- I01 21 migrations ; `--fresh` deux fois, empreintes identiques.
- I02 `integrity_check` = ok ; clés étrangères sans anomalie.
- I03 0021 atomique : sur anomalie préalable, rien n'est appliqué
  [CT15].
- I04 REAL refusé dans les nouvelles colonnes `*_minor`.
- I05 Second SUPERADMIN actif refusé par la base [CT1].
- I06 Avenant immuable (UPDATE, DELETE refusés) [K9 ; CT10].
- I07 Prix de vente d'une ligne de commande confirmée immuable en base
  [Y5 ; DB11].
- I08 Attribution de permission jamais supprimée, retrait tracé [CT2].
- I09 Quantité originale libre en brouillon, figée après confirmation
  [PROP C1].
- I10 Un devis → une commande, contrôlé par la base [cahier].
- I11 Client non supprimable [cahier].
- I12 Taux immuable (existant) avec auteur obligatoire [K5 ; CT5].
- I13 Plafond d'affectation par emplacement contrôlé aussi en base
  [K12 ; CT11].
- I14 Correction d'inventaire refusée par la base sans SUPERADMIN [K17 ;
  CT14].
- I15 `core.audit.ACTIONS_VALIDES` synchronisé avec le CHECK de la base
  (33 actions, 34 selon Y4 bis) [CT].
- I16 Historique du référentiel article immuable [CT3 ; Y4 bis].

**E2E (E)**

Les livraisons sont simulées par insertion directe de lignes de BL, car
la 5.9 n'est pas codée. Les bons de sortie sont créés de la même façon,
car la 5.8 n'est pas codée.

- E01 Devis → CONFIRMÉ → commande → avenant +20 → 120 INITIALE + 5
  SUPPLÉMENT → situation [O1, X9].
- E02 Avenant nouvel article (cas 2) avec le taux de l'affaire [O2, X7].
- E03 O8 cas A : ajout couvert par le stock existant [L1].
- E04 Y1 + X3 : 60 barres NOIR réservées chez GMC dès la confirmation
  du client → bon de sortie de 100 avec le même résultat prévu →
  réservation convertie en affectation ; les 40 autres affectées à une
  deuxième affaire ; aucun mouvement créé par la 5.6 ; retour bloqué
  jusqu'à la 5.8.
- E05 X6 : clôture complète 100 / 70 / 30.
- E06 Y5 : prix négocié au stade du devis → CONFIRMÉ → commande →
  avenant +20 au même prix ; toute tentative de modifier le prix est
  refusée.
- E07 Droits : création de compte → permissions → devis accepté →
  affectation refusée [O5, X4].
- E08 X9 : supplément puis avenant, supplément conservé.

**Tests X1 à X9 et Y1 à Y5 (renvois, identiques dans §18 et §20)**

| Décision | Tests |
|---|---|
| X1 (remplacé par Y5) | voir Y5 |
| X2 + Y2 | U14, U15, M11 |
| X3 | U20, M38 à M42, M60, E04 |
| X4 | P06, P07, P09 à P16, E07 |
| X5 + Y3 | U11, U12 |
| X6 | U19, M48 à M52, M62, P11, E05 |
| X7 | M08, M24, P12, E02 |
| X8 | U05, M04 |
| X9 | M36, M37, M44, E01, E08 |
| Y1 | M43, M61, M62, M63, P16, E04 |
| Y4 | U22, M04, M64 |
| Y5 | M27, M28, M29, I07, E06 |

---

## 13. Non-régression

- **NR01** — Les 293 tests existants sont conservés et doivent passer.
  - Adaptations prévues, chacune listée au codage, **sans changer une
    seule assertion** :
    - `tests/helpers.py` : l'utilisateur de test devient SUPERADMIN
      (FACT : rôle ADMINISTRATEUR aujourd'hui) ;
    - les **13 appels** de `corriger_inventaire` (3 fichiers) reçoivent
      une référence de PV (K17) ;
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
- **NR03** — Comportement 5.5 inchangé hors K17, garde-fou et retour
  bloqué d'un lot portant une affectation sur résultat prévu.

---

## 14. N1 à N15 — définitifs [V]

| N | Règle | Sources |
|---|---|---|
| N1 | Méthode de poids validée par article (kg/ml, kg/m², kg/pièce, autre validée) ; MV = base à vérifier ; comparer, ne jamais choisir silencieusement, validation SUPERADMIN, historique ; progressif, projet non bloqué. | N1, K7 |
| N2 | Tonne : poids calculé ; aucune saisie arbitraire ; méthode manquante → demande de compléter. | N2, K18 |
| N3 | GALVA : poids brut × (1 + %/100) ; trois états ; % obligatoire pour vendre en GALVA ; vente GALVA seulement en KG ou TONNE. | N3, K20, O7, X8, Y4 |
| N4 | GPP × 1,02, fixe actuellement, jamais cumulé ; jamais appliqué au poids déclaré. | N4, K19, O7 |
| N5 | Devises imposées ; taux saisi par le commercial en TND pour 1 EUR, historisé, figé à CONFIRMÉ, référence de l'affaire et de ses avenants, modifiable exceptionnellement par le SUPERADMIN ; coût EUR = TND ÷ taux ; transport : EUR/t en tonne, montant total EUR saisi sur la ligne du devis hors tonne, avec le poids de la ligne. | N5, K4, K5, K22, O2, O3, X2, X5, X7, Y2, Y3 |
| N6 | Quantité originale fixe ; avenants par le SUPERADMIN ; quantité d'avenant = normale ; supplément = au-delà de V, conservé comme supplément. | N6, K3, K15, O1, X9 |
| N7 | Diminution jamais sous le livré ; libération explicite ; marchandise = stock GMC disponible. | N7, K13 |
| N8 | Ligne identique = prix confirmé de la commande ; **aucune renégociation après confirmation**, la négociation se fait au stade du devis ; prix de vente jamais modifié par un coût d'achat ; autre commande = autre prix possible. | N8, K10, O8, Y5 (remplace X1) |
| N9 | Réservés au SUPERADMIN et audités : comptes, rôles, droits, permissions ; modifications stratégiques, corrections ; codage, versions, améliorations ; validation des évolutions importantes ; avenants ; clôture avec reliquat. | N9, K9, X4, X6 |
| N10 | Affectations et réservations de lots bruts : SUPERADMIN seul pour le moment ; accès définis par compte, module, permission ; rôle COMMERCIAL sans tous les droits automatiquement ; délégation prévue, aucune active. | N10, K8, O5, X4, Y1 |
| N11 | GMC et transformateurs ; autres emplacements au besoin ; localisation ≠ affectation ; une allocation n'est jamais un mouvement. | N11, K11, O9 |
| N12 | Bon de sortie → situation chez le transformateur → bon de réception → lot transformé ; réservation d'un lot brut dès la confirmation du client, puis affectation automatique avec la transformation (Y1) ; affectation sur résultat prévu dès la 5.6 (X3) ; lot transformé et rattachement en 5.8. | N12, K1, O4, X3, Y1 |
| N13 | Disponibilité réelle ; refus des doubles affectations, des dépassements et des mouvements sous l'affecté ; jamais de choix automatique. | N13, K12 |
| N14 | Un seul SUPERADMIN actuellement ; droits par compte et rôle/permission, non simplement par le nom affiché ; délégation future prévue. | N14, K16, O5, X4 |
| N15 | Transformation et changement d'état : nouveau lot à caractéristiques propres ; lot d'origine traçable ; vendable après réception. | N15, K2, O4 |

---

## 15. K1 à K22 — définitifs [V]

| K | Règle | Complétée par |
|---|---|---|
| K1 | Flux bon de sortie → situation calculée → bon de réception → stock GMC. | O4, X3 |
| K2 | Compatibilité directe d'un lot déjà dans l'état demandé ; chemin par transformation ; 12 m jamais directement 6 m. | O4, X3, Y1 |
| K3 | Quantité originale fixe ; avenants ; six grandeurs. | O1 |
| K4 | Prix de revient estimé ; transformation saisie par ligne ; estimation ≠ coût réel. | O7, X5, Y2, Y3 (taux en TND pour 1 EUR, division) |
| K5 | Taux saisi à la main, historisé, figé à la validation de l'offre. | O3, X7, Y6 |
| K6 | Hors tonne : poids manuel. | O7 (déclaré, final) |
| K7 | Référentiel progressif, projet non bloqué. | X8, Y4 bis |
| K8 | SUPERADMIN = Mohamed actuellement ; délégation prévue ; aucune active. | O5, X4 |
| K9 | Avenants SUPERADMIN, historisés, avec impact. | O1, X4 |
| K10 | Ligne identique = même prix. Sa partie « renégociation datée » est **remplacée par Y5** (pas de renégociation après confirmation). | Y5 |
| K11 | Emplacements ; localisation ≠ affectation. | O9 |
| K12 | Contrôles de disponibilité ; aucun choix automatique. | X3 |
| K13 | TND millimes, EUR centimes ; arrondi final ; diminution ≥ livré. | — |
| K14 | Aucun nouveau point métier à ouvrir. | Les Y (§22) sont signalés comme contradictions ou points restés ouverts, sans être tranchés. |
| K15 | Six grandeurs de situation. | O1, X9 |
| K16 | Droits par compte et rôle/permission, non simplement par le nom affiché. | X4 |
| K17 | Corrections d'inventaire : SUPERADMIN, PV signé par la Direction Générale dans l'audit. | X4 |
| K18 | Tonne : poids calculé. | — |
| K19 | GPP × 1,02, jamais cumulé. | O7 |
| K20 | % GALVA : trois états, jamais 0 automatique. | X8, Y4 |
| K21 | Avenant cas 1 / cas 2 ; ancienne commande intacte. | O1, O2, X7 |
| K22 | Devises imposées. | X5 |

---

## 16. O1 à O9 — définitifs

| O | Statut | Règle |
|---|---|---|
| O1 | VALIDÉ | Quantité d'avenant = quantité normale, identifiable ; supplément = au-delà de V. |
| O2 | VALIDÉ | Avenant = taux de la préparation du devis initial ; aucun nouveau taux. |
| O3 | VALIDÉ | Validation de l'offre = CONFIRMÉ ; taux et conditions figés ; SUPERADMIN seul ensuite. |
| O4 | VALIDÉ | Affectation commerciale possible chez le transformateur ; vendable après réception ; quatre notions. Mise en œuvre : X3. |
| O5 | VALIDÉ | Comptes et accès définis par le SUPERADMIN, par utilisateur, module, permission si nécessaire ; rôle COMMERCIAL sans tous les droits automatiquement. |
| O6 | Supprimé | Devenu CT7. |
| O7 | VALIDÉ | Hors tonne : poids déclaré obligatoire (saisi au devis, Y2), final, jamais majoré ; sert au poids final, au prix de revient estimatif et, plus tard, à la répartition du transport réel (Y2) ; clause transport EUR/T remplacée par X2/Y2 ; pas de GALVA hors poids (Y4). |
| O8 | VALIDÉ ; partie fournisseur **HORS PÉRIMÈTRE 5.6 (5.7)** | Cas A : lot existant, coût réel, aucun achat (affectation 5.6, lecture L1). Cas B : nouvelle commande fournisseur, nouvelle négociation, nouveau lot et coût ; prix initial jamais écrasé ; prix de vente non modifié. Sa phrase sur une nouvelle négociation client est remplacée par Y5. |
| O9 | VALIDÉ | GMC et transformateurs ; autres emplacements au besoin réel. |

---

## 17. C1 à C14

Statuts : **VALIDÉ** ; **VALIDÉ EN PARTIE** (le reste est une [PROP] à
valider) ; **À VALIDER**.

| C | Sujet | Statut | Validé | Reste [PROP] |
|---|---|---|---|---|
| C1 | Devis → commande | VALIDÉ EN PARTIE | Un devis → une commande (cahier) | Seulement depuis un devis CONFIRMÉ ; une seule même si annulée ; lignes d'origine issues du devis (sauf avenant) ; sous-ensemble ; quantité libre en brouillon puis figée |
| C2 | Unités de vente | VALIDÉ EN PARTIE | Pièces + unité ; TONNE, PIÈCE, ML, M², autres autorisées (K6, O7) ; KG pour la galvanisation (Y4) | Liste initiale TONNE, KG (selon Y4 bis), PIÈCE, ML, M², extensible par le SUPERADMIN ; ML = pièces × longueur ; M² saisi ; prix dans l'unité de vente |
| C3 | Transport | VALIDÉ EN PARTIE | Obligatoire, 0 saisi (BR §19) ; EUR ; EUR/T en tonne, montant total saisi sur la ligne du devis hors tonne, avec le poids (X2, Y2) ; transport final réparti au poids en 5.10 (Y2) | [CT] recalcul sur V (cas 1) ; [PROP] pas de transport estimé sur un supplément |
| C4 | Annulations | VALIDÉ EN PARTIE | Devis : SUPERADMIN, 8 causes ; commande confirmée : SUPERADMIN, refusée si livrée | Même liste pour la commande ; « Autre » + commentaire ; brouillon annulé par son auteur ; devis confirmé non annulable |
| C5 | Validité du devis | VALIDÉ EN PARTIE | Cycle EN_COURS → CONFIRMÉ / EXPIRÉ / ANNULÉ | Jusqu'à la fin de la date incluse ; prolongation avant expiration ; devis expiré figé |
| C6 | Réservations | VALIDÉ EN PARTIE | Manuelles, optionnelles, informatives | Plafond au disponible de l'emplacement ; annulation, pas de suppression |
| C7 | Suppléments | VALIDÉ EN PARTIE | Au-delà de V (O1) ; motif (cahier) ; SUPERADMIN (N10) ; jamais requalifié (X9) | Possible à tout moment tant que la commande est confirmée |
| C8 | Réaffectation | VALIDÉ EN PARTIE | Tracée, motif, reste conservé ; reste du même type (X9) | SUPERADMIN ; typage à la destination selon son V (un supplément déplacé peut y devenir INITIALE ?) ; même lot, même emplacement ; non livré seulement |
| C9 | Libération | VALIDÉ EN PARTIE | Explicite (N7) ; à la clôture (X6) | Libération pour erreur : SUPERADMIN, motif |
| C10 | Clôture | VALIDÉ EN PARTIE | Signalement « entièrement livrée », SOLDÉE manuelle (cahier) ; clôture avec reliquat X6 | Définition du signal : livré ≥ V et aucune affectation active non livrée |
| C11 | Situation | VALIDÉ EN PARTIE | Catégories (K15, O1, O4, D5) | Formules [CT] §6.8 |
| C12 | Fiche client | VALIDÉ EN PARTIE | Clients : SUPERADMIN, audit, jamais supprimés | La fiche actuelle suffit ; destination et incoterm repris sur le devis |
| C13 | LAC | VALIDÉ | LAC = NOIR | — |
| C14 | Date de confirmation | À VALIDER | — | Date de confirmation par le client ; validation interne tracée à part |

---

## 18. X1 à X9 — décisions intégrées [V]

| X | Décision | Où c'est intégré | Tests |
|---|---|---|---|
| X1 | **REMPLACÉ par Y5** (30/09, 23 h 06) : « pas de renégociation de prix de vente ; commande confirmée, prix de vente confirmé ; la renégociation sera avant validation si elle existe ». | §6.7, DB11 | voir Y5 : M27, M28, M29, I07, E06 |
| X2 | Transport saisi en EUR/T ; tonne : EUR/T × t ; autre unité : aucun poids implicite, montant total EUR saisi manuellement ; aucune conversion cachée. **Précisé par Y2** : saisie sur la ligne du devis, avec le poids de la ligne ; transport final réparti au poids en 5.10. | §6.7, §7.2, DB6 | U14, U15, M11 |
| X3 | A : affectation en 5.6 sur besoin et marchandise identifiés, même chez le transformateur ; aucun lot transformé en 5.6 ; rattachement au lot résultant en 5.8 ; jamais un mouvement. Option A de la v5 reprise telle quelle. **Complété par Y1** (réservation d'un lot brut dès la confirmation du client). | §6.3 bis, §6.11, DB12, DB17, CT18, CT21 | U20, M38 à M42, M60, E04 |
| X4 | Opérations stratégiques de la 5.6 réservées au SUPERADMIN ; délégation future prévue, aucune supplémentaire active ; droits liés au compte et aux permissions, pas au nom. | §6.19, DB1, DB2 | P06, P07, P09 à P16, E07 |
| X5 | « coût EUR = Y (TND) × R (taux de change) » ; taux de l'affaire, saisi par le commercial, historisé, modifiable exceptionnellement par le SUPERADMIN ; aucun nouveau taux. **Précisé par Y3** : taux saisi en TND pour 1 EUR, donc R = 1 ÷ taux (division exacte). | §6.2, `core/prix_revient.py` | U11, U12 |
| X6 | A : clôture avec reliquat en une opération contrôlée (demande, calcul, affichage, confirmation, libération, motif) ; reliquat jamais converti en livraison. | §6.17, DB8, DB13 | U19, M48 à M52, M62, P11, E05 |
| X7 | Taux saisi, historisé, figé pour l'affaire, utilisé pour les avenants ; jamais remplacé à chaque avenant ; modification exceptionnelle par le SUPERADMIN. | §6.2, DB4 ; Y6 | M08, M24, P12, E02 |
| X8 | B : % GALVA obligatoire dans la référence article ; hors tonne, poids déclaré final, pas de réapplication ; tonne inchangée. Avec **Y4**, il n'y a plus de GALVA hors poids : la partie « hors tonne » ne se présente plus. | §6.9, DB3 | U05, M04 |
| X9 | A : un supplément reste un supplément ; jamais requalifié automatiquement ni rétroactivement ; historique conservé. | §6.13, §6.14, CT17, DB18 | M36, M37, M44, E01, E08 |

Correspondance avec la v5 : tes X1 à X9 répondent aux X1 à X9 de la v5.

- Exception : ton X5 porte sur la **conversion TND/EUR**, alors que le X5
  de la v5 portait sur l'exemple O8 « 10 DT/pièce ». Celui-ci est réglé
  par ta règle « prix de vente conservé en EUR » (§4 de ton message) :
  l'exemple se lit en EUR.
- Le point P1 de la v5 (O8 fournisseur en 5.7) est réglé par ton §5.

**Réponses Y1 à Y5 (30/09, 23 h 06)** : voir §0. Y2 et Y3 sont intégrés
dans X2 et X5 ci-dessus ; Y5 remplace X1 ; Y1 complète X3 ; Y4 complète
X8.

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
| N1 | Méthode de poids validée, progressive | N1 | Po | DB3 | référentiel | M02, M05 | 5.6 (périmètre Y4) | VALIDÉ |
| N2 | Tonne = calcul | N2 | Po | DB6 | poids_vente | U10, M03 | 5.6 | VALIDÉ |
| N3 | GALVA % ; GALVA seulement au poids | N3, Y4 | Po | DB3, DB6 | poids_vente | U02, U04, U05, M64 | 5.6 | VALIDÉ |
| N4 | GPP 1,02 | N4 | Po | DB3 | poids_vente | U03, U06 | 5.6 | VALIDÉ |
| N5 | Devises, taux, transport | N5 | Dv | DB4, DB6 | devis | M06 à M11 | 5.6 | VALIDÉ |
| N6 | Quantités, avenants, supplément | N6 | Cm, Av | DB9, DB10 | commande | U16, M20, M21 | 5.6 | VALIDÉ |
| N7 | Diminution, libération explicite | N7 | Cm, Af | DB12 | commande, affectation | M25, M26 | 5.6 | VALIDÉ |
| N8 | Prix des lignes identiques ; pas de renégociation après confirmation | N8, Y5 | Cm | DB11 | commande | M27 à M30 | 5.6 | VALIDÉ |
| N9 | Opérations sensibles SUPERADMIN | N9 | Dr | DB2 | droits | P01 à P15 | 5.6 | VALIDÉ |
| N10 | Affectations et réservations SUPERADMIN ; accès par permission | N10, Y1 | Af, Dr | DB2 | droits, affectation | P09, P16 | 5.6 | VALIDÉ |
| N11 | Localisation ≠ affectation | N11 | Af | DB12 | affectation | M31, M32 | 5.6 | VALIDÉ |
| N12 | Flux de transformation ; réservation d'un lot brut | N12, Y1 | Af, St | DB12, DB17 | affectation, stock | M38, M42, M43, M60, M61 | 5.6 / 5.8 | VALIDÉ |
| N13 | Garde-fou | N13 | St, Af | DB12, DB15 | stock | M58, M59, I13 | 5.6 | VALIDÉ |
| N14 | Un SUPERADMIN, par compte | N14 | Dr | DB1 | droits | P07, P08, I05 | 5.6 | VALIDÉ |
| N15 | Nouveau lot après transformation | N15 | St | — | (5.8) | M38 | 5.8 | VALIDÉ |
| K1 | Bon de sortie → réception | K1 | St | DB17 | stock | M42, M55 | 5.6 / 5.8 | VALIDÉ |
| K2 | Compatibilité directe | K2 | Af | DB12 | affectation | M43 | 5.6 | VALIDÉ |
| K3 | Grandeurs de quantité | K3 | Cm | DB9, DB10 | commande | U16 | 5.6 | VALIDÉ |
| K4 | Prix de revient estimé | K4 | Dv | DB6 | prix_revient | U11, U12, U21 | 5.6 | VALIDÉ |
| K5 | Taux saisi, figé | K5 | Dv | DB4 | devis | M06, M07, M08 | 5.6 | VALIDÉ |
| K6 | Poids manuel hors tonne | K6 | Po | DB6 | poids_vente | U08 | 5.6 | VALIDÉ |
| K7 | Référentiel progressif | K7 | Po | DB3 | référentiel | M05, I16 | 5.6 (périmètre Y4) | VALIDÉ |
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
| C2 | Unités de vente | C2, Y4 | Dv | DB6 | devis | M64, U22 | 5.6 | À VALIDER |
| C3 | Transport | C3, X2 | Dv | DB6 | devis | M11 | 5.6 | À VALIDER |
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
| X2 | Transport EUR/T ; hors tonne montant total | X2, Y2 | Dv | DB6 | devis, prix_revient | U14, U15, M11 | 5.6 | VALIDÉ |
| X3 | Affectation chez le transformateur (option A v5) | X3, Y1 | Af | DB12, DB17 | affectation, stock | U20, M38 à M42, M60, E04 | 5.6 + rattachement 5.8 | VALIDÉ |
| X4 | Opérations réservées SUPERADMIN | X4 | Dr | DB1, DB2 | droits | P06, P07, P09 à P16, E07 | 5.6 | VALIDÉ |
| X5 | Coût EUR = Y × R, avec R = 1 ÷ taux (TND pour 1 EUR) | X5, Y3 | Dv | DB4 | prix_revient | U11, U12 | 5.6 | VALIDÉ |
| X6 | Clôture avec reliquat | X6 | Cm | DB8, DB13 | commande | U19, M48 à M52, M62, P11, E05 | 5.6 | VALIDÉ |
| X7 | Taux figé pour l'affaire | X7 | Dv, Av | DB4 | devis, commande | M08, M24, P12, E02 | 5.6 | VALIDÉ |
| X8 | % GALVA obligatoire ; pas de réapplication | X8, Y4 | Po | DB3 | poids_vente | U05, M04 | 5.6 | VALIDÉ |
| X9 | Supplément conservé | X9 | Af | DB12, DB18 | affectation | M36, M37, M44, E01, E08 | 5.6 | VALIDÉ |
| Y1 | Lot brut réservé dès la confirmation client, affecté automatiquement avec la transformation | Y1 | Af | DB12 | affectation | M43, M61, M62, M63, P16, E04 | 5.6 (+ 5.8) | VALIDÉ |
| Y1 bis | Précisions : bloquante ? moment ? confirmation = commande CONFIRMÉE ? SUPERADMIN ? | §22 | Af | DB12 | affectation | M43, M61 | 5.6 | À VALIDER |
| Y2 | Transport hors tonne et poids saisis sur la ligne du devis ; transport final réparti au poids | Y2 | Dv | DB6 | devis | U15, M11 | 5.6 (répartition 5.9/5.10) | VALIDÉ |
| Y3 | Taux saisi en TND pour 1 EUR ; coût EUR = TND ÷ taux | Y3 | Dv | DB4 | prix_revient | U11, U12 | 5.6 | VALIDÉ |
| Y4 | GALVA seulement pour une vente en KG ou TONNE | Y4 | Po | DB6 | poids_vente, devis | U22, M04, M64 | 5.6 (+ 5.8) | VALIDÉ |
| Y4 bis | Unité de la ligne ou de l'article ? KG = vente au poids ? Référentiel minimal en 5.6 ? | §22 | Po | DB3, DB6 | référentiel, unité | R10, M02, I16, U22 | 5.6 ? | À VALIDER |
| Y5 | Pas de renégociation après confirmation ; négociation au stade du devis | Y5 | Dv, Cm | DB11 | devis, commande | M27, M28, M29, I07, E06 | 5.6 | VALIDÉ |
| Y5 bis | Correction d'une erreur de saisie du prix après confirmation ? | §22 | Cm | DB11 | commande | M27 | 5.6 | À VALIDER |
| Y6 | Effet d'une modification exceptionnelle du taux | §22 | Dv | DB4, DB6 | devis | P12 | 5.6 | À VALIDER |
| L1 | Cas A d'O8 = affectation 5.6 | §6.10 | Af | — | affectation | M46, E03 | 5.6 | À VALIDER |

---

## 21. CT1 à CT21 — aucun validé

| CT | Sujet | Résolu ? | Décision associée | Reste à valider |
|---|---|---|---|---|
| CT1 | Un seul SUPERADMIN actif, contrôlé par la base | Non | N14, X4 (métier) | Le contrôle en base ; transmission = désactiver l'un, activer l'autre |
| CT2 | Permissions : catalogue, attributions, rôle sans permission automatique, marque « réservé » | Métier réglé (O5, X4) | O5, X4 | Le mécanisme : catalogue, marquage en donnée, contrôles appliqués aux modules 5.6, « un rôle ne donne aucune permission » |
| CT3 | Référentiel : historique immuable des paramètres, sources présentées | Non | N1, K7, X8 | Mécanisme ; dépend de Y4 bis (iii) |
| CT4 | GPP 1,02 = paramètre historisé | Non | N4, K19 | Paramètre plutôt que constante |
| CT5 | Taux : ligne immuable avec auteur ; nouveau taux avant CONFIRMÉ ; commande sans taux propre | En partie | O2, X7, Y3 (sens : TND pour 1 EUR) | Changement avant CONFIRMÉ = nouvelle ligne ; modification exceptionnelle : Y6 |
| CT6 | Prix de revient : calcul exact au total de la ligne, un seul arrondi | En partie | O3 (conditions historisées) | Proposé : calculé pendant EN_COURS, **instantané enregistré à CONFIRMÉ** (au lieu de « jamais stocké » en v5) ; effet de Y6 |
| CT7 | Indicateur « transformation prévue » sur la ligne de devis ; jamais de 0 implicite | Non | K4 | Tel quel |
| CT8 | Unité du coût de transformation obligatoire | Non | K4, BR §15 | Liste d'unités |
| CT9 | Coûts estimés copiés du devis ; saisis pour un avenant ; jamais pré-remplis depuis un achat | Non | O8, K21 | Tel quel |
| CT10 | Table d'avenants unique, immuable ; aussi pour une intervention sur devis CONFIRMÉ | Non | K9, O3 | Tel quel. Plus d'avenant de prix : X1 est remplacé par Y5 |
| CT11 | Garde-fou N13 sur tous les mouvements | Non | N13, K12 | Partie livraison préparée pour la 5.9 |
| CT12 | Situation E calculée en 5.6 | Non | K1, D5 | Tel quel |
| CT13 | Signal « utilisable après transformation » (lecture seule) pour un lot brut **non réservé** | Non | K2, Y1 | Tel quel |
| CT14 | PV : référence et date obligatoires dans l'audit ; SUPERADMIN exigé par le service et la base | Non | K17 | Tel quel ; adaptation des 13 appels de test |
| CT15 | 0021 atomique, additive, valeurs par défaut | Non | — | Tel quel |
| CT16 | Ligne d'avenant : origine AVENANT, O = 0 | Non | O1, K21 | Tel quel |
| CT17 | INITIALE jusqu'à V, sinon SUPPLÉMENT ; jamais requalifié | Métier réglé (X9) | O1, X9 | Le mécanisme |
| CT18 | Affectation sur résultat prévu, selon l'option A de la v5 | Métier réglé (X3 = A) | O4, X3, D1 | Le mécanisme : résultat prévu saisi sur la ligne du bon de sortie (DB17), déclaré par une fonction SUPERADMIN tant que la 5.8 ne crée pas les bons, identique à celui d'une réservation du lot (Y1), figé dès qu'une affectation s'y rattache ; quantité en pièces attendues ; retour refusé jusqu'à la 5.8 ; livraison interdite en 5.9. |
| CT19 | Clôture : statut SOLDÉE + reliquat enregistré par ligne + motif (exemples + « Autre » avec commentaire) | Métier réglé (X6 = A) | C10, X6 | La représentation (SOLDÉE ou statut propre) |
| CT20 | Poids : origine DÉCLARÉ/CALCULÉ, unité, méthode et % utilisés | Obligation validée (O7, Y2) | O7, X8, Y2 | L'enregistrement |
| CT21 *(nouveau, Y1)* | Réservation d'un lot brut : ligne d'`affectation_stock` de nature « réservation », avec lot, quantité, état prévu et quantité attendue ; déduite du disponible ; convertie automatiquement en affectation (même ligne ou ligne liée, conversion tracée) ; libérée par annulation, clôture ou SUPERADMIN | Métier réglé dans son principe (Y1) | Y1, N10, X3, X6 | Le mécanisme, et les précisions Y1 bis |

Aucun CT n'est supprimé. Aucun n'est considéré comme validé. CT21 est ajouté pour Y1.

---

## 22. Contradictions résiduelles et précisions à confirmer

Tes réponses du 30/09 (23 h 06) règlent :

- **Y2 et Y3** entièrement ;
- **Y1, Y4 et Y5** dans leur principe. Chacun laisse une ou plusieurs
  précisions : Y1 bis, Y4 bis, Y5 bis.

**Y6** et **L1** n'ont pas reçu de réponse. Comme toujours, je ne tranche
rien ; pour chaque point, ma proposition figure en premier.

**Y1 bis — Réservation d'un lot brut : quatre précisions**

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

**Y4 bis — Galvanisation en KG ou TONNE : trois précisions**

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

**Y5 bis — Erreur de saisie du prix après confirmation**

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

**Y6 — Effet d'une modification exceptionnelle du taux (toujours ouvert)**

- **FACT.** X7 : le taux est « figé pour l'affaire ; utilisé pour les
  avenants et calculs futurs … Seul le SUPERADMIN peut effectuer une
  modification exceptionnelle ». La v5 demandait l'effet de cette
  modification sur les avenants suivants, avec l'autre possibilité : « les
  avenants gardent toujours le taux d'origine, même après une
  intervention ».
- **PROPOSITION.** Deux options :
  - (a) le taux modifié, historisé avec motif et date, devient la
    référence de l'affaire pour les calculs et avenants **postérieurs** ;
    l'instantané de l'offre CONFIRMÉE (CT6) garde l'ancien taux ;
  - (b) les avenants gardent toujours le taux d'origine ; la
    modification exceptionnelle ne sert qu'à corriger l'offre elle-même.
- **IMPACT.** CT5, CT6, test P12.
- **POINT À VALIDER.** Mohamed, après une modification exceptionnelle du
  taux, les avenants suivants utilisent-ils (a) le nouveau taux, ou (b)
  toujours le taux d'origine ?

**L1 — Cas A d'O8 (toujours ouvert)**

- **FACT.** Ton §5 de la v6 range « si article disponible dans le stock
  GMC : utiliser le stock existant et son lot » dans la partie
  fournisseur d'O8, en 5.7.
- **PROPOSITION.** L'**affectation** d'un lot existant, utilisée dans ce
  cas, est celle de la 5.6, déjà dans le périmètre. Le choix « stock
  disponible → lot existant / indisponible → achat » et tout le côté
  fournisseur restent en 5.7.
- **IMPACT.** M46, E03.
- **POINT À VALIDER.** Mohamed, confirmes-tu cette lecture ?

**Vérifications faites sur tes nouvelles réponses. Aucune autre
contradiction n'a été trouvée.**

- Y5 et X1, K10, O8 : Y5 **remplace** X1, la partie « renégociation
  datée » de K10 et la phrase d'O8 sur une nouvelle négociation client.
  Ces remplacements sont signalés partout (§6.7, §14 à §18, §20). Ce qui
  reste valide : une nouvelle ligne identique reprend le prix confirmé
  (K10), et le prix de vente n'est jamais modifié par un coût d'achat
  (O8).
- Y4 et X8 : cohérents. Le % GALVA reste obligatoire ; le cas « GALVA hors
  tonne » de X8 ne se présente plus.
- Y4 et O7 : cohérents. Le GPP hors poids reste possible, avec le poids
  déclaré tel quel.
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

**Pour pouvoir coder la 5.6** (ma proposition entre parenthèses) :

1. **Y1 bis** :
   - réservation bloquante (oui) ;
   - moment de l'affectation automatique (au bon de sortie) ;
   - « confirmation client » = commande CONFIRMÉE (oui) ;
   - réservation par le SUPERADMIN seul (oui).
2. **Y4 bis** :
   - règle GALVA contrôlée sur l'unité de la ligne (oui) ;
   - KG traité comme la tonne (oui) ;
   - référentiel article minimal en 5.6 (oui).
3. **Y5 bis** : erreur de prix après confirmation → (a) annulation et
   nouveau devis, ou (b) correction SUPERADMIN avec motif. Je ne propose
   pas d'option : c'est une décision de gestion.
4. **Y6** : après une modification exceptionnelle du taux (nouveau taux
   pour les avenants suivants).
5. **L1** : cas A d'O8 = affectation 5.6 (oui).
6. **[PROP] des C** : restes de C1 à C12 et C14 (§17), dont la question
   C8 « un supplément déplacé peut-il devenir INITIALE à la
   destination ? ».
7. **CT1 à CT21** : validation des choix techniques (§21).
8. **Validation explicite de l'analyse.**

**Si tu acceptes mes propositions en bloc** (points 1, 2, 4, 5, 6, 7) et
réponds au point 3, l'analyse est prête pour ta validation finale.

---

## 24. Contrôles finaux

| Contrôle | Résultat |
|---|---|
| X1 à X9 et Y1 à Y5 intégrés partout où nécessaire | Oui : §0, §6, §11, §12, §14 à §21 ; renvois de tests identiques dans §12, §18 et §20 |
| Aucune ancienne règle contradictoire conservée | Dans cette analyse : oui. Remplacés : X1 et la renégociation de K10/O8 → Y5 ; « supplément au-delà de l'originale » (N6 v3) → au-delà de V ; « Mohamed désigne le taux » → saisie par le commercial en TND pour 1 EUR ; transport hors tonne « EUR/T × poids déclaré » (clause d'O7) → montant total saisi sur la ligne du devis (X2, Y2) ; GALVA hors tonne (X8) → sans objet (Y4) ; « CT6 jamais stocké » → instantané à CONFIRMÉ (proposé). **Attention** : `docs/BUSINESS_RULES.md`, gelé, contient encore des textes à reporter après validation (§25) : §21 N6 (« au-delà de la quantité originale ») ; §20 introduction (« Points encore ouverts : O1 à O9 ») ; §20 note sous D5 (« point O4, non tranché ») ; §22 K3 (« non tranchée, point O1 ») ; §22 K5 (« points O5 et O3 ») ; §22 K10 (renégociation datée, remplacée par Y5). Aucune de O1 à O9, X1 à X9 ni Y1 à Y5 n'y figure. |
| X3/Y1 ne créent aucun lot transformé en 5.6 | Oui : §6.3 bis, §6.11, M38, M61 |
| X3/Y1 ne créent aucun mouvement physique | Oui : une réservation et une affectation ne sont jamais des mouvements (M38, M43, S05) |
| X6 ne transforme pas un reliquat en livraison | Oui : §6.17, M51 |
| X9 ne requalifie jamais un supplément | Oui : §6.13, §6.14, M36, M37, M44 |
| Formule X5 selon la convention validée | Oui : « coût EUR = Y (TND) × R » avec R = 1 ÷ taux saisi en TND pour 1 EUR (Y3) ; 726,47 et 4 499,41 inchangés |
| X2 sans conversion cachée en tonnes | Oui : §6.7, §6.9, U15 ; saisie sur la ligne du devis (Y2) |
| X8 conserve l'obligation du % GALVA | Oui : §6.9, M04 ; GALVA seulement au poids (Y4) |
| O8 fournisseur en 5.7 | Oui : §3, §7.2, §16 ; cas A : L1 |
| Pas de débordement sur 5.7 à 5.10 | Oui : §7.2 (préparé, rien créé). La répartition du transport réel (Y2) est en 5.10 ; le respect de la réservation à l'envoi (Y1) est en 5.8. |
| Base inchangée | Oui : empreinte `89e3225d…ab718e4`, 20 migrations, fichier daté du 30/09 09:55 |
| Code inchangé | Oui : aucun fichier de `core/`, `db/`, `repositories/`, `services/`, `tests/`, `migrations/` modifié ; seul ce document est créé |

---

## 25. Checklist finale avant codage

- [x] Y2, Y3 : validés.
- [x] Y1, Y4, Y5 : validés dans leur principe.
- [ ] Réponses à Y1 bis, Y4 bis, Y5 bis, Y6 et L1.
- [ ] Validation (ou correction) des [PROP] restantes des C1 à C12 et C14.
- [ ] Validation (ou correction) des CT1 à CT21.
- [ ] Validation humaine explicite de l'analyse.
- [ ] Puis, avant la première ligne de code, sur ton accord (ces
      documents sont aujourd'hui gelés) :
  - reporter O1 à O9, C10, X1 à X9, Y1 à Y5 et les réponses restantes
    dans `docs/BUSINESS_RULES.md`, en corrigeant les textes listés au
    §24 ;
  - archiver les analyses v5, v6 et v7 dans `docs/` et dans le projet ;
  - mettre à jour le suivi.
- [ ] Puis seulement : créer la migration 0021, coder, tester, rapport.

---

**Verdict de préparation : NON PRÊT — POINTS À VALIDER : Y1 bis, Y4 bis,
Y5 bis, Y6, L1, puis les propositions C et CT1 à CT21.**

Le codage de la Phase 5.6 ne commencera qu'après ta validation humaine
explicite de l'analyse.
