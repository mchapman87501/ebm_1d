#!/usr/bin/env python3
"""
Provides a QChart that tracks mouse movement.
"""

from PySide6.QtCore import Signal, QPointF
from PySide6.QtWidgets import (
    QGraphicsSceneHoverEvent,
)
from PySide6 import QtCharts


class MousingChart(QtCharts.QChart):
    hovered = Signal(QPointF)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.hovered.emit(event.scenePos())
