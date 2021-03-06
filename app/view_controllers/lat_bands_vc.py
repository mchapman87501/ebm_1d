#!/usr/bin/env python3
"""
Provides a way to depict albedo/temperature by latitude band.
"""

import typing as tp

from PySide2.QtGui import QColor
from PySide2.QtWidgets import QWidget
from PySide2.Qt3DExtras import Qt3DExtras

from .sphere_vc import SphereVC
from .albedo_texture_mapper import AlbedoTextureMapper


class LatBandsVC:
    """
    LatBandsVC lays out and controls a view of latitude bands.
    """

    def __init__(self) -> None:
        self.view = Qt3DExtras.Qt3DWindow()
        self._configure_view()
        self.widget = QWidget.createWindowContainer(self.view)
        self.sphere_mgr = SphereVC(self.view)
        self.albedo_mapper = AlbedoTextureMapper()

    def _configure_view(self) -> None:
        self.view.defaultFrameGraph().setClearColor(QColor(0, 0, 0))

    def set_albedos(self, albedos: tp.Sequence[float]) -> None:
        """
        Apply a set of albedos to self's sphere.
        albedos is a sequence of albedo values for one hemisphere,
        extending from equator to pole.
        """

        # Albedos covers one hemisphere from equator to pole, so it
        # needs to be doubled to represent pole to pole
        eq_to_pole = list(albedos)
        pole_to_eq = list(reversed(eq_to_pole))
        all_values = pole_to_eq + eq_to_pole

        texture_img_path = self.albedo_mapper.img_from_albedos(all_values)
        self.sphere_mgr.set_texture(texture_img_path)
