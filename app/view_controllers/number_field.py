#!/usr/bin/env python3
"""
Provides a QLineEdit controller that allows numeric input.
"""

import typing as tp

from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import QObject, Signal

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
