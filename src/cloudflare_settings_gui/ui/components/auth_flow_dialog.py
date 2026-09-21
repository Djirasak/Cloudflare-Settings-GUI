from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QWidget

from cloudflare_settings_gui.ui.components.shadow_card import SHADOW_MARGIN, build_shadowed_card, center_on_parent


class AuthFlowDialog(QDialog):
    """A modal popup that hosts the authentication/loading flow on top of the main window."""

    def __init__(self, content: QWidget, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("rootWindow")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN, SHADOW_MARGIN)
        outer.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

        card, card_layout = build_shadowed_card()
        card_layout.addWidget(content)

        outer.addWidget(card)

        self._card_layout = card_layout
        self._content = content

    def set_content(self, new_content: QWidget) -> None:
        # Hide/show around the resize to avoid a broken UpdateLayeredWindowIndirect dirty rect on Windows.
        was_visible = self.isVisible()
        if was_visible:
            self.hide()

        self._card_layout.removeWidget(self._content)
        self._content.hide()
        self._content.deleteLater()

        self._card_layout.addWidget(new_content)
        new_content.show()
        self._content = new_content

        center_on_parent(self)
        if was_visible:
            self.show()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        center_on_parent(self)
