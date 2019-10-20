#!/usr/bin/env python3
"""
Provides a way to solve iteratively for latitudinal temperature.
"""

from dataclasses import dataclass
import numpy as np
import typing as tp

from .insol_params import InsolParams
from .earth_geom import EarthGeom
from .insol import Insol


class Error(Exception):
    pass


@dataclass(frozen=True)
class HeatParams:
    F: float = 7.6  # Transport coefficient, W/m**2
    A: float = 204.0  # Radiative heat-loss coefficient, intercept
    B: float = 2.17  # Radiative heat-loss coefficient, slope

    albedo_ice: float = 0.6
    albedo_land: float = 0.3
    temp_critical: float = -10.0  # Critical temp, C, below which all is ice


@dataclass(frozen=True)
class Solution:
    temps: np.ndarray
    albedos: np.ndarray
    avg: float


class TempSolver:
    def __init__(
        self,
        earth_geom: EarthGeom,
        insol_params: tp.Optional[InsolParams] = None,
        heat_params: tp.Optional[HeatParams] = None,
    ) -> None:
        self._eg = earth_geom
        self._hp = heat_params or HeatParams()
        self._ip = insol_params or InsolParams()
        self._insol = Insol(self._ip, self._eg)

    def solve(
        self, solar_mult: float, temp: np.ndarray, max_iter: int = 100
    ) -> Solution:
        """
        Solve for temperatures and albedos by latitude band.
        Return the computed average planetary temperature.
        """
        threshold = 0.05  # We're done when max_temp_diff reaches this thresh.
        assert len(temp) == self._eg.num_zones
        insolation = self._insol.get_insolation()
        f = self._hp.F
        a = self._hp.A
        b = self._hp.B

        for i in range(max_iter):
            temp_old = temp

            # Depending on previous temp, albedo is either land or ice:
            albedo = np.empty(temp.shape)
            albedo[:] = self._hp.albedo_ice
            albedo[temp_old > self._hp.temp_critical] = self._hp.albedo_land

            temp_avg = sum(self._eg.lats_frac * temp)
            temp = (
                solar_mult * insolation * (1.0 - albedo) + f * temp_avg - a
            ) / (b + f)
            max_temp_diff = max(abs(temp_old - temp))

            if max_temp_diff <= threshold:
                return Solution(temp, albedo, temp_avg)
        raise Error(f"Failed to converge after {max_iter} iterations.")
