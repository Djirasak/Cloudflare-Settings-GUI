from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from cloudflare_settings_gui.ui.components.toast import Toast
from cloudflare_settings_gui.ui.pages.main.partials.domain_sidebar import DomainSidebarPartial

LEFT_PANEL_STRETCH = 8
RIGHT_PANEL_STRETCH = 2


class MainPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("page")
        self.setMinimumWidth(420)

        self._domain_sidebar = DomainSidebarPartial()
        self._toast = Toast()

        self._panels_layout = QHBoxLayout()
        self._panels_layout.setContentsMargins(0, 0, 0, 0)
        self._panels_layout.setSpacing(0)
        self._panels_layout.addWidget(self._build_left_panel(), LEFT_PANEL_STRETCH)
        self._panels_layout.addWidget(self._domain_sidebar, RIGHT_PANEL_STRETCH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(self._panels_layout)
        layout.addWidget(self._toast)

        self._domain_sidebar.action_feedback.connect(self._on_action_feedback)

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("mainLeftPanel")
        return panel

    def _on_action_feedback(self, success: bool, message: str) -> None:
        if success:
            self._toast.show_success(message)
        else:
            self._toast.show_error(message)

    def load_domains(self, account_id: str, api_token: str) -> None:
        self._domain_sidebar.load_domains(account_id, api_token)
