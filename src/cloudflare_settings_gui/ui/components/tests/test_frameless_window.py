from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import QLabel, QPushButton

from cloudflare_settings_gui.ui.components.frameless_window import (
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    RESIZE_BORDER,
    FramelessWindow,
)


class TestFramelessWindow:
    def test_sets_window_title_and_icon(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window")
        qtbot.addWidget(window)

        assert window.windowTitle() == "Test Window"
        assert not window.windowIcon().isNull()

    def test_close_button_closes_window(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window")
        qtbot.addWidget(window)
        window.show()

        close_button = window.findChild(QPushButton, "windowCloseButton")
        assert close_button is not None

        qtbot.mouseClick(close_button, Qt.MouseButton.LeftButton)

        assert window.isVisible() is False

    def test_minimize_button_minimizes_window(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window")
        qtbot.addWidget(window)
        window.show()

        minimize_button = next(b for b in window.findChildren(QPushButton, "windowButton") if b.text() == "—")

        qtbot.mouseClick(minimize_button, Qt.MouseButton.LeftButton)

        assert window.isMinimized() is True

    def test_toggle_maximize_switches_window_state(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window", initial_size=(800, 600))
        qtbot.addWidget(window)
        window.show()

        assert window.isMaximized() is False

        window.toggle_maximize()
        assert window.isMaximized() is True

        window.toggle_maximize()
        assert window.isMaximized() is False

    def test_maximize_button_maximizes_window(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window")
        qtbot.addWidget(window)
        window.show()

        maximize_button = next(
            b for b in window.findChildren(QPushButton, "windowButton") if not b.icon().isNull()
        )

        qtbot.mouseClick(maximize_button, Qt.MouseButton.LeftButton)

        assert window.isMaximized() is True

    def test_resize_border_margin_collapses_when_maximized(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window")
        qtbot.addWidget(window)
        window.show()

        assert window._outer_layout.contentsMargins().left() == RESIZE_BORDER

        window.toggle_maximize()
        assert window._outer_layout.contentsMargins().left() == 0

        window.toggle_maximize()
        assert window._outer_layout.contentsMargins().left() == RESIZE_BORDER

    def test_set_content_swaps_the_displayed_widget(self, qtbot):
        first_content = QLabel("first")
        window = FramelessWindow(first_content, title="Test Window")
        qtbot.addWidget(window)
        window.show()

        second_content = QLabel("second")
        window.set_content(second_content)

        assert window._content is second_content
        assert second_content.parent() is not None
        assert second_content.isVisible() is True

    def test_applies_initial_size(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window", initial_size=(800, 600))
        qtbot.addWidget(window)
        window.show()

        assert window.width() == 800
        assert window.height() == 600

    def test_has_a_sane_minimum_size(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window")
        qtbot.addWidget(window)

        assert window.minimumWidth() == MIN_WINDOW_WIDTH
        assert window.minimumHeight() == MIN_WINDOW_HEIGHT

    def test_dragging_bottom_right_corner_resizes_window(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window", initial_size=(800, 600))
        qtbot.addWidget(window)
        window.show()

        start_width = window.width()
        start_height = window.height()

        corner = QPoint(window.width() - 4, window.height() - 4)
        target = corner + QPoint(50, 40)

        qtbot.mousePress(window, Qt.MouseButton.LeftButton, pos=corner)
        qtbot.mouseMove(window, pos=target)
        qtbot.mouseRelease(window, Qt.MouseButton.LeftButton, pos=target)

        assert window.width() >= start_width + 40
        assert window.height() >= start_height + 30

    def test_dragging_does_not_shrink_below_minimum_size(self, qtbot):
        window = FramelessWindow(QLabel("content"), title="Test Window", initial_size=(800, 600))
        qtbot.addWidget(window)
        window.show()

        corner = QPoint(window.width() - 4, window.height() - 4)
        target = QPoint(10, 10)

        qtbot.mousePress(window, Qt.MouseButton.LeftButton, pos=corner)
        qtbot.mouseMove(window, pos=target)
        qtbot.mouseRelease(window, Qt.MouseButton.LeftButton, pos=target)

        assert window.width() >= MIN_WINDOW_WIDTH
        assert window.height() >= MIN_WINDOW_HEIGHT
