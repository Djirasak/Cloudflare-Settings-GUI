from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QPushButton

from cloudflare_settings_gui.ui.frameless_window import FramelessWindow


def test_sets_window_title_and_icon(qtbot):
    window = FramelessWindow(QLabel("content"), title="Test Window")
    qtbot.addWidget(window)

    assert window.windowTitle() == "Test Window"
    assert not window.windowIcon().isNull()


def test_close_button_closes_window(qtbot):
    window = FramelessWindow(QLabel("content"), title="Test Window")
    qtbot.addWidget(window)
    window.show()

    close_button = window.findChild(QPushButton, "windowCloseButton")
    assert close_button is not None

    qtbot.mouseClick(close_button, Qt.MouseButton.LeftButton)

    assert window.isVisible() is False


def test_minimize_button_minimizes_window(qtbot):
    window = FramelessWindow(QLabel("content"), title="Test Window")
    qtbot.addWidget(window)
    window.show()

    minimize_button = window.findChild(QPushButton, "windowButton")
    assert minimize_button is not None

    qtbot.mouseClick(minimize_button, Qt.MouseButton.LeftButton)

    assert window.isMinimized() is True
