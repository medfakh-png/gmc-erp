"""
Masses linéiques validées par Mohamed (Phase 5.5, décision définitive).

Seules les valeurs explicitement validées figurent ici — aucune formule
n'est déduite ni généralisée à d'autres articles :

    FP 45/20  = 7,2 kg/ml
    FP 120/30 = 28,8 kg/ml
    FP 130/30 = 31,2 kg/ml   (la valeur 28,8 précédemment associée à
                              FP 130/30 est annulée)

Les anciennes valeurs de la liste MV (4,07 pour FP 45/20 ; 283,8 pour
FP 120/30) ne doivent jamais être réintroduites.

Règle validée : si le fichier MV contient une valeur différente, elle n'est
ni fusionnée automatiquement ni remplacée silencieusement —
`comparer_avec_liste_mv()` se contente de SIGNALER l'écart, sans rien
modifier. L'import de la liste MV (non réalisé en Phase 5.5) s'en servira.

Tôle plane — règle définitive validée (Phase 5.5) : volume × densité.

    Volume (dm³) = longueur (dm) × largeur (dm) × épaisseur (dm)
    Poids (kg)   = Volume (dm³) × 8 kg/dm³

La densité de calcul des tôles planes est 8 kg/dm³ (règle GMC ; aucune
autre valeur, en particulier pas 7,85). Les dimensions se saisissent avec
leur unité (mm par défaut d'usage, cm ou m acceptés) et sont converties en
dm : 100 mm = 1 dm ; 10 cm = 1 dm ; 10 dm = 1 m. Contrôle validé :
3000 mm × 1500 mm × 1 mm = 30 dm × 15 dm × 0,01 dm = 4,5 dm³ ; × 8 kg/dm³
= 36 kg. Aucun résultat intermédiaire n'est interprété comme des grammes ;
aucun calcul intermédiaire n'est arrondi (arithmétique décimale exacte).
Les poids de tôle de la liste MV sont en kg.
"""

from __future__ import annotations

import decimal
import typing

from core import unites
from core.erreurs import ErreurSaisieInvalide

# Densité de calcul des tôles planes (règle GMC validée) : 8 kg/dm³.
DENSITE_TOLE_PLANE = unites.lire("8 kg/dm³")


def _propre(valeur: decimal.Decimal) -> decimal.Decimal:
    """Même valeur exacte, sans zéros décimaux superflus (affichage)."""
    return decimal.Decimal(format(valeur.normalize(), "f"))


MASSES_LINEIQUES_VALIDEES: dict[str, unites.Mesure] = {
    "FP 45/20": unites.lire("7,2 kg/ml"),
    "FP 120/30": unites.lire("28,8 kg/ml"),
    "FP 130/30": unites.lire("31,2 kg/ml"),
}


def masse_lineique_validee(designation: str) -> typing.Optional[unites.Mesure]:
    """Masse linéique validée de cette désignation exacte, ou None si aucune n'a été validée."""
    return MASSES_LINEIQUES_VALIDEES.get(designation)


def comparer_avec_liste_mv(designation: str, masse_mv: unites.Mesure) -> typing.Optional[dict]:
    """
    Compare une masse lue dans le fichier MV (avec son unité) à la valeur
    validée. Renvoie None si aucune valeur n'est validée pour cette
    désignation ou si les deux sont identiques ; sinon, un signalement
    d'écart. Ne modifie jamais rien : la décision reste à Mohamed.
    """
    validee = masse_lineique_validee(designation)
    if validee is None:
        return None
    valeur_mv = unites.en_kg_par_metre(masse_mv)
    valeur_validee = unites.en_kg_par_metre(validee)
    if valeur_mv == valeur_validee:
        return None
    return {
        "designation": designation,
        "valeur_validee_kg_m": str(valeur_validee),
        "valeur_liste_mv_kg_m": str(valeur_mv),
        "action": "ECART_SIGNALE_AUCUNE_MODIFICATION",
    }


def calcul_poids_tole_plane(
    longueur: typing.Any, largeur: typing.Any, epaisseur: typing.Any
) -> dict:
    """
    Poids d'une tôle plane = volume (dm³) × 8 kg/dm³ (règle validée). Chaque
    dimension se saisit AVEC son unité (« 3000 mm », « 150 cm », « 3 m »,
    « 30 dm ») ; une dimension sans unité est refusée. Les dimensions sont
    converties en dm, le volume est calculé en dm³, puis multiplié par la
    densité. Arithmétique décimale exacte, aucun arrondi intermédiaire.
    Renvoie le détail du calcul (traçabilité).
    """
    mesures = {
        "longueur": unites.exiger(longueur, unites.LONGUEUR, "longueur"),
        "largeur": unites.exiger(largeur, unites.LONGUEUR, "largeur"),
        "epaisseur": unites.exiger(epaisseur, unites.LONGUEUR, "épaisseur"),
    }
    dimensions_dm = {champ: unites.en_decimetres(m) for champ, m in mesures.items()}
    for champ, valeur in dimensions_dm.items():
        if valeur <= 0:
            raise ErreurSaisieInvalide(
                f"Tôle plane : {champ} « {mesures[champ].saisie} » doit être strictement positive."
            )
    volume_dm3 = dimensions_dm["longueur"] * dimensions_dm["largeur"] * dimensions_dm["epaisseur"]
    densite = unites.en_kg_par_dm3(DENSITE_TOLE_PLANE)
    return {
        "saisies": {champ: m.saisie for champ, m in mesures.items()},
        "dimensions_dm": {champ: str(_propre(valeur)) for champ, valeur in dimensions_dm.items()},
        "volume_dm3": _propre(volume_dm3),
        "densite_kg_dm3": _propre(densite),
        "poids_kg": _propre(volume_dm3 * densite),
    }


def poids_tole_plane_kg(
    longueur: typing.Any, largeur: typing.Any, epaisseur: typing.Any
) -> decimal.Decimal:
    """Poids (kg, décimal exact) d'une tôle plane — cf. calcul_poids_tole_plane()."""
    return calcul_poids_tole_plane(longueur, largeur, epaisseur)["poids_kg"]
