#!/usr/bin/env python3
# type: ignore

import sys
from PySide2.QtGui import QPainter, QIntValidator, QDoubleValidator
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QAction,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QSizePolicy,
    QLabel,
    QLineEdit,
)
from PySide2.QtCore import Qt
from PySide2.QtCharts import QtCharts

from ..view_controllers.lat_bands_vc import LatBandsVC


class MainWinContent(QWidget):
    _FIELD_WIDTH = 64

    def __init__(self) -> None:
        super().__init__()

        layout = self._main_layout = QVBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size.setVerticalStretch(1)

        grid = QGridLayout()
        grid.setColumnStretch(3, 1)
        grid.addWidget(self._label("Bands:"), 0, 0)
        self.lat_bands_field = self._int_field(
            0, 360, tooltip="Number of latitude bands"
        )
        grid.addWidget(self.lat_bands_field, 0, 1)

        # Control for setting initial global average temperature
        grid.addWidget(self._label("Init. Temp:"), 1, 0)
        self.gat0_field = self._int_field(
            -100,
            100,
            placeholder="°C",
            tooltip="Initial global average temperature, Celsius",
        )

        grid.addWidget(self.gat0_field, 1, 1)

        # Control for setting range of solar multiplier values
        grid.addWidget(self._label("Solar Multiplier:"), 2, 0)
        ff = self._float_field
        field = self.min_sol_mult_field = ff(
            0,
            100,
            placeholder="Min",
            tooltip="Minimum Solar Constant multiplier",
        )
        grid.addWidget(field, 2, 1)
        field = self.max_sol_mult_field = ff(
            0,
            100,
            placeholder="Max",
            tooltip="Maximum Solar Constant multiplier",
        )
        grid.addWidget(field, 2, 2)

        layout.addLayout(grid)

        # Display of global average temperature vs. solar multiplier,
        #   rising vs. falling
        chart = self.gatsm_chart = QtCharts.QChart()
        chart.setAnimationOptions(QtCharts.QChart.AllAnimations)
        chart_view = self.gatsm_view = QtCharts.QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)

        size.setVerticalStretch(1)
        chart_view.setSizePolicy(size)
        chart_view.setMinimumSize(480, 320)

        self._main_layout.addWidget(chart_view)

        # Display of albedo by latitude band, for a given
        # point on the rising plot
        hbox = QHBoxLayout()
        hbox.addStretch(1)

        vbox1 = QVBoxLayout()
        vbox1.addWidget(self._label("Rising", Qt.AlignCenter))
        vm = self.rising_vc = LatBandsVC()
        min_size = (192, 192)
        widget = vm.widget
        widget.setMinimumSize(*min_size)
        vbox1.addWidget(widget)
        hbox.addLayout(vbox1)

        hbox.addStretch(1)

        # Display of albedo by latitude band, for a given
        # point on the falling plot
        vbox2 = QVBoxLayout()
        vbox2.addWidget(self._label("Falling", Qt.AlignCenter))
        vm = self.falling_vc = LatBandsVC()
        widget = vm.widget
        widget.setMinimumSize(*min_size)
        vbox2.addWidget(widget)
        hbox.addLayout(vbox2)

        hbox.addStretch(1)

        self._main_layout.addLayout(hbox)
        self.setLayout(self._main_layout)

    def _label(
        self, text: str, align: Qt.Alignment = Qt.AlignRight
    ) -> QLabel:
        result = QLabel(text)
        result.setAlignment(align)
        return result

    def _int_field(
        self,
        min_val: int,
        max_val: int,
        placeholder: str = "",
        tooltip: str = "",
    ) -> QLineEdit:
        result = QLineEdit()
        # TODO derive the max width from the text repr of min_val, max_val.
        result.setMaximumWidth(self._FIELD_WIDTH)
        result.setAlignment(Qt.AlignRight)
        validator = QIntValidator(min_val, max_val)
        result.setValidator(validator)
        if placeholder:
            result.setPlaceholderText(placeholder)
        if tooltip:
            result.setToolTip(tooltip)
        return result

    def _float_field(
        self,
        min_val: float = 0.0,
        max_val: float = 1.0,
        decimals: int = 1,
        placeholder: str = "",
        tooltip: str = "",
    ) -> QLineEdit:
        result = QLineEdit()
        # TODO derive the max width from the text repr of min_val, max_val.
        result.setMaximumWidth(self._FIELD_WIDTH)
        result.setAlignment(Qt.AlignRight)
        validator = QDoubleValidator(min_val, max_val, decimals)
        result.setValidator(validator)
        if placeholder:
            result.setPlaceholderText(placeholder)
        if tooltip:
            result.setToolTip(tooltip)
        return result


class MainWin(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("1D EBM")
        self._build_menus()

        self._main_content = MainWinContent()
        self.setCentralWidget(self._main_content)
        self.status = self.statusBar()

    def _build_menus(self) -> None:
        self.menu = self.menuBar()
        self.m_file = self.menu.addMenu("File")

        ea = self.exit_action = QAction("Exit", self)
        ea.setShortcut("Ctrl+Q")
        self.m_file.addAction(ea)


def main() -> None:
    """Mainline for interactive review of layout."""
    app = QApplication(sys.argv)
    win = MainWin()
    win.exit_action.triggered.connect(sys.exit)
    win.show()
    app.exec_()


if __name__ == "__main__":
    main()
