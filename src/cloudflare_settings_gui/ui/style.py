APP_STYLESHEET = """
QWidget {
    background-color: #14161a;
    color: #e6e8eb;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 14px;
}

QLabel#title {
    font-size: 22px;
    font-weight: 600;
    color: #f6821f;
}

QLabel#subtitle {
    color: #9aa0a8;
    font-size: 13px;
}

QLabel#status {
    font-size: 13px;
    padding: 2px 0px;
}

QLabel#statusOk {
    color: #3ddc84;
}

QLabel#statusError {
    color: #ff6b6b;
}

QLabel#statusPending {
    color: #9aa0a8;
}

QLineEdit {
    background-color: #1e2126;
    border: 1px solid #2a2e35;
    border-radius: 8px;
    padding: 10px 12px;
    color: #e6e8eb;
    selection-background-color: #f6821f;
}

QLineEdit:focus {
    border: 1px solid #f6821f;
}

QPushButton {
    background-color: #f6821f;
    color: #14161a;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #ff9a3d;
}

QPushButton:pressed {
    background-color: #d96e14;
}

QPushButton:disabled {
    background-color: #2a2e35;
    color: #5b6069;
}

QPushButton#secondary {
    background-color: transparent;
    color: #e6e8eb;
    border: 1px solid #2a2e35;
}

QPushButton#secondary:hover {
    border: 1px solid #f6821f;
    color: #f6821f;
    background-color: transparent;
}

QFrame#card {
    background-color: #1a1d22;
    border: 1px solid #2a2e35;
    border-radius: 14px;
}
"""
