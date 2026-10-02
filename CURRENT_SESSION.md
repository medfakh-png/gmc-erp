# Dernière session de travail — Phase 5.1 à 5.4, puis Phase 5.5 (analyse validée, code terminé, corrections/clarifications intégrées)

## Règle de méthode en vigueur depuis la Phase 5.5 (imposée par l'utilisateur)

Cycle obligatoire pour **toute** sous-phase future :
**ANALYSE → VALIDATION HUMAINE → CODE → TESTS → RAPPORT → VALIDATION FINALE.**
Jamais de passage direct de l'analyse au code. Pendant l'analyse : aucun
code métier, aucune migration, aucune modification du schéma, aucun
changement fonctionnel. Si une nouvelle décision métier apparaît pendant le
développement : STOP, la présenter (FACT / PROPOSITION / POINT À VALIDER),
attendre la validation avant de continuer sur ce point.

## Contexte au démarrage

La Phase 4.1 (phase corrective) était terminée et validée. L'utilisateur a
demandé le démarrage de la **Phase 5 — Backend Foundation**, avec une
consigne explicite de progressivité (pas de génération du backend en une
seule fois) et un protocole de rapport standardisé obligatoire à partir de
cette phase.

## Étape 5.1 — Analyse du backend actuel (validée)

Aucun code écrit à cette étape (analyse uniquement, conformément à la
consigne explicite). Travaux :

1. Relecture intégrale de `CLAUDE.md`, `PROJECT_STATUS.md`,
   `CURRENT_SESSION.md`, `CHANGELOG.md`, `docs/BUSINESS_RULES.md`,
   `docs/STOCK_RULES.md`, `docs/PRIX_REVIENT.md`, `docs/DATABASE.md`.
2. Écart signalé : `docs/TRANSFORMATIONS.md`, `docs/MACF.md`,
   `docs/TESTS.md` référencés par le cadrage mais absents du projet.
3. Inspection réelle du code (aucun backend, aucun framework, aucune
   dépendance externe — confirmé par lecture des imports).
4. Vérifications DB : `--fresh`, `integrity_check`, `foreign_key_check`,
   31/31 tests — tous au vert, aucune régression.
5. Production du rapport d'architecture cible (A-M), validé par
   l'utilisateur avec 5 décisions explicites :
   - **M.1** — pas d'API HTTP en Phase 5, services Python indépendants de
     toute couche HTTP.
   - **M.2** — structure de dossiers validée : `core/`, `repositories/`,
     `services/`, `db/`, `tests/`.
   - **M.3** — ne pas créer `docs/TRANSFORMATIONS.md`/`MACF.md`/`TESTS.md`
     tant qu'ils n'ont pas de contenu réel.
   - **M.4** — erreurs métier détaillées en français dès la Phase 5.3.
   - **M.5** — ordre d'implémentation : 5.2→5.3→5.4→5.5→5.6→5.7→5.8→5.9→
     5.10→5.11.

## Étape 5.2 — Configuration + connexion DB + infrastructure (terminée, en attente de validation)

Périmètre strict respecté : aucun module métier, aucune modification de la
base de données, aucune nouvelle règle métier, aucun travail frontend.

1. **`core/configuration.py`** (nouveau) — configuration centralisée :
   chemin de base SQLite, environnement (`development`/`test`/
   `production`), niveau et destination des logs, résolus via les
   variables d'environnement `GMC_ENV`/`GMC_DB_PATH`/`GMC_LOG_LEVEL`/
   `GMC_LOG_FILE`, avec repli sur un défaut calculé depuis l'emplacement
   du module (jamais depuis le répertoire courant du processus). Fonction
   `configurer_logging()` : logger technique `gmc`, idempotent, séparé de
   `journal_audit` (qui reste la seule source de traçabilité métier, pas
   encore codée).
2. **`db/connexion.py`** (nouveau) — connexion SQLite centralisée,
   réutilisant tel quel `db/migrate.py:get_connection` (donc
   `PRAGMA foreign_keys=ON` + `PRAGMA journal_mode=WAL` déjà validés, pas
   de duplication de cette logique) + mécanisme générique
   `transaction(conn)` (context manager : commit si succès, rollback si
   exception, exception d'origine toujours relancée) que les futurs
   services (Phase 5.3+) réutiliseront pour leurs écritures atomiques.
3. **`tests/test_phase5_2_infrastructure.py`** (nouveau, 19 tests) :
   configuration (défaut, test, rejet valeurs invalides, indépendance au
   répertoire courant, variables d'environnement), connexion
   (foreign_keys, WAL, fermeture), transaction (commit, rollback, rollback
   après exception sans donnée partielle, propagation de l'exception
   d'origine), logging (niveau, idempotence, écriture fichier, logger
   enfant).
4. `db/migrate.py` et `db/valorisation.py` **non modifiés** — réutilisés
   tels quels, conformément à la consigne de rétrocompatibilité.
5. Vérifications techniques réelles exécutées (aucun résultat inventé) :
   `--fresh` (16 migrations, ok), `PRAGMA integrity_check` → `ok`,
   `PRAGMA foreign_key_check` → aucune anomalie, `ruff`/`flake8`/`mypy`
   exécutés sur les fichiers créés (deux anomalies réelles trouvées et
   corrigées : une variable de test inutilisée, une redéfinition de nom
   détectée par mypy — voir `CHANGELOG.md`), suite complète `pytest` :
   **50/50 tests verts** (31 existants inchangés + 19 nouveaux).

## Étape 5.3 — Repositories + erreurs métier + audit (terminée, en attente de validation)

Périmètre strict respecté : aucune logique des futurs Stock/Affaire/Achat/
Transformation/Livraison/Facturation Service, aucune API HTTP, aucun
frontend, aucune modification de la base de données ou des règles métier.

**Reformulation faite avant codage** (comme demandé) : pas de repository
par agrégat métier cette phase (lot, mouvement_stock, commande_client...)
— seuls `repositories/base.py` (générique) et
`repositories/audit_repository.py` (transverse, explicitement demandé par
cette sous-phase) ont été créés. Les repositories métier appartiennent
aux futurs services (Phase 5.5+) qui les définiront selon leurs besoins
réels.

1. **`core/erreurs.py`** (nouveau) — hiérarchie `ErreurMetier` + 6
   sous-classes ciblées (`ErreurStockInsuffisant`, `ErreurPlafondDepasse`,
   `ErreurReaffectationInvalide`, `ErreurEnregistrementImmuable`,
   `ErreurDeviseMelangee`, `ErreurEnregistrementIntrouvable`) + repli
   générique `ErreurRegleViolee`. `traduire_erreur_sqlite()` reconnaît 8
   triggers réels (vérifiés en base) et retombe sur un message générique
   (mais jamais silencieux) pour le reste — conforme à la décision M.4 de
   la Phase 5.1 (erreurs métier en français dès la 5.3).
2. **`repositories/base.py`** (nouveau) — `executer()` (traduit toute
   `IntegrityError` via `core.erreurs`), `un_ou_aucun()`, `tous()`.
3. **`repositories/audit_repository.py`** (nouveau) — accès SQL structuré
   à `journal_audit` (`inserer`, `obtenir`, `lister_pour_entite`,
   `lister_pour_affaire`), sans logique métier ; n'expose ni mise à jour
   ni suppression (la table est totalement immuable en base).
4. **`core/audit.py`** (nouveau) — service d'audit : `enregistrer()`
   valide l'action contre `ACTIONS_VALIDES` (12 valeurs, vérifiées
   directement contre le CHECK réel de `journal_audit.action`), sérialise
   `avant`/`apres` en JSON, **ne fait qu'un INSERT sur la connexion
   fournie** — jamais sa propre transaction, pour participer à la
   transaction ouverte par l'appelant (conforme à la règle validée en
   Phase 5.1 §H et au principe de transactions atomiques de la Phase 5.2).
5. **`tests/test_phase5_3.py`** (nouveau, 32 tests) : hiérarchie
   d'erreurs (7), traduction SQLite→métier (11), repositories/base (3),
   audit_repository (3), core.audit (6), garde-fou anti-dérive
   `ACTIONS_VALIDES` vs CHECK réel (1), intégration transaction (commit
   conjoint + rollback conjoint, 2 tests décisifs).
6. Vérifications réelles exécutées : suite complète `pytest` → **82/82
   verts** (50 précédents + 32 nouveaux), `ruff`/`flake8`/`mypy` sans
   erreur (après correction de 7 anomalies de style réelles — lignes trop
   longues, indentation de continuation — trouvées par `flake8`, aucune
   n'affectait le comportement), `--fresh`/`integrity_check`/
   `foreign_key_check` inchangés (44 tables/4 vues/41 triggers/46 index).

## Étape 5.4 — Numérotation documentaire (validée par l'utilisateur)

Contrairement aux étapes 5.2 et 5.3, l'utilisateur n'a pas fourni de
cadrage détaillé pour cette sous-phase — juste « je valide , la prochaine »
après la validation de la Phase 5.3. Avant de coder, une reformulation
brève a été envoyée (transparence, pas de décision silencieuse) : périmètre
limité à un seul utilitaire de numérotation, aucune création de document,
aucune modification de schéma, en s'appuyant uniquement sur le format et
les 10 types de document déjà validés (Phase 2, confirmés Phase 4, dans
`docs/BUSINESS_RULES.md` et le commentaire de
`migrations/0002_numerotation.sql`).

1. **`core/numerotation.py`** (nouveau) — `prochain_numero(conn,
   type_document, annee=None) -> str` : incrémente atomiquement
   `compteur_numerotation` (table déjà en place, Phase 4) et renvoie le
   numéro humain au format `TYPE-ANNEE-NNNN` (ex. `DEV-2026-0001`).
   `annee` par défaut = année civile en cours. `TYPES_DOCUMENT_VALIDES`
   (10 préfixes) validés avant tout accès DB (`ValueError` sinon).
   N'ouvre jamais sa propre transaction — participe à celle de l'appelant,
   même principe que `core.audit.enregistrer()` (Phase 5.3) : un rollback
   annule aussi l'incrémentation, le numéro n'est jamais perdu ni dupliqué.
2. **`repositories/numerotation_repository.py`** (nouveau) — accès SQL
   structuré (`incrementer_et_obtenir`, upsert atomique via `RETURNING`,
   et `obtenir`, lecture seule).
3. **`repositories/base.py`** (modifié) — nouvelle aide générique
   `executer_et_retourner()` pour toute écriture avec clause `RETURNING`,
   réutilisable par tout futur repository.
4. **`tests/test_phase5_4_numerotation.py`** (nouveau, 26 tests) : format,
   incrémentation, isolation par type et par année, année par défaut,
   validation des 10 types, 3 tests d'intégration décisifs avec
   `db.connexion.transaction()` (commit définitif, rollback qui redonne le
   même numéro, partage de transaction avec une autre écriture), lecture
   seule.
5. Aucune création de document (devis, commande...) — cette fonction sera
   appelée par les futurs services métier (Phase 5.5+), à l'intérieur de
   leur propre transaction, au moment de créer leur document.
6. Vérifications réelles exécutées : suite complète `pytest` → **108/108
   verts** (82 précédents + 26 nouveaux), `ruff`/`flake8` sans erreur,
   `mypy --explicit-package-bases` sans erreur sur le code source (limite
   pré-existante de l'environnement confirmée sur les fichiers de test —
   voir « Problèmes rencontrés » ci-dessous), `--fresh`/
   `integrity_check`/`foreign_key_check` inchangés (44 tables/4 vues/41
   triggers/46 index, aucune migration ajoutée).

## Étape 5.5 — Stock Service : ANALYSE (validée par l'utilisateur)

Aucun code, aucune migration, aucune modification de la base. Les
constats ci-dessous ont été prouvés par exécution réelle sur des bases
**jetables** (hors projet, dossier temporaire) — jamais sur `db/gmc.db`.

**Nouvelle règle métier communiquée (non codée, à reporter dans
`docs/BUSINESS_RULES.md` après validation)** — catalogue articles : la liste
MV est la base initiale du référentiel ; le référentiel n'est pas fermé
(création ultérieure possible) ; une création ne modifie jamais un article
existant ; chaque article a son propre identifiant ; caractéristiques
structurées et normalisées ; utilisable dans tous les modules ; création
traçable (utilisateur, date) ; désignation commerciale ≠ libellé normalisé
possible ; éviter les doublons fonctionnels. **Réservés à l'utilisateur**
(ne pas décider) : qui crée, validation préalable, format du code article,
règles de fusion/déduplication, champs obligatoires supplémentaires.

Constats principaux (détail complet dans le rapport d'analyse remis en
conversation) :

1. Origine de la liste MV : fichier `tablleau_preparation.xlsx`, feuille
   `mv` (2 colonnes : DESIGNATION, Masse) — 387 lignes non vides, 8
   doublons exacts, 2 doublons de casse, 4 désignations avec espaces
   parasites, 377 désignations distinctes après normalisation
   espaces/casse/séparateurs ; 2 masses suspectes (FP 45/20 = 4,07 ;
   FP 120/30 = 283,8) ; pour les tôles, « Masse » = kg **par tôle**, pas
   kg/m (incompatible avec `article.masse_lineique_kg_m`). Jamais importée
   dans la base (0 article).
2. Table `article` : pas d'unicité, pas de créateur (`cree_par`), pas de
   statut, pas de libellé normalisé distinct de la désignation, aucun
   trigger (UPDATE et DELETE d'un article non référencé acceptés).
3. Défauts de convention/garde-fous stock prouvés : solde résiduel fantôme
   chez le transformateur après retour (100 envoyés/95 reçus/5 chutes →
   total toutes zones 195) ; double entrée de réception acceptée ; double
   sortie de livraison pour une même ligne de BL acceptée ; affectation au
   delà du stock physique acceptée (plafond = quantité initiale) ;
   emplacement inconnu accepté ; correction d'inventaire sans motif
   acceptée ; stock d'ouverture au 31/12/2025 impossible (un lot doit
   venir d'un BL ou d'un lot parent) ; `reconstruire_cmp()` fait un
   COMMIT au milieu d'une transaction ouverte ; débit 1 → 2 pièces refusé
   par `trg_reception_transfo_plafond`.
4. Écarts entre helpers de test et modèle validé : sortie livraison sans
   destination `LIVRE` (le modèle Phase 3 prévoit STOCK_GMC → LIVRE) ;
   retour de transformation référencé avec l'id de l'en-tête sous un type
   `reception_transformation_ligne`.

## Étape 5.5 — Stock Service : CODE (terminé, en attente de validation finale)

L'utilisateur a validé l'analyse avec des décisions complémentaires
(catalogue articles, stock d'ouverture N = clôture N-1, transformateur =
emplacement physique réel, brique `enregistrer_mouvement`, correction
d'inventaire, garde-fous, M2, M3, CMP après transaction, masses, code
article non décidé → UUID conservé) et un périmètre strict (§12 de sa
validation). Tout a été consigné dans `docs/BUSINESS_RULES.md` §11-§14.

1. **`migrations/0017_stock_service_socle.sql`** (M1, M2, M3 autorisés) :
   type `CONSOMMATION_TRANSFORMATION` (clôture du lot d'origine au retour),
   type `ENTREE_STOCK_OUVERTURE`, tables `stock_ouverture` /
   `stock_ouverture_ligne` (immuables, `cree_par` obligatoire, valeur =
   pièces × coût), 3e origine de lot (exactement une origine), index
   uniques anti-double-comptage. Reconstruction de `lot` et
   `mouvement_stock` par la technique de la migration 0016 ; conservation
   des données prouvée par un test dédié.
2. **`core/erreurs.py`** : 9 nouvelles erreurs françaises (quantité,
   emplacement, mouvement incohérent, document source manquant, doublon,
   motif, disponibilité, montant, ouverture) ; **correction d'un défaut
   latent de la Phase 5.3** : la traduction ne reconnaissait que les NOMS
   des triggers, alors que SQLite ne transmet que le TEXTE du RAISE — les
   vrais messages sont maintenant reconnus (preuve par test sur de vraies
   erreurs de la base), la reconnaissance par nom est conservée.
3. **`repositories/`** : `base.py` (+ `un_dict`, `des_dicts`, lecture
   indépendante du `row_factory`), `article_repository.py` (lecture
   seule), `stock_repository.py`, `stock_ouverture_repository.py`.
4. **`services/stock_service.py`** : consultations (soldes, stock par
   emplacement et à une date, stock chez les transformateurs,
   disponibilité, quantité affectable, historique), contrôle de
   conservation, `enregistrer_mouvement()` (aucune transaction propre,
   aucun COMMIT), `enregistrer_retour_transformation()` (paire
   anti-fantôme), `corriger_inventaire()` (transaction complète mouvement +
   audit), `reconstruire_cmp_apres_transaction()`.
5. **`services/stock_ouverture_service.py`** : capacité technique du stock
   d'ouverture (aucun import réel réalisé).
6. **`tests/test_phase5_5_stock.py`** : 70 tests (tous les tests
   obligatoires du §13 de la validation) ; suite complète **178/178**
   (108 existants inchangés + 70).
7. Documentation : `CLAUDE.md` (règle 7 : cycle Analyse → Validation →
   Code ; carte du code), `docs/BUSINESS_RULES.md` (§11-§14),
   `docs/DATABASE.md`, `docs/STOCK_RULES.md`.

## Étape 5.5 — CORRECTIONS/CLARIFICATIONS validées (intégrées, en attente de validation finale)

Règles validées définitivement par l'utilisateur après le rapport de code
(consignées dans `docs/BUSINESS_RULES.md` §12, §14, §15) :

1. **Unité obligatoire à la saisie** (règle transversale) —
   `core/unites.py` : lecture d'une saisie avec unité (refus si absente ou
   ambiguë), saisie d'origine conservée, conversions exactes kg↔t,
   prix/kg↔prix/t, montants exacts (refus plutôt qu'arrondi non validé).
   Appliquée aux deux saisies de la 5.5 : `corriger_inventaire()` (quantité
   et poids avec unité, saisie tracée dans l'audit) et l'inventaire
   initial (toutes les valeurs avec unité, saisie dans
   `saisie_originale`).
2. **FP définitifs** — `core/masses_validees.py` : FP 45/20 = 7,2 ;
   FP 120/30 = 28,8 ; FP 130/30 = 31,2 kg/ml ; un écart avec le fichier MV
   est signalé, jamais fusionné ni remplacé.
3. **Démarrage 2026 = inventaire initial de démarrage** (le 31/12/2025
   n'est pas l'ouverture automatique) — migration
   `0018_inventaire_initial_demarrage.sql` (remplace l'ouverture de 0017,
   données reprises) + `services/inventaire_initial_service.py` : unique,
   à l'instant exact de mise en service, impossible si des mouvements
   existent, clos dès la première opération, aucun mouvement daté avant.
   L'architecture ne bloque pas les inventaires annuels (stock théorique à
   un instant, corrections tracées).
4. **Tôles** : formule consignée telle que validée (résultat en kg,
   coefficient 8) ; aucun calcul automatique implémenté (unités d'entrée à
   préciser, non nécessaire en 5.5).
5. **STOP signalé** : « valorisation interne : kg » vs moteur CMP validé par
   pièce — moteur inchangé ; l'inventaire initial n'accepte qu'un coût par
   pièce en attendant la décision.
6. Tests : 223/223 (108 Phases 4 à 5.4 inchangés ; 79 Stock Service dont
   8 appels de `corriger_inventaire` adaptés à la saisie avec unité,
   10 tests d'ouverture remplacés par 16 tests d'inventaire initial,
   1 test de migration 0018 ; 36 tests unités/masses).

## Étape 5.5 — FINALISATION : unité du CMP et tôles (terminée, en attente de validation finale)

Deux décisions validées définitivement par l'utilisateur (consignées dans
`docs/BUSINESS_RULES.md` §16 et §14, `docs/PRIX_REVIENT.md` §6) :

1. **Unité du CMP / coût de revient** : le CMP est exprimé dans l'unité de
   valorisation de l'article (DT/kg, DT/ml, DT/unité, DT/tonne), jamais
   imposé en DT/kg, aucune unité par défaut ; changement d'unité tracé
   (ancienne unité conservée, date, utilisateur), historiques de coûts
   jamais réécrits. Mise en œuvre :
   - analyse (FACT) : l'unité était implicite partout (« par pièce ») ;
     aucun article n'avait d'unité ; la base réelle ne contient aucune
     donnée ;
   - migration `0019_unite_valorisation_article.sql` (justifiée à
     l'utilisateur avant application) : historique immuable
     `article_unite_valorisation`, `lot.unite_prix` (fixée à la création,
     figée ; lots existants = `UNITE`), `inventaire_initial_ligne.unite_cout`,
     cache CMP recréé avec l'unité ;
   - `db/valorisation.py` réécrit : quantité de chaque mouvement dans l'unité
     (pièces, ml, kg, t), entrée = quantité dans l'unité du lot × prix du
     lot, sortie au prorata dans l'unité en vigueur à la date du mouvement,
     chute et coût réel dans l'unité, calcul pur séparé de l'écriture ;
     résultats Phase 4/4.1 identiques à l'unité ;
   - `services/unite_valorisation_service.py` (+ repository) : définition
     initiale, changement motivé (non rétroactif, jamais futur), CMP tracé
     dans l'ancienne et la nouvelle unité ;
   - inventaire initial : coût dans l'unité de l'article (kg ↔ t seulement) ;
     Stock Service : entrée en STOCK_GMC de valeur non exacte refusée avant
     enregistrement.
2. **Tôles** : dimensions en mm (cm/m convertis), formule
   `((L × l × e) / 1000) × 8` appliquée telle quelle, contrôle 3000 × 1500 ×
   1 mm = 36 kg (`core/masses_validees.py:calcul_poids_tole_plane()`).
   Constat signalé : avec des mm, la formule donne des grammes (36 000) —
   converti en kg, à confirmer.
3. **STOP signalé** : aucune règle d'arrondi validée pour « quantité × prix »
   non exact au millime (fréquent au kg/t/ml) — refusé en attendant.
4. Tests : 268/268 (223 existants dont 1 test d'inventaire initial adapté à
   la règle tranchée et la fixture `seed_referentiels` qui définit l'unité
   UNITE de l'article de test ; + 20 tests de valorisation par unité ; + 25
   tests prix/unité et tôles).

## Étape 5.5 — FINALISATION (suite) : arrondi au millime et tôles par volume (terminée, prête pour validation finale)

Décisions validées définitivement (`docs/BUSINESS_RULES.md` §17 et §14) :

1. **Arrondi monétaire** : millime le plus proche, 0,5 vers le haut, une
   seule fois par montant calculé, sur le montant final ; aucun sous-calcul
   arrondi. Mise en œuvre : `core/arrondi.py` (implémentation unique) ;
   `db/valorisation.py` (entrée, sortie, CMP, coût réel, chute au CMP exact
   à l'envoi), inventaire initial (valeur = montant arrondi), régularisation
   (entrée recalculée), `core/unites.montant_minor_masse_prix` (vente au
   poids). Les refus « montant non exact » de la finalisation précédente
   sont retirés. Valeurs saisies et prix unitaires convertis jamais
   arrondis.
2. **Tôles** : volume (dm³) × 8 kg/dm³, dimensions converties en dm
   (mm, cm, dm, m) ; plus aucune interprétation « en grammes ». Ajout de
   dm, dm³/m³ et kg/dm³ dans `core/unites.py`.
3. **Ventes au poids en tonnes** (précision de l'utilisateur) intégrée au
   §15.
4. Aucune migration. Tests : 276/276 (108 Phases 4 à 5.4 et 79 Stock
   Service inchangés ; 2 tests « refus du montant non exact » supprimés et
   remplacés par 10 nouveaux tests d'arrondi/tôles ; 4 tests adaptés).

## Étape 5.5 — DERNIÈRE CORRECTION : prix conservé dans son unité d'origine (terminée, prête pour validation finale)

1. **Vérification demandée** : un prix 2 500,5 DT/t pour un article en DT/kg
   était refusé (calculs exacts en mémoire, mais stockage impossible : prix
   de lot entiers dans l'unité de l'article) ; la base acceptait aussi un
   REAL dans une colonne `*_minor`. Rapport FACT → LIMITATION →
   PROPOSITION → IMPACT, arrêt pour validation.
2. **Décision validée « Proposition A »** (`docs/BUSINESS_RULES.md` §18) :
   prix conservé dans l'unité saisie quand kg ↔ tonne ; conversion exacte
   au calcul seulement ; seul le montant final arrondi. Proposition B
   (représentation globale) non retenue.
3. Mise en œuvre : migration `0020_unite_prix_saisie.sql` (unités du lot et
   de la régularisation, garde-fou « montant entier » sur 28 colonnes) ;
   `db/valorisation.py` (`convertir_prix_exact`, `ecart_unitaire_exact`,
   coût réel dans son unité, `cout_reel_lot_exact`) ; `core/unites.py`
   (`prix_saisi`, `unites_de_prix_compatibles`, message « Un prix unitaire
   n'est jamais arrondi… ») ; inventaire initial (coût conservé dans son
   unité, trace de la conversion) ; `stock_repository`, `core/erreurs.py`,
   fixture de régularisation.
4. Tests : 293/293 (17 nouveaux dans `tests/test_phase5_5_prix_saisis.py` ;
   2 tests adaptés : coût d'inventaire au kg saisi à la tonne désormais
   conservé à la tonne, test de migration 0019 appliquant aussi 0020).

## Phase 5.5 — VALIDÉE par l'utilisateur (30/09/2026)

## Étape 5.6 — ANALYSE (livrée, en attente de validation — aucun code)

Périmètre proposé (lecture de la roadmap « affaires, achats,
transformations, livraisons, coûts/marge » dans cet ordre, à confirmer) :
**Affaire Service** — devis, commande client, affectations initiales,
quantités supplémentaires, réaffectations, situation d'une affaire.

Constats principaux (FACT, schéma réel) : prix du devis et de la commande
sans unité (contraire aux règles §15/§18) ; ligne de commande en pièces
seulement (aucun poids commercial, alors que les ventes au poids sont en
tonnes) ; aucun lien ligne de commande ↔ ligne de devis ; aucune
vérification article/finition/longueur entre un lot affecté et la ligne de
commande ; une réaffectation partielle clôture toute l'affectation
d'origine ; plafond d'affectation de la base calculé sur la quantité
initiale du lot (le service devra utiliser `quantite_affectable_lot()`).

Points à valider : voir le rapport d'analyse (périmètre, unité de la
quantité commandée, unités des prix, affectation d'un lot d'une autre
finition/longueur, plafond de l'affectation initiale, motif d'un
supplément, cycle de vie du devis et de la commande, réservations,
clients et taux de change, réaffectation partielle).

### Réponses reçues (30/09/2026)

- **Point 3 — transport estimatif : DÉCISION VALIDÉE** (consignée dans
  `docs/BUSINESS_RULES.md` §19) : prix de transport par tonne ; pour une
  ligne vendue dans une autre unité (pièce, ml…), le système demande le
  prix de transport de la ligne, saisi manuellement.
  - FACT (schéma réel) : seul `devis_ligne.prix_transport_estimatif_minor`
    existe, sans unité et facultatif ; la ligne de commande n'a aucun
    champ transport.
  - Sous-points ouverts (PROPOSITIONS, non décidées) :
    a) saisie manuelle = **montant total de la ligne** (plutôt qu'un prix
       par pièce ou par ml) — lecture littérale de « le prix de transport
       de cette ligne » ;
    b) prix à la tonne **saisi sur chaque ligne** (comme aujourd'hui dans
       le schéma) plutôt qu'une fois par devis ;
    c) saisie manuelle **obligatoire** pour valider la ligne ; 0 accepté
       seulement s'il est saisi explicitement (ex. enlèvement par le
       client).
  - Reste du point 3 (prix de vente et prix d'achat estimatif conservés
    dans leur unité de saisie, §18) : toujours en attente.
- Points 1, 2, 4 à 11 : en attente.

### Cahier « Phase 5.6 — analyse technique finale » reçu (30/09/2026)

L'utilisateur a validé le périmètre et la plupart des règles.
L'analyse technique finale est livrée dans `docs/ANALYSE_PHASE_5_6.md`.

- **Périmètre validé** : clients, devis et lignes, réservations
  informatives, commande et lignes, affectations, suppléments,
  réaffectations, statuts, situation calculée. Aucune opération 5.6 ne
  crée de mouvement de stock.
- **Règles validées dans le cahier** :
  - clients : Mohamed seul, audit, jamais supprimés ;
  - devis : EN_COURS → CONFIRMÉ / EXPIRÉ / ANNULÉ ;
  - annulation par Mohamed seul, avec une cause parmi 8 normalisées ;
  - réservation informative ;
  - un devis → une commande ;
  - quantité en pièces + unité de vente ;
  - poids de vente : formule validée ou saisie manuelle, figé à la
    confirmation ;
  - transport : DT/t par ligne ou montant total saisi, obligatoire, 0
    explicite ;
  - commande : BROUILLON → CONFIRMÉE → SOLDÉE ;
  - annulation d'une commande confirmée par Mohamed seul, refusée si déjà
    livrée ;
  - manques → approvisionnement (5.7) ;
  - plafonds réels ;
  - supplément avec motif ;
  - réaffectation partielle conservant le reste ;
  - SOLDÉE manuelle.
- **Bilan de l'analyse** :
  - 23 incohérences relevées (FACT) ;
  - migration 0021 proposée (non créée) ;
  - services, transactions, audit ;
  - environ 150 tests listés ;
  - vérification indépendante des FACT par un agent séparé : 9
    imprécisions corrigées.
- **En attente de ta décision** :
  - 6 décisions bloquantes :
    - D1 compatibilité lot ↔ ligne ;
    - D2 formules du poids de vente et zinc ;
    - D3 devises et taux d'un devis ;
    - D4 modifications d'une commande confirmée ;
    - D5 choix manuel des lots à la confirmation ;
    - D6 identification de Mohamed ;
  - 14 confirmations rapides (C1 à C14).
- **Base inchangée** : empreinte identique avant et après. 293 tests
  passent toujours.

### Décisions D1 à D6 validées (30/09/2026) — analyse version 2

Reportées dans `docs/BUSINESS_RULES.md` §20 et dans
`docs/ANALYSE_PHASE_5_6.md` (section « RÈGLES VALIDÉES — D1 À D6 » et
schéma logique §2) :

- **D1** : même article ; même finition, sauf NOIR/LAC → GALVA ou GPP ;
  même longueur, sauf multiples exacts.
- **D2** : vente en tonne → masse validée de la MV (fiche article), jamais
  de formule inventée ; autres unités → poids manuel ; GALVA → poids de
  base + % GALVA selon la règle déjà validée.
- **D3** : vente EUR, achat estimé TND, transport estimé EUR, chacun avec
  sa devise ; taux seulement si une conversion est nécessaire.
- **D4** : modifications historisées d'une commande confirmée (ajout,
  augmentation, diminution, ligne livrée ou affectée), sans mouvement ni
  allocation cassée.
- **D5** : disponibilité réelle calculée, choix des lots toujours manuel,
  aucun FIFO ; stock chez le galvanisateur distingué (catégories A à F),
  affectable avant réception, sans mouvement.
- **D6** : Mohamed = compte SUPERADMIN ; droits liés au rôle du compte,
  jamais au nom.

**Nouvelles ambiguïtés à trancher (N1 à N15)** :

- N1, N2 : nature de la masse (kg/m ou kg/pièce) ; article sans masse
  vendu à la tonne ;
- N3, N4 : règle GALVA **introuvable** dans le projet (seule la colonne
  `pct_galva` existe) ; GPP ;
- N5 : devises pré-remplies ou imposées, transport en EUR/t, arrondi EUR
  au centime, taux non utilisé en 5.6 ;
- N6 à N9 : avenants — augmentation ≠ supplément (quantité en vigueur),
  diminution, lignes livrées ou affectées, qui et motif ;
- N10 : rôles autorisés à affecter ;
- N11 : emplacement mémorisé dans l'affectation et la réservation ;
- N12 : distinguer E et F ;
- N13 : garde-fou tant que la 5.8 ne fait pas suivre les affectations ;
- N14 : rôle SUPERADMIN unique ;
- N15 : combinaison des exceptions D1.

Les confirmations C1 à C12 et C14 restent en attente (C13 tranchée par
D1).

### Décisions N1 à N15 reçues (30/09/2026) — analyse version 3

Reportées dans `docs/BUSINESS_RULES.md` §21 et correction de D1 au §20 :

- N1 : méthode de poids validée (kg/ml, kg/m², kg/pièce ou autre méthode
  validée) ; masses MV à vérifier ; comparaison et validation par Mohamed,
  jamais de choix silencieux.
- N2 : vente en tonne = méthode validée obligatoire, pas de poids manuel de
  contournement.
- N3 : GALVA = poids brut × (1 + % ÷ 100), % saisi par article (IPE100 6 m
  : 48,6 → 51,516 kg à 6 %).
- N4 : GPP + 2 % fixe.
- N5 : achat et transformation en TND, vente et transport en EUR ; taux de
  devis désigné par Mohamed, historisé.
- N6 : quantité originale conservée ; au-delà de l'originale =
  supplément au CMP.
- N7 : diminution avec libération explicite.
- N8 : même prix pour les lignes identiques d'une commande ; regroupement
  possible à la facturation.
- N9, N10, N14 : opérations sensibles au SUPERADMIN ; affectations au
  SUPERADMIN seul pour l'instant, délégation future prévue ; un seul
  SUPERADMIN.
- N11 : localisation conservée.
- N12 : transformation en 5.8.
- N13 : garde-fou absolu.
- N15 : remplacé par la **correction** — un lot brut n'est pas GALVA ou GPP
  avant transformation ; l'affectation porte sur l'état réel du lot.

**Contradictions restantes K1 à K22** (analyse §4). Une relecture
indépendante a relevé 28 écarts ; ils sont corrigés, et les ajouts vont
de K16 à K22. Principales :

- K1 : naissance du lot transformé chez le galvanisateur, pour que
  l'exemple D5 reste possible ;
- K2 : exceptions D1 = « utilisable après transformation » ;
- K3 : plafond INITIAL et suppléments issus d'avenants ;
- K4 : formule du coût estimé converti ;
- K5 : auteur du taux ;
- K7 : méthodes de poids et fiabilisation du référentiel ;
- K8 : périmètre de « affecter » ;
- K10 : définition de « ligne identique » et renégociation.

C1 à C14 reproduites telles quelles (§5), avec la liste des C touchées par
N6.

### Réponses définitives K1 à K22 reçues (30/09/2026) — analyse version 4

Reportées dans `docs/BUSINESS_RULES.md` §22 (et précision d'arrondi au
§17). Trois de mes propositions sont **remplacées** :

- lot transformé né au bon de réception, dans le stock GMC — pas chez le
  galvanisateur (K1) ;
- taux saisi à la main par le commercial, figé à la validation de l'offre
  — pas un taux choisi dans une liste du SUPERADMIN (K5) ;
- aucune délégation active (K8, K16).

Nouveautés :

- prix de revient estimé = (achat TND + transformation TND) ÷ taux +
  transport EUR ; coût de transformation saisi par ligne (K4) ;
- corrections d'inventaire : SUPERADMIN + PV signé par la Direction
  Générale (K17 ; modifie un service de la 5.5) ;
- % GALVA : non renseigné, 0 % (état brut) ou % défini (K20) ;
- GPP × 1,02, jamais cumulé avec GALVA (K19) ;
- avenant : cas 1 (article existant) ou cas 2 (nouvel article) (K21) ;
- devises imposées (K22).

Avant livraison, une relecture indépendante du premier jet de la version
4 a relevé 40 écarts (mots durcis ou omis, choix techniques présentés
comme validés, renvois inexacts) ; tous corrigés dans l'analyse et dans
`docs/BUSINESS_RULES.md` §20 à §22.

Encore ouverts (K14 : ce ne sont pas de nouvelles règles, mais des
questions d'application) :

- O1 : valorisation des quantités ajoutées par avenant (cas 1 : 100 + 20 ;
  cas 2 : nouvel article) ;
- O2 : taux de change d'une ligne ajoutée par avenant ;
- O3 : « validation de l'offre » = devis CONFIRMÉ ?
- O4 : affecter la production attendue d'une transformation en cours
  (exemple 100 / 60 / 40) — proposé en 5.8 ;
- O5 : définition du « commercial autorisé » (rôle ou permission) et
  création des comptes en 5.6 ;
- O6 : supprimée (devenue le choix technique CT7) ;
- O7 : poids saisi à la main hors tonne pour du GALVA/GPP : poids final
  ou poids brut majoré ?
- O8 : portée d'une renégociation de prix (une ligne ou toutes les lignes
  identiques) ;
- O9 : référentiel d'autres emplacements dès la 5.6 ou au premier
  besoin ;
- 10 confirmations C partiellement sans réponse ;
- 15 choix techniques CT1 à CT15, **aucun validé**.

## Important — réalité de l'environnement

Cette session de travail s'exécute dans un environnement cloud isolé et
temporaire (pas directement sur ton PC Windows). La base, le code et les
tests décrits ici ont réellement été exécutés et vérifiés dans cet
environnement. Pour continuer à travailler dessus localement, il faudra
récupérer ces fichiers — transmis en fin de session.

## Aucune décision métier silencieuse

Les seules règles métier ajoutées l'ont été par l'utilisateur lui-même
(validation de l'analyse Phase 5.5, consignée dans
`docs/BUSINESS_RULES.md` §11-§14). Les décisions prises par Claude sont
d'ordre technique (ex. résolution de la configuration, conventions de
paquets, nom du type `CONSOMMATION_TRANSFORMATION`, document source d'une
correction = sa ligne d'audit, horodatage de l'ouverture au 31/12
23:59:59.999) et sont signalées comme telles dans `PROJECT_STATUS.md` et
le rapport de phase, jamais présentées comme des règles métier.

## Problèmes rencontrés

- `mypy` : collision de nom de module (`core/configuration.py` vu à la
  fois comme `configuration` et `core.configuration`) car `core/` n'a pas
  de `__init__.py` — résolu en exécutant `mypy` avec
  `--explicit-package-bases` depuis la racine du projet, sans changer la
  structure de fichiers déjà validée (M.2).
- `mypy` : redéfinition de la variable `handler` dans
  `configurer_logging()` (boucle de nettoyage des anciens handlers, puis
  variable annotée pour le nouveau) — corrigé en renommant la variable de
  boucle en `ancien_handler`.
- Ni l'un ni l'autre n'est un problème métier ; les deux sont documentés
  dans `CHANGELOG.md`.
- Phase 5.3 : `flake8` (non exécuté explicitement en Phase 5.2 avec ce
  seuil de longueur de ligne sur les nouveaux fichiers) a trouvé 7 lignes
  dépassant 100 caractères et 3 problèmes d'indentation de continuation
  dans `core/erreurs.py` et `tests/test_phase5_3.py` — tous corrigés
  (reformulation sur plusieurs lignes), re-vérifiés à zéro erreur. Aucun
  impact sur le comportement, uniquement du style.
- Correction de comptage signalée : le rapport Phase 5.1 indiquait « 11
  types d'action » pour `journal_audit.action` ; le CHECK réel en
  contient **12** (vérifié directement en base pour construire
  `core.audit.ACTIONS_VALIDES`, avec un test qui garde les deux
  synchronisés en permanence).
- Phase 5.4 : `mypy` (installation autonome de cet environnement) ne peut
  résoudre l'import `pytest` sur aucun fichier de test du projet —
  confirmé pré-existant (reproduit à l'identique sur
  `tests/test_phase5_2_infrastructure.py` et `tests/test_phase5_3.py`,
  déjà validés), donc pas une régression de cette phase. `mypy` reste donc
  exécuté uniquement sur le code source dans cet environnement, jamais sur
  les tests — signalé en toute transparence plutôt que silencieusement
  contourné.

- Phase 5.5 (code) : défaut latent découvert dans `core/erreurs.py`
  (Phase 5.3) — voir point 2 de l'étape 5.5 CODE ; corrigé sans modifier
  aucun test existant.
- Phase 5.5 (code) : 150 lignes > 100 caractères signalées par `flake8`
  dans les nouveaux fichiers — reformatées (`ruff format` + découpage des
  chaînes longues), aucun changement de comportement (178/178 après).

## Points ouverts

Phases 5.1 à 5.4 et analyse 5.5 : validées explicitement.

Phase 5.5 — aucun point bloquant. Limite acceptée : un prix plus fin que
le millime dans sa propre unité (ex. 2 500,5005 DT/t) est refusé. Non bloquants : contrôle « seul Mohamed » (Phase 14) ; article oublié dans l'inventaire
initial découvert après la mise en service ; pour la Phase 5.8 : retour
d'un stock d'inventaire initial situé chez un transformateur, débit 1 → N
pièces, coût du lot résultat vs chute. Résolus : FP 120/30 et FP 130/30 ;
ouverture remplacée par l'inventaire initial ; valorisation interne (unité
du CMP §16) ; arrondi (§17) ; tôles (volume × 8 kg/dm³) ; ventes en tonnes
= ventes au poids.

## Prochaine étape exacte

Attendre la **validation finale** de l'analyse Phase 5.6, version 4
(`docs/ANALYSE_PHASE_5_6.md`) : D1 à D6, N1 à N15 et K1 à K22 intégrés
(règles métier §20 à §22). Encore ouverts : O1 à O9 (O6 devenue CT7),
10 confirmations C sans réponse, et les CHOIX TECHNIQUES CT1 à CT15, non
considérés comme validés.
Aucun code, aucune migration avant. Ne pas commencer la 5.7.
