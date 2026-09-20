from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from cloudflare_settings_gui.services.cloudflare.facade import DomainInfo
from cloudflare_settings_gui.ui.components.toggle_switch import ToggleSwitch

ACTIVE_STATUS = "active"


class DomainCard(QFrame):
    """Displays one domain and raises intent signals — it never talks to the API itself."""

    dev_mode_toggled = pyqtSignal(bool)
    purge_cache_requested = pyqtSignal()

    def __init__(self, domain: DomainInfo) -> None:
        super().__init__()
        self.setObjectName("domainCard")

        is_active = domain.status == ACTIVE_STATUS
        self.setProperty("active", is_active)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        status_badge = QLabel(domain.status)
        status_badge.setObjectName("statusBadgeActive" if is_active else "statusBadgePending")

        name = QLabel(domain.name)
        name.setObjectName("domainName")
        name.setWordWrap(True)

        dev_mode_label = QLabel("Development Mode")
        dev_mode_label.setObjectName("fieldLabel")

        self._dev_mode_switch = ToggleSwitch()
        self._dev_mode_switch.setChecked(domain.dev_mode_enabled)
        self._dev_mode_switch.toggled.connect(self.dev_mode_toggled.emit)

        dev_mode_row = QHBoxLayout()
        dev_mode_row.setSpacing(8)
        dev_mode_row.addWidget(dev_mode_label)
        dev_mode_row.addStretch(1)
        dev_mode_row.addWidget(self._dev_mode_switch)

        purge_cache_button = QPushButton("ล้างแคช")
        purge_cache_button.setObjectName("secondary")
        purge_cache_button.setCursor(Qt.CursorShape.PointingHandCursor)
        purge_cache_button.clicked.connect(self.purge_cache_requested.emit)

        layout.addWidget(status_badge, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(name)
        layout.addSpacing(4)
        layout.addLayout(dev_mode_row)
        layout.addWidget(purge_cache_button)

    def set_dev_mode_checked(self, checked: bool) -> None:
        self._dev_mode_switch.blockSignals(True)
        self._dev_mode_switch.setChecked(checked)
        self._dev_mode_switch.blockSignals(False)
