from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QVBoxLayout, QWidget

SHADOW_MARGIN = 24


def center_on_parent(dialog: QWidget) -> None:
    parent = dialog.parentWidget()
    if parent is None:
        return

    parent_center = parent.window().frameGeometry().center()
    dialog.move(parent_center.x() - dialog.width() // 2, parent_center.y() - dialog.height() // 2)


def build_shadowed_card(with_shadow: bool = True) -> tuple[QFrame, QVBoxLayout]:
    """A rounded QFrame with an empty QVBoxLayout ready for content, optionally drop-shadowed.

    The shadow effect re-renders on every size change, which causes visible ghosting on
    windows that resize dynamically (e.g. maximizing). Keep it only for fixed-size popups.
    """
    card = QFrame()
    card.setObjectName("windowCard")

    if with_shadow:
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

    card_layout = QVBoxLayout(card)
    card_layout.setContentsMargins(0, 0, 0, 0)
    card_layout.setSpacing(0)

    return card, card_layout
