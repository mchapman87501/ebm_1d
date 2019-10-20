#!/usr/bin/env python3
import numpy as np

from .temp_solver import TempSolver
from .earth_geom import EarthGeom


def test_default_scenario() -> None:
    num_lat_zones = 9
    eg = EarthGeom(num_lat_zones)
    solver = TempSolver(eg)

    temps = np.full(num_lat_zones, -60.0)
    solar_mult = 0.6
    solution = solver.solve(solar_mult, temps)
    print("Average temp:", solution.avg)
    print("Initial temps:", temps)
    print("Final temps:", solution.temps)
