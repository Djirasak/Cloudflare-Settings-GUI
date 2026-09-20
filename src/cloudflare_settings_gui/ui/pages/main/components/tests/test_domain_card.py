from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QPushButton

from cloudflare_settings_gui.services.cloudflare.facade import DomainInfo
from cloudflare_settings_gui.ui.components.toggle_switch import ToggleSwitch
from cloudflare_settings_gui.ui.pages.main.components.domain_card import DomainCard


def _make_card(qtbot, status: str = "active", dev_mode_enabled: bool = False) -> DomainCard:
    card = DomainCard(
        DomainInfo(zone_id="zone-1", name="example.com", status=status, dev_mode_enabled=dev_mode_enabled)
    )
    qtbot.addWidget(card)
    card.show()
    return card


class TestDomainCard:
    def test_shows_name_and_status_badge(self, qtbot):
        card = _make_card(qtbot)

        assert card.findChild(QLabel, "domainName").text() == "example.com"
        badge = card.findChild(QLabel, "statusBadgeActive")
        assert badge is not None
        assert badge.text() == "active"

    def test_active_status_gives_card_active_border(self, qtbot):
        card = _make_card(qtbot, status="active")

        assert card.property("active") is True

    def test_dev_mode_switch_reflects_initial_state(self, qtbot):
        assert _make_card(qtbot, dev_mode_enabled=False).findChild(ToggleSwitch).isChecked() is False
        assert _make_card(qtbot, dev_mode_enabled=True).findChild(ToggleSwitch).isChecked() is True

    def test_non_active_status_uses_pending_badge_and_no_active_border(self, qtbot):
        card = _make_card(qtbot, status="pending")

        assert card.findChild(QLabel, "statusBadgePending") is not None
        assert card.findChild(QLabel, "statusBadgeActive") is None
        assert card.property("active") is False

    def test_toggling_switch_emits_dev_mode_toggled(self, qtbot):
        card = _make_card(qtbot)
        switch = card.findChild(ToggleSwitch)

        with qtbot.waitSignal(card.dev_mode_toggled, timeout=1000) as blocker:
            qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)

        assert blocker.args == [True]

    def test_clicking_purge_button_emits_purge_cache_requested(self, qtbot):
        card = _make_card(qtbot)
        button = card.findChild(QPushButton)

        with qtbot.waitSignal(card.purge_cache_requested, timeout=1000):
            qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

    def test_set_dev_mode_checked_does_not_reemit_signal(self, qtbot):
        card = _make_card(qtbot)

        received = []
        card.dev_mode_toggled.connect(received.append)
        card.set_dev_mode_checked(True)

        assert card.findChild(ToggleSwitch).isChecked() is True
        assert received == []
