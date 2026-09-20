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
