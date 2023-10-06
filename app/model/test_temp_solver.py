#!/usr/bin/env python3

import numpy as np
import pytest

from .earth_model import EarthModel
from .temp_solver import Error, TempSolver


def get_t_avg(
    solver: TempSolver, smults: np.ndarray, temps: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    gats: list[float] = []
    for sm in smults:
        solution = solver.solve(sm, temps)
        gats.append(solution.avg)
        temps = solution.temps
    # Return the sequence of global avg temps, and the final temperatures.
    return (np.array(gats), temps)


def test_default_scenario() -> None:
    num_lat_zones = 9
    eg = EarthModel(num_lat_zones)
    solver = TempSolver(eg)

    temps = np.full(num_lat_zones, -60.0)

    # Verify that the model demonstrates hysteresis in the
    # expected range of solar multipliers, when the
    # latitudinal temperatures from each solve are used as
    # initial conditions for the next solve.
    sm_rising = np.arange(0.4, 10.0, 0.5)
    sm_falling = np.arange(10.0, 0.4, -0.5)

    gat_rising, temps = get_t_avg(solver, sm_rising, temps)
    gat_falling, temps = get_t_avg(solver, sm_falling, temps)

    dgat_rising = np.diff(gat_rising)
    # There should be only one "step" in the
    # sequence of rising temperatures, and the change
    # in temperature should always be > 0.
    dgat_ln = np.log10(dgat_rising)
    assert len(dgat_ln[dgat_ln > 1]) == 1

    dgat_falling = np.diff(gat_falling)
    dgat_ln = np.log10(np.abs(dgat_falling))
    assert 2 >= len(dgat_ln[dgat_ln > 1.0]) >= 1

    # This test points the way toward auto-ranging - automatically
    # determining the min/max solar multiplier in which hysteresis
    # manifests.


def test_divergent() -> None:
    num_lat_zones = 360
    eg = EarthModel(num_lat_zones)
    solver = TempSolver(eg)

    temps = np.full(num_lat_zones, 200.0)
    with pytest.raises(Error):
        solver.solve(0.0, temps, max_iter=5)
