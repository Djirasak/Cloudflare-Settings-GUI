from PyQt6.QtCore import Qt

from cloudflare_settings_gui.ui.authentication_page import (
    MOCK_VERIFY_DELAY_MS,
    MOCK_ZONE_COUNT,
    AuthenticationPage,
)


def test_initial_state_is_pending_with_continue_disabled(qtbot):
    page = AuthenticationPage()
    qtbot.addWidget(page)

    assert page._status_label.objectName() == "statusPending"
    assert page._continue_button.isEnabled() is False


def test_verify_with_empty_fields_shows_error(qtbot):
    page = AuthenticationPage()
    qtbot.addWidget(page)

    qtbot.mouseClick(page._verify_button, Qt.MouseButton.LeftButton)

    assert page._status_label.objectName() == "statusError"
    assert page._continue_button.isEnabled() is False


def test_verify_with_partial_fields_shows_error(qtbot):
    page = AuthenticationPage()
    qtbot.addWidget(page)

    qtbot.keyClicks(page._email_input, "user@example.com")
    qtbot.keyClicks(page._account_id_input, "account-123")
    # API token left empty

    qtbot.mouseClick(page._verify_button, Qt.MouseButton.LeftButton)

    assert page._status_label.objectName() == "statusError"
    assert page._continue_button.isEnabled() is False


def test_verify_with_all_fields_filled_succeeds(qtbot):
    page = AuthenticationPage()
    qtbot.addWidget(page)

    qtbot.keyClicks(page._email_input, "user@example.com")
    qtbot.keyClicks(page._account_id_input, "account-123")
    qtbot.keyClicks(page._token_input, "token-abc")

    qtbot.mouseClick(page._verify_button, Qt.MouseButton.LeftButton)

    assert page._verify_button.isEnabled() is False
    assert page._continue_button.isEnabled() is False
    assert page._status_label.objectName() == "statusPending"

    qtbot.wait(MOCK_VERIFY_DELAY_MS + 200)

    assert page._verify_button.isEnabled() is True
    assert page._continue_button.isEnabled() is True
    assert page._status_label.objectName() == "statusOk"
    assert str(MOCK_ZONE_COUNT) in page._status_label.text()


def test_return_pressed_in_any_field_triggers_verify(qtbot):
    page = AuthenticationPage()
    qtbot.addWidget(page)

    qtbot.keyClicks(page._email_input, "user@example.com")
    qtbot.keyClicks(page._account_id_input, "account-123")
    qtbot.keyClicks(page._token_input, "token-abc")
    qtbot.keyClick(page._token_input, Qt.Key.Key_Return)

    assert page._verify_button.isEnabled() is False
