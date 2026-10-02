"""
Repository de l'inventaire initial de démarrage (Phase 5.5, migration 0018).

Règle validée : GMC ERP démarre en 2026 par un inventaire initial réalisé à
l'instant exact de mise en service ; il devient le stock initial du
système. Ce n'est ni un achat, ni un BL fournisseur, ni une réception.

Accès SQL structuré aux tables `inventaire_initial` (en-tête unique) et
`inventaire_initial_ligne`, sans logique métier : les contrôles sont faits
par `services/inventaire_initial_service.py`. Les deux tables sont
immuables en base (triggers) : aucune mise à jour ni suppression exposée.
"""

from __future__ import annotations

import sqlite3
import typing

from repositories.base import des_dicts, executer, un_dict


def inserer_entete(
    conn: sqlite3.Connection,
    *,
    id: str,
    date_heure_mise_en_service: str,
    cree_par: str,
    observation: typing.Optional[str] = None,
) -> None:
    executer(
        conn,
        """
        INSERT INTO inventaire_initial (id, date_heure_mise_en_service, observation, cree_par)
        VALUES (?, ?, ?, ?)
        """,
        (id, date_heure_mise_en_service, observation, cree_par),
    )


def obtenir_entete(conn: sqlite3.Connection) -> typing.Optional[dict]:
    """L'inventaire initial (il n'en existe qu'un), ou None."""
    return un_dict(conn, "SELECT * FROM inventaire_initial")


def inserer_ligne(
    conn: sqlite3.Connection,
    *,
    id: str,
    inventaire_initial_id: str,
    article_id: str,
    finition: str,
    longueur_m: float,
    quantite: int,
    poids_kg: float,
    emplacement: str,
    cout_unitaire_minor: int,
    unite_cout: str,
    valeur_minor: int,
    devise: str,
    saisie_originale: str,
    cree_par: str,
) -> None:
    executer(
        conn,
        """
        INSERT INTO inventaire_initial_ligne
            (id, inventaire_initial_id, article_id, finition, longueur_m, quantite, poids_kg,
             emplacement, cout_unitaire_minor, unite_cout, valeur_minor, devise,
             saisie_originale, cree_par)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            id,
            inventaire_initial_id,
            article_id,
            finition,
            longueur_m,
            quantite,
            poids_kg,
            emplacement,
            cout_unitaire_minor,
            unite_cout,
            valeur_minor,
            devise,
            saisie_originale,
            cree_par,
        ),
    )


def obtenir_ligne(conn: sqlite3.Connection, ligne_id: str) -> typing.Optional[dict]:
    return un_dict(conn, "SELECT * FROM inventaire_initial_ligne WHERE id = ?", (ligne_id,))


def lister_lignes(conn: sqlite3.Connection, inventaire_initial_id: str) -> list[dict]:
    return des_dicts(
        conn,
        "SELECT * FROM inventaire_initial_ligne WHERE inventaire_initial_id = ? "
        "ORDER BY cree_le, rowid",
        (inventaire_initial_id,),
    )
