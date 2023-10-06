#!/usr/bin/env python3
"""
Adds behavior to the main window.
"""

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from ..layout.main_win import MainWin
from ..model.model import AvgTempResult, Model, ResultGen
from .chart_controller import ChartController
from .number_field import NumberField


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
        self._lat_trans_field = NumberField.for_float(mw.lhtc_field)

        self._model: Model | None = None
        self._result_gen: ResultGen | None = None
        self._results: list[AvgTempResult] = []

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
        self._exit_action.triggered.connect(self._main_win.close)
        for field in [
            self._lat_bands_field,
            self._gat0_field,
            self._min_sol_mult_field,
            self._max_sol_mult_field,
            self._lat_trans_field,
        ]:
            field.value_changed.connect(self._model_updated)
        self._chart_controller.selected_solar_mult.connect(
            self._select_solar_mult
        )

    def _init_control_content(self) -> None:
        # Set default field values.
        self._lat_bands_field.set_value(9)
        self._gat0_field.set_value(-60)
        self._min_sol_mult_field.set_value(4)
        self._max_sol_mult_field.set_value(8)
        self._lat_trans_field.set_value(7.6)

    def _model_updated(self) -> None:
        self._model = Model()
        self._chart_controller.clear()

        self._result_gen = None
        try:
            sm_min = self._min_sol_mult_field.value()
            sm_max = self._max_sol_mult_field.value()
            gat = self._gat0_field.value()
            lat_bands = int(self._lat_bands_field.value())
            lat_heat_transfer = self._lat_trans_field.value()
            self._result_gen = self._model.gen_temps(
                sm_min, sm_max, gat, lat_bands, lat_heat_transfer
            )
            self._get_result_later(10)
        except ValueError:
            pass

    def _get_result_later(self, msec: int | None = None) -> None:
        if msec is None:
            msec = 10
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
