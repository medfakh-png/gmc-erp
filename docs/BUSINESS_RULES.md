# Règles métier GMC — référence unique et à jour

Ce document est la référence unique des règles métier validées. En cas de
divergence apparente avec un autre document ou une ancienne conversation,
**ce fichier fait foi** (il est mis à jour à chaque validation).

Dernière mise à jour : Phase 5.6 (analyse) — réponses K1 à K22 (§22),
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

## 20. Affaires — décisions D1 à D6 VALIDÉES (Phase 5.6, 30/09/2026)

Source : message « Phase 5.6 — validation finale des décisions D1 à D6 ».
Détail et mise en œuvre proposée : `docs/ANALYSE_PHASE_5_6.md`.
Décisions complémentaires N1 à N15 : §21. Réponses définitives K1 à K22 :
§22. Points encore ouverts : O1 à O9 de `docs/ANALYSE_PHASE_5_6.md` §5.2.

**D1 — Compatibilité lot ↔ ligne de commande.** Un lot peut servir une
ligne si les trois conditions sont réunies :

1. même article ;
2. même finition, sauf NOIR/LAC → GALVA et NOIR/LAC → GPP ;
3. même longueur, sauf les **multiples exacts** (12 m peut servir
   2 × 6 m).

Toute autre compatibilité est refusée pour le moment ; aucune autre règle
ne doit être inventée. LAC = NOIR dans le logiciel.

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
  manuellement.
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
  point **O4**, non tranché.

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
- **N4 — GPP.** Majoration **fixe de 2 %**, intégrée au calcul
  conformément à la règle métier déjà discutée ; ne pas la remplacer par
  0 %.

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
    directement en EUR ; aucune conversion cachée en tonnes.

### Commande confirmée (avenants)

- **N6.** La quantité originale est conservée. Les avenants peuvent
  produire une quantité en vigueur. Ce qui dépasse la quantité **originale** reste un
  **supplément** et suit la règle CMP.
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
  son compte et son rôle système, jamais par le nom affiché.

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
    quantité normale) : **non tranchée**, point O1 de
    `docs/ANALYSE_PHASE_5_6.md`.
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
    l'ancienne condition est conservée.
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
    stratégique déjà validées.
  - Pas de système où le commercial doit sélectionner un taux prédéfini
    existant.
  - Ce que recouvre « utilisateur commercial autorisé » (rôle ou
    permission) et le moment exact de la « validation de l'offre » :
    points O5 et O3 de `docs/ANALYSE_PHASE_5_6.md`.
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
  validées.
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
- **K19 — GPP.**
  - GPP est une finition distincte de GALVA : poids GPP = poids brut ×
    1,02 (fixe actuellement).
  - Jamais cumulé avec le % GALVA : NOIR/LAC → GPP = +2 % ; NOIR/LAC →
    GALVA = % GALVA.
- **K20 — % GALVA.**
  - 0 % = état brut de la matière.
  - Trois cas distincts : % défini, 0 % défini, % non renseigné. Un % non
    renseigné n'est **jamais** transformé automatiquement en 0 %.
  - Vente GALVA sans % renseigné et validé → le système demande de
    compléter le référentiel.

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
  - Actuellement un seul SUPERADMIN : Mohamed.
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
  réponse.

## Identifiants et numérotation

- UUID en interne pour toutes les clés primaires.
- Numéro humain séquentiel par type de document, par année : `DEV-2026-0001`,
  `CMD-2026-0001`, `BCF-2026-0001`, `BLF-2026-0001`, `FFO-2026-0001`,
  `BCT-2026-0001`, `BST-2026-0001`, `RTR-2026-0001`, `BLC-2026-0001`,
  `FAC-2026-0001`.
- Les numéros d'origine des documents fournisseurs (n° de BL réel du
  fournisseur, n° de facture réel) sont toujours conservés séparément, en
  texte libre, jamais remplacés par le numéro interne GMC.
