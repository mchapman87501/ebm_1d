#!/usr/bin/env python3
"""
Provides user interaction for a rising/falling temperature chart.
"""

import typing as tp

from PySide6.QtCore import Qt, QObject, Signal, QPointF
from PySide6 import QtCharts

from ..model.model import AvgTempResult
from ..layout.mousing_chart import MousingChart


class ChartController(QObject):
    """
    Manages user interaction for a rising/falling temperature chart.
    """

    selected_solar_mult = Signal(float)

    def __init__(
        self, chart: MousingChart, chart_view: QtCharts.QChartView
    ) -> None:
        super().__init__()
        self._chart = chart
        self._chart_view = chart_view

        self._chart.hovered.connect(self._handle_whole_chart_hover)

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
        result.hovered.connect(self._handle_hover)
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

    def _handle_whole_chart_hover(self, point: QPointF) -> None:
        # Transform to the data coordinate-space of the chart.
        # See https://stackoverflow.com/a/44078533
        scene_pos = self._chart_view.mapToScene(point.toPoint())
        chart_item_pos = self._chart.mapFromScene(scene_pos)
        series_point = self._chart.mapToValue(chart_item_pos)
        print("  Series data x coordinate:", series_point.x())
        self.selected_solar_mult.emit(series_point.x())

    def _handle_hover(self, point: QPointF, moving_in: bool) -> None:
        return
        if moving_in:
            self.selected_solar_mult.emit(point.x())

    def _handle_click(self, point: QPointF) -> None:
        return
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
