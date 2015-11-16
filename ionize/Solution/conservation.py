from __future__ import division
import warnings
from numpy import mean
from ..constants import lpm3


def kohlrausch(self):
    """Return the Kohlrausch regulating function (KRF) value of a solution.

    Throw a warning if the ions in the solution are not near fully ionized.
    """
    KRF = 0

    for ion, c in zip(self.ions, self.concentrations):
        z_eff = (mean([z*f for z, f in
                 zip(ion.valence, ion.ionization_fraction())]))
        KRF += abs(z_eff) * c * lpm3 / ion.mobility()
        if max(ion.ionization_fraction()) < .9:
            warnings.warn('ions are not fully ionized. KRF is a poor approx.')

    return KRF


def alberty(self):
    """Return the Alberty conservation function value of a solution.

    Throw a warning if the ions are not univalent, or if water dissociation
    cannot be neglected.
    """
    al = 0

    for ion, c in zip(self.ions, self.concentrations):
        if len(ion.reference_mobility) == 1:
            al += c * lpm3 / abs(ion.actual_mobility()[0])
        else:
            f = ion.ionization_fraction()
            if max(f)/sum(f) < .9:
                warnings.warn('Ion not in single valance. Alberty invalid.')
            elif abs(ion.valence[f.argmax()]) != 1:
                warnings.warn('Ion valance is not 1. Alberty invalid.')
            al += c * lpm3 / abs(ion.actual_mobility()[f.argmax()])

    return al


def jovin(self):
    """Return the Jovin conservation function value of a solution.

    Throw a warning if the ions are not univalent, or if water dissociation
    cannot be neglected.
    """
    jov = 0

    for ion, c in zip(self.ions, self.concentrations):
        if len(ion.reference_mobility) == 1:
            jov += c * ion.valence[0]
        else:
            f = ion.ionization_fraction()
            if max(f)/sum(f) < .9:
                warnings.warn('Ion not in single valance. Jovin invalid.')
            # elif abs(ion.valence[f.index(max(f))]) != 1:
            elif abs(ion.valence[f.argmax()]) != 1:
                warnings.warn('Ion valance is not 1. Jovin invalid.')
            jov += c * ion.valence[f.argmax()]

    return jov


def gas(self):
    alberty = self.alberty()
    jovin = self.jovin()
    gas = [alberty - jovin / self._hydronium.mobility(self.pH),
           alberty - jovin / self._hydroxide.mobility(self.pH)]
    return tuple(gas)
