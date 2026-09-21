from unittest.mock import patch

from cloudflare_settings_gui.services.cloudflare.gateway import CloudflareGateway


class TestCloudflareGateway:
    def test_verify_token_calls_sdk_user_tokens_verify(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.user.tokens.verify.return_value = "verified"

            gateway = CloudflareGateway(api_token="token-abc")
            result = gateway.verify_token()

            assert mock_client_cls.call_args.kwargs["api_token"] == "token-abc"
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

    def test_list_tokens_calls_sdk_user_tokens_list(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.user.tokens.list.return_value = ["token1", "token2"]

            gateway = CloudflareGateway(api_token="token-abc")
            result = gateway.list_tokens()

            mock_client.user.tokens.list.assert_called_once_with()
            assert result == ["token1", "token2"]

    def test_list_zones_calls_sdk_zones_list(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.zones.list.return_value = ["zone1", "zone2"]

            gateway = CloudflareGateway(api_token="token-abc")
            result = gateway.list_zones("account-123")

            mock_client.zones.list.assert_called_once_with(account={"id": "account-123"})
            assert result == ["zone1", "zone2"]

    def test_list_tunnels_calls_sdk_zero_trust_tunnels_list(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value
            mock_client.zero_trust.tunnels.list.return_value = ["tunnel1", "tunnel2"]

            gateway = CloudflareGateway(api_token="token-abc")
            result = gateway.list_tunnels("account-123")

            mock_client.zero_trust.tunnels.list.assert_called_once_with(account_id="account-123")
            assert result == ["tunnel1", "tunnel2"]

    def test_set_development_mode_calls_sdk_settings_edit(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value

            gateway = CloudflareGateway(api_token="token-abc")
            gateway.set_development_mode("zone-1", True)

            mock_client.zones.settings.edit.assert_called_once_with(
                setting_id="development_mode", zone_id="zone-1", value="on"
            )

    def test_set_development_mode_off_passes_off_value(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value

            gateway = CloudflareGateway(api_token="token-abc")
            gateway.set_development_mode("zone-1", False)

            mock_client.zones.settings.edit.assert_called_once_with(
                setting_id="development_mode", zone_id="zone-1", value="off"
            )

    def test_purge_cache_calls_sdk_cache_purge(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value

            gateway = CloudflareGateway(api_token="token-abc")
            gateway.purge_cache("zone-1")

            mock_client.cache.purge.assert_called_once_with(zone_id="zone-1", purge_everything=True)

    def test_clears_email_and_key_so_token_auth_always_wins(self):
        with patch("cloudflare_settings_gui.services.cloudflare.gateway.Cloudflare") as mock_client_cls:
            mock_client = mock_client_cls.return_value

            CloudflareGateway(api_token="token-abc")

            assert mock_client.api_email is None
            assert mock_client.api_key is None
