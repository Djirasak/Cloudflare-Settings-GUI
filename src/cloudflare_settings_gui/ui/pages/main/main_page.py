from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class MainPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("page")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 32)

        label = QLabel("Hello")
        label.setObjectName("title")
        layout.addWidget(label)
