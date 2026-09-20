import json

import httpx
from cloudflare import Cloudflare
from cloudflare.types.accounts.account import Account
from cloudflare.types.user.token_verify_response import TokenVerifyResponse
from cloudflare.types.zones.zone import Zone

_RESET = "\033[0m"
_DIM = "\033[2m"
_CYAN = "\033[36m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_RED = "\033[31m"


def _pretty_body(content: bytes) -> str:
    if not content:
        return ""
    try:
        return json.dumps(json.loads(content), indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return content.decode(errors="replace")


def _status_color(status_code: int) -> str:
    if status_code < 300:
        return _GREEN
    if status_code < 400:
        return _YELLOW
    return _RED


def _log_request(request: httpx.Request) -> None:
    print(f"\n{_CYAN}--> {request.method} {request.url}{_RESET}")
    body = _pretty_body(request.content)
    if body:
        print(f"{_DIM}{body}{_RESET}")


def _log_response(response: httpx.Response) -> None:
    response.read()
    color = _status_color(response.status_code)
    print(f"{color}<-- {response.status_code} {response.reason_phrase}{_RESET}")
    body = _pretty_body(response.content)
    if body:
        print(f"{_DIM}{body}{_RESET}")


class CloudflareGateway:
    """Thin wrapper around the Cloudflare SDK client — raw API calls, no business logic."""

    def __init__(self, api_token: str) -> None:
        http_client = httpx.Client(event_hooks={"request": [_log_request], "response": [_log_response]})
        self._client = Cloudflare(api_token=api_token, http_client=http_client)
        # SDK falls back to CLOUDFLARE_EMAIL/API_KEY env vars when unset, and prioritizes
        # that legacy auth over our Bearer token if api_email ends up non-None (our .env
        # sets it for UI prefill). Setting api_email=None here wouldn't help — None is what
        # triggers the env fallback — so clear both post-construction instead.
        self._client.api_email = None
        self._client.api_key = None

    def verify_token(self) -> TokenVerifyResponse | None:
        return self._client.user.tokens.verify()

    def get_account(self, account_id: str) -> Account | None:
        return self._client.accounts.get(account_id=account_id)

    def list_zones(self, account_id: str) -> list[Zone]:
        return list(self._client.zones.list(account={"id": account_id}))

    def set_development_mode(self, zone_id: str, enabled: bool) -> None:
        value = "on" if enabled else "off"
        self._client.zones.settings.edit(setting_id="development_mode", zone_id=zone_id, value=value)

    def purge_cache(self, zone_id: str) -> None:
        self._client.cache.purge(zone_id=zone_id, purge_everything=True)
