"""
Demonstrate a change in texture rendering behavior starting in PySide6 6.3.x.
I think this is the first version to use RHI with Metal backend.
"""


import sys
from pathlib import Path

import PySide6
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QColor
from PySide6.QtGui import QVector3D as Vec3
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget


class SphereVC:
    def __init__(self, view: Qt3DExtras.Qt3DWindow) -> None:
        self.root_entity = Qt3DCore.QEntity()

        ce = self.camera_entity = view.camera()
        ce.lens().setPerspectiveProjection(45.0, 1.0, 0.1, 1000.0)
        ce.setPosition(Vec3(0, 8, 8))
        ce.setUpVector(Vec3(0, 1, 0))
        ce.setViewCenter(Vec3(0, 0, 0))

        self.light = Qt3DCore.QEntity(self.root_entity)
        self.point_light = Qt3DRender.QPointLight(self.light)
        self.point_light.setColor("white")
        self.point_light.setIntensity(1.0)
        self.light.addComponent(self.point_light)
        t = self.light_transform = Qt3DCore.QTransform(self.light)
        t.setTranslation(ce.position())
        self.light.addComponent(t)

        self.mesh = Qt3DExtras.QSphereMesh()
        self.mesh.setSlices(30)
        self.mesh.setRadius(3)

        m = self.material = Qt3DExtras.QDiffuseSpecularMaterial()
        m.setAmbient(QColor(220, 255, 255))
        m.setShininess(10.0)

        self.entity = Qt3DCore.QEntity(self.root_entity)
        self.entity.addComponent(self.mesh)
        self.entity.addComponent(self.material)

        view.setRootEntity(self.root_entity)

    def set_example_texture(self) -> None:
        data_dir = Path(__file__).resolve().parent / "data"
        texture_path = data_dir / "sample_texture.png"
        img_url = QUrl.fromLocalFile(str(texture_path.resolve()))

        loader = Qt3DRender.QTextureLoader(self.entity)
        loader.setMirrored(False)
        loader.setSource(img_url)
        self.material.setDiffuse(loader)


class MainWin(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(640, 480)
        self.view = Qt3DExtras.Qt3DWindow()
        self.view.defaultFrameGraph().setClearColor(QColor(0, 0, 0))
        self.widget = QWidget.createWindowContainer(self.view)
        self.sphere_vc = SphereVC(self.view)
        self._build_menus()
        self.setCentralWidget(self.widget)

    def _build_menus(self) -> None:
        self.menu = self.menuBar()

        self.m_file = self.menu.addMenu("File")
        self.m_edit = self.menu.addMenu("Edit")

        ta = self.add_texture_action = QAction("Add Texture", self)
        ta.setShortcut("Ctrl+T")
        self.m_edit.addAction(ta)
        ta.triggered.connect(self.sphere_vc.set_example_texture)

        ea = self.exit_action = QAction("Exit", self)
        ea.setShortcut("Ctrl+Q")
        self.m_file.addAction(ea)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWin()

    if len(sys.argv) >= 2:
        venv_name = Path(sys.argv[1]).name
        vinfo = sys.version_info[:3]
        py_version = ".".join(str(comp) for comp in vinfo)
        pyside_version = PySide6.__version__
        win.setWindowTitle(
            f"Python {py_version} - PySide6 {pyside_version} - {venv_name}"
        )

    win.exit_action.triggered.connect(sys.exit)
    win.show()
    app.exec()
