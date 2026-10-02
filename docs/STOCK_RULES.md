# Règles de stock — mouvement physique, chutes et intégrité de la base

Document créé en **Phase 4.1** (phase corrective), à la demande explicite de
l'utilisateur (§7 du cadrage). Référence unique pour la mécanique du stock
(le registre append-only et ses garanties), la règle définitive des
**chutes**, et la checklist d'**intégrité** vérifiée à chaque phase. Pour les
coûts et la régularisation fournisseur, voir `docs/PRIX_REVIENT.md`. Pour le
détail schéma/tables, voir `docs/DATABASE.md`.

## 1. Le registre `mouvement_stock` — source de vérité exclusive

Inchangé depuis la Phase 4, rappelé ici car toute règle de ce document en
dépend :

- **Append-only, totalement immuable** (ni UPDATE ni DELETE, imposé par
  trigger). Aucune exception, y compris pour corriger une erreur de saisie —
  une correction passe par un **nouveau mouvement compensatoire**, jamais par
  la modification d'un mouvement existant.
- **Aucun autre endroit de la base ne stocke un solde de stock comme source
  de vérité indépendante.** `cmp_stock_general`, `cmp_historique`,
  `v_solde_lot_emplacement`, `v_stock_non_affecte_par_lot` sont tous des
  **caches ou vues reconstructibles** exclusivement depuis
  `mouvement_stock` — jamais mis à jour indépendamment, jamais désynchronisés
  par construction (puisqu'ils n'existent que comme fonction de ce registre).
- `affectation_stock` (réservation logique d'une quantité pour une affaire)
  **ne crée jamais de mouvement par elle-même** — une affectation ne bouge
  rien physiquement tant qu'elle n'est pas honorée par une sortie réelle.
  C'est pour cette raison que le cache CMP réagit à **tout** mouvement
  touchant `STOCK_GMC`, quelle que soit l'affectation liée (voir
  `docs/DATABASE.md` et `docs/PRIX_REVIENT.md` pour le détail).
- Les allocations ne créent jamais de double comptage : chaque affectation
  référence un lot précis et une quantité précise, plafonnée par trigger
  (`trg_affectation_plafond`, ne compte que les affectations `ACTIVE`), et
  chaque sortie physique est plafonnée par le solde réel du lot à
  l'emplacement (`trg_mouvement_solde_source`) — vérifié par les tests 1 à 3
  et par `tests/test_contraintes.py`.

### 1.1 Stock Service (Phase 5.5)

Depuis la Phase 5.5, `services/stock_service.py` est la seule voie
d'écriture dans le registre (`enregistrer_mouvement()`, sans transaction
propre ni COMMIT) ; il contrôle le type, les emplacements, le document
source, les doublons, le solde et le poids (tableau complet dans
`docs/DATABASE.md`, section « Phase 5.5 »).

- **Transformateur = emplacement réel** (décision validée) : envoi → GMC
  −N, transformateur +N ; retour de M pièces → GMC +M (lot résultat) et
  transformateur −M (lot d'origine, `CONSOMMATION_TRANSFORMATION`), toujours
  par paire (`enregistrer_retour_transformation()`) ; chutes → transformateur
  −K, CHUTES +K. Aucun stock fantôme possible par cette voie.
- **Disponibilité** : `disponibilite()` distingue physique `STOCK_GMC`,
  affecté non sorti, disponible (= physique − affecté), chez les
  transformateurs, et réservé devis (informatif, jamais déduit).
  `quantite_affectable_lot()` = physique réel − affecté : à utiliser avant
  toute affectation (le trigger `trg_affectation_plafond` ne plafonne que
  sur la quantité initiale du lot).
- **Correction d'inventaire** : `corriger_inventaire()`, une transaction
  complète (mouvement + audit `CORRECTION_INVENTAIRE`), motif obligatoire,
  utilisateur tracé, sur `STOCK_GMC` ou chez un transformateur.
- **Inventaire initial de démarrage** (`services/inventaire_initial_service.py`,
  règle validée) : origine spécifique (jamais un achat), à l'instant exact
  de mise en service ; unique ; impossible si le registre contient déjà des
  mouvements ; clos dès la première opération ; aucun mouvement ne peut être
  daté avant la mise en service. Chaque fin d'année, le module d'inventaire
  annuel (phase dédiée) comparera le stock théorique à un instant donné
  (`stock_service.stock(..., jusqu_au=...)`) à l'inventaire physique et
  corrigera les écarts par des corrections tracées — jamais par une nouvelle
  entrée de stock.
- **Unité obligatoire à la saisie** : `corriger_inventaire()` et
  l'inventaire initial exigent des valeurs avec unité (`core/unites.py`) et
  conservent la saisie d'origine (audit ou `saisie_originale`).
- **Test de conservation** : `verifier_conservation()` — entrées externes
  (réceptions + inventaire initial + corrections +) − corrections − = STOCK_GMC +
  transformateurs + CHUTES + LIVRE, en pièces, avec la liste des anomalies
  (stock fantôme, livraison sans destination `LIVRE`).
- **CMP** : exprimé dans l'unité de valorisation de l'article (DT/kg,
  DT/ml, DT/unité, DT/tonne — `docs/BUSINESS_RULES.md` §16) ;
  `reconstruire_cmp()` n'est appelé qu'après la validation de la
  transaction métier (`reconstruire_cmp_apres_transaction()`), car il fait
  lui-même un COMMIT. Tout montant calculé est arrondi une seule fois au
  millime le plus proche, 0,5 vers le haut (`docs/BUSINESS_RULES.md` §17).

## 2. Chutes — règle définitive (Phase 4.1 §3)

Une chute est la matière non récupérée lors d'une transformation
(galvanisation/GPP/débit) : reçu + chute = envoyé, toujours (trigger
`trg_reception_transfo_plafond`).

### 2.1 Valorisation

La chute est valorisée **au CMP, figé au moment où la matière a quitté
`STOCK_GMC` pour la transformation** (le mouvement `SORTIE_TRANSFORMATION`
d'origine) — **pas** au moment où la chute est constatée au retour, ni
influencée par ce qui s'est passé sur le pool entre-temps. La matière ne
change pas de pool pendant qu'elle est chez le transformateur ; son coût est
donc figé dès son départ de GMC.

`db/valorisation.py:cout_chute_unitaire_minor()` calcule le CMP par unité
de valorisation à cet instant (`cout_chute_detail()` donne aussi l'unité) ;
`cout_chute_total_minor()` = quantité de la chute **dans cette unité**
(pièces, ml, kg ou tonnes) × le CMP **exact** à cet instant (jamais le CMP
arrondi affiché), arrondi une seule fois au millime le plus proche, 0,5
vers le haut (règle §17) — c'est ce montant qu'il faut écrire dans
`chute.cout_cmp_total_minor`. Vérifié par
`tests/test_scenarios.py::test_11_...` et
`tests/test_phase41.py::test_chute_valorisee_au_cmp_et_sort_du_stock_normal`.

### 2.2 Sortie du stock normal

La chute fait partie d'un mouvement `SORTIE_TRANSFORMATION` qui retire la
**totalité** de la quantité envoyée de `STOCK_GMC` (le pool général diminue
de toute la quantité envoyée, pas seulement de la part qui deviendra chute —
le reste redevient un lot au retour). La chute elle-même
(mouvement `SORTIE_CHUTE`, de `CHEZ_TRANSFORMATEUR:<id>` vers `CHUTES`) ne
touche donc plus `STOCK_GMC` à ce stade : la sortie du stock normal a déjà eu
lieu à l'envoi, pas à la constatation de la chute — cohérent avec la
valorisation figée au moment de l'envoi (§2.1).

### 2.3 Traçabilité

Chaque chute reste traçable par :

- **affaire** : `chute.commande_client_id` (nullable — une transformation
  peut aussi concerner du stock général sans affaire précise),
- **article** : via `chute.lot_id → lot.article_id`,
- **transformation** : `chute.transformateur_id`,
- **date** : `chute.date`.

Vérifié par
`tests/test_phase41.py::test_chute_tracable_par_affaire_article_transformation_date`.

### 2.4 Exclusion de la marge individuelle

**Le coût d'une chute n'est jamais intégré automatiquement dans la marge
individuelle d'une affaire.** `chute.impact_marge_valide` reste à `0` par
défaut, en permanence — `db/valorisation.py` ne le bascule jamais à `1`
lui-même. Ce n'est plus un point ouvert (contrairement à la Phase 4) : la
Phase 4.1 **tranche définitivement** que ce coût va exclusivement dans le
bilan consolidé annuel (§2.5), jamais dans le calcul de marge d'une affaire
précise — aucune affaire ne voit sa marge individuelle modifiée par le seul
fait qu'une chute lui soit rattachée. Vérifié par
`tests/test_phase41.py::test_chute_sans_impact_immediat_sur_marge_individuelle`
(qui constate qu'aucune colonne de `commande_client` — qui ne porte
d'ailleurs aucune colonne de marge — n'est modifiée par la création ou la
valorisation d'une chute).

### 2.5 Bilan consolidé annuel

Le système permet de produire, à tout moment, un total annuel des coûts de
chutes, tous articles et toutes affaires confondus, via la vue
`v_bilan_chutes_annuel` (créée en `migrations/0016_devise_montants_minor.sql`) :

```sql
SELECT annee, devise, nombre_chutes, quantite_totale, poids_total_kg, cout_total_minor
FROM v_bilan_chutes_annuel
WHERE annee = '2026' AND devise = 'TND';
```

Regroupe par année (`substr(date,1,4)`) et par devise (des chutes dans des
devises différentes ne se somment jamais entre elles — cf.
`docs/PRIX_REVIENT.md` §1). Exemple du cadrage (Affaire A = 2 500 TND +
B = 1 200 + C = 800 → bilan annuel = 4 500 TND), reproduit à l'échelle des
tests par
`tests/test_phase41.py::test_bilan_consolide_annuel_des_chutes`.

## 3. Intégrité de la base — checklist vérifiée (Phase 4.1 §6)

Vérifiée à chaque phase, revérifiée intégralement en Phase 4.1 après la
migration 0016 :

| Vérification | Résultat |
|---|---|
| `python3 db/migrate.py --fresh` reconstruit depuis zéro | ✅ (deux exécutions indépendantes, résultats identiques) |
| Toutes les migrations passent (0001 à 0016) | ✅ |
| `PRAGMA integrity_check` | ✅ `ok` |
| `PRAGMA foreign_key_check` | ✅ aucune anomalie |
| Schéma final | 44 tables, 4 vues, 41 triggers, 46 index |
| Le stock reste reconstructible depuis le ledger append-only | ✅ (`reconstruire_cmp()` relit intégralement `mouvement_stock`) |
| Aucun stock physique stocké comme source de vérité indépendante | ✅ (§1 ci-dessus) |
| Les allocations ne créent pas de double comptage | ✅ (tests 1-3, `trg_affectation_plafond`) |
| Les régularisations financières ne réécrivent jamais l'historique physique | ✅ (`docs/PRIX_REVIENT.md` §3, cas B) |
| `python3 -m pytest tests/` | ✅ 31/31 (voir `CHANGELOG.md` pour le détail des ajouts Phase 4.1) |

Une seule différence structurelle avec la Phase 4 : **3 vues** sont devenues
**4** (ajout de `v_bilan_chutes_annuel`) — le nombre de tables, triggers et
index n'a pas changé (une reconstruction de table pour changer un type de
colonne n'ajoute ni ne retire de table).

**Revérifiée en Phase 5.5** après la migration 0017 : `--fresh` (17
migrations) ✅, `PRAGMA integrity_check` → `ok` ✅, `PRAGMA
foreign_key_check` → aucune anomalie ✅, schéma **46 tables, 4 vues, 45
triggers, 50 index** (+2 tables d'ouverture, +4 triggers d'immuabilité,
+4 index dont les 2 index uniques anti-doublons), migration 0017 prouvée
sans perte sur une base contenant déjà des données
(`tests/test_phase5_5_stock.py::test_migration_0017_conserve_les_donnees_existantes`),
pytest ✅ 178/178. **Puis après la migration 0018** (inventaire initial) :
`--fresh` (18 migrations) ✅, `integrity_check` → `ok` ✅,
`foreign_key_check` → aucune anomalie ✅, schéma inchangé en nombre (46
tables, 4 vues, 45 triggers, 50 index), reprise des données 0017 prouvée
(`test_migration_0018_reprend_les_donnees_de_l_ouverture_0017`), pytest ✅
223/223. **Puis après la migration 0019** (unité de valorisation) :
`--fresh` (19 migrations) ✅, `integrity_check` → `ok` ✅,
`foreign_key_check` → aucune anomalie ✅, schéma **47 tables, 4 vues, 51
triggers, 52 index** (+1 table d'historique d'unité, +6 triggers, +2 index),
ré-application sans effet ✅, reconstruction du CMP idempotente
(`test_reconstruction_cmp_multi_unites_idempotente`), migration prouvée sur
une base contenant déjà des données sans inventer d'unité
(`test_migration_0019_n_invente_aucune_unite_d_article`), pytest ✅
268/268. **Puis après l'arrondi monétaire et la correction du calcul des
tôles** (aucune migration) : `--fresh` exécuté deux fois → empreinte du
schéma identique ✅, `integrity_check` → `ok` ✅, `foreign_key_check` →
aucune anomalie ✅, schéma inchangé (47 tables, 4 vues, 51 triggers, 52
index), pytest ✅ 276/276. **Puis après la migration 0020** (prix conservé
dans son unité d'origine, garde-fou « montant entier ») : `--fresh` (20
migrations) exécuté deux fois → empreinte du schéma identique ✅,
`integrity_check` → `ok` ✅, `foreign_key_check` → aucune anomalie ✅,
schéma 47 tables, 4 vues, **94 triggers**, 52 index, ré-application sans
effet ✅, migration refusée proprement sur une base contenant un prix non
entier (`test_migration_0020_refuse_une_base_contenant_un_prix_non_entier`),
pytest ✅ 293/293.
