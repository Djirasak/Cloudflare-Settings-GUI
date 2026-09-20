import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from cloudflare_settings_gui.resources import resource_path
from cloudflare_settings_gui.ui.authentication_page import AuthenticationPage
from cloudflare_settings_gui.ui.frameless_window import FramelessWindow
from cloudflare_settings_gui.ui.style import APP_STYLESHEET


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLESHEET)
    app.setWindowIcon(QIcon(str(resource_path("assets", "cloudflare_mark.svg"))))

    window = FramelessWindow(AuthenticationPage(), title="Cloudflare Settings GUI")
    window.show()

    sys.exit(app.exec())
