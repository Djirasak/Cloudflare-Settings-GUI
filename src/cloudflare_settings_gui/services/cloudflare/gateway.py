from cloudflare import Cloudflare
from cloudflare.types.accounts.account import Account
from cloudflare.types.user.token_verify_response import TokenVerifyResponse
from cloudflare.types.zones.zone import Zone


class CloudflareGateway:
    """Thin wrapper around the Cloudflare SDK client — raw API calls, no business logic."""

    def __init__(self, api_token: str) -> None:
        self._client = Cloudflare(api_token=api_token)

    def verify_token(self) -> TokenVerifyResponse | None:
        return self._client.user.tokens.verify()

    def get_account(self, account_id: str) -> Account | None:
        return self._client.accounts.get(account_id=account_id)

    def list_zones(self, account_id: str) -> list[Zone]:
        return list(self._client.zones.list(account={"id": account_id}))
