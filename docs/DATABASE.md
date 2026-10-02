# Base de données GMC — documentation technique (Phase 4 / 4.1)

Moteur : **SQLite** (fichier local `db/gmc.db`), choix validé et justifié en
Phase 2 (pas de cloud). `PRAGMA foreign_keys = ON` et `PRAGMA journal_mode =
WAL` à chaque connexion (voir `db/migrate.py:get_connection`).

État au terme de la Phase 5.5 : **47 tables, 4 vues, 94 triggers, 52 index**,
répartis sur **20 fichiers de migration** (`migrations/0001_*.sql` à
`migrations/0020_*.sql`), appliqués par `db/migrate.py` (Phase 4.1 : 44
tables, 4 vues, 41 triggers, 46 index, 16 migrations — les migrations 0017
à 0020 sont détaillées plus bas, section « Phase 5.5 »). Base reconstruite
et vérifiée intégralement (`PRAGMA integrity_check` → `ok`,
`PRAGMA foreign_key_check` → aucune anomalie), idempotence et
reproductibilité prouvées (ré-application sans effet, reconstruction
`--fresh` identique à chaque fois — voir `docs/STOCK_RULES.md` §3 pour la
checklist complète). La 4e vue (`v_bilan_chutes_annuel`) et le passage de
tous les montants financiers en entiers (`*_minor` + `devise`) datent de la
migration 0016 — voir `docs/PRIX_REVIENT.md` pour la représentation
monétaire et `docs/STOCK_RULES.md` pour la règle des chutes.

## Comment reconstruire / faire évoluer la base

```
python3 db/migrate.py            # applique les migrations manquantes
python3 db/migrate.py --fresh    # supprime et reconstruit tout depuis zéro
```

**Une migration déjà appliquée n'est jamais modifiée.** Une correction se
fait via un nouveau fichier `NNNN_*.sql` (voir `migrations/0015_*.sql` pour
un exemple réel : deux vues/triggers corrigés après avoir été découverts
incorrects en écrivant les tests, sans toucher aux fichiers déjà appliqués).

## Les quatre notions, toujours séparées

| Notion | Table(s) | Rôle |
|---|---|---|
| Document | `devis`, `commande_client`, `bon_commande_fournisseur`, `bl_fournisseur`, `facture_fournisseur`, `bon_commande_transformation`, `bon_sortie_transformation`, `reception_transformation`, `bl_client`, `facture_client`... | Ce qui a été émis/reçu sur papier ou en intention |
| Mouvement physique | `mouvement_stock` | Ce qui a réellement bougé physiquement |
| Affectation | `affectation_stock`, `reaffectation` | Une réservation logique d'une quantité pour une affaire — ne bouge rien physiquement |
| Événement financier | `facture_fournisseur`, `facture_client`, `regularisation_prix_fournisseur` | Ce qui a une conséquence comptable |

## Le registre de stock (`mouvement_stock`) — source de vérité exclusive

**Append-only, immuable** (ni UPDATE ni DELETE, imposé par trigger — voir
`migrations/0012_triggers_immutabilite.sql`). Toute autre donnée de stock
(soldes, disponibilité, CMP) est un **cache reconstructible** depuis ce
registre — jamais une source de vérité indépendante.

- `quantite` et `poids_kg` sont **toujours positifs**.
- La direction est portée par `emplacement_source` (si non NULL, retire de
  cet emplacement) et `emplacement_destination` (si non NULL, ajoute à cet
  emplacement).
- Emplacements possibles : `STOCK_GMC`, `CHEZ_TRANSFORMATEUR:<id>`, `CHUTES`,
  `LIVRE`. Le stock GMC = `STOCK_GMC` + chaque transformateur (décision
  validée Phase 5.5 : un transformateur est un emplacement physique réel).
- **Depuis la Phase 5.5, toute écriture passe par
  `services/stock_service.py:enregistrer_mouvement()`** (voir la section
  « Phase 5.5 » ci-dessous pour la règle type ↔ emplacements ↔ document).
- `document_source_type` / `document_source_id` : référence polymorphe vers
  le document déclencheur (nom de table + id). **Convention à respecter par
  tout futur code métier** (Phase 5) : pour un mouvement `SORTIE_TRANSFORMATION`,
  `document_source_type = 'bon_sortie_transformation_ligne'` et
  `document_source_id = <id de cette ligne>` — le moteur de valorisation
  (`cout_chute_unitaire_minor`/`cout_chute_total_minor`, voir plus bas)
  s'appuie explicitement sur cette convention pour retrouver le mouvement de
  sortie d'origine d'une chute.

Le solde d'un lot à un emplacement se lit via la vue `v_solde_lot_emplacement`
(jamais stocké).

## Le moteur de valorisation CMP (`db/valorisation.py`)

Implémente les règles de `docs/BUSINESS_RULES.md` §1 et §16. **Depuis la
finalisation de la Phase 5.5, le CMP est exprimé dans l'unité de
valorisation de l'article** (DT/kg, DT/ml, DT/unité ou DT/tonne — migration
0019 et `docs/PRIX_REVIENT.md` §6) : chaque mouvement est valorisé dans
l'unité en vigueur à sa date, au poids (KG/TONNE) ou au métrage/à la pièce
(ML/UNITE). Tout montant calculé est arrondi une seule fois au millime le
plus proche, 0,5 vers le haut (`core/arrondi.py`, règle §17) ; une chute
utilise le CMP exact à l'envoi. **Depuis la Phase 4.1, tous les montants
sont des entiers en unité monétaire minimale** —
toute fonction qui renvoie un montant porte le suffixe `_minor`. Référence
complète (signatures, exemples, pourquoi deux variantes unitaire/total) dans
**`docs/PRIX_REVIENT.md` §5** ; liste courte ici :

- `reconstruire_cmp(conn)` — reconstruit **intégralement** `cmp_stock_general`
  et `cmp_historique` en relisant tout `mouvement_stock` dans l'ordre
  chronologique. Idempotent, à appeler chaque fois qu'un coût de sortie doit
  être calculé sur des données à jour. Refuse (`ValueError`) tout mélange de
  devises au sein d'un même pool (garde-fou technique, cf.
  `docs/PRIX_REVIENT.md` §1).
- `cmp_actuel_minor(conn, article_id, finition, longueur_m)` /
  `cmp_devise_actuelle(conn, ...)` — CMP courant d'un pool et sa devise, lus
  depuis le cache.
- `cout_reel_lot_minor(conn, lot_id)` — coût réel d'un lot (règle 2), jamais
  lié au CMP ; lit `COALESCE(prix_unitaire_definitif_minor,
  prix_unitaire_provisoire_minor)`, ce qui implémente à lui seul la règle de
  régularisation fournisseur définitive (`docs/PRIX_REVIENT.md` §3).
- `cout_sortie_minor(conn, ...)` / `cout_sortie_total_minor(conn, ...)` —
  décident automatiquement, pour une sortie physique donnée, entre coût réel
  (INITIALE) et CMP au moment de la sortie (SUPPLEMENT/stock général) ; la
  variante `_total` renvoie le montant exact à facturer, sans dérive
  d'arrondi.
- `cout_chute_unitaire_minor(conn, chute_id)` / `cout_chute_total_minor(conn, chute_id)`
  — CMP au moment où la matière a quitté `STOCK_GMC` pour la transformation
  (pas au moment du retour).

### Point technique important — comment le ledger CMP et le coût réel cohabitent

`cmp_stock_general` / `cmp_historique` sont un **cache mécanique**, piloté
uniquement par `mouvement_stock` : **toute** sortie physique de `STOCK_GMC`
fait mécaniquement varier le pool CMP, **y compris une sortie liée à une
affectation INITIALE** (coût réel). Ce n'est pas une approximation : c'est
nécessaire, parce qu'une affectation ne crée jamais de mouvement par
elle-même (elle est purement logique), donc le ledger CMP ne peut réagir
qu'à des mouvements physiques réels, jamais à la création d'une affectation.

En conséquence, `cmp_stock_general.quantite_totale` représente la quantité
**physiquement présente en STOCK_GMC** pour ce pool (affectée ou non), pas
seulement la quantité disponible — c'est la vue `v_stock_non_affecte_par_lot`
qui répond à "combien est réellement disponible maintenant" (elle exclut les
affectations actives pas encore physiquement sorties).

La règle "coût réel du lot pour une affectation INITIALE" (règle métier 2)
n'est donc **jamais** appliquée en modifiant ce ledger : c'est une bascule
appliquée uniquement dans `cout_sortie()`, qui choisit la bonne valeur à
attribuer à UNE sortie donnée (pour le coût d'une affaire, une marge...) sans
jamais perturber le calcul mécanique du CMP lui-même. C'est un principe
standard de comptabilité de stock hybride (CMP en tenue de stock + coût
spécifique pour une affaire précise) et cela garantit que le ledger CMP reste
toujours simple, mécanique et parfaitement reconstructible, quelle que soit
la complexité des règles de marge appliquées par-dessus.

Propriété mathématique utilisée (et testée, cf. test 11) : une moyenne
pondérée ne change jamais quand on retire une quantité à son propre prix
moyen — donc le CMP "juste avant" et "juste après" une sortie sont toujours
identiques, y compris quand cette sortie vide entièrement le pool. Dans ce
cas, `cmp_unitaire_minor` **n'est pas remis à zéro** : il conserve le
dernier CMP connu, qui est exactement la valeur à laquelle cette sortie a
été valorisée.

**Phase 4.1 — exactitude entière du solde du pool.** `valeur_totale_minor`
n'est **jamais** mis à jour en multipliant un prix unitaire arrondi par une
quantité : chaque sortie retire un montant calculé par **retrait
proportionnel exact** sur le total courant
(`valeur_totale_minor × quantité_sortie / quantité_totale`, arrondi une
seule fois, en arithmétique entière pure). Cette méthode garantit qu'une
sortie qui vide entièrement un pool le ramène à **exactement** 0, sans
résidu d'arrondi cumulé — la technique standard utilisée par les systèmes
comptables réels. Le montant exact de chaque mouvement est conservé dans
`cmp_historique.montant_mouvement_minor` (signé : positif pour une entrée,
négatif pour une sortie) et relu tel quel par
`db/valorisation.py:montant_mouvement_minor()`, jamais recalculé après coup
— voir `docs/PRIX_REVIENT.md` §5 pour le détail et l'exemple chiffré de la
dérive que cette méthode évite.

## Réaffectation — workflow imposé (corrigé en migration 0015)

Une réaffectation lie deux lignes `affectation_stock` déjà existantes.
Ordre **obligatoire** des opérations (sinon le plafond du lot serait
transitoirement dépassé) :

1. Clôturer l'affectation d'origine : `UPDATE affectation_stock SET
   statut='CLOTUREE' WHERE id = <origine>`.
2. Créer l'affectation de destination (`INSERT INTO affectation_stock ...`,
   `statut` par défaut `ACTIVE`) — passe désormais le contrôle de plafond
   du lot, puisque l'origine ne compte plus (seules les affectations
   `ACTIVE` comptent dans le plafond).
3. Insérer la ligne `reaffectation` reliant origine → destination, avec
   `motif` obligatoire.

Protections imposées par trigger (`migrations/0015_*.sql`) :
- Impossible de réaffecter une affectation déjà physiquement livrée
  (`mouvement_physique_id IS NOT NULL`).
- Impossible de réaffecter deux fois la même origine.
- La quantité réaffectée ne peut pas dépasser celle de l'affectation
  d'origine.

Voir `tests/helpers.py:reaffecter()` pour une implémentation de référence de
ce workflow, réutilisable telle quelle par le futur code métier (Phase 5).

## Immuabilité — deux niveaux

1. **Totalement immuables** (ni UPDATE ni DELETE) : `mouvement_stock`,
   `taux_change`, `regularisation_prix_fournisseur`, `journal_audit`, et
   depuis la Phase 5.5 `inventaire_initial` / `inventaire_initial_ligne`
   (une erreur d'inventaire initial se corrige par une correction
   d'inventaire tracée) et `article_unite_valorisation` (un changement
   d'unité s'enregistre par une nouvelle ligne). `lot.unite_prix` est
   figée à la création du lot.
2. **DELETE interdit, UPDATE encadré** : tous les documents métier (devis,
   commandes, BL, factures, lots, affectations, transformations...) —
   une suppression doit devenir une annulation tracée (changement de
   statut), jamais un `DELETE` réel.
3. **Caches reconstructibles, volontairement PAS immuables** :
   `cmp_stock_general`, `cmp_historique`. Ils avaient été rendus immuables
   par erreur en migration 0012 (traités à tort comme un journal d'audit
   permanent) — corrigé en migration 0015, car `reconstruire_cmp()` a
   besoin de pouvoir les vider et les régénérer intégralement.

## Contraintes d'intégrité qui ne sont pas de simples CHECK/UNIQUE

(portent sur un agrégat d'autres lignes, donc implémentées par trigger,
`migrations/0013_triggers_metier.sql`) :

- `trg_mouvement_solde_source` — un mouvement ne peut jamais retirer d'un
  emplacement plus que ce que le lot y possède réellement (solde dérivé des
  mouvements déjà enregistrés). Couvre à lui seul plusieurs cas : réception
  de transformation sans stock GMC réellement envoyé, mouvement incohérent,
  livraison dépassant le stock disponible.
- `trg_affectation_plafond` — la somme des affectations **actives** d'un lot
  ne dépasse jamais sa quantité initiale (corrigé en 0015 : ne compte plus
  les affectations déjà clôturées, pour permettre les réaffectations).
- `trg_bl_client_ligne_plafond` — une livraison ne dépasse jamais ce qui a
  été affecté et pas encore livré.
- `trg_reaffectation_origine_active` / `trg_reaffectation_cloture_origine` —
  voir section réaffectation ci-dessus.
- `trg_reception_transfo_plafond` — reçu + chute ne dépassent jamais ce qui
  a été envoyé en transformation.
- Double rattachement financier (une ligne facturée une seule fois) : assuré
  par de simples contraintes `UNIQUE`, aucun trigger nécessaire.

## Vues

- `v_solde_lot_emplacement` — solde d'un lot par emplacement, dérivé
  exclusivement de `mouvement_stock`.
- `v_approvisionnement_ligne` — suivi commandé / commandé-fournisseur /
  réceptionné / reste à approvisionner, par ligne de commande client.
- `v_stock_non_affecte_par_lot` — stock réellement disponible (non affecté)
  par lot ; corrigée en migration 0015 (une affectation déjà physiquement
  sortie ne doit plus être soustraite une deuxième fois).
- `v_bilan_chutes_annuel` (Phase 4.1, migration 0016) — bilan consolidé
  annuel des coûts de chutes, par année et par devise. Voir
  `docs/STOCK_RULES.md` §2.5.

## Phase 5.5 — migrations 0017 à 0020 et Stock Service

Migration `0017_stock_service_socle.sql` (décisions validées M1, M2, M3 de
l'analyse Phase 5.5), même technique de reconstruction que la migration
0016 :

- **M2 — `CONSOMMATION_TRANSFORMATION`** (nouveau type de mouvement) : au
  retour d'une transformation, la quantité reçue quitte
  `CHEZ_TRANSFORMATEUR:<id>` du lot d'origine (aucune destination : la
  matière est devenue le lot résultat), dans la même transaction que
  l'`ENTREE_RETOUR_TRANSFORMATION` du lot résultat en `STOCK_GMC`. Ces deux
  types ne s'enregistrent **que par paire**, via
  `stock_service.enregistrer_retour_transformation()` — plus de stock
  fantôme chez le transformateur. N'affecte pas le CMP (ne touche pas
  `STOCK_GMC`).
- **M3 — stock d'ouverture** (remplacé par l'inventaire initial de
  démarrage en migration 0018, voir ci-dessous) : tables `stock_ouverture`
  (en-tête, une par année, `annee` unique, `date_reference` = 31/12 de
  N-1, `cree_par` obligatoire) et `stock_ouverture_ligne` (article, finition, longueur,
  pièces, poids, emplacement réel `STOCK_GMC` ou `CHEZ_TRANSFORMATEUR:<id>`,
  `cout_unitaire_minor` par pièce, `valeur_minor` = pièces × coût (CHECK),
  devise, `cree_par`), toutes deux immuables (triggers no_update/no_delete) ;
  type de mouvement `ENTREE_STOCK_OUVERTURE` ; `lot.stock_ouverture_ligne_id`
  = 3e origine possible d'un lot (CHECK : **exactement une** origine parmi
  BL fournisseur / lot parent / ligne d'ouverture). Le coût validé est
  écrit comme prix provisoire ET définitif du lot : `reconstruire_cmp()`
  (inchangé) l'utilise tel quel comme coût d'entrée.
- **M1 — garde-fous anti-double-comptage** : index uniques partiels
  `ux_mouvement_entree_origine_par_lot` (une seule entrée d'origine par
  lot) et `ux_mouvement_type_par_document` (un seul mouvement d'un type
  donné par ligne de document source).

Règle type ↔ emplacements ↔ document appliquée par le Stock Service :

| Type | Source | Destination | Document source |
|---|---|---|---|
| `ENTREE_RECEPTION_FOURNISSEUR` | — | `STOCK_GMC` | `bl_fournisseur_ligne` (lot issu de cette ligne, quantité = quantité initiale) |
| `ENTREE_INVENTAIRE_INITIAL` (migration 0018) | — | emplacement réel de la ligne | `inventaire_initial_ligne` |
| `SORTIE_TRANSFORMATION` | `STOCK_GMC` | `CHEZ_TRANSFORMATEUR:<transformateur du bon>` | `bon_sortie_transformation_ligne` |
| `CONSOMMATION_TRANSFORMATION` (par paire) | `CHEZ_TRANSFORMATEUR:<id>` | — | `reception_transformation_ligne` |
| `ENTREE_RETOUR_TRANSFORMATION` (par paire) | — | `STOCK_GMC` | `reception_transformation_ligne` |
| `SORTIE_CHUTE` | `CHEZ_TRANSFORMATEUR:<id>` | `CHUTES` | `reception_transformation_ligne` |
| `SORTIE_LIVRAISON_CLIENT` | `STOCK_GMC` | **`LIVRE`** (obligatoire) | `bl_client_ligne` |
| `CORRECTION_INVENTAIRE_POSITIVE` | — | `STOCK_GMC` ou transformateur | `journal_audit` (créé avec elle, motif obligatoire) |
| `CORRECTION_INVENTAIRE_NEGATIVE` | `STOCK_GMC` ou transformateur | — | `journal_audit` (créé avec elle, motif obligatoire) |
| `TRANSFERT` | non pris en charge (aucune règle métier définie, un seul dépôt) | | |

**Migration `0018_inventaire_initial_demarrage.sql`** (règle validée
« démarrage du système en 2026 », qui annule l'ouverture au 31/12/N-1) :
tables `inventaire_initial` (en-tête **unique**, `date_heure_mise_en_service`
= instant exact de mise en service au format du registre, UTC ;
`cree_par` obligatoire) et `inventaire_initial_ligne` (mêmes champs que
l'ancienne ligne d'ouverture + `saisie_originale` JSON : valeurs et unités
telles que saisies) ; `lot.inventaire_initial_ligne_id` (remplace
`stock_ouverture_ligne_id`) ; type `ENTREE_INVENTAIRE_INITIAL` (remplace
`ENTREE_STOCK_OUVERTURE`) ; index uniques M1 mis à jour. Données de 0017
reprises (test dédié). Aucun mouvement ne peut être daté avant l'instant de
mise en service ; l'inventaire initial est clos dès la première opération.

**Migration `0019_unite_valorisation_article.sql`** (règle définitive
validée « unité du CMP / coût de revient », `docs/BUSINESS_RULES.md` §16) —
nécessaire car le schéma n'avait aucune place pour une unité de
valorisation (tout était implicitement « par pièce ») :

- `article_unite_valorisation` (nouvelle table, **immuable**) : `nature`
  (`DEFINITION_INITIALE`, une seule par article, valable depuis l'origine ;
  ou `CHANGEMENT`), `unite` (`KG`/`ML`/`UNITE`/`TONNE`), `unite_precedente`,
  `date_effet` (format du registre), `motif` (obligatoire pour un
  changement), `detail_cmp` (JSON : CMP de chaque pool dans l'ancienne et
  la nouvelle unité), `cree_le`, `cree_par`. Trigger de contrôle : pas de
  date d'effet future ; un changement exige une unité existante, une unité
  précédente égale à l'unité en vigueur, une date postérieure au
  changement précédent et à tout mouvement déjà enregistré de l'article.
- `lot.unite_prix` : unité des prix du lot. Fixée automatiquement à la
  création (unité en vigueur de l'article) si elle n'est pas fournie,
  vérifiée si elle l'est, puis figée ; un lot est refusé si l'article n'a
  aucune unité définie. Lots existants : `UNITE` (FAIT : ils étaient
  valorisés par pièce) ; aucun article existant ne reçoit d'unité.
- `inventaire_initial_ligne` reconstruite : + `unite_cout` ; la CHECK
  « valeur = pièces × coût » ne vaut plus que pour `UNITE` (le service
  contrôle l'exactitude dans les autres unités). Lignes existantes :
  `UNITE`.
- `cmp_stock_general` / `cmp_historique` recréés (caches) avec
  `unite_valorisation`, `poids_total_kg` / `poids_total_apres_kg`,
  `quantite_valorisation` / `quantite_valorisation_apres` ; vides après la
  migration, régénérés par `reconstruire_cmp()`.

**Migration `0020_unite_prix_saisie.sql`** (décision validée « Proposition
A », `docs/BUSINESS_RULES.md` §18 — prix conservé dans son unité d'origine) :

- vérification préalable : la migration échoue (et ne modifie rien) si un
  montant non entier existe déjà dans une colonne `*_minor` ;
- `lot` : le trigger de contrôle accepte désormais une unité de prix égale
  à l'unité de l'article OU, pour un article au poids, l'autre unité de
  masse (kg ↔ tonne) ; + `unite_prix_definitif` (obligatoire avec le prix
  définitif, même compatibilité) ; + `unite_valorisation_article` (unité de
  l'article à la création, fixée par la base puis figée) ;
- `inventaire_initial_ligne.unite_cout` : unité du coût saisi, contrôlée ;
- `regularisation_prix_fournisseur` : + `unite_prix_provisoire`,
  `unite_prix_definitif`, `unite_ecart` ; écart contrôlé par conversion
  exacte (unité commune, la tonne en cas de kg/tonne) ; reprise des faits
  existants (trigger d'immuabilité suspendu puis recréé à l'identique) ;
- **garde-fou « montant monétaire entier »** : 38 triggers (insertion et
  mise à jour) refusent un nombre à virgule dans les 28 colonnes `*_minor`
  des 19 tables concernées (SQLite l'acceptait dans une colonne INTEGER).

Note : les helpers de test historiques (`tests/helpers.py`, Phase 4)
enregistrent encore une livraison sans destination `LIVRE` et un retour de
transformation sans consommation du lot d'origine ; ils ne sont utilisés
que par les tests Phase 4/4.1 (inchangés). Tout nouveau code passe par le
Stock Service, et `stock_service.verifier_conservation()` signale ces deux
écarts comme anomalies.

## Points techniques encore ouverts

- ~~Traitement comptable des chutes~~ — **tranché définitivement en Phase
  4.1** (§25-C, hérité de la Phase 1, n'est plus un point ouvert). Voir
  `docs/STOCK_RULES.md` §2.4-2.5 : `chute.impact_marge_valide` reste à `0`
  en permanence, le coût alimente exclusivement le bilan consolidé annuel.
- ~~Numérotation automatique~~ — code applicatif livré en Phase 5.4
  (`core/numerotation.py`).
- Débit 1 → N pièces (ex. 1 × 12 m → 2 × 6 m) : refusé par
  `trg_reception_transfo_plafond`, qui compte en pièces (Phase 5.8).
- Retour d'un stock d'inventaire initial situé chez un transformateur au
  démarrage : aucun bon de sortie n'existe pour lui, alors que la réception
  de transformation en exige un (Phase 5.8).
- ~~Valorisation « interne : kg »~~ — **tranché** : le CMP suit l'unité de
  valorisation de l'article (`docs/BUSINESS_RULES.md` §16, migration 0019).
- ~~Unités de saisie de la formule des tôles~~ — **tranché** : volume
  (dm³) × 8 kg/dm³, dimensions converties en dm (`docs/BUSINESS_RULES.md`
  §14, `core/masses_validees.py`).
- ~~Règle d'arrondi~~ — **tranché** : millime le plus proche, 0,5 vers le
  haut, une seule fois sur le montant final (`docs/BUSINESS_RULES.md` §17,
  `core/arrondi.py`) ; aucune migration nécessaire.
- Les prix des lignes de documents (BL, commandes, factures...) n'ont pas
  encore d'unité explicite en base (DT/kg, DT/t, DT/pièce) : à traiter par
  chaque service de document (Phases 5.6 à 5.9), conformément à la règle
  §15.
- `v_cout_affaire` et `v_marge_affaire`, évoquées en Phase 2/3, n'ont pas
  encore été créées : elles nécessitent le moteur de valorisation (livré
  cette phase) mais leur écriture précise (quelles lignes exactement
  entrent dans le coût d'une affaire) relève du calcul métier, donc de la
  Phase 5.
