#!/usr/bin/env python3
"""
Provides a QChart that tracks mouse movement.
"""

from PySide6 import QtCharts
from PySide6.QtCore import QPointF, Signal
from PySide6.QtWidgets import (
    QGraphicsSceneHoverEvent,
)


class MousingChart(QtCharts.QChart):
    hovered = Signal(QPointF)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.hovered.emit(event.pos())
