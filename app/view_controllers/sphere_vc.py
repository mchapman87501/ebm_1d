#!/usr/bin/env python3
"""
Provides a way to present a view of a planetary sphere.
"""

import os
from pathlib import Path

from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor
from PySide6.QtGui import QVector3D as V3


# See https://code.qt.io/cgit/qt/qt3d.git/tree/examples/qt3d/basicshapes-cpp/main.cpp?h=5.13  # noqa: E501
# I try to separate GUI-related code into layout and interaction, but of
# course "widgets" - the things being arranged - encompass both.
class SphereVC:
    """SphereVC lays out and controls a view of a planetary sphere."""

    def __init__(self, view: Qt3DExtras.Qt3DWindow) -> None:
        """Initialize a new instance.

        Args:
        ----
            view: where to render the planetary sphere.
        """
        self.root_entity = Qt3DCore.QEntity()

        ce = self.camera_entity = view.camera()
        ce.lens().setPerspectiveProjection(45.0, 1.0, 0.1, 1000.0)
        self.reset_camera()

        self.light = Qt3DCore.QEntity(self.root_entity)
        self.point_light = Qt3DRender.QPointLight(self.light)
        self.point_light.setColor("white")
        self.point_light.setIntensity(1.0)
        self.light.addComponent(self.point_light)
        # Move the light to the camera's position - on-camera 'flash'!
        t = self.light_transform = Qt3DCore.QTransform(self.light)
        t.setTranslation(ce.position())
        self.light.addComponent(t)

        self.mesh = Qt3DExtras.QSphereMesh()
        self.mesh.setRings(30)
        self.mesh.setSlices(30)
        self.mesh.setRadius(2)

        t = self.transform = Qt3DCore.QTransform()
        t.setScale(1.3)
        t.setTranslation(V3(0.0, 0.0, 0.0))

        m = self.material = Qt3DExtras.QDiffuseSpecularMaterial()
        m.setAmbient(QColor(200, 200, 255))
        m.setShininess(20.0)

        self.entity = Qt3DCore.QEntity(self.root_entity)
        self.entity.addComponent(self.mesh)
        self.entity.addComponent(self.material)
        self.entity.addComponent(self.transform)

        self.loader: Qt3DRender.QTextureLoader | None = None

        view.setRootEntity(self.root_entity)
        self.entity.setEnabled(True)

        # Enable camera interaction
        # https://github.com/gpiasenza/Qt3DTests/blob/master/MainWindow.cpp
        self.cam_controller = Qt3DExtras.QOrbitCameraController(self.entity)
        self.cam_controller.setCamera(self.camera_entity)

    def reset_camera(self) -> None:
        """Reset the camera to its default position/orientation."""
        ce = self.camera_entity
        ce.setPosition(V3(0, 8, 8))
        ce.setUpVector(V3(0, 1, 0))
        ce.setViewCenter(V3(0, 0, 0))

    def set_texture(self, img_path: Path) -> None:
        """Set the texture image for self's sphere.

        Args:
            img_path: image file containing a texture
        """
        # This is from https://stackoverflow.com/q/49887994/2826337
        # and from https://forum.qt.io/topic/106370/qdiffusespecularmaterial-diffuse-texture/4  # noqa: E501
        local_pathname = os.fspath(img_path.resolve())
        img_url = QUrl.fromLocalFile(local_pathname)

        if self.loader is None:
            ldr = self.loader = Qt3DRender.QTextureLoader(self.entity)
            ldr.setMirrored(False)

        self.loader.setSource(img_url)

        if self.material.diffuse() != self.loader:
            self.material.setDiffuse(self.loader)
