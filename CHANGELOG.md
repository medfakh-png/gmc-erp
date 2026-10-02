# Changelog GMC

Toutes les dates sont celles des sessions de travail, pas nécessairement
celles de validation par l'utilisateur.

## Phase 5.6 — Analyse v10 (barres 12 m / 6 m), décisions L et C, base commune GitHub (02/10/2026)

Documentation seulement : aucun code, aucune migration, aucun test
nouveau, base inchangée. 293 tests réussis, inchangés.

### Ajouté

- **Base commune** : dépôt GitHub privé `medfakh-png/gmc-erp` et copie
  de travail `C:\Users\medfa\GMC-ERP`. `db/gmc.db` retirée du suivi Git
  (fichier régénérable), `.gitignore` ajouté.
- `docs/ANALYSE_PHASE_5_6_v10.md` (version 10.4) : analyse ciblée de la
  règle « 1 barre de 12 m = 2 barres de 6 m », validée (LG1 à LG9,
  Q-COUPE, V10-1 à V10-8).
- `docs/REVUE_PHASE_5_6_L_C.md` : revue détaillée des 22 lectures L et
  des 14 propositions C, telle qu'elle était avant les décisions
  (document historique).
- `docs/DECISIONS_PHASE_5_6_2026-10-02.md` : registre de toutes les
  décisions prises par Mohamed le 02/10/2026.
- `docs/BUSINESS_RULES.md` :
  - §23 : décisions O1 à O9, X1 à X9, Y1 à Y6, CT1 à CT21, P-MULT,
    P-BST, P-ART, P-RET, P-KG-TR (analyses v5 à v9), jusque-là
    consignées seulement dans les analyses ;
  - §24 : règle définitive des barres de 12 m et de 6 m, avec le texte
    validé mot pour mot, le modèle retenu, l'exemple chiffré et les
    quinze tests obligatoires ;
  - §25 : Y6-L, Q-ANNUL, lectures L-a à L-v, propositions C1 à C14 ;
  - §26 : registre des règles remplacées ;
  - §27 : les 8 points encore ouverts de la Phase 5.6.
- Relecture indépendante de la mise à jour contre ses sources : 2 écarts
  de sens et une dizaine d'écarts de formulation, corrigés avant
  l'enregistrement.

### Modifié

- `docs/BUSINESS_RULES.md` §19 à §22 : notes « Mise à jour » ou
  « REMPLACÉ » posées à la place des règles concernées, sans effacer
  l'ancien texte : K2 (remplacée par LG8), D1 point 3, D5 (O4 tranché),
  N3 et K20 (% GALVA saisi sur la ligne), N4 et K19 (GPP = réglage
  global), N5 (transport en KG), N6 et K3 (O1), N14 et K8/K16 (CT1),
  K5 (O3, O5, L-t), K6 et K18 (CT20), K10 (Y5), K14, K21 (Y6 ; transport
  d'une ligne ajoutée : point ouvert), transport (C3, P-KG-TR) ; notes
  aussi aux §8 (transformations), §11 (articles) et §15 (vente en KG).
- `PROJECT_STATUS.md`, `CURRENT_SESSION.md`, `CLAUDE.md` : état au
  02/10/2026, base commune, ordre des travaux validé, écarts connus.

### Constaté (audit en lecture seule, non corrigé)

- Le code de la Phase 5.5 n'applique pas la règle 12 m / 6 m : une barre
  de 12 m est invisible pour une commande de 6 m ; la base accepte un lot
  de 6 m sur une ligne de 12 m ; aucun test ne couvre la règle.
- `docs/DATABASE.md` cite une fonction `cout_sortie()` qui n'existe pas
  sous ce nom (`cout_sortie_minor()`, `cout_sortie_detail()`,
  `cout_sortie_total_minor()`).
- Les documents des Phases 1 à 3 ne sont pas dans le dépôt.

### Non fait (volontairement)

- Aucune migration pour la règle 12 m / 6 m (elle sera dédiée ;
  colonnes ajoutées, aucune table reconstruite, aucune donnée supprimée).
- Rien pour V10-8 tant que la Phase 5.6 n'est pas validée dans son
  ensemble.

## Phase 5.6 — Analyses v5 à v9 (du 30/09 au 02/10/2026)

Documentation seulement : aucun code, aucune migration, base inchangée.
Entrée ajoutée après coup, le 02/10/2026.

- `docs/ANALYSE_PHASE_5_6_v6.md` à `docs/ANALYSE_PHASE_5_6_v9.md` :
  analyses consolidées successives. La v5 n'existe que comme fichier
  remis en conversation ; ses passages utiles sont cités dans la v9.
- Décisions intégrées : O1 à O9, X1 à X9, Y1 à Y5 (30/09/2026) ; CT1 à
  CT21 et Y1 bis (01/10/2026) ; Y6, P-MULT, P-BST, P-ART, P-RET, P-KG-TR
  (02/10/2026).
- La v9 propose une migration 0021 (non créée), 210 cas de test (non
  écrits) et un plan de développement ; elle tient un registre des
  décisions remplacées (H1 à H40).

## Phase 5.6 — Réponses K1 à K22 intégrées, analyse version 4 (30/09/2026)

Documentation seulement : aucun code, aucune migration, base inchangée.

- `docs/BUSINESS_RULES.md` : nouveau §22 (K1 à K22, dont K14) ; arrondi
  par devise au §17 (EUR au centime) ; §19, §20 et §21 alignés (N5
  remplacé par K5 pour le taux ; note K1/K2 sous D5 ; renvois O1 à O9).
- `docs/ANALYSE_PHASE_5_6.md` version 4 :
  - N1 à N15 et K1 à K22 définitifs ;
  - flux de transformation définitif (bon de sortie → situation virtuelle
    → bon de réception → nouveau lot en stock GMC) ;
  - quantités originale, avenants, en vigueur et supplément ;
  - formule et exemples du prix de revient estimé (726,47 EUR ; 4 499,41
    EUR) ;
  - contradictions R1 à R9 (R1, R3 et R9 non tranchées) ;
  - décisions ouvertes O1 à O9 (O6 devenue le choix technique CT7) ;
  - 10 confirmations C sans réponse ;
  - choix techniques CT1 à CT15, aucun validé ;
  - relecture indépendante : 40 écarts relevés et corrigés ;
  - impacts sur le modèle (chaque point marqué validé ou choix technique) ;
  - matrice des droits ;
  - tests définitifs.

## Phase 5.6 — Décisions N1 à N15 intégrées, analyse version 3 (30/09/2026)

Documentation seulement : aucun code, aucune migration, base inchangée.

- `docs/BUSINESS_RULES.md` : §21 (N1 à N15) ; correction de D1 au §20 (un
  lot brut n'est pas GALVA ou GPP avant transformation) ; transport en EUR
  au §19.
- `docs/ANALYSE_PHASE_5_6.md` version 3 :
  - statut de N1 à N15 ;
  - schéma logique revu (la transformation crée un nouveau lot) ;
  - contradictions K1 à K22 (dont K16 à K22 issues d'une relecture
    indépendante, 28 écarts corrigés) ;
  - C1 à C14 au format ID / Question / Proposition / Impact ;
  - incohérences I1 à I31 ;
  - migration 0021 revue : référentiel des poids validés, permission
    « affecter » délégable, auteur du taux, garde-fou étendu aux
    livraisons, affectation sur état exact ;
  - tests complétés (groupes RA, GF, Z).

## Phase 5.6 — Décisions D1 à D6 validées, analyse version 2 (30/09/2026)

Documentation seulement : aucun code, aucune migration, base inchangée.

- `docs/BUSINESS_RULES.md` §20 : décisions D1 à D6 ; note de devise au
  §19.
- `docs/ANALYSE_PHASE_5_6.md` version 2 : section « RÈGLES VALIDÉES — D1
  À D6 » ; schéma logique (stock physique chez GMC et chez le
  galvanisateur, réservation, affectation, transformation, réception) avec
  l'exemple 100, 60, 40 ; catégories A à F ; ambiguïtés N1 à N15 ;
  migration 0021 revue (rôle SUPERADMIN, avenants de commande, emplacement
  des affectations, devises par prix, nature de la masse) ; tests
  complétés (groupes U, X, Y).

## Phase 5.6 — Analyse technique finale livrée (30/09/2026)

Documentation seulement (aucun code, aucune migration, base inchangée :
empreinte identique, 293 tests toujours verts) : `docs/ANALYSE_PHASE_5_6.md`.
Contenu :
- 23 incohérences constatées ;
- proposition de migration 0021 (non créée) ;
- repositories et services, règles de transaction et d'audit ;
- liste des tests et impacts ;
- 6 décisions bloquantes et 14 confirmations rapides en attente.

Les FACT ont été revérifiés par un agent indépendant ; 9 imprécisions ont
été corrigées avant livraison.

## Phase 5.6 — Analyse : décision transport (30/09/2026)

Documentation seulement (aucun code, aucune migration) : règle
`docs/BUSINESS_RULES.md` §19 — transport estimatif au prix par tonne ;
ligne vendue dans une autre unité (pièce, ml…) → prix de transport de la
ligne demandé et saisi manuellement.

## Phase 5.5 — VALIDÉE par l'utilisateur (30/09/2026)

Phase 5.5 (Stock Service) validée explicitement. Démarrage de la Phase 5.6
par son analyse seule (aucun code, aucune migration).

## Phase 5.5 — Dernière correction : prix conservé dans son unité d'origine (Proposition A)

### Ajouté
- `migrations/0020_unite_prix_saisie.sql` : vérification préalable des
  montants existants ; `lot.unite_prix` (kg ↔ tonne admis pour un article
  au poids), `lot.unite_prix_definitif`, `lot.unite_valorisation_article` ;
  contrôle de `inventaire_initial_ligne.unite_cout` ; unités de
  `regularisation_prix_fournisseur` et écart contrôlé par conversion
  exacte ; garde-fou « montant monétaire entier » (38 triggers, 28 colonnes
  `*_minor`). Schéma : 47 tables, 4 vues, 94 triggers, 52 index.
- `db/valorisation.py` : `convertir_prix_exact()`, `ecart_unitaire_exact()`,
  `unite_cout_reel_lot()`, `cout_reel_lot_exact()`.
- `core/unites.py` : `prix_saisi()`, `unites_de_prix_compatibles()`,
  `UNITES_MASSE`, messages « Un prix unitaire n'est jamais arrondi.
  Saisissez le prix avec une précision représentable dans son unité
  d'origine. » (remplace « aucune règle d'arrondi n'est validée »).
- `tests/test_phase5_5_prix_saisis.py` (17 tests).

### Modifié
- Moteur : coût d'entrée et coût réel pris avec l'unité de leur propre prix
  (provisoire ou définitif) ; conversion exacte, arrondi du seul montant
  final.
- Inventaire initial : coût conservé dans son unité saisie (et non plus
  converti à l'enregistrement) ; trace de la conversion et des valeurs
  exacte et arrondie.
- `repositories/stock_repository.py`, `core/erreurs.py` (traductions des
  nouveaux refus), `tests/helpers.py` (régularisation avec unités).
- Tests adaptés : coût d'inventaire saisi à la tonne pour un article au kg
  (désormais conservé à la tonne) ; test de migration 0019 appliquant aussi
  0020.

### Vérifié
- pytest 293/293 ; `--fresh` ×2 (empreinte identique, 20 migrations),
  `integrity_check` ok, `foreign_key_check` 0 anomalie, ré-application sans
  effet ; ruff, flake8, mypy sans erreur sur le périmètre Phase 5.

## Phase 5.5 — Finalisation : arrondi au millime et tôles par volume × densité

Intégration des décisions validées définitivement par l'utilisateur. Aucune
migration. Aucune autre règle métier modifiée ; choix techniques signalés
dans `PROJECT_STATUS.md` (n° 25-28).

### Ajouté
- `core/arrondi.py` : `arrondi_minor()` — millime le plus proche, 0,5 vers
  le haut, une seule fois (implémentation unique pour tous les moteurs).
- `core/unites.py` : `dm`, volumes `dm³`/`m³` (`en_dm3`, `en_m3`), masse
  volumique `kg/dm³`, `en_decimetres()`.
- `db/valorisation.py` : `montant_arrondi_minor()`,
  `cmp_exact_au_moment_du_mouvement()`, `en_texte()`.
- Tests : 6 tests d'arrondi dans `tests/test_phase5_5_valorisation.py`
  (entrée, sortie/CMP à 0,5, chute au CMP exact, coût réel, régularisation,
  inventaire initial), 4 dans `tests/test_phase5_5_unites.py` (arrondi,
  règle unique, conversions dm/dm³/m³, précision conservée).

### Modifié
- Arrondi appliqué une seule fois au montant final : entrée de lot, sortie,
  CMP affiché, coût réel d'affaire, chute (désormais au CMP exact à
  l'envoi), inventaire initial, régularisation, vente au poids
  (`montant_minor_masse_prix`). Refus « montant non exact » retirés
  (`stock_service`, `inventaire_initial_service`, moteur).
- `core/masses_validees.py` : tôle = volume (dm³) × 8 kg/dm³
  (`DENSITE_TOLE_PLANE`), dimensions converties en dm ; plus
  d'interprétation « en grammes ».
- `docs/BUSINESS_RULES.md` : §14 (tôles), §15 (ventes au poids en
  tonnes), nouveau §17 (arrondi) ; `docs/PRIX_REVIENT.md` §6.4.
- Tests adaptés : conversions kg/t (plus de branche de refus), exemple de
  contrôle des tôles (volume au lieu de grammes), conversions des tôles
  (+ dm), inventaire initial (valeur incohérente seulement).

### Vérifié
- pytest 276/276 ; `--fresh` ×2 (empreinte du schéma identique),
  `integrity_check` ok, `foreign_key_check` 0 anomalie, ré-application sans
  effet, exécution directe `python3 db/valorisation.py` ; ruff, flake8,
  mypy (18 fichiers) sans erreur sur le périmètre Phase 5.

## Phase 5.5 — Finalisation : unité du CMP et dimensions des tôles

Intégration des deux décisions validées définitivement par l'utilisateur.
Aucune règle métier créée sans validation ; choix techniques signalés dans
`PROJECT_STATUS.md` (n° 23-25).

### Ajouté
- `migrations/0019_unite_valorisation_article.sql` : historique immuable
  `article_unite_valorisation` (définition initiale, changements datés,
  motivés, avec utilisateur et CMP tracé dans les deux unités) ;
  `lot.unite_prix` (fixée à la création, figée ; lots existants `UNITE`) ;
  `inventaire_initial_ligne.unite_cout` ; cache CMP recréé avec l'unité,
  la quantité dans l'unité et le poids. Schéma : 47 tables, 4 vues, 51
  triggers, 52 index, 19 migrations.
- `services/unite_valorisation_service.py`,
  `repositories/unite_valorisation_repository.py`.
- `core/erreurs.py` : `ErreurUniteValorisation` + traduction des refus de
  la migration 0019.
- `core/unites.py` : `cm`, « unité(s) », prix `/ml`, `/m`, `/unité`,
  `prix_minor_en_unite_valorisation()` (kg ↔ t seulement),
  `en_millimetres()`.
- `core/masses_validees.py` : `calcul_poids_tole_plane()` /
  `poids_tole_plane_kg()` (dimensions en mm, formule inchangée, contrôle
  36 kg).
- `tests/test_phase5_5_valorisation.py` (20 tests) ; 25 tests ajoutés à
  `tests/test_phase5_5_unites.py` (prix dans l'unité de valorisation,
  tôles).

### Modifié
- `db/valorisation.py` : CMP piloté par l'unité de valorisation de l'article
  (au poids pour KG/TONNE, au métrage/à la pièce pour ML/UNITE), unité en
  vigueur à la date de chaque mouvement, calcul pur séparé de l'écriture,
  montants non exacts refusés ; fonctions `*_detail()`, `cmp_actuel()`,
  `unite_prix_lot()`, `calculer_pools()`, `etat_pools_article()`.
- `services/stock_service.py` : entrée en STOCK_GMC de valeur non exacte
  refusée avant enregistrement ; erreurs d'unité et de montant traduites.
- `services/inventaire_initial_service.py` : coût dans l'unité de
  valorisation de l'article.
- `tests/helpers.py` : `seed_referentiels` définit l'unité `UNITE` de
  l'article de test (obligatoire depuis 0019) ; `definir_unite_valorisation`.
- `tests/test_phase5_5_stock.py` : test « coût au kg en attente de
  décision » remplacé par « coût hors unité de l'article refusé » (la
  décision est prise).

### Vérifié
- pytest 268/268 ; `--fresh` (19 migrations), `integrity_check` ok,
  `foreign_key_check` 0 anomalie, ré-application sans effet, reconstruction
  CMP idempotente ; ruff, flake8, mypy sans erreur sur le périmètre Phase 5.

## Phase 5.5 — Corrections/clarifications validées (après le code)

Intégration des règles validées définitivement par l'utilisateur, limitée à
ce qui est nécessaire à la cohérence de la Phase 5.5. Aucune règle métier
créée sans validation.

### Ajouté
- `core/unites.py` : règle « unité obligatoire à la saisie » — lecture
  (« 2 500 kg », « 2,5 t », « 5 DT/kg », « 5 000 DT/tonne », « 12 m »,
  « 10 pièces »), refus d'une saisie sans unité ou ambiguë (« 2.500 kg »),
  saisie d'origine conservée, conversions exactes kg↔t et prix/kg↔prix/t,
  montants exacts (refus plutôt qu'arrondi non validé).
- `core/masses_validees.py` : FP 45/20 = 7,2 ; FP 120/30 = 28,8 ;
  FP 130/30 = 31,2 kg/ml ; comparaison avec la liste MV qui signale sans
  jamais remplacer.
- `migrations/0018_inventaire_initial_demarrage.sql` : `inventaire_initial`
  (unique, instant exact de mise en service) et `inventaire_initial_ligne`
  (avec `saisie_originale` JSON), `lot.inventaire_initial_ligne_id`, type
  `ENTREE_INVENTAIRE_INITIAL` ; remplace l'ouverture au 31/12/N-1 de la
  migration 0017 (non modifiée), données reprises.
- `services/inventaire_initial_service.py`,
  `repositories/inventaire_initial_repository.py`.
- `core/erreurs.py` : `ErreurUniteManquante`, `ErreurSaisieInvalide`,
  `ErreurInventaireInitialInvalide` (remplace `ErreurOuvertureInvalide`).
- `tests/test_phase5_5_unites.py` (36 tests) ; 16 tests d'inventaire
  initial et 1 test de migration 0018 dans `tests/test_phase5_5_stock.py`.

### Modifié
- `services/stock_service.py` : `corriger_inventaire()` exige quantité et
  poids avec unité (saisie tracée dans l'audit) ; horodatages normalisés
  (UTC) ; aucun mouvement daté avant la mise en service ; type
  `ENTREE_INVENTAIRE_INITIAL`.
- `tests/test_phase5_5_stock.py` : 8 appels de `corriger_inventaire`
  adaptés à la saisie avec unité (assertions inchangées) ; 10 tests de
  l'ouverture au 31/12 remplacés (règle annulée par l'utilisateur).

### Supprimé
- `services/stock_ouverture_service.py`,
  `repositories/stock_ouverture_repository.py` (remplacés, jamais validés
  définitivement).

### Signalé (STOP, non modifié)
- « Valorisation interne : kg » face au moteur CMP validé par pièce
  (`db/valorisation.py` inchangé) : décision demandée.

### Non-régression
- 223/223 tests verts (108 Phases 4 à 5.4 inchangés). `--fresh` (18
  migrations), `integrity_check` → `ok`, `foreign_key_check` → aucune
  anomalie ; 46 tables, 4 vues, 45 triggers, 50 index. `ruff`, `flake8`,
  `mypy` : aucune erreur.

## Phase 5.5 — Stock Service : code (après validation de l'analyse)

Implémentation limitée au périmètre validé (§12 de la validation officielle
de l'analyse). Nouvelles règles métier : uniquement celles décidées par
l'utilisateur, consignées dans `docs/BUSINESS_RULES.md` §11-§14.

### Ajouté
- `migrations/0017_stock_service_socle.sql` :
  - **M2** type `CONSOMMATION_TRANSFORMATION` (sortie du lot d'origine de
    chez le transformateur au retour de transformation — fin du stock
    fantôme, constat E1) ;
  - **M3** tables `stock_ouverture` et `stock_ouverture_ligne` (immuables,
    `cree_par` obligatoire, valeur = pièces × coût unitaire), type
    `ENTREE_STOCK_OUVERTURE`, `lot.stock_ouverture_ligne_id` (exactement
    une origine par lot) ;
  - **M1** index uniques `ux_mouvement_entree_origine_par_lot` et
    `ux_mouvement_type_par_document` (constats E2 et E4).
  Reconstruction de `lot` et `mouvement_stock` (technique de la migration
  0016), index et triggers recréés à l'identique.
- `services/stock_service.py` : consultations, disponibilité, quantité
  affectable, historique, contrôle de conservation,
  `enregistrer_mouvement()`, `enregistrer_retour_transformation()`,
  `corriger_inventaire()`, `reconstruire_cmp_apres_transaction()`.
- `services/stock_ouverture_service.py` : `creer_stock_ouverture()`,
  `ajouter_ligne_ouverture()`, `lignes_ouverture()`.
- `repositories/stock_repository.py`, `stock_ouverture_repository.py`,
  `article_repository.py` (lecture seule) ; `repositories/base.py` :
  `un_dict()`, `des_dicts()`.
- `core/erreurs.py` : `ErreurQuantiteInvalide`, `ErreurEmplacementInvalide`,
  `ErreurMouvementIncoherent`, `ErreurDocumentSourceManquant`,
  `ErreurMouvementEnDouble`, `ErreurMotifObligatoire`,
  `ErreurDisponibiliteInsuffisante`, `ErreurMontantIncoherent`,
  `ErreurOuvertureInvalide`.
- `tests/test_phase5_5_stock.py` : 70 tests.

### Corrigé (technique, pas métier)
- `core/erreurs.py:traduire_erreur_sqlite()` (Phase 5.3) ne reconnaissait
  que les **noms** des triggers, alors qu'une `IntegrityError` levée par
  `RAISE(ABORT, ...)` ne contient que le **texte** du RAISE : en conditions
  réelles, toutes les erreurs tombaient sur le repli générique. Les vrais
  messages sont désormais reconnus (preuve :
  `test_traduction_des_vraies_erreurs_de_la_base`) ; la reconnaissance par
  nom est conservée, les tests Phase 5.3 sont inchangés.

### Documenté
- `CLAUDE.md` : règle 7 (cycle Analyse → Validation humaine → Code →
  Tests → Rapport → Validation finale) et carte du code.
- `docs/BUSINESS_RULES.md` §11-§14, `docs/DATABASE.md` (migration 0017,
  tableau type ↔ emplacements ↔ document), `docs/STOCK_RULES.md` §1.1.

### Vérifié
- `--fresh` (17 migrations), `PRAGMA integrity_check` → `ok`,
  `PRAGMA foreign_key_check` → aucune anomalie ; schéma 46 tables, 4 vues,
  45 triggers, 50 index. `ruff`, `flake8 --max-line-length=100`, `mypy
  --explicit-package-bases` (code source) : aucune erreur.

### Non-régression
- 178/178 tests verts (108 existants inchangés + 70 nouveaux).

## Phase 5.5 — Stock Service : analyse (aucun code, aucune migration)

Première sous-phase soumise au nouveau cycle obligatoire ANALYSE →
VALIDATION HUMAINE → CODE → TESTS → RAPPORT → VALIDATION FINALE.

### Documenté
- Règle de méthode et nouvelle règle métier « catalogue articles »
  consignées dans `PROJECT_STATUS.md` / `CURRENT_SESSION.md` (non codées).
- Rapport d'analyse du Stock Service remis en conversation : état du
  référentiel articles (origine et anomalies de la liste MV), état du
  moteur stock, architecture proposée, anti-double-comptage, transactions,
  erreurs, tests, modifications DB éventuelles, points à valider.

### Constaté (prouvé sur bases jetables, jamais sur `db/gmc.db`)
- 11 sondes exécutées : solde résiduel chez le transformateur après retour,
  double entrée de réception acceptée, double sortie de livraison acceptée,
  affectation au-delà du physique acceptée, article modifiable/supprimable,
  doublons d'articles acceptés, COMMIT intempestif de `reconstruire_cmp()`
  dans une transaction ouverte, stock d'ouverture impossible, correction
  d'inventaire sans motif acceptée, emplacement inconnu accepté, débit
  1 → 2 pièces refusé. Aucun correctif appliqué — propositions soumises à
  validation.

### Non-régression
- Aucun fichier de code, de test ou de migration modifié. 108/108 tests
  verts, `PRAGMA integrity_check` → `ok`, `PRAGMA foreign_key_check` →
  aucune anomalie, schéma inchangé (44 tables, 4 vues, 41 triggers,
  46 index, 16 migrations).

## Phase 5.4 — Numérotation documentaire

Aucun cadrage détaillé fourni pour cette sous-phase (contrairement à
5.2/5.3) — reformulation faite avant codage (voir `CURRENT_SESSION.md`),
appuyée uniquement sur des décisions déjà validées (format et 10 types de
document, Phase 2/4). Aucune nouvelle règle métier, aucune modification de
la base de données.

### Ajouté
- `core/numerotation.py` (nouveau) : `prochain_numero(conn, type_document,
  annee=None) -> str` — génère le numéro humain séquentiel au format déjà
  validé (`DEV-2026-0001`, etc.), `annee` par défaut = année civile en
  cours. `TYPES_DOCUMENT_VALIDES` (10 préfixes : DEV, CMD, BCF, BLF, FFO,
  BCT, BST, RTR, BLC, FAC — identiques à `docs/BUSINESS_RULES.md` et au
  commentaire de `migrations/0002_numerotation.sql`) ; `ValueError` levée
  avant tout accès DB si le type est invalide. `dernier_numero_attribue()`
  (lecture seule, diagnostic). N'ouvre jamais sa propre transaction —
  participe à celle de l'appelant, comme `core.audit.enregistrer()`
  (Phase 5.3) : un rollback annule aussi l'incrémentation du compteur, qui
  n'est donc jamais "brûlée" par une écriture qui n'a finalement pas eu
  lieu (le numéro repris est alors identique à celui de la tentative
  annulée — preuve par test dédié).
- `repositories/numerotation_repository.py` (nouveau) :
  `incrementer_et_obtenir()` (upsert atomique en une seule instruction SQL
  avec clause `RETURNING`, sur `compteur_numerotation` — table en place
  depuis la migration 0002, Phase 4, inchangée), `obtenir()` (lecture
  seule).
- `repositories/base.py` (modifié) : ajout de `executer_et_retourner()`
  (aide générique pour toute écriture avec clause `RETURNING`, même
  traduction d'erreur que `executer()`) — utilisée par
  `numerotation_repository.py`, réutilisable par tout futur repository.
- `tests/test_phase5_4_numerotation.py` (nouveau, 26 tests) : format et
  incrémentation (4), isolation des compteurs par type et par année (2),
  année par défaut (1), validation du type de document (13, dont un test
  paramétré sur les 10 types valides + garde-fou "exactement 10 types"),
  intégration avec `db.connexion.transaction()` (3 tests décisifs : commit
  définitif, rollback qui redonne le même numéro, numérotation partageant
  la transaction d'une autre écriture simulée), lecture seule (2),
  repository (2 par recoupement direct, incluses dans les 13 précédentes).

### Vérifié (technique)
- `ruff check` et `flake8 --max-line-length=100` : aucune erreur sur les
  fichiers créés/modifiés.
- `mypy --explicit-package-bases` sur les fichiers source (hors tests) :
  aucune erreur. Limitation confirmée, pré-existante et non spécifique à
  cette phase : l'installation autonome de `mypy` dans cet environnement
  ne peut pas résoudre l'import `pytest` (aucun stub trouvé) sur AUCUN
  fichier de test du projet — reproduit à l'identique sur
  `tests/test_phase5_2_infrastructure.py` et `tests/test_phase5_3.py`
  (déjà validés), donc pas une régression introduite ici. `mypy` reste
  donc exécuté uniquement sur le code source, jamais sur les tests, dans
  cet environnement.
- `--fresh` reproductible (16 migrations, aucune nouvelle). `PRAGMA
  integrity_check` → `ok`. `PRAGMA foreign_key_check` → aucune anomalie.
  Schéma inchangé : 44 tables, 4 vues, 41 triggers, 46 index — aucun
  fichier `migrations/*.sql` créé ni modifié.

### Non-régression
- 108/108 tests verts (82 tests Phase 4/4.1/5.2/5.3 inchangés + 26
  nouveaux tests Phase 5.4).

## Phase 5.3 — Repositories + erreurs métier + audit

Aucune nouvelle règle métier, aucune modification de la base de données.
Livre le socle transverse (erreurs, accès SQL structuré, audit) que les
futurs services métier (Phase 5.5+) réutiliseront.

### Ajouté
- `core/erreurs.py` (nouveau) : hiérarchie `ErreurMetier` — 6 sous-classes
  ciblées (`ErreurStockInsuffisant`, `ErreurPlafondDepasse`,
  `ErreurReaffectationInvalide`, `ErreurEnregistrementImmuable`,
  `ErreurDeviseMelangee`, `ErreurEnregistrementIntrouvable`) + repli
  générique `ErreurRegleViolee`. `traduire_erreur_sqlite(exc)` traduit une
  `sqlite3.IntegrityError` en `ErreurMetier` avec message français,
  reconnaissant explicitement 8 triggers réels de la base
  (`trg_mouvement_solde_source`, `trg_affectation_plafond`,
  `trg_bl_client_ligne_plafond`, `trg_reception_transfo_plafond`,
  `trg_reaffectation_origine_active`, `trg_reaffectation_cloture_origine`,
  `trg_commande_ligne_qte_immuable`, `trg_lot_no_update_quantite`), plus
  une reconnaissance générique par motif (`_no_delete`/`_no_update`) pour
  les autres triggers d'immuabilité, et un repli final qui conserve
  toujours le message technique d'origine.
- `repositories/base.py` (nouveau) : `executer()` (traduit toute
  `IntegrityError` via `core.erreurs`), `un_ou_aucun()`, `tous()` — base
  commune réutilisable par tout futur repository.
- `repositories/audit_repository.py` (nouveau) : accès SQL structuré à
  `journal_audit` — `inserer`, `obtenir`, `lister_pour_entite`,
  `lister_pour_affaire`. N'expose ni mise à jour ni suppression (la table
  est totalement immuable en base depuis la Phase 4).
- `core/audit.py` (nouveau) : service d'audit. `ACTIONS_VALIDES` (12
  valeurs, identiques au CHECK de `journal_audit.action`).
  `enregistrer()` valide l'action en Python avant tout accès DB (message
  clair plutôt que le rejet brut d'une contrainte CHECK), sérialise
  `avant`/`apres` en JSON (`json.dumps`, accepte aussi une chaîne déjà
  sérialisée), et **exécute un simple INSERT sur la connexion fournie**
  sans jamais ouvrir sa propre transaction — pour permettre à l'appelant
  de le regrouper avec son écriture métier dans un seul
  `db.connexion.transaction(conn)` (Phase 5.2). `historique_entite()`,
  `historique_affaire()`.
- `tests/test_phase5_3.py` (nouveau, 32 tests) : hiérarchie d'erreurs (7),
  traduction SQLite→métier pour les 8 triggers connus + les cas génériques
  + le repli (11), `repositories/base.py` (3), `repositories/
  audit_repository.py` (3), `core/audit.py` (6, dont la sérialisation JSON
  et le rejet précoce d'une action invalide), garde-fou anti-dérive entre
  `ACTIONS_VALIDES` et le CHECK réel de la base (1), intégration avec
  `db.connexion.transaction()` (2 tests décisifs : commit conjoint d'une
  écriture métier simulée et de son audit, rollback conjoint des deux en
  cas d'exception).

### Corrigé (technique, pas métier)
- 7 anomalies de style trouvées par `flake8` (lignes > 100 caractères,
  indentation de continuation) dans `core/erreurs.py` et
  `tests/test_phase5_3.py`, corrigées par reformulation multi-lignes.
  Aucun impact sur le comportement.
- Correction de comptage (signalée en toute transparence) : le rapport de
  Phase 5.1 indiquait « 11 types d'action » pour `journal_audit.action` ;
  le CHECK réel en base en contient **12** — vérifié directement pour
  construire `core.audit.ACTIONS_VALIDES`, avec un test qui garantit que
  les deux ne peuvent plus diverger silencieusement à l'avenir.

### Non-régression
- 82/82 tests verts (50 tests Phase 4/4.1/5.2 inchangés + 32 nouveaux
  tests Phase 5.3). `--fresh` reproductible. `PRAGMA integrity_check` →
  `ok`. `PRAGMA foreign_key_check` → aucune anomalie. Schéma inchangé : 44
  tables, 4 vues, 41 triggers, 46 index.

## Phase 5.2 — Configuration + connexion DB + infrastructure

Aucune nouvelle règle métier, aucune modification de la base de données.
Livre uniquement le socle technique nécessaire aux futurs services métier.

### Ajouté
- `core/configuration.py` (nouveau) : configuration centralisée
  (`Configuration`, dataclass immuable) — chemin de la base SQLite,
  environnement (`development`/`test`/`production`), niveau et destination
  des logs. `configuration_par_defaut()`, `configuration_test(db_path)`,
  `charger_configuration()` (résolution via les variables d'environnement
  `GMC_ENV`/`GMC_DB_PATH`/`GMC_LOG_LEVEL`/`GMC_LOG_FILE`, avec repli sur un
  défaut calculé depuis l'emplacement du module — jamais depuis le
  répertoire courant du processus). `configurer_logging()` (logger
  technique `gmc`, idempotent) et `obtenir_logger()`.
- `db/connexion.py` (nouveau) : `get_connection(config=None)` — réutilise
  `db/migrate.py:get_connection` (donc `PRAGMA foreign_keys=ON` +
  `PRAGMA journal_mode=WAL` déjà validés, aucune duplication de cette
  logique) et résout la configuration active si aucune n'est fournie.
  `transaction(conn)` — context manager générique (commit si succès,
  rollback + relance de l'exception d'origine sinon) que les futurs
  services (Phase 5.3+) réutiliseront pour regrouper plusieurs écritures
  en une seule unité atomique. `fermer(conn)` — fermeture explicite avec
  log.
- `tests/test_phase5_2_infrastructure.py` (nouveau, 19 tests) :
  configuration (7 tests), connexion (4 tests), transaction (4 tests),
  logging (4 tests). Aucun test métier — uniquement l'infrastructure.

### Vérifié (technique)
- `ruff`, `flake8` et `mypy` exécutés sur les fichiers créés (aucun
  n'était mentionné comme déjà utilisé sur le projet — vérifiés présents
  dans l'environnement avant exécution, résultats réels rapportés, jamais
  supposés). Deux anomalies réelles trouvées et corrigées :
  - une variable de test assignée sans être utilisée (`tx` dans
    `test_transaction_propage_exception_d_origine`) ;
  - une redéfinition de nom détectée par `mypy` dans
    `configurer_logging()` (variable de boucle `handler` puis variable
    annotée `handler` réutilisée pour le nouveau handler) — corrigé en
    renommant la variable de boucle en `ancien_handler`.
  Après correction : `ruff check` et `flake8` sans erreur, `mypy
  --explicit-package-bases` sans erreur (nécessaire car `core/` n'a pas de
  `__init__.py`, cohérent avec la convention déjà en place pour `db/`).
- `db/migrate.py` et `db/valorisation.py` **non modifiés** — réutilisés
  tels quels (rétrocompatibilité vérifiée : `--fresh`, migrations, tests
  existants tous au vert après création des nouveaux fichiers).

### Non-régression
- 50/50 tests verts (31 tests Phase 4/4.1 inchangés + 19 nouveaux tests
  Phase 5.2). `--fresh` reproductible. `PRAGMA integrity_check` → `ok`.
  `PRAGMA foreign_key_check` → aucune anomalie. Schéma inchangé : 44
  tables, 4 vues, 41 triggers, 46 index — identique à la Phase 4.1.

## Phase 4.1 — Phase corrective (montants entiers, coût final fournisseur, chutes)

Aucune nouvelle fonctionnalité métier. Corrige et verrouille des points
techniques de la Phase 4, à la demande explicite de l'utilisateur.

### Ajouté
- `migrations/0016_devise_montants_minor.sql` : convertit **tous** les
  montants financiers de `REAL` vers `INTEGER` en unité monétaire minimale
  (millime TND / centime EUR / cent USD), avec une colonne `devise`
  explicite sur chaque table concernée (17 tables reconstruites). Ajoute la
  vue `v_bilan_chutes_annuel` (bilan consolidé annuel des coûts de chutes,
  par année et par devise). Base vide de données métier au moment de la
  migration (vérifié) — conversion sans perte par construction, écrite
  comme une vraie migration de données.
- `docs/PRIX_REVIENT.md` (nouveau) : représentation monétaire, coût d'entrée
  d'un lot, règle définitive de régularisation fournisseur (coût final après
  facture), référence complète de `db/valorisation.py`.
- `docs/STOCK_RULES.md` (nouveau) : mécanique du registre de stock, règle
  définitive des chutes (valorisation, traçabilité, exclusion de la marge
  individuelle, bilan consolidé annuel), checklist d'intégrité de la base.
- `tests/test_phase41.py` (nouveau, 10 tests) : 3 devises (TND/EUR/USD) +
  garde-fou anti-mélange de devises sur un pool CMP + 4 tests de la règle
  des chutes (valorisée au CMP, sortie du stock normal, traçabilité par
  affaire/article/transformation/date, absence d'impact sur la marge
  individuelle, consolidation annuelle).
- `tests/test_scenarios.py::test_6bis_...` (nouveau) : régularisation
  fournisseur sur un lot **partiellement** sorti (le 3e des 3 états de lot
  exigés par le cadrage, en plus de « totalement en stock » et « totalement
  sorti », déjà couverts par les tests 5 et 6 existants).
- `tests/helpers.py:regulariser_facture_fournisseur()` (nouveau) : construit
  facture fournisseur + régularisation, applique automatiquement la règle
  définitive (`lot_deja_sorti` → `impact_analytique` → mise à jour ou non de
  `lot.prix_unitaire_definitif_minor`).

### Changé (règle métier, décidée par l'utilisateur — tranche un point resté ouvert depuis la Phase 1)
- **Traitement comptable des chutes, définitif.** Le coût CMP d'une chute
  n'est **jamais** intégré à la marge individuelle d'une affaire
  (`chute.impact_marge_valide` reste à `0` en permanence) ; il alimente
  exclusivement un **bilan consolidé annuel**, toutes affaires confondues
  (`v_bilan_chutes_annuel`). Ce n'est plus un point ouvert.
- **Coût final d'un lot après facture fournisseur.** Si le lot n'est pas
  encore sorti au moment de la facture, son coût final devient le prix
  facturé et **le CMP du pool est reconstruit avec ce coût final** (plus
  jamais avec le prix BL provisoire pour ce lot). Si le lot est déjà sorti
  (totalement ou partiellement), la régularisation reste un écart séparé,
  jamais rétroactif — règle déjà validée en Phase 3/4, prolongée
  explicitement au cas « partiellement sorti » et prouvée par un test dédié.

### Corrigé (technique, pas métier)
- **Tous les montants financiers** : `REAL`/`FLOAT` → `INTEGER` (unité
  monétaire minimale) + `devise` explicite. Élimine tout risque de dérive
  d'arrondi flottant sur les prix, coûts, montants de facture et écarts de
  régularisation. Voir `docs/PRIX_REVIENT.md` §1.
- `db/valorisation.py` réécrit en arithmétique entière pure (aucun `float`
  dans le module). Le solde d'un pool CMP n'est plus mis à jour en
  multipliant un prix unitaire arrondi par une quantité, mais par un retrait
  proportionnel **exact** sur le total courant — garantit qu'un pool
  entièrement vidé retombe à exactement 0, sans résidu d'arrondi. Le montant
  exact de chaque mouvement est conservé (`cmp_historique.montant_mouvement_minor`,
  signé) et relu tel quel, jamais recalculé après coup.
- `chute.cout_cmp_unitaire` et `bl_client_ligne.cout_cmp_unitaire` renommées
  `cout_cmp_total_minor` : ces colonnes stockaient déjà, dans les faits, un
  usage ambigu entre prix unitaire et montant ; elles sont maintenant
  explicitement des **montants totaux**, exacts par construction. Toutes les
  fonctions de `db/valorisation.py` qui renvoient un montant portent
  désormais le suffixe `_minor` (ex. `cout_reel_lot` →
  `cout_reel_lot_minor`, `cout_sortie` → `cout_sortie_minor` +
  `cout_sortie_total_minor`, `cout_chute` → `cout_chute_unitaire_minor` +
  `cout_chute_total_minor`) — renommage exhaustif, documenté et repris dans
  tous les tests, pour qu'aucun code futur ne puisse confondre un entier
  « unité minimale » avec une valeur décimale.
- Garde-fou ajouté dans `reconstruire_cmp()` : refuse (`ValueError`) plutôt
  que de mélanger silencieusement deux devises dans le total d'un même pool
  CMP.

### Non-régression
- 31/31 tests verts (20 tests Phase 4 adaptés à la nouvelle représentation
  monétaire, aucun supprimé, + 1 test ajouté aux scénarios obligatoires + 10
  nouveaux tests Phase 4.1). `--fresh` reproductible (deux reconstructions
  indépendantes, résultats identiques). `PRAGMA integrity_check` → `ok`,
  `PRAGMA foreign_key_check` → aucune anomalie.

## Phase 4 — Base de données réelle

### Ajouté
- 15 migrations SQL (`migrations/0001_*.sql` à `0015_*.sql`) : schéma complet
  (44 tables, 3 vues, 41 triggers, 46 index).
- `db/migrate.py` — exécuteur de migrations, idempotent, avec option
  `--fresh` pour une reconstruction complète et vérifiable.
- `db/valorisation.py` — moteur de calcul CMP (coût moyen pondéré),
  implémentant les 4 règles de valorisation définitives.
- `tests/` — 20 tests automatisés (11 scénarios obligatoires + 9 tests de
  contraintes d'intégrité), tous verts.
- `CLAUDE.md`, `PROJECT_STATUS.md`, `CURRENT_SESSION.md`,
  `docs/DATABASE.md`, `docs/BUSINESS_RULES.md`.

### Changé (règle métier, décidée par l'utilisateur)
- **Valorisation du stock général : FIFO → CMP.** Le FIFO proposé en
  Phase 2/3 est officiellement abandonné. Coût réel du lot conservé pour les
  quantités affectées à une affaire (inchangé) ; CMP au moment de la sortie
  pour les suppléments et les chutes (nouveau).

### Corrigé (technique, pas métier — trouvé en écrivant les tests)
- `cmp_historique` rendue à tort immuable en Phase 4 initiale : corrigé pour
  rester un cache pleinement reconstructible.
- `v_stock_non_affecte_par_lot` : double-comptage d'une quantité affectée
  déjà physiquement livrée, corrigé.
- `trg_affectation_plafond` : ne compte plus que les affectations actives
  (plus les clôturées), pour permettre une réaffectation à 100% d'un lot
  déjà entièrement affecté.
- `trg_reaffectation_origine_active` : la protection "affectation encore
  active" (devenue incompatible avec le point précédent) a été remplacée par
  deux protections plus précises : impossible de réaffecter une affectation
  déjà physiquement livrée, impossible de réaffecter deux fois la même
  origine.
- `db/valorisation.py::reconstruire_cmp` : le CMP d'un pool ne retombe plus
  à zéro quand une sortie le vide complètement (il conserve le dernier CMP
  connu, mathématiquement correct et nécessaire pour valoriser correctement
  les chutes et suppléments qui épuisent un pool).

## Phase 3 — Modèle de données détaillé

### Ajouté
- Dictionnaire de données complet pour 23 tables + tables de support,
  conventions, modèle relationnel, 7 scénarios anti-double-comptage
  démontrés avec données concrètes.

### Validé par l'utilisateur
- Régularisation d'un lot déjà vendu : écart séparé, jamais rétroactif.
- UUID interne + numéros humains lisibles par document.
- Numérotation automatique séquentielle, distincte par type de document.
- Stock : registre append-only comme source de vérité exclusive, cache
  autorisé mais toujours reconstructible.
- Chutes enregistrées et traçables, traitement comptable laissé ouvert.

## Phase 2 — Architecture technique

### Ajouté
- Architecture 4 couches, séparation Document / Mouvement physique /
  Affectation / Événement financier, dictionnaire de données par domaine,
  mécanisme de régularisation fournisseur, 8 tests d'architecture
  obligatoires.

### Validé par l'utilisateur
- Valorisation initiale : coût réel du lot affecté / FIFO pour le stock
  général (remplacé par CMP en Phase 4, voir plus haut).
- Coût d'entrée d'un lot : prix BL provisoire, prix facture définitif,
  toujours conservés séparément.
- Stock disponible pour supplément : uniquement stock GMC non affecté.
- Livraison GMC : livré = facturé.

## Phase 1 — Analyse fonctionnelle

### Ajouté
- Analyse fonctionnelle complète (§0-§28), publiée comme document de
  référence.
