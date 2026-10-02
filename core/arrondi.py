"""
Règle d'arrondi monétaire (Phase 5.5 — règle définitive validée).

Règle validée : lorsqu'un calcul monétaire ne tombe pas exactement au
millime, le système arrondit au millime le plus proche, 0,5 millime étant
arrondi vers le haut, et ceci UNE SEULE FOIS par montant calculé :
- aucun arrondi silencieux à plusieurs niveaux ;
- aucun sous-calcul n'est arrondi : la précision interne est conservée
  (arithmétique décimale / fractionnaire exacte) jusqu'au montant final ;
- l'arrondi s'applique au montant monétaire final concerné ;
- la règle est identique et reproductible dans tous les moteurs : ce module
  est l'UNIQUE implémentation, utilisée par `core/unites.py` et
  `db/valorisation.py`.

Exemple validé : 1 000,5 kg × 2,501 DT/kg = 2 502,2505 DT -> 2 502,251 DT.

Les montants sont exprimés en unités monétaires minimales (millime pour
TND, centime pour EUR/USD — représentation validée en Phase 4.1) : arrondir
« au millime » d'un montant TND revient à arrondir à l'unité minimale.
"""

from __future__ import annotations

import decimal
import fractions
import typing


def arrondi_minor(valeur: typing.Union[int, decimal.Decimal, fractions.Fraction]) -> int:
    """
    Montant final exact (en unités monétaires minimales, éventuellement
    fractionnaire) -> entier le plus proche, 0,5 arrondi vers le haut.
    Arithmétique entière pure (aucun flottant). Les montants arrondis par le
    système sont toujours positifs ou nuls ; une valeur négative est refusée
    plutôt que de supposer un sens d'arrondi.
    """
    if isinstance(valeur, bool) or not isinstance(
        valeur, (int, decimal.Decimal, fractions.Fraction)
    ):
        raise TypeError(f"Montant à arrondir invalide : {valeur!r}.")
    exacte = fractions.Fraction(valeur)
    if exacte < 0:
        raise ValueError(f"Montant négatif à arrondir : {valeur!r} (non pris en charge).")
    quotient, reste = divmod(exacte.numerator, exacte.denominator)
    if reste * 2 >= exacte.denominator:
        quotient += 1
    return quotient
