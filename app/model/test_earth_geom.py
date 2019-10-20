#!/usr/bin/env python3

from .earth_geom import EarthGeom


def test_ctor() -> None:
    num_bands = 9
    eg = EarthGeom(num_bands)
    assert len(eg.lats_rad) == num_bands
    assert len(eg.lats_frac) == num_bands
