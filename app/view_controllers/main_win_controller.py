#!/usr/bin/env python3
"""
Adds behavior to the main window.
"""

import sys
import typing as tp

from PySide2.QtWidgets import QApplication, QLineEdit
from PySide2.QtCore import Qt, QObject, QTimer, Signal, QPointF
from PySide2.QtCharts import QtCharts

from ..layout.main_win import MainWin
from ..model.model import Model, ResultGen, AvgTempResult


NumberConverter = tp.Callable[[str], float]


class NumberField(QObject):
    value_changed = Signal(float)

    def __init__(
        self, text_field: QLineEdit, converter: NumberConverter
    ) -> None:
        super().__init__()
        self._value: tp.Optional[float] = None
        self._field = text_field
        self._converter = converter
        self._field.editingFinished.connect(self._text_field_edited)

    def _text_field_edited(self) -> None:
        try:
            if self._field.hasAcceptableInput():
                new_value = self._converter(self._field.text())
                if new_value != self._value:
                    self._value = new_value
                    self.value_changed.emit(self._value)
        except Exception as info:
            print("Error handling number field change:", info)
            pass

    def value(self) -> float:
        if self._value is None:
            raise ValueError("Field has no value.")
        return self._value

    def set_value(self, new_value: float) -> None:
        self._field.setText(str(new_value))
        self._text_field_edited()

    @classmethod
    def for_int(cls, text_field: QLineEdit) -> "NumberField":
        return cls(text_field, int)

    @classmethod
    def for_float(cls, text_field: QLineEdit) -> "NumberField":
        return cls(text_field, float)


class ChartController(QObject):
    selected_solar_mult = Signal(float)

    def __init__(
        self, chart: QtCharts.QChart, chart_view: QtCharts.QChartView
    ) -> None:
        super().__init__()
        self._chart = chart
        self._chart_view = chart_view

        self._chart.removeAllSeries()
        self._rising = self._line_series("Rising")
        self._falling = self._line_series("Falling")

        self._chart.removeAllSeries()
        self._chart.addSeries(self._rising)
        self._chart.addSeries(self._falling)
        self._chart.createDefaultAxes()

        self._chart.setAcceptHoverEvents(True)
        self._chart.setCursor(Qt.PointingHandCursor)

        # Track added values.
        self._x_vals: tp.Set[float] = set()
        self._y_vals: tp.Set[float] = set()
        self._rising_results: tp.List[AvgTempResult] = []
        self._falling_results: tp.List[AvgTempResult] = []

    def _line_series(self, name: str) -> QtCharts.QLineSeries:
        result = QtCharts.QLineSeries()
        result.setName(name)
        result.setPointsVisible(True)
        # result.hovered.connect(self._handle_hover)
        result.clicked.connect(self._handle_click)
        return result

    def clear(self) -> None:
        self._rising.clear()
        self._falling.clear()
        self._x_vals = set()
        self._y_vals = set()
        self._rising_results = []
        self._falling_results = []

    def add_result(self, new_result: AvgTempResult) -> None:
        x = new_result.solar_mult
        y = new_result.solution.avg

        is_rising = new_result.delta > 0

        series = self._rising if is_rising else self._falling
        series.append(x, y)

        results = self._rising_results if is_rising else self._falling_results
        results.append(new_result)
        self._x_vals.add(x)
        self._y_vals.add(y)

    def finished_adding(self) -> None:
        if self._x_vals:
            xmin, xmax = min(self._x_vals), max(self._x_vals)
            self._chart.axisX().setRange(xmin, xmax)

        if self._y_vals:
            ymin, ymax = min(self._y_vals), max(self._y_vals)
            self._chart.axisY().setRange(ymin, ymax)

    def _handle_hover(self, point: QPointF, moving_in: bool) -> None:
        if moving_in:
            self.selected_solar_mult.emit(point.x())

    def _handle_click(self, point: QPointF) -> None:
        self.selected_solar_mult.emit(point.x())

    def get_rising_solution(
        self, solar_mult: float
    ) -> tp.Optional[AvgTempResult]:
        """
        Get the 'rising solar multiplier' latitude bands for
        a given solar multiplier.
        """
        if not self._rising_results:
            return None

        i = self._nearest(solar_mult, self._rising_results)
        return self._rising_results[i]

    def get_falling_solution(
        self, solar_mult: float
    ) -> tp.Optional[AvgTempResult]:
        """
        Get the 'falling solar multiplier' latitude bands for
        a given solar multiplier.
        """
        if not self._falling_results:
            return None

        i = self._nearest(solar_mult, self._falling_results)
        return self._falling_results[i]

    def _nearest(
        self, solar_mult: float, records: tp.List[AvgTempResult]
    ) -> int:
        dists = [
            (abs(r.solar_mult - solar_mult), i) for i, r in enumerate(records)
        ]
        return min(dists)[-1]


class MainWinController:
    """
    Controls user interactions with the main window.
    """

    def __init__(self, main_win: MainWin) -> None:
        self._main_win = main_win
        mw = self._main_win._main_content
        self._exit_action = self._main_win.exit_action
        self._lat_bands_field = NumberField.for_int(mw.lat_bands_field)
        self._gat0_field = NumberField.for_float(mw.gat0_field)
        self._min_sol_mult_field = NumberField.for_float(
            mw.min_sol_mult_field
        )
        self._max_sol_mult_field = NumberField.for_float(
            mw.max_sol_mult_field
        )

        self._model: tp.Optional[Model] = None
        self._result_gen: tp.Optional[ResultGen] = None
        self._results: tp.List[AvgTempResult] = []

        self._chart_controller = ChartController(
            mw.gatsm_chart, mw.gatsm_view
        )

        self._rising_vc = mw.rising_vc
        self._falling_vc = mw.falling_vc

        self._connect_controls()
        self._init_control_content()

    def show(self) -> None:
        self._main_win.show()

    def _connect_controls(self) -> None:
        self._exit_action.triggered.connect(sys.exit)
        for field in [
            self._lat_bands_field,
            self._gat0_field,
            self._min_sol_mult_field,
            self._max_sol_mult_field,
        ]:
            field.value_changed.connect(self._model_updated)
        self._chart_controller.selected_solar_mult.connect(
            self._select_solar_mult
        )

    def _init_control_content(self) -> None:
        self._lat_bands_field.set_value(9)
        self._gat0_field.set_value(-60)
        self._min_sol_mult_field.set_value(0.5)
        self._max_sol_mult_field.set_value(2)

    def _model_updated(self) -> None:
        self._model = Model()
        self._chart_controller.clear()

        self._result_gen = None
        try:
            sm_min = self._min_sol_mult_field.value()
            sm_max = self._max_sol_mult_field.value()
            gat = self._gat0_field.value()
            lat_bands = int(self._lat_bands_field.value())
            self._result_gen = self._model.gen_temps(
                sm_min, sm_max, gat, lat_bands
            )
            self._get_result_later(10)
        except ValueError as info:
            pass
            print("Could not create new model: ", info)

    def _get_result_later(self, msec: tp.Optional[int] = 10) -> None:
        QTimer.singleShot(msec, self._get_model_result)

    def _get_model_result(self) -> None:
        if self._result_gen is not None:
            try:
                result = self._result_gen.send(None)
                self._chart_controller.add_result(result)
                self._get_result_later()
            except StopIteration:
                self._chart_controller.finished_adding()

    def _select_solar_mult(self, solar_mult: float) -> None:
        cc = self._chart_controller
        atr_up = cc.get_rising_solution(solar_mult)
        atr_down = cc.get_falling_solution(solar_mult)
        if atr_up is not None:
            self._rising_vc.set_albedos(atr_up.solution.albedos)
        if atr_down is not None:
            self._falling_vc.set_albedos(atr_down.solution.albedos)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    layout = MainWin()
    controller = MainWinController(layout)
    controller.show()
    app.exec_()
