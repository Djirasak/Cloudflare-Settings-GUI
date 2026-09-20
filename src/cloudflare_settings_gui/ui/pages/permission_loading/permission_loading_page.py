from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

VERIFY_DELAY_MS = 600


class PermissionLoadingPage(QWidget):
    finished = pyqtSignal()

    def __init__(self, message: str = "กำลังตรวจสอบสิทธิ์ด้วยข้อมูลที่จดจำไว้...") -> None:
        super().__init__()
        self.setObjectName("page")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 48, 32, 48)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        spinner = QProgressBar()
        spinner.setObjectName("spinner")
        spinner.setRange(0, 0)
        spinner.setTextVisible(False)
        spinner.setFixedHeight(4)

        label = QLabel(message)
        label.setObjectName("subtitle")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)

        layout.addWidget(spinner)
        layout.addWidget(label)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.finished.emit)
        self._timer.start(VERIFY_DELAY_MS)
