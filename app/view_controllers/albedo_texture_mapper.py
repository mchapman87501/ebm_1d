"""Provides a way to generate texture map images from albedo values."""

import math
import shutil
import tempfile
import typing as tp
from pathlib import Path

import numpy as np
from PySide6.QtGui import QImage


def _gen_img_ids() -> tp.Generator[str, None, None]:
    i = 1
    while True:
        yield f"img_{i}.png"
        i += 1


class AlbedoTextureMapper:
    """Generates OpenGL texture maps to represent by-latitude albedo."""

    def __init__(self) -> None:
        """Initialize a new instance."""
        self._working_dir = Path(tempfile.mkdtemp())
        self._working_dir.mkdir(parents=True, exist_ok=True)
        self._img_ids = _gen_img_ids()

    def __del__(self) -> None:
        """Delete this instance and its temporary files."""
        shutil.rmtree(self._working_dir)

    def img_path_from_albedos(self, albedos: np.ndarray) -> Path:
        """Get the path of an image build from albedos."""
        return self._save_img(self.img_from_albedos(albedos))

    def img_from_albedos(self, albedos: np.ndarray) -> QImage:
        """Get an image from a sequence of normalized albedo values."""
        # Require albedos to be in 0.0 ... 1.0
        # Map those to grayscale values, 0..255.
        # Assume the albedo values are for a set of evenly-spaced latitude
        # angles, from -90...90.
        if np.any(albedos < 0.0) or np.any(albedos > 1.0):  # noqa: PLR2004
            msg = f"Albedo values must be in 0.0 ... 1.0: {albedos}"
            raise ValueError(msg)

        gray_values = (255 * albedos).astype(np.uint8)
        if len(albedos) <= 1:
            return self._create_img(gray_values)
        return self._proportional_img(list(gray_values))

    def _proportional_img(self, gray_values: list[int]) -> QImage:
        # Map the per-latitude values to cartesian.  Assume the first value
        # is for latitude 0, the last for latitude 90°.
        num_intervals = len(gray_values)
        values: list[int] = []
        dlat = math.pi / num_intervals
        lat = -math.pi / 2.0
        scale = 100.0

        for v in gray_values:
            lat_next = lat + dlat

            y0 = int(scale * math.sin(lat))
            yf = int(scale * math.sin(lat_next))
            values += [v] * (yf - y0)

            lat = lat_next

        np_values = np.array(values, dtype=np.uint8)
        np_values.shape = (len(values), 1)
        return self._create_img(np_values)

    def _create_img(self, values: np.ndarray) -> QImage:
        (h, w) = values.shape
        return QImage(values.data, w, h, 1, QImage.Format_Grayscale8)

    def _save_img(self, img: QImage) -> Path:
        output_name = self._working_dir / next(self._img_ids)
        img.save(str(output_name))
        return output_name
