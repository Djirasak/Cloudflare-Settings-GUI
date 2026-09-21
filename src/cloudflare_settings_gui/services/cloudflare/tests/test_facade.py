from unittest.mock import MagicMock, patch

from cloudflare import CloudflareError
from cloudflare.types.shared.token import Token

from cloudflare_settings_gui.services.cloudflare.facade import CloudflareFacade
from cloudflare_settings_gui.services.cloudflare.permissions import REQUIRED_PERMISSION_NAMES

_ZONE_RESOURCES = {"com.cloudflare.api.account.abc": {"com.cloudflare.api.account.zone.*": "*"}}


def _make_token(name: str, permission_names: list[str], token_id: str = "token-id-123") -> Token:
    return Token.model_validate(
        {
            "id": token_id,
            "name": name,
            "status": "active",
            "policies": [
                {
                    "id": "policy-1",
                    "effect": "allow",
                    "resources": _ZONE_RESOURCES,
                    "permission_groups": [
                        {"id": f"group-{i}", "name": permission_name}
                        for i, permission_name in enumerate(permission_names)
                    ],
                }
            ],
        }
    )


def _make_app_token(permission_names: list[str] = REQUIRED_PERMISSION_NAMES) -> Token:
    return _make_token("XGUI_TOKEN", permission_names)


class TestCloudflareFacade:
    def _make_facade_with_mock_gateway(self) -> tuple[CloudflareFacade, MagicMock]:
        with patch("cloudflare_settings_gui.services.cloudflare.facade.CloudflareGateway") as mock_gateway_cls:
            facade = CloudflareFacade(api_token="token-abc")
            return facade, mock_gateway_cls.return_value

    def test_check_token_returns_success_for_active_token(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.verify_token.return_value = MagicMock(status="active")

        result = facade.check_token()

        assert result.is_valid is True
        assert result.error == ""

    def test_check_token_returns_failure_for_inactive_token(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.verify_token.return_value = MagicMock(status="disabled")

        result = facade.check_token()

        assert result.is_valid is False
        assert result.error != ""

    def test_check_token_returns_failure_when_status_missing(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.verify_token.return_value = None

        result = facade.check_token()

        assert result.is_valid is False

    def test_check_token_catches_sdk_error(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.verify_token.side_effect = CloudflareError("boom")

        result = facade.check_token()

        assert result.is_valid is False
        assert "boom" in result.error

    def test_check_account_returns_success_when_found(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        account = MagicMock()
        account.name = "My Account"
        mock_gateway.get_account.return_value = account

        result = facade.check_account("account-123")

        assert result.is_valid is True
        assert result.account_name == "My Account"
        mock_gateway.get_account.assert_called_once_with("account-123")

    def test_check_account_returns_failure_when_not_found(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.get_account.return_value = None

        result = facade.check_account("account-123")

        assert result.is_valid is False

    def test_check_account_catches_sdk_error(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.get_account.side_effect = CloudflareError("boom")

        result = facade.check_account("account-123")

        assert result.is_valid is False
        assert "boom" in result.error

    def test_check_permissions_returns_success_with_all_items_granted(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.list_tokens.return_value = [_make_app_token()]

        with patch("cloudflare_settings_gui.services.cloudflare.facade.save_token_id") as mock_save_token_id:
            result = facade.check_permissions()

        assert result.is_valid is True
        assert result.error == ""
        assert [item.name for item in result.items] == REQUIRED_PERMISSION_NAMES
        assert all(item.granted for item in result.items)
        mock_save_token_id.assert_called_once_with("token-id-123")

    def test_check_permissions_returns_failure_when_no_app_token_found(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.list_tokens.return_value = [_make_token("github_tarot", REQUIRED_PERMISSION_NAMES)]

        result = facade.check_permissions()

        assert result.is_valid is False
        assert result.items == []

    def test_check_permissions_app_token_name_match_is_case_insensitive(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.list_tokens.return_value = [_make_token("xgui_prod", REQUIRED_PERMISSION_NAMES)]

        with patch("cloudflare_settings_gui.services.cloudflare.facade.save_token_id"):
            result = facade.check_permissions()

        assert result.is_valid is True

    def test_check_permissions_app_token_name_accepts_gui_prefix(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.list_tokens.return_value = [_make_token("GUI_prod", REQUIRED_PERMISSION_NAMES)]

        with patch("cloudflare_settings_gui.services.cloudflare.facade.save_token_id"):
            result = facade.check_permissions()

        assert result.is_valid is True

    def test_check_permissions_marks_missing_items_and_fails(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        incomplete = [name for name in REQUIRED_PERMISSION_NAMES if name != "Cache Purge"]
        mock_gateway.list_tokens.return_value = [_make_app_token(incomplete)]

        with patch("cloudflare_settings_gui.services.cloudflare.facade.save_token_id"):
            result = facade.check_permissions()

        assert result.is_valid is False
        assert "Cache Purge" in result.error
        granted_by_name = {item.name: item.granted for item in result.items}
        assert granted_by_name["Cache Purge"] is False
        assert granted_by_name["Zone Read"] is True

    def test_check_permissions_catches_sdk_error(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.list_tokens.side_effect = CloudflareError("boom")

        result = facade.check_permissions()

        assert result.is_valid is False
        assert "boom" in result.error

    def test_list_zones_returns_domain_info_for_each_zone(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        zone1 = MagicMock()
        zone1.id = "zone-1"
        zone1.name = "example.com"
        zone1.status = "active"
        zone1.development_mode = 10782
        zone2 = MagicMock()
        zone2.id = "zone-2"
        zone2.name = "example.org"
        zone2.status = None
        zone2.development_mode = 0
        mock_gateway.list_zones.return_value = [zone1, zone2]

        result = facade.list_zones("account-123")

        assert result.error == ""
        assert [d.zone_id for d in result.domains] == ["zone-1", "zone-2"]
        assert [d.name for d in result.domains] == ["example.com", "example.org"]
        assert [d.status for d in result.domains] == ["active", ""]
        assert [d.dev_mode_enabled for d in result.domains] == [True, False]

    def test_list_zones_catches_sdk_error(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.list_zones.side_effect = CloudflareError("network down")

        result = facade.list_zones("account-123")

        assert result.domains == []
        assert "network down" in result.error

    def test_set_development_mode_returns_success(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()

        result = facade.set_development_mode("zone-1", True)

        mock_gateway.set_development_mode.assert_called_once_with("zone-1", True)
        assert result.success is True
        assert result.error == ""

    def test_set_development_mode_catches_sdk_error(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.set_development_mode.side_effect = CloudflareError("boom")

        result = facade.set_development_mode("zone-1", True)

        assert result.success is False
        assert "boom" in result.error

    def test_purge_cache_returns_success(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()

        result = facade.purge_cache("zone-1")

        mock_gateway.purge_cache.assert_called_once_with("zone-1")
        assert result.success is True
        assert result.error == ""

    def test_purge_cache_catches_sdk_error(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.purge_cache.side_effect = CloudflareError("boom")

        result = facade.purge_cache("zone-1")

        assert result.success is False
        assert "boom" in result.error

    def test_list_tunnels_returns_tunnel_info_for_each_tunnel(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        tunnel1 = MagicMock()
        tunnel1.id = "tunnel-1"
        tunnel1.name = "office"
        tunnel1.status = "healthy"
        tunnel2 = MagicMock()
        tunnel2.id = "tunnel-2"
        tunnel2.name = "backup"
        tunnel2.status = None
        mock_gateway.list_tunnels.return_value = [tunnel1, tunnel2]

        result = facade.list_tunnels("account-123")

        assert result.error == ""
        assert [t.tunnel_id for t in result.tunnels] == ["tunnel-1", "tunnel-2"]
        assert [t.name for t in result.tunnels] == ["office", "backup"]
        assert [t.status for t in result.tunnels] == ["healthy", ""]

    def test_list_tunnels_catches_sdk_error(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.list_tunnels.side_effect = CloudflareError("network down")

        result = facade.list_tunnels("account-123")

        assert result.tunnels == []
        assert "network down" in result.error
