import sys

from PyQt6.QtWidgets import QApplication

from cloudflare_settings_gui.ui.style import APP_STYLESHEET
from cloudflare_settings_gui.ui.token_page import TokenPage


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)

    window = TokenPage()
    window.show()

    sys.exit(app.exec())
