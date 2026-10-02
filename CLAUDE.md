# GMC — Instructions pour toute session Claude Code future

Ce fichier est le point d'entrée obligatoire de toute session future sur ce
projet. Lis-le en entier avant de toucher au code.

## Ce qu'est ce projet

Un logiciel de gestion (ERP local, mono-poste, usage interne) pour **Global
Metal Company (GMC)**, filiale tunisienne du groupe INTERMETAL-PROSID-SNCI,
négociant en tubes et profilés métalliques. Le logiciel couvre : stock,
achats, ventes, transformations (galvanisation/GPP/débit) chez des
sous-traitants, conformité MACF/CBAM, et un tableau de bord.

Interlocuteur : Mohamed Fakhfakh (directeur export), **non développeur** —
toute explication technique doit être donnée en langage clair, jamais en
jargon non expliqué.

## Méthodologie — RÈGLES ABSOLUES, ne jamais déroger

1. **Jamais de code sans analyse préalable.** Besoin → règle métier →
   architecture → dépendances → risques → seulement ensuite le code.
2. **Base de données locale** (SQLite), jamais cloud — décision validée et
   justifiée en Phase 2, ne pas remettre en cause sans qu'on te le demande.
3. **Roadmap stricte en 16 phases** (voir PROJECT_STATUS.md pour l'état
   actuel) : 1-Analyse fonctionnelle, 2-Architecture technique, 3-Modèle de
   données, 4-Base de données, 5-Backend, 6-Frontend, 7-Stock, 8-Achats,
   9-Ventes, 10-Transformations, 11-MACF, 12-Dashboard, 13-Import/export,
   14-Sécurité/audit, 15-Tests, 16-Packaging Windows.
4. **Jamais de règle MACF inventée.** Les seuils, taux, et obligations MACF
   réels doivent être fournis par l'utilisateur ou vérifiés à une source
   officielle — jamais supposés.
5. **Documentation progressive obligatoire**, tenue à jour à chaque phase :
   README.md, ARCHITECTURE.md, DATABASE.md, BUSINESS_RULES.md, MACF.md,
   INSTALLATION.md, USER_GUIDE.md, TESTS.md, CHANGELOG.md (dans `docs/` sauf
   CHANGELOG.md à la racine).
6. **Validation explicite obligatoire entre phases.** Ne jamais enchaîner sur
   la phase suivante sans un message de validation explicite de
   l'utilisateur. Si une décision métier réellement nécessaire manque :
   **ARRÊTE-TOI et demande**, ne décide jamais silencieusement à sa place.
   Une clarification purement technique (comment implémenter une règle déjà
   validée) reste de ton ressort, mais doit être signalée clairement, jamais
   présentée comme si elle allait de soi.
7. **Cycle obligatoire de toute sous-phase (depuis la Phase 5.5)** :
   **ANALYSE → VALIDATION HUMAINE → CODE → TESTS → RAPPORT → VALIDATION
   FINALE.** Jamais de passage direct de l'analyse au code. Pendant
   l'analyse : lire les documents, inspecter le code et le schéma réels,
   identifier besoins, dépendances et ambiguïtés, proposer architecture,
   tests et modifications DB — mais aucun code métier, aucune migration,
   aucune modification du schéma, aucun changement fonctionnel ; puis
   attendre la validation explicite. Après validation : implémenter
   uniquement ce qui a été validé. Si une nouvelle décision métier apparaît
   pendant le développement : **STOP**, présenter FACT / PROPOSITION /
   IMPACT / POINT À VALIDER, et attendre la validation avant de continuer
   sur ce point. Chaque rapport classe ses affirmations en FACT /
   PROPOSITION / DÉCISION VALIDÉE / POINT OUVERT, et ne déclare jamais PASS
   sans preuve réelle (commande et résultat réels).

## Où trouver quoi

- `migrations/*.sql` — schéma de la base, un fichier par étape, jamais
  modifié après application (une correction = une nouvelle migration, jamais
  une édition d'un fichier déjà appliqué — cf. `0015_corrections_*.sql` pour
  un exemple réel de correction ainsi traitée).
- `db/migrate.py` — exécuteur de migrations (`python3 db/migrate.py`,
  `--fresh` pour une reconstruction complète depuis zéro, utile pour prouver
  la reproductibilité).
- `db/valorisation.py` — moteur de calcul du CMP (coût moyen pondéré), voir
  `docs/DATABASE.md` pour son fonctionnement détaillé. `reconstruire_cmp()`
  fait un COMMIT interne : ne jamais l'appeler dans une transaction ouverte
  (utiliser `stock_service.reconstruire_cmp_apres_transaction()`).
- `db/connexion.py` — connexion SQLite + `transaction(conn)` (Phase 5.2).
- `core/` — configuration, erreurs métier françaises (`erreurs.py`), audit
  (`audit.py`), numérotation documentaire (`numerotation.py`), règle
  d'arrondi monétaire unique (`arrondi.py`).
- `repositories/` — accès SQL structuré, sans logique métier (dont
  `stock_repository.py`, `inventaire_initial_repository.py`,
  `article_repository.py` en lecture seule).
- `services/` — services métier : `stock_service.py` (Phase 5.5 : seule
  voie d'écriture dans le registre des mouvements),
  `inventaire_initial_service.py` et `unite_valorisation_service.py`
  (unité de valorisation des articles et son historique).
- `core/unites.py` — règle « unité obligatoire à la saisie » (lecture,
  conversions exactes kg↔t, mm/cm/m, prix dans l'unité de valorisation,
  volumes dm³/m³, montants) ; `core/masses_validees.py` — masses linéiques
  validées (FP) et poids des tôles planes (volume dm³ × 8 kg/dm³).
- `db/gmc.db` — la base réelle (ignorée par git si un dépôt est initialisé un
  jour ; c'est un fichier binaire régénérable par `migrate.py`).
- `tests/` — tests pytest (`python3 -m pytest tests/ -v` ou
  `/root/.local/bin/pytest tests/ -v` selon l'environnement).
- `docs/DATABASE.md` — dictionnaire de données réel + design du moteur CMP.
- `docs/BUSINESS_RULES.md` — règles métier validées, à jour (référence
  unique — ne jamais laisser une règle métier vivre uniquement dans un
  message de conversation).
- `docs/PRIX_REVIENT.md` (Phase 4.1) — coût d'un lot, régularisation
  fournisseur (règle définitive), représentation monétaire (entiers +
  devise TND/EUR/USD).
- `docs/STOCK_RULES.md` (Phase 4.1) — mécanique du registre de stock, règle
  définitive des chutes (valorisation, traçabilité, exclusion de la marge
  individuelle, bilan consolidé annuel), checklist d'intégrité de la base.
- `PROJECT_STATUS.md` — où en est le projet, phase par phase.
- `CURRENT_SESSION.md` — ce qui s'est passé à la toute dernière session de
  travail (à relire en premier en reprenant le travail).
- `CHANGELOG.md` — historique daté des changements significatifs.

## Repères techniques essentiels (ne jamais réinventer sans validation)

- **Montants financiers (définitif depuis la Phase 4.1)** : jamais de
  `REAL`/`FLOAT`. Toujours un entier en unité monétaire minimale (millime
  TND = 1/1000, centime EUR/USD = 1/100), colonne `<nom>_minor`, toujours
  accompagnée d'une colonne `devise`. Un pool CMP ne mélange jamais deux
  devises. Détail complet : `docs/PRIX_REVIENT.md` §1. Les quantités
  physiques (poids, longueur) et pourcentages restent en `REAL`.
- **Valorisation (définitive depuis la Phase 4, remplace le FIFO des Phases
  2/3)** : stock général GMC → CMP par pool (article, finition, longueur) ;
  quantité normale affectée à une affaire → coût réel du lot ; quantité
  supplémentaire → CMP au moment de la sortie ; chute → CMP au moment de la
  sortie (= au moment où la matière a quitté GMC pour la transformation).
  Détails dans `docs/BUSINESS_RULES.md` et `docs/DATABASE.md`.
- **Le registre `mouvement_stock` est la seule source de vérité du stock**,
  append-only, jamais modifié ni supprimé. Tout le reste (soldes, CMP) est
  un cache reconstructible depuis ce registre. Un transformateur est un
  emplacement physique réel du stock GMC ; un retour de transformation
  s'enregistre toujours par paire (entrée du lot résultat + sortie du lot
  d'origine de chez le transformateur) — jamais de stock fantôme.
- **Inventaire initial de démarrage (Phase 5.5)** : origine de stock
  spécifique, jamais un achat, à l'instant exact de mise en service,
  unique ; le 31/12/2025 n'est PAS l'ouverture automatique de 2026.
  Ensuite, chaque fin d'année : inventaire physique + rapprochement →
  ouverture de l'année suivante (par corrections tracées).
- **Unité obligatoire à la saisie (Phase 5.5)** : jamais d'unité devinée ;
  saisie d'origine conservée ; kg pour les masses physiques, tonnes pour
  les ventes au poids (`core/unites.py`).
- **Unité du CMP (Phase 5.5, règle définitive)** : le CMP et les coûts de
  lot sont exprimés dans l'unité de valorisation de l'article (DT/kg,
  DT/ml, DT/unité, DT/tonne) — jamais imposés en DT/kg, jamais d'unité par
  défaut. Historique immuable `article_unite_valorisation` ; chaque
  mouvement valorisé dans l'unité en vigueur à sa date
  (`docs/PRIX_REVIENT.md` §6).
- **Prix conservé dans son unité d'origine (Phase 5.5, « Proposition A »)** :
  le lot garde le prix saisi et son unité (`lot.unite_prix`,
  `lot.unite_prix_definitif`, kg ↔ tonne admis pour un article au poids) et
  l'unité de l'article à sa création (`lot.unite_valorisation_article`) ;
  conversion exacte au calcul seulement (`convertir_prix_exact`), jamais de
  prix converti arrondi. Quatre notions distinctes : unité de valorisation,
  unité du prix saisi, unité physique, unité de calcul
  (`docs/BUSINESS_RULES.md` §18).
- **Arrondi monétaire (Phase 5.5, règle définitive)** : millime le plus
  proche, 0,5 vers le haut, une seule fois sur le montant final ; aucun
  sous-calcul arrondi (précision exacte conservée) ; implémentation unique
  `core/arrondi.py`. Une valeur saisie n'est jamais arrondie. La base
  refuse tout nombre à virgule dans une colonne `*_minor` (migration 0020).
- **Articles (Phase 5.5)** : création réservée à Mohamed, modification
  uniquement par dérogation auditée ; le Stock Service ne fait que les
  lire. Format du code article non décidé : UUID technique en attendant.
- **Quatre notions toujours séparées** : Document (devis, commande, BL,
  facture...) / Mouvement physique (`mouvement_stock`) / Affectation
  (`affectation_stock`, ne crée jamais de mouvement par elle-même) /
  Événement financier (facture, régularisation).
- **UUID (TEXT) en clé primaire partout**, + numéro humain séquentiel par
  type de document (`compteur_numerotation`).
- **Aucune suppression réelle** de document/lot/mouvement — tout est
  protégé par trigger (annulation/statut à la place). Seules `journal_audit`,
  `mouvement_stock`, `taux_change`, `regularisation_prix_fournisseur`,
  `inventaire_initial` et `inventaire_initial_ligne` sont en plus totalement
  immuables (ni UPDATE ni DELETE), ainsi que `article_unite_valorisation`.
  `cmp_stock_general` et
  `cmp_historique` sont des **caches reconstructibles**, volontairement PAS
  immuables (correction Phase 4, cf. migration 0015 et `docs/DATABASE.md`).

## Avant de commencer toute nouvelle session

1. Lis ce fichier en entier.
2. Lis `PROJECT_STATUS.md` et `CURRENT_SESSION.md`.
3. Lis `docs/BUSINESS_RULES.md`, `docs/PRIX_REVIENT.md` et
   `docs/STOCK_RULES.md` avant de toucher à quoi que ce soit qui touche au
   stock, aux prix, aux montants financiers ou à la valorisation.
4. Ne commence aucun développement au-delà de ce que la phase en cours
   autorise sans validation explicite de l'utilisateur.
