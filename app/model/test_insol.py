#!/usr/bin/env python3
"""
Someday this will provide actual unit tests for the insol module.
"""

from .insol import Insol
from .insol_params import InsolParams
from .earth_geom import EarthGeom

import pytest


def test_effective_solar_constant() -> None:
    ip = InsolParams()
    eg = EarthGeom(9)
    s = ip.solar_const
    ins = Insol(ip, eg)
    # White-box testing:
    s_effective = ins._solar_constant
    ratio = s / s_effective
    assert ratio == pytest.approx(4)

    print("Avg insolation by latitude band:", ins.get_insolation())
    assert ins.get_insolation().mean() <= ins._solar_constant
