from dataclasses import dataclass, field

from cloudflare import CloudflareError

from cloudflare_settings_gui.services.cloudflare.gateway import CloudflareGateway

ACTIVE_TOKEN_STATUS = "active"


@dataclass
class CredentialCheckResult:
    is_valid: bool
    account_name: str = ""
    zone_count: int = 0
    error: str = ""


@dataclass
class DomainInfo:
    zone_id: str
    name: str
    status: str
    dev_mode_enabled: bool = False


@dataclass
class ZoneListResult:
    domains: list[DomainInfo] = field(default_factory=list)
    error: str = ""


@dataclass
class DevelopmentModeResult:
    success: bool = False
    error: str = ""


@dataclass
class PurgeCacheResult:
    success: bool = False
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

    def list_zones(self, account_id: str) -> ZoneListResult:
        try:
            zones = self._gateway.list_zones(account_id)
            domains = [
                DomainInfo(
                    zone_id=zone.id or "",
                    name=zone.name,
                    status=zone.status or "",
                    # Positive = seconds until dev mode expires (on); <=0 = off/never enabled.
                    dev_mode_enabled=zone.development_mode > 0,
                )
                for zone in zones
            ]
            return ZoneListResult(domains=domains)
        except CloudflareError as error:
            return ZoneListResult(error=str(error))

    def set_development_mode(self, zone_id: str, enabled: bool) -> DevelopmentModeResult:
        try:
            self._gateway.set_development_mode(zone_id, enabled)
            return DevelopmentModeResult(success=True)
        except CloudflareError as error:
            return DevelopmentModeResult(error=str(error))

    def purge_cache(self, zone_id: str) -> PurgeCacheResult:
        try:
            self._gateway.purge_cache(zone_id)
            return PurgeCacheResult(success=True)
        except CloudflareError as error:
            return PurgeCacheResult(error=str(error))
