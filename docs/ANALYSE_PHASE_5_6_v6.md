# Phase 5.6 — Analyse consolidée finale : les AFFAIRES (version 6)

**Statut : ANALYSE UNIQUEMENT — en attente de validation humaine finale.**

- Aucun code, aucune migration (la **0021 n'est pas créée**), aucune
  table, aucun service, aucun repository, aucun test existant modifié,
  base inchangée.
- Ce fichier est **nouveau**. Les documents existants (analyse v4,
  règles métier, suivi) restent tels quels.
- La v5 n'existe que comme fichier remis dans notre conversation : elle
  n'est ni dans `docs/` ni dans le projet claude.ai. Les passages de la
  v5 dont dépend cette v6 sont donc **cités ici en toutes lettres**.
- Date : 30/09/2026.
- Sources :
  - v5 ;
  - règles validées des Phases 1 à 5.5 (`docs/BUSINESS_RULES.md`, notées
    « BR § ») ;
  - D1 à D6, N1 à N15, K1 à K22, O1 à O9, C1 à C14 ;
  - tes décisions X1 à X9 (message « Consolidation finale de l'analyse
    v6 ») ;
  - l'état réel du projet et de la base, vérifié en lecture seule.
- Avant livraison, un relecteur indépendant a comparé ce document à tes
  messages et au schéma réel. Il a relevé 21 écarts, dont 5 importants ;
  tous sont corrigés ici. Les chiffres et les FACT ont été confirmés,
  sauf deux formulations rectifiées.

Légende :

- **[V]** : décision validée par toi (source citée).
- **[CT]** : choix technique proposé, **non validé**.
- **[PROP]** : proposition métier de ma part (issue des C), **non
  validée**.
- **[Y…]** : contradiction ou point laissé ouvert, présenté en FACT →
  PROPOSITION → IMPACT → POINT À VALIDER (§22). Je ne tranche aucun Y.
- **FACT** : constaté dans le schéma, le code ou les documents.

---

## Sommaire

1. Objet de la Phase 5.6
2. Périmètre inclus
3. Hors périmètre
4. État réel du projet avant la Phase 5.6
5. Architecture concernée
6. Modèle métier consolidé
   - 6.1 à 6.6 : clients, devis, réservations, commandes, lignes,
     avenants
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
21. CT1 à CT20
22. Contradictions résiduelles
23. Points nécessitant encore une validation humaine
24. Contrôles finaux
25. Checklist finale avant codage

---

## 1. Objet de la Phase 5.6

Mettre en place, dans le backend (services Python, sans API HTTP ni
interface), la gestion commerciale des **affaires** :

- clients, devis, réservations informatives ;
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
  O7, X8) : ils font partie du devis. Le coût réel et la marge restent en
  5.10.
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
  d'article : périmètre à confirmer, **Y4**.

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
| Taux | `taux_change` : colonne `taux REAL > 0`, immuable (triggers), sans auteur. Le schéma ne fixe ni valeur ni sens de lecture. Seuls les tests enregistrent `devise='EUR', taux=3.4` ; y lire « 1 EUR = 3,4 TND » est une **déduction** tirée de l'exemple K4. |
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
  - Ta convention X5 « coût EUR = Y (TND) × R » : lien avec K4 = **Y3**.
- Transport [V X2] : voir 6.7.
- Cycle EN_COURS → CONFIRMÉ / EXPIRÉ / ANNULÉ [V cahier] :
  - annulation par le SUPERADMIN (« Mohamed seul »), avec une cause
    parmi 8 [V cahier] ;
  - validité et prolongation [PROP C5].

### 6.3 Réservations informatives

- Manuelles, optionnelles, informatives ; jamais un mouvement ni une
  affectation [V cahier].
- Plafond = disponible réel à l'emplacement visé ; annulation, jamais
  suppression [PROP C6].

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
- **X1** [V] : une renégociation du prix de vente s'applique à **toutes
  les lignes identiques concernées** de la même commande.
  - C'est une modification commerciale historisée : nouveau prix, date
    d'effet, prix précédent jamais écrasé [V X1, K10].
  - Quantités déjà livrées (et donc facturées, BR §5) avant la date
    d'effet : **Y5**.
- Le prix de vente confirmé n'est jamais modifié parce qu'un coût d'achat
  change [V O8].
- Une autre commande peut avoir un autre prix [V N8].
- **Transport X2** [V] :
  - saisi dans le devis en **EUR/T** ;
  - ligne vendue en TONNE : transport EUR = EUR/T × quantité en tonnes
    (ex. 4,32 t × 85,50 = 369,36 EUR) ;
  - autre unité : **aucun poids implicite**, aucune conversion cachée en
    tonnes ; montant total de transport EUR saisi manuellement « sur la
    ligne de facturation selon l'unité concernée » → **Y2**.

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

### 6.9 Poids [V N1 à N4, K6, K7, K18 à K20, O7, X8]

- **Vente en TONNE** : poids calculé par la méthode validée de la fiche
  article ; aucune saisie manuelle arbitraire.
  - Méthode manquante → le système demande de compléter le référentiel.
  - GALVA : poids brut × (1 + % ÷ 100). GPP : poids brut × 1,02. Jamais
    cumulés.
  - Exemples : 48,6 / 51,516 / 49,572 kg ; 100 barres GALVA = 5,1516 t.
- **Hors tonne** (PIÈCE, ML, M², autre unité autorisée) :
  - poids **déclaré obligatoire** = **poids final** de la commande ;
  - aucun % GALVA ni +2 % GPP réappliqué ;
  - la quantité et l'unité de vente restent les données commerciales
    principales ;
  - pas d'intervention automatique sur le dossier à cause du seul poids.
- Usages du poids déclaré [V O7, « notamment »] :
  - le poids final de la commande ;
  - le **prix de revient estimatif** : un prix au poids se multiplie par
    le poids déclaré, par exemple 2 800,5 TND/t × 0,5 t = 1 400,25 TND ;
  - le transport « lorsque celui-ci est exprimé en EUR/T » : **remplacé
    par X2** (aucune conversion en tonnes hors tonne).
- Poids de vente figé à la confirmation [V cahier].
- **X8 = B** [V] : le % GALVA reste obligatoire dans la référence article
  pour vendre en GALVA, y compris hors tonne. Il n'est pas appliqué au
  poids déclaré. C'est l'option (b) de la v5, citée : « toute vente
  GALVA exige un % renseigné, même hors tonne, pour compléter le
  référentiel, sans l'appliquer ».
  - Les trois états (défini, 0 % = brut, non renseigné) sont conservés.
  - Un % non renseigné n'est jamais converti en 0 [V K20].
  - Le référentiel se construit progressivement (K7) ; une vente GALVA
    sur un article sans % déclenche la demande de compléter.
- Référentiel : comparer, présenter, ne jamais choisir silencieusement,
  validation SUPERADMIN, historique [V N1, K7] ; périmètre **Y4**.

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
  autre état : **Y1**.

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
  transformateur avec son résultat prévu (X3) ; avant l'envoi : Y1.
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

- Les quatre notions d'O4 sont affichées.
- Formules [CT] au §6.8.

### 6.17 Clôture avec reliquat [V C10, X6]

Opération contrôlée **unique** :

1. le SUPERADMIN demande la clôture ;
2. le système calcule et affiche le reliquat (ex. 100 commandées,
   70 livrées → 30 ; « les 30 peuvent encore être affectées à
   différentes allocations ») ;
3. le système affiche les affectations encore présentes sur ce reliquat ;
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
| Réservation | (aucun aujourd'hui) | active / annulée [PROP C6] |

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
  - affectations, suppléments compris (N10) ;
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

- Jamais d'écrasement : quantités, prix (X1), taux (X7), avenants,
  affectations, clôtures, droits.
- Audit : 12 actions aujourd'hui → **31 proposées** (32 si Y4 = a,
  avec CREATION_ARTICLE) [CT] :
  - les 12 existantes, dont REAFFECTATION, QUANTITE_SUPPLEMENTAIRE,
    MODIFICATION_PRIX, ANNULATION_DOCUMENT, CORRECTION_INVENTAIRE ;
  - 19 nouvelles : CREATION_CLIENT, MODIFICATION_CLIENT, CREATION_COMPTE,
    MODIFICATION_COMPTE, ATTRIBUTION_PERMISSION, RETRAIT_PERMISSION,
    VALIDATION_REFERENTIEL_ARTICLE, SAISIE_TAUX_DEVIS, CONFIRMATION_DEVIS,
    INTERVENTION_DEVIS_CONFIRME, PROLONGATION_DEVIS, RESERVATION,
    ANNULATION_RESERVATION, CONFIRMATION_COMMANDE, AVENANT_COMMANDE,
    AFFECTATION, LIBERATION_AFFECTATION, CLOTURE_COMMANDE,
    DECLARATION_RESULTAT_PREVU.

---

## 7. Impacts base de données

### 7.1 Créé en 5.6 (dans la future 0021) — voir §11

### 7.2 Préparé seulement (aucune colonne créée en 5.6)

| Pour | Élément | Raison |
|---|---|---|
| 5.7 | Prix négocié d'une commande fournisseur confirmée historisé, jamais écrasé ; statut « confirmée » ; historique des négociations ; `v_approvisionnement_ligne` sur V (FACT : utilise la quantité originale) | O8 fournisseur |
| 5.8 | Création des documents de transformation (dont la saisie du résultat prévu à la création du bon de sortie) ; lien affectation → lot résultant ; coupe 1 → N ; écarts reçu/prévu | X3 |
| 5.9 | Interdiction de livrer une affectation sur transformation non rattachée ; prix applicable selon la date d'effet (X1, Y5) ; transport hors tonne (Y2) | X1, X2, X3 |
| 5.10 | Coût réel, marge | — |
| Plus tard | Autres emplacements (O9) ; import de la MV | O9 |

---

## 8. Impacts services

| Service | Nouveau / modifié | Contenu |
|---|---|---|
| `droits_service` | Nouveau | Comptes (SUPERADMIN seul) ; attribution/retrait de permissions, audités ; vérification compte actif + permission ; opérations réservées. |
| `client_service` | Nouveau | Créer/modifier (SUPERADMIN), audit, jamais de suppression. |
| `referentiel_article_service` | Nouveau (selon **Y4**) | Création d'article (SUPERADMIN) ; valeurs candidates présentées sans choisir ; validation SUPERADMIN (méthode, % GALVA) avec historique. |
| `core/poids_vente.py` | Nouveau | Tonne : méthode × facteur de finition (NOIR 1 ; GALVA 1 + %/100 ; GPP 1,02) ; hors tonne : poids déclaré obligatoire, jamais majoré ; % GALVA exigé pour une vente GALVA (X8). |
| `core/prix_revient.py` | Nouveau | Conversion TND → EUR selon **Y3** ; prix au poids × poids déclaré hors tonne (O7) ; prix de revient exact, un seul arrondi ; transport selon X2. |
| `devis_service` | Nouveau | Préparation (permission) ; taux saisi et historisé ; devises imposées ; coûts ; prix de revient ; réservations ; confirmation (taux et conditions figés) ; intervention SUPERADMIN (Y6) ; expiration, prolongation ; annulation (SUPERADMIN). |
| `commande_service` | Nouveau | Création depuis le devis ; brouillon ; confirmation ; avenants cas 1/cas 2 ; renégociation X1 ; diminution (N7, K13) ; annulation ; clôture avec reliquat X6. |
| `affectation_service` | Nouveau | SUPERADMIN ; lot choisi à la main ; état identique ou résultat prévu (X3) ; déclaration du résultat prévu (CT18) ; INITIALE / SUPPLÉMENT (O1, X9) ; réaffectation avec reste recréé ; libération ; plafonds par emplacement. |
| `situation_service` | Nouveau, lecture seule | §6.16. |
| `stock_service` | Modifié | `corriger_inventaire` : SUPERADMIN + PV (K17) ; quantité affectable par emplacement ; garde-fou N13 sur tous les mouvements ; retour de transformation refusé si le lot porte une affectation sur résultat prévu, jusqu'à la 5.8 (CT18). |
| `unite_valorisation_service` | Modifié (selon **Y4**) | Changement d'unité d'un article réservé au SUPERADMIN (BR §11, §16). |
| `core/audit.py` | Modifié | 31 actions (§6.20). |

---

## 9. Impacts repositories

| Repository | Nouveau / modifié |
|---|---|
| `client_repository`, `utilisateur_repository`, `permission_repository` | Nouveaux |
| `devis_repository` (devis, lignes, taux), `reservation_repository` | Nouveaux |
| `commande_repository`, `avenant_repository` (avenants, historique des prix) | Nouveaux |
| `affectation_repository` (affecté actif non livré par lot, emplacement, ligne, type ; résultat prévu) | Nouveau |
| `situation_repository` (lectures agrégées, livré par ligne et type) | Nouveau |
| `referentiel_article_repository` | Nouveau (selon Y4) |
| `stock_repository` | Modifié : affecté non livré **par emplacement** (FACT : aujourd'hui par lot et par pool seulement) |
| `article_repository` | Modifié : lecture des paramètres validés |

---

## 10. Impacts tests

- **136 nouveaux cas** proposés (§12).
- **293 tests existants conservés** (§13), avec des adaptations limitées
  et listées.
- Les tests qui dépendent d'un point encore ouvert portent son repère
  (Y1 à Y6, C, CT).

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
| DB3 | Référentiel article (selon Y4) | Paramètres validés et historisés : méthode de poids, valeur et unité, % GALVA à trois états, sources, validé par/le ; paramètre GPP 1,02 ; masse linéique actuelle lue comme « valeur MV à vérifier » | [V N1, N3, N4, K7, K20, X8] ; CT3, CT4 |
| DB4 | `taux_change` | + auteur ; + motif pour une modification exceptionnelle | [V K5, X7] ; CT5 |
| DB5 | `devis` | Destination, incoterm ; annulation (cause, commentaire) ; confirmé par/le ; prolongation ; transitions contrôlées | [V cahier, O3] ; C4, C5 |
| DB6 | `devis_ligne` | Unité et quantité de vente ; poids (valeur, unité, origine CALCULÉ/DÉCLARÉ, méthode et % utilisés) ; une devise par prix, **vente EUR imposée** ; coût de transformation (indicateur, montant, unité) ; transport (EUR/t ou montant total) ; instantané du prix de revient à CONFIRMÉ | [V K4, K22, O7, X2, X8, cahier] ; CT6, CT7, CT8, CT20 |
| DB7 | `reservation_devis` | Emplacement, auteur, annulation | [V cahier] ; C6 |
| DB8 | `commande_client` | Un devis → une commande (index unique) ; annulation ; clôture (motif, commentaire, par, le) ; `date_confirmation` facultative en brouillon si C14 l'exige | [V cahier, X6] ; C1, C14, CT19 |
| DB9 | `commande_ligne` | Lien ligne de devis ; origine DEVIS/AVENANT ; unité, poids, prix EUR imposé, transport, coûts estimés ; **aucune colonne de taux** | [V O1, O2, K21, K22, X7] ; CT9, CT16 |
| DB9b | `commande_ligne` (trigger) | Quantité originale libre en brouillon puis figée (remplace `trg_commande_ligne_qte_immuable`) | [PROP C1] |
| DB10 | `avenant` (nouvelle) | Type, cible, valeurs avant/après, motif, impact, auteur, date ; immuable | [V K9, O1] ; CT10 |
| DB11 | Historique des prix de ligne (nouvelle) | Ligne, prix EUR, date d'effet, avenant ; immuable ; X1 = une entrée par ligne identique | [V X1, K10] ; CT10 |
| DB12 | `affectation_stock` | Emplacement ; référence de la ligne de bon de sortie et état prévu pour une affectation sur transformation ; raison de clôture ; plafond par emplacement (trigger remplacé) | [V N11, X3] ; CT11, CT17, CT18 |
| DB13 | Reliquat de clôture (nouvelle) | Par ligne : V, livré normal, reliquat à la clôture ; immuable | [V X6] ; CT19 |
| DB14 | `journal_audit` | CHECK étendu à 31 actions (32 si Y4 = a) ; reconstruction, audit recopié | [V] ; CT |
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
atteindre un total. Le nombre baissera de 3 si Y4 = b (R10, M02, I16).

| Catégorie | Nombre |
|---|---|
| Unitaires (U) | 21 |
| Repository (R) | 10 |
| Services — contrat technique (S) | 6 |
| Permissions (P) | 15 |
| Métier (M) | 60 |
| Intégrité (I) | 16 |
| E2E (E) | 8 |
| **Total nouveaux** | **136** |
| Non-régression | 293 existants + 3 contrôles (§13) |

**Unitaires (U)**

- U01 IPE100 6 m NOIR = 48,6 kg [N1, N2].
- U02 GALVA 6 % = 51,516 kg [N3].
- U03 GPP = 49,572 kg [N4, K19].
- U04 GALVA 0 % défini = 48,6 kg [K20].
- U05 % GALVA non renseigné → demande de compléter, jamais 0 [K20, X8].
- U06 GPP jamais cumulé avec GALVA [K19].
- U07 100 barres GALVA = 5,1516 t [N3].
- U08 Hors tonne : poids déclaré rendu tel quel, aucune majoration même
  avec un % défini [O7, X8].
- U09 Hors tonne : poids déclaré absent → refus [O7].
- U10 Tonne : poids manuel refusé [K18].
- U11 Exemple K4 : achat 2 000 TND, transformation 300 TND, taux 3,40,
  transport 50 EUR → 726,47 EUR [K4 ; Y3].
- U12 Ligne 4,32 t : achat 2 800,5 TND/t, transformation 450 TND/t, taux
  3,40, transport 85,50 EUR/t → 4 499,41 EUR (1 041,53 EUR/t) [K4 ; CT6 ;
  Y3].
- U13 Un seul arrondi final, aucun arrondi intermédiaire [K13, BR §17].
- U14 Transport tonne : 4,32 t × 85,50 = 369,36 EUR [X2].
- U15 Transport hors tonne = montant saisi, jamais converti [X2 ; Y2].
- U16 V = O + avenants (100 + 20 = 120) [K3, O1].
- U17 Reste à livrer = V − livré normal [K15 ; CT].
- U18 À approvisionner = V − (affecté normal actif non livré + livré
  normal) [CT].
- U19 Reliquat 100 / 70 → 30 [X6].
- U20 Cohérence du résultat prévu : 100 × 12 m → au plus 200 × 6 m ;
  12 m → 5 m (pas un multiple exact) refusé [D1 ; CT18].
- U21 Hors tonne : prix au poids × poids déclaré (2 800,5 TND/t × 0,5 t
  = 1 400,25 TND) [O7].

**Repository (R)**

- R01 Client : créer, modifier, lire ; aucune suppression.
- R02 Utilisateur : créer, lire, activer/désactiver.
- R03 Permissions : attribuer, retirer (tracé), droits effectifs.
- R04 Devis : devis, lignes et taux, lecture complète.
- R05 Réservations : créer, annuler, lister les actives par emplacement.
- R06 Commande : depuis le devis, lignes avec origine.
- R07 Avenants et historique des prix : insertion, lecture
  chronologique.
- R08 Affectations : affecté actif non livré par lot, emplacement, ligne
  et type ; résultat prévu.
- R09 Situation : livré par ligne et type.
- R10 Référentiel article : historique des paramètres [Y4].

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

**Métier (M)**

*Clients et référentiel*

- M01 Client créé ou modifié par le SUPERADMIN, audité ; suppression
  refusée [cahier].
- M02 Valeurs candidates présentées, aucune choisie ; validation
  SUPERADMIN ; historique [N1, K7 ; CT3 ; Y4].
- M03 Vente en tonne sans méthode validée → demande de compléter [K18].
- M04 Vente GALVA (tonne ou hors tonne) sur un article sans % → demande
  de compléter [X8].
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
- M11 Transport obligatoire ; 0 seulement s'il est saisi [BR §19 ; Y2].
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

- M27 X1 : renégociation → toutes les lignes identiques de la commande
  reçoivent le nouveau prix avec date d'effet ; ancien prix conservé
  (quantités déjà livrées : Y5).
- M28 X1 : lignes non identiques et autres commandes non touchées.
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
- M43 Lot NOIR encore chez GMC pour une ligne GALVA → selon Y1 ; signalé
  « utilisable après transformation » [CT13 ; Y1].
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

**Intégrité (I)**

- I01 21 migrations ; `--fresh` deux fois, empreintes identiques.
- I02 `integrity_check` = ok ; clés étrangères sans anomalie.
- I03 0021 atomique : sur anomalie préalable, rien n'est appliqué
  [CT15].
- I04 REAL refusé dans les nouvelles colonnes `*_minor`.
- I05 Second SUPERADMIN actif refusé par la base [CT1].
- I06 Avenant immuable (UPDATE, DELETE refusés) [K9 ; CT10].
- I07 Historique des prix de ligne immuable [X1].
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
  (31 actions, 32 si Y4 = a) [CT].
- I16 Historique du référentiel article immuable [CT3 ; Y4].

**E2E (E)**

Les livraisons sont simulées par insertion directe de lignes de BL, car
la 5.9 n'est pas codée. Les bons de sortie sont créés de la même façon,
car la 5.8 n'est pas codée.

- E01 Devis → CONFIRMÉ → commande → avenant +20 → 120 INITIALE + 5
  SUPPLÉMENT → situation [O1, X9].
- E02 Avenant nouvel article (cas 2) avec le taux de l'affaire [O2, X7].
- E03 O8 cas A : ajout couvert par le stock existant [L1].
- E04 X3 : 100 chez le galvanisateur, résultat prévu déclaré ; 60 et 40
  affectées à deux affaires ; aucun mouvement ; retour bloqué jusqu'à la
  5.8.
- E05 X6 : clôture complète 100 / 70 / 30.
- E06 X1 : renégociation sur deux lignes identiques.
- E07 Droits : création de compte → permissions → devis accepté →
  affectation refusée [O5, X4].
- E08 X9 : supplément puis avenant, supplément conservé.

**Tests X1 à X9 (renvois, identiques dans §18 et §20)**

| X | Tests |
|---|---|
| X1 | M27, M28, M29, I07, E06 |
| X2 | U14, U15, M11 |
| X3 | U20, M38 à M42, M60, E04 |
| X4 | P06, P07, P09 à P15, E07 |
| X5 | U11, U12 (convention selon Y3) |
| X6 | U19, M48 à M52, P11, E05 |
| X7 | M08, M24, P12, E02 |
| X8 | U05, U08, M04 |
| X9 | M36, M37, M44, E01, E08 |

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
| N3 | GALVA : poids brut × (1 + %/100) ; trois états ; % obligatoire pour vendre en GALVA, y compris hors tonne, sans l'appliquer au poids déclaré. | N3, K20, O7, X8 |
| N4 | GPP × 1,02, fixe actuellement, jamais cumulé ; jamais appliqué au poids déclaré. | N4, K19, O7 |
| N5 | Devises imposées ; taux saisi par le commercial, historisé, figé à CONFIRMÉ, référence de l'affaire et de ses avenants, modifiable exceptionnellement par le SUPERADMIN ; conversion selon X5/Y3 ; transport selon X2. | N5, K4, K5, K22, O2, O3, X2, X5, X7 |
| N6 | Quantité originale fixe ; avenants par le SUPERADMIN ; quantité d'avenant = normale ; supplément = au-delà de V, conservé comme supplément. | N6, K3, K15, O1, X9 |
| N7 | Diminution jamais sous le livré ; libération explicite ; marchandise = stock GMC disponible. | N7, K13 |
| N8 | Ligne identique = prix applicable ; renégociation → toutes les lignes identiques de la commande, historisée ; prix de vente jamais modifié par un coût d'achat ; autre commande = autre prix possible. | N8, K10, O8, X1 |
| N9 | Réservés au SUPERADMIN et audités : comptes, rôles, droits, permissions ; modifications stratégiques, corrections ; codage, versions, améliorations ; validation des évolutions importantes ; avenants ; clôture avec reliquat. | N9, K9, X4, X6 |
| N10 | Affectations : SUPERADMIN seul pour le moment ; accès définis par compte, module, permission ; rôle COMMERCIAL sans tous les droits automatiquement ; délégation prévue, aucune active. | N10, K8, O5, X4 |
| N11 | GMC et transformateurs ; autres emplacements au besoin ; localisation ≠ affectation ; une allocation n'est jamais un mouvement. | N11, K11, O9 |
| N12 | Bon de sortie → situation chez le transformateur → bon de réception → lot transformé ; affectation sur résultat prévu dès la 5.6 (X3) ; lot transformé et rattachement en 5.8. | N12, K1, O4, X3 |
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
| K4 | Prix de revient estimé ; transformation saisie par ligne ; estimation ≠ coût réel. | O7, X5, Y3 |
| K5 | Taux saisi à la main, historisé, figé à la validation de l'offre. | O3, X7, Y6 |
| K6 | Hors tonne : poids manuel. | O7 (déclaré, final) |
| K7 | Référentiel progressif, projet non bloqué. | X8, Y4 |
| K8 | SUPERADMIN = Mohamed actuellement ; délégation prévue ; aucune active. | O5, X4 |
| K9 | Avenants SUPERADMIN, historisés, avec impact. | O1, X4 |
| K10 | Ligne identique = même prix ; renégociation datée, ancienne condition conservée. | X1, Y5 |
| K11 | Emplacements ; localisation ≠ affectation. | O9 |
| K12 | Contrôles de disponibilité ; aucun choix automatique. | X3 |
| K13 | TND millimes, EUR centimes ; arrondi final ; diminution ≥ livré. | — |
| K14 | Aucun nouveau point métier à ouvrir. | Les Y (§22) sont signalés comme contradictions ou points restés ouverts, sans être tranchés. |
| K15 | Six grandeurs de situation. | O1, X9 |
| K16 | Droits par compte et rôle/permission, non simplement par le nom affiché. | X4 |
| K17 | Corrections d'inventaire : SUPERADMIN, PV signé par la Direction Générale dans l'audit. | X4 |
| K18 | Tonne : poids calculé. | — |
| K19 | GPP × 1,02, jamais cumulé. | O7 |
| K20 | % GALVA : trois états, jamais 0 automatique. | X8 |
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
| O7 | VALIDÉ | Hors tonne : poids déclaré obligatoire, final, jamais majoré ; sert au poids final et au prix de revient estimatif ; clause transport remplacée par X2. |
| O8 | VALIDÉ ; partie fournisseur **HORS PÉRIMÈTRE 5.6 (5.7)** | Cas A : lot existant, coût réel, aucun achat (affectation 5.6, lecture L1). Cas B : nouvelle commande fournisseur, nouvelle négociation, nouveau lot et coût ; prix initial jamais écrasé ; prix de vente non modifié. Distinct de X1. |
| O9 | VALIDÉ | GMC et transformateurs ; autres emplacements au besoin réel. |

---

## 17. C1 à C14

Statuts : **VALIDÉ** ; **VALIDÉ EN PARTIE** (le reste est une [PROP] à
valider) ; **À VALIDER**.

| C | Sujet | Statut | Validé | Reste [PROP] |
|---|---|---|---|---|
| C1 | Devis → commande | VALIDÉ EN PARTIE | Un devis → une commande (cahier) | Seulement depuis un devis CONFIRMÉ ; une seule même si annulée ; lignes d'origine issues du devis (sauf avenant) ; sous-ensemble ; quantité libre en brouillon puis figée |
| C2 | Unités de vente | VALIDÉ EN PARTIE | Pièces + unité ; TONNE, PIÈCE, ML, M², autres autorisées (K6, O7) | Liste initiale extensible par le SUPERADMIN ; ML = pièces × longueur ; M² saisi ; prix dans l'unité de vente |
| C3 | Transport | VALIDÉ EN PARTIE | Obligatoire, 0 saisi (BR §19) ; EUR ; EUR/T en tonne, montant total sinon (X2) | [CT] recalcul sur V (cas 1) ; pas de transport estimé sur un supplément ; lieu de saisie hors tonne : Y2 |
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
| X1 | B : nouveau prix → toutes les lignes identiques concernées de la commande ; historique conservé, jamais écrasé ; modification commerciale historisée. | §6.7, DB11 ; Y5 | M27, M28, M29, I07, E06 |
| X2 | Transport saisi en EUR/T ; tonne : EUR/T × t ; autre unité : aucun poids implicite, montant total EUR saisi manuellement « sur la ligne de facturation » ; aucune conversion cachée. | §6.7, DB6 ; Y2 | U14, U15, M11 |
| X3 | A : affectation en 5.6 sur besoin et marchandise identifiés, même chez le transformateur ; aucun lot transformé en 5.6 ; rattachement au lot résultant en 5.8 ; jamais un mouvement. Option A de la v5 reprise telle quelle. | §6.11, DB12, DB17, CT18 ; Y1 | U20, M38 à M42, M60, E04 |
| X4 | Opérations stratégiques de la 5.6 réservées au SUPERADMIN ; délégation future prévue, aucune supplémentaire active ; droits liés au compte et aux permissions, pas au nom. | §6.19, DB1, DB2 | P06, P07, P09 à P15, E07 |
| X5 | « coût EUR = Y (TND) × R (taux de change) » ; taux de l'affaire, saisi par le commercial, historisé, modifiable exceptionnellement par le SUPERADMIN ; aucun nouveau taux. | §6.2, `core/prix_revient.py` ; Y3 | U11, U12 |
| X6 | A : clôture avec reliquat en une opération contrôlée (demande, calcul, affichage, confirmation, libération, motif) ; reliquat jamais converti en livraison. | §6.17, DB8, DB13 | U19, M48 à M52, P11, E05 |
| X7 | Taux saisi, historisé, figé pour l'affaire, utilisé pour les avenants ; jamais remplacé à chaque avenant ; modification exceptionnelle par le SUPERADMIN. | §6.2, DB4 ; Y6 | M08, M24, P12, E02 |
| X8 | B : % GALVA obligatoire dans la référence article ; hors tonne, poids déclaré final, pas de réapplication ; tonne inchangée. | §6.9, DB3 | U05, U08, M04 |
| X9 | A : un supplément reste un supplément ; jamais requalifié automatiquement ni rétroactivement ; historique conservé. | §6.13, §6.14, CT17, DB18 | M36, M37, M44, E01, E08 |

Correspondance avec la v5 : tes X1 à X9 répondent aux X1 à X9 de la v5.

- Exception : ton X5 porte sur la **conversion TND/EUR**, alors que le X5
  de la v5 portait sur l'exemple O8 « 10 DT/pièce ». Celui-ci est réglé
  par ta règle « prix de vente conservé en EUR » (§4 de ton message) :
  l'exemple se lit en EUR.
- Le point P1 de la v5 (O8 fournisseur en 5.7) est réglé par ton §5.

---

## 19. Règles existantes à préserver (contrôle point par point)

| Règle (ton §4) | Préservée dans |
|---|---|
| Absence de FIFO ; affectation manuelle ; aucun choix automatique du lot | §6.10, M47 |
| Localisation physique ≠ affectation ; aucune affectation n'est un mouvement | §6.10, §6.11, M31, M38, S05 |
| Disponibilité réelle calculée | §6.10, M33 |
| Compatibilités article, finition, longueur ; exceptions NOIR/LAC → GALVA/GPP et 12 m → 2 × 6 m | §6.12 (exceptions via transformation, K2), U20 ; Y1 |
| Réception de transformation obligatoire avant disponibilité commerciale du produit transformé | §6.11, §6.16 (F) |
| Vente EUR ; matière TND ; transformation TND ; transport selon X2 | §6.2, §6.7 |
| Prix, quantités et avenants historisés ; quantité originale jamais écrasée ; V calculée | §6.6, §6.8, DB9 à DB11 |
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
| N3 | GALVA % | N3 | Po | DB3 | poids_vente | U02, U04, U05 | 5.6 | VALIDÉ |
| N4 | GPP 1,02 | N4 | Po | DB3 | poids_vente | U03, U06 | 5.6 | VALIDÉ |
| N5 | Devises, taux, transport | N5 | Dv | DB4, DB6 | devis | M06 à M11 | 5.6 | VALIDÉ |
| N6 | Quantités, avenants, supplément | N6 | Cm, Av | DB9, DB10 | commande | U16, M20, M21 | 5.6 | VALIDÉ |
| N7 | Diminution, libération explicite | N7 | Cm, Af | DB12 | commande, affectation | M25, M26 | 5.6 | VALIDÉ |
| N8 | Prix des lignes identiques | N8 | Cm | DB11 | commande | M27 à M30 | 5.6 | VALIDÉ |
| N9 | Opérations sensibles SUPERADMIN | N9 | Dr | DB2 | droits | P01 à P15 | 5.6 | VALIDÉ |
| N10 | Affectations SUPERADMIN ; accès par permission | N10 | Af, Dr | DB2 | droits, affectation | P09 | 5.6 | VALIDÉ |
| N11 | Localisation ≠ affectation | N11 | Af | DB12 | affectation | M31, M32 | 5.6 | VALIDÉ |
| N12 | Flux de transformation | N12 | Af, St | DB17 | affectation, stock | M38, M42, M60 | 5.6 / 5.8 | VALIDÉ |
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
| K10 | Ligne identique, prix daté | K10 | Cm | DB11 | commande | M29 | 5.6 | VALIDÉ |
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
| O7 | Poids déclaré final ; sert au prix de revient | O7 | Po | DB6 | poids_vente, prix_revient | U08, U09, U21 | 5.6 | VALIDÉ |
| O8 | Fournisseur : nouveau lot, prix jamais écrasé ; cas A = affectation d'un lot existant | O8 | Af (cas A) ; achats | — (5.7) | affectation (cas A) ; achat (5.7) | M12, M30, M46, E03 | 5.7 (cas A : 5.6, L1) | HORS PÉRIMÈTRE (partie fournisseur) |
| O9 | Emplacements au besoin | O9 | Af | — | — | — | plus tard | VALIDÉ |
| C1 | Devis → commande | C1 | Cm | DB8, DB9b | commande | M17, M18, I09, I10 | 5.6 | À VALIDER |
| C2 | Unités de vente | C2 | Dv | DB6 | devis | — | 5.6 | À VALIDER |
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
| X1 | Renégociation → lignes identiques | X1 | Cm | DB11 | commande | M27, M28, M29, I07, E06 | 5.6 (facturation 5.9) | VALIDÉ |
| X2 | Transport EUR/T ; hors tonne montant total | X2 | Dv | DB6 | devis, prix_revient | U14, U15, M11 | 5.6 | VALIDÉ |
| X3 | Affectation chez le transformateur (option A v5) | X3 | Af | DB12, DB17 | affectation, stock | U20, M38 à M42, M60, E04 | 5.6 + rattachement 5.8 | VALIDÉ |
| X4 | Opérations réservées SUPERADMIN | X4 | Dr | DB1, DB2 | droits | P06, P07, P09 à P15, E07 | 5.6 | VALIDÉ |
| X5 | Coût EUR = Y × R | X5 | Dv | DB4 | prix_revient | U11, U12 | 5.6 | VALIDÉ |
| X6 | Clôture avec reliquat | X6 | Cm | DB8, DB13 | commande | U19, M48 à M52, P11, E05 | 5.6 | VALIDÉ |
| X7 | Taux figé pour l'affaire | X7 | Dv, Av | DB4 | devis, commande | M08, M24, P12, E02 | 5.6 | VALIDÉ |
| X8 | % GALVA obligatoire ; pas de réapplication | X8 | Po | DB3 | poids_vente | U05, U08, M04 | 5.6 | VALIDÉ |
| X9 | Supplément conservé | X9 | Af | DB12, DB18 | affectation | M36, M37, M44, E01, E08 | 5.6 | VALIDÉ |
| Y1 | Lot brut chez GMC pour un autre état | §22 | Af | DB12 | affectation | M43 | 5.6 | À VALIDER |
| Y2 | Lieu de saisie du transport hors tonne | §22 | Dv | DB6 | devis | U15, M11 | 5.6 / 5.9 | À VALIDER |
| Y3 | Convention de conversion X5 / K4 | §22 | Dv | DB4 | prix_revient | U11, U12 | 5.6 | À VALIDER |
| Y4 | Référentiel article dans la 5.6 ? | §22 | Po | DB3 | référentiel, unité | R10, M02, I16 | 5.6 ? | À VALIDER |
| Y5 | X1 et quantités déjà livrées | §22 | Cm | DB11 | commande | M27 | 5.9 | À VALIDER |
| Y6 | Effet d'une modification exceptionnelle du taux | §22 | Dv | DB4, DB6 | devis | P12 | 5.6 | À VALIDER |
| L1 | Cas A d'O8 = affectation 5.6 | §6.10 | Af | — | affectation | M46, E03 | 5.6 | À VALIDER |

---

## 21. CT1 à CT20 — aucun validé

| CT | Sujet | Résolu ? | Décision associée | Reste à valider |
|---|---|---|---|---|
| CT1 | Un seul SUPERADMIN actif, contrôlé par la base | Non | N14, X4 (métier) | Le contrôle en base ; transmission = désactiver l'un, activer l'autre |
| CT2 | Permissions : catalogue, attributions, rôle sans permission automatique, marque « réservé » | Métier réglé (O5, X4) | O5, X4 | Le mécanisme : catalogue, marquage en donnée, contrôles appliqués aux modules 5.6, « un rôle ne donne aucune permission » |
| CT3 | Référentiel : historique immuable des paramètres, sources présentées | Non | N1, K7, X8 | Mécanisme ; dépend de Y4 |
| CT4 | GPP 1,02 = paramètre historisé | Non | N4, K19 | Paramètre plutôt que constante |
| CT5 | Taux : ligne immuable avec auteur ; nouveau taux avant CONFIRMÉ ; commande sans taux propre | En partie | O2, X7 | Changement avant CONFIRMÉ = nouvelle ligne ; modification exceptionnelle : Y6 ; convention : Y3 |
| CT6 | Prix de revient : calcul exact au total de la ligne, un seul arrondi | En partie | O3 (conditions historisées) | Proposé : calculé pendant EN_COURS, **instantané enregistré à CONFIRMÉ** (au lieu de « jamais stocké » en v5) ; effet de Y6 |
| CT7 | Indicateur « transformation prévue » sur la ligne de devis ; jamais de 0 implicite | Non | K4 | Tel quel |
| CT8 | Unité du coût de transformation obligatoire | Non | K4, BR §15 | Liste d'unités |
| CT9 | Coûts estimés copiés du devis ; saisis pour un avenant ; jamais pré-remplis depuis un achat | Non | O8, K21 | Tel quel |
| CT10 | Table d'avenants unique, immuable ; aussi pour une intervention sur devis CONFIRMÉ | Non | K9, O3, X1 | Tel quel, avec la renégociation X1 = avenant de prix |
| CT11 | Garde-fou N13 sur tous les mouvements | Non | N13, K12 | Partie livraison préparée pour la 5.9 |
| CT12 | Situation E calculée en 5.6 | Non | K1, D5 | Tel quel |
| CT13 | Signal « utilisable après transformation » (lecture seule) | Non | K2 | Dépend de Y1 |
| CT14 | PV : référence et date obligatoires dans l'audit ; SUPERADMIN exigé par le service et la base | Non | K17 | Tel quel ; adaptation des 13 appels de test |
| CT15 | 0021 atomique, additive, valeurs par défaut | Non | — | Tel quel |
| CT16 | Ligne d'avenant : origine AVENANT, O = 0 | Non | O1, K21 | Tel quel |
| CT17 | INITIALE jusqu'à V, sinon SUPPLÉMENT ; jamais requalifié | Métier réglé (X9) | O1, X9 | Le mécanisme |
| CT18 | Affectation sur résultat prévu, selon l'option A de la v5 | Métier réglé (X3 = A) | O4, X3, D1 | Le mécanisme : résultat prévu saisi sur la ligne du bon de sortie (DB17), déclaré par une fonction SUPERADMIN tant que la 5.8 ne crée pas les bons, figé dès qu'une affectation s'y rattache ; quantité en pièces attendues ; retour refusé jusqu'à la 5.8 ; livraison interdite en 5.9. Dépend aussi de Y1. |
| CT19 | Clôture : statut SOLDÉE + reliquat enregistré par ligne + motif (exemples + « Autre » avec commentaire) | Métier réglé (X6 = A) | C10, X6 | La représentation (SOLDÉE ou statut propre) |
| CT20 | Poids : origine DÉCLARÉ/CALCULÉ, unité, méthode et % utilisés | Obligation validée (O7) | O7, X8 | L'enregistrement |

Aucun CT n'est supprimé. Aucun n'est considéré comme validé.

---

## 22. Contradictions résiduelles

J'ai cherché les contradictions entre la v5, N, K, O, C, X,
l'architecture et le schéma réel. **Six points restent** : quatre
contradictions (Y2, Y3, Y4, Y5) et deux questions restées sans réponse
(Y1, Y6). Je ne les tranche pas.

**Y1 — Lot brut encore chez GMC, pour une ligne d'un autre état**

C'est une sous-question de la v5 restée sans réponse (X3 v5 : « lecture
« pas avant le bon de sortie » »).

- **FACT.**
  - O4 : « Dès que la marchandise est envoyée vers le transformateur par
    Bon de Sortie GMC, la transformation à effectuer est déjà
    identifiée … Elle peut être affectée COMMERCIALEMENT … car son
    emplacement physique est connu ; la transformation prévue est
    connue ; la quantité envoyée est connue ».
  - X3 : l'affectation peut être créée « sur le besoin client identifié ;
    sur la marchandise identifiée ; **même lorsque** cette marchandise a
    déjà été envoyée au transformateur ». « Même lorsque » peut se lire
    « y compris avant l'envoi ».
  - K2 : NOIR 12 m n'est pas directement compatible avec GALVA 6 m.
- **PROPOSITION.** Deux options :
  - (a) une ligne d'un autre état ne reçoit un lot brut qu'**après son
    bon de sortie**, avec son résultat prévu déclaré. Avant, le lot est
    seulement signalé « utilisable après transformation » (CT13) ;
  - (b) un lot brut encore chez GMC peut déjà être affecté, comme
    « affectation sur transformation à venir ». Le SUPERADMIN déclare la
    transformation prévue au moment d'affecter, et l'envoi devra la
    respecter (5.8).
- **IMPACT.**
  - (b) réserve du stock brut pour une transformation pas encore
    commandée.
  - (b) exige, en 5.8, d'empêcher d'envoyer ce lot vers une autre
    transformation ou de le vendre brut.
  - Touche CT13, CT18 et M43.
- **POINT À VALIDER.** Mohamed, un lot NOIR encore chez GMC (pas encore
  envoyé) peut-il être affecté à une ligne GALVA, GPP ou 6 m : (a) non,
  seulement après le bon de sortie, ou (b) oui, avec la transformation
  déclarée à l'affectation ?

**Y2 — Transport hors tonne « sur la ligne de facturation »**

- **FACT.**
  - X2 : hors tonne, « le montant total de transport EUR est saisi
    manuellement sur la ligne de **facturation** ».
  - La facturation client est en **5.9**, hors périmètre.
  - BR §19 et cahier §9 : le transport estimé se saisit ligne par ligne
    sur le devis, et « la saisie du transport est obligatoire pour
    valider la ligne ». Ton message d'origine : « il faut me demander le
    prix de transport de cette ligne à remplir manuellement ».
  - K4 : le prix de revient estimé du devis inclut le « TRANSPORT
    ESTIMATIF EUR ».
- **PROPOSITION.** Deux options :
  - (a) « ligne de facturation » désigne la ligne de devis ou de commande
    (la ligne qui sera facturée) : hors tonne, le montant total estimé en
    EUR est saisi sur la ligne du devis, obligatoire, 0 seulement s'il
    est saisi (BR §19 inchangé) ;
  - (b) hors tonne, pas de transport estimé au devis : le montant n'est
    saisi qu'à la facturation (5.9). Le prix de revient estimé de ces
    lignes est alors sans transport.
- **IMPACT.**
  - (b) modifie BR §19, cahier §9 et K4 pour les lignes hors tonne.
  - Touche `devis_ligne` (DB6), U15 et M11.
- **POINT À VALIDER.** Mohamed, pour une ligne vendue en pièce, ML ou M²,
  le transport estimé est-il saisi (a) sur la ligne du devis, ou (b)
  seulement sur la facture ?

**Y3 — Formule X5 « × R » et formule K4 « ÷ taux »**

- **FACT.**
  - K4 (validé) : « (PRIX ACHAT MATIÈRE TND + PRIX TRANSFORMATION TND)
    / TAUX DE CHANGE PRÉVISIONNEL + TRANSPORT ESTIMATIF EUR ». Exemple :
    « Taux de change = 3,40 TND/EUR » ; « 2 300 TND / 3,40 = 676,470588…
    EUR ».
  - X5 : « coût EUR = Y (TND) × R (taux de change) … Ne pas introduire
    un nouveau taux ou une nouvelle logique de conversion ».
  - Le schéma ne fixe pas le sens du taux. Seuls les tests enregistrent
    3,4 pour l'EUR, ce qui se lit 1 EUR = 3,4 TND (déduction tirée de
    K4).
  - Les deux formules ne coïncident que si R = 1 ÷ 3,40 = 0,294117647…
    EUR par TND. Avec R = 3,40 : 2 300 × 3,40 = 7 820, pas 676,47.
- **PROPOSITION.** Deux options :
  - (a) le commercial saisit le taux comme dans K4, en TND pour 1 EUR
    (ex. 3,40). Le R de X5 = 1 ÷ taux saisi, calculé exactement, jamais
    arrondi. Les exemples restent 726,47 EUR et 4 499,41 EUR ;
  - (b) le commercial saisit R directement, en EUR pour 1 TND (ex.
    0,2941). Avec R à 4 décimales et les mêmes entrées (U11, U12), on
    obtient 726,43 EUR (au lieu de 726,47) et 4 499,16 EUR (au lieu de
    4 499,41).
- **IMPACT.**
  - Sens du taux enregistré dans `taux_change`.
  - Écran de saisie.
  - Précision.
  - Valeurs attendues des tests U11 et U12.
- **POINT À VALIDER.** Mohamed, le taux saisi est-il (a) en TND pour
  1 EUR (3,40), le calcul faisant la division, ou (b) en EUR pour 1 TND
  (0,2941…) ? Avec (b), combien de décimales ?

**Y4 — Référentiel article (méthode de poids, % GALVA, unité) : dans la 5.6 ?**

- **FACT.**
  - Ton périmètre 5.6 (§2) ne cite pas le référentiel article.
  - Or une vente en TONNE exige une méthode de poids validée (N2, K18),
    et une vente GALVA un % renseigné et validé (X8). Les masses de la
    MV doivent être vérifiées avant de servir de référence (N1).
  - Schéma : `masse_lineique_kg_m` obligatoire, sans trace de
    validation ; `pct_galva` facultatif.
  - La création d'article est réservée à Mohamed (BR §11), et aucun
    service ne la réalise.
  - `unite_valorisation_service` (changement d'unité d'un article) ne
    contrôle pas le SUPERADMIN, alors que BR §11 et §16 en font une
    dérogation de Mohamed.
- **PROPOSITION.** Deux options :
  - (a) la 5.6 inclut le minimum :
    - création d'article par le SUPERADMIN ;
    - enregistrement et validation, avec historique, de la méthode de
      poids et du % GALVA ;
    - valeurs candidates présentées (CT3) ;
    - contrôle SUPERADMIN sur le changement d'unité.
    - Sans import de la MV.
  - (b) le référentiel est traité dans une autre phase. En 5.6, une vente
    en tonne ou en GALVA reste impossible tant qu'aucune méthode ni
    aucun % n'est validé.
- **IMPACT.**
  - DB3, `referentiel_article_service`, `unite_valorisation_service`,
    tests R10, M02 et I16.
  - Avec (b) : −3 tests, et devis en tonne non utilisables en réel.
- **POINT À VALIDER.** Mohamed, le référentiel article minimal fait-il
  partie de la 5.6 : (a) oui, ou (b) non, et dans quelle phase ?

**Y5 — X1 et quantités déjà livrées**

- **FACT.**
  - X1 : le nouveau prix « s'applique à toutes les lignes identiques
    concernées de cette même commande ».
  - K10 : nouveau prix « historisé ; date d'effet historisée ; ancienne
    condition conservée ».
  - BR §5 : « LIVRÉ = FACTURÉ ». Une quantité livrée est donc déjà
    facturée à l'ancien prix.
- **PROPOSITION.** Deux options :
  - (a) le nouveau prix vaut pour les quantités livrées à partir de sa
    date d'effet ; les quantités déjà livrées gardent l'ancien prix
    (aucune rétroactivité) ;
  - (b) le nouveau prix vaut aussi pour les quantités déjà livrées, avec
    une régularisation de facture (5.9).
- **IMPACT.** En 5.6, rien ne change : l'historique des prix avec date
  d'effet (DB11) sert aux deux options. La différence apparaît en 5.9
  (facturation). **Non bloquant pour le codage de la 5.6.**
- **POINT À VALIDER.** Mohamed, une renégociation touche-t-elle (a)
  seulement ce qui sera livré après sa date d'effet, ou (b) aussi ce qui
  est déjà livré ?

**Y6 — Effet d'une modification exceptionnelle du taux (question X7 de la v5, en partie sans réponse)**

- **FACT.** X7 : le taux est « figé pour l'affaire ; utilisé pour les
  avenants et calculs futurs … Seul le SUPERADMIN peut effectuer une
  modification exceptionnelle ». La v5 demandait l'effet de cette
  modification sur les avenants suivants, avec l'autre possibilité : « les
  avenants gardent toujours le taux d'origine, même après une
  intervention ». Ta réponse X7 ne tranche pas ce point.
- **PROPOSITION.** Deux options :
  - (a) le taux modifié, historisé avec motif et date, devient la
    référence de l'affaire pour les calculs et avenants **postérieurs** ;
    l'instantané de l'offre CONFIRMÉE (CT6) garde l'ancien taux ;
  - (b) les avenants gardent toujours le taux d'origine ; la
    modification exceptionnelle ne sert qu'à corriger l'offre elle-même.
- **IMPACT.** CT5, CT6, test P12.
- **POINT À VALIDER.** Mohamed, après une modification exceptionnelle du
  taux par le SUPERADMIN, les avenants suivants utilisent-ils (a) le
  nouveau taux, ou (b) toujours le taux d'origine ?

**Hors de ces six points, je n'ai pas trouvé d'autre contradiction.**
Voici ce que j'ai vérifié et comment chaque cas est traité.

- X1 et K10 : la renégociation est explicite, une nouvelle ligne ne
  change rien seule.
- X6 et N7 : la libération se fait dans une opération confirmée par le
  SUPERADMIN.
- X9 et O1 : le supplément est conservé ; V ne sert qu'aux nouvelles
  affectations.
- X9 et la réaffectation (BR §7, C8) : le reste d'origine garde son
  type ; le typage à la destination reste dans la [PROP] C8.
- X8 et K7/K20 : les trois états sont conservés ; seule la vente GALVA
  est bloquée sans %.
- X4 et O5/N10 : les opérations réservées ne sont pas attribuables ; les
  autres le sont ; aucune règle par le nom.
- O8 et X1 : sujets distincts ; le cas A fait l'objet de la lecture L1.
- Périmètre, K17 et N13 : ce sont des contrôles ajoutés, justifiés par X4
  et K12, sans nouvelle écriture de stock.
- Schéma réel (§4) :
  - la devise TND par défaut est traitée par DB6, DB9 et NR01 ;
  - `date_confirmation` obligatoire en brouillon est traitée par DB8 et
    C14 ;
  - la réaffectation qui clôture toute l'origine est traitée par DB18 ;
  - l'absence de lien entre bon de sortie et transformation prévue est
    traitée par DB17 ;
  - le changement d'unité d'un article est rattaché à Y4.

---

## 23. Points nécessitant encore une validation humaine

**Bloquants pour le codage de la 5.6** :

1. **Y1** — Lot brut chez GMC pour une ligne d'un autre état : (a) après
   le bon de sortie seulement, ou (b) dès l'affectation.
2. **Y2** — Transport hors tonne : (a) sur la ligne du devis, ou (b) à la
   facturation seulement.
3. **Y3** — Convention du taux : (a) TND pour 1 EUR, calcul par division,
   ou (b) R en EUR pour 1 TND (et nombre de décimales).
4. **Y4** — Référentiel article minimal et contrôle du changement
   d'unité : (a) en 5.6, ou (b) ailleurs.
5. **Y6** — Taux après une modification exceptionnelle : (a) nouveau taux
   pour la suite, ou (b) taux d'origine pour les avenants.
6. **L1** — Cas A d'O8 : confirmer que l'affectation d'un lot existant
   est celle de la 5.6.
7. **[PROP] des C** — Restes de C1 à C12 et C14 (§17), dont la
   question C8 « un supplément déplacé peut-il devenir INITIALE à la
   destination ? ».
8. **CT1 à CT20** — Validation des choix techniques (§21).
9. **Validation explicite de la v6.**

**Non bloquant pour la 5.6 (à trancher avant la 5.9)** :

10. **Y5** — X1 et quantités déjà livrées.

---

## 24. Contrôles finaux

| Contrôle | Résultat |
|---|---|
| X1 à X9 intégrés partout où nécessaire | Oui : §6, §11, §12, §14 à §21 ; renvois de tests identiques dans §12, §18 et §20 |
| Aucune ancienne règle contradictoire conservée | Dans cette analyse : oui. Remplacés : « supplément au-delà de l'originale » (N6 v3) → au-delà de V ; « Mohamed désigne le taux » → saisie par le commercial ; transport hors tonne « EUR/T × poids déclaré » (clause d'O7) → montant total (X2) ; « CT6 jamais stocké » → instantané à CONFIRMÉ (proposé). **Attention** : `docs/BUSINESS_RULES.md`, gelé à ta demande, contient encore des textes à reporter après validation (§25) : §21 N6 (« au-delà de la quantité originale ») ; §20 introduction (« Points encore ouverts : O1 à O9 ») ; §20 note sous D5 (« point O4, non tranché ») ; §22 K3 (« non tranchée, point O1 ») ; §22 K5 (« points O5 et O3 »). Aucune de O1 à O9 ni de X1 à X9 n'y figure. |
| X3 ne crée aucun lot transformé en 5.6 | Oui : §6.11, M38 |
| X3 ne crée aucun mouvement physique | Oui : §6.11, M38, S05 |
| X6 ne transforme pas un reliquat en livraison | Oui : §6.17, M51 |
| X9 ne requalifie jamais un supplément | Oui : §6.13, §6.14, M36, M37, M44 |
| Formule X5 selon la convention validée | Reproduite **mot pour mot** ; son rapport avec K4 est le point **Y3** |
| X2 sans conversion cachée en tonnes | Oui : §6.7, §6.9, U15 ; lieu de saisie : Y2 |
| X8 conserve l'obligation du % GALVA | Oui : §6.9, M04 |
| O8 fournisseur en 5.7 | Oui : §3, §7.2, §16 ; cas A : L1 |
| Pas de débordement sur 5.7 à 5.10 | Oui : §7.2 (préparé, rien créé). BL et bons de sortie sont simulés dans les tests, sans service de livraison ni de transformation. La seule donnée de transformation ajoutée (DB17) découle de ton choix X3 = A. |
| Base inchangée | Oui : empreinte `89e3225d…ab718e4`, 20 migrations, fichier daté du 30/09 09:55 |
| Code inchangé | Oui : aucun fichier de `core/`, `db/`, `repositories/`, `services/`, `tests/`, `migrations/` modifié ; seul ce document est créé |

---

## 25. Checklist finale avant codage

- [ ] Réponses à Y1, Y2, Y3, Y4, Y6 et confirmation de L1 (Y5 peut
      attendre la 5.9).
- [ ] Validation (ou correction) des [PROP] restantes des C1 à C12 et C14.
- [ ] Validation (ou correction) des CT1 à CT20.
- [ ] Validation humaine explicite de l'analyse v6.
- [ ] Puis, avant la première ligne de code, sur ton accord (ces
      documents sont aujourd'hui gelés) :
  - reporter O1 à O9, C10, X1 à X9 et les réponses Y dans
    `docs/BUSINESS_RULES.md`, en corrigeant les textes listés au §24 ;
  - archiver la v5 et la v6 dans `docs/` et dans le projet ;
  - mettre à jour le suivi.
- [ ] Puis seulement : créer la migration 0021, coder, tester, rapport.

---

**Verdict de préparation : NON PRÊT — POINTS À VALIDER : Y1, Y2, Y3, Y4,
Y6 et L1, puis les propositions C et CT1 à CT20 (Y5 avant la 5.9).**

Le codage de la Phase 5.6 ne commencera qu'après ta validation humaine
explicite de l'analyse v6.
