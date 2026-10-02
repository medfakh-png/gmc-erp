"""
Repository du stock physique (Phase 5.5).

Accès SQL structuré aux lots, au registre `mouvement_stock` (append-only,
seule source de vérité du stock), aux soldes dérivés de ce registre, aux
affectations/réservations (lecture seule, pour la disponibilité) et aux
lignes de documents qui déclenchent un mouvement (lecture seule, pour
vérifier le document source).

Aucune règle métier ici : les contrôles (couple type/emplacements,
doublons, soldes, motifs...) sont faits par `services/stock_service.py`.
Toutes les lectures renvoient des dictionnaires, indépendamment du
`row_factory` de la connexion fournie.
"""

from __future__ import annotations

import sqlite3
import typing

from repositories.base import des_dicts, executer, un_dict, un_ou_aucun

TYPES_ENTREE_ORIGINE = (
    "ENTREE_RECEPTION_FOURNISSEUR",
    "ENTREE_RETOUR_TRANSFORMATION",
    "ENTREE_INVENTAIRE_INITIAL",
)


# ---------------------------------------------------------------------------
# Lots
# ---------------------------------------------------------------------------


def obtenir_lot(conn: sqlite3.Connection, lot_id: str) -> typing.Optional[dict]:
    return un_dict(
        conn,
        """
        SELECT id, article_id, bl_fournisseur_ligne_id, lot_parent_id, inventaire_initial_ligne_id,
               finition, longueur_m, quantite_initiale, poids_initial_kg,
               prix_unitaire_provisoire_minor, prix_unitaire_definitif_minor, devise, unite_prix,
               unite_prix_definitif, unite_valorisation_article, cree_le
        FROM lot WHERE id = ?
        """,
        (lot_id,),
    )


def inserer_lot(
    conn: sqlite3.Connection,
    *,
    id: str,
    article_id: str,
    finition: str,
    longueur_m: float,
    quantite_initiale: int,
    poids_initial_kg: float,
    prix_unitaire_provisoire_minor: int,
    prix_unitaire_definitif_minor: typing.Optional[int],
    devise: str,
    bl_fournisseur_ligne_id: typing.Optional[str] = None,
    lot_parent_id: typing.Optional[str] = None,
    inventaire_initial_ligne_id: typing.Optional[str] = None,
    unite_prix: typing.Optional[str] = None,
    unite_prix_definitif: typing.Optional[str] = None,
) -> None:
    """
    `unite_prix` : unité dans laquelle le prix provisoire a été saisi (KG,
    ML, UNITE, TONNE) ; `unite_prix_definitif` : unité du prix définitif
    (obligatoire s'il y a un prix définitif). La base vérifie qu'elles sont
    l'unité de valorisation de l'article ou, pour un article valorisé au
    poids, l'autre unité de masse (kg <-> tonne, migration 0020). Si
    `unite_prix` est omise, la base la fixe à l'unité de l'article (0019).
    L'unité de valorisation de l'article à la création est enregistrée par
    la base (`unite_valorisation_article`).
    """
    executer(
        conn,
        """
        INSERT INTO lot (id, article_id, bl_fournisseur_ligne_id, lot_parent_id,
                         inventaire_initial_ligne_id,
                         finition, longueur_m, quantite_initiale, poids_initial_kg,
                         prix_unitaire_provisoire_minor, prix_unitaire_definitif_minor, devise,
                         unite_prix, unite_prix_definitif)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id,
            article_id,
            bl_fournisseur_ligne_id,
            lot_parent_id,
            inventaire_initial_ligne_id,
            finition,
            longueur_m,
            quantite_initiale,
            poids_initial_kg,
            prix_unitaire_provisoire_minor,
            prix_unitaire_definitif_minor,
            devise,
            unite_prix,
            unite_prix_definitif,
        ),
    )


def devises_du_pool_en_stock_gmc(
    conn: sqlite3.Connection, article_id: str, finition: str, longueur_m: float
) -> set[str]:
    """Devises des lots de ce pool (article, finition, longueur) ayant déjà touché STOCK_GMC."""
    lignes = des_dicts(
        conn,
        """
        SELECT DISTINCT l.devise AS devise
        FROM lot l
        JOIN mouvement_stock m ON m.lot_id = l.id
        WHERE l.article_id = ? AND l.finition = ? AND l.longueur_m = ?
          AND (m.emplacement_source = 'STOCK_GMC' OR m.emplacement_destination = 'STOCK_GMC')
        """,
        (article_id, finition, longueur_m),
    )
    return {ligne["devise"] for ligne in lignes}


# ---------------------------------------------------------------------------
# Registre des mouvements (append-only)
# ---------------------------------------------------------------------------


def inserer_mouvement(
    conn: sqlite3.Connection,
    *,
    id: str,
    lot_id: str,
    type_mouvement: str,
    quantite: int,
    poids_kg: float,
    emplacement_source: typing.Optional[str],
    emplacement_destination: typing.Optional[str],
    document_source_type: str,
    document_source_id: str,
    utilisateur_id: str,
    motif: typing.Optional[str] = None,
    date_heure: typing.Optional[str] = None,
) -> None:
    """Simple INSERT — aucune transaction ouverte ni validée ici."""
    executer(
        conn,
        """
        INSERT INTO mouvement_stock
            (id, lot_id, type, quantite, poids_kg, emplacement_source, emplacement_destination,
             document_source_type, document_source_id, date_heure, utilisateur_id, motif)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,
                COALESCE(?, strftime('%Y-%m-%dT%H:%M:%f','now')), ?, ?)
        """,
        (
            id,
            lot_id,
            type_mouvement,
            quantite,
            poids_kg,
            emplacement_source,
            emplacement_destination,
            document_source_type,
            document_source_id,
            date_heure,
            utilisateur_id,
            motif,
        ),
    )


def obtenir_mouvement(conn: sqlite3.Connection, mouvement_id: str) -> typing.Optional[dict]:
    return un_dict(conn, "SELECT * FROM mouvement_stock WHERE id = ?", (mouvement_id,))


def entree_origine_du_lot(conn: sqlite3.Connection, lot_id: str) -> typing.Optional[dict]:
    """
    L'entrée d'origine déjà enregistrée pour ce lot (réception, retour de
    transformation ou inventaire initial de démarrage).
    """
    marqueurs = ", ".join("?" for _ in TYPES_ENTREE_ORIGINE)
    return un_dict(
        conn,
        f"SELECT * FROM mouvement_stock WHERE lot_id = ? AND type IN ({marqueurs})",
        (lot_id, *TYPES_ENTREE_ORIGINE),
    )


def mouvement_pour_document(
    conn: sqlite3.Connection,
    type_mouvement: str,
    document_source_type: str,
    document_source_id: str,
) -> typing.Optional[dict]:
    return un_dict(
        conn,
        """
        SELECT * FROM mouvement_stock
        WHERE type = ? AND document_source_type = ? AND document_source_id = ?
        """,
        (type_mouvement, document_source_type, document_source_id),
    )


def lister_mouvements(
    conn: sqlite3.Connection,
    *,
    lot_id: typing.Optional[str] = None,
    article_id: typing.Optional[str] = None,
    depuis: typing.Optional[str] = None,
    jusqu_au: typing.Optional[str] = None,
) -> list[dict]:
    """Mouvements dans l'ordre chronologique (puis ordre d'enregistrement)."""
    conditions: list[str] = []
    params: list[typing.Any] = []
    if lot_id is not None:
        conditions.append("m.lot_id = ?")
        params.append(lot_id)
    if article_id is not None:
        conditions.append("l.article_id = ?")
        params.append(article_id)
    if depuis is not None:
        conditions.append("m.date_heure >= ?")
        params.append(depuis)
    if jusqu_au is not None:
        conditions.append("m.date_heure <= ?")
        params.append(jusqu_au)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return des_dicts(
        conn,
        f"""
        SELECT m.*, l.article_id, l.finition, l.longueur_m
        FROM mouvement_stock m JOIN lot l ON l.id = m.lot_id
        {where}
        ORDER BY m.date_heure, m.rowid
        """,
        params,
    )


# ---------------------------------------------------------------------------
# Soldes (toujours dérivés du registre, jamais stockés)
# ---------------------------------------------------------------------------


def solde_lot_emplacement(
    conn: sqlite3.Connection, lot_id: str, emplacement: str, jusqu_au: typing.Optional[str] = None
) -> tuple[int, float]:
    """(pièces, poids kg) du lot à cet emplacement, dérivés du registre."""
    ligne = un_ou_aucun(
        conn,
        """
        SELECT
            COALESCE(SUM(CASE WHEN emplacement_destination = ? THEN quantite ELSE 0 END), 0)
          - COALESCE(SUM(CASE WHEN emplacement_source = ? THEN quantite ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN emplacement_destination = ? THEN poids_kg ELSE 0 END), 0)
          - COALESCE(SUM(CASE WHEN emplacement_source = ? THEN poids_kg ELSE 0 END), 0)
        FROM mouvement_stock
        WHERE lot_id = ? AND (? IS NULL OR date_heure <= ?)
        """,
        (emplacement, emplacement, emplacement, emplacement, lot_id, jusqu_au, jusqu_au),
    )
    if ligne is None:
        return 0, 0.0
    return int(ligne[0]), float(ligne[1])


def stock_par_lot_et_emplacement(
    conn: sqlite3.Connection,
    *,
    lot_id: typing.Optional[str] = None,
    emplacement: typing.Optional[str] = None,
    prefixe_emplacement: typing.Optional[str] = None,
    article_id: typing.Optional[str] = None,
    finition: typing.Optional[str] = None,
    longueur_m: typing.Optional[float] = None,
    jusqu_au: typing.Optional[str] = None,
    inclure_soldes_nuls: bool = False,
) -> list[dict]:
    """
    Soldes non nuls (en pièces) par lot et par emplacement, avec les
    caractéristiques de l'article. Dérivé exclusivement du registre ;
    `jusqu_au` permet de lire le stock à une date donnée.
    """
    conditions: list[str] = []
    params: list[typing.Any] = [jusqu_au, jusqu_au, jusqu_au, jusqu_au]
    if lot_id is not None:
        conditions.append("d.lot_id = ?")
        params.append(lot_id)
    if emplacement is not None:
        conditions.append("d.emplacement = ?")
        params.append(emplacement)
    if prefixe_emplacement is not None:
        conditions.append("substr(d.emplacement, 1, ?) = ?")
        params.extend([len(prefixe_emplacement), prefixe_emplacement])
    if article_id is not None:
        conditions.append("l.article_id = ?")
        params.append(article_id)
    if finition is not None:
        conditions.append("l.finition = ?")
        params.append(finition)
    if longueur_m is not None:
        conditions.append("l.longueur_m = ?")
        params.append(longueur_m)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    having = "" if inclure_soldes_nuls else "HAVING SUM(d.dq) <> 0"
    return des_dicts(
        conn,
        f"""
        WITH d AS (
            SELECT lot_id, emplacement_destination AS emplacement, quantite AS dq, poids_kg AS dp
            FROM mouvement_stock
            WHERE emplacement_destination IS NOT NULL AND (? IS NULL OR date_heure <= ?)
            UNION ALL
            SELECT lot_id, emplacement_source AS emplacement, -quantite AS dq, -poids_kg AS dp
            FROM mouvement_stock
            WHERE emplacement_source IS NOT NULL AND (? IS NULL OR date_heure <= ?)
        )
        SELECT d.lot_id AS lot_id, l.article_id AS article_id, a.designation AS designation,
               l.finition AS finition, l.longueur_m AS longueur_m, d.emplacement AS emplacement,
               SUM(d.dq) AS quantite, SUM(d.dp) AS poids_kg
        FROM d
        JOIN lot l ON l.id = d.lot_id
        JOIN article a ON a.id = l.article_id
        {where}
        GROUP BY d.lot_id, d.emplacement
        {having}
        ORDER BY a.designation, l.finition, l.longueur_m, d.emplacement, d.lot_id
        """,
        params,
    )


def totaux_par_type(conn: sqlite3.Connection) -> dict[str, int]:
    """Nombre total de pièces déplacées, par type de mouvement."""
    return {
        ligne["type"]: int(ligne["quantite"])
        for ligne in des_dicts(
            conn, "SELECT type, SUM(quantite) AS quantite FROM mouvement_stock GROUP BY type"
        )
    }


def retours_transformation_non_apparies(conn: sqlite3.Connection) -> list[dict]:
    """
    Lignes de réception de transformation dont l'entrée du lot résultat
    (ENTREE_RETOUR_TRANSFORMATION) n'est pas compensée exactement par la
    sortie du lot d'origine de chez le transformateur
    (CONSOMMATION_TRANSFORMATION) — c'est-à-dire du stock fantôme.
    """
    return des_dicts(
        conn,
        """
        SELECT document_source_id AS reception_transformation_ligne_id,
               SUM(CASE WHEN type = 'ENTREE_RETOUR_TRANSFORMATION'
                        THEN quantite ELSE 0 END) AS quantite_entree,
               SUM(CASE WHEN type = 'CONSOMMATION_TRANSFORMATION'
                        THEN quantite ELSE 0 END) AS quantite_consommee
        FROM mouvement_stock
        WHERE type IN ('ENTREE_RETOUR_TRANSFORMATION', 'CONSOMMATION_TRANSFORMATION')
        GROUP BY document_source_type, document_source_id
        HAVING quantite_entree <> quantite_consommee
        """,
    )


def livraisons_sans_destination_livre(conn: sqlite3.Connection) -> list[dict]:
    return des_dicts(
        conn,
        """
        SELECT id, lot_id, quantite, emplacement_destination FROM mouvement_stock
        WHERE type = 'SORTIE_LIVRAISON_CLIENT'
          AND (emplacement_destination IS NULL OR emplacement_destination <> 'LIVRE')
        """,
    )


def compter_mouvements(conn: sqlite3.Connection, types_exclus: typing.Sequence[str] = ()) -> int:
    """Nombre de mouvements du registre, hors types exclus."""
    marqueurs = ", ".join("?" for _ in types_exclus) or "''"
    ligne = un_ou_aucun(
        conn,
        f"SELECT COUNT(*) FROM mouvement_stock WHERE type NOT IN ({marqueurs})",
        tuple(types_exclus),
    )
    return int(ligne[0]) if ligne is not None else 0


def instant_mise_en_service(conn: sqlite3.Connection) -> typing.Optional[str]:
    """Instant de mise en service (inventaire initial de démarrage), ou None s'il n'existe pas."""
    ligne = un_ou_aucun(conn, "SELECT date_heure_mise_en_service FROM inventaire_initial")
    return ligne[0] if ligne is not None else None


# ---------------------------------------------------------------------------
# Affectations et réservations (lecture seule — disponibilité)
# ---------------------------------------------------------------------------


def quantite_affectee_non_sortie_lot(conn: sqlite3.Connection, lot_id: str) -> int:
    ligne = un_ou_aucun(
        conn,
        """
        SELECT COALESCE(SUM(quantite), 0) FROM affectation_stock
        WHERE lot_id = ? AND statut = 'ACTIVE' AND mouvement_physique_id IS NULL
        """,
        (lot_id,),
    )
    return int(ligne[0]) if ligne is not None else 0


def quantite_affectee_non_sortie_pool(
    conn: sqlite3.Connection, article_id: str, finition: str, longueur_m: float
) -> int:
    ligne = un_ou_aucun(
        conn,
        """
        SELECT COALESCE(SUM(a.quantite), 0)
        FROM affectation_stock a JOIN lot l ON l.id = a.lot_id
        WHERE l.article_id = ? AND l.finition = ? AND l.longueur_m = ?
          AND a.statut = 'ACTIVE' AND a.mouvement_physique_id IS NULL
        """,
        (article_id, finition, longueur_m),
    )
    return int(ligne[0]) if ligne is not None else 0


def quantite_reservee_devis(
    conn: sqlite3.Connection, article_id: str, finition: str, longueur_m: float, a_la_date: str
) -> int:
    """Réservations « badge » de devis encore en cours et non expirés — informatif uniquement."""
    ligne = un_ou_aucun(
        conn,
        """
        SELECT COALESCE(SUM(r.quantite), 0)
        FROM reservation_devis r
        JOIN devis_ligne dl ON dl.id = r.devis_ligne_id
        JOIN devis d ON d.id = dl.devis_id
        WHERE r.article_id = ? AND r.finition = ? AND r.longueur_m = ?
          AND r.expire_le >= ? AND d.statut = 'EN_COURS'
        """,
        (article_id, finition, longueur_m, a_la_date),
    )
    return int(ligne[0]) if ligne is not None else 0


# ---------------------------------------------------------------------------
# Référentiels et documents sources (lecture seule)
# ---------------------------------------------------------------------------


def utilisateur_existe(conn: sqlite3.Connection, utilisateur_id: str) -> bool:
    return (
        un_ou_aucun(conn, "SELECT 1 FROM utilisateur WHERE id = ?", (utilisateur_id,)) is not None
    )


def transformateur_existe(conn: sqlite3.Connection, transformateur_id: str) -> bool:
    return (
        un_ou_aucun(conn, "SELECT 1 FROM transformateur WHERE id = ?", (transformateur_id,))
        is not None
    )


def obtenir_bl_fournisseur_ligne(conn: sqlite3.Connection, ligne_id: str) -> typing.Optional[dict]:
    return un_dict(
        conn,
        "SELECT id, article_id, finition, longueur_m, quantite, poids_kg "
        "FROM bl_fournisseur_ligne WHERE id = ?",
        (ligne_id,),
    )


def obtenir_bon_sortie_transformation_ligne(
    conn: sqlite3.Connection, ligne_id: str
) -> typing.Optional[dict]:
    return un_dict(
        conn,
        """
        SELECT bstl.id, bstl.lot_id, bstl.quantite, bst.transformateur_id
        FROM bon_sortie_transformation_ligne bstl
        JOIN bon_sortie_transformation bst ON bst.id = bstl.bon_sortie_transformation_id
        WHERE bstl.id = ?
        """,
        (ligne_id,),
    )


def obtenir_reception_transformation_ligne(
    conn: sqlite3.Connection, ligne_id: str
) -> typing.Optional[dict]:
    return un_dict(
        conn,
        """
        SELECT rtl.id, rtl.bon_sortie_transformation_ligne_id, rtl.lot_resultat_id,
               rtl.quantite_recue, rtl.poids_recu_kg, rtl.quantite_chute, rtl.poids_chute_kg,
               bstl.lot_id AS lot_origine_id, bst.transformateur_id
        FROM reception_transformation_ligne rtl
        JOIN bon_sortie_transformation_ligne bstl
             ON bstl.id = rtl.bon_sortie_transformation_ligne_id
        JOIN bon_sortie_transformation bst ON bst.id = bstl.bon_sortie_transformation_id
        WHERE rtl.id = ?
        """,
        (ligne_id,),
    )


def obtenir_bl_client_ligne(conn: sqlite3.Connection, ligne_id: str) -> typing.Optional[dict]:
    return un_dict(
        conn,
        "SELECT id, lot_id, commande_ligne_id, type, quantite, poids_facturable_kg "
        "FROM bl_client_ligne WHERE id = ?",
        (ligne_id,),
    )
