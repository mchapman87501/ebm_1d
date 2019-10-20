#!/usr/bin/env python3
"""
"""

from .insol import *
from .insol_params import *
from .earth_geom import *


def test_effective_solar_constant() -> None:
    # How is S measured?  Scientists had a good estimate of its value
    # long before we could send any objects/instruments above our
    # atmosphere.
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
