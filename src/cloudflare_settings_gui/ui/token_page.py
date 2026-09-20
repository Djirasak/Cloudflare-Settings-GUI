from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

MOCK_VERIFY_DELAY_MS = 600
MOCK_ZONE_COUNT = 5


class TokenPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Cloudflare Settings GUI")
        self.setMinimumSize(480, 420)

        self._token_input = QLineEdit()
        self._verify_button = QPushButton("ตรวจสอบสิทธิ์")
        self._continue_button = QPushButton("ดำเนินการต่อ")
        self._status_label = QLabel("กรอก API token ของ Cloudflare เพื่อเริ่มต้นใช้งาน")

        self._build_ui()
        self._verify_button.clicked.connect(self._on_verify_clicked)
        self._continue_button.clicked.connect(self._on_continue_clicked)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(380)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(16)

        title = QLabel("Cloudflare Settings GUI")
        title.setObjectName("title")

        subtitle = QLabel("ใส่ API Token เพื่อตรวจสอบสิทธิ์การใช้งาน")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)

        self._token_input.setPlaceholderText("API Token")
        self._token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._token_input.returnPressed.connect(self._on_verify_clicked)

        self._status_label.setWordWrap(True)
        self._set_status("กรอก API token ของ Cloudflare เพื่อเริ่มต้นใช้งาน", "statusPending")

        self._continue_button.setObjectName("secondary")
        self._continue_button.setEnabled(False)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addWidget(self._verify_button)
        button_row.addWidget(self._continue_button)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addWidget(self._token_input)
        card_layout.addWidget(self._status_label)
        card_layout.addSpacing(4)
        card_layout.addLayout(button_row)

        outer.addStretch(1)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(card)
        row.addStretch(1)
        outer.addLayout(row)
        outer.addStretch(1)

    def _set_status(self, text: str, state: str) -> None:
        self._status_label.setText(text)
        self._status_label.setObjectName(state)
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)

    def _on_verify_clicked(self) -> None:
        token = self._token_input.text().strip()
        if not token:
            self._set_status("กรุณากรอก API token ก่อนตรวจสอบ", "statusError")
            return

        self._verify_button.setEnabled(False)
        self._continue_button.setEnabled(False)
        self._set_status("กำลังตรวจสอบสิทธิ์...", "statusPending")

        QTimer.singleShot(MOCK_VERIFY_DELAY_MS, self._on_verify_result)

    def _on_verify_result(self) -> None:
        self._verify_button.setEnabled(True)
        self._set_status(
            f"โทเค็นใช้งานได้ — อ่านโซนได้ {MOCK_ZONE_COUNT} โซน",
            "statusOk",
        )
        self._continue_button.setEnabled(True)

    def _on_continue_clicked(self) -> None:
        print("ดำเนินการต่อ: ยังไม่มีหน้าโซน (จะทำในรอบถัดไป)")
