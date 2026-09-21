from dataclasses import dataclass, field

from cloudflare import CloudflareError
from cloudflare.types.shared.token import Token

from cloudflare_settings_gui.credentials import save_token_id
from cloudflare_settings_gui.services.cloudflare.gateway import CloudflareGateway
from cloudflare_settings_gui.services.cloudflare.permissions import REQUIRED_PERMISSION_NAMES

ACTIVE_TOKEN_STATUS = "active"
APP_TOKEN_NAME_PREFIXES = ("xgui_", "gui_")


@dataclass
class TokenCheckResult:
    is_valid: bool
    error: str = ""


@dataclass
class AccountCheckResult:
    is_valid: bool
    account_name: str = ""
    error: str = ""


@dataclass
class PermissionCheckItem:
    name: str
    granted: bool


@dataclass
class PermissionCheckResult:
    is_valid: bool
    items: list[PermissionCheckItem] = field(default_factory=list)
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


@dataclass
class TunnelInfo:
    tunnel_id: str
    name: str
    status: str


@dataclass
class TunnelListResult:
    tunnels: list[TunnelInfo] = field(default_factory=list)
    error: str = ""


class CloudflareFacade:
    """App-facing entry point for Cloudflare operations.

    Wraps CloudflareGateway calls into simple, UI-friendly results and never lets
    SDK exceptions escape past this layer.
    """

    def __init__(self, api_token: str) -> None:
        self._gateway = CloudflareGateway(api_token)

    def check_token(self) -> TokenCheckResult:
        try:
            token_status = self._gateway.verify_token()
            if token_status is None or token_status.status != ACTIVE_TOKEN_STATUS:
                return TokenCheckResult(is_valid=False, error="API token ไม่ถูกต้องหรือหมดอายุ")
            return TokenCheckResult(is_valid=True)
        except CloudflareError as error:
            return TokenCheckResult(is_valid=False, error=str(error))

    def check_account(self, account_id: str) -> AccountCheckResult:
        try:
            account = self._gateway.get_account(account_id)
            if account is None:
                return AccountCheckResult(is_valid=False, error="ไม่พบ Account ID นี้")
            return AccountCheckResult(is_valid=True, account_name=account.name)
        except CloudflareError as error:
            return AccountCheckResult(is_valid=False, error=str(error))

    def check_permissions(self) -> PermissionCheckResult:
        try:
            tokens = self._gateway.list_tokens()
            app_token = self._find_app_token(tokens)
            if app_token is None:
                prefixes = " หรือ ".join(f'"{prefix}"' for prefix in APP_TOKEN_NAME_PREFIXES)
                return PermissionCheckResult(
                    is_valid=False,
                    error=f"ไม่พบ API Token ที่ชื่อขึ้นต้นด้วย {prefixes} ในรายการ token ของผู้ใช้",
                )

            if app_token.id:
                save_token_id(app_token.id)

            granted = self._granted_permission_names(app_token)
            items = [PermissionCheckItem(name=name, granted=name in granted) for name in REQUIRED_PERMISSION_NAMES]
            missing = [item.name for item in items if not item.granted]
            error = f"API token ขาดสิทธิ์ที่จำเป็น: {', '.join(missing)}" if missing else ""
            return PermissionCheckResult(is_valid=not missing, items=items, error=error)
        except CloudflareError as error:
            return PermissionCheckResult(is_valid=False, error=str(error))

    @staticmethod
    def _find_app_token(tokens: list[Token]) -> Token | None:
        for token in tokens:
            if token.name and token.name.lower().startswith(APP_TOKEN_NAME_PREFIXES):
                return token
        return None

    @staticmethod
    def _granted_permission_names(token: Token) -> set[str]:
        return {
            group.name
            for policy in (token.policies or [])
            for group in policy.permission_groups
            if group.name
        }

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

    def list_tunnels(self, account_id: str) -> TunnelListResult:
        try:
            tunnels = self._gateway.list_tunnels(account_id)
            infos = [
                TunnelInfo(tunnel_id=tunnel.id or "", name=tunnel.name or "", status=tunnel.status or "")
                for tunnel in tunnels
            ]
            return TunnelListResult(tunnels=infos)
        except CloudflareError as error:
            return TunnelListResult(error=str(error))
