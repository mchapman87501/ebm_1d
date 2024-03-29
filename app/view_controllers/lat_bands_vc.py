#!/usr/bin/env python3
"""Provides a way to depict albedo/temperature by latitude band."""

import numpy as np
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DInput import Qt3DInput
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

from .albedo_texture_mapper import AlbedoTextureMapper
from .sphere_vc import SphereVC


class _Clickable3DWindow(Qt3DExtras.Qt3DWindow):
    double_clicked = Signal()

    def mouseDoubleClickEvent(self, event: Qt3DInput.QMouseEvent) -> None:
        self.double_clicked.emit()


class LatBandsVC:
    """LatBandsVC lays out and controls a view of latitude bands."""

    def __init__(self) -> None:
        # Documentation for Qt3DWindow is surprisingly scarce...
        self.view = _Clickable3DWindow()  # Qt3DExtras.Qt3DWindow()
        self._configure_view()
        self.widget = QWidget.createWindowContainer(self.view)
        self.sphere_mgr = SphereVC(self.view)
        self.albedo_mapper = AlbedoTextureMapper()
        self._prev_values = np.zeros(1)

        self.view.double_clicked.connect(self.sphere_mgr.reset_camera)

    def _configure_view(self) -> None:
        self.view.defaultFrameGraph().setClearColor(QColor(0, 0, 0))

    def set_albedos(self, albedos: np.ndarray) -> None:
        """
        Apply a set of albedos to self's sphere.
        albedos is a sequence of albedo values for one hemisphere,
        extending from equator to pole.
        """
        # Albedos covers one hemisphere from equator to pole, so it
        # needs to be doubled to represent pole to pole
        eq_to_pole = albedos
        pole_to_eq = albedos[::-1]
        all_values = np.concatenate((pole_to_eq, eq_to_pole))

        if not np.array_equal(all_values, self._prev_values):
            path = self.albedo_mapper.img_path_from_albedos(all_values)
            self.sphere_mgr.set_texture(path)
            self._prev_values = all_values
