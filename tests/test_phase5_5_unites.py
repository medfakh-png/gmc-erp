"""
Tests Phase 5.5 — règle transversale « unité obligatoire à la saisie » et
masses linéiques validées (FP).

Règles validées testées :
- toute saisie de quantité, poids, longueur ou prix comporte son unité ; une
  saisie sans unité, ou ambiguë, est refusée ; l'unité saisie est conservée ;
- 1 tonne = 1 000 kg ; 5 DT HT/kg = 5 000 DT HT/tonne ; vente de 2 500 kg =
  2,5 tonnes à 5 000 DT/tonne = CA HT 12 500 DT — sans aucune différence de
  montant selon le chemin de conversion ;
- FP 120/30 = 28,8 kg/ml ; FP 130/30 = 31,2 kg/ml (28,8 pour FP 130/30
  annulé) ; FP 45/20 = 7,2 kg/ml ; une valeur différente du fichier MV est
  signalée, jamais fusionnée ni remplacée silencieusement ;
- arrondi monétaire : millime le plus proche, 0,5 vers le haut, une seule
  fois, sur le montant final (1 000,5 kg × 2,501 DT/kg -> 2 502,251 DT) ;
- tôle plane : volume (dm³) × 8 kg/dm³, dimensions converties en dm
  (3000 × 1500 × 1 mm -> 36 kg) ; dm <-> m, dm³ <-> m³.
"""

from __future__ import annotations

import decimal
import fractions

import pytest

from core import arrondi, masses_validees, unites
from core.erreurs import (
    ErreurMontantIncoherent,
    ErreurSaisieInvalide,
    ErreurUniteManquante,
    ErreurUniteValorisation,
)

D = decimal.Decimal


# ---------------------------------------------------------------------------
# Unité obligatoire, saisie conservée
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "texte,nature,valeur,unite",
    [
        ("2 500 kg", unites.MASSE, D("2500"), "kg"),
        ("2,5 tonnes", unites.MASSE, D("2.5"), "t"),
        ("5 DT/kg", unites.PRIX, D("5"), "TND/kg"),
        ("5 000 DT/tonne", unites.PRIX, D("5000"), "TND/t"),
        ("5 DT HT/kg", unites.PRIX, D("5"), "TND/kg"),
        ("12 m", unites.LONGUEUR, D("12"), "m"),
        ("10 pièces", unites.COMPTAGE, D("10"), "pièce"),
        ("12 500 DT", unites.MONTANT, D("12500"), "TND"),
        ("28,8 kg/ml", unites.MASSE_LINEIQUE, D("28.8"), "kg/m"),
        ("3,20 EUR/kg", unites.PRIX, D("3.20"), "EUR/kg"),
    ],
)
def test_lecture_des_saisies_avec_unite(texte, nature, valeur, unite):
    m = unites.lire(texte)
    assert (m.nature, m.valeur, m.unite) == (nature, valeur, unite)
    assert m.saisie == texte  # la saisie d'origine est conservée telle quelle
    assert m.trace()["saisie"] == texte


@pytest.mark.parametrize("saisie", ["2500", "2 500", "12,5", "  7 "])
def test_saisie_sans_unite_refusee(saisie):
    with pytest.raises(ErreurUniteManquante):
        unites.lire(saisie)


@pytest.mark.parametrize("valeur", [2500, 2.5, D("2500")])
def test_nombre_seul_refuse_par_les_services(valeur):
    with pytest.raises(ErreurUniteManquante):
        unites.exiger(valeur, unites.MASSE, "poids")
    with pytest.raises(ErreurUniteManquante):
        unites.mesure(valeur, None)
    with pytest.raises(ErreurUniteManquante):
        unites.mesure(valeur, "  ")


@pytest.mark.parametrize(
    "saisie",
    [
        "2.500 kg",  # point : milliers ou décimales ? ambigu
        "2.500,5 kg",
        "25 00 kg",
        "2 500 kgs",  # unité inconnue
        "5 DT TTC/kg",  # TTC : conversion impossible sans taux de TVA validé
        "-3 kg",
        "kg",
        "2,5 pièces",  # une quantité de pièces est entière
    ],
)
def test_saisie_ambigue_ou_invalide_refusee(saisie):
    with pytest.raises(ErreurSaisieInvalide):
        m = unites.lire(saisie)
        unites.en_pieces(m)  # n'est atteint que pour « 2,5 pièces »


def test_unite_de_nature_differente_refusee():
    with pytest.raises(ErreurSaisieInvalide):
        unites.exiger("12 m", unites.MASSE, "poids")
    with pytest.raises(ErreurSaisieInvalide):
        unites.en_kg(unites.lire("5 DT/kg"))


# ---------------------------------------------------------------------------
# kg <-> tonne, prix/kg <-> prix/tonne
# ---------------------------------------------------------------------------


def test_kg_tonne():
    assert unites.en_kg(unites.lire("2,5 t")) == D("2500")
    assert unites.en_kg(unites.lire("2 500 kg")) == D("2500")
    assert unites.en_tonnes(unites.lire("2 500 kg")) == D("2.5")
    assert unites.en_tonnes(unites.lire("1 kg")) == D("0.001")


def test_prix_kg_tonne():
    # 5 DT HT/kg = 5 000 DT HT/tonne (en millimes : 5 000 /kg = 5 000 000 /t).
    assert unites.prix_minor_par_kg(unites.lire("5 DT HT/kg")) == D("5000")
    assert unites.prix_minor_par_tonne(unites.lire("5 DT HT/kg")) == D("5000000")
    assert unites.prix_minor_par_kg(unites.lire("5 000 DT HT/tonne")) == D("5000")
    assert unites.prix_minor_par_tonne(unites.lire("5 000 DT/tonne")) == D("5000000")
    assert unites.prix_minor_par_kg(unites.lire("3,20 EUR/kg")) == D("320")  # centimes


def test_exemple_valide_vente_2500_kg():
    """2 500 kg = 2,5 t ; 5 DT/kg = 5 000 DT/t ; CA HT = 12 500 DT, quel que soit le chemin."""
    attendu = unites.montant_minor(unites.lire("12 500 DT"))
    assert attendu == 12_500_000  # millimes
    for masse in ("2 500 kg", "2,5 t"):
        for prix in ("5 DT HT/kg", "5 000 DT HT/tonne"):
            assert unites.montant_minor_masse_prix(unites.lire(masse), unites.lire(prix)) == attendu


def test_conversion_sans_aucune_difference_de_montant():
    """
    Masse en kg ou en t, prix au kg ou à la tonne : montant strictement
    identique (adapté à la règle d'arrondi validée : les montants non exacts
    sont désormais arrondis une seule fois, identiquement sur les 4 chemins).
    """
    for kg in ("0,001", "1", "2 500", "2 500,125", "18 437,5", "999,999"):
        for dt_par_kg in ("0,001", "1", "5", "4,875", "12,5"):
            masse_kg = unites.lire(f"{kg} kg")
            masse_t = unites.mesure(unites.en_tonnes(masse_kg), "t")
            prix_kg = unites.lire(f"{dt_par_kg} DT/kg")
            prix_t = unites.mesure(unites.prix_minor_par_tonne(prix_kg) / 1000, "DT/tonne")
            reference = unites.montant_minor_masse_prix(masse_kg, prix_kg)
            for masse, prix in ((masse_t, prix_t), (masse_kg, prix_t), (masse_t, prix_kg)):
                assert unites.montant_minor_masse_prix(masse, prix) == reference


def test_montant_arrondi_au_millime_une_seule_fois():
    """Règle validée : millime le plus proche, 0,5 vers le haut, une seule fois."""
    # Exemple validé : 1 000,5 kg × 2,501 DT/kg = 2 502,2505 DT -> 2 502,251 DT
    for masse in ("1 000,5 kg", "1,0005 t"):
        for prix in ("2,501 DT/kg", "2 501 DT/tonne"):
            assert (
                unites.montant_minor_masse_prix(unites.lire(masse), unites.lire(prix)) == 2_502_251
            )
    # 0,5 millime -> 1 (vers le haut) ; 0,4 -> 0 ; 0,6 -> 1 ; 1,5 -> 2
    for kg, attendu in (("0,5", 1), ("0,4", 0), ("0,6", 1), ("1,5", 2)):
        masse = unites.lire(f"{kg} kg")
        assert unites.montant_minor_masse_prix(masse, unites.lire("1 DT/tonne")) == attendu


def test_regle_d_arrondi_unique_et_reproductible():
    assert arrondi.arrondi_minor(D("2502250.5")) == 2_502_251
    assert arrondi.arrondi_minor(fractions.Fraction(4001, 4)) == 1000  # 1 000,25
    assert arrondi.arrondi_minor(fractions.Fraction(2001, 2)) == 1001  # 1 000,5 -> vers le haut
    assert arrondi.arrondi_minor(7) == 7
    with pytest.raises(TypeError):
        arrondi.arrondi_minor(0.5)  # jamais de flottant
    with pytest.raises(ValueError):
        arrondi.arrondi_minor(D("-0.5"))
    # Même implémentation dans le moteur CMP et dans les conversions d'unités.
    from db import valorisation

    assert (
        valorisation.montant_arrondi_minor(fractions.Fraction("1000.5"), 2501)
        == unites.montant_minor_masse_prix(unites.lire("1 000,5 kg"), unites.lire("2,501 DT/kg"))
        == 2_502_251
    )


def test_longueur_et_pieces():
    assert unites.en_metres(unites.lire("6000 mm")) == D("6")
    assert unites.en_metres(unites.lire("12 m")) == D("12")
    assert unites.en_pieces(unites.lire("10 pièces")) == 10
    assert (
        unites.montant_minor_pieces_prix(unites.lire("10 pièces"), unites.lire("5 DT/pièce"))
        == 50_000
    )


# ---------------------------------------------------------------------------
# Masses linéiques validées (FP)
# ---------------------------------------------------------------------------


def test_fp_120_30_egale_28_8_kg_ml():
    m = masses_validees.masse_lineique_validee("FP 120/30")
    assert unites.en_kg_par_metre(m) == D("28.8")


def test_fp_130_30_egale_31_2_kg_ml():
    m = masses_validees.masse_lineique_validee("FP 130/30")
    assert unites.en_kg_par_metre(m) == D("31.2")
    assert unites.en_kg_par_metre(m) != D("28.8")  # ancienne valeur annulée


def test_fp_45_20_egale_7_2_kg_ml_et_anciennes_valeurs_jamais_reintroduites():
    assert unites.en_kg_par_metre(masses_validees.masse_lineique_validee("FP 45/20")) == D("7.2")
    valeurs = {
        unites.en_kg_par_metre(m) for m in masses_validees.MASSES_LINEIQUES_VALIDEES.values()
    }
    assert D("4.07") not in valeurs and D("283.8") not in valeurs


def test_valeur_differente_du_fichier_mv_signalee_jamais_remplacee():
    ecart = masses_validees.comparer_avec_liste_mv("FP 120/30", unites.lire("283,8 kg/m"))
    assert ecart == {
        "designation": "FP 120/30",
        "valeur_validee_kg_m": "28.8",
        "valeur_liste_mv_kg_m": "283.8",
        "action": "ECART_SIGNALE_AUCUNE_MODIFICATION",
    }
    ecart_130 = masses_validees.comparer_avec_liste_mv("FP 130/30", unites.lire("30,6 kg/m"))
    assert ecart_130 is not None and ecart_130["valeur_validee_kg_m"] == "31.2"
    # La valeur validée n'a pas été touchée par la comparaison.
    assert unites.en_kg_par_metre(masses_validees.masse_lineique_validee("FP 120/30")) == D("28.8")
    assert masses_validees.comparer_avec_liste_mv("FP 120/30", unites.lire("28,8 kg/ml")) is None
    assert masses_validees.comparer_avec_liste_mv("FP 20/3", unites.lire("0,471 kg/m")) is None


# ---------------------------------------------------------------------------
# Unités de prix de valorisation (règle « unité du CMP », finalisation 5.5)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "texte,unite_valorisation,attendu",
    [
        ("2,5 DT/kg", "KG", 2500),
        ("2 500 DT/tonne", "KG", 2500),  # seule conversion admise : kg <-> t
        ("2,5 DT/kg", "TONNE", 2_500_000),
        ("2 500 DT/t", "TONNE", 2_500_000),
        ("12 DT/ml", "ML", 12_000),
        ("12 DT/m", "ML", 12_000),
        ("30 DT/pièce", "UNITE", 30_000),
        ("30 DT/unité", "UNITE", 30_000),
        ("5,20 EUR/kg", "KG", 520),
    ],
)
def test_prix_dans_l_unite_de_valorisation(texte, unite_valorisation, attendu):
    assert (
        unites.prix_minor_en_unite_valorisation(unites.lire(texte), unite_valorisation) == attendu
    )


@pytest.mark.parametrize(
    "texte,unite_valorisation",
    [
        ("30 DT/pièce", "KG"),  # il faudrait le poids du lot : conversion implicite refusée
        ("30 DT/pièce", "TONNE"),
        ("12 DT/ml", "UNITE"),  # il faudrait la longueur du lot
        ("12 DT/ml", "KG"),
        ("2,5 DT/kg", "ML"),
        ("2,5 DT/kg", "UNITE"),
    ],
)
def test_prix_hors_unite_de_valorisation_refuse(texte, unite_valorisation):
    with pytest.raises(ErreurUniteValorisation, match="aucune conversion implicite"):
        unites.prix_minor_en_unite_valorisation(unites.lire(texte), unite_valorisation)


def test_prix_converti_non_exact_refuse():
    # 2 500,0005 DT/t = 2 500,0005 millimes/kg : pas un entier de millimes -> refusé, pas arrondi
    with pytest.raises(ErreurMontantIncoherent):
        unites.prix_minor_en_unite_valorisation(unites.lire("2 500,0005 DT/t"), "KG")
    with pytest.raises(ErreurUniteValorisation, match="inconnue"):
        unites.prix_minor_en_unite_valorisation(unites.lire("2,5 DT/kg"), "M2")


def test_unites_et_centimetres_reconnus():
    assert (unites.lire("10 unités").nature, unites.en_pieces(unites.lire("10 unités"))) == (
        unites.COMPTAGE,
        10,
    )
    assert unites.en_metres(unites.lire("150 cm")) == D("1.5")
    assert unites.lire("12 DT/ml").unite == "TND/ml"
    assert unites.lire("30 DT/unité").unite == "TND/pièce"


# ---------------------------------------------------------------------------
# Tôle plane : Poids (kg) = Volume (dm³) × 8 kg/dm³, dimensions converties en dm
# ---------------------------------------------------------------------------


def test_tole_exemple_de_controle_36_kg():
    """Volume (dm³) × 8 kg/dm³ : 30 dm × 15 dm × 0,01 dm = 4,5 dm³ ; × 8 = 36 kg."""
    detail = masses_validees.calcul_poids_tole_plane("3000 mm", "1500 mm", "1 mm")
    assert detail["dimensions_dm"] == {"longueur": "30", "largeur": "15", "epaisseur": "0.01"}
    assert detail["volume_dm3"] == D("4.5")
    assert detail["densite_kg_dm3"] == D(8)
    assert detail["poids_kg"] == D(36)
    assert "resultat_formule_g" not in detail  # aucun résultat intermédiaire « en grammes »
    assert detail["saisies"] == {"longueur": "3000 mm", "largeur": "1500 mm", "epaisseur": "1 mm"}
    assert unites.en_kg_par_dm3(masses_validees.DENSITE_TOLE_PLANE) == D(8)  # jamais 7,85


@pytest.mark.parametrize(
    "longueur,largeur,epaisseur,poids_kg",
    [
        ("2000 mm", "1000 mm", "2 mm", D(32)),  # 20 × 10 × 0,02 = 4 dm³ × 8 = 32 kg
        ("6000 mm", "1500 mm", "3 mm", D(216)),  # 60 × 15 × 0,03 = 27 dm³ × 8 = 216 kg
        ("2500 mm", "1250 mm", "1,5 mm", D("37.5")),  # 25 × 12,5 × 0,015 = 4,6875 dm³
        ("1000 mm", "1000 mm", "0,5 mm", D(4)),  # 10 × 10 × 0,005 = 0,5 dm³ × 8 = 4 kg
    ],
)
def test_tole_autres_dimensions(longueur, largeur, epaisseur, poids_kg):
    assert masses_validees.poids_tole_plane_kg(longueur, largeur, epaisseur) == poids_kg


def test_tole_conversions_mm_cm_m():
    assert unites.en_millimetres(unites.lire("1 m")) == D(1000)  # 1 000 mm = 1 m
    assert unites.en_millimetres(unites.lire("100 cm")) == D(1000)  # 100 cm = 1 m
    assert unites.en_millimetres(unites.lire("1 mm")) == D(1)
    for dimensions in (
        ("3000 mm", "1500 mm", "1 mm"),
        ("3 m", "1,5 m", "0,001 m"),
        ("300 cm", "150 cm", "0,1 cm"),
        ("30 dm", "15 dm", "0,01 dm"),
        ("3 m", "1500 mm", "0,1 cm"),
    ):
        assert masses_validees.poids_tole_plane_kg(*dimensions) == D(36), dimensions


def test_conversions_vers_le_decimetre_et_volumes():
    # mm -> dm (100 mm = 1 dm), cm -> dm (10 cm = 1 dm), m -> dm (1 m = 10 dm)
    assert unites.en_decimetres(unites.lire("3000 mm")) == D(30)
    assert unites.en_decimetres(unites.lire("1 mm")) == D("0.01")
    assert unites.en_decimetres(unites.lire("100 mm")) == D(1)
    assert unites.en_decimetres(unites.lire("150 cm")) == D(15)
    assert unites.en_decimetres(unites.lire("3 m")) == D(30)
    # dm -> m (÷ 10) ; m -> dm (× 10)
    assert unites.en_metres(unites.lire("30 dm")) == D(3)
    assert unites.en_decimetres(unites.lire("1 m")) == D(10)
    # dm³ -> m³ (÷ 1 000) ; m³ -> dm³ (× 1 000)
    assert unites.en_m3(unites.lire("4,5 dm³")) == D("0.0045")
    assert unites.en_dm3(unites.lire("0,0045 m³")) == D("4.5")
    assert unites.en_dm3(unites.lire("1 m3")) == D(1000)
    with pytest.raises(ErreurUniteManquante):
        unites.exiger("4,5", unites.VOLUME, "volume")


def test_tole_precision_conservee_avant_l_arrondi_final():
    # 1234 × 567 × 1,5 mm = 12,34 × 5,67 × 0,015 dm = 1,049517 dm³ -> 8,396136 kg, exact
    detail = masses_validees.calcul_poids_tole_plane("1234 mm", "567 mm", "1,5 mm")
    assert detail["volume_dm3"] == D("1.049517")
    assert detail["poids_kg"] == D("8.396136")  # aucun arrondi intermédiaire
    # Valorisée à 2,501 DT/kg : 8,396136 × 2 501 = 20 998,736136 millimes -> 20 999 (une fois)
    masse = unites.mesure(detail["poids_kg"], "kg")
    assert unites.montant_minor_masse_prix(masse, unites.lire("2,501 DT/kg")) == 20_999
    # (arrondir le poids d'abord à 8,396 kg aurait donné 20 998 : sous-calcul arrondi, interdit)
    assert unites.montant_minor_masse_prix(unites.lire("8,396 kg"), unites.lire("2,501 DT/kg")) == (
        20_998
    )


def test_tole_unite_obligatoire_et_dimension_invalide():
    with pytest.raises(ErreurUniteManquante):
        masses_validees.poids_tole_plane_kg(3000, "1500 mm", "1 mm")
    with pytest.raises(ErreurUniteManquante):
        masses_validees.poids_tole_plane_kg("3000", "1500 mm", "1 mm")
    with pytest.raises(ErreurSaisieInvalide):
        masses_validees.poids_tole_plane_kg("3000 mm", "1500 kg", "1 mm")  # pas une longueur
    with pytest.raises(ErreurSaisieInvalide):
        masses_validees.poids_tole_plane_kg("3000 mm", "1500 mm", "0 mm")
    with pytest.raises(ErreurSaisieInvalide):
        masses_validees.poids_tole_plane_kg("3.000 mm", "1500 mm", "1 mm")  # ambigu


def test_tole_resultat_coherent_en_kg():
    poids = masses_validees.poids_tole_plane_kg("3000 mm", "1500 mm", "1 mm")
    masse = unites.mesure(poids, "kg")
    assert unites.en_kg(masse) == D(36)
    assert unites.en_tonnes(masse) == D("0.036")  # 1 t = 1 000 kg
    # Contrôle physique : 3 m × 1,5 m × 0,001 m = 0,0045 m³ × 8 000 kg/m³ = 36 kg
    assert D(3) * D("1.5") * D("0.001") * D(8000) == poids
