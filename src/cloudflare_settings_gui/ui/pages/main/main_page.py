from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from cloudflare_settings_gui.ui.components.toast import Toast
from cloudflare_settings_gui.ui.pages.main.partials.left_panel import LeftPanelPartial
from cloudflare_settings_gui.ui.pages.main.partials.right_panel import RightPanelPartial

LEFT_PANEL_STRETCH = 7
RIGHT_PANEL_STRETCH = 3


class MainPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("page")
        self.setMinimumWidth(420)

        self._left_panel = LeftPanelPartial()
        self._right_panel = RightPanelPartial()
        self._toast = Toast()

        self._panels_layout = QHBoxLayout()
        self._panels_layout.setContentsMargins(0, 0, 0, 0)
        self._panels_layout.setSpacing(0)
        self._panels_layout.addWidget(self._left_panel, LEFT_PANEL_STRETCH)
        self._panels_layout.addWidget(self._right_panel, RIGHT_PANEL_STRETCH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(self._panels_layout)
        layout.addWidget(self._toast)

        self._right_panel.action_feedback.connect(self._on_action_feedback)

    def _on_action_feedback(self, success: bool, message: str) -> None:
        if success:
            self._toast.show_success(message)
        else:
            self._toast.show_error(message)

    def load_account_data(self, account_id: str, api_token: str) -> None:
        self._left_panel.load_tunnels(account_id, api_token)
        self._right_panel.load_domains(account_id, api_token)
