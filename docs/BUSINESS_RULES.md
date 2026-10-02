# Règles métier GMC — référence unique et à jour

Ce document est la référence unique des règles métier validées. En cas de
divergence apparente avec un autre document ou une ancienne conversation,
**ce fichier fait foi** (il est mis à jour à chaque validation).

Dernière mise à jour : Phase 5.6 (analyse, aucun code) — le 02/10/2026 :
décisions O, X, Y, CT et P des analyses v5 à v9 (§23), règle définitive
des barres de 12 m et de 6 m (§24), décisions sur les lectures L-a à L-v
et les propositions C1 à C14 (§25), registre des règles remplacées (§26),
points encore ouverts (§27). Les règles des §19 à §22 que ces décisions
remplacent portent une note « Mise à jour » à leur place.
Précédente : Phase 5.6 (analyse) — réponses K1 à K22 (§22),
décisions N1 à N15 (§21),
correction de D1 (§20), décisions D1 à D6 (§20), précisions sur le
transport (§19), le 30/09/2026.
Précédente : Phase 5.5 — dernière correction (prix conservé dans
son unité d'origine §18), après la finalisation (arrondi monétaire §17,
tôles calculées par volume × densité 8 kg/dm³ §14, unité du CMP / coût de
revient §16), après les
corrections/clarifications validées (inventaire initial de démarrage §12,
masses FP définitives §14, unité obligatoire à la saisie §15) et les règles
Phase 5.5 (catalogue articles §11, transformateur = emplacement physique
réel §13).
Précédente : Phase 4.1 (montants entiers + devise, coût final fournisseur,
chutes).

> **Montants financiers** : depuis la Phase 4.1, tout montant est un entier
> en unité monétaire minimale (millimes TND / centimes EUR / cents USD),
> jamais un `REAL`/flottant. Voir `docs/PRIX_REVIENT.md` pour la règle
> complète et la liste des colonnes concernées. Les quantités physiques
> (poids, longueur) et les pourcentages restent en `REAL`, inchangés.

## 1. Règles de valorisation du stock — DÉFINITIVES (Phase 4)

**Le FIFO est abandonné.** Il avait été proposé en Phase 2/3 pour le stock
général, mais la Phase 4 l'a explicitement remplacé par le CMP. Ne jamais
réintroduire de logique FIFO dans le code.

| Situation | Méthode de valorisation |
|---|---|
| Stock général GMC (non affecté à une affaire) | **CMP** (coût moyen pondéré), calculé par pool (article, finition, longueur) |
| Quantité normale affectée à une affaire (affectation de type INITIALE) | **Coût réel du lot** affecté — jamais le CMP |
| Quantité supplémentaire (affectation de type SUPPLEMENT) | **CMP applicable au moment de la sortie physique** |
| Chute (issue d'une transformation) | **CMP applicable au moment de la sortie physique** (= au moment où la matière a quitté GMC pour la transformation, pas au moment où la chute est constatée au retour) |

Le coût réel d'un lot est son `prix_unitaire_definitif_minor` si la
régularisation facture a déjà été **appliquée au lot** (lot pas encore sorti
au moment de la facture — voir §3), sinon son
`prix_unitaire_provisoire_minor` (prix du BL) en attendant.

**Unité** : le CMP et les coûts de lot sont exprimés dans l'**unité de
valorisation de l'article** (DT/kg, DT/ml, DT/unité ou DT/tonne) — jamais
imposés en DT/kg. Voir §16.

Détail d'implémentation (moteur `db/valorisation.py`) : voir
`docs/DATABASE.md` — notamment la distinction entre le ledger CMP mécanique
(qui suit tout mouvement physique de STOCK_GMC, quelle que soit
l'affectation) et le coût réellement *attribué* à une affaire donnée.

## 2. Coût d'entrée d'un lot fournisseur

- Coût provisoire = prix du BL fournisseur (`prix_unitaire_provisoire_minor`).
- Coût final = prix de la facture fournisseur (`prix_unitaire_definitif_minor`),
  renseigné à la régularisation, **seulement** si le lot n'était pas encore
  sorti (voir §3).
- Les deux sont toujours conservés, jamais l'un n'écrase l'autre.

## 3. Régularisation facture fournisseur (écart BL / facture) — DÉFINITIVE (Phase 4.1 §1)

Détail complet, exemple chiffré obligatoire et référence des fonctions dans
**`docs/PRIX_REVIENT.md` §3** — résumé ici :

- **Lot pas encore sorti physiquement** (`lot_deja_sorti = 0`,
  `impact_analytique = 'APPLIQUE_AU_LOT'`) : le prix définitif est appliqué
  directement au lot (`prix_unitaire_definitif_minor` mis à jour) — rien n'a
  encore consommé l'ancien coût, aucun risque de réécriture d'un historique
  déjà figé. **Le CMP du pool est alors reconstruit avec ce coût facturé
  final**, plus jamais avec le prix BL provisoire pour ce lot (ex. 100
  unités à 5,000 TND provisoire, facturées 6,000 TND, toutes encore en
  stock → coût final du lot = CMP reconstruit = 6,000 TND).
- **Lot déjà sorti, totalement ou partiellement** (`lot_deja_sorti = 1`,
  `impact_analytique = 'ECART_SEPARE'`) : **jamais rétroactif**. On n'écrit
  jamais par-dessus le coût déjà utilisé pour calculer une affaire ou une
  marge déjà clôturée, on ne réécrit jamais les mouvements physiques
  historiques (`mouvement_stock` est immuable de toute façon), et le CMP déjà
  consommé par les sorties passées ne bouge pas. Un enregistrement séparé
  (`regularisation_prix_fournisseur`, immuable) trace l'écart pour référence,
  sans toucher au passé — que le lot soit partiellement ou totalement sorti,
  seule cette distinction compte.

## 4. Stock disponible pour une quantité supplémentaire

Une quantité supplémentaire ne peut être prélevée que sur du stock GMC
**réellement disponible et non affecté à une autre affaire**. Prendre du
stock déjà affecté ailleurs n'est jamais automatique : cela doit passer par
une **réaffectation manuelle, tracée, avec motif obligatoire** (voir §7).

## 5. Livraison GMC

**LIVRÉ = FACTURÉ.** La sortie physique de GMC (mouvement de stock vers
`LIVRE`) déclenche en même temps : diminution du stock, augmentation de la
quantité livrée, augmentation de la quantité facturée, enregistrement du
chiffre d'affaires. La facture elle-même **ne diminue jamais le stock** —
c'est toujours la sortie physique qui fait foi.

## 6. Achats multi-fournisseurs / multi-transformateurs

Une même commande client peut être couverte par plusieurs BL de plusieurs
fournisseurs (ex. commande de 100 = BL fournisseur 1 de 60 + BL fournisseur 2
de 40). Chaque réception crée son propre lot, distinct, avec sa propre ligne
de BL d'origine — jamais de fusion de deux réceptions dans un même lot, pour
qu'aucune quantité ne puisse jamais être comptée deux fois.

## 7. Réaffectation

Une réaffectation (déplacer une quantité déjà affectée à une affaire A vers
une affaire B) est **toujours tracée dans une table dédiée** (`reaffectation`),
**jamais silencieuse**, avec un **motif obligatoire**. L'affectation d'origine
se clôture automatiquement. Une affectation déjà physiquement livrée ne peut
plus être réaffectée (la marchandise est déjà partie).

## 8. Transformation (galvanisation / GPP / débit)

L'origine d'un envoi en transformation est toujours du stock GMC
(`STOCK_GMC`), jamais un stock intermédiaire. Au retour, la quantité reçue
utilisable devient un **nouveau lot** (lié au lot d'origine par filiation,
`lot_parent_id`) ; la quantité non récupérée est enregistrée comme **chute**.
Reçu + chute ne dépassent jamais ce qui a été envoyé. Le transformateur est
un emplacement physique réel du stock GMC — voir §13 (Phase 5.5).

**Mise à jour (Phase 5.6, 02/10/2026).** Pour la préparation des bons de
sortie transformation, deux transformations seulement sont retenues :
GALVANISATION et GPP (P-RET, §23). Le sort du « débit » cité dans le
titre ci-dessus, que la base connaît encore, n'est **pas tranché** : il
relève de Q-TRF et de la Phase 5.8 (§27). Par ailleurs, une barre de 12 m
transformée peut revenir en 2 pièces de 6 m (CT18, §23) : le contrôle
« reçu + chute ≤ envoyé » devra alors se compter en unités de 6 m et
non en nombre de pièces (proposition de l'analyse v10, §M) — à traiter
en 5.8.

## 9. Chutes — DÉFINITIVE (Phase 4.1 §3)

Les chutes sont enregistrées et tracées séparément du stock normal, **jamais
supprimées**. Leur valorisation (règle CMP, §1) est calculée et conservée
(`chute.cout_cmp_total_minor`). Ce n'est plus un point ouvert depuis la Phase
4.1 : le traitement comptable est **tranché définitivement** —
`chute.impact_marge_valide` reste à `0` en permanence (le coût n'est **jamais**
intégré automatiquement dans la marge individuelle d'une affaire), et ce
coût alimente exclusivement un **bilan consolidé annuel** (vue
`v_bilan_chutes_annuel`), tous articles et affaires confondus. Détail complet
dans **`docs/STOCK_RULES.md` §2**.

## 10. Fournisseur / facture

Le pays d'origine du fournisseur est obligatoire (nécessaire au module
MACF). Le rapprochement BL ↔ facture se fait ligne à ligne (une ligne de BL
n'est facturée qu'une fois) ; plusieurs BL peuvent être regroupés sur une
même facture de fin de mois.

## 11. Catalogue articles — DÉCISIONS VALIDÉES (Phase 5.5)

- La liste MV (fichier `tablleau_preparation.xlsx`, feuille `mv`) constitue
  la base initiale du référentiel articles. Le référentiel **n'est pas une
  liste fermée** : de nouveaux articles pourront être créés ultérieurement
  selon les besoins commerciaux.
- La création d'un nouvel article est **réservée à Mohamed** ; les
  utilisateurs opérationnels ne créent pas directement d'article. Toute
  création est tracée (utilisateur, date).
- Un article existant **ne peut pas être modifié normalement** : toute
  modification nécessite une **dérogation spéciale de Mohamed**, est
  auditée et conserve la traçabilité de l'ancien état.
- **Mise à jour (Phase 5.6, 02/10/2026).** Précisé par P-ART (§23) :
  modification à impact métier = nouvelle version historisée ; correction
  administrative = auditée, sans nouvelle version. Tout utilisateur peut
  **demander** une création ; seul le SUPERADMIN crée (L-o, §25) ; seul
  le SUPERADMIN modifie une désignation (L-p, §25).
- Chaque article possède une désignation normalisée et un identifiant
  interne stable (UUID technique). Le **format définitif du code article
  n'est pas encore décidé** — aucune convention ne doit être inventée.
- Les doublons de la liste MV ne sont **jamais fusionnés automatiquement** :
  Mohamed fournit progressivement la liste MV nettoyée et validée, qui sera
  la référence de l'import initial ; les doublons sont traités uniquement
  sur la base de ses corrections. Aucun import automatique de la liste MV
  sur la base des anciennes données non nettoyées.
- Le Stock Service lit les articles, vérifie leur existence et utilise
  leurs caractéristiques ; il ne crée ni ne modifie jamais un article.

## 12. Inventaire initial de démarrage et fin d'exercice — DÉCISION VALIDÉE (Phase 5.5, corrigée)

**Remplace la règle « stock d'ouverture 2026 = stock réel au 31/12/2025 »,
annulée : le stock du 31/12/2025 n'est PAS l'ouverture automatique de 2026.**

- GMC ERP commence son exploitation en 2026 par un **inventaire initial de
  démarrage**, réalisé à l'**instant exact de mise en service** du système.
  Il contient notamment : article, quantité/pièces, poids, emplacement
  physique, coût unitaire validé, valeur, date/heure, traçabilité. Il
  devient le stock initial du système.
- Il n'est **pas** un achat, ne génère **pas** de faux BL fournisseur,
  n'alimente **pas** les statistiques d'achat et n'est **pas** une réception
  fournisseur. Le coût validé devient le coût d'entrée du stock dans la
  valorisation.
- Après cet instant, toutes les opérations réelles 2026 sont enregistrées
  normalement dans le système.
- **Fin d'exercice**, chaque année : inventaire théorique du système,
  inventaire physique, saisie manuelle de l'inventaire physique,
  rapprochement, analyse des écarts, correction/validation ; l'inventaire
  validé devient le stock d'ouverture de l'année suivante. Soit :
  inventaire initial 2026 → opérations 2026 → clôture 2026 → inventaire
  physique + rapprochement → ouverture 2027, puis même logique chaque
  année. Le module d'inventaire annuel sera développé dans une phase
  dédiée ; la Phase 5.5 garantit seulement que l'architecture ne le bloque
  pas (stock théorique à un instant donné, corrections tracées).

## 13. Transformateur = emplacement physique réel — DÉCISION VALIDÉE (Phase 5.5)

Un transformateur constitue un emplacement physique réel du stock GMC. Le
stock est visible à chaque instant dans chaque emplacement. Exemple : 100
pièces envoyées → GMC −100, transformateur +100 ; si 95 reviennent → GMC
+95, transformateur −95 ; les 5 chutes sont enregistrées séparément (§9).
Il est **interdit** qu'après réception de 95 pièces GMC affiche 95 et le
transformateur continue d'afficher 100 (stock fantôme) : la conservation
physique entre les emplacements (GMC, transformateurs, chutes, livré) est
garantie.

## 14. Masses — VALEURS DÉFINITIVES (Phase 5.5)

- **FP 45/20 = 7,2 kg/ml** ; **FP 120/30 = 28,8 kg/ml** ;
  **FP 130/30 = 31,2 kg/ml**. La valeur 28,8 kg/ml précédemment associée à
  FP 130/30 est **annulée**. Ne jamais réintroduire les anciennes valeurs
  4,07 et 283,8.
- Si le fichier MV contient des valeurs différentes, elles ne sont **ni
  fusionnées automatiquement ni remplacées silencieusement** (l'écart est
  signalé, la décision reste à Mohamed).
- Tôles planes LAC/GALVA — poids unitaire (règle définitive) : **volume ×
  densité**. `Volume (dm³) = longueur (dm) × largeur (dm) × épaisseur (dm)`
  puis `Poids (kg) = Volume (dm³) × 8 kg/dm³`. **Densité de calcul des
  tôles planes = 8 kg/dm³** (règle GMC ; ne jamais la remplacer par 7,85 ou
  une autre valeur). Dimensions saisies avec leur unité (en pratique en
  mm ; cm, dm ou m acceptés), converties en dm ; une dimension sans unité
  est refusée. **Contrôle : 3000 mm × 1500 mm × 1 mm = 30 dm × 15 dm ×
  0,01 dm = 4,5 dm³ ; × 8 = 36 kg.** Aucun résultat intermédiaire n'est
  interprété comme des grammes ; aucun calcul intermédiaire n'est arrondi.
  Implémentation : `core/masses_validees.py:calcul_poids_tole_plane()`.
- Table de conversion validée : dm → m ÷ 10 ; m → dm × 10 ; dm³ → m³
  ÷ 1 000 ; m³ → dm³ × 1 000 ; 1 000 mm = 1 m ; 100 cm = 1 m ;
  100 mm = 1 dm ; 10 dm = 1 m.
- Tôles larmées : poids catalogue indiqué dans la fiche MV.
- Le poids des tôles dans le fichier MV est en **kg**.

## 15. Unité obligatoire à la saisie — RÈGLE TRANSVERSALE VALIDÉE (Phase 5.5)

- Toute saisie de quantité, poids, longueur ou prix comporte
  **obligatoirement son unité** (ex. `2 500 kg`, `2,5 tonnes`, `5 DT/kg`,
  `5 000 DT/tonne`, `12 m`, `10 pièces`). Le système ne devine **jamais**
  une unité implicite et **refuse une saisie ambiguë** lorsqu'une unité est
  nécessaire. L'utilisateur voit toujours clairement l'unité au moment de
  la saisie.
- L'unité saisie est **conservée pour la traçabilité** ; le système peut
  ensuite convertir automatiquement vers l'unité interne nécessaire aux
  calculs, sans jamais perdre l'unité d'origine.
- 1 tonne = 1 000 kg. Masses physiques internes (stock, achats/réceptions,
  transformations, livraisons physiques) : **kg**. Longueurs : unité
  explicite. Pièces : unités/pièces. Les ventes au poids sont
  commercialement exprimées en **tonnes** (lorsque l'article est vendu au
  poids). Le **CMP / coût de revient** suit l'unité de valorisation de
  l'article (§16) : il n'est pas imposé en kg.
- **Mise à jour (Phase 5.6).** Le **KG** est aussi une unité de vente au
  poids, comme la tonne (Y4, CT20, C2 : §23, §25).
- Exemple : 5 DT HT/kg = 5 000 DT HT/tonne. Vente de 2 500 kg : quantité
  physique 2 500 kg, quantité commerciale 2,5 tonnes, prix commercial
  5 000 DT/tonne, CA HT 12 500 DT.

> Le point « valorisation interne : kg » signalé en Phase 5.5 est
> **tranché** par la règle §16 (unité de valorisation de l'article).

## 16. Unité du CMP / coût de revient — RÈGLE DÉFINITIVE (Phase 5.5)

- Le CMP n'est **pas** systématiquement calculé en DT/kg. Il est toujours
  exprimé dans l'**unité de valorisation applicable à l'article** :
  **DT/KG**, **DT/ML**, **DT/UNITE** ou **DT/TONNE**. Exemples : article
  valorisé au kg → CMP en DT/kg ; au mètre linéaire → DT/ml ; à l'unité →
  DT/unité ; à la tonne → DT/tonne.
- L'unité du CMP dépend **automatiquement** de l'unité de produit définie
  pour l'article. Le système n'impose jamais arbitrairement DT/kg et ne
  choisit **aucune unité par défaut** : un article sans unité définie ne
  peut recevoir aucun lot ni être valorisé.
- Cette règle ne change pas l'unité des données physiques (masses en kg,
  longueurs avec unité explicite, ventes en tonnes, pièces en unités) ; le
  moteur de valorisation utilise l'unité de l'article et fait les
  conversions nécessaires de manière explicite et traçable.
- **Changement d'unité** : autorisé selon les règles de modification d'un
  article déjà validées (§11 — dérogation de Mohamed). L'ancienne unité est
  conservée dans l'historique, la nouvelle est enregistrée, la date et
  l'utilisateur sont tracés ; les historiques de coûts précédents ne sont
  **jamais réécrits silencieusement**.
- Toutes les règles CMP précédentes restent applicables (historique des
  lots, coût provisoire/définitif, régularisation fournisseur, chutes au
  CMP figé à l'envoi, pas de FIFO, stock général au CMP, quantité normale
  affectée au coût réel du lot, quantité supplémentaire au CMP).

Mise en œuvre (détail : `docs/PRIX_REVIENT.md` §6, `docs/DATABASE.md`) :

- historique immuable `article_unite_valorisation` (définition initiale,
  puis changements datés et motivés) ; le lot conserve le prix saisi et son
  unité d'origine (§18), ainsi que l'unité de l'article à sa création ;
- quantité d'un mouvement dans l'unité : UNITE = pièces ; ML = pièces ×
  longueur ; KG = kg ; TONNE = kg / 1 000. Au kg et à la tonne, le CMP se
  répartit au poids ; au ml et à l'unité, au métrage / à la pièce ;
- chaque mouvement est valorisé dans l'unité en vigueur à sa date : un
  changement d'unité ne réécrit aucune ligne antérieure ; un changement ne
  peut pas prendre effet avant un mouvement déjà enregistré de l'article ;
- seule conversion de prix acceptée : kg ↔ tonne (§18) ; un prix dans une
  autre unité (ex. DT/pièce pour un article au kg) est refusé — aucune
  conversion implicite.

Les montants calculés suivent la règle d'arrondi §17.

## 17. Arrondi monétaire — RÈGLE DÉFINITIVE (Phase 5.5)

- Lorsqu'un calcul monétaire ne tombe pas exactement au millime, le système
  **arrondit au millime le plus proche**, **0,5 millime arrondi vers le
  haut**, et ceci **une seule fois par montant calculé**.
- Exemple : 1 000,5 kg × 2,501 DT/kg = 2 502,2505 DT → **2 502,251 DT**
  enregistré.
- Aucun arrondi silencieux à plusieurs niveaux ; aucun sous-calcul arrondi
  successivement ; la précision interne est conservée jusqu'au calcul
  final ; l'arrondi s'applique au montant monétaire final concerné ; la
  règle est identique et reproductible dans tous les moteurs.
- S'applique à : entrée de lot, coût réel d'affaire, CMP, sortie de stock,
  chute, inventaire initial, régularisation fournisseur et autres montants
  calculés.

Mise en œuvre : implémentation unique `core/arrondi.py`, utilisée par le
moteur CMP et par les conversions d'unités. Détail et choix techniques :
`docs/PRIX_REVIENT.md` §6.4.

Précision validée en Phase 5.6 (K13, §22) : l'arrondi se fait à l'unité
minimale de la devise du montant, soit le millime pour le TND et le
**centime pour l'EUR**. La règle est la même : 0,5 vers le haut, une seule
fois, sur le montant final.

## 18. Prix conservé dans son unité d'origine — DÉCISION DÉFINITIVE (Phase 5.5, « Proposition A »)

- Le prix unitaire est **conservé dans l'unité dans laquelle il a été
  réellement saisi**, lorsque la conversion vers l'unité de valorisation de
  l'article est une conversion physique exacte **kg ↔ tonne**.
- Le prix saisi n'est **jamais arrondi** ; le prix original et son unité
  d'origine sont **conservés** ; la conversion vers l'unité de valorisation
  se fait **uniquement au moment du calcul** ; **aucun arrondi
  intermédiaire** ; seul le **montant monétaire final** est arrondi au
  millime (§17).
- **Exemple obligatoire** : article valorisé en DT/kg, prix fournisseur
  2 500,5 DT/t → le lot conserve 2 500 500 millimes, unité TONNE, article
  KG ; au calcul, 2 500,5 DT/t ÷ 1 000 = 2,5005 DT/kg (jamais 2,501 DT/kg) ;
  1 000,3 kg × 2,5005 = 2 501,25015 DT → **2 501,250 DT**.
- Quatre notions toujours distinctes : **A. unité de valorisation de
  l'article** (KG, TONNE, ML, UNITE — unité du CMP) ; **B. unité du prix
  saisi** (conservée avec le prix : 2 500,5 DT/TONNE, 2,80 DT/KG,
  1,50 DT/ML, 5 DT/UNITE) ; **C. unité physique** (kg, tonne, m, pièce —
  règles inchangées) ; **D. unité de calcul** (conversion exacte B → A au
  moment du calcul, sans arrondi).
- Le **CMP reste exprimé dans l'unité de valorisation de l'article** ; les
  lots peuvent avoir des prix dans une autre unité compatible, convertis
  exactement.
- **Régularisation fournisseur**, **coût d'affaire**, **chutes** (CMP exact,
  jamais le CMP affiché arrondi), **inventaire initial** : même principe.
- Un prix **plus fin que le millime dans sa propre unité** (ex.
  2 500,5005 DT/t) reste refusé : la représentation monétaire globale
  (Phase 4.1) n'est pas modifiée (Proposition B non retenue).

Mise en œuvre : migration 0020, `docs/PRIX_REVIENT.md` §6.

## 19. Transport estimatif d'une ligne de devis / commande — DÉCISION VALIDÉE (Phase 5.6, analyse, 30/09/2026)

Décision de l'utilisateur (réponse au point 3 de l'analyse 5.6) : « le prix
de transport sera affecté par tonnes. Si on a des articles dont l'unité de
vente est différente (soit unité ou ML par exemple), il faut me demander le
prix de transport de cette ligne à remplir manuellement. »

- Le prix de transport estimatif est un **prix par tonne** (DT/t).
- **Ligne vendue au poids** (en tonnes, §15) : transport de la ligne =
  poids de vente de la ligne en tonnes × prix de transport par tonne ;
  montant arrondi une seule fois au millime (§17).
- **Ligne vendue dans une autre unité** (pièce/UNITE, ML…) : le transport
  n'est **pas calculé** ; le système **demande** à l'utilisateur le prix de
  transport de cette ligne, **saisi manuellement**. Il ne le devine jamais
  (pas de conversion silencieuse pièces/ml → tonnes).
- Portée : transport **estimatif** du devis / de la commande. Le transport
  réel du bon de livraison (`bl_client.prix_transport_reel_minor`, jamais
  le théorique) n'est pas concerné par cette décision.

Précisions validées par le cahier « Phase 5.6 — analyse technique
finale » (§9, 30/09/2026) :

- le transport estimé se gère **ligne par ligne** ; le prix DT/t est saisi
  par ligne, **jamais** globalement pour tout le devis ;
- vente au poids : poids vendu converti en tonnes × DT/t, arrondi une seule
  fois au millime ;
- autre unité (pièce, ML, M² ou autre) : jamais de conversion automatique
  en tonnes ; l'utilisateur saisit directement le **montant total** du
  transport de la ligne ;
- la saisie du transport est **obligatoire** pour valider la ligne ; un
  transport égal à 0 n'est autorisé que si l'utilisateur saisit
  explicitement 0.

Mise en œuvre proposée : `docs/ANALYSE_PHASE_5_6.md`, en attente de
validation.

Devise : D3 et N5 (§20, §21) mettent le transport estimé en **EUR**. La
mention « DT/t » ci-dessus se lit donc **EUR/t** ; en autre unité, le
montant total est saisi en EUR. L'arrondi « au millime » ci-dessus vaut
pour le TND ; un montant en EUR s'arrondit **au centime** (K13, §22).

**Mise à jour (02/10/2026).** Ligne vendue en **KG** : transport = KG ÷
1 000 × EUR/t (P-KG-TR, §23). Le transport hors poids et le poids de la
ligne sont saisis sur la ligne du devis (Y2, §23). Après la confirmation
de la commande, le transport estimé n'est **plus recalculé**, même en cas
d'avenant ; pas de transport estimé sur un supplément (C3, §25).

## 20. Affaires — décisions D1 à D6 VALIDÉES (Phase 5.6, 30/09/2026)

Source : message « Phase 5.6 — validation finale des décisions D1 à D6 ».
Détail et mise en œuvre proposée : `docs/ANALYSE_PHASE_5_6.md`.
Décisions complémentaires N1 à N15 : §21. Réponses définitives K1 à K22 :
§22. Les points O1 à O9, ouverts le 30/09, sont **tranchés** : §23.

**D1 — Compatibilité lot ↔ ligne de commande.** Un lot peut servir une
ligne si les trois conditions sont réunies :

1. même article ;
2. même finition, sauf NOIR/LAC → GALVA et NOIR/LAC → GPP ;
3. même longueur, sauf les **multiples exacts** (12 m peut servir
   2 × 6 m).

Toute autre compatibilité est refusée pour le moment ; aucune autre règle
ne doit être inventée. LAC = NOIR dans le logiciel.

**Mise à jour (02/10/2026).** Le point 3 est précisé par la règle
définitive du §24 : la seule équivalence de longueur est **12 m → 2 × 6 m**,
à finition identique, sans transformation ; le sens inverse (6 m → 12 m)
est interdit ; aucune autre conversion (12 → 4, 12 → 3, 6 → 3…) n'est
validée pour le moment : chacune demanderait une décision métier séparée.

**Correction validée (message N1 à N15).** D1 s'applique lorsque l'état
**réel** du lot correspond à la ligne. Sinon, une transformation est
nécessaire. Un lot brut (ex. NOIR 12 m) n'est **pas** un lot GALVA ou GPP
avant transformation. Le processus est :

1. stock brut ;
2. envoi au transformateur ;
3. transformation réelle ;
4. réception dans le nouvel état ;
5. **nouveau lot** transformé, avec traçabilité vers le lot brut ;
6. affectation et vente selon les caractéristiques réelles du nouveau lot.

Le résultat peut être tout résultat de transformation réellement effectué
(GALVA 6 m, GPP 6 m, GPP 12 m…). La conciliation de cette correction avec
les exceptions de D1 ci-dessus (affectation seulement sur un état
identique ; exceptions réalisées **par transformation**) est **validée**
(K2, §22) : D1 ne concerne que la compatibilité directe d'un lot déjà dans
l'état commercial demandé ; le chemin par transformation est autorisé si
la transformation prévue le permet réellement.

**D2 — Poids commercial.**

- **Vente en TONNE** : poids calculé automatiquement avec la méthode
  validée pour l'article, c'est-à-dire la masse validée de la MV
  enregistrée dans la fiche article. Sans masse validée, le système
  n'invente ni ne déduit aucune formule : l'article doit d'abord être créé
  ou complété avec sa masse validée.
- **Vente en PIÈCE, ML, M² ou autre unité** : poids commercial saisi
  manuellement. **Mise à jour (CT20, §23)** : la vente en KG est une
  vente au poids, à poids calculé comme en TONNE ; un poids déclaré à la
  main n'est permis qu'en NOIR/LAC hors vente au poids.
- **GALVA** : poids commercial = poids de base calculé + % GALVA
  applicable. Formule précisée au §21 (N3). **GPP** : majoration fixe de
  2 % (§21, N4).

**D3 — Devises.** Prix de vente : **EUR** ; prix d'achat estimé :
**TND** ; transport estimé : **EUR**. Chaque prix a sa propre devise et
sa propre unité de prix (pas de devise unique partagée). Le taux de change
n'est utilisé que lorsqu'une conversion est réellement nécessaire.

**D4 — Modification d'une commande confirmée.** Les commandes confirmées
sont régulièrement ajustées (ajout d'articles, ajustement d'articles
commandés). La modification est **historisée** :

- la valeur originale n'est jamais écrasée sans trace ;
- ancienne et nouvelle valeur conservées ;
- utilisateur, date et heure, motif si requis ;
- historique complet ;
- situation de l'affaire recalculée ;
- allocations existantes jamais cassées ;
- aucun mouvement physique de stock pour une modification commerciale.

Cas couverts : ajout de ligne, augmentation, diminution, ligne
partiellement livrée, ligne affectée à un ou plusieurs lots (règles
précises : points N6 à N9).

**D5 — Choix des lots et stock chez le galvanisateur.**

- Le système calcule la disponibilité réelle et **ne choisit jamais
  automatiquement** les lots. Le choix est manuel, par l'utilisateur
  autorisé. Aucun FIFO.
- On distingue localisation physique, allocation commerciale, stock
  disponible et stock affecté.
- Un envoi chez le galvanisateur peut ne pas être entièrement affecté. Les
  pièces non affectées chez le galvanisateur :
  - restent du stock GMC ;
  - sont localisées chez le galvanisateur ;
  - sont affectables ou réservables à une nouvelle affaire avant leur
    réception chez GMC ;
  - ne sont jamais comptées comme stock de l'entrepôt GMC.
- Catégories :
  - A. disponible chez GMC ;
  - B. chez le galvanisateur ;
  - C. chez le galvanisateur, affecté ;
  - D. chez le galvanisateur, non affecté ;
  - E. envoyé, en attente de réception ;
  - F. transformé, disponible chez le galvanisateur.
- Une affectation ne crée **aucun mouvement physique** ni aucune
  réception.
- **Note (K1, K2, §22).** Le lot transformé n'entre dans le stock GMC
  qu'au bon de réception de transformation ; avant, la situation chez le
  transformateur est **virtuelle** (calculée à partir du stock physique
  qui s'y trouve). Le lot transformé n'est commercialement compatible
  qu'après réception. Affecter la production attendue d'une
  transformation en cours (les 40 pièces de l'exemple, catégorie F) :
  point **O4**, non tranché le 30/09.
- **Mise à jour (02/10/2026).** O4 est **tranché** : affectation
  commerciale possible chez le transformateur, vente seulement après la
  réception (O4, X3, §23 ; pièce en trop d'une transformation : L-u, §25).

**D6 — Compte SUPERADMIN.** Mohamed est le compte **SUPERADMIN**. Les
droits réservés (« Mohamed seul » dans les règles de la Phase 5.6) sont
liés au **compte et à son rôle système**, jamais au nom affiché.

## 21. Affaires — décisions N1 à N15 (Phase 5.6, 30/09/2026)

Source : message « Phase 5.6 — mes décisions définitives N1 à N15 ».
Précisions définitives K1 à K22 : §22.

### Fiche article et poids

- **N1 — Méthode de poids unitaire validée.**
  - La MV existante est la base de départ de la liste matière. La fiche
    article est construite et fiabilisée progressivement.
  - Les masses linéiques de la MV (ex. IPE100, UPN200) doivent être
    **vérifiées** avant de devenir des valeurs de référence.
  - Pour les tôles planes et les fers plats FP, le système **compare** les
    valeurs disponibles, **Mohamed décide et valide** la valeur de
    référence, et cette valeur est enregistrée dans la fiche article. Elle
    est ensuite utilisée pour les étapes suivantes.
  - La première validation des masses est une **étape de fiabilisation du
    référentiel article**.
  - Le système n'invente jamais une masse et ne choisit **jamais
    silencieusement** entre plusieurs valeurs.
  - Méthodes possibles, selon la nature de l'article : kg/ml, kg/m²,
    kg/pièce, ou autre méthode explicitement validée dans la fiche article.
- **N2 — Vente en TONNE.** L'article doit obligatoirement être établi
  dans la fiche avec une méthode de poids unitaire validée. Il ne doit donc
  **normalement** pas exister de vente en TONNE avec une donnée de poids
  manquante si la fiche est correctement établie. Aucune formule inventée.
  La saisie manuelle d'un poids ne doit pas servir à **contourner**
  l'absence de méthode validée.
- **N3 — GALVA.**
  - Le % GALVA est saisi manuellement **pour chaque article**.
  - Poids GALVA = poids brut × (1 + % GALVA ÷ 100).
  - Exemple validé : IPE100 6 m brut = 8,1 kg/ml × 6 m = 48,6 kg par
    barre ; GALVA 6 % = 8,1 × 6 × 1,06 = 51,516 kg par barre.
  - **Mise à jour (02/10/2026).** La formule ne change pas. Le % est
    **saisi sur chaque ligne GALVA** : celui de la fiche article est
    proposé, l'utilisateur le garde ou le change (L-h, L-h bis, §25).
- **N4 — GPP.** Majoration **fixe de 2 %**, intégrée au calcul
  conformément à la règle métier déjà discutée ; ne pas la remplacer par
  0 %. **Mise à jour (01/10/2026)** : le 2 % est un réglage unique,
  modifiable par le SUPERADMIN seul, avec date d'effet (CT4, §23).

### Devises et taux

- **N5.**
  - Prix d'achat matière : **TND**. Coûts de transformation (GALVA, GPP) :
    **TND**. Prix de vente : **EUR**. Transport estimé : **EUR**.
  - Lors de la préparation du devis, **Mohamed désigne le taux de change**
    utilisé pour convertir les coûts nécessaires au devis. Ce taux de devis
    (prévisionnel) est historisé. **Remplacé par K5 (§22)** : le taux est
    saisi manuellement par l'utilisateur commercial autorisé qui prépare
    le devis, puis figé après validation de l'offre.
  - Transport : vente en TONNE → EUR/t × poids vendu en tonnes ; vente en
    PIÈCE, ML, M² ou autre → montant **total** du transport saisi
    directement en EUR ; aucune conversion cachée en tonnes. **Mise à
    jour (P-KG-TR, §23)** : vente en KG → KG ÷ 1 000 × EUR/t.

### Commande confirmée (avenants)

- **N6.** La quantité originale est conservée. Les avenants peuvent
  produire une quantité en vigueur. Ce qui dépasse la quantité **originale** reste un
  **supplément** et suit la règle CMP. **Mise à jour (O1, §23)** : une
  quantité ajoutée par avenant est une quantité **normale** ; le
  supplément est ce qui dépasse la quantité **en vigueur**.
- **N7.** Une commande peut être diminuée.
  - Les marchandises déjà réceptionnées et validées qui ne servent plus ne
    sont pas supprimées : elles deviennent du stock GMC disponible selon
    leur localisation et leur état réel.
  - Pour une marchandise affectée, l'utilisateur choisit **explicitement**
    l'affectation à réduire ou libérer. Le système ne choisit jamais.
  - Tout est historisé et audité.
- **N8.**
  - Si l'article, la finition et les autres caractéristiques commerciales
    sont identiques, le prix de vente ne change pas **simplement parce
    qu'une nouvelle ligne apparaît** dans la même commande : une nouvelle
    ligne identique conserve le prix applicable de la commande.
  - À la facturation, les lignes compatibles peuvent être regroupées, sans
    jamais supprimer l'historique des lignes de commande.
  - Une autre commande peut avoir un autre prix.

### Droits

- **N9.** Les décisions stratégiques et les opérations sensibles sont
  réservées au SUPERADMIN (Mohamed) et toujours auditées :
  - comptes utilisateurs, rôles et droits, tâches et permissions ;
  - modifications stratégiques, corrections ;
  - codage, mises à jour de version, améliorations ;
  - validation des évolutions importantes.
- **N10.** Pour le moment, **seul le SUPERADMIN** effectue les
  affectations. Le mécanisme permettra une délégation ultérieure à
  d'autres utilisateurs autorisés. « Ne pas imposer dès maintenant le rôle
  COMMERCIAL. » (Aucune délégation actuellement : K8, §22.)
- **N14.** Il existe **actuellement** un seul SUPERADMIN : Mohamed. Il est identifié par
  son compte et son rôle système, jamais par le nom affiché. **Mise à
  jour (CT1, §23 ; L-f, §25)** : exactement un seul SUPERADMIN, imposé
  par l'application et par la base ; il ne peut être ni désactivé ni
  changé de rôle.

### Stock

- **N11.** Les allocations et réservations conservent la localisation
  physique : GMC, galvanisateur, autres emplacements autorisés.
  L'affectation commerciale ne change **jamais** la localisation.
- **N12.** La logique complète de transformation est développée en Phase
  5.8. La Phase 5.6 n'invente aucune logique de réception ou de
  transformation.
- **N13.** Aucun mouvement physique ne doit pouvoir faire passer le stock
  physique disponible sous la quantité déjà affectée (garde-fou).
- **N15.** Remplacé par la correction de D1 (§20) : une combinaison du
  type NOIR 12 m → GALVA 6 m est un chemin de transformation, pas une
  affectation directe. Formulation définitive « Transformation et
  changement d'état » : §22.


## 22. Affaires — réponses définitives K1 à K22 (Phase 5.6, 30/09/2026)

Source : message « Phase 5.6 — réponses définitives aux questions K1 à
K22 ». Ces décisions **remplacent** toute interprétation précédente
contraire. Décisions encore ouvertes (O1 à O9 ; O6 déplacée en choix
technique CT7), confirmations C et choix techniques CT1 à CT15 (aucun
validé) : `docs/ANALYSE_PHASE_5_6.md` §5.

**Mise à jour (02/10/2026).** Cette liste de points ouverts date du
30/09. Depuis : O1 à O9 tranchés, CT1 à CT21 validés (§23), propositions
C tranchées (§25). Ce qui reste ouvert est au §27.

### Transformation et compatibilité

- **K1 — Flux de transformation.**
  - Le flux obligatoire est :
    1. bon de sortie GMC → transformateur ;
    2. marchandises physiquement chez le transformateur ;
    3. préparation/réception prévue selon les quantités attendues ;
    4. **bon de réception de transformation** → retour dans le stock GMC.
  - Le lot transformé n'est **pas** considéré comme physiquement revenu
    chez GMC avant le bon de réception.
  - Entre sortie et réception, le système doit pouvoir représenter
    **virtuellement** la situation du stock chez le transformateur.
    Exemple : bon de sortie de 100 pièces → GMC −100, transformateur +100
    pièces physiques ; leur réception finale est attendue ; les quantités
    prévues/réceptionnables peuvent être calculées virtuellement **à
    partir du stock physique chez le transformateur**. Cette situation
    intermédiaire est traçable et calculable, mais ne constitue pas
    encore une réception GMC.
  - À la réception : réception conforme, nouvelles caractéristiques,
    création et entrée du lot transformé dans le stock GMC. Exemple :
    NOIR 12 m → sortie → transformation → réception → GALVA 6 m en stock
    GMC.
- **K2 — Compatibilité.**
  - D1 = compatibilité **directe** d'un lot déjà dans l'état commercial
    demandé : NOIR 12 m n'est pas directement compatible avec GALVA 6 m.
  - Le chemin NOIR 12 m → transformation → GALVA 6 m est autorisé si la
    transformation prévue le permet réellement.
  - Une transformation peut modifier la finition, la longueur, la
    quantité, le poids et l'état commercial.
  - Le lot brut est l'**origine traçable**. Le lot transformé devient un
    **nouveau lot commercialement compatible après réception**.
  - Si la transformation consiste réellement à couper/transformer le
    produit, le nouveau lot a sa nouvelle longueur, sa nouvelle quantité,
    son nouveau poids, sa nouvelle finition/état et sa traçabilité vers
    le lot d'origine. Un lot brut de 12 m n'est **jamais** considéré comme
    directement disponible en 6 m.
  - **REMPLACÉ le 02/10/2026 (LG8, §24)** — la dernière phrase ci-dessus
    n'est plus vraie à finition identique. Nouvelle règle : « Un lot 12 m
    peut servir une ligne 6 m à finition compatible identique selon
    l'équivalence 1 × 12 m = 2 × 6 m. Cette compatibilité n'est pas une
    transformation industrielle. » La phrase reste vraie quand la
    finition change (NOIR 12 m → GALVA 6 m passe par une transformation).
- **N15 (reformulé).** Transformation et changement d'état : le nouveau
  lot a ses propres caractéristiques, quantité, longueur, poids,
  finition, localisation et traçabilité ; le lot d'origine reste
  historiquement traçable.

### Quantités et avenants

- **K3 — Quantités.**
  - La quantité originale reste **fixe** dans l'historique ; elle n'est
    jamais écrasée ni transformée après coup.
  - Pendant l'exécution de la commande et le suivi d'avancement, le
    SUPERADMIN **peut** modifier la quantité à livrer par **avenant**.
  - À distinguer : quantité originale, quantité actuellement demandée / en
    vigueur, quantités ajoutées ou diminuées par avenant, quantités déjà
    livrées, reste à livrer, quantité supplémentaire éventuelle.
  - Exemple : 100 initiales + 20 par avenant = 120 en vigueur. Le système
    ne transforme **jamais** rétroactivement les 100 en 120.
  - Valorisation des quantités ajoutées par avenant (supplément au CMP ou
    quantité normale) : **non tranchée** le 30/09, point O1 de
    `docs/ANALYSE_PHASE_5_6.md`. **Tranchée depuis (O1, §23)** : quantité
    normale.
- **K9 — Avenants.**
  - Toute modification après validation de la commande est un avenant,
    réservé au SUPERADMIN.
  - Il conserve : ancienne valeur, nouvelle valeur, utilisateur, date et
    heure, motif, **impact**, historique.
- **K10 — Lignes identiques.**
  - Identique = même article, finition, longueur, unité de vente et autres
    caractéristiques nécessaires.
  - Une nouvelle ligne identique conserve le prix applicable de la
    commande, et ne modifie jamais automatiquement le prix d'une ligne
    existante.
  - Nouvelle négociation → nouveau prix historisé, avec date d'effet ;
    l'ancienne condition est conservée. **REMPLACÉ par Y5 (§23)** : pas
    de renégociation du prix de vente après la confirmation de la
    commande ; elle se fait avant, au stade du devis.
  - Regroupement possible à la facturation, sans perte d'historique.
- **K13 — Diminution.** Autorisée, jamais sous la quantité déjà livrée.
  Une marchandise devenue inutile reste du stock GMC disponible, selon
  son emplacement et son état.
- **K15 — Situation.** Distinguer toujours : quantité originale, quantité
  en vigueur, quantités ajoutées, supplément, livré, reste à livrer.
- **K21 — Avenant.**
  - Cas 1, article déjà dans la première version de la commande : aucune
    intervention particulière sur la méthode de calcul de la ligne ; les
    règles existantes de la ligne s'appliquent, sans refaire
    **inutilement** toute la logique de la commande.
  - Cas 2, nouvel article : la nouvelle ligne est recalculée entièrement
    (article, finition, longueur, unité, quantité, poids, prix, coût
    matière, coût de transformation, transport, taux de change du devis
    ou de la commande selon son contexte, autres données commerciales).
  - L'ancienne commande reste historiquement intacte.
  - **Mise à jour (02/10/2026).** Le taux est toujours celui du devis
    validé et gelé (Y6, §23 ; Y6-L, §25). Pour le **transport estimé**
    d'une ligne ajoutée par avenant, K21 (« recalculée entièrement, …
    transport ») et C3 (« plus recalculé, même en cas d'avenant », §25)
    ne disent pas la même chose : **point ouvert**, §27.

### Devis, devises et taux

- **K4 — Prix de revient estimé du devis.**
  - **Prix de revient estimé (EUR) = (prix d'achat matière TND + prix de
    transformation TND) ÷ taux de change prévisionnel + transport estimé
    EUR.**
  - Exemple : (2 000 + 300) ÷ 3,40 + 50 = 726,470588… EUR.
  - Le coût de transformation est saisi **manuellement** par article, sur
    chaque ligne concernée ; pas de récupération automatique obligatoire
    d'une grille.
  - Pas d'arrondi intermédiaire inutile ; arrondi final selon la devise.
  - Cette méthode concerne le devis (coût estimé). Elle ne remplace pas le
    coût réel ni la marge analytique (phases ultérieures).
- **K5 — Taux de change prévisionnel.**
  - Un utilisateur commercial autorisé peut préparer un devis. Il
    **saisit manuellement** le taux de change prévisionnel : le taux qu'il
    décide d'utiliser le jour de préparation de son devis.
  - Le taux est enregistré et historisé avec le devis.
  - Après validation de l'offre : taux **figé**, le devis conserve le
    taux utilisé ; l'utilisateur commercial ne peut plus le modifier ;
    aucune modification par un utilisateur opérationnel ; seul le
    SUPERADMIN peut intervenir, selon les règles de modification
    stratégique déjà validées. **Mise à jour (L-t, §25)** : aucune
    modification exceptionnelle du taux n'est développée en 5.6.
  - Pas de système où le commercial doit sélectionner un taux prédéfini
    existant.
  - Ce que recouvre « utilisateur commercial autorisé » (rôle ou
    permission) et le moment exact de la « validation de l'offre » :
    points O5 et O3 de `docs/ANALYSE_PHASE_5_6.md`, **tranchés** depuis
    (§23). Convention du taux : TND pour 1 EUR (Y3, CT5, §23).
- **K22 — Devises imposées** selon le type de prix : vente EUR, achat
  matière estimatif TND, coût estimatif de transformation TND, transport
  estimatif EUR. Elles peuvent être préremplies automatiquement et ne
  sont **pas librement modifiables** par l'utilisateur.

### Arrondi

- **K13 — Monnaies.** TND en millimes, EUR en centimes. Calculs
  intermédiaires en précision complète ; arrondi uniquement au montant
  final, selon la devise.

### Poids et référentiel article

- **K6 — Autres unités.** Pour une vente en PIÈCE, ML, M² ou autre unité
  autorisée, le poids peut être déterminé manuellement selon les règles
  validées. **Mise à jour (CT20, §23)** : poids déclaré seulement en
  NOIR/LAC hors vente au poids ; le KG est une vente au poids.
- **K7 — Référentiel article.**
  - Les masses sont vérifiées **progressivement** par l'utilisation réelle.
    Le système permet d'améliorer progressivement le référentiel jusqu'à
    obtenir une version complète et fiable.
  - Pour un article : comparer les valeurs existantes, ne jamais choisir
    silencieusement, présenter les références disponibles, validation par
    le SUPERADMIN, enregistrement de la valeur retenue et de son
    historique.
  - Le projet n'est pas bloqué en exigeant tout de suite la validation de
    toutes les masses.
- **K18 — Vente en TONNE.**
  - Poids calculé automatiquement selon la méthode validée ; aucune saisie
    manuelle arbitraire.
  - Si la méthode manque : le système demande de compléter et valider le
    référentiel.
  - **Mise à jour (Y4, CT20, §23)** : même règle pour une vente en KG.
- **K19 — GPP.**
  - GPP est une finition distincte de GALVA : poids GPP = poids brut ×
    1,02 (fixe actuellement).
  - Jamais cumulé avec le % GALVA : NOIR/LAC → GPP = +2 % ; NOIR/LAC →
    GALVA = % GALVA.
  - **Mise à jour (CT4, §23)** : le 2 % est un réglage global historisé,
    pas une constante du code ; même valeur aujourd'hui.
- **K20 — % GALVA.**
  - 0 % = état brut de la matière.
  - Trois cas distincts : % défini, 0 % défini, % non renseigné. Un % non
    renseigné n'est **jamais** transformé automatiquement en 0 %.
  - Vente GALVA sans % renseigné et validé → le système demande de
    compléter le référentiel.
  - **MODIFIÉ le 02/10/2026 (L-h, L-h bis, §25)** : le % de la fiche
    article est **proposé** sur la ligne ; l'utilisateur le garde ou le
    change ; un écart est signalé, jamais bloqué. Sur une ligne GALVA, le
    % est obligatoire et strictement supérieur à 0 (0 % reste l'état
    brut, donc interdit pour du GALVA). Un % non renseigné n'est toujours
    jamais transformé en 0 %. La puce précédente (« sans % renseigné et
    validé → compléter le référentiel ») devient : sans % sur la ligne,
    la ligne GALVA ne peut pas être validée (L-h bis) ; la validation
    préalable du % par le SUPERADMIN n'est plus exigée (§26).

### Stock et droits

- **K11 — Emplacements.**
  - GMC, chaque transformateur ou galvanisateur, autres emplacements
    nécessaires.
  - Localisation physique ≠ affectation commerciale ; une allocation n'est
    jamais un mouvement physique.
- **K12 — Contrôles.**
  - Le système calcule la disponibilité réelle et empêche les doubles
    affectations incompatibles, les allocations au-delà du disponible
    réel et les mouvements incompatibles avec les quantités affectées.
  - Il ne choisit jamais automatiquement les lots.
- **K8, K16 — SUPERADMIN.**
  - Actuellement un seul SUPERADMIN : Mohamed. **Mise à jour (CT1, §23)** :
    exactement un seul, imposé par l'application et par la base.
  - Droits déterminés par le compte utilisateur et le rôle/permission, et
    **non simplement** par le nom affiché.
  - L'architecture doit permettre qu'à l'avenir Mohamed puisse
    céder/déléguer ces pouvoirs à une autre personne jugée apte ; cette
    délégation future est prévue architecturalement ; **aucune
    délégation** actuellement.
- **K17 — Corrections d'inventaire.**
  - Opérations sensibles réservées au SUPERADMIN ; toute correction doit
    être justifiée, auditée, traçable.
  - Une correction d'inventaire doit **obligatoirement** être accompagnée
    d'un **PV signé par la Direction Générale** ; le système conserve la
    référence/trace de ce PV dans l'audit de l'opération.
  - Une correction ne permet jamais de modifier silencieusement
    l'historique physique.
  - Modifie le service `corriger_inventaire` validé en 5.5 (aucun
    contrôle de rôle aujourd'hui).

### Portée de la phase

- **K14.** « Aucun nouveau point métier à ouvrir. Les règles déjà validées
  doivent simplement être intégrées dans les services et tests
  correspondants. » Les points O1 à O9 de `docs/ANALYSE_PHASE_5_6.md`
  §5.2 ne créent pas de nouvelle règle : ce sont des questions
  d'application des règles ci-dessus, laissées ouvertes jusqu'à ta
  réponse. **Réponses reçues** : §23.

## 23. Affaires — décisions O, X, Y, CT et P (Phase 5.6, du 30/09 au 02/10/2026)

Ces décisions ont été prises pendant les analyses v5 à v9. Elles étaient
consignées dans les analyses et **reportées ici le 02/10/2026**. Le détail
(tes mots, les exemples, les cas de test) reste dans
`docs/ANALYSE_PHASE_5_6_v9.md` : §0, §0 bis, §0 ter, §16, §18, §21, §26.
Dans cette section, « V » désigne la quantité **en vigueur** d'une ligne
(quantité originale + avenants).

### O1 à O9 — tranchés

| Repère | Règle |
|---|---|
| O1 | Une quantité ajoutée par avenant est une quantité **normale**, identifiable. Le supplément est ce qui dépasse V. |
| O2 | Un avenant utilise le taux de change de la préparation du devis initial ; aucun nouveau taux. Confirmé par Y6. |
| O3 | « Validation de l'offre » = devis à l'état CONFIRMÉ : taux et conditions figés ; le SUPERADMIN seul peut intervenir ensuite. |
| O4 | Affectation commerciale possible sur une marchandise chez le transformateur ; vendable seulement après la réception. Mise en œuvre : X3. |
| O5 | Comptes et accès définis par le SUPERADMIN, par utilisateur, par module et par permission si nécessaire. Le rôle COMMERCIAL ne donne pas automatiquement tous les droits commerciaux. |
| O6 | Supprimé : devenu le choix technique CT7. |
| O7 | Vente hors poids (ni KG ni TONNE) : poids déclaré obligatoire, saisi au devis, final, jamais majoré. Il sert au poids final, au prix de revient estimatif et, plus tard, à la répartition du transport réel. Poids déclaré seulement en NOIR/LAC (CT20). |
| O8 | Cas A : lot existant, coût réel, aucun achat (affectation en 5.6). Cas B : nouvelle commande fournisseur, nouveau lot, nouveau coût ; le prix initial n'est jamais écrasé ; le prix de vente n'est pas modifié. La partie fournisseur relève de la 5.7. |
| O9 | Emplacements : GMC et les transformateurs ; d'autres emplacements seulement au besoin réel. |

### X1 à X9

| Repère | Règle |
|---|---|
| X1 | **Remplacé par Y5** (plus de nouveau prix après confirmation). |
| X2 | Transport saisi en EUR/t. Vente en tonne : EUR/t × tonnes. Autre unité : aucun poids implicite, montant total en EUR saisi à la main. Précisé par Y2 et P-KG-TR. |
| X3 | Affectation en 5.6 sur un besoin et une marchandise identifiés, même chez le transformateur. Aucun lot transformé en 5.6 ; rattachement au lot résultant en 5.8. Jamais un mouvement. |
| X4 | Opérations stratégiques de la 5.6 réservées au SUPERADMIN. Délégation future prévue, aucune supplémentaire active. Droits liés au compte et aux permissions, pas au nom. |
| X5 | Coût en EUR = montant en TND converti au taux de l'affaire. Précisé par Y3 : le taux se saisit en TND pour 1 EUR, donc coût EUR = montant TND ÷ taux, calcul exact. |
| X6 | Clôture avec reliquat en une opération contrôlée : demande, calcul, affichage, confirmation, libération, motif. Le reliquat n'est jamais converti en livraison. Précisé par CT19. |
| X7 | Taux saisi, historisé, figé pour l'affaire, utilisé pour les avenants ; jamais remplacé à chaque avenant. |
| X8 | % GALVA obligatoire dans la référence article (décision du 30/09). La partie « GALVA hors tonne » est sans objet depuis Y4. Depuis le 02/10, le % est saisi sur la ligne et celui de la fiche est seulement proposé (L-h, §25) ; si la fiche est vide ou à 0 %, rien n'est proposé et l'utilisateur saisit un % supérieur à 0. |
| X9 | Un supplément reste un supplément : jamais requalifié, ni automatiquement ni rétroactivement. Maintenu par CT17. Une réaffectation vers une autre affaire crée une **nouvelle** affectation, typée à la destination (C8 bis, §25) : ce n'est pas une requalification de l'affectation d'origine. |

### Y1 à Y6

| Repère | Règle |
|---|---|
| Y1 | Un lot brut encore chez GMC peut être **réservé** pour une ligne d'un autre état dès la commande confirmée. La transformation prévue est déclarée à la réservation. |
| Y1 bis (a) | La réservation d'un lot brut **bloque réellement** le disponible : 100 barres, 25 réservées → disponible 75, stock physique toujours 100. Aucun mouvement. |
| Y1 bis (b) | Au bon de sortie transformation (BST), le système compare le résultat prévu à la réservation : identique → conversion ; différent → BST refusé. Aucun choix automatique. **Modifié par L-s (§25)** : un BST peut exécuter une partie seulement de la réservation. |
| Y1 bis (c) | « Confirmation client » = commande client confirmée. |
| Y1 bis (d) | Seul le SUPERADMIN peut réserver. |
| Y1 bis (mécanisme) | La réservation reste dans l'historique ; une nouvelle affectation liée est créée au BST ; le lien réservation → affectation est traçable. |
| Y2 | Transport prévisionnel hors poids : montant total en EUR **et** poids de la ligne saisis sur la ligne du devis. Le transport final, connu après facturation, sera réparti au poids pour la marge par article (5.9 / 5.10). |
| Y3 | Le commercial saisit le taux en **TND pour 1 EUR** (exemple : 3,40). |
| Y4 | La galvanisation ne concerne que des lignes vendues en **KG ou en TONNE**. Même règle pour le GPP. Le contrôle porte sur l'unité de vente de la ligne. Le KG est une vente au poids, comme la tonne. |
| Y5 | Pas de renégociation du prix de vente après confirmation : « commande confirmée, prix de vente confirmé ». La négociation se fait avant, au stade du devis. Une **erreur** de prix après confirmation se corrige par le SUPERADMIN, avec motif et audit ; ce n'est pas une renégociation (CT10). |
| Y6 | Tous les avenants d'une commande confirmée utilisent le taux du devis validé et gelé. Libellé confirmé le 02/10 (Y6-L, §25). |

### CT1 à CT21 — choix techniques validés le 01/10/2026

| Repère | Contenu retenu |
|---|---|
| CT1 | Exactement **un seul SUPERADMIN**, imposé par l'application et par la base ; un deuxième est refusé. |
| CT2 | Comptes, permissions, modules et droits par compte et par module créés dès la 5.6. Droits initiaux = situation actuelle. Aucune délégation supplémentaire active ; architecture prête pour une délégation future sans refonte. Le rôle « commercial » ne donne pas automatiquement tous les droits commerciaux. Les opérations sensibles demandent une permission explicite. |
| CT3 | Historique jamais modifié des validations des valeurs article (masse, méthode de poids, unité, sources, auteur, date, motif). La masse actuelle de la fiche est une « valeur MV à vérifier ». Une vente à poids calculé ne peut pas utiliser une masse non validée. SUPERADMIN seul. Jamais rétroactif sur un devis ou une commande confirmés. **Pour le % GALVA : modifié par L-h (§25).** |
| CT4 | GPP = réglage unique en base, 2 % aujourd'hui, commun à tous les articles, modifiable par le SUPERADMIN seul, avec date d'effet. Les devis et commandes confirmés gardent le taux utilisé. |
| CT5 | Taux saisi à la main en TND pour 1 EUR ; chaque saisie est une nouvelle valeur, jamais modifiée ni supprimée, avec auteur et date ; taux conservé tel que saisi, jamais arrondi ; figé à la confirmation. Modification exceptionnelle par le SUPERADMIN (décision du 01/10) : nouveau taux, motif obligatoire, audit complet, sans effet sur les avenants (Y6). **Cette fonction n'est pas développée en 5.6 (L-t, §25).** |
| CT6 | Prix de revient calculé sur le total de la ligne ; un seul arrondi final au centime EUR ; revient unitaire affiché = total ÷ quantité. **Photo complète et figée** à la confirmation. |
| CT7 | « Transformation prévue : OUI / NON » sur chaque ligne de devis. Si OUI, coût obligatoire (0 seulement s'il est saisi) ; si NON, aucun coût. GALVA et GPP imposent une vente en KG ou TONNE. |
| CT8 | L'unité du coût de transformation est conservée avec le coût : TND/t, TND/kg, TND/pièce, TND/ml ou montant total de la ligne. |
| CT9 | Coûts estimés recopiés du devis vers la commande ; saisis dans l'avenant pour un article ajouté ; jamais pré-remplis depuis un ancien achat. Prévision commerciale ≠ coût réel. |
| CT10 | Une seule table d'avenants, jamais modifiée : ancienne et nouvelle valeur, motif, auteur, date, impact quantitatif et financier avant/après. Même mécanique pour les interventions exceptionnelles du SUPERADMIN sur une commande confirmée. Aucun avenant de prix après confirmation ; une erreur de prix se corrige par le SUPERADMIN, avec motif obligatoire et audit complet : ce n'est pas une nouvelle négociation. Ligne au poids : un avenant de quantité recalcule le poids par la méthode validée. |
| CT11 | Aucun mouvement physique ne fait passer le stock disponible sous l'affecté ou le bloqué ; contrôle dans l'application et dans la base. |
| CT12 | La marchandise envoyée en transformation et non réceptionnée se calcule à partir du stock physique chez les transformateurs. |
| CT13 | Lot brut non réservé : signal « utilisable après transformation », informatif seulement. |
| CT14 | Correction d'inventaire : référence et date du PV signé par la Direction Générale, auteur, date, audit complet ; SUPERADMIN obligatoire. |
| CT15 | Migration de la 5.6 : tout ou rien, additive, sans suppression ni réécriture destructrice, données reprises, tests existants préservés. |
| CT16 | Ligne ajoutée par avenant marquée AVENANT, quantité initiale 0 ; la situation montre « 0 initial + X ajouté ». |
| CT17 | Type d'affectation fixé à la création : NORMALE tant que le cumul normal ne dépasse pas V ; au-delà, SUPPLÉMENT avec motif ; jamais requalifié. (« NORMALE » est le libellé ; le code existant dans la base reste INITIALE, cf. §1.) |
| CT18 | Résultat attendu renseigné à l'établissement du BST. État de retour imposé : galvanisation → GALVA ; GPP → GPP. Conversion de longueur exacte (25 × 12 m → 50 × 6 m). Le résultat doit correspondre à une éventuelle réservation préalable ; il est figé dès qu'une affectation s'y rattache. Livraison interdite avant réception. |
| CT19 | Clôture avec reliquat : statut SOLDÉE ; motif obligatoire (reliquat annulé par le client, reliquat devenu inutile, commande abandonnée, AUTRE + commentaire) ; reliquat conservé ligne par ligne. |
| CT20 | Chaque ligne garde son poids, son unité et son origine : CALCULÉ ou DÉCLARÉ. DÉCLARÉ seulement en NOIR/LAC hors vente au poids. GALVA et GPP : poids toujours calculé. |
| CT21 | Réservation d'un lot brut pour transformation : statuts ACTIVE / CONVERTIE / LIBÉRÉE ; libérée par l'annulation de la commande, la clôture avec reliquat, une diminution avec choix explicite, ou le SUPERADMIN avec motif. |

### Décisions P du 02/10/2026 (matin)

| Repère | Règle |
|---|---|
| P-MULT | Besoin en barres de 6 m servi par des barres de 12 m : calcul **par excès**. 49 × 6 m → 25 × 12 m → 50 × 6 m ; 49 affectées ; 1 restante, stock GMC réel, traçable, jamais attribuée automatiquement. Précisé par L-n (§25). |
| P-BST | La **5.6 prépare** le bon de sortie transformation : lot, disponibilité, résultat attendu, comparaison avec la réservation, document. Aucun mouvement, aucun lot transformé. La **5.8 exécute** : sortie physique, mouvement, transformation, nouveau lot, réception. |
| P-ART | Création d'article par le SUPERADMIN seul ; les utilisateurs sélectionnent un article ou demandent une création. Modification à impact métier (masse, poids, % GALVA, unité de valorisation, caractéristiques de calcul, règles techniques) = nouvelle version historisée, ancien état conservé, aucun recalcul silencieux. Correction administrative (libellé, faute de frappe) : sans nouvelle version, mais auditée (ancienne et nouvelle valeur, utilisateur, date et heure, motif si nécessaire). Une commande confirmée garde les caractéristiques de sa confirmation. |
| P-RET | Deux transformations seulement : GALVANISATION → retour GALVA ; GPP → retour GPP. Le type choisi dans le BST fixe la finition de retour. Un même transformateur peut avoir les deux capacités. Pas de type AUTRE, découpe ou perçage. |
| P-KG-TR | Ligne vendue en KG avec transport en EUR/t : KG ÷ 1 000 × EUR/t (5 000 kg à 100 EUR/t → 500 EUR). Prix de vente, coût d'achat, coût de transformation et transport restent toujours séparés. |

## 24. Barres de 12 m et de 6 m — RÈGLE DÉFINITIVE (Phase 5.6, 02/10/2026)

Source : tes messages du 02/10/2026 (décisions LG1 à LG9, validations
V10-1 à V10-8). Analyse complète : `docs/ANALYSE_PHASE_5_6_v10.md`.

**État : règle validée, pas encore codée.** Le code de la Phase 5.5 ne
connaît qu'« 1 pièce de 12 m » : une barre de 12 m y est invisible pour
une commande de 6 m, et la base accepte encore un lot de 6 m sur une
ligne de 12 m. Ces écarts seront corrigés par le travail décrit plus bas.

### Texte de la règle (validé mot pour mot)

> Une barre de 12 m peut servir deux unités commerciales de 6 m à
> finition identique et compatible.
>
> La compatibilité 12 m → 6 m ne constitue pas une transformation
> industrielle et ne crée pas de nouveau lot ni de mouvement de
> transformation.
>
> Une sortie partielle d'une barre de 12 m sous forme de 6 m laisse un
> reliquat de 6 m rattaché au lot source.
>
> Le reliquat de 6 m est consommé avant l'ouverture d'une nouvelle barre
> de 12 m lorsque cela est possible.
>
> Deux barres de 6 m ne peuvent jamais être considérées automatiquement
> comme une barre de 12 m.
>
> Une pièce de 6 m issue d'une barre de 12 m ne peut plus être revendue
> comme une pièce de 12 m.
>
> La valeur de la partie sortie et celle du reliquat doivent conserver
> exactement la valeur initiale du lot, sous réserve de l'arrondi
> monétaire minimal autorisé.

### Décisions LG1 à LG9 et Q-COUPE

| Repère | Décision |
|---|---|
| LG1 | 1 barre de 12 m = 2 barres de 6 m pour la disponibilité commerciale. Règle de compatibilité du stock, pas une transformation : aucun mouvement de transformation dans le registre. |
| LG2 | À finition identique seulement : NOIR → NOIR, GALVA → GALVA, GPP → GPP. NOIR/LAC → GALVA reste une transformation de finition. |
| LG3 | **Pour le moment**, une seule conversion est validée : 12 m → 2 × 6 m. Aucun moteur générique (12 → 4, 12 → 3, 6 → 3… ne sont pas permis). Toute autre conversion devra faire l'objet d'une décision métier séparée. |
| LG4 | Vente partielle : stock 1 × 12 m, vente 1 × 6 m → 6 m sortis, 6 m restants. Le reliquat reste rattaché au lot source, devient disponible comme 6 m, n'est plus vendable comme 12 m. |
| LG5 | Valorisation proportionnelle à la longueur : lot 1 × 12 m à 100 TND, vente 1 × 6 m → 50 TND sortis, 50 TND restants. Pas de second CMP indépendant qui perdrait le lien avec le lot source. |
| LG6 | Sens inverse interdit : 2 × 6 m ne sont jamais considérées automatiquement comme 1 × 12 m disponible. Une commande de 12 m n'est servie que par une disponibilité réelle de 12 m. |
| LG7 | Le contrôle d'affectation vérifie au minimum : article, finition, longueur, compatibilité de longueur, disponibilité. Interdit : lot 6 m → ligne 12 m. Autorisé : lot 12 m → ligne 6 m. |
| LG8 | Remplace la dernière phrase de K2 (§22) : « Un lot 12 m peut servir une ligne 6 m à finition compatible identique selon l'équivalence 1 × 12 m = 2 × 6 m. Cette compatibilité n'est pas une transformation industrielle. » |
| LG9 | Quinze tests obligatoires (liste ci-dessous). |
| Q-COUPE | Oui : une ligne NOIR 6 m peut être servie par des barres NOIR de 12 m, sans opération de découpe en 5.6. |

### Validations V10-1 à V10-8

| Repère | Décision |
|---|---|
| V10-1 | Le reliquat de 6 m est consommé avant d'entamer une nouvelle barre. Ce n'est pas un FIFO général : la règle ne vise que les reliquats de barre nés de l'équivalence 12 m → 6 m. Elle est déterministe et auditable. |
| V10-2 | Pour les articles valorisés ou quantifiés au KG ou à la TONNE, une pièce de 6 m issue d'une barre de 12 m représente la moitié de la longueur et donc, dans le modèle actuel, la moitié du poids de la barre (120 kg → 60 kg). Aucun nouveau poids fournisseur n'est créé ; la traçabilité vers le lot source est conservée. |
| V10-3 | La valeur du reliquat se calcule par différence : valeur sortie + valeur restante = valeur initiale, à l'unité monétaire minimale près. La règle d'arrondi du §17 est respectée. |
| V10-4 | Le stock s'affiche « 2 barres de 12 m + 1 pièce de 6 m ». Il ne s'affiche jamais « 5 × 6 m » **comme stock physique**, car cela ferait perdre l'information physique réelle. La représentation conserve au minimum : la longueur physique et l'origine, la quantité, le reliquat, le lot source, la valeur associée. L'équivalence en 6 m sert à la disponibilité commerciale ; l'information physique du lot n'est jamais supprimée. |
| V10-5 | Un reliquat de 6 m NOIR peut partir en galvanisation ou en GPP : c'est une transformation, traitée en 5.8, à ne pas confondre avec la règle 12 m → 6 m. |
| V10-6 | La modification du schéma aura sa propre migration corrective, clairement identifiable. Toutes les données existantes sont préservées ; rien n'est supprimé ni reconstruit arbitrairement. |
| V10-7 | Ordre des travaux : documentation métier, tests, migration dédiée, code, tests complets, rapport, validation. |
| V10-8 | Si un reliquat compatible de 6 m existe dans un autre lot que celui choisi : **avertissement + confirmation + motif obligatoire + audit**. Le système ne refuse pas, ne choisit jamais le lot et n'impose aucun FIFO. Le choix du lot reste manuel (D5). |

### Modèle retenu (analyse v10 validée)

- **Le lot acheté reste un lot de 12 m.** Sa donnée source (longueur,
  nombre de barres, poids fournisseur, prix) n'est jamais modifiée. Le
  système ne transforme jamais « 1 × 12 m » en « 2 × 6 m » dans le lot.
- **Chaque sortie et chaque affectation porte la longueur des pièces
  concernées** (12 m ou 6 m). C'est la seule donnée nouvelle à stocker.
  Sa mise en œuvre est un **choix technique** décrit dans la v10 (§M,
  §N), à réaliser par la migration dédiée : colonne « longueur de la
  pièce » sur le mouvement, l'affectation et la ligne de bon de livraison
  client (sur le mouvement, une valeur vide signifie « longueur du
  lot ») ; vues de lecture ; triggers remplacés ou ajoutés. Aucune table
  reconstruite, aucune donnée supprimée.
- **Aucun mouvement de conversion, aucun lot enfant, aucun second CMP.**
  Le reliquat de 6 m est simplement ce qui reste du même lot.
- **La disponibilité en 6 m est un calcul**, jamais une donnée stockée :
  - disponible en 6 m = pièces libres des lots de 6 m + pièces de 6 m
    que les lots de 12 m peuvent encore fournir ;
  - disponible en 12 m = barres entières libres, comptées **lot par
    lot** : deux reliquats de deux lots ne font jamais une barre ;
  - les deux chiffres répondent à deux questions différentes et ne
    s'additionnent jamais.
- **Le coût suit la longueur** : 6 m pris sur une barre de 12 m coûtent
  la moitié de la barre ; le reliquat garde l'autre moitié, calculée par
  différence.

Exemple validé. Lot acheté : 3 barres de 12 m, 360 kg, 300 TND. Vente de
1 × 6 m.

| | Avant la vente | Après la vente |
|---|---|---|
| Donnée du lot | 12 m ; 3 barres ; 360 kg ; 300 TND | Identique |
| Stock physique | 3 barres de 12 m ; 360 kg ; 300 TND | 2 barres de 12 m + 1 pièce de 6 m ; 300 kg ; 250 TND |
| Disponible à la vente | En 12 m : 3. En 6 m : 6 | En 12 m : 2. En 6 m : 5 (1 reliquat + 4 par équivalence) |

Contrôle : 50 (sortie) + 50 (reliquat) + 200 (2 barres) = 300 TND ;
60 + 60 + 240 = 360 kg.

### Trois reliquats à ne jamais confondre

| | Reliquat de barre | Reliquat de conversion | Reliquat de commande |
|---|---|---|---|
| Origine | Vente directe de 6 m sur une barre de 12 m, à finition identique | Transformation : 25 × 12 m donnent 50 pièces pour 49 commandées (P-MULT) | Clôture d'une commande non entièrement livrée |
| Nature | Pièce physique de 6 m, dans le lot source | Pièce du lot transformé, après réception | Quantité commandée non livrée ; ce n'est pas du stock |
| Disponible à la vente | Immédiatement, comme 6 m | Après la réception du lot transformé (L-u, §25) | Sans objet |
| Règle | LG4, V10-1 à V10-4 | P-MULT (§23), L-u (§25) | X6, CT19 (§23) |

### Quinze tests obligatoires (LG9) — écrits avant le code lorsque cela est possible

1. 1 × 12 m, commande 1 × 12 m : accepté.
2. 1 × 12 m, commande 2 × 6 m : accepté.
3. 1 × 12 m, commande 1 × 6 m : accepté, reliquat 1 × 6 m.
4. Reliquat 1 × 6 m, commande 1 × 6 m : accepté.
5. 1 × 12 m, commande 3 × 6 m : refusé.
6. 2 × 6 m, commande 1 × 12 m : refusé.
7. 1 × 6 m, commande 1 × 12 m : refusé.
8. NOIR 12 m, ligne GALVA 6 m : refusé comme simple compatibilité.
9. GALVA 12 m, ligne GALVA 6 m : accepté.
10. GPP 12 m, ligne GPP 6 m : accepté.
11. Vérification du coût 12 m / 6 m.
12. Vérification du reliquat et de sa valeur.
13. Reconstruction du stock après consommation partielle.
14. Absence de double comptage.
15. Traçabilité lot source → sortie → reliquat.

## 25. Affaires — décisions du 02/10/2026 : Y6-L, Q-ANNUL, lectures L, propositions C

Source : tes réponses du 02/10/2026, cas par cas. Registre complet :
`docs/DECISIONS_PHASE_5_6_2026-10-02.md`. Contexte de chaque point (texte
d'origine, constat dans le dépôt, impact) :
`docs/REVUE_PHASE_5_6_L_C.md`.

**Portée.** Seul ce qui est écrit dans les tableaux ci-dessous a été
validé : c'est le texte qui t'a été présenté cas par cas. Certains détails
des propositions de la v9 ne t'ont pas été présentés un par un et restent
des **propositions d'analyse, non validées** : une commande qui reprend
une partie seulement des lignes du devis ; destination et incoterm repris
sur le devis ; une ligne de BST qui porte une quantité non réservée ; le
taux GPP du jour de l'avenant pour une ligne ajoutée par avenant. Ils
seront présentés avant le code.

### Taux de change et bon de sortie transformation (BST)

| Repère | Décision |
|---|---|
| Y6-L | La règle écrite est la référence : tous les avenants d'une commande confirmée utilisent le taux de change du devis validé et gelé. |
| Q-ANNUL | Un BST préparé et non exécuté peut être annulé par le SUPERADMIN seul : motif et audit obligatoires, historique conservé, allocations et réservations libérées explicitement, statut annulé conservé. Un BST exécuté ne s'annule pas ainsi. |

### Lectures L-a à L-v

| Repère | Décision | Règle retenue |
|---|---|---|
| L-a | Oui | « Réservation commerciale » = réservation de devis, qui ne bloque pas le stock. « Affectation » inclut réaffectations et libérations. |
| L-b | Oui, précisé | « Lot brut » = lot NOIR, c'est-à-dire l'état d'achat chez le fournisseur (NOIR ou LAC), avant toute transformation. |
| L-c | Oui | Normal ou supplément : décidé dès la réservation du lot brut, puis gardé. |
| L-d | Oui | Une affectation à cheval sur la quantité en vigueur est refusée ; elle se saisit en deux fois (normal, puis supplément avec motif). |
| L-e | Oui | Ligne ajoutée par avenant : valeurs d'article du jour de l'avenant ; les lignes existantes gardent les leurs. |
| L-f | Oui | Le seul SUPERADMIN ne peut être ni désactivé ni changé de rôle ; son compte est créé à l'installation. |
| L-f bis | Reporté | Le cas du SUPERADMIN indisponible sera décidé plus tard (§27). |
| L-g | Oui | Tout nouveau compte démarre sans aucun droit. |
| L-h | Modifié | Le % GALVA de la fiche article est **proposé** sur la ligne ; l'utilisateur le garde ou le change ; un écart est signalé, jamais bloqué. Le % utilisé est enregistré sur la ligne, avec son auteur, et figé à la confirmation du devis. |
| L-h bis | Décidé | Sur une ligne GALVA, le % est obligatoire et strictement supérieur à 0 : 0 % est interdit. |
| L-i | Oui | Une réservation ne se déplace pas : libération avec motif, puis nouvelle réservation. |
| L-j | Oui | Pas d'avenant sur un devis ; seulement sur une commande confirmée. |
| L-k | Oui | Une barre inscrite dans un BST préparé est **engagée** : elle est déduite du disponible, même encore sur le parc. |
| L-l | Oui, pour le moment | Seul le SUPERADMIN prépare un BST ; délégation possible plus tard. |
| L-m | Abandonnée | Un BST n'est jamais refusé pour une question de capacité du transformateur. |
| L-n | Modifié | Achat en excès libre. La réservation de barres avant transformation reste au plus juste (49 × 6 m → 25 barres). |
| L-o | Décidé | Tout utilisateur peut demander la création d'un article ; seul le SUPERADMIN le crée, si nécessaire. |
| L-p | Oui, précisé | Seul le SUPERADMIN modifie une désignation, qu'il a confirmée et validée ; motif facultatif. Les autres champs de l'article suivent P-ART (§23). |
| L-q | Oui | Le devis affiche une marge prévisionnelle ; la marge réelle vient en 5.10. |
| L-r | Oui | En préparant un BST, on désigne soi-même la réservation exécutée. |
| L-s | Modifié | Exécution partielle d'une réservation permise ; le reste demeure réservé. |
| L-t | Modifié | Aucune modification exceptionnelle du taux n'est développée en 5.6. Le taux du devis validé reste la seule référence. Rappel de tes décisions du 02/10 si la fonction devait exister un jour : elle serait autorisée, historisée, auditée, non rétroactive, et ne changerait ni le taux du devis, ni les anciennes lignes, ni les avenants enregistrés. |
| L-u | Oui, précisé | La pièce en trop d'une transformation est affectable à une commande confirmée dès que le BST est préparé ; vendable seulement après la réception ; réservable à titre informatif au stade du devis. |
| L-v | Oui | Un devis en cours n'est jamais recalculé tout seul quand un article change : le système signale, l'utilisateur décide. |

**Ce qui bloque le disponible d'un lot chez GMC** (L-a, L-k, Y1 bis) :

`disponible = physique − affecté non livré − réservé pour transformation − engagé dans un BST préparé`

Quatre notions à ne jamais confondre : la **réservation de devis**
(informative, jamais déduite), la **réservation de lot brut** pour
transformation (déduite), l'**affectation** (déduite), l'**engagement
dans un BST préparé** (déduit). Aucune ne crée de mouvement physique.

### Propositions C1 à C14

| Repère | Décision | Règle retenue |
|---|---|---|
| C1 | Oui | Commande créée seulement depuis un devis CONFIRMÉ ; quantités modifiables en brouillon, figées à la confirmation. |
| C1 bis | A | Quantité modifiée en brouillon : recalcul avec les valeurs figées du devis. |
| C1 ter | Décidé | Commande annulée : toutes les demandes en amont sont annulées, et on revient à la première phase : un **nouveau devis** est nécessaire. La marchandise déjà réceptionnée reste en stock. La marchandise déjà transformée chez le transformateur reste en stock. Les bons de commande restent **si la marchandise est réceptionnée** ; ceux dont rien n'est réceptionné sont annulés avec les autres demandes en amont. |
| C2 | Oui | Unités de vente : TONNE, KG, PIÈCE, ML, M² ; liste extensible par le SUPERADMIN ; prix dans l'unité de vente. |
| C3 | Modifié | Après la confirmation de la commande, le transport estimé n'est plus recalculé, même en cas d'avenant ; les chiffres définitifs viennent aux étapes suivantes. Pas de transport estimé sur un supplément. |
| C4 | Oui | Commande annulée avec la même liste de causes que le devis ; « Autre » exige un commentaire ; un brouillon est annulé par son auteur ; un devis confirmé ne s'annule pas. |
| C4 bis | Reporté | La liste des 8 causes d'annulation sera fixée plus tard (§27). |
| C5 | Modifié | Un devis dont la validité est dépassée n'est pas annulé ; ses réservations sont libérées. Il peut être **actualisé** plus tard : il redevient modifiable (prix, taux, quantités), l'ancien état restant dans l'historique. |
| C5 bis | Décidé | Heure de référence : heure de Tunisie. |
| C6 | Oui | Réservation de devis limitée au disponible ; annulée, jamais supprimée. |
| C7 | Oui | Supplément possible tant que la commande est confirmée. |
| C8 | Oui | Réaffectation par le SUPERADMIN, sur du non livré, même lot, même emplacement. |
| C8 bis | A | Le type d'un supplément réaffecté se décide à la destination. |
| C9 | Oui | Affectation faite par erreur : libérée par le SUPERADMIN avec motif. |
| C10 | Oui | « Entièrement livrée » = livré ≥ quantité en vigueur et plus rien en attente ; clôture manuelle. (« Plus rien en attente » = aucune affectation active non livrée, v9 §17.) |
| C10 bis | A | Pour une ligne vendue au poids, la comparaison se fait en pièces. |
| C11 | Oui | Reste à livrer = quantité en vigueur − livré. À approvisionner = quantité en vigueur − (affecté + réservé pour transformation + livré). **Précision de calcul (choix technique de la v9 §6.8, signalé, pas une règle nouvelle)** : « livré » = livré en quantité normale ; « affecté » = affecté en quantité normale, actif et pas encore livré. But : ne pas compter deux fois une quantité affectée puis livrée, et ne pas mêler les suppléments au calcul. |
| C12 | Oui | Fiche client inchangée en 5.6 ; adresse et identifiant fiscal notés pour la 5.9. |
| C13 | Déjà validé | LAC = NOIR. |
| C14 | Modifié | La date de confirmation est enregistrée automatiquement quand la commande passe à l'état CONFIRMÉE, par le SUPERADMIN ou le commercial. |

## 26. Règles remplacées ou modifiées — registre

Ce registre rassemble les remplacements. Quand l'ancienne règle est
écrite dans ce document (§19 à §23), elle y reste, avec une note à sa
place. Le registre complet des remplacements antérieurs au 02/10 (H1 à
H40) est dans `docs/ANALYSE_PHASE_5_6_v9.md` §26.

### Remplacements décidés le 02/10/2026

| Règle antérieure | Remplacée par | Conséquence |
|---|---|---|
| K2 (§22) : « un lot brut de 12 m n'est jamais considéré comme directement disponible en 6 m » | LG8 (§24) | Vrai seulement quand la finition change. |
| v9, Q-COUPE : proposition « non » | Q-COUPE (§24) | Affectation directe d'un lot NOIR 12 m à une ligne NOIR 6 m acceptée. |
| CT3, pour le % GALVA : valeur validée par le SUPERADMIN seul | L-h, L-h bis (§25) | Le % est saisi sur la ligne ; l'historique de validation du % devient inutile. La validation de la **masse** reste. |
| Y1 bis (b) : « le système reprend exactement ce qui a été réservé » | L-s (§25) | Un BST peut envoyer moins que la quantité réservée ; finition et longueur attendues inchangées. |
| CT5 : modification exceptionnelle du taux par le SUPERADMIN | L-t (§25) | Fonction non développée en 5.6. |
| v9, lecture L-m : BST refusé sans capacité | L-m abandonnée (§25) | Aucun contrôle de capacité à la préparation d'un BST. |
| v9, lecture L-n : une seule barre en trop | L-n (§25) | Limite valable pour la réservation seulement ; achat libre. |
| v9, C3 : transport recalculé sur la quantité en vigueur | C3 (§25) | Aucun recalcul après confirmation. |
| v9, C5 : prolongation avant expiration seulement ; devis expiré figé | C5 (§25) | Actualisation possible après l'échéance. |
| v9, C14 : date de confirmation par le client | C14 (§25) | Date automatique au passage à CONFIRMÉE. |

### Rappel de remplacements antérieurs, visibles dans les §20 à §22

| Règle antérieure | Remplacée par | Conséquence |
|---|---|---|
| N6 (§21) : supplément au-delà de la quantité **originale** | O1 (§23) | Supplément au-delà de la quantité **en vigueur**. |
| K10 (§22), partie « nouvelle négociation → nouveau prix » | Y5 (§23) | Plus de renégociation après confirmation. |
| N4, K19 : GPP « × 1,02 » comme constante | CT4 (§23) | Réglage global historisé ; même valeur. |

## 27. Phase 5.6 — points encore ouverts au 02/10/2026

La Phase 5.6 n'est **pas validée dans son ensemble**. Rien n'est codé :
aucune migration, aucun service, aucun test pour la 5.6.

| N° | Point | État |
|---|---|---|
| 1 | C4 bis : liste des 8 causes d'annulation | À fournir par Mohamed. Elle n'existe dans aucun document du dépôt ; elle ne doit pas être inventée. |
| 2 | L-f bis : SUPERADMIN indisponible | À décider plus tard. |
| 3 | Q-BCT (lien entre BST et bon de commande de transformation) et Q-TRF (capacités d'un transformateur) | En analyse. Contraintes fixées : aucun mouvement physique sans commande de transformation ; le SUPERADMIN seul crée les transformateurs ; un transformateur peut avoir plusieurs capacités ; aucune migration maintenant. À traiter avec Q-TRF : le sort du type « débit », que le §8 et la base connaissent alors que P-RET ne retient que deux transformations. |
| 4 | BST préparé et non exécuté d'une commande annulée : annulé d'office ou conservé ? | À relier à Q-ANNUL. |
| 5 | Bon de commande partiellement réceptionné quand la commande client est annulée : sort de la partie non reçue | À préciser en 5.7 (achats). |
| 6 | Format du code article | Ouvert depuis la 5.5 ; n'empêche pas de coder. |
| 7 | Transport estimé d'une ligne **ajoutée par avenant** (nouvel article) : saisi et calculé pour cette nouvelle ligne (K21, §22), ou aucun transport estimé après la confirmation (C3, §25) ? | Relevé à la relecture du 02/10/2026 ; à trancher par Mohamed. |
| 8 | Validation d'ensemble de la Phase 5.6 | En attente. |

## Identifiants et numérotation

- UUID en interne pour toutes les clés primaires.
- Numéro humain séquentiel par type de document, par année : `DEV-2026-0001`,
  `CMD-2026-0001`, `BCF-2026-0001`, `BLF-2026-0001`, `FFO-2026-0001`,
  `BCT-2026-0001`, `BST-2026-0001`, `RTR-2026-0001`, `BLC-2026-0001`,
  `FAC-2026-0001`.
- Les numéros d'origine des documents fournisseurs (n° de BL réel du
  fournisseur, n° de facture réel) sont toujours conservés séparément, en
  texte libre, jamais remplacés par le numéro interne GMC.
