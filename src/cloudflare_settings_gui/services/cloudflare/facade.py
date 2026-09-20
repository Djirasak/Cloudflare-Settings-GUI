from dataclasses import dataclass

from cloudflare import CloudflareError

from cloudflare_settings_gui.services.cloudflare.gateway import CloudflareGateway

ACTIVE_TOKEN_STATUS = "active"


@dataclass
class CredentialCheckResult:
    is_valid: bool
    account_name: str = ""
    zone_count: int = 0
    error: str = ""


class CloudflareFacade:
    """App-facing entry point for Cloudflare operations.

    Wraps CloudflareGateway calls into simple, UI-friendly results and never lets
    SDK exceptions escape — callers only ever see a CredentialCheckResult.
    """

    def __init__(self, api_token: str) -> None:
        self._gateway = CloudflareGateway(api_token)

    def check_credentials(self, account_id: str) -> CredentialCheckResult:
        try:
            token_status = self._gateway.verify_token()
            if token_status is None or token_status.status != ACTIVE_TOKEN_STATUS:
                return CredentialCheckResult(is_valid=False, error="API token ไม่ถูกต้องหรือหมดอายุ")

            account = self._gateway.get_account(account_id)
            if account is None:
                return CredentialCheckResult(is_valid=False, error="ไม่พบ Account ID นี้")

            zones = self._gateway.list_zones(account_id)
            return CredentialCheckResult(is_valid=True, account_name=account.name, zone_count=len(zones))
        except CloudflareError as error:
            return CredentialCheckResult(is_valid=False, error=str(error))
