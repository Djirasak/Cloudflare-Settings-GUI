from unittest.mock import patch

from cloudflare_settings_gui.services.cloudflare.facade import TunnelInfo, TunnelListResult
from cloudflare_settings_gui.ui.pages.main.partials.tunnels import TunnelsPartial

WAIT_TIMEOUT_MS = 2000


def _make_tunnels_partial(qtbot) -> TunnelsPartial:
    partial = TunnelsPartial()
    qtbot.addWidget(partial)
    partial.show()
    return partial


def _patch_facade():
    return patch("cloudflare_settings_gui.ui.pages.main.partials.tunnels.CloudflareFacade")


class TestTunnelsPartial:
    def test_populates_tunnel_list_on_success(self, qtbot):
        partial = _make_tunnels_partial(qtbot)

        with _patch_facade() as mock_facade_cls:
            mock_facade_cls.return_value.list_tunnels.return_value = TunnelListResult(
                tunnels=[
                    TunnelInfo(tunnel_id="tunnel-1", name="office", status="healthy"),
                    TunnelInfo(tunnel_id="tunnel-2", name="backup", status="down"),
                ]
            )
            partial.load_tunnels("account-123", "token-abc")

            qtbot.waitUntil(lambda: partial._tunnel_list.count() == 2, timeout=WAIT_TIMEOUT_MS)

            mock_facade_cls.assert_called_once_with("token-abc")
            mock_facade_cls.return_value.list_tunnels.assert_called_once_with("account-123")

        assert partial._tunnel_list.item(0).text() == "office — healthy"
        assert partial._tunnel_list.item(1).text() == "backup — down"
        qtbot.waitUntil(lambda: partial._status_label.isVisible() is False, timeout=WAIT_TIMEOUT_MS)

    def test_shows_error_message_on_failure(self, qtbot):
        partial = _make_tunnels_partial(qtbot)

        with _patch_facade() as mock_facade_cls:
            mock_facade_cls.return_value.list_tunnels.return_value = TunnelListResult(
                error="เชื่อมต่อ API ไม่สำเร็จ"
            )
            partial.load_tunnels("account-123", "token-abc")

            qtbot.waitUntil(lambda: partial._status_label.objectName() == "statusError", timeout=WAIT_TIMEOUT_MS)

        assert partial._tunnel_list.count() == 0
        assert "เชื่อมต่อ API ไม่สำเร็จ" in partial._status_label.text()

    def test_shows_empty_message_when_no_tunnels(self, qtbot):
        partial = _make_tunnels_partial(qtbot)

        with _patch_facade() as mock_facade_cls:
            mock_facade_cls.return_value.list_tunnels.return_value = TunnelListResult(tunnels=[])
            partial.load_tunnels("account-123", "token-abc")

            qtbot.waitUntil(lambda: partial._status_label.isVisible() is True, timeout=WAIT_TIMEOUT_MS)

        assert partial._tunnel_list.count() == 0
