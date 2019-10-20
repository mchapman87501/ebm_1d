#!/usr/bin/env python3
"""
"""

import datetime
import math
import numpy as np
from pathlib import Path
from PIL import Image
import shutil
import tempfile
import typing as tp


def _gen_img_ids() -> tp.Generator[str, None, None]:
    i = 1
    while True:
        yield f"img_{i}.png"
        i += 1


class AlbedoTextureMapper:
    """Generates OpenGL texture maps to represent by-latitude albedo."""

    # TODO build/add texture representing albedo by latitude.
    # https://stackoverflow.com/q/54451636/2826337

    # Strategies:
    # Use pillow to generate a 1-pixel-wide albedo strip image
    # Then either:
    #    Save the image to a temporary file and set its path as a
    #    QTextureImage source URL;
    # or
    #    Construct an inline 'data:image/png' URL from the image data,
    #    and set that as the QTextureImage source URL.

    def __init__(self) -> None:
        self._working_dir = Path(tempfile.mkdtemp())
        self._working_dir.mkdir(parents=True, exist_ok=True)
        self._img_ids = _gen_img_ids()

    def __del__(self) -> None:
        shutil.rmtree(self._working_dir)

    def img_from_albedos(self, albedos: tp.List[float]) -> Path:
        # Assume albedos are in 0.0 ... 1.0
        # Map those to grayscale values, 0..255.
        # Assume the albedo values are for a set of evenly-spaced latitude
        # angles, from -90...90.
        validate = np.array(albedos)
        if (validate < 0.0).any() or (validate > 1.0).any():
            raise ValueError("Albedo values must be in 0.0 ... 1.0")

        values = [int(255 * a) for a in albedos]
        if len(albedos) <= 1:
            return self._create_img(values)
        return self._proportional_img(list(values))

    def _proportional_img(self, lat_values: tp.List[int]) -> Path:
        # Map the per-latitude values to cartesian.  Assume the first value
        # is for latitude 0, the last for latitude 90°.
        num_intervals = len(lat_values)
        values: tp.List[int] = []
        dlat = math.pi / num_intervals
        lat = -math.pi / 2.0
        lat_max = math.pi / 2.0
        scale = 100.0

        for v in lat_values:
            lat_next = lat + dlat

            y0 = int(scale * math.sin(lat))
            yf = int(scale * math.sin(lat_next))
            values += [v] * (yf - y0)

            lat = lat_next
        return self._create_img(values)

    def _create_img(self, values: tp.List[int]) -> Path:
        nparray = np.array(values, dtype=np.uint8)
        nparray.shape = (len(values), 1)

        img = Image.fromarray(nparray, mode="L")
        output_name = self._working_dir / next(self._img_ids)
        img.save(output_name)
        return output_name
