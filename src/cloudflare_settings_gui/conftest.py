import pytest

from cloudflare_settings_gui.ui.pages.permission_config import permission_config_page as permission_config_page_module


@pytest.fixture(autouse=True)
def fake_credential_store(monkeypatch):
    store = {"email": "", "account_id": "", "api_token": ""}

    def fake_load():
        return dict(store)

    def fake_save(email, account_id, api_token):
        store["email"] = email
        store["account_id"] = account_id
        store["api_token"] = api_token

    def fake_clear():
        store["email"] = ""
        store["account_id"] = ""
        store["api_token"] = ""

    monkeypatch.setattr(permission_config_page_module, "load_credentials", fake_load)
    monkeypatch.setattr(permission_config_page_module, "save_credentials", fake_save)
    monkeypatch.setattr(permission_config_page_module, "clear_credentials", fake_clear)
    return store
