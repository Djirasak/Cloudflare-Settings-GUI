import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cloudflare_settings_gui.credentials import clear_credentials, load_credentials, save_credentials


class PermissionConfigPage(QWidget):
    continue_requested = pyqtSignal(str, str)  # account_id, api_token
    close_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("page")
        self.setMinimumWidth(420)

        self._email_input = QLineEdit()
        self._account_id_input = QLineEdit()
        self._token_input = QLineEdit()
        self._close_button = QPushButton("ปิดโปรแกรม")
        self._continue_button = QPushButton("ดำเนินการต่อ")
        self._status_label = QLabel()
        self._remember_checkbox = QCheckBox("จดจำข้อมูลนี้ไว้ในเครื่องนี้")

        self._build_ui()
        self._prefill_saved_credentials()
        self._close_button.clicked.connect(self.close_requested.emit)
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
            field.returnPressed.connect(self._on_continue_clicked)

        self._status_label.setWordWrap(True)
        self._set_status("กรอกอีเมล, Account ID และ API token ของ Cloudflare เพื่อเริ่มต้นใช้งาน", "statusPending")

        for button in (self._close_button, self._continue_button):
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        self._close_button.setObjectName("secondary")

        self._remember_checkbox.setCursor(Qt.CursorShape.PointingHandCursor)

        button_row = QVBoxLayout()
        button_row.setSpacing(12)
        button_row.addWidget(self._continue_button)
        button_row.addWidget(self._close_button)

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

    def _on_continue_clicked(self) -> None:
        email = self._email_input.text().strip()
        account_id = self._account_id_input.text().strip()
        token = self._token_input.text().strip()

        if not email or not account_id or not token:
            self._set_status("กรุณากรอกอีเมล, Account ID และ API token ให้ครบก่อนดำเนินการต่อ", "statusError")
            return

        if self._remember_checkbox.isChecked():
            save_credentials(email, account_id, token)
        else:
            clear_credentials()

        self.continue_requested.emit(account_id, token)
