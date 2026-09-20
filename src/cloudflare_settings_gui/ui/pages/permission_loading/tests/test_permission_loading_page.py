from PyQt6.QtWidgets import QLabel, QProgressBar

from cloudflare_settings_gui.ui.pages.permission_loading.permission_loading_page import (
    VERIFY_DELAY_MS,
    PermissionLoadingPage,
)


class TestPermissionLoadingPage:
    def test_shows_spinner_and_message(self, qtbot):
        page = PermissionLoadingPage("กำลังโหลด...")
        qtbot.addWidget(page)

        spinner = page.findChild(QProgressBar, "spinner")
        assert spinner is not None
        assert spinner.minimum() == 0
        assert spinner.maximum() == 0

        labels = [label.text() for label in page.findChildren(QLabel)]
        assert "กำลังโหลด..." in labels

    def test_emits_finished_after_delay(self, qtbot):
        page = PermissionLoadingPage()
        qtbot.addWidget(page)

        with qtbot.waitSignal(page.finished, timeout=VERIFY_DELAY_MS + 500):
            pass
