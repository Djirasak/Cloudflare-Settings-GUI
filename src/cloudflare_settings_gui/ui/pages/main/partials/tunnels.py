from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from cloudflare_settings_gui.services.cloudflare.facade import CloudflareFacade, TunnelListResult
from cloudflare_settings_gui.ui.components.worker import FacadeWorker


class TunnelsPartial(QWidget):
    """The "Tunnel" tab of the left panel — lists this account's Cloudflare Tunnels."""

    def __init__(self) -> None:
        super().__init__()

        # Global pool, not one parented to this widget — parenting deadlocks the GIL if the widget
        # is destroyed while a worker is still in flight.
        thread_pool = QThreadPool.globalInstance()
        assert thread_pool is not None
        self._thread_pool = thread_pool

        self._status_label = QLabel("กำลังโหลดรายการ Tunnel...")
        self._status_label.setObjectName("statusPending")
        self._tunnel_list = QListWidget()
        self._tunnel_list.setObjectName("tunnelList")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addWidget(self._status_label)
        layout.addWidget(self._tunnel_list)

    def load_tunnels(self, account_id: str, api_token: str) -> None:
        self._tunnel_list.clear()
        self._set_status("กำลังโหลดรายการ Tunnel...", "statusPending")

        worker = FacadeWorker(CloudflareFacade(api_token).list_tunnels, account_id)
        worker.signals.result.connect(self._on_tunnels_loaded)
        worker.signals.error.connect(lambda message: self._set_status(message, "statusError"))
        self._thread_pool.start(worker)

    def _set_status(self, text: str, state: str) -> None:
        self._status_label.setText(text)
        self._status_label.setObjectName(state)
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)
        self._status_label.setVisible(bool(text))

    def _on_tunnels_loaded(self, result: TunnelListResult) -> None:
        if result.error:
            self._set_status(result.error, "statusError")
            return

        if not result.tunnels:
            self._set_status("ไม่พบ Tunnel ในบัญชีนี้", "statusPending")
            return

        self._set_status("", "statusPending")
        for tunnel in result.tunnels:
            self._tunnel_list.addItem(QListWidgetItem(f"{tunnel.name} — {tunnel.status}"))
