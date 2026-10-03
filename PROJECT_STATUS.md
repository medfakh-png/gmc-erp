# État du projet GMC

Roadmap complète : 16 phases (voir `CLAUDE.md`). État au terme de la
dernière session :

| Phase | Nom | Statut |
|---|---|---|
| 1 | Analyse fonctionnelle | ✅ Terminée et validée |
| 2 | Architecture technique | ✅ Terminée et validée |
| 3 | Modèle de données détaillé | ✅ Terminée et validée |
| 4 | Base de données réelle | ✅ Terminée et validée |
| 4.1 | Phase corrective (montants entiers, coût final fournisseur, chutes) | ✅ Terminée et validée |
| 5.1 | Backend — Analyse de l'existant + architecture cible | ✅ Terminée et validée (M.1-M.5) |
| 5.2 | Backend — Configuration + connexion DB + infrastructure | ✅ Terminée et validée |
| 5.3 | Backend — Repositories + erreurs métier + audit | ✅ Terminée et validée |
| 5.4 | Backend — Numérotation documentaire | ✅ Terminée et validée |
| 5.5 | Backend — Stock Service | ✅ Terminée et validée (30/09/2026) |
| 5.6 | Backend — Affaires (clients, devis, réservations, commande, affectations, suppléments, réaffectations, situation) — périmètre validé | 🔎 **Analyse seulement, aucun code.** Analyses v9 (`docs/ANALYSE_PHASE_5_6_v9.md`) et v10 (`docs/ANALYSE_PHASE_5_6_v10.md`, barres 12 m / 6 m, **validée** le 02/10/2026). Décisions validées et reportées dans `docs/BUSINESS_RULES.md` §19 à §26. **8 points encore ouverts** (§27) ; **validation d'ensemble de la 5.6 en attente** |
| 5.7-5.11 | Services métier (achats, transformations, livraisons, coûts/marge), tests d'intégration | ⏳ Pas commencées |
| 6 | Frontend | ⏳ Pas commencée |
| 7-16 | Stock, achats, ventes, transformations, MACF, dashboard, import/export, sécurité, tests, packaging | ⏳ Pas commencées |

## Base commune du projet (depuis le 02/10/2026)

Le projet a maintenant une source unique, partagée entre Mohamed, Claude
et ChatGPT :

- **Dépôt GitHub privé** : `medfakh-png/gmc-erp`, branche `main`.
- **Copie de travail sur le PC de Mohamed** : `C:\Users\medfa\GMC-ERP`
  (même contenu que le dépôt, plus une archive de sauvegarde
  `gmc-erp_sauvegarde_2026-10-02.zip`, volontairement hors dépôt).
- La base `db/gmc.db` n'est **pas** dans le dépôt (fichier régénérable
  par `python3 db/migrate.py`).

Historique du dépôt : `576a425` (sauvegarde initiale, état Phase 5.5
validée + analyse 5.6 v9) ; `9671f70` (`db/gmc.db` retirée du suivi) ;
puis le dépôt documentaire du 02/10/2026 décrit ci-dessous.

## Phase 5.6 — état au 02/10/2026

**Rien n'est codé pour la 5.6.** Le code, les migrations et la base sont
exactement ceux de la Phase 5.5 validée : 20 migrations, 47 tables,
4 vues, 94 triggers, 293 tests réussis.

Ce qui est validé (détail dans `docs/BUSINESS_RULES.md`) :

- §19 à §22 : transport, D1 à D6, N1 à N15, K1 à K22 (30/09/2026).
- §23 : O1 à O9, X1 à X9, Y1 à Y6, CT1 à CT21, P-MULT, P-BST, P-ART,
  P-RET, P-KG-TR (analyses v5 à v9, du 30/09 au 02/10/2026).
- §24 : **règle définitive des barres de 12 m et de 6 m** (LG1 à LG9,
  V10-1 à V10-8). 1 barre de 12 m = 2 barres de 6 m à finition identique,
  sans transformation ; sens inverse interdit ; reliquat rattaché au lot
  source ; coût proportionnel à la longueur.
- §25 : les 22 lectures L-a à L-v et les 14 propositions C1 à C14,
  tranchées une par une le 02/10/2026 (deux sous-questions reportées :
  L-f bis et C4 bis, §27) ; Y6-L ; Q-ANNUL.
- §26 : registre des règles remplacées (dont K2, remplacée par LG8).

**Écart connu entre la règle et le code (FACT, audit du 02/10/2026).** Le
code de la Phase 5.5 ne connaît qu'« 1 pièce de 12 m » : une barre de
12 m est invisible pour une commande de 6 m ; on ne peut pas en prendre
6 m sans prendre la barre entière ; la base accepte un lot de 6 m sur une
ligne de 12 m ; aucun test ne couvre la règle (cinq cas réels exécutés,
analyse v10 §B). La correction est décrite
dans l'analyse v10 et n'est pas commencée.

**Ordre des travaux validé (V10-7)**, chaque étape sur accord explicite :

1. Documentation métier — **fait le 02/10/2026**.
2. Tests de la règle 12 m / 6 m, écrits avant le code lorsque cela est
   possible — **écrits le 02/10/2026, en attente de la validation de
   Mohamed** : `tests/test_phase5_6_longueurs_12m_6m.py`, 29 cas (les
   quinze tests obligatoires T01 à T15 et les compléments T16 à T25 ;
   aucun test pour V10-8). 2 cas réussissent déjà ; 27 sont marqués
   « en attente » : 7 attendent la migration, 20 attendent aussi le code.
   Suite complète : 295 réussis, 27 en attente.
3. Migration corrective dédiée, additive pour les données (colonnes
   ajoutées, aucune table reconstruite, aucune donnée supprimée ;
   vues et triggers remplacés ou ajoutés).
4. Code : disponibilité, compatibilité lot / ligne, affectation,
   valorisation, reconstruction, contraintes.
5. Tests complets : nouveaux, existants, reconstruction, intégrité,
   `--fresh`, non-régression.
6. Rapport, puis validation.

V10-8 (avertissement quand un reliquat existe dans un autre lot) reste
dans l'analyse : aucun code, aucune migration, aucun test tant que
l'ensemble de la Phase 5.6 n'est pas validé.

**Points ouverts de la 5.6** : `docs/BUSINESS_RULES.md` §27 (8 points).

**Écarts documentaires connus (audit du 02/10/2026), non corrigés** :

- les documents des Phases 1 à 3 ne sont pas dans le dépôt ;
- `docs/DATABASE.md` cite une fonction `cout_sortie()` ; le code contient
  `cout_sortie_minor()`, `cout_sortie_detail()` et
  `cout_sortie_total_minor()` ;
- l'analyse v5 n'existe que comme fichier remis en conversation ; ses
  passages utiles sont cités dans la v9.

## Règle de méthode (depuis la Phase 5.5, imposée par l'utilisateur)

Cycle obligatoire pour toute sous-phase : **ANALYSE → VALIDATION HUMAINE →
CODE → TESTS → RAPPORT → VALIDATION FINALE**. Jamais de code, de migration
ni de modification de schéma pendant l'analyse. Toute décision métier
nouvelle apparue pendant le développement : STOP, FACT / PROPOSITION /
POINT À VALIDER, attendre la validation.

## Règles métier validées en Phase 5.5

Consignées dans `docs/BUSINESS_RULES.md` : §11 catalogue articles
(création réservée à Mohamed, modification par dérogation auditée, pas de
fusion automatique des doublons MV, code article non décidé → UUID), §12
**inventaire initial de démarrage** à l'instant de mise en service, puis
inventaire physique + rapprochement chaque fin d'année (le 31/12/2025 n'est
pas l'ouverture automatique de 2026), §13 transformateur = emplacement
physique réel (pas de stock fantôme), §14 masses définitives (FP 45/20 =
7,2 ; FP 120/30 = 28,8 ; FP 130/30 = 31,2 kg/ml ; tôles planes = volume
dm³ × 8 kg/dm³, contrôle 3000 × 1500 × 1 mm = 36 kg), §15 **unité
obligatoire à la saisie** (kg physique, tonnes pour les ventes au poids),
§16 **unité du CMP / coût de revient** (DT/kg, DT/ml, DT/unité ou DT/tonne
selon l'article, jamais imposé en DT/kg, aucune unité par défaut,
changement tracé sans réécriture de l'historique), §17 **arrondi
monétaire** (millime le plus proche, 0,5 vers le haut, une seule fois sur
le montant final).

## Ce qui existe concrètement à ce stade (Phase 5.5)

En plus du socle Phase 5.2 à 5.4 :

- **Migrations 0017, 0018 et 0019** : 47 tables, 4 vues, 51 triggers, 52
  index, 19 migrations. Type `CONSOMMATION_TRANSFORMATION` (M2), inventaire
  initial de démarrage (0018 remplace l'ouverture au 31/12 de 0017 : 2
  tables immuables avec saisie d'origine, type `ENTREE_INVENTAIRE_INITIAL`,
  3e origine de lot), index uniques anti-double-comptage (M1), unité de
  valorisation (0019 : historique immuable `article_unite_valorisation`,
  `lot.unite_prix` figée, unité du coût d'inventaire initial, cache CMP
  avec unité).
- **`db/valorisation.py`** : moteur CMP piloté par l'unité de valorisation
  de l'article (au poids pour KG/TONNE, au métrage/à la pièce pour
  ML/UNITE), unité en vigueur à la date de chaque mouvement, montants non
  arrondis une seule fois au millime (chute au CMP exact). Résultats Phase
  4/4.1 identiques à l'unité.
- **`core/arrondi.py`** : implémentation unique de la règle d'arrondi
  monétaire, utilisée par le moteur CMP et les conversions d'unités.
- **`services/unite_valorisation_service.py`** : définition initiale et
  changement motivé de l'unité de valorisation d'un article (historique,
  date, utilisateur, CMP tracé dans les deux unités).
- **`services/stock_service.py`** : consultations (soldes, stock par
  emplacement et à une date, stock chez les transformateurs, disponibilité
  = physique − affecté, réservation informative, quantité affectable,
  historique), contrôle de conservation, `enregistrer_mouvement()` (sans
  transaction propre ni COMMIT), retour de transformation par paire,
  correction d'inventaire (mouvement + audit, motif obligatoire), CMP
  reconstruit après la transaction.
- **`services/inventaire_initial_service.py`** : capacité technique de
  l'inventaire initial de démarrage (aucun import réel).
- **`core/unites.py`** : unité obligatoire à la saisie, conversions exactes
  kg↔t, mm/cm/m, prix dans l'unité de valorisation (kg↔t seulement, aucune
  conversion implicite), dm, dm³/m³, kg/dm³, montants arrondis une seule
  fois ; **`core/masses_validees.py`** : masses FP validées, écarts MV
  signalés sans remplacement, poids des tôles planes (volume dm³ × 8
  kg/dm³).
- **Repositories** : `stock_repository.py`, `inventaire_initial_repository.py`,
  `unite_valorisation_repository.py`, `article_repository.py` (lecture
  seule) ; `base.py` enrichi.
- **`core/erreurs.py`** : 12 nouvelles erreurs (dont
  `ErreurUniteValorisation`) + correction de la traduction des vraies
  erreurs de la base (défaut latent de la 5.3).
- **Migration 0020** : prix conservé dans son unité d'origine (lot :
  `unite_prix` kg ↔ tonne admis, `unite_prix_definitif`,
  `unite_valorisation_article` ; unités de la régularisation) et
  garde-fou « montant monétaire entier » sur les 28 colonnes `*_minor`.
  Schéma : 47 tables, 4 vues, 94 triggers, 52 index, 20 migrations.
- 293 tests automatisés, tous verts (108 Phases 4 à 5.4 inchangés + 79
  Stock Service + 64 unités/masses/tôles/arrondi + 25 valorisation par
  unité et arrondi + 17 prix conservés dans leur unité d'origine).

## Décisions d'architecture backend validées (Phase 5.1)

- Pas d'API HTTP en Phase 5 — services Python indépendants de toute couche
  HTTP ; l'API/le frontend seront traités ultérieurement (Phase 6).
- Structure de dossiers validée : `core/`, `repositories/`, `services/`,
  `db/`, `tests/`.
- Ne pas créer `docs/TRANSFORMATIONS.md`, `docs/MACF.md`, `docs/TESTS.md`
  tant qu'ils n'ont pas de contenu réel.
- Les erreurs métier seront détaillées en français dès la Phase 5.3, avec
  une structure technique exploitable.
- Ordre d'implémentation validé : 5.2 → 5.3 → 5.4 → 5.5 → 5.6 → 5.7 → 5.8 →
  5.9 → 5.10 → 5.11.

## Ce qui existe concrètement à ce stade (Phase 5.4)

En plus du socle Phase 5.2/5.3 (inchangé) :

- **`core/numerotation.py`** — `prochain_numero(conn, type_document,
  annee=None) -> str` : numéro humain séquentiel par type de document et
  par année civile (`DEV-2026-0001`, etc.), format et 10 types déjà
  validés (Phase 2/4), aucune règle inventée. N'ouvre jamais sa propre
  transaction (même principe que `core/audit.py`, Phase 5.3) : un
  rollback annule aussi l'incrémentation du compteur.
- **`repositories/numerotation_repository.py`** — accès SQL structuré à
  `compteur_numerotation` (upsert atomique).
- **`repositories/base.py`** — nouvelle aide générique
  `executer_et_retourner()` (écriture avec clause `RETURNING`).
- 108 tests automatisés, tous verts : 82 tests Phase 4/4.1/5.2/5.3
  (inchangés) + 26 nouveaux tests Phase 5.4.
- Aucune création de document, aucune dépendance externe ajoutée, aucune
  modification de la base de données.

## Ce qui existe concrètement à ce stade (Phase 5.3)

En plus du socle Phase 5.2 (inchangé) :

- **`core/erreurs.py`** — hiérarchie `ErreurMetier` (7 sous-classes ciblées
  + repli générique `ErreurRegleViolee`) et `traduire_erreur_sqlite()`,
  qui convertit les `IntegrityError` levées par les triggers déjà en
  place (Phase 4) en messages français exploitables — conforme à la
  décision M.4 de la Phase 5.1.
- **`repositories/base.py`** — helpers SQL génériques (`executer`,
  `un_ou_aucun`, `tous`), utilisés par tout repository concret. Aucun
  repository par agrégat métier (lot, mouvement_stock, commande_client...)
  n'a été créé cette phase — ils seront ajoutés au fil des Phases 5.5+ par
  le service qui en aura réellement besoin (choix signalé et expliqué au
  début de cette session, voir `CURRENT_SESSION.md`).
- **`repositories/audit_repository.py`** — accès SQL structuré à
  `journal_audit` (insertion, lecture par entité/affaire), sans logique
  métier.
- **`core/audit.py`** — service d'audit : `enregistrer()` (valide l'action
  contre les 12 valeurs réellement autorisées par le CHECK de
  `journal_audit.action`, sérialise `avant`/`apres` en JSON, ne fait
  qu'un simple INSERT sur la connexion fournie — ne pas ouvrir sa propre
  transaction, pour permettre de la regrouper avec l'écriture métier
  qu'elle documente), `historique_entite()`, `historique_affaire()`.
- 82 tests automatisés, tous verts : 50 tests Phase 4/4.1/5.2 (inchangés)
  + 32 nouveaux tests Phase 5.3 (hiérarchie d'erreurs, traduction des
  erreurs SQLite, repositories, service d'audit, intégration avec le
  mécanisme de transaction de la Phase 5.2 — commit et rollback
  conjoints).
- Toujours aucune dépendance externe ajoutée.

## Ce qui existe concrètement à ce stade (Phase 5.2)

- Une vraie base SQLite (`db/gmc.db`), construite par 16 migrations
  versionnées, reconstruite et vérifiée : **44 tables, 4 vues, 41 triggers,
  46 index**. `PRAGMA integrity_check` → `ok`. `PRAGMA foreign_key_check` →
  aucune anomalie. **Schéma inchangé depuis la Phase 4.1** — la Phase 5.2 n'a
  touché aucune migration, aucune table, aucune règle métier.
- Le moteur de calcul CMP (`db/valorisation.py`), inchangé depuis la Phase
  4.1, **entièrement en arithmétique entière**.
- **Tous les montants financiers de la base sont des entiers** en unité
  monétaire minimale (millime TND / centime EUR / cent USD) — voir
  `docs/PRIX_REVIENT.md`.
- **Socle d'infrastructure backend (nouveau, Phase 5.2)** :
  - `core/configuration.py` — configuration centralisée (chemin de base,
    environnement `development`/`test`/`production`, niveau et destination
    des logs), résolue depuis des variables d'environnement
    (`GMC_ENV`, `GMC_DB_PATH`, `GMC_LOG_LEVEL`, `GMC_LOG_FILE`), avec repli
    sur un défaut jamais dépendant du répertoire courant du processus.
  - `db/connexion.py` — connexion SQLite centralisée (réutilise
    `db/migrate.py:get_connection`, donc `PRAGMA foreign_keys=ON` +
    `PRAGMA journal_mode=WAL` déjà validés) + mécanisme générique de
    transaction (`transaction(conn)`, commit sur succès / rollback sur
    exception) que les futurs services (Phase 5.3+) réutiliseront.
  - Logging technique standard (module `logging`), séparé et sans lien
    avec `journal_audit` (traçabilité métier, toujours pas encore codée).
  - Aucune dépendance externe ajoutée (uniquement la bibliothèque standard
    Python + `pytest` pour les tests, déjà présent).
- 50 tests automatisés (`tests/`, exécutés avec `pytest`), tous verts : les
  31 tests Phase 4/4.1 (inchangés, aucune régression) + 19 nouveaux tests
  d'infrastructure Phase 5.2 (configuration, connexion, transactions,
  logging).
- La documentation technique à jour : `docs/DATABASE.md`,
  `docs/BUSINESS_RULES.md`, `docs/PRIX_REVIENT.md`, `docs/STOCK_RULES.md`,
  `CLAUDE.md`.

**Aucun module métier (Stock/Affaire/Achat/Transformation/Livraison/
Coût-Marge Service) n'a encore été développé** — la Phase 5.2 a
volontairement livré uniquement le socle technique (configuration,
connexion, transactions, logging), conformément à son périmètre strict.

## Décisions techniques prises cette phase (signalées, pas des décisions métier)

Phase 4 (rappel, détaillées dans `docs/DATABASE.md`) :
1. Le cache CMP (`cmp_stock_general`/`cmp_historique`) avait été rendu à
   tort immuable ; corrigé pour rester reconstructible.
2. Le plafond d'affectation d'un lot et le workflow de réaffectation ont dû
   être ajustés pour permettre une réaffectation à 100% d'un lot déjà
   entièrement affecté (contradiction interne découverte et corrigée).

Phase 4.1 (cette session, détaillées dans `CHANGELOG.md` et
`docs/PRIX_REVIENT.md`) :
3. Défaut technique de devise : `'TND'` partout, sauf `facture_client`/
   `facture_client_ligne` (`'EUR'`, cohérent avec le nom d'origine
   `montant_eur` et le contexte douane déjà validé). Chaque ligne reste
   libre de porter sa propre devise.
4. `chute.cout_cmp_unitaire` et `bl_client_ligne.cout_cmp_unitaire` ont été
   renommées `cout_cmp_total_minor` (deviennent des **montants totaux**, pas
   des prix unitaires) — nécessaire pour que le montant stocké soit
   exactement celui retiré du pool CMP, sans dérive d'arrondi. Voir
   `docs/PRIX_REVIENT.md` §5.
5. Garde-fou technique ajouté : un pool CMP (article/finition/longueur) est
   mono-devise ; `reconstruire_cmp()` refuse plutôt que de mélanger deux
   devises dans un même total. N'a aujourd'hui aucun effet observable (GMC
   n'a qu'une devise d'exploitation pour son stock général) — c'est une
   protection, pas une nouvelle règle métier.

Phase 5.2 (cette session, détaillées dans `CHANGELOG.md`) :
6. `core/configuration.py` résout la configuration via des variables
   d'environnement (`GMC_ENV`/`GMC_DB_PATH`/`GMC_LOG_LEVEL`/`GMC_LOG_FILE`)
   avec repli sur un défaut calculé depuis l'emplacement du module — jamais
   depuis le répertoire courant du processus. Choix technique, pas une
   règle métier.
7. `core/` et `db/` n'ont pas de `__init__.py` (paquets-espace de noms
   implicites Python 3), cohérent avec la convention déjà en place pour
   `db/` depuis la Phase 4.

Phase 5.3 (cette session, détaillées dans `CHANGELOG.md`) :
8. Seul `repositories/audit_repository.py` a été créé cette phase — pas
   de repository par agrégat métier (lot, mouvement_stock,
   commande_client...). Choix technique de périmètre, signalé et expliqué
   en début de session : ces repositories appartiennent aux futurs
   Stock/Affaire/Achat Service (Phase 5.5+), qui les définiront selon
   leurs propres besoins réels.
9. Correction de comptage : le rapport Phase 5.1 indiquait « 11 types
   d'action » pour `journal_audit.action` — vérification directe du CHECK
   en base (Phase 5.3) : ce sont **12** valeurs. Erreur de comptage sans
   conséquence sur le code ou les données.

Phase 5.4 (cette session, détaillées dans `CHANGELOG.md`) :
10. Aucun cadrage détaillé n'avait été fourni pour cette sous-phase
    (contrairement à 5.2/5.3, qui avaient chacune un document de cadrage
    complet). Périmètre limité, signalé avant codage : un seul utilitaire
    de numérotation (`prochain_numero()`), aucune création de document —
    choix technique de portée, pas une décision métier.
11. `mypy` (installation autonome de cet environnement) ne peut résoudre
    l'import `pytest` sur aucun fichier de test — limite d'environnement
    pré-existante (confirmée identique sur les tests déjà validés des
    Phases 5.2/5.3), pas une régression de cette phase. `mypy` reste donc
    limité au code source dans cet environnement.

## Points ouverts nécessitant ton avis

Jusqu'à la Phase 5.4 : aucun point resté ouvert. Le traitement comptable
des chutes a été **tranché définitivement en Phase 4.1** (voir
`docs/STOCK_RULES.md` §2.4-2.5) ; les points d'architecture backend
(M.1-M.5) ont été tranchés en Phase 5.1 (voir plus haut).

Phase 5.6 — points restant ouverts (02/10/2026) : voir
`docs/BUSINESS_RULES.md` §27. En résumé : liste des 8 causes
d'annulation ; SUPERADMIN indisponible ; Q-BCT et Q-TRF ; BST préparé
d'une commande annulée ; bon de commande partiellement réceptionné à
l'annulation (5.7) ; format du code article ; transport estimé d'une
ligne ajoutée par avenant ; validation d'ensemble.

Phase 5.5 — points restant ouverts :
- Aucun point bloquant.
- Limite acceptée (décision « Proposition A ») : un prix plus fin que le
  millime dans sa propre unité (ex. 2 500,5005 DT/t) est refusé, jamais
  arrondi — la représentation monétaire globale n'est pas modifiée. Le cas
  2 500,5 DT/t pour un article au kg est, lui, accepté et exact.
- Contrôle « seul Mohamed » pour définir/changer une unité de valorisation :
  utilisateur et motif tracés, droits appliqués en Phase 14.
- Article oublié dans l'inventaire initial et découvert après la mise en
  service : comment l'intégrer ? (l'inventaire initial est clos dès la
  première opération ; non bloquant).
- Phase 5.8 : retour d'un stock d'inventaire initial situé chez un
  transformateur (pas de bon de sortie), débit 1 → N pièces, coût du lot
  résultat vs coût de la chute.
- Résolus : FP 120/30 = 28,8 et FP 130/30 = 31,2 kg/ml ; ouverture
  remplacée par l'inventaire initial (plus de question « ouverture après
  des mouvements » : l'inventaire initial précède toute opération) ;
  « valorisation interne : kg » tranché par la règle de l'unité du CMP
  (§16) ; règle d'arrondi tranchée (§17) ; tôles tranchées (volume dm³ ×
  8 kg/dm³) ; ventes en tonnes = ventes au poids (précisé).

## Décisions techniques prises en Phase 5.5 (signalées, pas des décisions métier)

12. Nom du nouveau type de mouvement : `CONSOMMATION_TRANSFORMATION`
    (proposé dans l'analyse, décision de principe validée).
13. Document source d'une correction d'inventaire = sa ligne
    `journal_audit` (créée dans la même transaction) — évite une table
    supplémentaire non validée.
14. ~~Horodatage d'ouverture au 31/12 23:59:59.999~~ — remplacé :
    l'inventaire initial est horodaté à l'instant exact de mise en service,
    fourni avec son heure (fuseau recommandé), converti en UTC (convention
    du registre). Aucun mouvement ne peut être daté avant.
15. Coût d'inventaire initial écrit comme prix provisoire ET définitif du
    lot (coût déjà validé, aucune régularisation fournisseur possible) —
    inchangé.
16. ~~Une seule ouverture, refusée si du stock existe avant~~ — remplacé :
    un seul inventaire initial (règle validée « un inventaire initial de
    démarrage »), impossible si le registre contient déjà des mouvements,
    clos dès la première opération (sinon modification rétroactive du CMP
    de sorties déjà passées).
17. Emplacements d'inventaire initial et de correction limités au stock GMC
    (`STOCK_GMC` + transformateurs) : CHUTES et LIVRE ne sont pas du stock.
18. `TRANSFERT` non pris en charge par le Stock Service (aucune règle
    métier définie, un seul dépôt).
19. Cohérence type ↔ emplacements, motif et emplacements valides contrôlés
    par le service (comme validé dans l'analyse) ; en base : uniquement les
    index uniques M1 et les CHECK des nouvelles tables.
20. Renommage « stock d'ouverture » → « inventaire initial » (migration
    0018) : empêche toute confusion future avec l'ouverture des années
    suivantes, qui résulte du rapprochement et ne crée jamais de stock.
21. Unités : les opérations saisies (correction d'inventaire, inventaire
    initial) exigent des valeurs avec unité et conservent la saisie
    d'origine ; la brique interne `enregistrer_mouvement` reste en unités
    internes nommées explicitement (`quantite` en pièces, `poids_kg`).
22. Montants : calcul décimal exact ; un montant qui ne tombe pas sur une
    unité monétaire minimale est refusé (aucune règle d'arrondi validée).
    Prix TTC refusé (conversion impossible sans taux de TVA validé) ; prix
    sans mention HT lu comme HT (la règle validée écrit indifféremment
    « 5 DT/kg » et « 5 DT HT/kg »).
23. Unité du CMP — mise en œuvre : historique immuable des unités d'article
    (il sert de trace d'audit de la dérogation : `journal_audit` n'a pas
    d'action prévue pour cela) ; définition initiale valable depuis
    l'origine de l'article ; changement jamais daté dans le futur ni avant
    le dernier mouvement de l'article ; `lot.unite_prix` fixée à la
    création puis figée ; lots existants marqués `UNITE` (fait : valorisés
    par pièce), aucun article existant ne reçoit d'unité.
24. Moteur : un pool vidé en pièces emporte toute sa valeur restante (pas de
    résidu même si les poids sortis diffèrent des poids entrés) ; seule
    conversion de prix acceptée kg ↔ tonne ; une unité = une pièce.
25. Tôles : dimensions acceptées en mm, cm, dm ou m (avec unité),
    converties en dm ; volume en dm³ × 8 kg/dm³ (densité lue comme une
    mesure « 8 kg/dm³ » pour la traçabilité).
26. Arrondi : une seule implémentation (`core/arrondi.py`, arithmétique
    entière) pour tous les moteurs ; une valeur saisie (montant ou prix
    unitaire) et un prix unitaire converti ne sont jamais arrondis ; même
    règle à l'unité minimale pour EUR/USD (centime) ; aucun montant négatif
    n'est arrondi.
27. Chute : valorisée avec le CMP exact à l'envoi (recalculé depuis le
    registre), plus avec le CMP arrondi affiché — conséquence directe de
    « aucun sous-calcul arrondi » ; identique à la Phase 4.1 lorsque le CMP
    tombe juste.
28. Le contrôle d'exactitude avant enregistrement d'une entrée (ajouté à la
    finalisation précédente) est retiré : tout montant est désormais
    calculable par la règle d'arrondi.
29. Proposition A — mise en œuvre : prix provisoire et prix définitif ont
    chacun leur unité (une facture peut être libellée en kg pour un BL à la
    tonne) ; écart de régularisation exprimé dans l'unité commune, ou à la
    tonne en cas de kg/tonne (seule unité où les deux prix restent des
    entiers exacts) ; entrée d'un lot calculée « quantité dans l'unité du
    prix × prix », strictement égale à « quantité dans l'unité de
    valorisation × prix converti exactement » (valable aussi pour un lot
    antérieur à un changement d'unité de l'article).
30. Garde-fou « montant entier » étendu à toutes les colonnes `*_minor` (et
    pas seulement aux prix de lot), vérification préalable qui fait échouer
    la migration sans rien modifier si une donnée existante n'est pas
    entière.

## Prochaine étape proposée

**Au 03/10/2026.** La documentation métier est à jour et l'étape 2
(tests de la règle 12 m / 6 m) est écrite. Suite proposée, sur accord
explicite de Mohamed à chaque étape :

1. valider l'étape 2 (les tests) ;
2. étape 3 : la migration corrective dédiée ;
3. étape 4 : le code, puis les tests complets et le rapport ;
4. en parallèle, à son rythme : ses réponses aux points ouverts de la
   5.6 (`docs/BUSINESS_RULES.md` §27), nécessaires à la validation
   d'ensemble de la Phase 5.6 mais pas à la règle 12 m / 6 m.

Aucune migration ni aucun code sans cet accord. Ne pas commencer la 5.7.

*Historique (situation au 30/09/2026, conservée telle quelle) :*

Phase 5.5 validée. Phase 5.6 : analyse livrée (voir `CURRENT_SESSION.md`),
en attente de ta validation et de tes réponses aux points à valider —
aucun code, aucune migration avant.

Décision reçue pendant l'analyse 5.6 (30/09/2026) : transport estimatif
au prix par tonne ; pour une ligne vendue à la pièce ou au ml, prix de
transport de la ligne demandé et saisi manuellement
(`docs/BUSINESS_RULES.md` §19). Sous-points tranchés par le cahier 5.6 :
montant total de la ligne, prix DT/t saisi par ligne, saisie obligatoire
avec 0 explicite.

Cahier « analyse technique finale » reçu. Analyse livrée dans
`docs/ANALYSE_PHASE_5_6.md` : 23 incohérences, proposition de migration
0021 (non créée), services, transactions, audit, environ 150 tests. En
attente : 6 décisions bloquantes (D1 à D6) et 14 confirmations rapides
(C1 à C14). Les règles du cahier seront reportées dans
`docs/BUSINESS_RULES.md` à la validation.

Décisions D1 à D6 validées le 30/09/2026 : compatibilité des lots, poids
commercial (masse MV, GALVA), devises (EUR, TND, EUR), avenants de
commande, choix manuel des lots et stock chez le galvanisateur
(catégories A à F), compte SUPERADMIN. Elles sont consignées dans
`docs/BUSINESS_RULES.md` §20. L'analyse version 2 ajoute le schéma logique
et 15 ambiguïtés nouvelles (N1 à N15), dont la règle GALVA « déjà
validée » introuvable dans le projet.

Décisions N1 à N15 reçues le 30/09/2026 (`docs/BUSINESS_RULES.md` §21) :

- méthode de poids validée dans la fiche article ;
- GALVA × (1 + % ÷ 100), GPP + 2 % ;
- taux de devis désigné par Mohamed ;
- supplément au-delà de la quantité originale ;
- affectations au SUPERADMIN seul (délégation future) ;
- garde-fou absolu ;
- **correction** : l'affectation porte sur l'état réel du lot, et une
  transformation crée un nouveau lot.

Réponses définitives K1 à K22 reçues le 30/09/2026
(`docs/BUSINESS_RULES.md` §22). L'analyse version 4 ne laisse ouverts que :

- O1 à O9 (O6 devenue le choix technique CT7) ;
- les confirmations C sans réponse ;
- la validation des choix techniques CT1 à CT15 (aucun n'est validé).

Une relecture indépendante du premier jet de la version 4 a relevé 40
écarts, tous corrigés avant livraison.

Encadré historique :

L'analyse version 3 liste 22 contradictions restantes (K1 à K22). Une
relecture indépendante (28 écarts corrigés) a été faite avant la
livraison.
