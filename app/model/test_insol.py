#!/usr/bin/env python3
"""
Someday this will provide actual unit tests for the insol module.
"""

from .insol import Insol
from .insol_params import InsolParams
from .earth_geom import EarthGeom


def test_effective_solar_constant() -> None:
    ip = InsolParams()
    eg = EarthGeom(9)
    s = ip.solar_const
    ins = Insol(ip, eg)
    s_effective = ins._solar_constant
    print("Ratio of s to s_effective:", s / s_effective)
    print("Insolation by latitude band:", ins._insol_by_lat)
    print(
        "ia - Insolation averaged over latitude bands, and years:",
        ins._avg_insol,
    )
