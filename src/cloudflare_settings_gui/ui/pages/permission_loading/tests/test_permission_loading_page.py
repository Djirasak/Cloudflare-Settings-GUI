from unittest.mock import patch

from PyQt6.QtWidgets import QLabel, QProgressBar

from cloudflare_settings_gui.services.cloudflare.facade import (
    AccountCheckResult,
    PermissionCheckItem,
    PermissionCheckResult,
    TokenCheckResult,
)
from cloudflare_settings_gui.ui.pages.permission_loading import permission_loading_page as page_module
from cloudflare_settings_gui.ui.pages.permission_loading.permission_loading_page import PermissionLoadingPage

_PASSING_TOKEN = TokenCheckResult(is_valid=True)
_PASSING_ACCOUNT = AccountCheckResult(is_valid=True, account_name="My Account")
_PASSING_PERMISSIONS = PermissionCheckResult(
    is_valid=True,
    items=[PermissionCheckItem(name="Zone Read", granted=True), PermissionCheckItem(name="DNS Read", granted=True)],
)


class TestPermissionLoadingPage:
    def _patch_facade(self):
        return patch("cloudflare_settings_gui.ui.pages.permission_loading.permission_loading_page.CloudflareFacade")

    def _make_page(
        self,
        qtbot,
        mock_facade_cls,
        token_result=_PASSING_TOKEN,
        account_result=_PASSING_ACCOUNT,
        permission_result=_PASSING_PERMISSIONS,
    ) -> PermissionLoadingPage:
        mock_facade = mock_facade_cls.return_value
        mock_facade.check_token.return_value = token_result
        mock_facade.check_account.return_value = account_result
        mock_facade.check_permissions.return_value = permission_result
        page = PermissionLoadingPage("account-123", "token-abc", "กำลังโหลด...")
        qtbot.addWidget(page)
        return page

    def test_shows_spinner_and_message(self, qtbot):
        with self._patch_facade() as mock_facade_cls:
            page = self._make_page(qtbot, mock_facade_cls)

        spinner = page.findChild(QProgressBar, "spinner")
        assert spinner is not None
        assert spinner.minimum() == 0
        assert spinner.maximum() == 0

        labels = [label.text() for label in page.findChildren(QLabel)]
        assert "กำลังโหลด..." in labels

    def test_emits_finished_when_all_steps_pass(self, qtbot, monkeypatch):
        monkeypatch.setattr(page_module, "RESULT_DISPLAY_DELAY_MS", 0)
        with self._patch_facade() as mock_facade_cls:
            page = self._make_page(qtbot, mock_facade_cls)

            with qtbot.waitSignal(page.finished, timeout=1000):
                pass

        assert "✓" in page._token_row.text()
        assert page._token_row.objectName() == "statusOk"
        assert "✓" in page._account_row.text()
        assert page._account_row.objectName() == "statusOk"
        assert "✓" in page._permission_row.text()
        assert page._permission_row.objectName() == "statusOk"

    def test_checks_run_in_order_with_account_id(self, qtbot, monkeypatch):
        monkeypatch.setattr(page_module, "RESULT_DISPLAY_DELAY_MS", 0)
        with self._patch_facade() as mock_facade_cls:
            page = self._make_page(qtbot, mock_facade_cls)

            with qtbot.waitSignal(page.finished, timeout=1000):
                pass

            mock_facade_cls.assert_called_once_with("token-abc")
            mock_facade_cls.return_value.check_token.assert_called_once_with()
            mock_facade_cls.return_value.check_account.assert_called_once_with("account-123")
            mock_facade_cls.return_value.check_permissions.assert_called_once_with()

    def test_renders_a_row_per_permission_item(self, qtbot, monkeypatch):
        monkeypatch.setattr(page_module, "RESULT_DISPLAY_DELAY_MS", 0)
        permission_result = PermissionCheckResult(
            is_valid=False,
            items=[
                PermissionCheckItem(name="Zone Read", granted=True),
                PermissionCheckItem(name="Cache Purge", granted=False),
            ],
            error="API token ขาดสิทธิ์ที่จำเป็น: Cache Purge",
        )
        with self._patch_facade() as mock_facade_cls:
            page = self._make_page(qtbot, mock_facade_cls, permission_result=permission_result)

            with qtbot.waitSignal(page.failed, timeout=1000):
                pass

        rows = [
            page._permission_items_layout.itemAt(i).widget() for i in range(page._permission_items_layout.count())
        ]
        assert [row.text() for row in rows] == ["✓ Zone Read", "✗ Cache Purge"]
        assert rows[0].objectName() == "permissionRowGranted"
        assert rows[1].objectName() == "permissionRowMissing"
        assert page._permission_row.objectName() == "statusError"

    def test_stops_at_token_step_and_never_checks_account_or_permissions(self, qtbot, monkeypatch):
        monkeypatch.setattr(page_module, "RESULT_DISPLAY_DELAY_MS", 0)
        with self._patch_facade() as mock_facade_cls:
            page = self._make_page(
                qtbot, mock_facade_cls, token_result=TokenCheckResult(is_valid=False, error="token หมดอายุ")
            )

            with qtbot.waitSignal(page.failed, timeout=1000) as blocker:
                pass

            mock_facade_cls.return_value.check_account.assert_not_called()
            mock_facade_cls.return_value.check_permissions.assert_not_called()

        assert blocker.args == ["token หมดอายุ"]
        assert page._token_row.objectName() == "statusError"
        assert page._account_row.objectName() == "statusPending"
        assert page._permission_row.objectName() == "statusPending"

    def test_stops_at_account_step_and_never_checks_permissions(self, qtbot, monkeypatch):
        monkeypatch.setattr(page_module, "RESULT_DISPLAY_DELAY_MS", 0)
        with self._patch_facade() as mock_facade_cls:
            page = self._make_page(
                qtbot, mock_facade_cls, account_result=AccountCheckResult(is_valid=False, error="ไม่พบบัญชี")
            )

            with qtbot.waitSignal(page.failed, timeout=1000) as blocker:
                pass

            mock_facade_cls.return_value.check_permissions.assert_not_called()

        assert blocker.args == ["ไม่พบบัญชี"]
        assert page._token_row.objectName() == "statusOk"
        assert page._account_row.objectName() == "statusError"
        assert page._permission_row.objectName() == "statusPending"

    def test_emits_failed_with_permission_error_when_permissions_missing(self, qtbot, monkeypatch):
        monkeypatch.setattr(page_module, "RESULT_DISPLAY_DELAY_MS", 0)
        with self._patch_facade() as mock_facade_cls:
            page = self._make_page(
                qtbot,
                mock_facade_cls,
                permission_result=PermissionCheckResult(is_valid=False, error="ขาดสิทธิ์"),
            )

            with qtbot.waitSignal(page.failed, timeout=1000) as blocker:
                pass

        assert blocker.args == ["ขาดสิทธิ์"]

    def test_emits_failed_when_a_step_raises_unexpectedly(self, qtbot, monkeypatch):
        monkeypatch.setattr(page_module, "RESULT_DISPLAY_DELAY_MS", 0)
        with self._patch_facade() as mock_facade_cls:
            mock_facade_cls.return_value.check_token.side_effect = RuntimeError("network down")
            page = PermissionLoadingPage("account-123", "token-abc")
            qtbot.addWidget(page)

            with qtbot.waitSignal(page.failed, timeout=1000) as blocker:
                pass

        assert blocker.args == ["network down"]
        assert page._token_row.objectName() == "statusError"
