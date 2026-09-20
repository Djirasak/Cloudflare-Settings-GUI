from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QColor, QIcon, QMouseEvent
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cloudflare_settings_gui.resources import resource_path

SHADOW_MARGIN = 24
TITLE_BAR_HEIGHT = 44
LOGO_SIZE = 16


class _TitleBar(QFrame):
    def __init__(self, window: QWidget, title: str) -> None:
        super().__init__()
        self.setObjectName("titleBar")
        self.setFixedHeight(TITLE_BAR_HEIGHT)

        self._window = window
        self._drag_offset: QPoint | None = None

        mark = QSvgWidget(str(resource_path("assets", "cloudflare_mark.svg")))
        mark.setFixedSize(LOGO_SIZE, LOGO_SIZE)
        mark.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        label = QLabel(title)
        label.setObjectName("titleText")
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        minimize_button = QPushButton("—")
        minimize_button.setObjectName("windowButton")
        minimize_button.setFixedSize(32, 32)
        minimize_button.setCursor(Qt.CursorShape.PointingHandCursor)
        minimize_button.clicked.connect(window.showMinimized)

        close_button = QPushButton("✕")
        close_button.setObjectName("windowCloseButton")
        close_button.setFixedSize(32, 32)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(window.close)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(10)
        layout.addWidget(mark)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(close_button)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._window.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._drag_offset = None


class FramelessWindow(QWidget):
    """A borderless, drop-shadowed window shell with a custom title bar around a content page."""

    def __init__(self, content: QWidget, title: str) -> None:
        super().__init__()
        self.setObjectName("rootWindow")
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(str(resource_path("assets", "cloudflare_mark.svg"))))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN)
        outer.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        card = QFrame()
        card.setObjectName("windowCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        card_layout.addWidget(_TitleBar(self, title))
        card_layout.addWidget(content)

        outer.addWidget(card)
