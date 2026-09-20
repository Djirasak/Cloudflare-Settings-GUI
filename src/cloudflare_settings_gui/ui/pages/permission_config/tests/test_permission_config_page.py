from PyQt6.QtCore import Qt

from cloudflare_settings_gui.ui.pages.permission_config.permission_config_page import PermissionConfigPage


class TestPermissionConfigPage:
    def _make_page(self, qtbot) -> PermissionConfigPage:
        page = PermissionConfigPage()
        qtbot.addWidget(page)
        page.show()
        return page

    def test_initial_state_is_pending_with_continue_enabled(self, qtbot):
        page = self._make_page(qtbot)

        assert page._status_label.objectName() == "statusPending"
        assert page._continue_button.isEnabled() is True

    def test_continue_with_empty_fields_shows_error(self, qtbot):
        page = self._make_page(qtbot)

        qtbot.mouseClick(page._continue_button, Qt.MouseButton.LeftButton)

        assert page._status_label.objectName() == "statusError"

    def test_continue_with_partial_fields_shows_error(self, qtbot):
        page = self._make_page(qtbot)

        qtbot.keyClicks(page._email_input, "user@example.com")
        qtbot.keyClicks(page._account_id_input, "account-123")

        qtbot.mouseClick(page._continue_button, Qt.MouseButton.LeftButton)

        assert page._status_label.objectName() == "statusError"

    def test_continue_button_emits_continue_requested(self, qtbot):
        page = self._make_page(qtbot)

        qtbot.keyClicks(page._email_input, "user@example.com")
        qtbot.keyClicks(page._account_id_input, "account-123")
        qtbot.keyClicks(page._token_input, "token-abc")

        with qtbot.waitSignal(page.continue_requested, timeout=1000) as blocker:
            qtbot.mouseClick(page._continue_button, Qt.MouseButton.LeftButton)

        assert blocker.args == ["account-123", "token-abc"]

    def test_return_pressed_in_any_field_triggers_continue(self, qtbot):
        page = self._make_page(qtbot)

        qtbot.keyClicks(page._email_input, "user@example.com")
        qtbot.keyClicks(page._account_id_input, "account-123")
        qtbot.keyClicks(page._token_input, "token-abc")

        with qtbot.waitSignal(page.continue_requested, timeout=1000):
            qtbot.keyClick(page._token_input, Qt.Key.Key_Return)

    def test_close_button_emits_close_requested(self, qtbot):
        page = self._make_page(qtbot)

        with qtbot.waitSignal(page.close_requested, timeout=1000):
            qtbot.mouseClick(page._close_button, Qt.MouseButton.LeftButton)

    def test_remember_checkbox_unchecked_by_default_with_no_saved_credentials(self, qtbot):
        page = self._make_page(qtbot)

        assert page._remember_checkbox.isChecked() is False

    def test_prefill_loads_saved_credentials_and_checks_remember_box(self, qtbot, fake_credential_store):
        fake_credential_store["email"] = "saved@example.com"
        fake_credential_store["account_id"] = "saved-account"
        fake_credential_store["api_token"] = "saved-token"

        page = self._make_page(qtbot)

        assert page._email_input.text() == "saved@example.com"
        assert page._account_id_input.text() == "saved-account"
        assert page._token_input.text() == "saved-token"
        assert page._remember_checkbox.isChecked() is True

    def test_continue_saves_credentials_when_remember_checked(self, qtbot, fake_credential_store):
        page = self._make_page(qtbot)
        page._remember_checkbox.setChecked(True)

        qtbot.keyClicks(page._email_input, "user@example.com")
        qtbot.keyClicks(page._account_id_input, "account-123")
        qtbot.keyClicks(page._token_input, "token-abc")
        qtbot.mouseClick(page._continue_button, Qt.MouseButton.LeftButton)

        assert fake_credential_store == {
            "email": "user@example.com",
            "account_id": "account-123",
            "api_token": "token-abc",
        }

    def test_continue_clears_credentials_when_remember_unchecked(self, qtbot, fake_credential_store):
        fake_credential_store["email"] = "old@example.com"
        fake_credential_store["account_id"] = "old-account"
        fake_credential_store["api_token"] = "old-token"

        page = self._make_page(qtbot)
        page._remember_checkbox.setChecked(False)
        qtbot.keyClicks(page._email_input, "user@example.com")
        qtbot.keyClicks(page._account_id_input, "account-123")
        qtbot.keyClicks(page._token_input, "token-abc")
        qtbot.mouseClick(page._continue_button, Qt.MouseButton.LeftButton)

        assert fake_credential_store == {"email": "", "account_id": "", "api_token": ""}
