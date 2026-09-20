from unittest.mock import MagicMock, patch

from cloudflare import CloudflareError

from cloudflare_settings_gui.services.cloudflare.facade import CloudflareFacade


class TestCloudflareFacade:
    def _make_facade_with_mock_gateway(self) -> tuple[CloudflareFacade, MagicMock]:
        with patch("cloudflare_settings_gui.services.cloudflare.facade.CloudflareGateway") as mock_gateway_cls:
            facade = CloudflareFacade(api_token="token-abc")
            return facade, mock_gateway_cls.return_value

    def test_valid_credentials_returns_success_result(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.verify_token.return_value = MagicMock(status="active")
        account = MagicMock()
        account.name = "My Account"
        mock_gateway.get_account.return_value = account
        mock_gateway.list_zones.return_value = ["zone1", "zone2", "zone3"]

        result = facade.check_credentials("account-123")

        assert result.is_valid is True
        assert result.account_name == "My Account"
        assert result.zone_count == 3
        assert result.error == ""

    def test_inactive_token_returns_failure(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.verify_token.return_value = MagicMock(status="disabled")

        result = facade.check_credentials("account-123")

        assert result.is_valid is False
        assert result.error != ""

    def test_missing_token_status_returns_failure(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.verify_token.return_value = None

        result = facade.check_credentials("account-123")

        assert result.is_valid is False

    def test_account_not_found_returns_failure(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.verify_token.return_value = MagicMock(status="active")
        mock_gateway.get_account.return_value = None

        result = facade.check_credentials("account-123")

        assert result.is_valid is False

    def test_sdk_error_is_caught_and_returned_as_failure(self):
        facade, mock_gateway = self._make_facade_with_mock_gateway()
        mock_gateway.verify_token.side_effect = CloudflareError("boom")

        result = facade.check_credentials("account-123")

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
