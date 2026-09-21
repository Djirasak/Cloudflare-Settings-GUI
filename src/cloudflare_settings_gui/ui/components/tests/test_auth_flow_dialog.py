from PyQt6.QtWidgets import QLabel, QWidget

from cloudflare_settings_gui.ui.components.auth_flow_dialog import AuthFlowDialog


class TestAuthFlowDialog:
    def test_wraps_content_as_modal_dialog(self, qtbot):
        content = QLabel("auth content")
        dialog = AuthFlowDialog(content)
        qtbot.addWidget(dialog)

        assert dialog.isModal() is True
        assert content.isVisible() is False

        dialog.show()
        assert content.isVisible() is True

    def test_set_content_swaps_widget_and_stays_visible(self, qtbot):
        content = QLabel("auth content")
        dialog = AuthFlowDialog(content)
        qtbot.addWidget(dialog)
        dialog.show()

        new_content = QLabel("next step")
        dialog.set_content(new_content)

        assert dialog.isVisible() is True
        assert new_content.isVisible() is True
        assert content.isVisible() is False

    def test_set_content_before_show_does_not_show_dialog(self, qtbot):
        content = QLabel("auth content")
        dialog = AuthFlowDialog(content)
        qtbot.addWidget(dialog)

        new_content = QLabel("next step")
        dialog.set_content(new_content)

        assert dialog.isVisible() is False

    def test_centers_on_parent_window(self, qtbot):
        parent = QWidget()
        parent.setGeometry(100, 100, 400, 300)
        qtbot.addWidget(parent)
        parent.show()

        content = QLabel("auth content")
        dialog = AuthFlowDialog(content, parent=parent)
        qtbot.addWidget(dialog)
        dialog.show()

        parent_center = parent.frameGeometry().center()
        dialog_center = dialog.frameGeometry().center()
        assert abs(dialog_center.x() - parent_center.x()) <= 1
        assert abs(dialog_center.y() - parent_center.y()) <= 1
