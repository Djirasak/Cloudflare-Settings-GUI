import keyring
import keyring.errors
import pytest

from cloudflare_settings_gui.credentials import (
    clear_credentials,
    load_credentials,
    load_token_id,
    save_credentials,
    save_token_id,
)


class TestCredentials:
    @pytest.fixture(autouse=True)
    def in_memory_keyring(self, monkeypatch):
        store: dict[tuple[str, str], str] = {}

        def fake_set_password(service, username, password):
            store[(service, username)] = password

        def fake_get_password(service, username):
            return store.get((service, username))

        def fake_delete_password(service, username):
            if (service, username) not in store:
                raise keyring.errors.PasswordDeleteError("not found")
            del store[(service, username)]

        monkeypatch.setattr(keyring, "set_password", fake_set_password)
        monkeypatch.setattr(keyring, "get_password", fake_get_password)
        monkeypatch.setattr(keyring, "delete_password", fake_delete_password)
        return store

    def test_save_and_load_round_trip(self):
        save_credentials("user@example.com", "account-123", "token-abc")

        assert load_credentials() == {
            "email": "user@example.com",
            "account_id": "account-123",
            "api_token": "token-abc",
        }

    def test_load_without_saved_credentials_returns_empty_strings(self):
        assert load_credentials() == {"email": "", "account_id": "", "api_token": ""}

    def test_clear_credentials_removes_saved_values(self):
        save_credentials("user@example.com", "account-123", "token-abc")

        clear_credentials()

        assert load_credentials() == {"email": "", "account_id": "", "api_token": ""}

    def test_clear_credentials_is_safe_when_nothing_saved(self):
        clear_credentials()

    def test_save_and_load_token_id_round_trip(self):
        save_token_id("token-id-123")

        assert load_token_id() == "token-id-123"

    def test_load_token_id_without_saved_value_returns_empty_string(self):
        assert load_token_id() == ""

    def test_clear_credentials_removes_saved_token_id(self):
        save_token_id("token-id-123")

        clear_credentials()

        assert load_token_id() == ""
