from PyQt6.QtCore import QEvent, QPoint, QSize, Qt
from PyQt6.QtGui import QIcon, QMouseEvent
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from cloudflare_settings_gui.resources import resource_path

TITLE_BAR_HEIGHT = 44
LOGO_SIZE = 16
MAXIMIZE_ICON_SIZE = QSize(10, 10)

# Dragging the title bar to a screen edge snaps the window there, mirroring
# Windows' native Aero Snap (top = maximize, left/right = half-screen split).
SNAP_TOP_THRESHOLD = 8
SNAP_SIDE_THRESHOLD = 24


class TitleBar(QFrame):
    """Draggable custom title bar with minimize/maximize/close controls for a top-level window."""

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

        self._maximize_icon = QIcon(str(resource_path("assets", "maximize_icon.svg")))
        self._restore_icon = QIcon(str(resource_path("assets", "restore_icon.svg")))

        self._maximize_button = QPushButton()
        self._maximize_button.setObjectName("windowButton")
        self._maximize_button.setFixedSize(32, 32)
        self._maximize_button.setIconSize(MAXIMIZE_ICON_SIZE)
        self._maximize_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._maximize_button.clicked.connect(window.toggle_maximize)
        self._update_maximize_icon()

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
        layout.addWidget(self._maximize_button)
        layout.addWidget(close_button)

        window.installEventFilter(self)

    def eventFilter(self, watched: QWidget, event: QEvent) -> bool:
        if watched is self._window and event.type() == QEvent.Type.WindowStateChange:
            self._update_maximize_icon()
        return super().eventFilter(watched, event)

    def _update_maximize_icon(self) -> None:
        is_maximized = self._window.isMaximized()
        self._maximize_button.setIcon(self._restore_icon if is_maximized else self._maximize_icon)
        self._maximize_button.setToolTip("คืนขนาดเดิม" if is_maximized else "ขยายเต็มจอ")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return

        global_pos = event.globalPosition().toPoint()
        if self._window.isMaximized():
            self._unmaximize_and_start_drag(global_pos)
        else:
            self._drag_offset = global_pos - self._window.frameGeometry().topLeft()

    def _unmaximize_and_start_drag(self, global_pos: QPoint) -> None:
        old_frame = self._window.frameGeometry()
        offset_ratio_x = (global_pos.x() - old_frame.left()) / max(old_frame.width(), 1)

        self._window.showNormal()

        drag_x = int(self._window.width() * offset_ratio_x)
        drag_y = TITLE_BAR_HEIGHT // 2
        self._drag_offset = QPoint(drag_x, drag_y)
        self._window.move(global_pos.x() - drag_x, global_pos.y() - drag_y)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._window.move(event.globalPosition().toPoint() - self._drag_offset)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self._drag_offset is not None:
            self._maybe_snap_to_edge(event.globalPosition().toPoint())
        self._drag_offset = None

    def _maybe_snap_to_edge(self, global_pos: QPoint) -> None:
        screen = QApplication.screenAt(global_pos) or self._window.screen()
        if screen is None:
            return

        area = screen.availableGeometry()

        if global_pos.y() <= area.top() + SNAP_TOP_THRESHOLD:
            self._window.showMaximized()
        elif global_pos.x() <= area.left() + SNAP_SIDE_THRESHOLD:
            self._window.setGeometry(area.left(), area.top(), area.width() // 2, area.height())
        elif global_pos.x() >= area.right() - SNAP_SIDE_THRESHOLD:
            self._window.setGeometry(area.left() + area.width() // 2, area.top(), area.width() // 2, area.height())

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._window.toggle_maximize()
