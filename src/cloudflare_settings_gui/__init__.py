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

    main_page = MainPage()
    window = FramelessWindow(main_page, title="Cloudflare Settings GUI", initial_size=(1440, 900))
    window.show()

    def show_auth_dialog() -> None:
        saved = load_credentials()
        has_saved_credentials = all(saved.values())
        auth_content = PermissionLoadingPage() if has_saved_credentials else PermissionConfigPage()
        auth_dialog = AuthFlowDialog(auth_content, parent=window)

        def finish(account_id: str, api_token: str) -> None:
            main_page.load_domains(account_id, api_token)
            auth_dialog.accept()

        def show_permission_loading(account_id: str, api_token: str) -> None:
            loading_page = PermissionLoadingPage()
            loading_page.finished.connect(lambda: finish(account_id, api_token))
            auth_dialog.set_content(loading_page)

        if isinstance(auth_content, PermissionLoadingPage):
            auth_content.finished.connect(lambda: finish(saved["account_id"], saved["api_token"]))
        else:
            auth_content.continue_requested.connect(show_permission_loading)
            auth_content.close_requested.connect(app.quit)

        auth_dialog.show()

    # Deferred so `window` has already been placed on screen by the window manager
    # before the dialog centers itself on it — otherwise frameGeometry() is stale.
    QTimer.singleShot(0, show_auth_dialog)

    sys.exit(app.exec())
