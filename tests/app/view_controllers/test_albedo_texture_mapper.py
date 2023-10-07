from pathlib import Path

import numpy as np
import pytest
from PySide6.QtGui import QImage

from app.view_controllers.albedo_texture_mapper import AlbedoTextureMapper

ATM1TestCases = list[tuple[list[float], set[int]]]


class _TestedAlbedoTextureMapper(AlbedoTextureMapper):
    def working_dir(self) -> Path:
        return self._working_dir


def atm1_cases() -> ATM1TestCases:
    """Ruff thinks this test fixture needs a docstring."""
    alb_range = [x / 100.0 for x in range(100)]
    alb_expected = {int(255 * x) for x in alb_range}
    return [
        ([0.3, 0.5, 0.6], {76, 127, 153}),
        ([0.5] * 100, {127}),
        (alb_range, alb_expected),
    ]


@pytest.mark.parametrize("albedos_in, expected", atm1_cases())
def test_atm1(albedos_in, expected) -> None:
    """Generate and display some simple albedo images."""
    m = _TestedAlbedoTextureMapper()

    img_path = m.img_path_from_albedos(np.array(albedos_in))

    img = QImage(str(img_path))
    # img height should be > len(albedos).
    # albedos has values extending from equator to one
    # pole, with one value for each latitude band.
    # img depicts albedos from pole to pole, and the
    # number of pixels devoted to each latitude band is
    # proportional to the extent of that band along the
    # rotational axis.  (Bands near equator should have
    # more pixels than bands near poles.)
    assert img.height() >= len(albedos_in)

    # Verify that the image pixel intensities are as
    # expected.
    actual = set()
    for y in range(img.height()):
        first_pix = img.pixelColor(0, y)
        assert first_pix.red() == first_pix.green() == first_pix.blue()
        actual.add(first_pix.red())
        # Verify that the color bands are vertical.
        for x in range(1, img.width()):
            pix = img.pixelColor(x, y)
            assert pix == first_pix

    assert actual.issubset(expected)

    # Verify cleanup
    assert m.working_dir().is_dir()

    # Disabled - cannot guarantee m.__del__ completes before
    # the cleanup test.
    # del m
