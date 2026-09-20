import keyring
import keyring.errors

SERVICE_NAME = "cloudflare-settings-gui"
_FIELDS = ("email", "account_id", "api_token")


def save_credentials(email: str, account_id: str, api_token: str) -> None:
    keyring.set_password(SERVICE_NAME, "email", email)
    keyring.set_password(SERVICE_NAME, "account_id", account_id)
    keyring.set_password(SERVICE_NAME, "api_token", api_token)


def load_credentials() -> dict[str, str]:
    return {field: keyring.get_password(SERVICE_NAME, field) or "" for field in _FIELDS}


def clear_credentials() -> None:
    for field in _FIELDS:
        try:
            keyring.delete_password(SERVICE_NAME, field)
        except keyring.errors.PasswordDeleteError:
            pass
