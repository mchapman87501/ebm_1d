#!/usr/bin/env python3
"""
Provides user interaction for a rising/falling temperature chart.
"""

import typing as tp

from PySide6 import QtCharts
from PySide6.QtCore import QObject, QPointF, Qt, Signal
from PySide6.QtGui import QPen
from PySide6.QtWidgets import QGraphicsLineItem

from ..layout.mousing_chart import MousingChart
from ..model.model import AvgTempResult


class ChartController(QObject):
    """
    Manages user interaction for a rising/falling temperature chart.
    """

    selected_solar_mult = Signal(float)
    chart_hover_pos = Signal(QPointF)

    def __init__(
        self, chart: MousingChart, chart_view: QtCharts.QChartView
    ) -> None:
        super().__init__()
        self._chart = chart
        self._chart_view = chart_view

        # Handle chart hover events, with debounce.
        self._chart.hovered.connect(self._handle_chart_hover)
        self._last_chart_x = -100.0

        self._chart.removeAllSeries()
        self._rising = self._line_series("Rising")
        self._falling = self._line_series("Falling")

        self._hover_line = self._create_hover_line(self._chart)

        self._chart.removeAllSeries()
        self._chart.addSeries(self._rising)
        self._chart.addSeries(self._falling)
        self._chart.createDefaultAxes()

        self._chart.setAcceptHoverEvents(True)
        self._chart.setCursor(Qt.CrossCursor)

        # Track added values.
        self._x_vals: set[float] = set()
        self._y_vals: set[float] = set()
        self._rising_results: list[AvgTempResult] = []
        self._falling_results: list[AvgTempResult] = []

    def _line_series(self, name: str) -> QtCharts.QLineSeries:
        result = QtCharts.QLineSeries()
        result.setName(name)
        result.setPointsVisible(True)
        return result

    def _create_hover_line(self, chart: QtCharts.QChart) -> tp.Any:
        scene = chart.scene()
        result = QGraphicsLineItem()
        result.setPen(QPen(Qt.black, 0.0, Qt.DashLine))

        def move_hover_line(new_value: QPointF) -> None:
            x = new_value.x()

            plot_area = chart.plotArea()
            x_min = plot_area.left()
            x_max = plot_area.right()
            result.setVisible(x_min <= x <= x_max)
            result.setLine(x, plot_area.bottom(), x, plot_area.top())

        self.chart_hover_pos.connect(move_hover_line)
        scene.addItem(result)
        return result

    def clear(self) -> None:
        self._rising.clear()
        self._falling.clear()
        self._x_vals = set()
        self._y_vals = set()
        self._rising_results = []
        self._falling_results = []
        self._last_chart_x = -100.0

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

    def _handle_chart_hover(self, point: QPointF) -> None:
        # Transform to the data coordinate-space of the chart.
        # See https://stackoverflow.com/a/44078533
        scene_pos = self._chart_view.mapToScene(point.toPoint())
        chart_item_pos = self._chart.mapFromScene(scene_pos)
        series_point = self._chart.mapToValue(chart_item_pos)
        series_x = series_point.x()

        self.chart_hover_pos.emit(scene_pos)

        # TODO smooth to a fraction of the data space extent,
        # rather than an absolute magnitude.
        abs_dx = abs(series_x - self._last_chart_x)
        if abs_dx >= 0.1:
            self._last_chart_x = series_x
            self.selected_solar_mult.emit(series_x)

    def get_rising_solution(self, solar_mult: float) -> AvgTempResult | None:
        """
        Get the 'rising solar multiplier' latitude bands for
        a given solar multiplier.
        """
        if not self._rising_results:
            return None

        i = self._nearest(solar_mult, self._rising_results)
        return self._rising_results[i]

    def get_falling_solution(self, solar_mult: float) -> AvgTempResult | None:
        """
        Get the 'falling solar multiplier' latitude bands for
        a given solar multiplier.
        """
        if not self._falling_results:
            return None

        i = self._nearest(solar_mult, self._falling_results)
        return self._falling_results[i]

    def _nearest(
        self, solar_mult: float, records: list[AvgTempResult]
    ) -> int:
        dists = [
            (abs(r.solar_mult - solar_mult), i) for i, r in enumerate(records)
        ]
        return min(dists)[-1]
