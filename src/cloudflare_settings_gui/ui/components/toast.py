from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QLabel, QWidget

DISPLAY_DURATION_MS = 3000


class Toast(QLabel):
    """A dismissible bar docked at the bottom of the page, for one-off success/error feedback."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("toast")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.hide()

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_success(self, text: str) -> None:
        self._show(text, "toastSuccess")

    def show_error(self, text: str) -> None:
        self._show(text, "toastError")

    def _show(self, text: str, state: str) -> None:
        self.setText(text)
        self.setObjectName(state)
        self.style().unpolish(self)
        self.style().polish(self)
        self.show()
        self._timer.start(DISPLAY_DURATION_MS)
