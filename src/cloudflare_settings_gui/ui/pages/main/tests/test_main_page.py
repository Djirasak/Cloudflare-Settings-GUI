from unittest.mock import patch

from PyQt6.QtWidgets import QWidget

from cloudflare_settings_gui.ui.pages.main.main_page import MainPage


def _make_page(qtbot) -> MainPage:
    page = MainPage()
    qtbot.addWidget(page)
    page.show()
    return page


class TestMainPageLayout:
    def test_splits_into_an_80_20_left_right_layout(self, qtbot):
        page = _make_page(qtbot)

        assert page._panels_layout.count() == 2
        assert page._panels_layout.stretch(0) == 8
        assert page._panels_layout.stretch(1) == 2

    def test_left_panel_starts_empty(self, qtbot):
        page = _make_page(qtbot)

        left_panel = page.findChild(QWidget, "mainLeftPanel")
        assert left_panel is not None
        assert left_panel.layout() is None

    def test_right_panel_is_the_domain_sidebar(self, qtbot):
        page = _make_page(qtbot)

        right_panel = page.findChild(QWidget, "mainSidePanel")
        assert right_panel is page._domain_sidebar

    def test_toast_starts_hidden_at_the_bottom(self, qtbot):
        page = _make_page(qtbot)

        assert page._toast.isVisible() is False
        assert page.layout().indexOf(page._toast) == page.layout().count() - 1


class TestMainPageLoadDomains:
    def test_delegates_to_domain_sidebar(self, qtbot):
        page = _make_page(qtbot)

        with patch.object(page._domain_sidebar, "load_domains") as mock_load_domains:
            page.load_domains("account-123", "token-abc")

        mock_load_domains.assert_called_once_with("account-123", "token-abc")


class TestMainPageToast:
    def test_success_feedback_shows_success_toast(self, qtbot):
        page = _make_page(qtbot)

        page._domain_sidebar.action_feedback.emit(True, "ล้างแคชสำเร็จ — example.com")

        assert page._toast.isVisible() is True
        assert page._toast.objectName() == "toastSuccess"
        assert page._toast.text() == "ล้างแคชสำเร็จ — example.com"

    def test_error_feedback_shows_error_toast(self, qtbot):
        page = _make_page(qtbot)

        page._domain_sidebar.action_feedback.emit(False, "เชื่อมต่อ API ไม่สำเร็จ")

        assert page._toast.isVisible() is True
        assert page._toast.objectName() == "toastError"
        assert page._toast.text() == "เชื่อมต่อ API ไม่สำเร็จ"
