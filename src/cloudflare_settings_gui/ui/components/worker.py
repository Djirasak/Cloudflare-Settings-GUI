from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import QObject, QRunnable, pyqtSignal


class WorkerSignals(QObject):
    result = pyqtSignal(object)
    error = pyqtSignal(str)


class FacadeWorker(QRunnable):
    """Runs a blocking call (e.g. a CloudflareFacade method) on a QThreadPool thread.

    Results are delivered back on the GUI thread via WorkerSignals, since PyQt marshals
    signal emissions across threads automatically when the receiver lives elsewhere.
    """

    def __init__(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            result = self._fn(*self._args, **self._kwargs)
        except Exception as error:  # surfaced to the GUI thread instead of crashing the pool silently
            self.signals.error.emit(str(error))
            return
        self.signals.result.emit(result)
