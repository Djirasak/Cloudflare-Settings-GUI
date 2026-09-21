from unittest.mock import patch

from PyQt6.QtWidgets import QWidget

from cloudflare_settings_gui.ui.pages.main.main_page import MainPage


def _make_page(qtbot) -> MainPage:
    page = MainPage()
    qtbot.addWidget(page)
    page.show()
    return page


class TestMainPageLayout:
    def test_splits_into_a_70_30_left_right_layout(self, qtbot):
        page = _make_page(qtbot)

        assert page._panels_layout.count() == 2
        assert page._panels_layout.stretch(0) == 7
        assert page._panels_layout.stretch(1) == 3

    def test_left_panel_is_the_tabbed_partial(self, qtbot):
        page = _make_page(qtbot)

        left_panel = page.findChild(QWidget, "mainLeftPanel")
        assert left_panel is page._left_panel

    def test_right_panel_is_the_right_panel_partial(self, qtbot):
        page = _make_page(qtbot)

        right_panel = page.findChild(QWidget, "mainSidePanel")
        assert right_panel is page._right_panel

    def test_toast_starts_hidden_at_the_bottom(self, qtbot):
        page = _make_page(qtbot)

        assert page._toast.isVisible() is False
        assert page.layout().indexOf(page._toast) == page.layout().count() - 1


class TestMainPageLoadAccountData:
    def test_delegates_to_right_panel(self, qtbot):
        page = _make_page(qtbot)

        with (
            patch.object(page._right_panel, "load_domains") as mock_load_domains,
            patch.object(page._left_panel, "load_tunnels"),
        ):
            page.load_account_data("account-123", "token-abc")

        mock_load_domains.assert_called_once_with("account-123", "token-abc")

    def test_delegates_to_left_panel(self, qtbot):
        page = _make_page(qtbot)

        with (
            patch.object(page._left_panel, "load_tunnels") as mock_load_tunnels,
            patch.object(page._right_panel, "load_domains"),
        ):
            page.load_account_data("account-123", "token-abc")

        mock_load_tunnels.assert_called_once_with("account-123", "token-abc")


class TestMainPageToast:
    def test_success_feedback_shows_success_toast(self, qtbot):
        page = _make_page(qtbot)

        page._right_panel.action_feedback.emit(True, "ล้างแคชสำเร็จ — example.com")

        assert page._toast.isVisible() is True
        assert page._toast.objectName() == "toastSuccess"
        assert page._toast.text() == "ล้างแคชสำเร็จ — example.com"

    def test_error_feedback_shows_error_toast(self, qtbot):
        page = _make_page(qtbot)

        page._right_panel.action_feedback.emit(False, "เชื่อมต่อ API ไม่สำเร็จ")

        assert page._toast.isVisible() is True
        assert page._toast.objectName() == "toastError"
        assert page._toast.text() == "เชื่อมต่อ API ไม่สำเร็จ"
