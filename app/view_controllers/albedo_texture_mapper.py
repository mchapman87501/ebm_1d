#!/usr/bin/env python3
"""
Provides a way to generate texture map images from albedo values.
"""

import math
import shutil
import tempfile
import typing as tp
from pathlib import Path

import numpy as np
from PIL import Image


def _gen_img_ids() -> tp.Generator[str, None, None]:
    i = 1
    while True:
        yield f"img_{i}.png"
        i += 1


class AlbedoTextureMapper:
    """
    Generates OpenGL texture maps to represent by-latitude albedo.
    """

    def __init__(self) -> None:
        self._working_dir = Path(tempfile.mkdtemp())
        self._working_dir.mkdir(parents=True, exist_ok=True)
        self._img_ids = _gen_img_ids()

    def __del__(self) -> None:
        shutil.rmtree(self._working_dir)

    def img_from_albedos(self, albedos: np.ndarray) -> Path:
        # Assume albedos are in 0.0 ... 1.0
        # Map those to grayscale values, 0..255.
        # Assume the albedo values are for a set of evenly-spaced latitude
        # angles, from -90...90.
        if np.any(albedos < 0.0) or np.any(albedos > 1.0):
            raise ValueError(
                f"Albedo values must be in 0.0 ... 1.0: {albedos}"
            )

        values = (255 * albedos).astype(np.uint8)
        if len(albedos) <= 1:
            return self._create_img(values)
        return self._proportional_img(list(values))

    def _proportional_img(self, lat_values: list[int]) -> Path:
        # Map the per-latitude values to cartesian.  Assume the first value
        # is for latitude 0, the last for latitude 90°.
        num_intervals = len(lat_values)
        values: list[int] = []
        dlat = math.pi / num_intervals
        lat = -math.pi / 2.0
        scale = 100.0

        for v in lat_values:
            lat_next = lat + dlat

            y0 = int(scale * math.sin(lat))
            yf = int(scale * math.sin(lat_next))
            values += [v] * (yf - y0)

            lat = lat_next
        return self._create_img(np.array(values, dtype=np.uint8))

    def _create_img(self, values: np.ndarray) -> Path:
        values.shape = (len(values), 1)

        img = Image.fromarray(values, mode="L")
        output_name = self._working_dir / next(self._img_ids)
        img.save(output_name)
        return output_name
