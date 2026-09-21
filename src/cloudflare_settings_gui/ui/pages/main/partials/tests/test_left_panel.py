from unittest.mock import patch

from cloudflare_settings_gui.ui.pages.main.partials.left_panel import TAB_TITLES, LeftPanelPartial


def _make_left_panel(qtbot) -> LeftPanelPartial:
    panel = LeftPanelPartial()
    qtbot.addWidget(panel)
    panel.show()
    return panel


class TestLeftPanelPartial:
    def test_has_a_tab_per_title(self, qtbot):
        panel = _make_left_panel(qtbot)

        assert panel._tabs.count() == len(TAB_TITLES)
        assert [panel._tabs.tabText(i) for i in range(panel._tabs.count())] == list(TAB_TITLES)

    def test_first_tab_is_selected_by_default(self, qtbot):
        panel = _make_left_panel(qtbot)

        assert panel._tabs.currentIndex() == 0

    def test_first_tab_is_the_tunnels_partial(self, qtbot):
        panel = _make_left_panel(qtbot)

        assert panel._tabs.widget(0) is panel._tunnels

    def test_load_tunnels_delegates_to_tunnels_partial(self, qtbot):
        panel = _make_left_panel(qtbot)

        with patch.object(panel._tunnels, "load_tunnels") as mock_load_tunnels:
            panel.load_tunnels("account-123", "token-abc")

        mock_load_tunnels.assert_called_once_with("account-123", "token-abc")
