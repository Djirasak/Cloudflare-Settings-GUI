from cloudflare_settings_gui.ui.components.shadow_card import build_shadowed_card


class TestBuildShadowedCard:
    def test_returns_card_with_shadow_and_empty_layout(self, qtbot):
        card, layout = build_shadowed_card()
        qtbot.addWidget(card)

        assert card.objectName() == "windowCard"
        assert card.graphicsEffect() is not None
        assert layout.count() == 0
        assert card.layout() is layout

    def test_can_skip_the_shadow(self, qtbot):
        card, _ = build_shadowed_card(with_shadow=False)
        qtbot.addWidget(card)

        assert card.graphicsEffect() is None
