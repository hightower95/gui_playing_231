"""
Generic Background Worker - Reusable threading for background tasks
"""
from PySide6.QtCore import QThread, Signal
from typing import Callable, Any, Optional


class BackgroundWorker(QThread):
    """Generic worker for executing functions in background threads

    Usage:
        def my_task(arg1, arg2):
            # Do work
            return result

        worker = BackgroundWorker(my_task, arg1, arg2)
        worker.finished.connect(lambda result: print(f"Done: {result}"))
        worker.error.connect(lambda err: print(f"Error: {err}"))
        worker.start()
    """

    # Signals
    progress = Signal(int, str)  # progress_percent, status_message
    finished = Signal(object)  # result data
    error = Signal(str)  # error_message

    def __init__(self, work_func: Callable, *args, **kwargs):
        """Initialize background worker

        Args:
            work_func: Function to execute in background thread
            *args: Positional arguments to pass to work_func
            **kwargs: Keyword arguments to pass to work_func
        """
        super().__init__()
        self.work_func = work_func
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False

    def cancel(self):
        """Request cancellation of the background task"""
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """Check if cancellation was requested"""
        return self._is_cancelled

    def run(self):
        """Execute the work function in background thread"""
        try:
            # Execute the function
            result = self.work_func(*self.args, **self.kwargs)

            # Only emit if not cancelled
            if not self._is_cancelled:
                self.finished.emit(result)

        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))
                import traceback
                traceback.print_exc()


class ProgressiveBackgroundWorker(QThread):
    """Background worker with built-in progress reporting

    The work function should accept a progress_callback parameter:

    Usage:
        def my_task(items, progress_callback=None):
            for i, item in enumerate(items):
                if progress_callback:
                    progress_callback(i * 100 // len(items), f"Processing {item}")
                # Do work
            return result

        worker = ProgressiveBackgroundWorker(my_task, items)
        worker.progress.connect(lambda pct, msg: print(f"{pct}%: {msg}"))
        worker.finished.connect(lambda result: print(f"Done: {result}"))
        worker.start()
    """

    # Signals
    progress = Signal(int, str)  # progress_percent, status_message
    finished = Signal(object)  # result data
    error = Signal(str)  # error_message

    def __init__(self, work_func: Callable, *args, **kwargs):
        """Initialize progressive background worker

        Args:
            work_func: Function to execute (must accept progress_callback parameter)
            *args: Positional arguments to pass to work_func
            **kwargs: Keyword arguments to pass to work_func
        """
        super().__init__()
        self.work_func = work_func
        self.args = args
        self.kwargs = kwargs
        self._is_cancelled = False

    def cancel(self):
        """Request cancellation of the background task"""
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        """Check if cancellation was requested"""
        return self._is_cancelled

    def _progress_callback(self, percent: int, message: str):
        """Internal progress callback that emits signal"""
        if not self._is_cancelled:
            self.progress.emit(percent, message)

    def run(self):
        """Execute the work function with progress reporting"""
        try:
            # Inject progress callback
            self.kwargs['progress_callback'] = self._progress_callback

            # Execute the function
            result = self.work_func(*self.args, **self.kwargs)

            # Only emit if not cancelled
            if not self._is_cancelled:
                self.finished.emit(result)

        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(str(e))
                import traceback
                traceback.print_exc()
