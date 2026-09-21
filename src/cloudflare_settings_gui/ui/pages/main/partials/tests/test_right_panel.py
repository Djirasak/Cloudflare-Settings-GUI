from unittest.mock import patch

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QPushButton

from cloudflare_settings_gui.services.cloudflare.facade import (
    DevelopmentModeResult,
    DomainInfo,
    PurgeCacheResult,
    ZoneListResult,
)
from cloudflare_settings_gui.ui.components.toggle_switch import ToggleSwitch
from cloudflare_settings_gui.ui.pages.main.partials.domain_sidebar import DomainSidebarPartial

WAIT_TIMEOUT_MS = 2000


def _make_sidebar(qtbot) -> DomainSidebarPartial:
    sidebar = DomainSidebarPartial()
    qtbot.addWidget(sidebar)
    sidebar.show()
    return sidebar


def _patch_facade():
    return patch("cloudflare_settings_gui.ui.pages.main.partials.domain_sidebar.CloudflareFacade")


def _load_domains(qtbot, sidebar: DomainSidebarPartial, mock_facade_cls, domains: list[DomainInfo]) -> None:
    mock_facade_cls.return_value.list_zones.return_value = ZoneListResult(domains=domains)
    sidebar.load_domains("account-123", "token-abc")
    qtbot.waitUntil(lambda: sidebar._domain_list.count() == len(domains), timeout=WAIT_TIMEOUT_MS)


def _domain_card(sidebar: DomainSidebarPartial, index: int):
    return sidebar._domain_list.itemWidget(sidebar._domain_list.item(index))


class TestDomainSidebarLoadDomains:
    def test_populates_domain_list_on_success(self, qtbot):
        sidebar = _make_sidebar(qtbot)

        with _patch_facade() as mock_facade_cls:
            _load_domains(
                qtbot,
                sidebar,
                mock_facade_cls,
                [
                    DomainInfo(zone_id="zone-1", name="example.com", status="active"),
                    DomainInfo(zone_id="zone-2", name="example.org", status="pending"),
                ],
            )

            mock_facade_cls.assert_called_once_with("token-abc")
            mock_facade_cls.return_value.list_zones.assert_called_once_with("account-123")

        assert _domain_card(sidebar, 0).findChild(QLabel, "domainName").text() == "example.com"
        qtbot.waitUntil(lambda: sidebar._status_label.isVisible() is False, timeout=WAIT_TIMEOUT_MS)

    def test_shows_error_message_on_failure(self, qtbot):
        sidebar = _make_sidebar(qtbot)

        with _patch_facade() as mock_facade_cls:
            mock_facade_cls.return_value.list_zones.return_value = ZoneListResult(error="เชื่อมต่อ API ไม่สำเร็จ")
            sidebar.load_domains("account-123", "token-abc")

            qtbot.waitUntil(lambda: sidebar._status_label.objectName() == "statusError", timeout=WAIT_TIMEOUT_MS)

        assert sidebar._domain_list.count() == 0
        assert "เชื่อมต่อ API ไม่สำเร็จ" in sidebar._status_label.text()

    def test_shows_empty_message_when_no_domains(self, qtbot):
        sidebar = _make_sidebar(qtbot)

        with _patch_facade() as mock_facade_cls:
            mock_facade_cls.return_value.list_zones.return_value = ZoneListResult(domains=[])
            sidebar.load_domains("account-123", "token-abc")

            qtbot.waitUntil(lambda: sidebar._status_label.isVisible() is True, timeout=WAIT_TIMEOUT_MS)

        assert sidebar._domain_list.count() == 0


class TestDomainCardActions:
    def test_dev_mode_toggle_calls_facade_and_emits_success_feedback(self, qtbot):
        sidebar = _make_sidebar(qtbot)

        with _patch_facade() as mock_facade_cls:
            _load_domains(
                qtbot, sidebar, mock_facade_cls, [DomainInfo(zone_id="zone-1", name="example.com", status="active")]
            )
            mock_facade_cls.return_value.set_development_mode.return_value = DevelopmentModeResult(success=True)

            switch = _domain_card(sidebar, 0).findChild(ToggleSwitch)
            with qtbot.waitSignal(sidebar.action_feedback, timeout=WAIT_TIMEOUT_MS) as blocker:
                qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)

        mock_facade_cls.return_value.set_development_mode.assert_called_once_with("zone-1", True)
        assert switch.isChecked() is True
        assert blocker.args[0] is True

    def test_dev_mode_toggle_reverts_and_emits_error_feedback_on_failure(self, qtbot):
        sidebar = _make_sidebar(qtbot)

        with _patch_facade() as mock_facade_cls:
            _load_domains(
                qtbot, sidebar, mock_facade_cls, [DomainInfo(zone_id="zone-1", name="example.com", status="active")]
            )
            mock_facade_cls.return_value.set_development_mode.return_value = DevelopmentModeResult(
                error="เชื่อมต่อ API ไม่สำเร็จ"
            )

            switch = _domain_card(sidebar, 0).findChild(ToggleSwitch)
            with qtbot.waitSignal(sidebar.action_feedback, timeout=WAIT_TIMEOUT_MS) as blocker:
                qtbot.mouseClick(switch, Qt.MouseButton.LeftButton)

        assert switch.isChecked() is False
        assert blocker.args == [False, "เชื่อมต่อ API ไม่สำเร็จ"]

    def test_purge_cache_button_emits_success_feedback(self, qtbot):
        sidebar = _make_sidebar(qtbot)

        with _patch_facade() as mock_facade_cls:
            _load_domains(
                qtbot, sidebar, mock_facade_cls, [DomainInfo(zone_id="zone-1", name="example.com", status="active")]
            )
            mock_facade_cls.return_value.purge_cache.return_value = PurgeCacheResult(success=True)

            button = _domain_card(sidebar, 0).findChild(QPushButton)
            with qtbot.waitSignal(sidebar.action_feedback, timeout=WAIT_TIMEOUT_MS) as blocker:
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        mock_facade_cls.return_value.purge_cache.assert_called_once_with("zone-1")
        assert blocker.args == [True, "ล้างแคชสำเร็จ — example.com"]

    def test_purge_cache_button_emits_error_feedback(self, qtbot):
        sidebar = _make_sidebar(qtbot)

        with _patch_facade() as mock_facade_cls:
            _load_domains(
                qtbot, sidebar, mock_facade_cls, [DomainInfo(zone_id="zone-1", name="example.com", status="active")]
            )
            mock_facade_cls.return_value.purge_cache.return_value = PurgeCacheResult(error="เชื่อมต่อ API ไม่สำเร็จ")

            button = _domain_card(sidebar, 0).findChild(QPushButton)
            with qtbot.waitSignal(sidebar.action_feedback, timeout=WAIT_TIMEOUT_MS) as blocker:
                qtbot.mouseClick(button, Qt.MouseButton.LeftButton)

        assert blocker.args == [False, "เชื่อมต่อ API ไม่สำเร็จ"]
