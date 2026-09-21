from PyQt6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget

from cloudflare_settings_gui.ui.pages.main.partials.tunnels import TunnelsPartial

TAB_TITLES = ("Tunnel", "DDNS")


class LeftPanelPartial(QWidget):
    """The left-hand tabbed panel — each tab is a placeholder until its feature lands."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("mainLeftPanel")

        self._tunnels = TunnelsPartial()

        self._tabs = QTabWidget()
        self._tabs.setObjectName("leftPanelTabs")
        self._tabs.addTab(self._tunnels, TAB_TITLES[0])
        self._tabs.addTab(self._build_placeholder_tab(), TAB_TITLES[1])

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)
        layout.addWidget(self._tabs)

    def load_tunnels(self, account_id: str, api_token: str) -> None:
        self._tunnels.load_tunnels(account_id, api_token)

    def _build_placeholder_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("เร็ว ๆ นี้")
        label.setObjectName("subtitle")
        layout.addWidget(label)
        layout.addStretch(1)
        return tab
