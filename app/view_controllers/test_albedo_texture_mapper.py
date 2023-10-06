#!/usr/bin/env python3

import numpy as np
import pytest
from PIL import Image

from .albedo_texture_mapper import AlbedoTextureMapper

ATM1TestCases = list[tuple[list[float], set[int]]]


@pytest.fixture()  # type: ignore
def atm1_cases() -> ATM1TestCases:
    alb_range = [x / 100.0 for x in range(100)]
    alb_expected = {int(255 * x) for x in alb_range}
    return [
        ([0.3, 0.5, 0.6], {76, 127, 153}),
        ([0.5] * 100, {127}),
        (alb_range, alb_expected),
    ]


def test_atm1(atm1_cases) -> None:  # type: ignore
    """Generate and display some simple albedo images."""
    m = AlbedoTextureMapper()

    for albedos, expected in atm1_cases:
        albedos = np.array(albedos)
        img_path = m.img_from_albedos(albedos)
        img = Image.open(img_path)
        # img height should be > len(albedos).
        # albedos has values extending from equator to one
        # pole, with one value for each latitude band.
        # img depicts albedos from pole to pole, and the
        # number of pixels devoted to each latitude band is
        # proportional to the extent of that band along the
        # rotational axis.  (Bands near equator should have
        # more pixels than bands near poles.)
        actual = set(img.getdata())
        assert actual.issubset(expected)
        assert len(actual) > 0

    # Whitebox - verify cleanup
    wd = m._working_dir
    assert wd.is_dir()

    # Disabled - cannot guarantee m.__del__ completes before
    # the cleanup test.
    # del m
