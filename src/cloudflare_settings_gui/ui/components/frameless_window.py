from PyQt6.QtCore import QEvent, QPoint, QRect, Qt
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from cloudflare_settings_gui.resources import resource_path
from cloudflare_settings_gui.ui.components.shadow_card import build_shadowed_card
from cloudflare_settings_gui.ui.components.title_bar import TitleBar

# Kept narrow enough that half-screen edge-snapping still produces a real split
# on common laptop displays (e.g. 1366px wide -> 683px half) instead of being
# clamped back up to the minimum.
MIN_WINDOW_WIDTH = 640
MIN_WINDOW_HEIGHT = 480

# The resizable main window skips the drop shadow (it re-renders on every size change,
# which visibly ghosts when the window jumps size abruptly, e.g. maximizing) so this
# only needs to be wide enough to grab with the mouse, not wide enough for a shadow blur.
RESIZE_BORDER = 6

_CURSOR_FOR_EDGE = {
    "left": Qt.CursorShape.SizeHorCursor,
    "right": Qt.CursorShape.SizeHorCursor,
    "top": Qt.CursorShape.SizeVerCursor,
    "bottom": Qt.CursorShape.SizeVerCursor,
    "top_left": Qt.CursorShape.SizeFDiagCursor,
    "bottom_right": Qt.CursorShape.SizeFDiagCursor,
    "top_right": Qt.CursorShape.SizeBDiagCursor,
    "bottom_left": Qt.CursorShape.SizeBDiagCursor,
}


class FramelessWindow(QWidget):
    """A borderless, resizable window shell with a custom title bar around a content page."""

    def __init__(self, content: QWidget, title: str, initial_size: tuple[int, int] | None = None) -> None:
        super().__init__()
        self.setObjectName("rootWindow")
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(str(resource_path("assets", "cloudflare_mark.svg"))))
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        self._resize_edge: str | None = None
        self._resize_start_geometry: QRect | None = None
        self._resize_start_pos: QPoint | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(RESIZE_BORDER, RESIZE_BORDER, RESIZE_BORDER, RESIZE_BORDER)
        self._outer_layout = outer

        card, card_layout = build_shadowed_card(with_shadow=False)
        card_layout.addWidget(TitleBar(self, title))
        card_layout.addWidget(content)

        outer.addWidget(card)

        self._card_layout = card_layout
        self._content = content

        if initial_size is not None:
            self.resize(*initial_size)

    def toggle_maximize(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            margin = 0 if self.isMaximized() else RESIZE_BORDER
            self._outer_layout.setContentsMargins(margin, margin, margin, margin)

    def set_content(self, new_content: QWidget) -> None:
        self._card_layout.removeWidget(self._content)
        self._content.hide()
        self._content.deleteLater()

        self._card_layout.addWidget(new_content)
        new_content.show()
        self._content = new_content

    def _edge_at(self, pos: QPoint) -> str | None:
        rect = self.rect()
        left = pos.x() <= RESIZE_BORDER
        right = pos.x() >= rect.width() - RESIZE_BORDER
        top = pos.y() <= RESIZE_BORDER
        bottom = pos.y() >= rect.height() - RESIZE_BORDER

        if top and left:
            return "top_left"
        if top and right:
            return "top_right"
        if bottom and left:
            return "bottom_left"
        if bottom and right:
            return "bottom_right"
        if left:
            return "left"
        if right:
            return "right"
        if top:
            return "top"
        if bottom:
            return "bottom"
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self._edge_at(event.position().toPoint())
            if edge is not None:
                self._resize_edge = edge
                self._resize_start_geometry = self.geometry()
                self._resize_start_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._resize_edge is None:
            edge = self._edge_at(event.position().toPoint())
            self.setCursor(_CURSOR_FOR_EDGE.get(edge, Qt.CursorShape.ArrowCursor))
        elif event.buttons() & Qt.MouseButton.LeftButton:
            self._resize_to(event.globalPosition().toPoint())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self._resize_edge = None
        self._resize_start_geometry = None
        self._resize_start_pos = None

    def _resize_to(self, global_pos: QPoint) -> None:
        assert self._resize_edge is not None
        assert self._resize_start_geometry is not None
        assert self._resize_start_pos is not None

        delta = global_pos - self._resize_start_pos
        geometry = QRect(self._resize_start_geometry)

        if "left" in self._resize_edge:
            new_left = geometry.left() + delta.x()
            if geometry.right() - new_left + 1 >= self.minimumWidth():
                geometry.setLeft(new_left)
        if "right" in self._resize_edge:
            geometry.setWidth(max(geometry.width() + delta.x(), self.minimumWidth()))
        if "top" in self._resize_edge:
            new_top = geometry.top() + delta.y()
            if geometry.bottom() - new_top + 1 >= self.minimumHeight():
                geometry.setTop(new_top)
        if "bottom" in self._resize_edge:
            geometry.setHeight(max(geometry.height() + delta.y(), self.minimumHeight()))

        self.setGeometry(geometry)
