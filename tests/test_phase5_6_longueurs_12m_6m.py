"""
Tests Phase 5.6 — règle définitive « barres de 12 m et de 6 m ».

Règle validée le 02/10/2026 (`docs/BUSINESS_RULES.md` §24, décisions LG1 à
LG9 et V10-1 à V10-7 ; analyse `docs/ANALYSE_PHASE_5_6_v10.md`) :

  - 1 barre de 12 m = 2 barres de 6 m pour la disponibilité commerciale, à
    finition identique, sans transformation, sans nouveau lot, sans second
    CMP ;
  - le sens inverse est interdit (2 × 6 m ne valent jamais 1 × 12 m) ;
  - une vente partielle laisse un reliquat de 6 m rattaché au lot source,
    consommé avant d'entamer une nouvelle barre ;
  - le coût suit la longueur ; valeur sortie + valeur restante = valeur
    initiale du lot.

ÉTAPE 2 DE L'ORDRE VALIDÉ (V10-7) — CES TESTS SONT ÉCRITS AVANT LA MIGRATION
ET AVANT LE CODE. Ils décrivent le comportement attendu ; la règle n'est pas
encore programmée. Conséquences :

  - les tests marqués `ATTEND_MIGRATION` ou `ATTEND_CODE` échouent
    aujourd'hui, et c'est attendu. Les premiers réussiront dès que la
    migration dédiée existera (étape 3) : ce sont des refus posés par la
    base. Les seconds demandent aussi le code (étape 4). Les marqueurs sont
    stricts : quand un test se met à réussir, pytest le signale, et son
    marqueur doit être retiré ;
  - les tests sans marqueur (T01, T22) réussissent déjà : ils prouvent que
    ce qui fonctionne aujourd'hui (12 m pour 12 m, lot de 6 m ordinaire)
    doit continuer à fonctionner à l'identique.

Contenu : les quinze tests obligatoires de Mohamed (LG9, T01 à T15) et les
compléments T16 à T25 de l'analyse v10 (§O.2). Le test T26 (V10-8,
avertissement quand un reliquat existe dans un autre lot) n'est
volontairement PAS écrit : aucun test pour V10-8 tant que l'ensemble de la
Phase 5.6 n'est pas validé.

NOMS TECHNIQUES PROVISOIRES. La v10 laisse les noms « à fixer au codage ».
Pour pouvoir écrire les tests d'abord, quatre noms sont posés ici, dans la
section « Adaptateur » ci-dessous, et nulle part ailleurs. Ce sont des
choix techniques, pas des règles métier : si un nom change au codage, seul
l'adaptateur change, jamais une attente métier. Les autres hypothèses
techniques de ces tests sont listées au même endroit, avec ce que ces tests
ne fixent volontairement pas.

Les affectations et les documents (BL client) sont créés par de simples
INSERT, comme dans les tests des Phases 4 à 5.5 : le service des affaires
(5.6) et celui des livraisons (5.9) n'existent pas encore. Les mouvements
de sortie passent par le Stock Service, seule voie d'écriture du registre.

Tous les montants attendus sont calculés à la main dans les commentaires.
Montants en millimes (1 DT = 1 000 millimes).
"""

from __future__ import annotations

import itertools
import sqlite3
import typing

import pytest

from core.configuration import configuration_test
from core.erreurs import ErreurDisponibiliteInsuffisante
from db import connexion, migrate, valorisation
from services import stock_service
from tests.helpers import (
    affecter,
    creer_commande,
    creer_lot_reception,
    definir_unite_valorisation,
    nid,
    seed_referentiels,
    tnd,
)

STOCK = stock_service.STOCK_GMC
LIVRE = stock_service.LIVRE

_PAS_ENCORE = "Règle 12 m / 6 m validée (BUSINESS_RULES §24) mais pas encore codée : "
ATTEND_MIGRATION = pytest.mark.xfail(
    strict=True,
    reason=_PAS_ENCORE + "refus posé par la base, attendu dès la migration dédiée (étape 3).",
)
ATTEND_CODE = pytest.mark.xfail(
    strict=True,
    reason=_PAS_ENCORE + "attendu après la migration (étape 3) et le code (étape 4).",
)

# Barre de référence des exemples : 12 m, 42 kg, 100 DT la barre.
POIDS_BARRE_KG = 42.0
PRIX_BARRE = tnd(100.0)  # 100 000 millimes


# ---------------------------------------------------------------------------
# Adaptateur — NOMS TECHNIQUES PROVISOIRES (choix techniques, à confirmer au
# codage ; aucun autre endroit du fichier ne les connaît)
# ---------------------------------------------------------------------------
#
# AUTRES HYPOTHÈSES TECHNIQUES DE CES TESTS (à confirmer au codage) :
#   a. `disponibilite(...)["disponible"]` garde son nom et donne la
#      disponibilité commerciale, équivalence 12 m -> 6 m comprise ;
#   b. un refus de la base arrive sous forme de `sqlite3.IntegrityError`
#      (trigger), comme aujourd'hui ;
#   c. `verifier_quantite_affectable` lève toujours
#      `ErreurDisponibiliteInsuffisante` ;
#   d. `cout_sortie_total_minor`, `cmp_actuel` et `verifier_conservation`
#      gardent leur nom ; pour un article valorisé à la pièce, la quantité de
#      valorisation d'un pool 12 m se compte en barres (une pièce de 6 m =
#      0,5 barre), comme dans l'exemple de la v10 §H ;
#   e. une longueur de pièce vide vaut « longueur du lot » sur le mouvement,
#      l'affectation et la ligne de BL client ;
#   f. `etat_physique_lot` lit le stock présent chez GMC ; sa valeur = coût
#      d'entrée du lot − coûts déjà sortis ;
#   g. une affectation livrée ne compte plus dans le plafond du lot.
#
# CE QUE CES TESTS NE FIXENT PAS, volontairement :
#   - la façon d'obtenir le poids d'une pièce de 6 m (calculé par le système,
#     ou saisi puis contrôlé) et le sort de la « dernière pièce » d'un lot ;
#   - le sens de `disponibilite(...)["physique_stock_gmc"]` pour le 6 m ;
#   - le contrôle lot / ligne côté service : le service des affaires (5.6)
#     n'existe pas encore, seul le contrôle de la base est testé ;
#   - V10-8 (reliquat dans un autre lot) : aucun test, sur consigne.

# 1. Colonne « longueur de la pièce » ajoutée par la future migration sur
#    mouvement_stock, affectation_stock et bl_client_ligne. Vide = longueur
#    du lot (v10 §N).
COLONNE_LONGUEUR_PIECE = "longueur_piece_m"

# 2. Paramètre correspondant du Stock Service
#    (`enregistrer_mouvement`, `verifier_quantite_affectable`).
PARAMETRE_LONGUEUR_PIECE = "longueur_piece_m"


class Lecture(typing.NamedTuple):
    """État physique d'un lot chez GMC (« lecture A » de la v10 §T.3)."""

    barres: int  # pièces entières à la longueur du lot
    pieces_6m: int  # reliquat de barre : 0 ou 1 pièce de 6 m
    poids_kg: float
    valeur_minor: int


def lecture_physique(conn, lot_id) -> Lecture:
    """3. Lecture « 2 barres de 12 m + 1 pièce de 6 m » (V10-4) : fonction et
    clés à créer dans le Stock Service."""
    etat = stock_service.etat_physique_lot(conn, lot_id)
    return Lecture(
        etat["barres_entieres"], etat["pieces_6m"], etat["poids_kg"], etat["valeur_minor"]
    )


def verifier_affectable(conn, lot_id, quantite, longueur_piece=None) -> None:
    """4. Contrôle de disponibilité du service, en pièces de la longueur indiquée."""
    if longueur_piece is None:
        stock_service.verifier_quantite_affectable(conn, lot_id, quantite)
    else:
        stock_service.verifier_quantite_affectable(
            conn, lot_id, quantite, **{PARAMETRE_LONGUEUR_PIECE: longueur_piece}
        )


# ---------------------------------------------------------------------------
# Fixtures et constructeurs
# ---------------------------------------------------------------------------


@pytest.fixture()
def conn(tmp_path):
    db_path = tmp_path / "gmc_longueurs_5_6.db"
    migrate.apply_migrations(db_path, fresh=True)
    c = connexion.get_connection(configuration_test(db_path))
    c.row_factory = sqlite3.Row  # tests/helpers.py lit les colonnes par leur nom
    yield c
    connexion.fermer(c)


@pytest.fixture()
def ids(conn):
    return seed_referentiels(conn)  # article de base : valorisé à la pièce (UNITE)


_horloge = itertools.count()


def _instant() -> str:
    """Horodatages distincts et croissants : l'ordre des sorties est certain."""
    n = next(_horloge)
    return f"2026-03-01T{8 + n // 3600:02d}:{n // 60 % 60:02d}:{n % 60:02d}.000"


def _inserer(conn, table: str, valeurs: dict) -> None:
    """INSERT direct ; annule proprement si la base refuse l'écriture."""
    colonnes = ", ".join(valeurs)
    marques = ", ".join("?" for _ in valeurs)
    try:
        conn.execute(
            f"INSERT INTO {table} ({colonnes}) VALUES ({marques})", tuple(valeurs.values())
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise


def _avec_longueur_piece(valeurs: dict, longueur_piece: typing.Optional[float]) -> dict:
    """Ajoute la longueur de la pièce seulement quand elle est précisée."""
    if longueur_piece is not None:
        valeurs = {**valeurs, COLONNE_LONGUEUR_PIECE: longueur_piece}
    return valeurs


def nouvel_article(conn, ids, unite: str) -> str:
    """Article de test valorisé dans `unite` (UNITE, ML ou KG)."""
    article_id = nid()
    conn.execute(
        "INSERT INTO article (id, designation, famille_id, masse_lineique_kg_m) VALUES (?,?,?,?)",
        (article_id, f"Tube {unite} {article_id[:4]}", ids["famille"], 3.5),
    )
    definir_unite_valorisation(conn, article_id, unite, ids["utilisateur"])
    conn.commit()
    return article_id


def _pour(ids, article: typing.Optional[str]) -> dict:
    return ids if article is None else {**ids, "article": article}


def creer_lot(
    conn,
    ids,
    *,
    barres=1,
    longueur=12.0,
    finition="NOIR",
    poids_piece=POIDS_BARRE_KG,
    prix=PRIX_BARRE,
    article=None,
) -> str:
    """Réception fournisseur : `barres` pièces de `longueur` m, entrées en STOCK_GMC."""
    return creer_lot_reception(
        conn,
        _pour(ids, article),
        quantite=barres,
        poids_kg=barres * poids_piece,
        prix_provisoire_minor=prix,
        finition=finition,
        longueur_m=longueur,
    )["lot_id"]


def creer_ligne(conn, ids, *, quantite, longueur, finition="NOIR", article=None) -> dict:
    """Commande confirmée d'une ligne : `quantite` pièces de `longueur` m."""
    return creer_commande(
        conn, _pour(ids, article), quantite=quantite, finition=finition, longueur_m=longueur
    )


def affecter_pieces(
    conn, ids, lot_id, cmd, quantite, *, poids, longueur_piece=None, type_="INITIALE", motif=None
) -> str:
    """Affectation écrite directement en base (le service des affaires viendra en 5.6)."""
    affectation_id = nid()
    _inserer(
        conn,
        "affectation_stock",
        _avec_longueur_piece(
            {
                "id": affectation_id,
                "lot_id": lot_id,
                "commande_ligne_id": cmd["commande_ligne_id"],
                "type": type_,
                "quantite": quantite,
                "poids_kg": poids,
                "utilisateur_id": ids["utilisateur"],
                "date_heure": "2026-02-01T08:00:00.000",
                "motif": motif,
            },
            longueur_piece,
        ),
    )
    return affectation_id


def ligne_bl_client(
    conn, lot_id, cmd, quantite, *, poids, longueur_piece=None, type_="INITIALE"
) -> str:
    """BL client d'une ligne (INSERT minimal) ; renvoie l'identifiant de la ligne."""
    bl_id, ligne_id = nid(), nid()
    _inserer(
        conn,
        "bl_client",
        {
            "id": bl_id,
            "numero": f"BLC-2026-{nid()[:8]}",
            "commande_client_id": cmd["commande_id"],
            "date": "2026-03-01",
        },
    )
    _inserer(
        conn,
        "bl_client_ligne",
        _avec_longueur_piece(
            {
                "id": ligne_id,
                "bl_client_id": bl_id,
                "lot_id": lot_id,
                "commande_ligne_id": cmd["commande_ligne_id"],
                "type": type_,
                "quantite": quantite,
                "poids_facturable_kg": poids,
            },
            longueur_piece,
        ),
    )
    return ligne_id


def mouvement_livraison(
    conn, ids, lot_id, bl_ligne_id, quantite, *, poids, longueur_piece=None
) -> str:
    """Sortie physique STOCK_GMC -> LIVRE par le Stock Service."""
    options = {} if longueur_piece is None else {PARAMETRE_LONGUEUR_PIECE: longueur_piece}
    with connexion.transaction(conn):
        return stock_service.enregistrer_mouvement(
            conn,
            lot_id=lot_id,
            type_mouvement="SORTIE_LIVRAISON_CLIENT",
            quantite=quantite,
            poids_kg=poids,
            emplacement_source=STOCK,
            emplacement_destination=LIVRE,
            utilisateur_id=ids["utilisateur"],
            document_source_type="bl_client_ligne",
            document_source_id=bl_ligne_id,
            date_heure=_instant(),
            **options,
        )


def sortir(
    conn,
    ids,
    lot_id,
    cmd,
    affectation_id,
    quantite,
    *,
    poids,
    longueur_piece=None,
    type_="INITIALE",
) -> str:
    """Livraison complète d'une affectation : BL client, sortie, clôture du lien."""
    bl_ligne_id = ligne_bl_client(
        conn, lot_id, cmd, quantite, poids=poids, longueur_piece=longueur_piece, type_=type_
    )
    mouvement_id = mouvement_livraison(
        conn, ids, lot_id, bl_ligne_id, quantite, poids=poids, longueur_piece=longueur_piece
    )
    conn.execute(
        "UPDATE affectation_stock SET mouvement_physique_id = ? WHERE id = ?",
        (mouvement_id, affectation_id),
    )
    conn.commit()
    if type_ == "SUPPLEMENT":
        valorisation.reconstruire_cmp(conn)  # un supplément se valorise au CMP
    return mouvement_id


def vendre(conn, ids, lot_id, *, quantite, longueur, poids, finition="NOIR", article=None) -> str:
    """Commande + affectation + livraison de `quantite` pièces de `longueur` m,
    prises sur le lot. La longueur de la pièce n'est précisée que si elle
    diffère de celle du lot (pièces de 6 m prises sur un lot de 12 m).
    Renvoie l'identifiant du mouvement de sortie."""
    longueur_lot = conn.execute("SELECT longueur_m FROM lot WHERE id = ?", (lot_id,)).fetchone()[0]
    longueur_piece = None if longueur == longueur_lot else longueur
    cmd = creer_ligne(
        conn, ids, quantite=quantite, longueur=longueur, finition=finition, article=article
    )
    affectation_id = affecter_pieces(
        conn, ids, lot_id, cmd, quantite, poids=poids, longueur_piece=longueur_piece
    )
    return sortir(
        conn, ids, lot_id, cmd, affectation_id, quantite, poids=poids, longueur_piece=longueur_piece
    )


def sortie_directe(ids, lot_id, *, quantite, poids, longueur_piece=None) -> dict:
    """Ligne de registre STOCK_GMC -> LIVRE écrite sans passer par le service :
    sert à vérifier que la base elle-même refuse une sortie impossible."""
    return _avec_longueur_piece(
        {
            "id": nid(),
            "lot_id": lot_id,
            "type": "SORTIE_LIVRAISON_CLIENT",
            "quantite": quantite,
            "poids_kg": poids,
            "emplacement_source": STOCK,
            "emplacement_destination": LIVRE,
            "document_source_type": "bl_client_ligne",
            "document_source_id": nid(),
            "date_heure": _instant(),
            "utilisateur_id": ids["utilisateur"],
        },
        longueur_piece,
    )


def dispo(conn, article_id, longueur, finition="NOIR") -> int:
    """Quantité disponible à la vente pour (article, finition, longueur)."""
    return stock_service.disponibilite(conn, article_id, finition, longueur)["disponible"]


def reste_gmc(conn, lot_id) -> int:
    return stock_service.soldes_lot(conn, lot_id).get(STOCK, {"quantite": 0})["quantite"]


def cout(conn, mouvement_id, lot_id) -> int:
    """Coût total attribué à une sortie, en millimes."""
    return valorisation.cout_sortie_total_minor(conn, mouvement_id, lot_id)


def compter(conn, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def donnee_source(conn, lot_id) -> tuple:
    """Donnée d'achat du lot : elle ne doit jamais changer."""
    return tuple(
        conn.execute(
            "SELECT longueur_m, quantite_initiale, poids_initial_kg, "
            "prix_unitaire_provisoire_minor, finition FROM lot WHERE id = ?",
            (lot_id,),
        ).fetchone()
    )


# ---------------------------------------------------------------------------
# Les quinze tests obligatoires (LG9)
# ---------------------------------------------------------------------------


def test_t01_une_barre_de_12m_sert_une_commande_de_12m(conn, ids):
    """T01 — 1 × 12 m, commande 1 × 12 m : accepté, reste 0.
    Réussit déjà aujourd'hui et doit continuer à réussir."""
    lot_id = creer_lot(conn, ids)
    cmd = creer_ligne(conn, ids, quantite=1, longueur=12.0)
    assert dispo(conn, ids["article"], 12.0) == 1

    verifier_affectable(conn, lot_id, 1)
    affectation_id = affecter_pieces(conn, ids, lot_id, cmd, 1, poids=POIDS_BARRE_KG)
    assert dispo(conn, ids["article"], 12.0) == 0

    mouvement_id = sortir(conn, ids, lot_id, cmd, affectation_id, 1, poids=POIDS_BARRE_KG)
    assert reste_gmc(conn, lot_id) == 0
    assert cout(conn, mouvement_id, lot_id) == tnd(100.0)  # la barre entière


def _une_barre_vendue_en_deux_pieces_de_6m(conn, ids, finition: str) -> None:
    lot_id = creer_lot(conn, ids, finition=finition)
    cmd = creer_ligne(conn, ids, quantite=2, longueur=6.0, finition=finition)
    # 1 barre de 12 m = 2 pièces de 6 m disponibles (LG1).
    assert dispo(conn, ids["article"], 6.0, finition) == 2

    verifier_affectable(conn, lot_id, 2, longueur_piece=6.0)
    affectation_id = affecter_pieces(
        conn, ids, lot_id, cmd, 2, poids=POIDS_BARRE_KG, longueur_piece=6.0
    )
    assert dispo(conn, ids["article"], 6.0, finition) == 0
    assert dispo(conn, ids["article"], 12.0, finition) == 0

    mouvement_id = sortir(
        conn, ids, lot_id, cmd, affectation_id, 2, poids=POIDS_BARRE_KG, longueur_piece=6.0
    )
    assert reste_gmc(conn, lot_id) == 0
    assert lecture_physique(conn, lot_id)[:2] == (0, 0)
    assert cout(conn, mouvement_id, lot_id) == tnd(100.0)  # 2 × 50 = la barre entière


@ATTEND_CODE
def test_t02_une_barre_de_12m_sert_deux_pieces_de_6m(conn, ids):
    """T02 — 1 × 12 m, commande 2 × 6 m : accepté, reste 0."""
    _une_barre_vendue_en_deux_pieces_de_6m(conn, ids, "NOIR")


@ATTEND_CODE
def test_t03_vente_d_une_piece_de_6m_laisse_un_reliquat_de_6m(conn, ids):
    """T03 — 1 × 12 m, commande 1 × 6 m : accepté ; reliquat 1 × 6 m ;
    disponible 6 m = 1 ; disponible 12 m = 0 (LG4)."""
    lot_id = creer_lot(conn, ids)
    cmd = creer_ligne(conn, ids, quantite=1, longueur=6.0)
    assert dispo(conn, ids["article"], 6.0) == 2
    assert dispo(conn, ids["article"], 12.0) == 1

    affectation_id = affecter_pieces(conn, ids, lot_id, cmd, 1, poids=21.0, longueur_piece=6.0)
    # La barre est entamée dès l'affectation : plus vendable comme 12 m.
    assert dispo(conn, ids["article"], 6.0) == 1
    assert dispo(conn, ids["article"], 12.0) == 0

    mouvement_id = sortir(conn, ids, lot_id, cmd, affectation_id, 1, poids=21.0, longueur_piece=6.0)
    lecture = lecture_physique(conn, lot_id)
    assert (lecture.barres, lecture.pieces_6m) == (0, 1)
    assert lecture.poids_kg == pytest.approx(21.0)
    assert lecture.valeur_minor == tnd(50.0)
    assert dispo(conn, ids["article"], 6.0) == 1
    assert dispo(conn, ids["article"], 12.0) == 0
    assert cout(conn, mouvement_id, lot_id) == tnd(50.0)  # la moitié de la barre (LG5)


@ATTEND_CODE
def test_t04_le_reliquat_de_6m_sert_une_commande_de_6m(conn, ids):
    """T04 — reliquat 1 × 6 m, commande 1 × 6 m : accepté, reste 0."""
    lot_id = creer_lot(conn, ids)
    vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)
    assert lecture_physique(conn, lot_id)[:2] == (0, 1)

    mouvement_id = vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)
    assert reste_gmc(conn, lot_id) == 0
    assert lecture_physique(conn, lot_id)[:2] == (0, 0)
    assert dispo(conn, ids["article"], 6.0) == 0
    assert cout(conn, mouvement_id, lot_id) == tnd(50.0)


@ATTEND_CODE
def test_t05_trois_pieces_de_6m_sur_une_seule_barre_refuse(conn, ids):
    """T05 — 1 × 12 m, commande 3 × 6 m : refusé (3 pièces demandées, 2 disponibles)."""
    lot_id = creer_lot(conn, ids)
    cmd = creer_ligne(conn, ids, quantite=3, longueur=6.0)
    assert dispo(conn, ids["article"], 6.0) == 2

    with pytest.raises(ErreurDisponibiliteInsuffisante):
        verifier_affectable(conn, lot_id, 3, longueur_piece=6.0)
    with pytest.raises(sqlite3.IntegrityError):
        affecter_pieces(conn, ids, lot_id, cmd, 3, poids=63.0, longueur_piece=6.0)
    # Même refus dans le registre : 3 pièces de 6 m ne sortent pas d'une barre.
    with pytest.raises(sqlite3.IntegrityError):
        _inserer(
            conn,
            "mouvement_stock",
            sortie_directe(ids, lot_id, quantite=3, poids=63.0, longueur_piece=6.0),
        )

    # Rien n'a été écrit, la barre est intacte.
    assert compter(conn, "affectation_stock") == 0
    assert compter(conn, "mouvement_stock") == 1  # seule l'entrée du lot
    assert dispo(conn, ids["article"], 6.0) == 2
    assert dispo(conn, ids["article"], 12.0) == 1


@ATTEND_MIGRATION
def test_t06_deux_barres_de_6m_ne_servent_pas_une_commande_de_12m(conn, ids):
    """T06 — 2 × 6 m, commande 1 × 12 m : refusé (LG6)."""
    lot_id = creer_lot(conn, ids, barres=2, longueur=6.0, poids_piece=21.0, prix=tnd(50.0))
    cmd = creer_ligne(conn, ids, quantite=1, longueur=12.0)
    assert dispo(conn, ids["article"], 12.0) == 0

    with pytest.raises(sqlite3.IntegrityError):
        affecter_pieces(conn, ids, lot_id, cmd, 1, poids=21.0)
    with pytest.raises(sqlite3.IntegrityError):
        affecter_pieces(conn, ids, lot_id, cmd, 2, poids=42.0)

    assert compter(conn, "affectation_stock") == 0
    assert dispo(conn, ids["article"], 6.0) == 2  # les deux barres de 6 m restent libres


@ATTEND_MIGRATION
def test_t07_une_barre_de_6m_ne_sert_pas_une_commande_de_12m(conn, ids):
    """T07 — 1 × 6 m, commande 1 × 12 m : refusé (LG6, LG7)."""
    lot_id = creer_lot(conn, ids, barres=1, longueur=6.0, poids_piece=21.0, prix=tnd(50.0))
    cmd = creer_ligne(conn, ids, quantite=1, longueur=12.0)
    assert dispo(conn, ids["article"], 12.0) == 0

    with pytest.raises(sqlite3.IntegrityError):
        affecter_pieces(conn, ids, lot_id, cmd, 1, poids=21.0)
    assert compter(conn, "affectation_stock") == 0


@ATTEND_CODE
def test_t08_noir_12m_ne_sert_pas_directement_une_ligne_galva_6m(conn, ids):
    """T08 — NOIR 12 m, ligne GALVA 6 m : refusé comme simple compatibilité
    (LG2). Changer de finition reste une transformation."""
    lot_12m = creer_lot(conn, ids, finition="NOIR")
    cmd = creer_ligne(conn, ids, quantite=2, longueur=6.0, finition="GALVA")
    assert dispo(conn, ids["article"], 6.0, "GALVA") == 0

    with pytest.raises(sqlite3.IntegrityError):
        affecter_pieces(conn, ids, lot_12m, cmd, 2, poids=POIDS_BARRE_KG, longueur_piece=6.0)

    # Même refus sans question de longueur : NOIR 6 m sur une ligne GALVA 6 m.
    lot_6m = creer_lot(conn, ids, barres=2, longueur=6.0, poids_piece=21.0, prix=tnd(50.0))
    with pytest.raises(sqlite3.IntegrityError):
        affecter_pieces(conn, ids, lot_6m, cmd, 2, poids=42.0)
    assert compter(conn, "affectation_stock") == 0

    # En NOIR, la disponibilité en 6 m additionne les vraies barres de 6 m et
    # les pièces que la barre de 12 m peut fournir : 2 + 2 = 4.
    assert dispo(conn, ids["article"], 6.0, "NOIR") == 4
    assert dispo(conn, ids["article"], 12.0, "NOIR") == 1


@ATTEND_CODE
def test_t09_galva_12m_sert_une_ligne_galva_6m(conn, ids):
    """T09 — GALVA 12 m, ligne GALVA 6 m : accepté (finition identique, LG2)."""
    _une_barre_vendue_en_deux_pieces_de_6m(conn, ids, "GALVA")


@ATTEND_CODE
def test_t10_gpp_12m_sert_une_ligne_gpp_6m(conn, ids):
    """T10 — GPP 12 m, ligne GPP 6 m : accepté (finition identique, LG2)."""
    _une_barre_vendue_en_deux_pieces_de_6m(conn, ids, "GPP")


@ATTEND_CODE
@pytest.mark.parametrize(
    "unite, prix, cout_barre",
    [
        ("UNITE", tnd(100.0), tnd(100.0)),  # 100 DT la pièce -> barre 100 DT, moitié 50
        ("ML", tnd(8.0), tnd(96.0)),  # 8 DT le mètre × 12 m = 96 DT, moitié 48
        ("KG", tnd(2.5), tnd(105.0)),  # 2,5 DT le kg × 42 kg = 105 DT, moitié 52,5
    ],
)
def test_t11_le_cout_suit_la_longueur(conn, ids, unite, prix, cout_barre):
    """T11 — coût 12 m / 6 m : une barre vendue de trois façons (v10 §G.2),
    pour un article valorisé à la pièce, au mètre ou au kilo."""
    article = nouvel_article(conn, ids, unite)
    moitie = cout_barre // 2

    # Barre A, vendue 1 × 12 m : la barre entière.
    barre_a = creer_lot(conn, ids, prix=prix, article=article)
    sortie = vendre(conn, ids, barre_a, quantite=1, longueur=12.0, poids=42.0, article=article)
    assert cout(conn, sortie, barre_a) == cout_barre

    # Barre B, vendue en deux fois 1 × 6 m : moitié + moitié.
    barre_b = creer_lot(conn, ids, prix=prix, article=article)
    premiere = vendre(conn, ids, barre_b, quantite=1, longueur=6.0, poids=21.0, article=article)
    seconde = vendre(conn, ids, barre_b, quantite=1, longueur=6.0, poids=21.0, article=article)
    assert (cout(conn, premiere, barre_b), cout(conn, seconde, barre_b)) == (moitie, moitie)

    # Barre C, vendue 1 × 6 m : la moitié sort, l'autre moitié reste dans le lot.
    barre_c = creer_lot(conn, ids, prix=prix, article=article)
    sortie = vendre(conn, ids, barre_c, quantite=1, longueur=6.0, poids=21.0, article=article)
    assert cout(conn, sortie, barre_c) == moitie
    assert lecture_physique(conn, barre_c).valeur_minor == moitie


@ATTEND_CODE
def test_t12_valeur_du_reliquat_calculee_par_difference(conn, ids):
    """T12 — reliquat et sa valeur (V10-3). Barre à 100,001 DT : chaque moitié
    vaut 50,000 5 DT. Arrondies séparément, elles feraient 50,001 + 50,001 =
    100,002 : un millime créé. Attendu : 50,001 + 50,000 = 100,001."""
    lot_id = creer_lot(conn, ids, prix=100_001)

    premiere = vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)
    assert cout(conn, premiere, lot_id) == 50_001  # 50 000,5 arrondi vers le haut
    lecture = lecture_physique(conn, lot_id)
    assert (lecture.barres, lecture.pieces_6m) == (0, 1)
    assert lecture.valeur_minor == 50_000  # 100 001 − 50 001 : par différence

    seconde = vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)
    assert cout(conn, seconde, lot_id) == 50_000  # la dernière pièce emporte le reste
    assert cout(conn, premiere, lot_id) + cout(conn, seconde, lot_id) == 100_001
    assert lecture_physique(conn, lot_id).valeur_minor == 0


def _photo(conn, article_id, lot_id) -> tuple:
    pools = [
        tuple(ligne)
        for ligne in conn.execute(
            "SELECT finition, longueur_m, unite_valorisation, quantite_valorisation, "
            "valeur_totale_minor, cmp_unitaire_minor FROM cmp_stock_general "
            "WHERE article_id = ? ORDER BY finition, longueur_m",
            (article_id,),
        )
    ]
    return (
        pools,
        lecture_physique(conn, lot_id),
        dispo(conn, article_id, 6.0),
        dispo(conn, article_id, 12.0),
    )


@ATTEND_CODE
def test_t13_reconstruction_identique_apres_consommation_partielle(conn, ids):
    """T13 — après la vente de 1 × 6 m, deux reconstructions successives
    donnent les mêmes soldes et les mêmes valeurs. Aucun pool 6 m n'est créé
    par l'équivalence : le reliquat reste dans le pool 12 m (LG5)."""
    lot_id = creer_lot(conn, ids, barres=3)  # 3 barres, 126 kg, 300 DT
    vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)

    valorisation.reconstruire_cmp(conn)
    premiere = _photo(conn, ids["article"], lot_id)
    valorisation.reconstruire_cmp(conn)
    seconde = _photo(conn, ids["article"], lot_id)
    assert premiere == seconde

    pool = valorisation.cmp_actuel(conn, ids["article"], "NOIR", 12.0)
    # Article valorisé à la pièce : le pool compte en barres, une pièce de 6 m = 0,5.
    assert pool["quantite_valorisation"] == pytest.approx(2.5)  # 2 barres et demie
    assert pool["valeur_totale_minor"] == tnd(250.0)  # 300 − 50
    assert pool["cmp_unitaire_minor"] == tnd(100.0)  # inchangé : 250 ÷ 2,5
    assert valorisation.cmp_actuel(conn, ids["article"], "NOIR", 6.0) is None
    assert lecture_physique(conn, lot_id)[:2] == (2, 1)


@ATTEND_CODE
def test_t14_aucun_double_comptage(conn, ids):
    """T14 — coûts sortis + valeur restante = coût du lot ; les disponibilités
    6 m et 12 m ne s'additionnent pas ; conservation vérifiée."""
    lot_id = creer_lot(conn, ids, barres=3)  # 3 barres, 126 kg, 300 DT
    piece = vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)
    barre = vendre(conn, ids, lot_id, quantite=1, longueur=12.0, poids=42.0)

    lecture = lecture_physique(conn, lot_id)
    assert (lecture.barres, lecture.pieces_6m) == (1, 1)  # 1 barre + 1 pièce de 6 m
    assert lecture.poids_kg == pytest.approx(63.0)  # 126 − 21 − 42
    # 50 (pièce de 6 m) + 100 (barre) + 150 (reste) = 300 DT, ni plus ni moins.
    assert cout(conn, piece, lot_id) == tnd(50.0)
    assert cout(conn, barre, lot_id) == tnd(100.0)
    assert lecture.valeur_minor == tnd(150.0)
    assert cout(conn, piece, lot_id) + cout(conn, barre, lot_id) + lecture.valeur_minor == tnd(
        300.0
    )

    # La même barre libre compte pour 1 en 12 m et pour 2 en 6 m : deux
    # réponses à deux questions, jamais un total de 4.
    assert dispo(conn, ids["article"], 12.0) == 1
    assert dispo(conn, ids["article"], 6.0) == 3  # 1 reliquat + 2 par équivalence

    assert stock_service.verifier_conservation(conn)["equilibre"] is True


@ATTEND_CODE
def test_t15_tracabilite_lot_source_sortie_reliquat(conn, ids):
    """T15 — affectation, BL client, mouvement et reliquat portent le même
    lot. Aucun lot nouveau, aucun mouvement de conversion ou de
    transformation (LG1, LG4)."""
    lot_id = creer_lot(conn, ids)
    avant = donnee_source(conn, lot_id)
    sortie = vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)

    def lots_de(table: str) -> set:
        return {ligne[0] for ligne in conn.execute(f"SELECT DISTINCT lot_id FROM {table}")}

    def controler() -> None:
        assert lots_de("affectation_stock") == {lot_id}
        assert lots_de("bl_client_ligne") == {lot_id}
        assert lots_de("mouvement_stock") == {lot_id}
        assert compter(conn, "lot") == 1  # aucun lot « enfant »
        types = {ligne[0] for ligne in conn.execute("SELECT DISTINCT type FROM mouvement_stock")}
        assert types == {"ENTREE_RECEPTION_FOURNISSEUR", "SORTIE_LIVRAISON_CLIENT"}
        assert donnee_source(conn, lot_id) == avant  # le lot reste un lot de 12 m

    controler()
    assert lecture_physique(conn, lot_id)[:2] == (0, 1)  # le reliquat est dans le lot source

    # Chaque écriture dit que la pièce fait 6 m.
    for table, condition, valeur in (
        ("mouvement_stock", "id = ?", sortie),
        ("affectation_stock", "mouvement_physique_id = ?", sortie),
        ("bl_client_ligne", "lot_id = ?", lot_id),
    ):
        longueur = conn.execute(
            f"SELECT {COLONNE_LONGUEUR_PIECE} FROM {table} WHERE {condition}", (valeur,)
        ).fetchone()[0]
        assert longueur == 6.0

    vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)  # vente du reliquat
    controler()
    assert compter(conn, "mouvement_stock") == 3  # 1 entrée + 2 sorties, rien d'autre


# ---------------------------------------------------------------------------
# Compléments de l'analyse v10 (§O.2), sauf T26 (V10-8)
# ---------------------------------------------------------------------------


@ATTEND_MIGRATION
@pytest.mark.parametrize(
    "longueur_lot, longueur_piece",
    [(12.0, 4.0), (12.0, 3.0), (6.0, 3.0)],
)
def test_t16_aucune_autre_conversion_de_longueur(conn, ids, longueur_lot, longueur_piece):
    """T16 — 12 m → 4 m, 12 m → 3 m, 6 m → 3 m : refusés. Une seule
    conversion est validée pour le moment : 12 m → 2 × 6 m (LG3)."""
    poids_lot = POIDS_BARRE_KG * longueur_lot / 12.0
    lot_id = creer_lot(conn, ids, longueur=longueur_lot, poids_piece=poids_lot)
    cmd = creer_ligne(conn, ids, quantite=1, longueur=longueur_piece)
    assert dispo(conn, ids["article"], longueur_piece) == 0

    with pytest.raises(sqlite3.IntegrityError):
        affecter_pieces(
            conn,
            ids,
            lot_id,
            cmd,
            1,
            poids=poids_lot * longueur_piece / longueur_lot,
            longueur_piece=longueur_piece,
        )
    assert compter(conn, "affectation_stock") == 0

    # Même refus dans le registre : aucune pièce de cette longueur ne sort du lot.
    with pytest.raises(sqlite3.IntegrityError):
        _inserer(
            conn,
            "mouvement_stock",
            sortie_directe(
                ids,
                lot_id,
                quantite=1,
                poids=poids_lot * longueur_piece / longueur_lot,
                longueur_piece=longueur_piece,
            ),
        )
    assert compter(conn, "mouvement_stock") == 1  # seule l'entrée du lot


@ATTEND_CODE
def test_t17_deux_reliquats_de_deux_lots_ne_font_pas_une_barre(conn, ids):
    """T17 — deux reliquats de 6 m dans deux lots, commande 1 × 12 m : refusé (LG6)."""
    lot_a = creer_lot(conn, ids)
    lot_b = creer_lot(conn, ids)
    vendre(conn, ids, lot_a, quantite=1, longueur=6.0, poids=21.0)
    vendre(conn, ids, lot_b, quantite=1, longueur=6.0, poids=21.0)

    assert dispo(conn, ids["article"], 6.0) == 2  # deux pièces de 6 m
    assert dispo(conn, ids["article"], 12.0) == 0  # mais aucune barre de 12 m

    cmd = creer_ligne(conn, ids, quantite=1, longueur=12.0)
    for lot_id in (lot_a, lot_b):
        with pytest.raises(sqlite3.IntegrityError):
            affecter_pieces(conn, ids, lot_id, cmd, 1, poids=POIDS_BARRE_KG)
        # Même refus dans le registre : un reliquat de 6 m ne sort pas comme 12 m.
        with pytest.raises(sqlite3.IntegrityError):
            _inserer(conn, "mouvement_stock", sortie_directe(ids, lot_id, quantite=1, poids=21.0))
    assert dispo(conn, ids["article"], 6.0) == 2
    assert compter(conn, "mouvement_stock") == 4  # 2 entrées + 2 sorties de 6 m


@ATTEND_CODE
def test_t18_plafond_d_affectation_compte_en_pieces_de_6m(conn, ids):
    """T18 — lot de 2 barres : 1 × 6 m et 1 × 12 m affectés, puis 1 × 12 m :
    la troisième affectation est refusée ; il reste 1 pièce de 6 m libre."""
    lot_id = creer_lot(conn, ids, barres=2)
    ligne_a = creer_ligne(conn, ids, quantite=1, longueur=6.0)
    ligne_b = creer_ligne(conn, ids, quantite=1, longueur=12.0)
    ligne_c = creer_ligne(conn, ids, quantite=1, longueur=12.0)

    affecter_pieces(conn, ids, lot_id, ligne_a, 1, poids=21.0, longueur_piece=6.0)
    affecter_pieces(conn, ids, lot_id, ligne_b, 1, poids=POIDS_BARRE_KG)
    with pytest.raises(sqlite3.IntegrityError):
        affecter_pieces(conn, ids, lot_id, ligne_c, 1, poids=POIDS_BARRE_KG)

    assert compter(conn, "affectation_stock") == 2
    assert dispo(conn, ids["article"], 6.0) == 1  # 4 − 1 − 2 = 1 pièce de 6 m
    assert dispo(conn, ids["article"], 12.0) == 0


@ATTEND_CODE
def test_t19_supplement_de_6m_valorise_au_cmp_du_pool_12m(conn, ids):
    """T19 — supplément de 6 m sur un pool 12 m (v10 §H). Deux barres à 100 et
    120 DT : pool 220 DT, CMP 110 DT la barre. Un supplément de 1 × 6 m
    retire une demi-barre : 220 × 0,5 ÷ 2 = 55 DT. Il reste 165 DT pour
    1,5 barre : le CMP reste 110 DT. Aucun pool 6 m n'est créé."""
    article = nouvel_article(conn, ids, "UNITE")
    lot_a = creer_lot(conn, ids, prix=tnd(100.0), article=article)
    creer_lot(conn, ids, prix=tnd(120.0), article=article)
    cmd = creer_ligne(conn, ids, quantite=1, longueur=6.0, article=article)

    affectation_id = affecter_pieces(
        conn,
        ids,
        lot_a,
        cmd,
        1,
        poids=21.0,
        longueur_piece=6.0,
        type_="SUPPLEMENT",
        motif="Supplément demandé par le client",
    )
    sortie = sortir(
        conn,
        ids,
        lot_a,
        cmd,
        affectation_id,
        1,
        poids=21.0,
        longueur_piece=6.0,
        type_="SUPPLEMENT",
    )

    assert cout(conn, sortie, lot_a) == tnd(55.0)
    pool = valorisation.cmp_actuel(conn, article, "NOIR", 12.0)
    assert pool["valeur_totale_minor"] == tnd(165.0)
    assert pool["quantite_valorisation"] == pytest.approx(1.5)
    assert pool["cmp_unitaire_minor"] == tnd(110.0)
    assert valorisation.cmp_actuel(conn, article, "NOIR", 6.0) is None


@ATTEND_MIGRATION
def test_t20_la_base_refuse_un_lot_6m_sur_une_ligne_12m(conn, ids):
    """T20 — écriture directe en base, comme la faisait un programme d'avant la
    règle : un lot de 6 m sur une ligne de 12 m est refusé par la base
    elle-même (cas 4 de l'audit du 02/10/2026)."""
    lot = creer_lot_reception(
        conn,
        ids,
        quantite=2,
        poids_kg=42.0,
        prix_provisoire_minor=tnd(50.0),
        finition="NOIR",
        longueur_m=6.0,
    )
    cmd = creer_ligne(conn, ids, quantite=1, longueur=12.0)
    with pytest.raises(sqlite3.IntegrityError):
        affecter(conn, ids, lot["lot_id"], cmd["commande_ligne_id"], "INITIALE", 1, 21.0)
    conn.rollback()
    assert compter(conn, "affectation_stock") == 0


@ATTEND_MIGRATION
def test_t21_un_lot_de_12m_n_entre_jamais_en_pieces_de_6m(conn, ids):
    """T21 — l'entrée d'origine d'un lot de 12 m se fait en barres de 12 m.
    La saisir en pièces de 6 m est refusé : le lot acheté reste un lot de
    12 m, rien n'est « converti » à l'entrée."""
    bl_id, ligne_id, lot_id = nid(), nid(), nid()
    _inserer(
        conn,
        "bl_fournisseur",
        {
            "id": bl_id,
            "numero": f"BLF-2026-{nid()[:8]}",
            "numero_origine_fournisseur": "ORIG-T21",
            "fournisseur_id": ids["fournisseur"],
            "date": "2026-01-05",
            "statut": "VALIDE",
        },
    )
    achat = {
        "article_id": ids["article"],
        "finition": "NOIR",
        "longueur_m": 12.0,
        "prix_unitaire_provisoire_minor": PRIX_BARRE,
        "devise": "TND",
    }
    _inserer(
        conn,
        "bl_fournisseur_ligne",
        {"id": ligne_id, "bl_fournisseur_id": bl_id, "quantite": 1, "poids_kg": 42.0, **achat},
    )
    _inserer(
        conn,
        "lot",
        {
            "id": lot_id,
            "bl_fournisseur_ligne_id": ligne_id,
            "quantite_initiale": 1,
            "poids_initial_kg": 42.0,
            **achat,
        },
    )

    with pytest.raises(sqlite3.IntegrityError):
        _inserer(
            conn,
            "mouvement_stock",
            {
                "id": nid(),
                "lot_id": lot_id,
                "type": "ENTREE_RECEPTION_FOURNISSEUR",
                "quantite": 2,
                "poids_kg": 42.0,
                "emplacement_destination": STOCK,
                "document_source_type": "bl_fournisseur_ligne",
                "document_source_id": ligne_id,
                "date_heure": "2026-01-05T08:00:00.000",
                "utilisateur_id": ids["utilisateur"],
                COLONNE_LONGUEUR_PIECE: 6.0,
            },
        )
    assert compter(conn, "mouvement_stock") == 0


def test_t22_un_lot_de_6m_ordinaire_se_comporte_comme_aujourd_hui(conn, ids):
    """T22 — lot réellement acheté en 6 m : rien ne change. Réussit déjà
    aujourd'hui et doit continuer à réussir, sans préciser de longueur de
    pièce."""
    lot_id = creer_lot(conn, ids, barres=10, longueur=6.0, poids_piece=21.0, prix=tnd(30.0))
    cmd = creer_ligne(conn, ids, quantite=4, longueur=6.0)
    assert dispo(conn, ids["article"], 6.0) == 10
    assert dispo(conn, ids["article"], 12.0) == 0

    verifier_affectable(conn, lot_id, 4)
    affectation_id = affecter_pieces(conn, ids, lot_id, cmd, 4, poids=84.0)
    assert dispo(conn, ids["article"], 6.0) == 6

    mouvement_id = sortir(conn, ids, lot_id, cmd, affectation_id, 4, poids=84.0)
    assert reste_gmc(conn, lot_id) == 6
    assert dispo(conn, ids["article"], 6.0) == 6
    assert cout(conn, mouvement_id, lot_id) == tnd(120.0)  # 4 × 30 DT
    assert stock_service.verifier_conservation(conn)["equilibre"] is True


@ATTEND_CODE
def test_t23_le_reliquat_sort_avant_d_entamer_une_nouvelle_barre(conn, ids):
    """T23 — exemple de Mohamed (V10-1) : stock 2 × 12 m + 1 × 6 m dans un lot,
    demande 1 × 6 m : la pièce de 6 m sort, les 2 barres restent intactes."""
    lot_id = creer_lot(conn, ids, barres=3)
    vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)
    assert lecture_physique(conn, lot_id)[:2] == (2, 1)  # 2 barres + 1 pièce de 6 m
    assert dispo(conn, ids["article"], 12.0) == 2
    assert dispo(conn, ids["article"], 6.0) == 5

    vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=21.0)
    assert lecture_physique(conn, lot_id)[:2] == (2, 0)  # les 2 barres sont intactes
    assert dispo(conn, ids["article"], 12.0) == 2
    assert dispo(conn, ids["article"], 6.0) == 4


@ATTEND_CODE
def test_t24_donnee_du_lot_inchangee_et_lecture_physique(conn, ids):
    """T24 — exemple complet de la v10 (§T.4) : 3 barres, 360 kg, 300 TND,
    vente de 1 × 6 m. La donnée d'achat du lot reste identique ; le stock
    physique se lit « 2 barres de 12 m + 1 pièce de 6 m », 300 kg, 250 TND ;
    jamais « 5 × 6 m » comme stock physique (V10-4)."""
    lot_id = creer_lot(conn, ids, barres=3, poids_piece=120.0)
    avant = donnee_source(conn, lot_id)
    assert avant == (12.0, 3, 360.0, tnd(100.0), "NOIR")
    assert dispo(conn, ids["article"], 12.0) == 3
    assert dispo(conn, ids["article"], 6.0) == 6  # par équivalence

    vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=60.0)

    assert donnee_source(conn, lot_id) == avant
    lecture = lecture_physique(conn, lot_id)
    assert (lecture.barres, lecture.pieces_6m) == (2, 1)
    assert lecture.poids_kg == pytest.approx(300.0)
    assert lecture.valeur_minor == tnd(250.0)

    # Disponibilité commerciale : une équivalence, pas un stock physique.
    assert dispo(conn, ids["article"], 12.0) == 2
    assert dispo(conn, ids["article"], 6.0) == 5  # 1 reliquat + 4 par équivalence


@ATTEND_CODE
def test_t25_une_piece_de_6m_pese_la_moitie_de_la_barre(conn, ids):
    """T25 — poids (V10-2) : barre de 120 kg, sortie de 1 × 6 m : 60 kg
    sortis ; le poids fournisseur du lot ne change pas. La façon d'obtenir
    ce poids (calculé par le système, ou saisi puis contrôlé) est un choix
    technique du codage : ce test ne la fixe pas."""
    lot_id = creer_lot(conn, ids, poids_piece=120.0)
    mouvement_id = vendre(conn, ids, lot_id, quantite=1, longueur=6.0, poids=60.0)

    poids_sorti = conn.execute(
        "SELECT poids_kg FROM mouvement_stock WHERE id = ?", (mouvement_id,)
    ).fetchone()[0]
    assert poids_sorti == pytest.approx(60.0)
    assert donnee_source(conn, lot_id)[2] == 120.0  # poids fournisseur inchangé
    lecture = lecture_physique(conn, lot_id)
    assert (lecture.barres, lecture.pieces_6m) == (0, 1)
    assert lecture.poids_kg == pytest.approx(60.0)
