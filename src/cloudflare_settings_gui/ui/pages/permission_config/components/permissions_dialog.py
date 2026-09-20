from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cloudflare_settings_gui.ui.components.shadow_card import SHADOW_MARGIN, build_shadowed_card, center_on_parent


class PermissionsDialog(QDialog):
    def __init__(self, permissions: list[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("rootWindow")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN)
        outer.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        card, card_layout = build_shadowed_card()
        card.setMinimumWidth(360)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(10)

        header_row = QHBoxLayout()
        title = QLabel("สิทธิ์การเข้าถึงที่ตรวจพบ")
        title.setObjectName("dialogTitle")

        close_button = QPushButton("✕")
        close_button.setObjectName("windowCloseButton")
        close_button.setFixedSize(28, 28)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.clicked.connect(self.reject)

        header_row.addWidget(title)
        header_row.addStretch(1)
        header_row.addWidget(close_button)
        card_layout.addLayout(header_row)
        card_layout.addSpacing(4)

        for permission in permissions:
            row = QLabel(f"✓  {permission}")
            row.setObjectName("permissionRow")
            card_layout.addWidget(row)

        card_layout.addSpacing(8)

        ok_button = QPushButton("ปิด")
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.clicked.connect(self.accept)
        card_layout.addWidget(ok_button)

        outer.addWidget(card)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        center_on_parent(self)
