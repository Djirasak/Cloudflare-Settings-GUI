import sys

import keyring
import keyring.errors

SERVICE_NAME = "cloudflare-settings-gui"
_FIELDS = ("email", "account_id", "api_token")
_TOKEN_ID_FIELD = "token_id"


def save_credentials(email: str, account_id: str, api_token: str) -> None:
    keyring.set_password(SERVICE_NAME, "email", email)
    keyring.set_password(SERVICE_NAME, "account_id", account_id)
    keyring.set_password(SERVICE_NAME, "api_token", api_token)


def load_credentials() -> dict[str, str]:
    return {field: keyring.get_password(SERVICE_NAME, field) or "" for field in _FIELDS}


def save_token_id(token_id: str) -> None:
    keyring.set_password(SERVICE_NAME, _TOKEN_ID_FIELD, token_id)


def load_token_id() -> str:
    return keyring.get_password(SERVICE_NAME, _TOKEN_ID_FIELD) or ""


def clear_credentials() -> None:
    for field in (*_FIELDS, _TOKEN_ID_FIELD):
        try:
            keyring.delete_password(SERVICE_NAME, field)
        except keyring.errors.PasswordDeleteError:
            pass


def clear_saved_credentials_cli() -> None:
    """Entry point for the `cleanup` console script."""
    clear_credentials()
    # Windows terminals often default to a legacy codepage (e.g. cp1252) that can't
    # encode Thai text, crashing a plain print() — reconfigure to UTF-8 first so this
    # works from cmd.exe, PowerShell, or a double-clicked .bat file alike.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("ล้างข้อมูลที่จดจำไว้ใน Windows Credential Manager เรียบร้อยแล้ว")
