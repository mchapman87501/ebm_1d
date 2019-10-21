#!/usr/bin/env python3

"""
Determines insolation as a function of latitude band.

The original matlab code on which this module is based seems to be
answering the following question:
For a given point on the equator of an idealized earth, how much
solar power does it receive, when one averages over a whole year?

The calculation assumes many simplifications.  For starters it assumes
Earth's rotational axis is exactly ortho to the orbital plane.
And it ignores the effects of latitude, averaging only for a point on the
surface which directly faces the sun for an instant of each day.

"""

import math
import numpy as np

from .earth_geom import EarthGeom
from .insol_params import InsolParams

D2R = math.pi / 180.0


class Insol:
    """
    Insol calculates insolation per latitude band.
    """

    def __init__(self, params: InsolParams, earth_geom: EarthGeom) -> None:
        self._params = params
        self._eg = earth_geom

        self._solar_constant = self._calc_solar_constant()
        self._insol_by_lat = self._unnormed_total_annual_insolation()

    def _calc_solar_constant(self) -> float:
        # Ratio of cross-sectional area of a sphere to surface area of
        # a sphere is (π * r**2) / (4 * π * r**2)
        return self._params.solar_const / 4.0

    def _unnormed_total_annual_insolation(self) -> np.ndarray:
        # Accumulate insolation throughout a year.
        days_in_year = self._params.days_in_yr
        year_per_day = 1.0 / days_in_year
        max_tilt = self._params.max_tilt * math.pi / 180.0
        max_zenith = math.pi / 2.0
        lats_rads = self._eg.lats_rad
        lats_frac = self._eg.lats_frac  # Fraction of total area by band
        year_fract = year_per_day
        insolation = np.zeros(len(lats_rads))
        for i in range(int(days_in_year)):
            tilt = max_tilt * math.cos(2.0 * math.pi * year_fract)
            day_insol = 0.0
            for j, (lrads, larea) in enumerate(zip(lats_rads, lats_frac)):
                # Add the fraction of available insolation received
                # by this band given its axial tilt.  Double the fraction
                # on the assumption that lats_rads covers only one hemisphere.
                # Assume the asymmetry error (northern hemi gets more/less
                # light than southern) is corrected by accumulating over a
                # whole year of tilt.
                zenith = min(lrads + tilt, max_zenith)
                insol_fract = max(0.0, larea * math.cos(zenith))
                day_insol += insol_fract
                insolation[j] += insol_fract
            year_fract += year_per_day

        # Average insolation across the year, per latitude band.
        insolation *= self._solar_constant / days_in_year
        return insolation

    def get_insolation(self) -> np.ndarray:
        """Get the average insolation over a year, by latitude band."""
        return self._insol_by_lat  # Read-only, please
