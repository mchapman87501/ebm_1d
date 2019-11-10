#!/usr/bin/env python3
"""
Provides a way to solve iteratively for latitudinal temperature.
"""

from dataclasses import dataclass
import numpy as np

from .earth_model import EarthModel


class Error(Exception):
    pass


@dataclass(frozen=True)
class Solution:
    temps: np.ndarray
    albedos: np.ndarray
    avg: float


class TempSolver:
    def __init__(
        self, earth_model: EarthModel, lat_transfer_coeff: float = 7.6
    ) -> None:
        self._em = earth_model
        # Latitude band heat transfer coefficient, W/m**2:
        self._lat_transfer_coeff = lat_transfer_coeff

    def solve(
        self, solar_mult: float, temp: np.ndarray, max_iter: int = 100
    ) -> Solution:
        """
        Solve for temperatures and albedos by latitude band.
        Return the computed average planetary temperature.
        """
        threshold = 0.05  # We're done when max_temp_diff reaches this thresh.
        m_insol = solar_mult * self._em.insol_by_lat
        f = self._lat_transfer_coeff
        a = 204.0  # Radiative heat-loss coefficient, intercept
        b = 2.17  # Radiative heat-loss coefficient, slope
        denom = b + f

        for i in range(max_iter):
            temp_old = temp
            albedo = self._get_albedo(temp)
            temp_avg = sum(self._em.lats_frac * temp)
            temp = (m_insol * (1.0 - albedo) + f * temp_avg - a) / denom
            max_temp_diff = max(abs(temp_old - temp))

            if max_temp_diff <= threshold:
                return Solution(temp, albedo, temp_avg)
        raise Error(f"Failed to converge after {max_iter} iterations.")

    def _get_albedo(self, temp: np.ndarray) -> np.ndarray:
        ice = 0.6
        land = 0.3
        t_crit = -10.0  # Critical temp, C, below which all is ice

        result = np.full_like(temp, ice)
        result[temp > t_crit] = land
        return result
