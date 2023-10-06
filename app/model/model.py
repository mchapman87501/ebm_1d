#!/usr/bin/env python3
"""
This is a simple energy balance model based on equation 3.13, and
a matlab implementation of the program associated with section 3.4 of
"A Climate Modelling Primer", 1st Edition, 1987,
by A. Henderson-Sellers and K. McGuffie.
Matlab implementation was written by David Holland, 2002/02.
"""

import typing as tp
from dataclasses import dataclass

import numpy as np

from .earth_model import EarthModel
from .temp_solver import Solution, TempSolver


@dataclass
class AvgTempResult:
    delta: float
    solar_mult: float
    solution: Solution


@dataclass
class ResultSeries:
    summary: str
    results: list[AvgTempResult]


ResultGen = tp.Generator[AvgTempResult, None, None]


# noinspection PyMethodMayBeStatic
class Model:
    def gen_temps(
        self,
        min_solar_mult: float,
        max_solar_mult: float,
        initial_gat: float,
        num_lat_zones: int,
        lat_transfer_coeff: float = 7.6,
    ) -> ResultGen:
        """
        Initialize a new instance.
        The model generates global average temperature and lat band temps
        for a range of solar multiples, for a given number of latitude zones,
        for a given lateral head transfer coefficient.
        """
        em = EarthModel(num_lat_zones)
        solver = TempSolver(em, lat_transfer_coeff)

        gat0 = np.full(num_lat_zones, initial_gat)
        a0 = np.full(num_lat_zones, 0.0)

        num_solar_mults = 10
        delta = (max_solar_mult - min_solar_mult) / num_solar_mults

        ascending = np.arange(min_solar_mult, max_solar_mult, delta)
        descending = np.arange(max_solar_mult, min_solar_mult, -delta)

        solution = Solution(gat0, a0, 0.0)  # Starting temps
        for mult in ascending:
            solution = solver.solve(mult, solution.temps)
            yield AvgTempResult(delta, mult, solution)

        for mult in descending:
            solution = solver.solve(mult, solution.temps)
            yield AvgTempResult(-delta, mult, solution)
