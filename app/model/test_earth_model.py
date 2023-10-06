#!/usr/bin/env python3
# type: ignore

import pytest

from .earth_model import EarthModel


def test_ctor() -> None:
    num_bands = 9
    eg = EarthModel(num_bands)
    assert len(eg.lats_rad) == num_bands
    assert len(eg.lats_frac) == num_bands


num_bands_data = [9, 18, 36]


@pytest.mark.parametrize("num_bands", num_bands_data)
def test_lats_frac(num_bands: int) -> None:
    eg = EarthModel(num_bands)
    assert eg.lats_frac.sum() == pytest.approx(1)


@pytest.mark.parametrize("num_bands", num_bands_data)
def test_lats_height(num_bands: int) -> None:
    eg = EarthModel(num_bands)
    # The normalized latitude band heights (ortho projection)
    # should sum to unit radius.
    assert eg.lats_height.sum() == pytest.approx(1)


@pytest.mark.parametrize("num_bands", num_bands_data)
def test_effective_solar_constant(num_bands) -> None:
    eg = EarthModel(num_bands)
    assert float(eg.insol_by_lat.sum()) == pytest.approx(1370.0 / 4)
