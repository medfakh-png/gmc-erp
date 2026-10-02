"""
Hiérarchie des erreurs métier GMC (Phase 5.3).

Objectif : traduire les rejets bruts de SQLite (`sqlite3.IntegrityError`,
souvent un nom de trigger dans le message) en erreurs Python explicites,
avec un message en français exploitable — l'utilisateur final n'est pas
développeur et ne doit jamais voir un message SQLite brut.

Deux façons d'obtenir une `ErreurMetier` :
  1. la lever directement (ex. `raise ErreurEnregistrementIntrouvable(...)`)
     quand le code applicatif détecte lui-même le problème (pas une
     violation de contrainte SQLite) ;
  2. laisser SQLite rejeter l'opération, puis appeler
     `traduire_erreur_sqlite(exc)` sur l'exception SQLite d'origine pour
     obtenir l'équivalent métier.

Aucune règle métier n'est ajoutée ici : ce module ne fait que nommer et
traduire des règles déjà appliquées par les migrations/triggers existants
(Phase 4/4.1) — il ne décide de rien par lui-même.
"""

from __future__ import annotations

import sqlite3


class ErreurMetier(Exception):
    """
    Base de toute erreur métier GMC. Ne jamais lever directement — toujours
    une sous-classe plus précise, ou `ErreurRegleViolee` en dernier
    recours.
    """


class ErreurStockInsuffisant(ErreurMetier):
    """Un mouvement retirerait plus que ce qu'un lot possède réellement à l'emplacement source."""


class ErreurPlafondDepasse(ErreurMetier):
    """
    Une affectation, une livraison ou une réception de transformation
    dépasserait le plafond autorisé (quantité du lot, quantité affectée non
    livrée, ou quantité envoyée en transformation).
    """


class ErreurReaffectationInvalide(ErreurMetier):
    """
    Une réaffectation viole une des règles du workflow imposé (déjà
    physiquement livrée, origine déjà réaffectée) — voir
    `docs/DATABASE.md` §« Réaffectation ».
    """


class ErreurEnregistrementImmuable(ErreurMetier):
    """
    Tentative de modification (UPDATE) ou de suppression (DELETE) d'un
    enregistrement protégé par trigger — soit totalement immuable
    (`mouvement_stock`, `taux_change`, `regularisation_prix_fournisseur`,
    `journal_audit`), soit un document métier dont seule la suppression
    est interdite (une annulation tracée doit être utilisée à la place).
    """


class ErreurDeviseMelangee(ErreurMetier):
    """
    Une opération mélangerait deux devises dans un même pool CMP
    (garde-fou de `db/valorisation.py`).
    """


class ErreurEnregistrementIntrouvable(ErreurMetier):
    """
    Recherche d'un enregistrement par identifiant qui n'existe pas — ce
    n'est jamais une violation de contrainte SQLite, c'est le code
    applicatif qui le détecte lui-même (ex. un repository qui ne trouve
    aucune ligne).
    """


class ErreurRegleViolee(ErreurMetier):
    """
    Repli générique : une contrainte SQLite (trigger ou CHECK) a rejeté
    l'opération, mais aucune sous-classe plus précise ne correspond. Le
    message technique d'origine est conservé pour le diagnostic, préfixé
    d'un message français générique.
    """


# ---------------------------------------------------------------------------
# Erreurs du Stock Service (Phase 5.5)
# ---------------------------------------------------------------------------


class ErreurQuantiteInvalide(ErreurMetier):
    """
    Quantité (nombre de pièces) ou poids invalide : non entier, nul,
    négatif, ou incohérent avec le document ou le stock (ex. retirer plus
    de poids qu'il n'en reste à l'emplacement).
    """


class ErreurEmplacementInvalide(ErreurMetier):
    """
    Emplacement inconnu ou mal formé (seuls STOCK_GMC,
    CHEZ_TRANSFORMATEUR:<id d'un transformateur existant>, CHUTES et LIVRE
    existent), ou emplacement non autorisé pour l'opération demandée.
    """


class ErreurMouvementIncoherent(ErreurMetier):
    """
    Le mouvement demandé ne respecte pas les règles de son type : couple
    type / emplacement source / emplacement destination non autorisé, lot
    ne correspondant pas au document source, quantité différente de celle
    du document, ou type de mouvement non pris en charge par cette voie.
    """


class ErreurDocumentSourceManquant(ErreurMetier):
    """
    Tout mouvement physique doit être rattaché au document qui le
    déclenche (règle Phase 1 §28.8) : document absent, inexistant, ou d'un
    type inattendu pour ce mouvement.
    """


class ErreurMouvementEnDouble(ErreurMetier):
    """
    Le mouvement a déjà été enregistré (ex. une deuxième entrée pour le
    même lot, une deuxième sortie pour la même ligne de BL client) —
    l'accepter compterait deux fois la même marchandise.
    """


class ErreurMotifObligatoire(ErreurMetier):
    """Une correction d'inventaire doit toujours être justifiée par un motif."""


class ErreurDisponibiliteInsuffisante(ErreurMetier):
    """
    La quantité demandée dépasse la quantité réellement disponible (stock
    physique GMC moins ce qui est déjà affecté et pas encore sorti) — à
    distinguer de `ErreurStockInsuffisant`, qui concerne le stock physique
    seul.
    """


class ErreurMontantIncoherent(ErreurMetier):
    """Valeur monétaire incohérente (ex. valeur ≠ quantité × coût unitaire)."""


class ErreurInventaireInitialInvalide(ErreurMetier):
    """
    Inventaire initial de démarrage impossible à enregistrer tel que demandé
    (déjà créé, opérations déjà commencées, date de mise en service
    invalide...). L'inventaire initial est unique : il devient le stock
    initial du système au moment exact de sa mise en service.
    """


class ErreurUniteManquante(ErreurMetier):
    """
    Saisie d'une quantité, d'un poids, d'une longueur, d'un prix ou d'un
    montant sans son unité (règle transversale validée Phase 5.5 : le
    système ne devine jamais une unité implicite).
    """


class ErreurSaisieInvalide(ErreurMetier):
    """
    Saisie refusée : valeur illisible ou ambiguë (ex. « 2.500 kg »), unité
    inconnue, unité d'une autre nature que celle attendue, ou unité non
    encore prise en charge pour cette opération.
    """


class ErreurUniteValorisation(ErreurMetier):
    """
    Unité de valorisation (CMP / coût de revient) absente, incohérente ou non
    convertible (règle définitive validée Phase 5.5) : le CMP est toujours
    exprimé dans l'unité de valorisation de l'article (DT/kg, DT/ml,
    DT/unité, DT/tonne) ; aucune unité n'est imposée ni supposée par défaut,
    aucune conversion implicite n'est faite.
    """


# ---------------------------------------------------------------------------
# Traduction des erreurs SQLite brutes
# ---------------------------------------------------------------------------

# Association fragment de message -> (classe, message français). Vérifiée
# contre les triggers réels de la base (`migrations/0012_*.sql`,
# `0013_*.sql`, `0015_*.sql`, `0017_*.sql`).
#
# Correction Phase 5.5 : SQLite ne place PAS le nom du trigger dans le
# message d'une `IntegrityError` levée par `RAISE(ABORT, '...')` — seul le
# texte du RAISE est transmis. La version Phase 5.3 ne reconnaissait que les
# noms de triggers (donc, en conditions réelles, tombait toujours sur le
# repli générique). Chaque entrée reconnaît désormais le nom du trigger ET
# un fragment distinctif du vrai message RAISE ; la reconnaissance par nom
# est conservée (rétrocompatibilité, tests Phase 5.3 inchangés).
_TRIGGERS_CONNUS: tuple[tuple[tuple[str, ...], type[ErreurMetier], str], ...] = (
    (
        ("trg_mouvement_solde_source", "solde insuffisant du lot"),
        ErreurStockInsuffisant,
        "Ce mouvement retirerait plus que ce que le lot possède réellement à cet emplacement.",
    ),
    (
        ("trg_affectation_plafond", "affectation refusée : dépasse la quantité disponible"),
        ErreurPlafondDepasse,
        "Cette affectation dépasserait la quantité disponible du lot.",
    ),
    (
        ("trg_bl_client_ligne_plafond", "livraison refusée : dépasse la quantité affectée"),
        ErreurPlafondDepasse,
        "Cette livraison dépasserait la quantité affectée non encore livrée.",
    ),
    (
        ("trg_reception_transfo_plafond", "réception de transformation refusée"),
        ErreurPlafondDepasse,
        "Reçu + chute dépasserait la quantité envoyée en transformation.",
    ),
    (
        ("trg_reaffectation_origine_active", "réaffectation refusée"),
        ErreurReaffectationInvalide,
        "Cette affectation ne peut pas être réaffectée "
        "(déjà physiquement livrée, ou déjà réaffectée).",
    ),
    (
        ("trg_reaffectation_cloture_origine",),
        ErreurReaffectationInvalide,
        "Impossible de clôturer l'affectation d'origine de cette réaffectation.",
    ),
    (
        ("trg_commande_ligne_qte_immuable", "quantite_originale est immuable"),
        ErreurEnregistrementImmuable,
        "La quantité originale d'une ligne de commande confirmée ne peut jamais être modifiée.",
    ),
    (
        ("trg_lot_no_update_quantite", "sont figés à la création"),
        ErreurEnregistrementImmuable,
        "La quantité initiale d'un lot ne peut jamais être modifiée après création.",
    ),
    (
        # Migration 0019 : unité de valorisation de l'article et unité du prix des lots.
        ("aucune unité de valorisation définie pour cet article",),
        ErreurUniteValorisation,
        "Aucune unité de valorisation n'est définie pour cet article : elle doit l'être "
        "avant tout lot ou toute valorisation (aucune unité n'est supposée par défaut).",
    ),
    (
        (
            "l'unité du prix du lot doit être l'unité de valorisation",
            "l'unité du coût doit être l'unité de valorisation",
            "le prix définitif doit être dans l'unité du prix du lot",
        ),
        ErreurUniteValorisation,
        "Les prix d'un lot s'expriment dans l'unité de valorisation en vigueur de l'article, "
        "ou dans l'autre unité de masse (kg <-> tonne) pour un article valorisé au poids "
        "(aucune conversion implicite).",
    ),
    (
        ("un prix définitif doit porter son unité",),
        ErreurUniteValorisation,
        "Un prix définitif doit être enregistré avec son unité d'origine, et inversement.",
    ),
    (
        ("lot.unite_valorisation_article est figée", "unite_valorisation_article est fixée"),
        ErreurEnregistrementImmuable,
        "L'unité de valorisation de l'article à la création du lot est fixée par la base.",
    ),
    (
        ("régularisation refusée",),
        ErreurUniteValorisation,
        "Régularisation refusée : chaque prix garde son unité d'origine, et l'écart est "
        "calculé par conversion exacte (kg <-> tonne uniquement).",
    ),
    (
        ("montant monétaire non entier refusé",),
        ErreurMontantIncoherent,
        "Un montant ou un prix enregistré est toujours un entier en unités monétaires "
        "minimales (millimes, centimes) : un nombre à virgule est refusé.",
    ),
    (
        ("lot.unite_prix est figée",),
        ErreurEnregistrementImmuable,
        "L'unité des prix d'un lot est figée à sa création.",
    ),
    (
        ("changement d'unité refusé", "unité de valorisation refusée"),
        ErreurUniteValorisation,
        "Changement d'unité de valorisation refusé : unité précédente, date d'effet ou "
        "mouvements déjà enregistrés incompatibles (aucune réécriture de l'historique).",
    ),
    (
        # Index uniques partiels de la migration 0017 (garde-fous M1) : une
        # seule entrée d'origine par lot, un seul mouvement d'un type donné
        # par ligne de document.
        ("UNIQUE constraint failed: mouvement_stock.",),
        ErreurMouvementEnDouble,
        "Ce mouvement de stock a déjà été enregistré : l'accepter compterait deux fois "
        "la même marchandise.",
    ),
)


def traduire_erreur_sqlite(exc: sqlite3.IntegrityError) -> ErreurMetier:
    """
    Traduit une `sqlite3.IntegrityError` (typiquement levée par un trigger
    ou une contrainte CHECK) en `ErreurMetier` avec un message français
    exploitable.

    Ne devine jamais une règle métier qui n'existe pas déjà dans le
    schéma : chaque traduction reconnue correspond à un trigger réel de la
    base. Un message non reconnu retombe sur `ErreurRegleViolee`, qui
    conserve le message technique d'origine plutôt que de l'escamoter.
    """
    message = str(exc)

    for fragments, classe, message_fr in _TRIGGERS_CONNUS:
        if any(fragment in message for fragment in fragments):
            return classe(message_fr)

    # Triggers d'immuabilité génériques : reconnus par leur nom (`*_no_delete`
    # / `*_no_update`) ou par le texte réel de leur RAISE (« suppression
    # interdite », « ... est immuable ... »).
    if "_no_delete" in message or "suppression" in message:
        return ErreurEnregistrementImmuable(
            "Cette suppression n'est pas autorisée — utilisez une annulation "
            f"tracée à la place. (détail technique : {message})"
        )
    if "_no_update" in message or "immuable" in message:
        return ErreurEnregistrementImmuable(
            "Cet enregistrement est immuable et ne peut pas être modifié. "
            f"(détail technique : {message})"
        )

    return ErreurRegleViolee(
        f"Opération refusée par une règle de la base de données. (détail technique : {message})"
    )
