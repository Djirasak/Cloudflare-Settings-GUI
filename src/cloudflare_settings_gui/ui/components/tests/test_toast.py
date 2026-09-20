from cloudflare_settings_gui.ui.components.toast import DISPLAY_DURATION_MS, Toast


def _make_toast(qtbot) -> Toast:
    toast = Toast()
    qtbot.addWidget(toast)
    return toast


class TestToast:
    def test_starts_hidden(self, qtbot):
        toast = _make_toast(qtbot)

        assert toast.isVisible() is False

    def test_show_success_displays_message_with_success_style(self, qtbot):
        toast = _make_toast(qtbot)

        toast.show_success("ล้างแคชสำเร็จ")

        assert toast.isVisible() is True
        assert toast.text() == "ล้างแคชสำเร็จ"
        assert toast.objectName() == "toastSuccess"

    def test_show_error_displays_message_with_error_style(self, qtbot):
        toast = _make_toast(qtbot)

        toast.show_error("เชื่อมต่อ API ไม่สำเร็จ")

        assert toast.isVisible() is True
        assert toast.text() == "เชื่อมต่อ API ไม่สำเร็จ"
        assert toast.objectName() == "toastError"

    def test_hides_itself_after_display_duration(self, qtbot):
        toast = _make_toast(qtbot)

        toast.show_success("ล้างแคชสำเร็จ")
        qtbot.waitUntil(lambda: toast.isVisible() is False, timeout=DISPLAY_DURATION_MS + 500)
