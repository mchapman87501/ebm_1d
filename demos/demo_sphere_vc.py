#!/usr/bin/env python3
"""
Creates a Qt app to interactively test sphere_vc.py.
"""


import sys

import numpy as np
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtGui import QAction, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from app.view_controllers.albedo_texture_mapper import AlbedoTextureMapper
from app.view_controllers.sphere_vc import SphereVC


class MainWin(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(640, 480)
        self._build_menus()
        self.view = Qt3DExtras.Qt3DWindow()
        self.view.defaultFrameGraph().setClearColor(QColor(0, 0, 0))
        self.widget = QWidget.createWindowContainer(self.view)
        self.sphere_vc = SphereVC(self.view)
        self.setCentralWidget(self.widget)

        self._textures = AlbedoTextureMapper()

    def _build_menus(self) -> None:
        self.menu = self.menuBar()

        self.m_file = self.menu.addMenu("File")
        self.m_edit = self.menu.addMenu("Edit")

        ta = self.add_texture_action = QAction("Add Texture", self)
        self.m_edit.addAction(ta)
        ta.triggered.connect(self._add_texture)

        ea = self.exit_action = QAction("Exit", self)
        ea.setShortcut("Ctrl+Q")
        self.m_file.addAction(ea)

    def _add_texture(self) -> None:
        up = np.arange(0.0, 1.0, 0.1)
        down = np.arange(1.0, 0.0, -0.1)
        albedos = np.concatenate((down, up))
        img_path = self._textures.img_path_from_albedos(albedos)
        self.sphere_vc.set_texture(img_path)


def main() -> None:
    """Mainline for interactive review of layout."""
    app = QApplication(sys.argv)
    win = MainWin()
    win.exit_action.triggered.connect(sys.exit)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
