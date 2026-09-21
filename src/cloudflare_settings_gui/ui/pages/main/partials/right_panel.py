from PyQt6.QtCore import QThreadPool, pyqtSignal
from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from cloudflare_settings_gui.services.cloudflare.facade import (
    CloudflareFacade,
    DevelopmentModeResult,
    DomainInfo,
    PurgeCacheResult,
    ZoneListResult,
)
from cloudflare_settings_gui.ui.components.worker import FacadeWorker
from cloudflare_settings_gui.ui.pages.main.components.domain_card import DomainCard


class DomainSidebarPartial(QWidget):
    """The right-hand domain list — owns its own data, loading state, and API calls.

    Loading and every card action run on a QThreadPool worker so a slow request never
    freezes the window; results come back on the GUI thread via Qt's queued signals.
    """

    action_feedback = pyqtSignal(bool, str)  # success, message — for a toast the page hosts

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("mainSidePanel")

        self._api_token = ""
        self._thread_pool = QThreadPool(self)

        self._status_label = QLabel("กำลังโหลดรายการโดเมน...")
        self._status_label.setObjectName("statusPending")
        self._domain_list = QListWidget()
        self._domain_list.setObjectName("domainList")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(12)

        title = QLabel("โดเมนทั้งหมด")
        title.setObjectName("title")

        layout.addWidget(title)
        layout.addWidget(self._status_label)
        layout.addWidget(self._domain_list)

    def _set_status(self, text: str, state: str) -> None:
        self._status_label.setText(text)
        self._status_label.setObjectName(state)
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)
        self._status_label.setVisible(bool(text))

    def load_domains(self, account_id: str, api_token: str) -> None:
        self._api_token = api_token
        self._domain_list.clear()
        self._set_status("กำลังโหลดรายการโดเมน...", "statusPending")

        worker = FacadeWorker(CloudflareFacade(api_token).list_zones, account_id)
        worker.signals.result.connect(self._on_domains_loaded)
        worker.signals.error.connect(lambda message: self._set_status(message, "statusError"))
        self._thread_pool.start(worker)

    def _on_domains_loaded(self, result: ZoneListResult) -> None:
        if result.error:
            self._set_status(result.error, "statusError")
            return

        if not result.domains:
            self._set_status("ไม่พบโดเมนในบัญชีนี้", "statusPending")
            return

        self._set_status("", "statusPending")
        for domain in result.domains:
            self._add_domain_card(domain)

    def _add_domain_card(self, domain: DomainInfo) -> None:
        card = DomainCard(domain)
        card.dev_mode_toggled.connect(lambda enabled: self._on_dev_mode_toggled(card, domain, enabled))
        card.purge_cache_requested.connect(lambda: self._on_purge_cache_requested(domain))

        item = QListWidgetItem()
        item.setSizeHint(card.sizeHint())
        self._domain_list.addItem(item)
        self._domain_list.setItemWidget(item, card)

    def _on_dev_mode_toggled(self, card: DomainCard, domain: DomainInfo, enabled: bool) -> None:
        worker = FacadeWorker(CloudflareFacade(self._api_token).set_development_mode, domain.zone_id, enabled)
        worker.signals.result.connect(lambda result: self._handle_dev_mode_result(card, domain, enabled, result))
        worker.signals.error.connect(
            lambda message: self._handle_dev_mode_result(card, domain, enabled, DevelopmentModeResult(error=message))
        )
        self._thread_pool.start(worker)

    def _handle_dev_mode_result(
        self, card: DomainCard, domain: DomainInfo, requested_enabled: bool, result: DevelopmentModeResult
    ) -> None:
        if not result.success:
            card.set_dev_mode_checked(not requested_enabled)
            self.action_feedback.emit(False, result.error)
            return

        state_text = "เปิด" if requested_enabled else "ปิด"
        self.action_feedback.emit(True, f"{state_text} Development Mode แล้ว — {domain.name}")

    def _on_purge_cache_requested(self, domain: DomainInfo) -> None:
        worker = FacadeWorker(CloudflareFacade(self._api_token).purge_cache, domain.zone_id)
        worker.signals.result.connect(lambda result: self._handle_purge_cache_result(domain, result))
        worker.signals.error.connect(
            lambda message: self._handle_purge_cache_result(domain, PurgeCacheResult(error=message))
        )
        self._thread_pool.start(worker)

    def _handle_purge_cache_result(self, domain: DomainInfo, result: PurgeCacheResult) -> None:
        if not result.success:
            self.action_feedback.emit(False, result.error)
            return

        self.action_feedback.emit(True, f"ล้างแคชสำเร็จ — {domain.name}")
