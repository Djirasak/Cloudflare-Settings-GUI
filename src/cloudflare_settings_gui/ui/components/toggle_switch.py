from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPaintEvent
from PyQt6.QtWidgets import QAbstractButton, QWidget

TRACK_WIDTH = 40
TRACK_HEIGHT = 22
KNOB_MARGIN = 2

TRACK_COLOR_OFF = QColor("#3a3f47")
TRACK_COLOR_ON = QColor("#f6821f")
KNOB_COLOR = QColor("#e6e8eb")


class ToggleSwitch(QAbstractButton):
    """A pill-shaped on/off switch — a friendlier stand-in for a checkbox."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(TRACK_WIDTH, TRACK_HEIGHT)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        track_rect = QRectF(0, 0, self.width(), self.height())
        painter.setBrush(TRACK_COLOR_ON if self.isChecked() else TRACK_COLOR_OFF)
        painter.drawRoundedRect(track_rect, self.height() / 2, self.height() / 2)

        knob_diameter = self.height() - KNOB_MARGIN * 2
        knob_x = self.width() - knob_diameter - KNOB_MARGIN if self.isChecked() else KNOB_MARGIN
        painter.setBrush(KNOB_COLOR)
        painter.drawEllipse(QRectF(knob_x, KNOB_MARGIN, knob_diameter, knob_diameter))
