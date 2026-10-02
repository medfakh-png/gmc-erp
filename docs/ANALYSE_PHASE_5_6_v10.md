# Phase 5.6 — Analyse v10 : barres 12 m / 6 m (complément ciblé de la v9)

**Statut : V10 VALIDÉE (02/10), points V10-1 à V10-8.** Les lectures L
et les propositions C sont tranchées : voir le registre des décisions. Aucun
code, aucune migration, aucun test d'implémentation, aucune modification
de la base. 293 tests réussis, inchangés.

**Déposé dans le dépôt le 02/10/2026**, à la demande de Mohamed (« mettre
à jour et enregistrer notre travail »), avec la mise à jour de
`docs/BUSINESS_RULES.md` (§24). Le texte ci-dessous est celui de la
version 10.4 ; seules les mentions d'état de cet en-tête et des sections
0 et 0 bis ont été actualisées.

- **Version 10.4 du 02/10/2026** : la lecture L-k est validée (section
  J.2). Les décisions du jour sont rassemblées dans
  `DECISIONS_PHASE_5_6_2026-10-02.md`.
- Version 10.3 du 02/10/2026 : précise les engagements qui bloquent
  le disponible (section J.2) et distingue le reliquat de barre du
  reliquat de conversion (section E). Aucune règle nouvelle.
- Version 10.2 du 02/10/2026 : intègre tes huit validations V10-1 à
  V10-8 (section S), la règle métier définitive à inscrire (section 0 bis)
  et la **structure cible précise** que tu as demandée : donnée physique
  du lot et disponibilité commerciale (section T). V10-8 est intégrée
  avec ta variante : avertissement, confirmation, motif obligatoire,
  audit (section T.5).
- Elle ne remplace pas la v9 : elle traite un seul sujet, la règle
  « 1 barre de 12 m = 2 barres de 6 m », et liste ce qu'elle remplace dans
  la v9 (section P).
- Les lectures L-a à L-v et les propositions C sont présentées à part,
  dans `REVUE_PHASE_5_6_L_C.md`. Aucune n'est validée.

Repères utilisés : **[FACT]** vérifié dans le dépôt ; **[V]** décision
validée par toi ; **[PROP]** proposition à valider ; **[CT]** choix
technique, signalé, jamais présenté comme une règle métier.

---

## Résumé

1. **[FACT]** Aujourd'hui une barre de 12 m est enregistrée comme
   « 1 pièce de 12 m » et rien d'autre. Elle est invisible pour une
   commande de 6 m ; en prendre 6 m est impossible sans prendre la barre
   entière ; la base accepte d'affecter une pièce de 6 m à une ligne de
   12 m.
2. **[PROP]** Le lot garde sa longueur réelle d'achat (12 m). Seul le
   **comptage** change : le stock d'un lot de 12 m se compte en **unités
   de 6 m** (une barre entière = 2 unités). Chaque sortie et chaque
   affectation indique la **longueur des pièces** concernées (12 m ou
   6 m).
3. **[PROP]** Aucun mouvement de conversion ni de transformation, aucun
   lot supplémentaire, aucun second CMP : le reliquat de 6 m est
   simplement l'unité restante **du même lot**.
4. **[PROP]** Le coût suit la longueur : 6 m pris sur une barre de 12 m
   coûtent la moitié de la barre ; le reliquat garde l'autre moitié,
   calculée par différence pour qu'aucun millime ne soit compté deux fois.
5. **[V]** Migration dédiée, clairement identifiable, à créer plus tard ;
   les 293 tests existants doivent passer sans changement d'assertion
   (tous leurs lots sont en 6 m).
6. **[V]** Les sept points V10-1 à V10-7 sont validés (section S).
7. **[V]** Le lot acheté reste un lot de 12 m dans sa donnée source ; la
   disponibilité en 6 m est un calcul dérivé (section T).
8. **[V]** Entre plusieurs lots, le système avertit, demande une
   confirmation et un motif, et trace le choix dans l'audit. Il ne refuse
   pas et ne choisit jamais le lot (V10-8, section T.5).

---

## 0. Décisions validées le 02/10 dans cette conversation [V]

Reportées dans `docs/BUSINESS_RULES.md` (§24 et §25) le 02/10/2026.

| Repère | Décision |
|---|---|
| **LG1** | 1 barre de 12 m = 2 barres de 6 m pour la disponibilité commerciale. Règle de normalisation / compatibilité du stock. Ce n'est pas une transformation industrielle : aucun mouvement de transformation dans le registre. |
| **LG2** | Portée : finition identique. NOIR 12 m → NOIR 6 m : oui. GALVA 12 m → GALVA 6 m : oui. GPP 12 m → GPP 6 m : oui. NOIR/LAC → GALVA : non, c'est une transformation de finition. |
| **LG3** | Une seule conversion validée : 12 m → 2 × 6 m. Aucun moteur générique (12 → 4, 12 → 3, 6 → 3… interdits). Toute autre conversion = décision métier séparée. |
| **LG4** | Vente partielle : stock 1 × 12 m, vente 1 × 6 m → 6 m sorti, 6 m restant. Le reliquat reste traçable vers le lot source 12 m, devient disponible comme 6 m, ne peut plus être vendu comme 12 m. La conversion est consommée progressivement. |
| **LG5** | Valorisation proportionnelle à la longueur : lot 1 × 12 m à 100 TND, vente 1 × 6 m → coût sorti 50 TND, valeur restante 50 TND. Ne pas créer deux CMP indépendants 12 m / 6 m qui perdraient le lien avec le lot source. |
| **LG6** | Sens inverse interdit : 2 × 6 m ne valent jamais 1 × 12 m. Une commande 12 m n'est servie que par une disponibilité réelle de 12 m. |
| **LG7** | Le contrôle d'affectation vérifie au minimum : article, finition, longueur, compatibilité de longueur, disponibilité. Interdit : lot 6 m → ligne 12 m. Autorisé : lot 12 m → ligne 6 m (LG1). |
| **LG8** | K2 est corrigé. Nouvelle règle : « Un lot 12 m peut servir une ligne 6 m à finition compatible identique selon l'équivalence 1 × 12 m = 2 × 6 m. Cette compatibilité n'est pas une transformation industrielle. » |
| **LG9** | Quinze tests obligatoires (section O). |
| **Y6-L** | La règle écrite est la référence : tous les avenants d'une commande confirmée utilisent le taux du devis validé et gelé. Une modification exceptionnelle doit être autorisée, historisée, auditée, non rétroactive, sans modifier les anciennes lignes ni les avenants enregistrés. |
| **Taux exceptionnel** | Ce n'est pas une règle de calcul de la 5.6 : un événement administratif tracé (ancienne valeur, nouvelle valeur, utilisateur, date/heure, motif, audit). Il ne réécrit ni le taux du devis ni les calculs historiques. Pas de logique complexe sans besoin concret. |
| **Q-COUPE** | La proposition « non » de la v9 est corrigée : oui, par LG1 à LG8, sans opération de découpe en 5.6. |
| **Q-ANNUL** | Un BST préparé et non exécuté peut être annulé par le SUPERADMIN seul : motif et audit obligatoires, historique conservé, allocations et réservations libérées explicitement, statut annulé conservé. Un BST exécuté ne s'annule pas par suppression ni changement de statut. |
| **Q-BCT** — reste en analyse | Le mouvement physique reste impossible sans commande de transformation. En 5.6 : préparation du BST, sans mouvement. Avant l'exécution (5.8) : le bon de commande de transformation doit exister et le BST doit lui être cohérent. **[FACT]** aujourd'hui `bon_sortie_transformation.bon_commande_transformation_id` est obligatoire dès la création du BST. |
| **Q-TRF** — reste en analyse | Le SUPERADMIN seul crée les transformateurs et leurs capacités (GALVANISATION → GALVA, GPP → GPP ; les deux possibles). Aucune migration maintenant. **[FACT]** aujourd'hui `transformateur.type` n'accepte qu'une valeur. |
| **L et C** | L-a à L-v et propositions C : tranchées le 02/10, après cette section ; voir `DECISIONS_PHASE_5_6_2026-10-02.md` et `BUSINESS_RULES.md` §25. |

## 0 bis. Règle métier définitive à inscrire [V, 02/10]

Texte validé, reporté tel quel dans `docs/BUSINESS_RULES.md` §24 le
02/10/2026 :

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

---

## A. Modèle actuel [FACT]

| Sujet | État réel | Où |
|---|---|---|
| Article | Pas de longueur : désignation, masse au mètre, % galva | table `article` |
| Longueur | Portée par le lot et par les lignes (devis, commande, BL fournisseur, réservation) | colonnes `longueur_m` |
| Lot | Une seule longueur ; quantité initiale en **pièces entières** | table `lot` |
| Achat 12 m | Enregistré tel quel : N pièces de 12 m | `bl_fournisseur_ligne`, `lot` |
| Registre | Un mouvement = un lot, un nombre entier de pièces, un poids | table `mouvement_stock` |
| Solde | Somme des pièces et des poids, par lot et par emplacement | `v_solde_lot_emplacement` ; `repositories/stock_repository.py` l. 254-257 |
| Disponibilité | Par (article, finition, **longueur strictement égale**) | `services/stock_service.py` l. 965-1011 ; `repositories/stock_repository.py` l. 116, 303, 420 |
| Affectation | Lot + ligne + pièces du lot ; **aucun** contrôle article / finition / longueur | table `affectation_stock` |
| Plafond d'affectation | Base : total actif ≤ quantité initiale du lot. Service : ≤ stock physique − déjà affecté | `trg_affectation_plafond` ; `quantite_affectable_lot` l. 939-949 |
| Valorisation | Coût réel du lot pour une affectation normale ; CMP du pool pour un supplément ou une chute | `db/valorisation.py` |
| Pool CMP | Un pool par (article, finition, longueur du lot) | table `cmp_stock_general` |
| Quantité valorisée | UNITE : pièces ; ML : pièces × longueur **du lot** ; KG : poids ; TONNE : poids ÷ 1 000 | `db/valorisation.py` l. 147-163 |
| Unité de vente | Non stockée : quantité en pièces, prix sans unité | `commande_ligne`, `devis_ligne` |
| Finitions | NOIR, GALVA, GPP. LAC n'existe pas (LAC = NOIR) | CHECK des tables |
| Données | Aucune donnée métier : la base ne contient que la liste des 20 migrations | `db/gmc.db` |

---

## B. Problème [FACT]

Cinq cas exécutés le 02/10 sur une base jetable, hors du dépôt.

| Cas | Attendu | Résultat réel |
|---|---|---|
| Stock 1 × 12 m, commande 1 × 12 m | Possible | Accepté ; coût 60 DT ; reste 0 |
| Stock 1 × 12 m, commande 2 × 6 m | Possible | Disponible 6 m = 0 ; affecter 2 pièces refusé |
| Stock 1 × 12 m, commande 1 × 6 m | Possible, reste 1 × 6 m | Disponible 6 m = 0 ; la barre entière part : reste 0, coût 60 DT au lieu de 30 |
| Stock 2 × 6 m, commande 1 × 12 m | Refus | La base accepte d'affecter une pièce de 6 m à la ligne 12 m |
| Stock 1 × 12 m, commande 3 × 6 m | Refus | Refusé, parce que 3 > 1 pièce et non parce que 3 > 2 |

Trois causes :

1. **Le stock se compte en pièces entières d'une seule longueur.** Une
   demi-barre n'existe pas dans le registre.
2. **La disponibilité exige une longueur strictement égale.** Un lot de
   12 m n'est jamais proposé pour du 6 m.
3. **Aucun contrôle ne relie le lot à la ligne.** Ni la base ni le code ne
   comparent article, finition et longueur.

La règle n'existe dans aucun des 293 tests : aucun ne crée un lot de 12 m.

---

## C. Modèle cible [PROP]

Six principes.

- **C1 — Le lot ne change pas.** Un achat de N barres de 12 m reste un lot
  de longueur 12 m et de N pièces. Rien n'est « converti » à l'entrée :
  les documents d'achat et l'inventaire physique restent vrais.
- **C2 — Seul le comptage change.** Le stock d'un lot de 12 m se compte en
  **unités de 6 m** : une barre entière = 2 unités, une pièce de 6 m =
  1 unité. Pour tout autre lot, l'unité reste la pièce, comme aujourd'hui.
- **C3 — La pièce porte sa longueur.** Chaque mouvement et chaque
  affectation d'un lot de 12 m indique si les pièces concernées sont des
  barres de 12 m ou des pièces de 6 m. La quantité reste un nombre entier
  de pièces.
- **C4 — Rien d'artificiel dans le registre.** Pas de mouvement de
  conversion, pas de mouvement de transformation, pas de lot « enfant ».
  La sortie d'une pièce de 6 m est une sortie ordinaire du lot de 12 m
  (LG1).
- **C5 — Une seule conversion.** 12 m → 6 m, facteur 2, écrite en dur.
  Aucune table de conversions, aucun calcul de multiples (LG3).
- **C6 — Sens unique.** Un lot de 6 m ne sert jamais une ligne de 12 m ;
  les reliquats de deux lots différents ne forment jamais une barre de
  12 m (LG6).

---

## D. Représentation du 12 m [PROP]

- Le lot : longueur 12 m, quantité initiale N barres. **Inchangé.**
- L'entrée d'origine : N pièces de 12 m, soit 2 × N unités.
- Le solde du lot à un emplacement : U unités, calculé depuis le registre.
- Lecture du solde : **barres entières = U ÷ 2 (division entière)** ;
  **reliquat = 1 pièce de 6 m si U est impair, sinon 0**.

Exemple : lot de 3 barres. Après la vente de 1 × 6 m, U = 5 : 2 barres
entières et 1 pièce de 6 m.

Cette lecture repose sur la règle **[V V10-1]** : une pièce de 6 m déjà
issue d'une barre de 12 m est consommée avant d'entamer une nouvelle
barre. Ton exemple : stock 2 × 12 m + 1 × 6 m, demande 1 × 6 m → la pièce
de 6 m sort, les 2 barres restent intactes.

- À l'intérieur d'un lot, le compte en unités applique cette règle par
  construction : 5 unités − 1 = 4 unités, soit 2 barres entières.
- Ce n'est **pas un FIFO** : la règle ne choisit aucun lot et ne classe
  aucune date. Elle ne concerne que les reliquats de la conversion
  12 m → 6 m.
- Elle est déterministe (même registre, même résultat) et auditable
  (chaque sortie porte son lot et la longueur des pièces).
- Entre **plusieurs lots**, le choix du lot reste manuel (D5). La règle
  validée dans ce cas est V10-8 : avertissement, confirmation, motif,
  audit (section T.5).

---

## E. Représentation du reliquat 6 m [PROP]

Le reliquat n'est pas un nouvel objet. C'est **l'unité impaire du lot de
12 m**.

| Exigence (LG4) | Comment le modèle y répond |
|---|---|
| Traçable vers le lot source 12 m | C'est le même lot : même identifiant |
| Disponible comme 6 m | L'unité restante entre dans la disponibilité 6 m (section K) |
| Plus vendable comme 12 m | Une vente 12 m exige 2 unités d'une barre entière du même lot |
| Conversion consommée progressivement | Chaque pièce de 6 m sortie retire 1 unité |

Nom proposé : **reliquat de barre**. À ne pas confondre avec le « reliquat
de conversion » de P-MULT (pièce en trop après une transformation) ni
avec le « reliquat de commande » (v9 §6.17).

Différence essentielle : le reliquat de **barre** est disponible
immédiatement comme 6 m (LG4). Le reliquat de **conversion** n'est
disponible qu'après la réception du lot transformé (5.8).

**[V V10-4]** Affichage : « 2 barres de 12 m + 1 pièce de 6 m », avec le
lot source et la valeur. Jamais « 5 × 6 m » comme stock physique
(section T).

---

## F. Traçabilité du lot source [PROP]

Une seule référence, du début à la fin : l'identifiant du lot de 12 m.

| Étape | Enregistrement | Lot référencé |
|---|---|---|
| Achat | BL fournisseur, entrée d'origine | Lot 12 m |
| Affectation d'une ligne 6 m | Affectation, pièces de 6 m | Lot 12 m |
| Livraison | Ligne de BL client, mouvement de sortie, pièces de 6 m | Lot 12 m |
| Reliquat | Solde du lot (1 unité) | Lot 12 m |
| Vente du reliquat | Nouvelle affectation, nouvelle sortie | Lot 12 m |

Fournisseur, BL d'origine, prix d'achat et facture restent donc
accessibles pour chaque pièce de 6 m vendue.

---

## G. Valorisation [PROP]

### G.1 Quantité d'un mouvement dans l'unité du prix

| Unité | Aujourd'hui [FACT] | Proposé |
|---|---|---|
| UNITE (par pièce) | pièces | pièces × (longueur de la pièce ÷ longueur du lot) : une pièce de 6 m d'un lot 12 m = 0,5 barre |
| ML (par mètre) | pièces × longueur du lot | pièces × longueur **de la pièce** |
| KG | poids du mouvement | inchangé |
| TONNE | poids ÷ 1 000 | inchangé |

Pour un lot autre que 12 m, la longueur de la pièce est celle du lot :
les quatre calculs donnent exactement le résultat d'aujourd'hui.

### G.2 Une barre de 12 m vendue de trois façons

| Prix du lot | Coût de la barre | Vendue 1 × 12 m | Vendue 2 × 6 m | Vendue 1 × 6 m | Valeur du reliquat |
|---|---|---|---|---|---|
| 100 DT par pièce | 100 | 100 | 50 + 50 | 50 | 50 |
| 8 DT par mètre | 96 | 96 | 48 + 48 | 48 | 48 |
| 2,5 DT par kg, barre de 42 kg | 105 | 105 | 52,5 + 52,5 | 52,5 | 52,5 |

La première ligne est ton exemple (LG5).

### G.3 Articles valorisés au kg ou à la tonne

Le coût suit le poids sorti. Pour qu'il reste proportionnel à la longueur
(LG5), **[V V10-2]** le poids de stock d'une pièce de 6 m prise sur une
barre de 12 m est **calculé** à partir du lot source :

`poids d'une pièce de 6 m = poids initial du lot ÷ nombre de barres achetées ÷ 2`

Ton exemple : 1 × 12 m = 120 kg → 1 × 6 m = 60 kg.

- Ce poids n'est pas saisi librement et **aucun nouveau poids fournisseur
  n'est créé** : le poids fournisseur reste celui du lot, inchangé.
- La dernière pièce emporte le poids restant du lot, pour que la somme
  des poids sortis soit exactement le poids du lot.
- Le poids commercial ou facturé d'une vente reste une notion distincte,
  inchangée.

### G.4 Arrondi

**[FACT]** Avec la règle d'arrondi du projet, une barre à 100,001 DT
coupée en deux donne 50,001 + 50,001 = 100,002 DT si chaque moitié est
arrondie séparément : un millime compté deux fois.

**[V V10-3]** La valeur du reliquat se calcule **par différence** : coût
total du lot − coûts déjà sortis. Résultat : 50,001 + 50,000 = 100,001.
La dernière sortie d'un lot emporte exactement sa valeur restante, comme
le fait déjà le moteur quand un pool est vidé.

Garantie attendue : **valeur sortie + valeur restante = valeur
initiale**, au millime près, sans montant créé ni perdu. Chaque montant
sorti reste arrondi selon la règle existante (`BUSINESS_RULES.md` §17) :
au millime le plus proche, 0,5 vers le haut, une seule fois.

### G.5 Ce qui ne change pas

Règles de la Phase 4 conservées : quantité normale affectée → coût réel
du lot ; supplément et chute → CMP au moment de la sortie ; prix conservé
dans son unité de saisie ; un seul arrondi sur le montant final.

---

## H. CMP [PROP]

- **Le pool ne change pas de définition** : (article, finition, longueur
  **du lot**). Un lot de 12 m reste dans le pool 12 m jusqu'à sa dernière
  unité.
- **Aucun pool 6 m n'est créé par la conversion.** Le reliquat reste
  valorisé dans son lot et dans le pool 12 m. C'est ce qui évite les deux
  CMP indépendants (LG5).
- Le pool 6 m continue d'exister pour les lots réellement achetés en 6 m.
- **Supplément de 6 m pris sur un lot 12 m** : CMP du pool 12 m au moment
  de la sortie, pour la part sortie.

Exemple, article valorisé à la pièce : pool NOIR 12 m, deux barres à 100
et 120 DT. Valeur 220 DT, CMP 110 DT par barre. Un supplément de 1 × 6 m
retire 0,5 barre : 220 × 0,5 ÷ 2 = 55 DT. Il reste 165 DT pour 1,5 barre :
le CMP reste 110 DT.

**[CT]** Le cache du CMP (`cmp_stock_general`, `cmp_historique`) compte
aujourd'hui des pièces entières. Il devra compter en unités. Ce sont des
caches reconstructibles, pas des tables immuables.

---

## I. Registre append-only [PROP]

Exemple complet : 1 barre de 12 m, vendue en deux fois.

| N° | Type de mouvement | Pièces | Longueur de la pièce | Unités | Solde du lot |
|---|---|---|---|---|---|
| 1 | ENTREE_RECEPTION_FOURNISSEUR | + 1 | 12 m | + 2 | 2 unités = 1 barre |
| 2 | SORTIE_LIVRAISON_CLIENT | − 1 | 6 m | − 1 | 1 unité = reliquat 6 m |
| 3 | SORTIE_LIVRAISON_CLIENT | − 1 | 6 m | − 1 | 0 |

- Trois lignes, toutes de types qui existent déjà. Aucune ligne de
  conversion, aucune ligne de transformation (LG1).
- Rien n'est modifié ni supprimé : seules des lignes s'ajoutent.
- **[CT]** L'information nouvelle est une colonne « longueur de la
  pièce » sur le mouvement. Vide = longueur du lot : toutes les lignes
  existantes et tous les lots autres que 12 m gardent leur sens.
- Le registre reste la seule source de vérité : il suffit à lui seul à
  dire ce qui est sorti et ce qui reste. On ne va pas chercher la
  longueur dans un autre document.

---

## J. Allocations [PROP]

### J.1 Contrôle lot / ligne (LG7)

| Contrôle | Règle |
|---|---|
| Article | Identique |
| Finition | Identique (LAC = NOIR). NOIR → GALVA ou GPP n'est jamais une compatibilité directe : c'est le chemin de transformation de la v9 |
| Longueur | Identique, **ou** lot 12 m pour une ligne 6 m |
| Disponibilité | En unités (J.2) |

| Lot | Ligne | Résultat |
|---|---|---|
| 12 m | 12 m | Accepté, 2 unités par pièce |
| 12 m | 6 m | Accepté, 1 unité par pièce |
| 6 m | 6 m | Accepté, comme aujourd'hui |
| 6 m | 12 m | **Refusé** (LG6) |
| NOIR 12 m | GALVA 6 m | **Refusé** en affectation directe (LG2) |
| GALVA 12 m | GALVA 6 m | Accepté |
| GPP 12 m | GPP 6 m | Accepté |

Le contrôle est fait dans le service **et** doublé dans la base, pour
qu'une écriture directe ne puisse plus le contourner (cas 4 de l'audit).

### J.2 Plafond

Pour un lot de 12 m présent chez GMC :

`2 × (pièces de 12 m affectées) + (pièces de 6 m affectées) + 2 × (barres réservées ou engagées) ≤ unités physiques`

Seules comptent les affectations actives non encore sorties. Les
réservations de lot brut (CT21, validé) et les quantités engagées dans un
BST préparé portent sur des barres entières : 2 unités chacune.

- L'engagement dans un BST préparé vient de la lecture **L-k, validée
  le 02/10** : il entre dans la formule.
- Les **réservations de devis** sont informatives : elles ne sont jamais
  déduites du disponible. **[FACT]** C'est déjà le comportement du code
  (`reserve_devis_informatif`).

### J.3 Ce que l'allocation garantit

| Question | Réponse |
|---|---|
| Réserve une quantité ? | Oui, en pièces de la ligne |
| Identifie le lot source ? | Oui |
| Respecte 12 m → 6 m ? | Oui, par le compte en unités |
| Allocation partielle ? | Oui, à la pièce de 6 m |
| Conserve le reliquat ? | Oui, c'est l'unité libre du lot |

Le choix du lot reste manuel (D5) : le système ne choisit jamais.

---

## K. Disponibilité [PROP]

Pour un lot de 12 m : `unités libres = unités physiques − engagements de J.2`.

- **Disponible en 6 m** (article, finition) = pièces libres des lots 6 m
  + unités libres des lots 12 m.
- **Disponible en 12 m** = pour chaque lot 12 m, unités libres ÷ 2
  (division entière), puis somme. Le calcul se fait **lot par lot** : deux
  reliquats de deux lots ne font pas une barre.

Exemple : lot de 2 barres (4 unités). Ligne A affectée 1 × 6 m, ligne B
affectée 1 × 12 m. Unités libres : 4 − 1 − 2 = 1. Disponible en 6 m : 1.
Disponible en 12 m : 0.

**Pas de double comptage.** La même barre libre apparaît dans « disponible
6 m » (2) et dans « disponible 12 m » (1). Ces deux chiffres répondent à
deux questions différentes et **ne s'additionnent jamais**. Le stock
total se lit en pièces physiques par lot (barres et reliquats), en mètres
ou en poids. L'écran de disponibilité 6 m distingue « lots 6 m » et
« issu de barres 12 m ».

---

## L. Reconstruction du stock [PROP]

- Solde d'un lot = somme des unités entrées − somme des unités sorties,
  lues dans le registre. Aucune quantité n'est stockée ailleurs.
- La reconstruction du CMP relit le registre dans l'ordre et applique G.1
  à chaque ligne. Deux reconstructions successives donnent le même
  résultat.
- Le contrôle de conservation existant (`verifier_conservation`) passe en
  unités.
- Valeur d'un lot = coût d'entrée − coûts sortis : toujours recalculable.

---

## M. Contraintes et triggers

**[FACT]** Objets actuels qui comptent des pièces :

| Objet | Rôle actuel |
|---|---|
| `trg_mouvement_solde_source` | Refuse une sortie supérieure au solde |
| `trg_affectation_plafond` | Total affecté ≤ quantité initiale du lot |
| `trg_bl_client_ligne_plafond` | Livraison ≤ affecté non livré |
| `trg_reception_transfo_plafond` | Reçu + chute ≤ envoyé (bloque 1 → 2 pièces) |
| `trg_reaffectation_*` | Réaffectation |
| `v_solde_lot_emplacement`, `v_stock_non_affecte_par_lot` | Soldes |
| `v_approvisionnement_ligne`, `v_bilan_chutes_annuel` | Approvisionnement, chutes |

**[PROP]** À la migration :

1. Longueur de la pièce autorisée : celle du lot, ou 6 m si le lot fait
   12 m. Toute autre valeur refusée.
2. L'entrée d'origine d'un lot se fait toujours en pièces de la longueur
   du lot.
3. Solde à la source et plafond d'affectation calculés en unités.
4. Contrôle lot / ligne de J.1 à l'insertion d'une affectation.
5. Vues de solde en unités, avec la lecture « barres + reliquat ».
6. `trg_reception_transfo_plafond` : à traiter en 5.8. Le compte en
   unités lève naturellement le blocage 25 × 12 m → 50 × 6 m (50 unités
   reçues pour 50 envoyées).

---

## N. Migration nécessaire — aucune n'est créée

**[V V10-6]** Une migration **corrective dédiée**, clairement
identifiable, jamais mélangée à une migration fonctionnelle. Aucune
migration et aucune modification du schéma maintenant.

| N° | Table ou objet | Changement prévu |
|---|---|---|
| N1 | `mouvement_stock` | Colonne « longueur de la pièce », facultative ; vide = longueur du lot |
| N2 | `affectation_stock` | Même colonne ; contrôle lot / ligne ; plafond en unités |
| N3 | `bl_client_ligne` | Longueur de la pièce livrée (reprise de la ligne de commande) |
| N4 | Vues | Lecture physique et disponibilité (section T) |
| N5 | Triggers de M | Remplacés ou ajoutés |
| N6 | Cache CMP | Quantités en unités ; recalculé par le moteur, comme à chaque reconstruction aujourd'hui |

- **Aucune donnée supprimée, aucune ligne réécrite, aucune table
  reconstruite.** Les colonnes sont ajoutées aux tables existantes ; les
  lignes existantes ne sont pas touchées. **[FACT]** Vérifié sur une copie
  jetable de la base : l'ajout d'une colonne facultative aux trois tables
  est accepté, les triggers d'immuabilité restent en place,
  `integrity_check` = ok.
- **[CT, corrigé]** La version 10 proposait de reconstruire les tables
  comme les migrations 0017 et 0018. C'est abandonné : l'ajout simple de
  colonnes suffit et respecte ta précision « aucune donnée historique
  reconstruite arbitrairement ».
- **[FACT]** La base ne contient aucune donnée métier aujourd'hui.
- Aucune migration déjà appliquée n'est modifiée.

**Ordre validé [V V10-6, V10-7]** : V10 validée → règles et documentation
(`BUSINESS_RULES.md`, `PROJECT_STATUS.md`, `CURRENT_SESSION.md`,
`CHANGELOG.md`, documents concernés) → tests écrits d'abord → migration
dédiée → code (disponibilité, compatibilité lot / ligne, allocation,
valorisation, reconstruction, contraintes et triggers) → tests complets
(nouveaux, existants, reconstruction, intégrité, `--fresh`,
non-régression) → rapport → validation.

Étape en cours : aucune. Tu as demandé de verrouiller d'abord les
lectures L et les propositions C.

Code à adapter au codage, pour information : `core/conversion_longueur.py`
(une seule conversion), `repositories/stock_repository.py`,
`services/stock_service.py`, `db/valorisation.py`, futur
`affectation_service`.

---

## O. Tests nécessaires — aucun n'est écrit

### O.1 Tes quinze tests (LG9)

| N° | Scénario | Attendu |
|---|---|---|
| T01 | 1 × 12 m, commande 1 × 12 m | Accepté ; reste 0 |
| T02 | 1 × 12 m, commande 2 × 6 m | Accepté ; reste 0 |
| T03 | 1 × 12 m, commande 1 × 6 m | Accepté ; reliquat 1 × 6 m ; disponible 6 m = 1 ; disponible 12 m = 0 |
| T04 | Reliquat 1 × 6 m, commande 1 × 6 m | Accepté ; reste 0 |
| T05 | 1 × 12 m, commande 3 × 6 m | Refusé : 3 unités demandées, 2 disponibles |
| T06 | 2 × 6 m, commande 1 × 12 m | Refusé |
| T07 | 1 × 6 m, commande 1 × 12 m | Refusé |
| T08 | NOIR 12 m, ligne GALVA 6 m | Refusé en compatibilité directe |
| T09 | GALVA 12 m, ligne GALVA 6 m | Accepté |
| T10 | GPP 12 m, ligne GPP 6 m | Accepté |
| T11 | Coût 12 m / 6 m | 100 → 50 sortis ; tableau G.2 pour pièce, mètre, kg |
| T12 | Reliquat et sa valeur | 1 unité ; 50 ; 100,001 → 50,001 + 50,000 |
| T13 | Reconstruction après consommation partielle | Mêmes soldes et mêmes valeurs après deux reconstructions |
| T14 | Absence de double comptage | Coûts sortis + valeur restante = coût du lot ; 6 m et 12 m non additionnés ; conservation vérifiée |
| T15 | Traçabilité | Affectation, BL, mouvement et reliquat portent le même lot |

### O.2 Compléments proposés

| N° | Scénario | Attendu |
|---|---|---|
| T16 | 12 m → 4 m, 12 m → 3 m, 6 m → 3 m | Refusés (LG3) |
| T17 | Deux reliquats de 6 m dans deux lots, commande 1 × 12 m | Refusé |
| T18 | Lot de 2 barres : 1 × 6 m et 1 × 12 m affectés, puis 1 × 12 m | Troisième affectation refusée ; 1 unité libre |
| T19 | Supplément de 6 m sur un pool 12 m | Exemple de la section H : 55 ; CMP inchangé ; aucun pool 6 m créé |
| T20 | Écriture directe en base d'un lot 6 m sur une ligne 12 m | Refusée par la base |
| T21 | Entrée d'origine d'un lot 12 m saisie en pièces de 6 m | Refusée |
| T22 | Lot 6 m ordinaire | Comportement identique à aujourd'hui |
| T23 | Stock 2 × 12 m + 1 × 6 m dans un lot, demande 1 × 6 m (ton exemple V10-1) | La pièce de 6 m sort ; 2 barres restent intactes |
| T24 | Exemple T.4 : 3 barres, 360 kg, 300 TND, vente 1 × 6 m | Donnée source du lot identique ; lecture physique « 2 barres + 1 pièce de 6 m », 300 kg, 250 TND ; jamais « 5 × 6 m » en stock physique |
| T25 | Poids : barre de 120 kg, sortie 1 × 6 m | 60 kg sortis ; poids fournisseur du lot inchangé |
| T26 | Reliquat libre dans le lot A, affectation 1 × 6 m demandée sur une barre neuve du lot B (V10-8) | Avertissement nommant le lot A, rien n'est écrit ; avec confirmation et motif : affectation créée, motif et choix dans l'audit ; sans motif : refusée |

### O.3 Non-régression

- Les 293 tests existants passent **sans changer une assertion**.
  **[FACT]** Tous leurs lots sont en 6 m.
- Reconstruction complète de la base deux fois : schéma identique.
- `integrity_check` et `foreign_key_check` sans anomalie.

---

## P. Impact sur les phases

| Phase | Impact |
|---|---|
| **5.6** Affaires | Contrôle lot / ligne et plafond en unités dans `affectation_service` ; disponibilité 6 m et 12 m ; `core/conversion_longueur.py` limité à 12 → 6. Réservation de lot brut et BST : barres entières, 2 unités chacune |
| **5.7** Achats | Aucun changement des documents : un achat en 12 m crée un lot 12 m. L'achat par excès (P-MULT) reste valable |
| **5.8** Transformations | Les lignes de BST portent la longueur des pièces ; un reliquat de 6 m NOIR peut partir en galvanisation ou en GPP (V10-5) ; la réception se compte en unités, ce qui règle 25 × 12 m → 50 × 6 m ; chutes en unités |
| **5.9** Livraisons | Une ligne 6 m servie par un lot 12 m sort en pièces de 6 m ; poids de stock selon G.3 ; garde-fou CT11 en unités |
| **5.10** Coûts, marge | Coût proportionnel à la longueur ; valeur du reliquat par différence. La v9 renvoyait cette règle à la 5.10 : elle est décidée (LG5) |
| Inventaire | Comptage en barres entières et pièces de 6 m par lot ; corrections en unités |

### Textes de la v9 et du dépôt remplacés par tes décisions

| Texte | Devient |
|---|---|
| `BUSINESS_RULES.md` §22, K2 : « un lot brut de 12 m n'est jamais considéré comme directement disponible en 6 m » | **SUPERSEDED PAR LG8** |
| v9 §6.12 : les exceptions de longueur « passent par une transformation » | **SUPERSEDED PAR LG1, LG2** à finition identique ; inchangé quand la finition change |
| v9 §6.3 bis et M76 : « coupe seule refusée » | La réservation pour transformation reste refusée (aucune transformation) ; l'**affectation directe** est acceptée (LG1) |
| v9 Q-COUPE : proposition « non » | **SUPERSEDED** : oui |
| v9 §8, `core/conversion_longueur.py` : « multiple exact » | **SUPERSEDED PAR LG3** : une seule conversion |
| v9 DB12 : plafond « en pièces du lot » | En unités pour un lot 12 m |
| v9 §7.2, 5.10 : « règle de coût à écrire » pour le reliquat | **Décidée** : LG5 |

D1, P-MULT, CT18 et le chemin NOIR 12 m → transformation → GALVA 6 m
restent valables.

---

## Q. Risques

| N° | Risque | Parade |
|---|---|---|
| R1 | La modification touche le registre et le moteur validés en 5.5 | Migration dédiée, faite uniquement d'ajouts ; 293 tests inchangés ; reconstruction deux fois |
| R2 | Écart entre le système et le parc si une barre neuve est entamée alors qu'un reliquat existe | Règle V10-1 validée ; avertissement entre lots V10-8 ; correction d'inventaire avec PV |
| R3 | Additionner « disponible 6 m » et « disponible 12 m » | Une seule source : les unités ; écrans qui distinguent l'origine |
| R4 | Coût non proportionnel pour les articles au kg si le poids est saisi librement | Poids calculé, V10-2 |
| R5 | Millime compté deux fois | Valeur du reliquat par différence, V10-3 |
| R6 | Une IA lit K2 ou la v9 et applique l'ancienne règle | Table « remplacés » ci-dessus ; mise à jour de `BUSINESS_RULES.md` et des fichiers d'état avant tout codage |
| R7 | Tentation d'un moteur générique de conversions | Conversion écrite en dur ; test T16 |
| R8 | Longueurs proches de 12 m (11,9 m, 12,1 m) | La règle ne s'applique qu'à 12 m exactement ; tout le reste se comporte comme aujourd'hui |
| R9 | Confusion entre reliquat de barre, reliquat de conversion et reliquat de commande | Trois noms distincts, section E |

---

## R. Variantes examinées et écartées

| Variante | Pourquoi elle est écartée |
|---|---|
| Convertir à l'entrée : enregistrer 2 pièces de 6 m pour chaque barre de 12 m | On ne sait plus quelles pièces forment encore une barre entière : la vente en 12 m et « ne peut plus être vendu comme 12 m » deviennent impossibles à garantir |
| Créer un lot enfant de 6 m au moment de la coupe | C'est un mouvement de conversion dans le registre (contraire à LG1) et un second CMP 6 m (contraire à LG5) |
| Fusionner les pools 12 m et 6 m | Change la règle de valorisation validée en Phase 4 sans nécessité |
| Quantités à virgule (0,5 barre) dans le registre | Le registre perd ses nombres entiers de pièces ; contrôles et inventaire deviennent ambigus |

---

## S. Validations reçues le 02/10 [V]

| N° | Décision | Précisions que tu as ajoutées |
|---|---|---|
| **V10-1** | Oui : le reliquat de 6 m est consommé avant d'entamer une nouvelle barre | Pas un FIFO général ; règle propre aux reliquats de la conversion 12 m → 6 m ; déterministe et auditable |
| **V10-2** | Oui : une pièce de 6 m pèse la moitié d'une barre de 12 m (120 kg → 60 kg) | Traçabilité vers le lot source ; aucun nouveau poids fournisseur ; valeur calculée à partir de la longueur, du poids et de la quantité source |
| **V10-3** | Oui : valeur du reliquat par différence | Valeur sortie + valeur restante = valeur initiale, à l'unité monétaire minimale près ; règle d'arrondi existante respectée |
| **V10-4** | Oui : affichage « 2 barres de 12 m + 1 pièce de 6 m » | Ne jamais afficher « 5 × 6 m » comme stock physique ; conserver longueur physique et origine, quantité, reliquat, lot source, valeur |
| **V10-5** | Oui : un reliquat de 6 m NOIR peut partir en galvanisation ou en GPP | Relève de la 5.8 : reliquat → sortie → transformation → réception → nouveau lot transformé ; ne pas confondre avec la règle 12 m → 6 m |
| **V10-6** | Oui : migration corrective dédiée | Clairement identifiable ; aucune migration ni changement de schéma maintenant ; toutes les données existantes préservées |
| **V10-7** | Oui : ordre des travaux | Documentation, tests, migration, code, tests complets, rapport (section N) |
| **V10-8** | Validée avec ta variante : avertissement + confirmation + motif obligatoire + audit | Pas de refus automatique ; pas de choix automatique du lot ; pas de FIFO général ; intégrée à l'analyse seulement |

---

## T. Donnée physique du lot et disponibilité commerciale : structure cible [PROP]

Réponse à ton point technique : le système ne transforme jamais
« 1 × 12 m » en « 2 × 6 m » dans la donnée source du lot.

### T.1 Trois niveaux séparés

| Niveau | Contenu | Nature | Où |
|---|---|---|---|
| 1. Donnée source du lot | Longueur d'achat, nombre de barres achetées, poids fournisseur, prix | **Stockée, jamais modifiée** | table `lot` : aucun changement |
| 2. Faits physiques | Chaque entrée et chaque sortie : nombre entier de pièces et leur longueur réelle | **Stockés, jamais modifiés** | registre `mouvement_stock` |
| 3. Lectures | État physique du lot ; disponibilité commerciale | **Calculées, jamais stockées** | vues et fonctions |

### T.2 Ce qui est stocké

| Table | Donnée | Sens | Changement |
|---|---|---|---|
| `lot` | `longueur_m` | Longueur physique d'achat : 12 m | Aucun |
| `lot` | `quantite_initiale` | Nombre de barres achetées | Aucun |
| `lot` | `poids_initial_kg` | Poids fournisseur | Aucun |
| `mouvement_stock` | `quantite` | Nombre entier de pièces déplacées | Aucun |
| `mouvement_stock` | longueur de la pièce | Longueur réelle des pièces déplacées ; vide = longueur du lot | **Ajout** |
| `affectation_stock` | `quantite` | Nombre de pièces de la ligne | Aucun |
| `affectation_stock` | longueur de la pièce | Longueur des pièces affectées | **Ajout** |

Ce qui n'est **pas** ajouté : aucune colonne « quantité en 6 m » dans le
lot, aucune « longueur normalisée », aucun lot enfant, aucun type de
mouvement nouveau.

### T.3 Ce qui est calculé

- **Lecture A — état physique d'un lot**, par emplacement : barres
  entières de 12 m ; pièces de 6 m en reliquat ; poids restant ; valeur
  restante. C'est ce que l'écran de stock affiche (V10-4).
- **Lecture B — disponibilité commerciale**, par article, finition et
  longueur demandée : quantité disponible, avec son origine (lots de la
  longueur demandée ; reliquats ; équivalence de barres entières).
- **Calcul intermédiaire** : les unités de 6 m (section D). Elles servent
  aux contrôles et ne sont jamais présentées comme le stock physique.

**[CT]** Deux vues en base, l'une pour la lecture A, l'autre pour la
lecture B, lues par `stock_service`. Noms à fixer au codage.

### T.4 Exemple complet

Lot acheté : 3 barres de 12 m, 360 kg, 300 TND, soit 120 kg et 100 TND
par barre. Vente de 1 × 6 m.

| Niveau | Avant la vente | Après la vente |
|---|---|---|
| 1. Donnée source | 12 m ; 3 barres ; 360 kg ; 300 TND | **Identique** |
| 2. Registre | Entrée : + 3 pièces de 12 m, 360 kg | + une ligne : sortie de 1 pièce de 6 m, 60 kg |
| 3. Lecture A (physique) | 3 barres de 12 m ; 360 kg ; 300 TND | **2 barres de 12 m + 1 pièce de 6 m** ; 300 kg ; 250 TND |
| 3. Lecture B (commerciale) | En 12 m : 3. En 6 m : 6, par équivalence | En 12 m : 2. En 6 m : 5, dont 1 reliquat et 4 par équivalence de 2 barres |

Le chiffre « 5 » n'existe que dans la lecture B, présenté comme une
équivalence commerciale. Le stock physique reste « 2 barres + 1 pièce ».

Relation conservée, sans transformation :

```
LOT SOURCE 12 m — 3 barres — 360 kg — 300 TND
      │
      ├── sortie 1 × 6 m      60 kg    50 TND   (BL client)
      │
      ├── reliquat 1 × 6 m    60 kg    50 TND
      │
      └── 2 barres de 12 m   240 kg   200 TND
```

Contrôle : 50 + 50 + 200 = 300 TND ; 60 + 60 + 240 = 360 kg.

### T.5 Priorité du reliquat entre plusieurs lots [V V10-8]

**[FACT]** À l'intérieur d'un lot, la priorité est garantie par le
compte en unités. Entre plusieurs lots, le lot est choisi à la main (D5)
et le système ne choisit jamais.

**[V V10-8, 02/10]** Variante retenue : **avertissement + confirmation +
motif obligatoire + audit**. Le refus automatique que je proposais n'est
pas retenu.

Cas : le lot A contient un reliquat libre de 1 × 6 m. Le lot B contient
des barres neuves de 12 m. La demande porte sur 1 × 6 m et l'utilisateur
sélectionne le lot B.

Le système doit :

1. détecter qu'un reliquat compatible de 6 m existe dans le lot A ;
2. afficher un avertissement clair ;
3. indiquer le lot concerné ;
4. permettre à l'utilisateur de confirmer son choix du lot B ;
5. exiger un motif si le lot B est choisi malgré le reliquat disponible ;
6. conserver le choix et le motif dans l'audit.

Message validé :

```
ATTENTION

Le lot A contient déjà un reliquat compatible de 1 × 6 m.

Vous avez sélectionné le lot B.

Continuer ?
Motif obligatoire : __________
```

Le système ne doit **ni** choisir automatiquement le lot A, **ni** imposer
un FIFO général, **ni** bloquer systématiquement le choix du lot B.
Principe conservé : le choix du lot reste manuel et auditable.

Précisions d'analyse, à corriger si elles ne te conviennent pas :

- **[PROP]** « Compatible » = même article, même finition, reliquat
  **libre** (non affecté, non réservé), présent chez GMC.
- **[PROP]** L'avertissement apparaît seulement quand l'opération
  entamerait une barre neuve de 12 m. Choisir un lot réellement acheté
  en 6 m ne déclenche rien : ta règle ne vise que les reliquats de la
  conversion.
- **[CT]** Déroulement en deux temps : la première demande ne modifie
  rien et renvoie l'avertissement avec le ou les lots concernés ; la
  seconde, avec la confirmation et le motif, enregistre l'affectation.
- **[CT]** Le motif est conservé avec l'affectation et dans le journal
  d'audit (utilisateur, date et heure, lot choisi, lot portant le
  reliquat, motif). Une action d'audit nouvelle est à prévoir.
- **[CT]** Ce contrôle vit dans le service. Aucun trigger ne refuse
  l'opération, puisqu'elle est permise.

Rien n'est codé pour V10-8 : ni code, ni migration, ni test
d'implémentation, tant que l'ensemble de la Phase 5.6 n'est pas validé.

### T.6 Reliquat envoyé en transformation [V V10-5]

Traité en 5.8, sans rien ajouter ici : reliquat 6 m NOIR → sortie
transformation → transformation → réception → **nouveau lot transformé**,
dont le lot parent est le lot source de 12 m. La règle 12 m → 6 m
n'intervient pas dans cette chaîne.

---

Aucun point de la v10 ne reste en attente.

---

**PHASE 5.6 — V10 VALIDÉE — LECTURES L ET PROPOSITIONS C TRANCHÉES — AUCUN CODE**
