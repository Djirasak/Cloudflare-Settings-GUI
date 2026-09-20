from unittest.mock import patch

from cloudflare_settings_gui.services.cloudflare.gateway import CloudflareGateway


class TestCloudflareGateway:
    def test_verify_token_calls_sdk_user_tokens_verify(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.user.tokens.verify.return_value = "verified"

            gateway = CloudflareGateway(api_token="token-abc")
            result = gateway.verify_token()

            mock_client_cls.assert_called_once_with(api_token="token-abc")
            mock_client.user.tokens.verify.assert_called_once()
            assert result == "verified"

    def test_get_account_calls_sdk_accounts_get(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.accounts.get.return_value = "account-obj"

            gateway = CloudflareGateway(api_token="token-abc")
            result = gateway.get_account("account-123")

            mock_client.accounts.get.assert_called_once_with(account_id="account-123")
            assert result == "account-obj"

    def test_list_zones_calls_sdk_zones_list(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.zones.list.return_value = ["zone1", "zone2"]

            gateway = CloudflareGateway(api_token="token-abc")
            result = gateway.list_zones("account-123")

            mock_client.zones.list.assert_called_once_with(account={"id": "account-123"})
            assert result == ["zone1", "zone2"]
