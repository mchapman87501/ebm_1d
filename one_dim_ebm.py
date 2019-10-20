#!/usr/bin/env python3
"""
Provides an interactive 1D EBM.
"""

import sys
from PySide2.QtWidgets import QApplication
from app.layout.main_win import MainWin
from app.view_controllers.main_win_controller import MainWinController


if __name__ == "__main__":
    app = QApplication(sys.argv)
    layout = MainWin()
    controller = MainWinController(layout)
    controller.show()
    app.exec_()
