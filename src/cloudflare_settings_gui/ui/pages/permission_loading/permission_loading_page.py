from PyQt6.QtCore import Qt, QThreadPool, QTimer, pyqtSignal
from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

from cloudflare_settings_gui.services.cloudflare.facade import (
    AccountCheckResult,
    CloudflareFacade,
    PermissionCheckItem,
    PermissionCheckResult,
    TokenCheckResult,
)
from cloudflare_settings_gui.ui.components.worker import FacadeWorker

RESULT_DISPLAY_DELAY_MS = 700
STEP_TOKEN = "ตรวจสอบ API Token"
STEP_ACCOUNT = "ตรวจสอบ Account"
STEP_PERMISSION = "ตรวจสอบสิทธิ์ (Permission)"


class PermissionLoadingPage(QWidget):
    finished = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(
        self,
        account_id: str,
        api_token: str,
        message: str = "กำลังตรวจสอบสิทธิ์ด้วยข้อมูลที่จดจำไว้...",
    ) -> None:
        super().__init__()
        self.setObjectName("page")
        self.setMinimumWidth(420)

        self._account_id = account_id
        self._facade = CloudflareFacade(api_token)
        # Global pool, not one parented to this widget — parenting deadlocks the GIL if the widget
        # is destroyed while a check is still in flight.
        thread_pool = QThreadPool.globalInstance()
        assert thread_pool is not None
        self._thread_pool = thread_pool

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

        self._token_row = self._build_pending_row(STEP_TOKEN)
        self._account_row = self._build_pending_row(STEP_ACCOUNT)
        self._permission_row = self._build_pending_row(STEP_PERMISSION)

        self._permission_items_layout = QVBoxLayout()
        self._permission_items_layout.setContentsMargins(20, 0, 0, 0)
        self._permission_items_layout.setSpacing(2)

        layout.addWidget(spinner)
        layout.addWidget(label)
        layout.addWidget(self._token_row)
        layout.addWidget(self._account_row)
        layout.addWidget(self._permission_row)
        layout.addLayout(self._permission_items_layout)

        self._check_token()

    def _build_pending_row(self, text: str) -> QLabel:
        row = QLabel(f"• {text}")
        row.setObjectName("statusPending")
        return row

    def _set_row_result(self, row: QLabel, text: str, passed: bool) -> None:
        row.setText(f"{'✓' if passed else '✗'} {text}")
        row.setObjectName("statusOk" if passed else "statusError")
        row.style().unpolish(row)
        row.style().polish(row)

    def _fail_after_delay(self, error: str) -> None:
        QTimer.singleShot(RESULT_DISPLAY_DELAY_MS, lambda: self.failed.emit(error))

    def _on_step_exception(self, row: QLabel, step_text: str, message: str) -> None:
        self._set_row_result(row, step_text, False)
        self._fail_after_delay(message)

    def _check_token(self) -> None:
        worker = FacadeWorker(self._facade.check_token)
        worker.signals.result.connect(self._on_token_result)
        worker.signals.error.connect(lambda message: self._on_step_exception(self._token_row, STEP_TOKEN, message))
        self._thread_pool.start(worker)

    def _on_token_result(self, result: TokenCheckResult) -> None:
        self._set_row_result(self._token_row, STEP_TOKEN, result.is_valid)
        if not result.is_valid:
            self._fail_after_delay(result.error)
            return
        self._check_account()

    def _check_account(self) -> None:
        worker = FacadeWorker(self._facade.check_account, self._account_id)
        worker.signals.result.connect(self._on_account_result)
        worker.signals.error.connect(
            lambda message: self._on_step_exception(self._account_row, STEP_ACCOUNT, message)
        )
        self._thread_pool.start(worker)

    def _on_account_result(self, result: AccountCheckResult) -> None:
        self._set_row_result(self._account_row, STEP_ACCOUNT, result.is_valid)
        if not result.is_valid:
            self._fail_after_delay(result.error)
            return
        self._check_permissions()

    def _check_permissions(self) -> None:
        worker = FacadeWorker(self._facade.check_permissions)
        worker.signals.result.connect(self._on_permission_result)
        worker.signals.error.connect(
            lambda message: self._on_step_exception(self._permission_row, STEP_PERMISSION, message)
        )
        self._thread_pool.start(worker)

    def _on_permission_result(self, result: PermissionCheckResult) -> None:
        self._set_row_result(self._permission_row, STEP_PERMISSION, result.is_valid)
        self._render_permission_items(result.items)
        if result.is_valid:
            QTimer.singleShot(RESULT_DISPLAY_DELAY_MS, self.finished.emit)
        else:
            self._fail_after_delay(result.error)

    def _render_permission_items(self, items: list[PermissionCheckItem]) -> None:
        for item in items:
            row = QLabel(f"{'✓' if item.granted else '✗'} {item.name}")
            row.setObjectName("permissionRowGranted" if item.granted else "permissionRowMissing")
            self._permission_items_layout.addWidget(row)
