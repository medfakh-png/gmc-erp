# Prix de revient — coûts, régularisation fournisseur et représentation monétaire

Document créé en **Phase 4.1** (phase corrective), à la demande explicite de
l'utilisateur (§7 du cadrage). Référence unique pour tout ce qui touche au
**coût d'un lot**, à sa **régularisation** après facture fournisseur, et à la
**représentation monétaire** utilisée dans toute la base. En cas de
divergence avec `docs/BUSINESS_RULES.md` ou `docs/DATABASE.md` sur ces
sujets précis, **ce fichier fait foi** (il est le plus récent et le plus
détaillé sur ces points).

## 1. Représentation monétaire — règle définitive (Phase 4.1 §2)

**Aucun montant financier n'est stocké en `REAL`/`FLOAT`.** Tout montant
financier est un **entier** exprimé dans l'**unité monétaire minimale** de sa
devise, accompagnée d'une colonne `devise` explicite sur la même ligne.

| Devise | Unité minimale | Exemple |
|---|---|---|
| TND (dinar tunisien) | 1/1000 (le **millime**) | 5,250 TND → `5250` |
| EUR (euro) | 1/100 (le **centime**) | 5,20 EUR → `520` |
| USD (dollar) | 1/100 (le **cent**) | 5,20 USD → `520` |

Convention de nommage : toute colonne monétaire s'appelle
`<nom>_minor` (ex. `prix_unitaire_provisoire_minor`) et est **toujours**
accompagnée d'une colonne `devise TEXT CHECK (devise IN ('TND','EUR','USD'))`
sur la même table. Toute fonction Python qui renvoie ou reçoit un montant
porte le suffixe `_minor` dans son nom (`db/valorisation.py`), sans
exception — pour qu'aucun code appelant ne puisse confondre un entier
« unité minimale » avec une valeur décimale.

**Ce qui reste en `REAL`** (ce ne sont pas des montants financiers) : les
quantités physiques (poids en kg, longueur en m), les pourcentages
(`pct_galva`, `pct_transformation`, `marge_pct`), les taux de change
(`taux_change.taux`, `facture_client.cours_change_declaration` — un taux est
un ratio entre deux devises, pas un montant dans une devise), et les
quantités environnementales MACF (`macf_ligne_achat.see_reelle`,
`valeur_defaut_utilisee`, en tCO2e).

### Pourquoi des entiers, et pas juste « arrondir à 3 décimales »

Un flottant binaire (`REAL`/`float`) ne peut pas représenter exactement la
plupart des montants décimaux (0,1 + 0,2 ≠ 0,3 en binaire) : les erreurs
sont minuscules à chaque opération mais **s'accumulent** sur des milliers de
mouvements de stock, jusqu'à produire des écarts visibles. Un entier en
unité minimale n'a, par construction, aucune de ces erreurs : additionner et
soustraire des millimes est une opération exacte, toujours.

### Devise par défaut, table par table

Par défaut, `devise = 'TND'` (devise d'exploitation locale de GMC), sauf
`facture_client`/`facture_client_ligne` où le défaut est `'EUR'` (la
facturation client se fait en devise étrangère — nom d'origine
`montant_eur`, contexte douane/MACF déjà validé). Ce sont des **défauts
techniques de bascule**, pas des règles métier nouvelles : chaque ligne reste
libre de porter sa propre devise, à choisir par le futur code métier (Phase
5) au moment de la saisie réelle. Voir l'en-tête de
`migrations/0016_devise_montants_minor.sql` pour la liste exhaustive,
table par table, de toutes les colonnes converties.

### Un pool CMP est mono-devise

`cmp_stock_general`/`cmp_historique` (un pool = un triplet article/finition/
longueur) ne mélangent jamais deux devises : la première écriture qui
alimente un pool fixe sa devise, et `db/valorisation.py:reconstruire_cmp()`
**refuse** (`ValueError`) toute écriture ultérieure dans une autre devise
sur ce même pool, plutôt que de l'additionner silencieusement. Ce n'est pas
une nouvelle règle métier (GMC n'a aujourd'hui qu'une seule devise
d'exploitation pour son stock général, TND) — c'est un garde-fou technique
qui rend l'erreur impossible par construction. Testé par
`tests/test_phase41.py::test_pool_cmp_refuse_le_melange_de_devises`.

## 2. Coût d'entrée d'un lot fournisseur

- **Coût provisoire** = prix du BL fournisseur
  (`lot.prix_unitaire_provisoire_minor`), renseigné à la réception.
- **Coût final** = prix de la facture fournisseur
  (`lot.prix_unitaire_definitif_minor`), renseigné **seulement** si la
  régularisation applique le prix directement au lot (voir §3 ci-dessous).
- Les deux sont **toujours conservés**, jamais l'un n'écrase l'autre — c'est
  `regularisation_prix_fournisseur` qui trace l'écart entre les deux, et
  jamais un `UPDATE` qui efface le provisoire.

## 3. Régularisation facture fournisseur — règle définitive (Phase 4.1 §1)

À la réception de la facture fournisseur, **une seule question** décide du
traitement : *le lot est-il encore, à ce moment précis, totalement en
stock ?*

### Cas A — lot encore totalement en stock (`lot_deja_sorti = 0`)

→ `regularisation_prix_fournisseur.impact_analytique = 'APPLIQUE_AU_LOT'`.

Le coût final du lot devient le prix facturé :
`lot.prix_unitaire_definitif_minor` est mis à jour. Rien n'a encore consommé
l'ancien coût provisoire, donc rien n'est réécrit rétroactivement — c'est une
mise à jour normale d'un coût pas encore figé.

**Conséquence directe sur le CMP** : `db/valorisation.py:reconstruire_cmp()`
lit `COALESCE(prix_unitaire_definitif_minor, prix_unitaire_provisoire_minor)`
comme coût d'entrée du lot dans le pool. Dès que le prix définitif est
renseigné, une reconstruction du CMP l'utilise **immédiatement et
entièrement** à la place du prix BL — le système ne reconstruit plus jamais
le CMP à partir du prix provisoire pour ce lot.

**Exemple obligatoire du cadrage, vérifié par**
`tests/test_scenarios.py::test_5_regularisation_lot_non_sorti_appliquee_au_lot_et_cmp_recalcule` :

| Étape | Valeur |
|---|---|
| Lot reçu (BL) | 100 unités, prix provisoire 5,000 TND |
| Facture fournisseur | prix facturé 6,000 TND |
| Les 100 unités sont toujours en stock | — |
| **Coût final du lot** | **6,000 TND** |
| **CMP reconstruit** | **6,000 TND** (jamais 5,000) |

### Cas B — lot déjà sorti, totalement ou partiellement (`lot_deja_sorti = 1`)

→ `regularisation_prix_fournisseur.impact_analytique = 'ECART_SEPARE'`.

**Jamais rétroactif.** `lot.prix_unitaire_definitif_minor` n'est **PAS**
modifié : le coût réel du lot (`cout_reel_lot_minor()`) reste au prix
provisoire, donc le CMP déjà consommé par les sorties passées ne bouge pas,
et l'historique physique (`mouvement_stock`, de toute façon immuable) n'est
jamais touché. Seule la ligne `regularisation_prix_fournisseur` trace,
séparément et intégralement, l'écart pour référence/audit :

- `prix_provisoire_minor` — prix BL d'origine,
- `prix_definitif_minor` — prix facturé,
- `ecart_unitaire_minor` — écart signé (`définitif - provisoire`),
- `date_regularisation`,
- `lot_deja_sorti = 1`,
- `impact_analytique = 'ECART_SEPARE'`.

Cette règle s'applique **identiquement** que le lot soit **partiellement**
sorti (une partie encore en stock, une partie déjà livrée — cf.
`tests/test_scenarios.py::test_6bis_regularisation_lot_partiellement_sorti_ecart_separe`)
ou **totalement** sorti
(`tests/test_scenarios.py::test_6_regularisation_lot_deja_sorti_ecart_separe_non_retroactif`) :
seul « sorti ou pas » compte, pas la quantité restante. C'est une décision
métier déjà validée dès la Phase 4 (le champ `lot_deja_sorti` existe depuis
`migrations/0009_couts_regularisation.sql`) — la Phase 4.1 n'a rien changé à
la règle elle-même, seulement à l'arithmétique (entiers + devise) et ajouté
les tests qui la prouvent explicitement sur les 3 états d'un lot.

`regularisation_prix_fournisseur` est **totalement immuable** (ni UPDATE ni
DELETE, trigger dédié) — une fois tracé, un écart ne peut plus être modifié
ni supprimé.

### Ce que le futur code applicatif (Phase 5) doit faire

`db/valorisation.py` ne décide **pas** lui-même `lot_deja_sorti` /
`impact_analytique` : ce sont des valeurs que le futur service applicatif
doit déterminer au moment de la régularisation (en vérifiant s'il existe déjà
un mouvement `SORTIE_*` sur ce lot) et écrire dans
`regularisation_prix_fournisseur`, puis — uniquement dans le cas
`APPLIQUE_AU_LOT` — mettre à jour `lot.prix_unitaire_definitif_minor`. Voir
`tests/helpers.py:regulariser_facture_fournisseur()` pour une implémentation
de référence, directement réutilisable.

## 4. Chute — valorisation (voir `docs/STOCK_RULES.md` pour la règle complète)

La chute est valorisée au CMP figé au moment où la matière a quitté
`STOCK_GMC` pour la transformation (pas au moment du retour) — détaillée
dans `docs/STOCK_RULES.md` §2, qui couvre aussi son exclusion de la marge
individuelle et son inclusion dans le bilan consolidé annuel.

## 5. Fonctions de `db/valorisation.py` — référence

Toutes renvoient des entiers en unité monétaire minimale (suffixe `_minor`).
Depuis la finalisation de la Phase 5.5, « par unité » signifie **par unité
de valorisation** (DT/kg, DT/ml, DT/unité ou DT/tonne — §6) : les variantes
`*_detail()` / `cmp_actuel()` renvoient le montant AVEC son unité.

| Fonction | Renvoie | Usage |
|---|---|---|
| `reconstruire_cmp(conn)` | `dict` pool → `{quantite_totale, valeur_totale_minor, cmp_unitaire_minor, devise}` | Reconstruit intégralement le cache CMP depuis `mouvement_stock`. À appeler avant tout calcul de coût de sortie. |
| `cmp_actuel_minor(conn, article_id, finition, longueur_m)` | `int` | CMP courant du pool (par unité), lu depuis le cache. |
| `cmp_devise_actuelle(conn, ...)` | `str \| None` | Devise du pool courant. |
| `cmp_au_moment_du_mouvement(conn, mouvement_stock_id)` | `int \| None` | CMP (par unité) figé au moment d'un mouvement précis. |
| `montant_mouvement_minor(conn, mouvement_stock_id)` | `int \| None` | Montant **exact, signé**, dont ce mouvement a fait varier le pool (+ entrée, − sortie) — jamais recalculé après coup. |
| `cout_reel_lot_minor(conn, lot_id)` | `int` | `COALESCE(prix_unitaire_definitif_minor, prix_unitaire_provisoire_minor)` — règle 2, jamais lié au CMP. |
| `cout_sortie_minor(conn, mouvement_stock_id, lot_id)` | `int` | Coût **par unité** applicable à une sortie (coût réel si INITIALE, sinon CMP au moment de la sortie). |
| `cout_sortie_total_minor(conn, mouvement_stock_id, lot_id)` | `int` | Montant **total exact** à facturer/imputer à cette sortie — à écrire dans `bl_client_ligne.cout_cmp_total_minor`. |
| `cout_chute_unitaire_minor(conn, chute_id)` | `int` | CMP par unité figé au moment de l'envoi en transformation (arrondi, affichage). |
| `cout_chute_total_minor(conn, chute_id)` | `int` | Montant total de la chute = quantité dans l'unité figée à l'envoi × CMP **exact** à l'envoi, arrondi une seule fois au millime (§6.4) — à écrire dans `chute.cout_cmp_total_minor`. |
| `montant_arrondi_minor(quantite, prix_minor)` | `int` | quantité exacte × prix exact, arrondi une seule fois au millime (règle §6.4). |
| `cmp_exact_au_moment_du_mouvement(conn, mouvement_stock_id)` | `(Fraction, str)` | CMP exact (non arrondi) et unité au moment d'une sortie de `STOCK_GMC`. |
| `cmp_actuel(conn, article_id, finition, longueur_m)` | `dict \| None` | CMP courant avec son unité de valorisation, sa quantité dans cette unité et sa devise. |
| `cmp_au_moment_du_mouvement_detail(conn, mouvement_stock_id)` | `dict \| None` | CMP figé pour un mouvement, avec l'unité en vigueur à sa date. |
| `cout_sortie_detail(conn, mouvement_stock_id, lot_id)` / `cout_chute_detail(conn, chute_id)` | `dict` | Coût unitaire d'une sortie / d'une chute avec son unité. |
| `unite_prix_lot(conn, lot_id)` | `str` | Unité des prix du lot (`lot.unite_prix`). |
| `unite_valorisation_en_vigueur(conn, article_id, instant=None)` | `str \| None` | Unité de valorisation de l'article à un instant. |
| `calculer_pools(conn, jusqu_au=None, article_id=None)` / `etat_pools_article(...)` | `tuple` / `list` | Calcul pur (sans écriture) des pools, pour contrôle ou traçabilité d'un changement d'unité. |

### Pourquoi deux variantes « unitaire » et « total »

Pour une sortie **SUPPLEMENT**, le montant total exact à facturer n'est
**pas** `cmp_unitaire_minor × quantité` : `cmp_unitaire_minor` est une valeur
**arrondie** dérivée pour l'affichage, alors que `montant_mouvement_minor`
est le montant **exact** (retrait proportionnel sur le total courant,
calculé une seule fois en arithmétique entière) réellement retiré du pool
pour ce mouvement précis — c'est cette valeur exacte que
`cout_sortie_total_minor()` relit, garantissant que le montant facturé à
l'affaire est **identique au millime/centime près** à ce que le ledger CMP a
réellement retiré. Voir la note de module en tête de `db/valorisation.py`
pour la démonstration chiffrée de l'écart possible entre les deux méthodes,
et pourquoi la méthode proportionnelle exacte garantit qu'un pool vidé
entièrement retombe toujours à exactement zéro, sans dérive résiduelle.

## 6. Unité de valorisation — règle définitive (finalisation Phase 5.5)

Règle validée (référence : `docs/BUSINESS_RULES.md` §16) : le CMP n'est pas
systématiquement en DT/kg ; il est exprimé dans l'**unité de valorisation
de l'article** (KG → DT/kg, ML → DT/ml, UNITE → DT/unité, TONNE → DT/tonne),
jamais imposée ni supposée par défaut.

### 6.1 Où l'unité est portée (migrations 0019 et 0020)

| Donnée | Unité |
|---|---|
| `article_unite_valorisation` | historique immuable : définition initiale (valable depuis l'origine de l'article), puis changements (unité précédente, nouvelle unité, date d'effet, motif de la dérogation, utilisateur, CMP de chaque pool dans l'ancienne et la nouvelle unité) |
| `lot.unite_prix` | unité dans laquelle le prix **provisoire** a été saisi (B) : l'unité de l'article ou, pour un article au poids, l'autre unité de masse (kg ↔ tonne) ; figée |
| `lot.unite_prix_definitif` | unité dans laquelle le prix **définitif** (facture) a été saisi (0020) ; obligatoire avec le prix définitif |
| `lot.unite_valorisation_article` | unité de valorisation de l'article (A) à la création du lot, fixée par la base puis figée (0020) |
| `inventaire_initial_ligne.unite_cout` | unité du coût **saisi** (B), même compatibilité |
| `cmp_stock_general.unite_valorisation`, `cmp_historique.unite_valorisation` | unité dans laquelle le CMP de la ligne est exprimé (celle en vigueur à la date du mouvement) |
| `regularisation_prix_fournisseur` | `unite_prix_provisoire` (= unité du prix du lot), `unite_prix_definitif` (unité de la facture), `unite_ecart` (unité commune ; la tonne si l'un est au kg et l'autre à la tonne) ; écart contrôlé par conversion exacte (0020) |

### 6.2 Calcul

- Quantité d'un mouvement dans une unité : UNITE = pièces ; ML = pièces ×
  longueur du lot ; KG = kg ; TONNE = kg / 1 000.
- **Entrée** d'un lot : quantité dans l'unité **du lot** × prix du lot
  (définitif sinon provisoire). C'est un montant d'argent : un lot créé
  avant un changement d'unité entre au pool exactement à son coût.
- **Sortie** : retrait proportionnel exact sur la quantité du pool dans
  l'unité **en vigueur à la date du mouvement** — au poids pour KG/TONNE,
  au métrage ou à la pièce pour ML/UNITE. Une sortie qui vide le pool en
  pièces emporte toute sa valeur restante (aucun résidu).
- **Coût réel** (affectation INITIALE) : quantité sortie dans l'unité du lot
  × coût réel du lot.
- **Chute** : quantité de chute dans l'unité en vigueur à l'envoi en
  transformation × CMP **exact** figé à l'envoi (jamais le CMP arrondi
  affiché).
- Chaque montant ci-dessus est arrondi une seule fois au millime (§6.4).
- **Régularisation** : cas A — le prix définitif (dans l'unité du lot)
  remplace le provisoire et le CMP est reconstruit ; cas B — écart tracé
  séparément, aucune réécriture (règle §3 inchangée).
- Seule conversion de prix acceptée : kg ↔ tonne (exacte,
  `convertir_prix_exact()`, fraction jamais arrondie). Un prix dans une
  autre unité que celle de l'article est refusé (aucune conversion
  implicite pièce ↔ kg ou pièce ↔ ml, qui dépendrait du poids ou de la
  longueur d'un lot).
- **Prix conservé dans son unité d'origine** (décision « Proposition A »,
  `docs/BUSINESS_RULES.md` §18) : article en DT/kg, lot à 2 500 500
  millimes/TONNE ; au calcul 2 500,5 millimes/kg exactement ; 1 000,3 kg →
  2 501 250,15 → 2 501,250 DT (une conversion prématurée en 2,501 DT/kg
  aurait donné 2 501,750 DT). Vérifié par `tests/test_phase5_5_prix_saisis.py`.

### 6.3 Changement d'unité

`services/unite_valorisation_service.py:changer_unite_valorisation()` :
motif obligatoire (dérogation), unité différente de l'actuelle, date
d'effet jamais dans le futur, jamais avant le dernier mouvement de
l'article (sinon la valorisation d'un mouvement déjà enregistré serait
réécrite). Les lignes `cmp_historique` antérieures restent dans l'ancienne
unité après toute reconstruction ; le CMP de chaque pool au moment du
changement est tracé dans les deux unités (`detail_cmp`). Exemple vérifié
par `tests/test_phase5_5_valorisation.py::test_changement_d_unite_trace_et_historique_non_reecrit` :
pool de 15 pièces / 1 540 kg valant 3 153,750 DT → 210,250 DT/unité avant,
2,048 DT/kg après ; la sortie suivante de 5 pièces / 520 kg est valorisée
au poids (1 064,903 DT) et non plus à la pièce (1 051,250 DT).

### 6.4 Arrondi monétaire — règle définitive (`docs/BUSINESS_RULES.md` §17)

Un montant calculé qui ne tombe pas exactement au millime est arrondi au
**millime le plus proche, 0,5 vers le haut, une seule fois**, sur le montant
final ; aucun sous-calcul n'est arrondi. Implémentation **unique** :
`core/arrondi.py:arrondi_minor()` (arithmétique entière pure), utilisée par
`db/valorisation.py` et `core/unites.py`.

| Montant | Calcul (précision interne conservée) | Exemple testé |
|---|---|---|
| Entrée d'un lot | quantité (unité du lot) × prix, arrondi une fois | 1 000,5 kg × 2,501 DT/kg → 2 502,251 DT |
| Sortie (stock général / supplément) | valeur du pool × quantité sortie / quantité du pool, arrondi une fois | 4,001 DT pour 4 kg, sortie de 2 kg → 2,001 DT |
| CMP (affichage) | valeur / quantité, arrondi une fois | 2,001 DT / 2 kg = 1,0005 → 1,001 DT/kg |
| Chute | quantité × CMP **exact** à l'envoi, arrondi une fois | 2 kg × 4,001/4 = 2,0005 → 2,001 DT (et non 2 × 1,000) |
| Coût réel d'une affaire | quantité (unité du lot) × coût réel, arrondi une fois | 410,5 kg × 2,001 → 821,411 DT |
| Inventaire initial | quantité (unité de l'article) × coût, arrondi une fois ; la valeur saisie doit être ce montant | 1 000,5 kg × 2,501 → « 2 502,251 DT » |
| Régularisation (cas A) | entrée recalculée avec le prix définitif, arrondi une fois | 1 000,5 kg × 2,503 → 2 504,252 DT |
| Vente au poids (`montant_minor_masse_prix`) | masse (kg) × prix (par kg), arrondi une fois — identique quel que soit le chemin kg/t | 1,0005 t × 2 501 DT/t → 2 502,251 DT |

Choix techniques (conséquences directes de la règle, pas de nouvelle règle) :

- Une **valeur saisie** (montant ou prix unitaire) n'est jamais arrondie :
  elle doit être exprimable en unités monétaires minimales entières dans
  son unité d'origine (représentation Phase 4.1), sinon elle est refusée
  (« Un prix unitaire n'est jamais arrondi. Saisissez le prix avec une
  précision représentable dans son unité d'origine. »). Un **prix unitaire
  converti** (ex. DT/t → DT/kg) n'est jamais stocké ni arrondi : le prix
  est conservé dans son unité d'origine et converti exactement au calcul
  (§18).
- La base refuse tout montant non entier (REAL) dans les 28 colonnes
  `*_minor` (garde-fou de la migration 0020).
- Pour EUR/USD, même règle à l'unité monétaire minimale de la devise (le
  centime), seule représentation possible depuis la Phase 4.1.
- Les montants arrondis sont toujours positifs ou nuls ; un montant négatif
  n'est jamais arrondi (aucun sens d'arrondi n'est supposé).
