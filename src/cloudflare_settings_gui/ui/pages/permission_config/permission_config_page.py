import os

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cloudflare_settings_gui.credentials import clear_credentials, load_credentials, save_credentials
from cloudflare_settings_gui.ui.pages.permission_config.components.permissions_dialog import PermissionsDialog

MOCK_VERIFY_DELAY_MS = 600
MOCK_ZONE_COUNT = 5
MOCK_PERMISSIONS = [
    "อ่านรายการโซน (Zone Read)",
    "แก้ไขการตั้งค่า DNS (DNS Edit)",
    "อ่าน/แก้ไขกฎ Firewall (Firewall Services Edit)",
    "อ่านการตั้งค่า SSL/TLS (SSL and Certificates Read)",
    "ล้างแคช (Cache Purge)",
]


class PermissionConfigPage(QWidget):
    continue_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("page")
        self.setMinimumWidth(420)

        self._email_input = QLineEdit()
        self._account_id_input = QLineEdit()
        self._token_input = QLineEdit()
        self._verify_button = QPushButton("ตรวจสอบสิทธิ์")
        self._continue_button = QPushButton("ดำเนินการต่อ")
        self._status_label = QLabel()
        self._remember_checkbox = QCheckBox("จดจำข้อมูลนี้ไว้ในเครื่องนี้")

        self._build_ui()
        self._prefill_saved_credentials()
        self._verify_button.clicked.connect(self._on_verify_clicked)
        self._continue_button.clicked.connect(self._on_continue_clicked)

    def _prefill_saved_credentials(self) -> None:
        saved = load_credentials()

        self._email_input.setText(saved["email"] or os.environ.get("CLOUDFLARE_EMAIL", ""))
        self._account_id_input.setText(saved["account_id"] or os.environ.get("CLOUDFLARE_ACCOUNT_ID", ""))
        self._token_input.setText(saved["api_token"] or os.environ.get("CLOUDFLARE_API_TOKEN", ""))
        self._remember_checkbox.setChecked(any(saved.values()))

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Cloudflare Settings GUI")
        title.setObjectName("title")

        subtitle = QLabel("กรอกข้อมูลบัญชี Cloudflare เพื่อตรวจสอบสิทธิ์การใช้งาน")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)

        self._email_input.setPlaceholderText("Email")
        self._account_id_input.setPlaceholderText("Account ID")
        self._token_input.setPlaceholderText("API Token")
        self._token_input.setEchoMode(QLineEdit.EchoMode.Password)

        for field in (self._email_input, self._account_id_input, self._token_input):
            field.returnPressed.connect(self._on_verify_clicked)

        self._status_label.setWordWrap(True)
        self._set_status("กรอกอีเมล, Account ID และ API token ของ Cloudflare เพื่อเริ่มต้นใช้งาน", "statusPending")

        for button in (self._verify_button, self._continue_button):
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        self._continue_button.setObjectName("secondary")
        self._continue_button.setEnabled(False)

        self._remember_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addWidget(self._verify_button)
        button_row.addWidget(self._continue_button)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addLayout(self._field_group("อีเมล", self._email_input))
        layout.addLayout(self._field_group("Account ID", self._account_id_input))
        layout.addLayout(self._field_group("API Token", self._token_input))
        layout.addWidget(self._remember_checkbox)
        layout.addWidget(self._status_label)
        layout.addSpacing(4)
        layout.addLayout(button_row)

    def _field_group(self, label_text: str, field: QLineEdit) -> QVBoxLayout:
        label = QLabel(label_text)
        label.setObjectName("fieldLabel")

        group = QVBoxLayout()
        group.setSpacing(6)
        group.addWidget(label)
        group.addWidget(field)
        return group

    def _set_status(self, text: str, state: str) -> None:
        self._status_label.setText(text)
        self._status_label.setObjectName(state)
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

    def _on_verify_clicked(self) -> None:
        email = self._email_input.text().strip()
        account_id = self._account_id_input.text().strip()
        token = self._token_input.text().strip()

        if not email or not account_id or not token:
            self._set_status("กรุณากรอกอีเมล, Account ID และ API token ให้ครบก่อนตรวจสอบ", "statusError")
            return

        self._verify_button.setEnabled(False)
        self._continue_button.setEnabled(False)
        self._set_status("กำลังตรวจสอบสิทธิ์...", "statusPending")

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self._on_verify_result)
        timer.start(MOCK_VERIFY_DELAY_MS)

    def _on_verify_result(self) -> None:
        self._verify_button.setEnabled(True)
        self._set_status(
            f"ตรวจสอบสิทธิ์สำเร็จ — อ่านโซนได้ {MOCK_ZONE_COUNT} โซน",
            "statusOk",
        )
        self._continue_button.setEnabled(True)

        if self._remember_checkbox.isChecked():
            save_credentials(
                self._email_input.text().strip(),
                self._account_id_input.text().strip(),
                self._token_input.text().strip(),
            )
        else:
            clear_credentials()

        self._permissions_dialog = PermissionsDialog(MOCK_PERMISSIONS, parent=self)
        self._permissions_dialog.show()

    def _on_continue_clicked(self) -> None:
        self.continue_requested.emit()
