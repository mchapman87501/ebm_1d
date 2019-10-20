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
        self._avg_insol = sum(self._eg.lats_frac * self._insol_by_lat)

    def _calc_solar_constant(self) -> float:
        return self._params.solar_const / 4.0
        # Ratio of cross-sectional area of a sphere to surface area of
        # a sphere is (π * r**2) / (4 * π * r**2)

    def _literal_translation_calc_solar_constant(self) -> float:
        """
        I'm not sure of the purpose of this calculation, taken from
        the matlab code.  It tries to average insolation over a
        cylinder - not even a perfect sphere.  It repeats essentially
        the same calculation around all 360 degrees of the cyliner, 24
        times - basically adding a small starting offset,
        corresponding loosely to the noon angular offset of the sun.
        I suspect an equivalent analytic solution would say:
        if the earth were a perfect sphere, it would intercept an
        amount of solar power proportional to its cross-sectional
        area: π*R**2.  Assuming a constant rate of rotation of
        360°/day, that "pressure" - 
        S ((joules / sec) / m**2) * π * R**2 
            * (24 * 60 * 60) secs/day
        - would be distributed evenly across the whole area of the
        - sphere: 4 * π * R**2.
        So, the effective solar constant would be S / 4.

        As it turns out, this function computes something quite different:
        the calculated solar constant as returned by this
        code is S / π.  (?!)
        
        """
        hours_in_day = self._params.hrs_in_day
        zonal_deg = self._params.zonal_deg
        solar_const = self._params.solar_const

        sum_insol = 0.0
        for hr in np.arange(hours_in_day):
            # Noon angle is effectively a fraction of a revolution -
            # 2π radians - expressed in degrees.
            noon_angle = zonal_deg * hr / hours_in_day
            for longitude in np.arange(zonal_deg):
                sun_angle = D2R * (longitude - noon_angle)
                sum_insol += max(0.0, math.cos(sun_angle))
        result = sum_insol * solar_const / (hours_in_day * zonal_deg)
        print("Solar const:", solar_const)
        print("Calc'd solar const:", result)
        # The ratio of solar_const to this result is ... PI?!
        # That's what you'd expect, analytically, when you are
        # computing effective solar constant incident on a cylinder,
        # rather than a sphere:
        # A cylinder with axis ortho to the plane of incident radiation
        # has cross-sectional area 2 * r * h, where r is the cylinder's
        # radius and h is its height.
        # The surface area of the cylinder, ignoring its end "caps"
        # (they are ignored in this algorithm)
        # is 2 * π * r * h.  So the ratio of cap-less area
        # to cross-section is π.
        return result

    def _unnormed_total_annual_insolation(self) -> np.ndarray:
        # Accumulate normalized insolation throughout a year.
        days_in_year = self._params.days_in_yr
        year_per_day = 1.0 / days_in_year
        max_tilt = self._params.max_tilt * math.pi / 180.0
        max_zenith = math.pi / 2.0
        lats_rads = self._eg.lats_rad

        year_fract = year_per_day
        insolation = np.zeros(len(lats_rads))
        for i in range(int(days_in_year)):
            tilt = max_tilt * math.cos(2.0 * math.pi * year_fract)
            for j, lat_rads in enumerate(lats_rads):
                zenith = min(lat_rads + tilt, max_zenith)
                insolation[j] += math.cos(zenith)
            year_fract += year_per_day

        # Average insolation across the year, per latitude band.
        insolation *= self._solar_constant / days_in_year
        return insolation

    def get_insolation(self) -> np.ndarray:
        """Get the average insolation over a year, by latitude band."""
        return self._insol_by_lat  # Read-only, please
