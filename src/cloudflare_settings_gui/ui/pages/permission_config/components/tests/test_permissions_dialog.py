from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QPushButton

from cloudflare_settings_gui.ui.pages.permission_config.components.permissions_dialog import PermissionsDialog

SAMPLE_PERMISSIONS = ["Zone Read", "DNS Edit"]


class TestPermissionsDialog:
    def test_shows_one_row_per_permission(self, qtbot):
        dialog = PermissionsDialog(SAMPLE_PERMISSIONS)
        qtbot.addWidget(dialog)
        dialog.show()

        row_texts = [
            label.text() for label in dialog.findChildren(QLabel) if label.objectName() == "permissionRow"
        ]
        assert len(row_texts) == len(SAMPLE_PERMISSIONS)
        for permission in SAMPLE_PERMISSIONS:
            assert any(permission in text for text in row_texts)

    def test_close_button_rejects_dialog(self, qtbot):
        dialog = PermissionsDialog(SAMPLE_PERMISSIONS)
        qtbot.addWidget(dialog)
        dialog.show()

        close_button = dialog.findChild(QPushButton, "windowCloseButton")
        assert close_button is not None

        qtbot.mouseClick(close_button, Qt.MouseButton.LeftButton)

        assert dialog.result() == PermissionsDialog.DialogCode.Rejected

    def test_ok_button_accepts_dialog(self, qtbot):
        dialog = PermissionsDialog(SAMPLE_PERMISSIONS)
        qtbot.addWidget(dialog)
        dialog.show()

        ok_button = next(
            button for button in dialog.findChildren(QPushButton) if button.objectName() != "windowCloseButton"
        )
        qtbot.mouseClick(ok_button, Qt.MouseButton.LeftButton)

        assert dialog.result() == PermissionsDialog.DialogCode.Accepted
