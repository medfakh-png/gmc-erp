"""
Numérotation documentaire (Phase 5.4).

Génère le numéro humain séquentiel de chaque document GMC, par type et par
année civile — format et liste de types déjà validés, jamais réinventés
ici : voir `docs/BUSINESS_RULES.md` § « Identifiants et numérotation »
(décision Phase 2, préfixes confirmés Phase 4) et le commentaire de
`migrations/0002_numerotation.sql` : `DEV-2026-0001`, `CMD-2026-0001`,
`BCF-2026-0001`, `BLF-2026-0001`, `FFO-2026-0001`, `BCT-2026-0001`,
`BST-2026-0001`, `RTR-2026-0001`, `BLC-2026-0001`, `FAC-2026-0001`.

Ce module fournit UNIQUEMENT le numéro suivant à partir de
`compteur_numerotation` (table en place depuis la Phase 4). Il ne crée
aucun document et ne connaît aucune règle propre à un type de document —
c'est aux futurs services (Phase 5.5+) d'appeler `prochain_numero()` au
moment de créer leur document, à l'intérieur de la même transaction
(`db.connexion.transaction`) que l'INSERT du document : si cette
transaction échoue, l'incrémentation du compteur est annulée avec le
reste du travail (le numéro n'est jamais "brûlé" par une écriture qui n'a
finalement pas eu lieu).

Un numéro effectivement attribué (transaction validée) n'est en revanche
jamais réutilisé, y compris si le document est ensuite annulé — cohérent
avec la règle générale du projet « aucune suppression réelle »
(`CLAUDE.md`) : une trace, jamais un trou comblé après coup.
"""
from __future__ import annotations

import datetime
import sqlite3
import typing

from repositories import numerotation_repository

# Types de document valides — reflètent exactement les 10 préfixes déjà
# validés (Phase 2, confirmés Phase 4). Contrairement à
# `core.audit.ACTIONS_VALIDES`, il n'existe aucune contrainte CHECK en
# base sur `compteur_numerotation.type_document` (colonne TEXT libre) :
# cette liste ne peut donc pas être vérifiée automatiquement contre le
# schéma — elle est vérifiée manuellement contre
# `docs/BUSINESS_RULES.md` et le commentaire de
# `migrations/0002_numerotation.sql`, qui énumèrent les deux mêmes 10
# valeurs.
TYPES_DOCUMENT_VALIDES = (
    "DEV",  # devis
    "CMD",  # commande_client
    "BCF",  # bon_commande_fournisseur
    "BLF",  # bl_fournisseur
    "FFO",  # facture_fournisseur
    "BCT",  # bon_commande_transformation
    "BST",  # bon_sortie_transformation
    "RTR",  # reception_transformation
    "BLC",  # bl_client
    "FAC",  # facture_client
)

_LARGEUR_MINIMALE_NUMERO = 4


def prochain_numero(
    conn: sqlite3.Connection,
    type_document: str,
    annee: typing.Optional[int] = None,
) -> str:
    """
    Attribue et renvoie le prochain numéro humain pour `type_document`,
    au format `{TYPE}-{ANNEE}-{NNNN}` (ex. `DEV-2026-0001`, et
    `DEV-2026-10000` sans troncature au-delà de 9999 : le zéro-remplissage
    est un minimum, pas un plafond).

    `annee` est optionnelle ; par défaut l'année civile en cours (calculée
    au moment de l'appel). Un appelant qui numérote un document daté
    différemment peut la fournir explicitement.

    Lève `ValueError` si `type_document` n'est pas l'un des 10 types
    validés (voir `TYPES_DOCUMENT_VALIDES`), avant tout accès à la base.
    """
    if type_document not in TYPES_DOCUMENT_VALIDES:
        raise ValueError(
            f"Type de document invalide : {type_document!r} "
            f"(attendu parmi {TYPES_DOCUMENT_VALIDES})"
        )

    if annee is None:
        annee = datetime.date.today().year

    dernier_numero = numerotation_repository.incrementer_et_obtenir(conn, type_document, annee)

    return f"{type_document}-{annee}-{dernier_numero:0{_LARGEUR_MINIMALE_NUMERO}d}"


def dernier_numero_attribue(conn: sqlite3.Connection, type_document: str, annee: int) -> int:
    """
    Renvoie le dernier numéro attribué pour ce type/cette année (0 si
    aucun n'a encore été attribué) — lecture seule, ne modifie rien.
    Diagnostic/affichage uniquement : ne jamais s'en servir pour deviner
    le prochain numéro, toujours passer par `prochain_numero()`.
    """
    ligne = numerotation_repository.obtenir(conn, type_document, annee)
    return ligne[0] if ligne is not None else 0
