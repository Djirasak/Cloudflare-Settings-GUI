from PyQt6.QtWidgets import QLabel

from cloudflare_settings_gui.ui.pages.main.main_page import MainPage


class TestMainPage:
    def test_shows_hello_label(self, qtbot):
        page = MainPage()
        qtbot.addWidget(page)

        labels = [label.text() for label in page.findChildren(QLabel)]
        assert "Hello" in labels
