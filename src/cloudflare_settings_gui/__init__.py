import sys

from dotenv import load_dotenv
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from cloudflare_settings_gui.credentials import load_credentials
from cloudflare_settings_gui.resources import resource_path
from cloudflare_settings_gui.ui.components.auth_flow_dialog import AuthFlowDialog
from cloudflare_settings_gui.ui.components.frameless_window import FramelessWindow
from cloudflare_settings_gui.ui.pages.main.main_page import MainPage
from cloudflare_settings_gui.ui.pages.permission_config.permission_config_page import PermissionConfigPage
from cloudflare_settings_gui.ui.pages.permission_loading.permission_loading_page import PermissionLoadingPage
from cloudflare_settings_gui.ui.style import build_stylesheet


def main() -> None:
    load_dotenv()

    app = QApplication(sys.argv)
    check_icon_path = str(resource_path("assets", "check_mark.svg")).replace("\\", "/")
    app.setStyleSheet(build_stylesheet(check_icon_path))
    app.setWindowIcon(QIcon(str(resource_path("assets", "cloudflare_mark.svg"))))

    window = FramelessWindow(MainPage(), title="Cloudflare Settings GUI", initial_size=(1440, 900))
    window.show()

    def show_auth_dialog() -> None:
        has_saved_credentials = all(load_credentials().values())
        auth_content = PermissionLoadingPage() if has_saved_credentials else PermissionConfigPage()
        auth_dialog = AuthFlowDialog(auth_content, parent=window)

        if isinstance(auth_content, PermissionLoadingPage):
            auth_content.finished.connect(auth_dialog.accept)
        else:
            auth_content.continue_requested.connect(auth_dialog.accept)

        auth_dialog.show()

    # Deferred so `window` has already been placed on screen by the window manager
    # before the dialog centers itself on it — otherwise frameGeometry() is stale.
    QTimer.singleShot(0, show_auth_dialog)

    sys.exit(app.exec())
