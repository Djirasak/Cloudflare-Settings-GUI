from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QLabel

from cloudflare_settings_gui.ui.components.frameless_window import FramelessWindow
from cloudflare_settings_gui.ui.components.title_bar import TitleBar


def _make_window(qtbot) -> tuple[FramelessWindow, TitleBar]:
    window = FramelessWindow(QLabel("content"), title="Test Window", initial_size=(800, 600))
    qtbot.addWidget(window)
    window.show()
    title_bar = window.findChild(TitleBar)
    assert title_bar is not None
    return window, title_bar


class TestTitleBarMaximizeIcon:
    def test_icon_swaps_when_window_state_changes(self, qtbot):
        window, title_bar = _make_window(qtbot)

        maximize_icon = title_bar._maximize_icon
        restore_icon = title_bar._restore_icon

        assert title_bar._maximize_button.icon().cacheKey() == maximize_icon.cacheKey()

        window.toggle_maximize()
        assert title_bar._maximize_button.icon().cacheKey() == restore_icon.cacheKey()

        window.toggle_maximize()
        assert title_bar._maximize_button.icon().cacheKey() == maximize_icon.cacheKey()


class TestTitleBarEdgeSnapping:
    def _drag(self, qtbot, title_bar, start_local: QPoint, target_global: QPoint) -> None:
        qtbot.mousePress(title_bar, Qt.MouseButton.LeftButton, pos=start_local)
        # Recompute the local point for each step: mouseMoveEvent moves the window (mirroring a
        # real drag), so a local point mapped before that move overshoots once re-globalized
        # against the window's new position — often onto another monitor.
        qtbot.mouseMove(title_bar, pos=title_bar.mapFromGlobal(target_global))
        qtbot.mouseRelease(title_bar, Qt.MouseButton.LeftButton, pos=title_bar.mapFromGlobal(target_global))

    def test_dragging_to_top_edge_maximizes_window(self, qtbot):
        window, title_bar = _make_window(qtbot)
        area = window.screen().availableGeometry()

        start_local = QPoint(200, 20)
        start_global = title_bar.mapToGlobal(start_local)
        self._drag(qtbot, title_bar, start_local, QPoint(start_global.x(), area.top()))

        assert window.isMaximized() is True

    def test_dragging_to_left_edge_snaps_to_left_half(self, qtbot):
        window, title_bar = _make_window(qtbot)
        area = window.screen().availableGeometry()

        start_local = QPoint(200, 20)
        start_global = title_bar.mapToGlobal(start_local)
        self._drag(qtbot, title_bar, start_local, QPoint(area.left(), start_global.y()))

        # Half-width, unless that would be narrower than the window's minimum size.
        expected_width = max(area.width() // 2, window.minimumWidth())
        assert window.isMaximized() is False
        assert window.width() == expected_width
        assert window.x() == area.left()

    def test_dragging_to_right_edge_snaps_to_right_half(self, qtbot):
        window, title_bar = _make_window(qtbot)
        area = window.screen().availableGeometry()

        start_local = QPoint(200, 20)
        start_global = title_bar.mapToGlobal(start_local)
        self._drag(qtbot, title_bar, start_local, QPoint(area.right(), start_global.y()))

        expected_width = max(area.width() // 2, window.minimumWidth())
        assert window.isMaximized() is False
        assert window.width() == expected_width
        assert window.x() == area.left() + area.width() // 2

    def test_dragging_away_from_edges_does_not_snap(self, qtbot):
        window, title_bar = _make_window(qtbot)

        start_local = QPoint(200, 20)
        start_global = title_bar.mapToGlobal(start_local)
        original_width = window.width()

        self._drag(qtbot, title_bar, start_local, start_global + QPoint(30, 30))

        assert window.isMaximized() is False
        assert window.width() == original_width

    def test_dragging_maximized_window_title_bar_restores_it(self, qtbot):
        window, title_bar = _make_window(qtbot)
        window.showMaximized()

        start_local = QPoint(200, 20)
        qtbot.mousePress(title_bar, Qt.MouseButton.LeftButton, pos=start_local)

        assert window.isMaximized() is False
