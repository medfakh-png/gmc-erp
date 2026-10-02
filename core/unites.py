"""
Unités de saisie (Phase 5.5 — règle transversale validée « unité
obligatoire à la saisie »).

Règle validée :
- toute saisie de quantité, poids, longueur, dimension ou prix comporte
  obligatoirement son unité ; le système ne devine JAMAIS une unité
  implicite et refuse une saisie ambiguë ;
- l'unité saisie est conservée pour la traçabilité (`Mesure.saisie`) ; le
  système convertit ensuite vers l'unité interne utilisée par les calculs ;
- 1 tonne = 1 000 kg ; masses physiques internes (achats, réceptions,
  transformations, livraisons physiques) en kg ; ventes commerciales en
  tonnes (ex. 5 DT HT/kg = 5 000 DT HT/tonne).

Ce module ne contient que des conversions physiques ou arithmétiques
exactes (arithmétique décimale, jamais de flottant) : aucune règle métier
n'y est décidée.

Unité de valorisation (règle définitive validée, Phase 5.5) : un prix de
revient s'exprime dans l'unité de valorisation de l'article — DT/kg (KG),
DT/ml (ML), DT/unité (UNITE, une unité = une pièce) ou DT/tonne (TONNE).
`prix_minor_en_unite_valorisation()` n'accepte qu'un prix déjà dans cette
unité, ou la seule conversion purement physique kg <-> t ; jamais une
conversion implicite pièce <-> kg ou pièce <-> ml (qui dépendrait du poids
ou de la longueur d'un lot).

Arrondi (règle définitive validée, `core/arrondi.py`) : un MONTANT CALCULÉ
qui ne tombe pas exactement au millime est arrondi au millime le plus
proche, 0,5 vers le haut, une seule fois, sur le montant final ; aucun
sous-calcul n'est arrondi (masses, volumes, prix unitaires et conversions
restent exacts). Une VALEUR SAISIE (montant ou prix unitaire) n'est jamais
arrondie : elle doit être exprimable en unités monétaires minimales
entières (représentation validée en Phase 4.1), sinon elle est refusée.

Unités internes : pièce (comptage), kg (masse), m (longueur), kg/m (masse
linéique), dm³ (volume), kg/dm³ (masse volumique), unité monétaire minimale
(montants). Conversions de référence validées : 1 000 mm = 1 m ;
100 cm = 1 m ; 100 mm = 1 dm ; 10 dm = 1 m ; 1 m³ = 1 000 dm³.
"""

from __future__ import annotations

import dataclasses
import decimal
import re
import typing

from core.arrondi import arrondi_minor
from core.erreurs import (
    ErreurMontantIncoherent,
    ErreurSaisieInvalide,
    ErreurUniteManquante,
    ErreurUniteValorisation,
)

D = decimal.Decimal

# Natures de grandeur.
COMPTAGE = "COMPTAGE"
MASSE = "MASSE"
LONGUEUR = "LONGUEUR"
MASSE_LINEIQUE = "MASSE_LINEIQUE"
PRIX = "PRIX"  # montant par unité (par kg, par tonne ou par pièce)
MONTANT = "MONTANT"
VOLUME = "VOLUME"
MASSE_VOLUMIQUE = "MASSE_VOLUMIQUE"

LIBELLES_NATURE = {
    COMPTAGE: "un nombre de pièces (ex. « 10 pièces »)",
    MASSE: "une masse (ex. « 2 500 kg » ou « 2,5 t »)",
    LONGUEUR: "une longueur (ex. « 12 m »)",
    MASSE_LINEIQUE: "une masse linéique (ex. « 28,8 kg/ml »)",
    PRIX: "un prix unitaire (ex. « 5 DT/kg », « 5 000 DT/tonne », « 12 DT/ml », « 30 DT/pièce »)",
    MONTANT: "un montant (ex. « 12 500 DT »)",
    VOLUME: "un volume (ex. « 4,5 dm³ » ou « 0,0045 m³ »)",
    MASSE_VOLUMIQUE: "une masse volumique (ex. « 8 kg/dm³ »)",
}

# Unité saisie (en minuscules) -> (nature, unité normalisée, facteur vers l'unité interne).
_UNITES_PHYSIQUES: dict[str, tuple[str, str, D]] = {}
for _alias in ("pièce", "pièces", "piece", "pieces", "pce", "pcs", "pc", "unité", "unités"):
    _UNITES_PHYSIQUES[_alias] = (COMPTAGE, "pièce", D(1))
for _alias in ("kg", "kilo", "kilos", "kilogramme", "kilogrammes"):
    _UNITES_PHYSIQUES[_alias] = (MASSE, "kg", D(1))
for _alias in ("t", "tonne", "tonnes"):
    _UNITES_PHYSIQUES[_alias] = (MASSE, "t", D(1000))
for _alias in ("m", "mètre", "mètres", "metre", "metres", "ml"):
    _UNITES_PHYSIQUES[_alias] = (LONGUEUR, "m", D(1))
for _alias in ("mm", "millimètre", "millimètres", "millimetre", "millimetres"):
    _UNITES_PHYSIQUES[_alias] = (LONGUEUR, "mm", D("0.001"))
for _alias in ("cm", "centimètre", "centimètres", "centimetre", "centimetres"):
    _UNITES_PHYSIQUES[_alias] = (LONGUEUR, "cm", D("0.01"))
for _alias in ("dm", "décimètre", "décimètres", "decimetre", "decimetres"):
    _UNITES_PHYSIQUES[_alias] = (LONGUEUR, "dm", D("0.1"))
# Volumes (unité interne : dm³) ; 1 m³ = 1 000 dm³.
for _alias in ("dm³", "dm3"):
    _UNITES_PHYSIQUES[_alias] = (VOLUME, "dm³", D(1))
for _alias in ("m³", "m3"):
    _UNITES_PHYSIQUES[_alias] = (VOLUME, "m³", D(1000))
# Masse volumique (unité interne : kg/dm³).
for _alias in ("kg/dm³", "kg/dm3"):
    _UNITES_PHYSIQUES[_alias] = (MASSE_VOLUMIQUE, "kg/dm³", D(1))
for _alias in ("kg/m", "kg/ml"):
    _UNITES_PHYSIQUES[_alias] = (MASSE_LINEIQUE, "kg/m", D(1))

# Devise saisie -> (code devise, nombre d'unités minimales par unité).
_DEVISES: dict[str, tuple[str, int]] = {
    "dt": ("TND", 1000),
    "tnd": ("TND", 1000),
    "eur": ("EUR", 100),
    "€": ("EUR", 100),
    "usd": ("USD", 100),
    "$": ("USD", 100),
}

# Unité « par ... » d'un prix -> (unité normalisée, facteur vers l'unité interne).
_PAR_UNITE: dict[str, tuple[str, D]] = {}
for _alias in ("kg",):
    _PAR_UNITE[_alias] = ("kg", D(1))
for _alias in ("t", "tonne", "tonnes"):
    _PAR_UNITE[_alias] = ("t", D(1000))
for _alias in ("pièce", "pièces", "piece", "pieces", "pce", "pcs", "pc", "unité", "unités"):
    _PAR_UNITE[_alias] = ("pièce", D(1))
for _alias in ("ml", "m", "mètre", "metre"):
    _PAR_UNITE[_alias] = ("ml", D(1))

# Unité « par ... » d'un prix -> unité de valorisation correspondante.
UNITE_VALORISATION_DU_PRIX = {"kg": "KG", "t": "TONNE", "ml": "ML", "pièce": "UNITE"}
# Unités de masse : les seules entre lesquelles un prix se convertit exactement
# (1 t = 1 000 kg). Décision validée (Proposition A).
UNITES_MASSE = frozenset({"KG", "TONNE"})
LIBELLES_UNITE_VALORISATION = {
    "KG": "DT/kg",
    "ML": "DT/ml",
    "UNITE": "DT/unité",
    "TONNE": "DT/tonne",
}

_SYMBOLES_DEVISE = "|".join(re.escape(d) for d in sorted(_DEVISES, key=len, reverse=True))
_MOTIF_PRIX = re.compile(rf"^(?P<devise>{_SYMBOLES_DEVISE})\s*(?P<ht>ht)?\s*/\s*(?P<par>[a-zèé]+)$")
_MOTIF_MONTANT = re.compile(rf"^(?P<devise>{_SYMBOLES_DEVISE})\s*(?P<ht>ht)?$")

# Nombres acceptés : « 2 500 », « 2 500,75 », « 2500 », « 2,5 », « 12.5 ».
# Refusés car ambigus : « 2.500 » (séparateur de milliers ou décimal ?),
# « 2.500,5 », « 25 00 ».
_ESPACES = "   "
_NOMBRE_FR = re.compile(r"^\d{1,3}(?: \d{3})+(?:,\d+)?$|^\d+(?:,\d+)?$")
_NOMBRE_POINT = re.compile(r"^(?P<entier>\d+)\.(?P<decimales>\d+)$")
_DEBUT_UNITE = re.compile(r"^(?P<nombre>[\d\s  .,]*\d)\s*(?P<unite>\S.*)?$")


@dataclasses.dataclass(frozen=True)
class Mesure:
    """
    Une valeur AVEC son unité. `saisie` conserve exactement ce que
    l'utilisateur a saisi (traçabilité) ; `valeur` et `unite` en sont la
    lecture normalisée ; les conversions vers l'unité interne sont faites
    par les fonctions de ce module.
    """

    valeur: D
    unite: str
    nature: str
    saisie: str
    devise: typing.Optional[str] = None
    hors_taxe: bool = False

    def __str__(self) -> str:
        return self.saisie

    def trace(self) -> dict:
        """Représentation JSON-sérialisable, à conserver pour la traçabilité."""
        donnees: dict[str, typing.Any] = {
            "saisie": self.saisie,
            "valeur": str(self.valeur),
            "unite": self.unite,
            "nature": self.nature,
        }
        if self.devise is not None:
            donnees["devise"] = self.devise
        return donnees


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------


def _lire_nombre(texte: str) -> D:
    brut = texte.strip()
    for espace in _ESPACES:
        brut = brut.replace(espace, " ")
    brut = re.sub(" +", " ", brut)
    if _NOMBRE_FR.match(brut):
        return D(brut.replace(" ", "").replace(",", "."))
    point = _NOMBRE_POINT.match(brut)
    if point:
        if len(point.group("decimales")) == 3 and point.group("entier") != "0":
            raise ErreurSaisieInvalide(
                f"Valeur ambiguë : « {texte.strip()} » (le point est-il un séparateur de "
                "milliers ou décimal ?). Utilisez une virgule pour les décimales "
                "(ex. « 2,5 ») et un espace pour les milliers (ex. « 2 500 »)."
            )
        return D(brut)
    raise ErreurSaisieInvalide(
        f"Valeur illisible ou ambiguë : « {texte.strip()} » "
        "(exemples valides : « 2 500 », « 2,5 », « 12 »)."
    )


def _valeur_programmatique(valeur: typing.Any) -> D:
    if isinstance(valeur, bool):
        raise ErreurSaisieInvalide(f"Valeur invalide : {valeur!r}.")
    if isinstance(valeur, D):
        return valeur
    if isinstance(valeur, int):
        return D(valeur)
    if isinstance(valeur, float):
        if valeur != valeur or valeur in (float("inf"), float("-inf")):
            raise ErreurSaisieInvalide(f"Valeur invalide : {valeur!r}.")
        return D(repr(valeur))
    if isinstance(valeur, str):
        return _lire_nombre(valeur)
    raise ErreurSaisieInvalide(f"Valeur invalide : {valeur!r}.")


def _construire(nombre: D, unite_saisie: str, texte_saisi: str) -> Mesure:
    unite = re.sub(r"\s+", " ", unite_saisie.strip())
    cle = unite.lower()
    if not cle:
        raise ErreurUniteManquante(
            f"Unité obligatoire : « {texte_saisi} » n'indique pas son unité "
            "(ex. « 2 500 kg », « 2,5 t », « 12 m », « 10 pièces », « 5 DT/kg »)."
        )
    if "ttc" in cle:
        raise ErreurSaisieInvalide(
            f"« {texte_saisi} » : un prix ou montant TTC n'est pas pris en charge (il ne peut "
            "pas être converti sans taux de TVA validé) — saisir la valeur hors taxes."
        )
    if nombre < 0:
        raise ErreurSaisieInvalide(f"« {texte_saisi} » : une valeur négative n'est pas admise.")
    if cle in _UNITES_PHYSIQUES:
        nature, normalisee, _ = _UNITES_PHYSIQUES[cle]
        return Mesure(valeur=nombre, unite=normalisee, nature=nature, saisie=texte_saisi)
    prix = _MOTIF_PRIX.match(cle)
    if prix:
        par = prix.group("par")
        if par not in _PAR_UNITE:
            raise ErreurSaisieInvalide(f"« {texte_saisi} » : unité de prix inconnue (« /{par} »).")
        code, _ = _DEVISES[prix.group("devise")]
        normalisee = f"{code}/{_PAR_UNITE[par][0]}"
        return Mesure(
            valeur=nombre,
            unite=normalisee,
            nature=PRIX,
            saisie=texte_saisi,
            devise=code,
            hors_taxe=bool(prix.group("ht")),
        )
    montant = _MOTIF_MONTANT.match(cle)
    if montant:
        code, _ = _DEVISES[montant.group("devise")]
        return Mesure(
            valeur=nombre,
            unite=code,
            nature=MONTANT,
            saisie=texte_saisi,
            devise=code,
            hors_taxe=bool(montant.group("ht")),
        )
    raise ErreurSaisieInvalide(f"« {texte_saisi} » : unité inconnue (« {unite} »).")


def lire(texte: str) -> Mesure:
    """Lit une saisie complète, valeur ET unité : « 2 500 kg », « 5 000 DT/tonne »..."""
    if not isinstance(texte, str) or not texte.strip():
        raise ErreurSaisieInvalide(f"Saisie vide ou invalide : {texte!r}.")
    brut = texte.strip()
    decoupe = _DEBUT_UNITE.match(brut)
    if not decoupe:
        raise ErreurSaisieInvalide(
            f"Saisie illisible : « {brut} » (la valeur doit précéder l'unité)."
        )
    nombre = _lire_nombre(decoupe.group("nombre"))
    return _construire(nombre, decoupe.group("unite") or "", brut)


def mesure(valeur: typing.Any, unite: typing.Optional[str]) -> Mesure:
    """Construit une mesure à partir d'une valeur et d'une unité fournies séparément."""
    if unite is None or not str(unite).strip():
        raise ErreurUniteManquante(
            f"Unité obligatoire pour la valeur {valeur!r} "
            "(ex. « kg », « t », « m », « pièces », « DT/kg »)."
        )
    nombre = _valeur_programmatique(valeur)
    texte = f"{valeur} {str(unite).strip()}"
    return _construire(nombre, str(unite), texte)


def exiger(saisie: typing.Any, nature: str, champ: str) -> Mesure:
    """
    Point d'entrée des services : accepte une `Mesure` ou un texte « valeur
    unité », de la nature attendue. Un nombre seul (sans unité) est TOUJOURS
    refusé : le système ne devine jamais une unité implicite.
    """
    if isinstance(saisie, Mesure):
        resultat = saisie
    elif isinstance(saisie, str):
        resultat = lire(saisie)
    elif isinstance(saisie, (int, float, D)) and not isinstance(saisie, bool):
        raise ErreurUniteManquante(
            f"{champ.capitalize()} : unité obligatoire — {saisie!r} ne précise pas son unité "
            f"(attendu : {LIBELLES_NATURE[nature]})."
        )
    else:
        raise ErreurSaisieInvalide(f"{champ.capitalize()} : saisie invalide ({saisie!r}).")
    if resultat.nature != nature:
        raise ErreurSaisieInvalide(
            f"{champ.capitalize()} : « {resultat.saisie} » n'est pas {LIBELLES_NATURE[nature]}."
        )
    return resultat


# ---------------------------------------------------------------------------
# Conversions vers les unités internes (exactes)
# ---------------------------------------------------------------------------


def _verifier_nature(m: Mesure, nature: str) -> None:
    if m.nature != nature:
        raise ErreurSaisieInvalide(f"« {m.saisie} » n'est pas {LIBELLES_NATURE[nature]}.")


def en_kg(m: Mesure) -> D:
    """Masse en kg (1 t = 1 000 kg)."""
    _verifier_nature(m, MASSE)
    return m.valeur * _UNITES_PHYSIQUES[m.unite][2]


def en_tonnes(m: Mesure) -> D:
    """Masse en tonnes (unité commerciale des ventes)."""
    return en_kg(m) / D(1000)


def en_metres(m: Mesure) -> D:
    _verifier_nature(m, LONGUEUR)
    return m.valeur * _UNITES_PHYSIQUES[m.unite][2]


def en_millimetres(m: Mesure) -> D:
    """Longueur en mm (1 000 mm = 1 m ; 100 cm = 1 m)."""
    return en_metres(m) * D(1000)


def en_decimetres(m: Mesure) -> D:
    """Longueur en dm (100 mm = 1 dm ; 10 cm = 1 dm ; 10 dm = 1 m)."""
    return en_metres(m) * D(10)


def en_dm3(m: Mesure) -> D:
    """Volume en dm³ (1 m³ = 1 000 dm³)."""
    _verifier_nature(m, VOLUME)
    return m.valeur * _UNITES_PHYSIQUES[m.unite][2]


def en_m3(m: Mesure) -> D:
    """Volume en m³ (dm³ ÷ 1 000)."""
    return en_dm3(m) / D(1000)


def en_kg_par_dm3(m: Mesure) -> D:
    """Masse volumique en kg/dm³."""
    _verifier_nature(m, MASSE_VOLUMIQUE)
    return m.valeur


def en_kg_par_metre(m: Mesure) -> D:
    _verifier_nature(m, MASSE_LINEIQUE)
    return m.valeur


def en_pieces(m: Mesure) -> int:
    """Nombre de pièces — toujours un entier."""
    _verifier_nature(m, COMPTAGE)
    if m.valeur != m.valeur.to_integral_value():
        raise ErreurSaisieInvalide(f"« {m.saisie} » : un nombre de pièces est toujours entier.")
    return int(m.valeur)


def _unites_minimales(devise: str) -> int:
    for code, minimales in _DEVISES.values():
        if code == devise:
            return minimales
    raise ErreurSaisieInvalide(f"Devise inconnue : {devise!r}.")  # pragma: no cover


def prix_minor_par_kg(m: Mesure) -> D:
    """Prix en unités monétaires minimales PAR KG (exact, éventuellement fractionnaire)."""
    _verifier_nature(m, PRIX)
    par = m.unite.split("/")[1]
    if par not in ("kg", "t"):
        raise ErreurSaisieInvalide(f"« {m.saisie} » n'est pas un prix par masse (kg ou tonne).")
    assert m.devise is not None
    return m.valeur * _unites_minimales(m.devise) / _PAR_UNITE[par][1]


def prix_minor_par_tonne(m: Mesure) -> D:
    """Prix en unités monétaires minimales PAR TONNE (1 t = 1 000 kg)."""
    return prix_minor_par_kg(m) * D(1000)


def prix_minor_par_piece(m: Mesure) -> int:
    """Prix par pièce en unités monétaires minimales — doit être exact."""
    _verifier_nature(m, PRIX)
    if m.unite.split("/")[1] != "pièce":
        raise ErreurSaisieInvalide(f"« {m.saisie} » n'est pas un prix par pièce.")
    assert m.devise is not None
    return _entier_exact(m.valeur * _unites_minimales(m.devise), m.saisie)


def montant_minor(m: Mesure) -> int:
    """Montant en unités monétaires minimales (millimes, centimes) — doit être exact."""
    _verifier_nature(m, MONTANT)
    assert m.devise is not None
    return _entier_exact(
        m.valeur * _unites_minimales(m.devise), m.saisie, MESSAGE_MONTANT_NON_REPRESENTABLE
    )


MESSAGE_PRIX_NON_REPRESENTABLE = (
    "Un prix unitaire n'est jamais arrondi. Saisissez le prix avec une précision "
    "représentable dans son unité d'origine."
)
MESSAGE_MONTANT_NON_REPRESENTABLE = (
    "Un montant saisi n'est jamais arrondi. Saisissez-le avec une précision représentable "
    "(millimes ou centimes entiers)."
)


def _entier_exact(valeur: D, libelle: str, message: str = MESSAGE_PRIX_NON_REPRESENTABLE) -> int:
    """Valeur saisie en unités monétaires minimales : entière, sinon refusée (jamais arrondie)."""
    if valeur != valeur.to_integral_value():
        raise ErreurMontantIncoherent(
            f"« {libelle} » = {format(valeur.normalize(), 'f')} unités monétaires minimales, "
            f"non entier. {message}"
        )
    return int(valeur)


def montant_minor_masse_prix(masse: Mesure, prix: Mesure) -> int:
    """
    Montant = masse × prix au poids, en unités monétaires minimales. Calculé
    en arithmétique décimale exacte sur l'unité interne (kg), puis arrondi
    UNE SEULE FOIS au millime le plus proche, 0,5 vers le haut (règle
    validée) : le résultat est identique que la masse soit saisie en kg ou en
    tonnes et le prix en DT/kg ou en DT/tonne (ex. 2 500 kg × 5 DT/kg =
    2,5 t × 5 000 DT/t = 12 500 DT ; 1 000,5 kg × 2,501 DT/kg = 2 502,251 DT).
    """
    return arrondi_minor(en_kg(masse) * prix_minor_par_kg(prix))


def montant_minor_pieces_prix(quantite: Mesure, prix: Mesure) -> int:
    """Montant exact = nombre de pièces × prix par pièce, en unités monétaires minimales."""
    return en_pieces(quantite) * prix_minor_par_piece(prix)


def prix_minor_en_unite_valorisation(m: Mesure, unite_valorisation: str) -> int:
    """
    Prix en unités monétaires minimales PAR UNITÉ DE VALORISATION
    (KG, ML, UNITE, TONNE) — entier exact, sinon refusé. Un prix unitaire
    n'est jamais arrondi : ce n'est pas un montant final, et l'arrondir
    reviendrait à arrondir un sous-calcul (interdit par la règle validée).

    Seules conversions faites (explicites, exactes) : kg <-> t (1 t = 1 000
    kg). Un prix dans une autre unité que celle de l'article (ex. DT/pièce
    pour un article valorisé au kg) est refusé : le convertir exigerait le
    poids ou la longueur d'un lot, ce serait une conversion implicite.
    """
    _verifier_nature(m, PRIX)
    if unite_valorisation not in LIBELLES_UNITE_VALORISATION:
        raise ErreurUniteValorisation(f"Unité de valorisation inconnue : {unite_valorisation!r}.")
    par = m.unite.split("/")[1]
    unite_prix = UNITE_VALORISATION_DU_PRIX[par]
    assert m.devise is not None
    en_minimales = m.valeur * _unites_minimales(m.devise)
    if unite_prix == unite_valorisation:
        valeur = en_minimales
    elif {unite_prix, unite_valorisation} == {"KG", "TONNE"}:
        valeur = en_minimales * D(1000) if unite_valorisation == "TONNE" else en_minimales / D(1000)
    else:
        raise ErreurUniteValorisation(
            f"« {m.saisie} » n'est pas exprimé dans l'unité de valorisation de l'article "
            f"({LIBELLES_UNITE_VALORISATION[unite_valorisation]}) : aucune conversion implicite "
            "n'est faite (seule la conversion kg <-> tonne est admise)."
        )
    return _entier_exact(
        valeur,
        f"{m.saisie} en {LIBELLES_UNITE_VALORISATION[unite_valorisation]}",
        MESSAGE_PRIX_NON_REPRESENTABLE
        + " Pour conserver toute la précision, gardez le prix dans son unité d'origine : "
        "la conversion exacte est faite au moment du calcul.",
    )


def unites_de_prix_compatibles(unite_prix: str, unite_valorisation: str) -> bool:
    """
    Un prix exprimé dans `unite_prix` peut-il valoriser un article dont
    l'unité de valorisation est `unite_valorisation` ? Oui si c'est la même
    unité, ou si les deux sont des unités de masse (kg <-> tonne : conversion
    physique exacte). Jamais pièce <-> kg ni ml <-> kg (conversion implicite).
    """
    return unite_prix == unite_valorisation or (
        unite_prix in UNITES_MASSE and unite_valorisation in UNITES_MASSE
    )


def prix_saisi(m: Mesure) -> tuple[int, str]:
    """
    Prix saisi conservé TEL QUEL dans son unité d'origine (décision validée,
    Proposition A) : (prix en unités monétaires minimales par unité
    d'origine, unité d'origine KG/TONNE/ML/UNITE). Jamais converti, jamais
    arrondi ; refusé s'il n'est pas représentable exactement dans son unité
    d'origine (ex. « 2 500,5 DT/tonne » -> (2 500 500, "TONNE") ; « 2 500,5005
    DT/tonne » -> refusé).
    """
    _verifier_nature(m, PRIX)
    assert m.devise is not None
    unite = UNITE_VALORISATION_DU_PRIX[m.unite.split("/")[1]]
    return _entier_exact(m.valeur * _unites_minimales(m.devise), m.saisie), unite
