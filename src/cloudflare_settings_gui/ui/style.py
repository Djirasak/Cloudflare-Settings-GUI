_APP_STYLESHEET_TEMPLATE = """
QWidget {
    background-color: #14161a;
    color: #e6e8eb;
    font-family: "Sarabun", "Segoe UI", "Inter", sans-serif;
    font-size: 14px;
}

QWidget#rootWindow {
    background: transparent;
}

QLabel {
    background-color: transparent;
    padding-top: 4px;
}

QFrame#windowCard {
    background-color: #1a1d22;
    border: 1px solid #2a2e35;
    border-radius: 16px;
}

QFrame#titleBar,
QWidget#page {
    background-color: transparent;
    border: none;
}

QFrame#titleBar {
    border-bottom: 1px solid #22252b;
}

QLabel#titleText {
    color: #b7bcc4;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.3px;
}

QPushButton#windowButton,
QPushButton#windowCloseButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    color: #9aa0a8;
    font-size: 13px;
    font-weight: 400;
    padding: 0px;
}

QPushButton#windowButton:hover {
    background-color: #262a31;
    color: #e6e8eb;
}

QPushButton#windowCloseButton:hover {
    background-color: #e5484d;
    color: #ffffff;
}

QLabel#title {
    font-size: 20px;
    font-weight: 600;
    color: #f6821f;
}

QLabel#subtitle {
    color: #9aa0a8;
    font-size: 13px;
}

QLabel#fieldLabel {
    color: #9aa0a8;
    font-size: 12px;
    font-weight: 600;
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

QWidget#mainLeftPanel {
    background-color: transparent;
}

QWidget#mainSidePanel {
    background-color: #1a1d22;
    border-left: 1px solid #2a2e35;
}

QListWidget#domainList {
    background-color: transparent;
    border: none;
    outline: none;
}

QListWidget#domainList::item {
    padding: 4px 0px;
    border: none;
}

QFrame#domainCard {
    background-color: #1a1d22;
    border: 1px solid #2a2e35;
    border-radius: 12px;
}

QFrame#domainCard[active="true"] {
    border: 1px solid #3ddc84;
}

QLabel#domainName {
    color: #e6e8eb;
    font-size: 14px;
    font-weight: 600;
}

QLabel#statusBadgeActive {
    background-color: rgba(61, 220, 132, 0.15);
    color: #3ddc84;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

QLabel#statusBadgePending {
    background-color: rgba(154, 160, 168, 0.15);
    color: #9aa0a8;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}

QLabel#toast {
    padding: 12px 20px;
    font-size: 13px;
    font-weight: 600;
}

QLabel#toastSuccess {
    background-color: #17301f;
    color: #3ddc84;
    border-top: 1px solid #234a2e;
}

QLabel#toastError {
    background-color: #3a1c1c;
    color: #ff6b6b;
    border-top: 1px solid #5a2a2a;
}

QLabel#permissionRow {
    color: #3ddc84;
    font-size: 13px;
}

QLabel#dialogTitle {
    font-size: 15px;
    font-weight: 600;
    color: #e6e8eb;
}

QCheckBox {
    background-color: transparent;
    color: #9aa0a8;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #3a3f47;
    border-radius: 4px;
    background-color: #21242a;
}

QCheckBox::indicator:hover {
    border: 1px solid #f6821f;
}

QCheckBox::indicator:checked {
    background-color: #f6821f;
    border: 1px solid #f6821f;
    image: url({check_icon_path});
}

QProgressBar#spinner {
    background-color: #21242a;
    border: none;
    border-radius: 2px;
}

QProgressBar#spinner::chunk {
    background-color: #f6821f;
    border-radius: 2px;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px 0px 2px 0px;
}

QScrollBar::handle:vertical {
    background: #3a3f47;
    border-radius: 5px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background: #4a5058;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
    border: none;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 0px 2px 0px 2px;
}

QScrollBar::handle:horizontal {
    background: #3a3f47;
    border-radius: 5px;
    min-width: 24px;
}

QScrollBar::handle:horizontal:hover {
    background: #4a5058;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
    background: none;
    border: none;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: none;
}

QLineEdit {
    background-color: #21242a;
    border: 1px solid #2f333b;
    border-radius: 10px;
    padding: 14px 14px;
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
    border-radius: 10px;
    padding: 13px 18px;
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
    border: 1px solid #2f333b;
}

QPushButton#secondary:hover {
    border: 1px solid #f6821f;
    color: #f6821f;
    background-color: transparent;
}

QPushButton#secondary:disabled {
    background-color: transparent;
    border: 1px solid #22252b;
    color: #5b6069;
}
"""


def build_stylesheet(check_icon_path: str) -> str:
    return _APP_STYLESHEET_TEMPLATE.replace("{check_icon_path}", check_icon_path)
