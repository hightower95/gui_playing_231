"""
Base Data Worker - Common pattern for background data loading

Provides a threadsafe worker pattern for loading data in a separate thread
with progress updates and cancellation support.
"""
from typing import Optional, Callable
from PySide6.QtCore import QObject, Signal


class BaseDataWorker(QObject):
    """
    Base worker class for loading data in a separate thread.

    Subclasses should override:
    - run(): Main entry point - call progress.emit() and finished.emit()
    - Optionally define _load_data() or similar private methods for actual work

    Example usage:
        class MyDataWorker(BaseDataWorker):
            def run(self):
                try:
                    if self._is_cancelled:
                        return
                    self.progress.emit(20, "Connecting...")

                    # Do work...
                    data = self._load_my_data()

                    if not self._is_cancelled:
                        self.progress.emit(100, "Complete")
                        self.finished.emit(data)
                except Exception as e:
                    self.error.emit(f"Failed: {str(e)}")
    """

    # Signals to communicate with main thread
    progress = Signal(int, str)  # progress_percent, status_message
    finished = Signal(object)  # loaded data (any type)
    error = Signal(str)  # error_message

    def __init__(self):
        super().__init__()
        self._is_cancelled = False

    def cancel(self):
        """Cancel the loading operation. Thread-safe."""
        self._is_cancelled = True

    @property
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self._is_cancelled

    def run(self):
        """
        Execute the data loading in background thread.

        Subclasses must override this method to implement actual data loading.
        Should check self._is_cancelled periodically and emit progress/finished/error signals.
        """
        raise NotImplementedError("Subclasses must implement run()")

    def emit_progress(self, percent: int, message: str) -> bool:
        """
        Emit progress and check for cancellation.

        Returns True if operation should continue, False if cancelled.
        Use as: if not self.emit_progress(50, "Loading..."): return
        """
        if self._is_cancelled:
            return False
        self.progress.emit(percent, message)
        return True
