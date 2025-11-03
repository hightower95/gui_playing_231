"""
Threading Utilities for Bootstrap Application
Provides decorators and utilities to simplify async operations
"""
import threading
import functools
from typing import Callable, Optional, Any
from tkinter import messagebox


def run_async(
    progress_callback: Optional[Callable] = None,
    busy_message: str = "Another step is running. Please wait.",
    error_callback: Optional[Callable] = None
):
    """
    Decorator to run a method asynchronously in a separate thread

    Args:
        progress_callback: Optional callback to execute during operation
        busy_message: Message to show if another operation is running
        error_callback: Optional callback to handle errors
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs) -> None:
            # Check if wizard is already running a step
            if hasattr(self, 'wizard') and getattr(self.wizard, 'running_step', False):
                messagebox.showwarning("Busy", busy_message)
                return

            # Set running flag
            if hasattr(self, 'wizard'):
                self.wizard.running_step = True

            def run_threaded():
                try:
                    # Execute progress callback if provided
                    if progress_callback:
                        progress_callback()

                    # Execute the original function
                    result = func(self, *args, **kwargs)
                    return result

                except Exception as e:
                    # Handle errors
                    if error_callback:
                        error_callback(e)
                    else:
                        # Default error handling
                        messagebox.showerror("Error", f"Operation failed: {e}")

                    # Log error if wizard has logging
                    if hasattr(self, 'wizard') and hasattr(self.wizard, 'log'):
                        self.wizard.log(
                            f"Error in {func.__name__}: {e}", "error")

                finally:
                    # Clear running flag
                    if hasattr(self, 'wizard'):
                        self.wizard.running_step = False

            # Start the thread
            thread = threading.Thread(target=run_threaded, daemon=True)
            thread.start()

        return wrapper
    return decorator


def run_in_background(
    target_function: Callable,
    args: tuple = (),
    kwargs: dict = None,
    completion_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None
) -> threading.Thread:
    """
    Run a function in the background and handle completion/errors

    Args:
        target_function: Function to run in background
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        completion_callback: Called when function completes successfully
        error_callback: Called when function raises an exception

    Returns:
        The created thread object
    """
    if kwargs is None:
        kwargs = {}

    def run_with_callbacks():
        try:
            result = target_function(*args, **kwargs)
            if completion_callback:
                completion_callback(result)
        except Exception as e:
            if error_callback:
                error_callback(e)
            else:
                print(f"Background task error: {e}")

    thread = threading.Thread(target=run_with_callbacks, daemon=True)
    thread.start()
    return thread


class ThreadSafeProgress:
    """
    Thread-safe progress tracking for long-running operations
    """

    def __init__(self, total_steps: int = 100):
        self.total_steps = total_steps
        self.current_step = 0
        self.status_message = "Starting..."
        self.completed = False
        self.error = None
        self._lock = threading.Lock()

    def update(self, step: int, message: str = ""):
        """Update progress safely from any thread"""
        with self._lock:
            self.current_step = min(step, self.total_steps)
            if message:
                self.status_message = message

    def increment(self, message: str = ""):
        """Increment progress by 1 step"""
        with self._lock:
            self.current_step = min(self.current_step + 1, self.total_steps)
            if message:
                self.status_message = message

    def set_complete(self, message: str = "Complete"):
        """Mark operation as completed"""
        with self._lock:
            self.current_step = self.total_steps
            self.status_message = message
            self.completed = True

    def set_error(self, error: Exception):
        """Mark operation as failed with error"""
        with self._lock:
            self.error = error
            self.completed = True

    def get_progress(self) -> tuple:
        """Get current progress as (current, total, percentage, message, completed, error)"""
        with self._lock:
            percentage = (self.current_step / self.total_steps) * \
                100 if self.total_steps > 0 else 0
            return (
                self.current_step,
                self.total_steps,
                percentage,
                self.status_message,
                self.completed,
                self.error
            )

    def reset(self):
        """Reset progress to initial state"""
        with self._lock:
            self.current_step = 0
            self.status_message = "Starting..."
            self.completed = False
            self.error = None


def safe_ui_update(widget, method_name: str, *args, **kwargs):
    """
    Safely update UI widget from any thread

    Args:
        widget: Tkinter widget to update
        method_name: Name of the method to call on the widget
        *args, **kwargs: Arguments to pass to the method
    """
    try:
        # Schedule the UI update on the main thread
        if hasattr(widget, 'after'):
            def update():
                if hasattr(widget, method_name):
                    method = getattr(widget, method_name)
                    method(*args, **kwargs)

            widget.after(0, update)

    except Exception as e:
        print(f"Failed to update UI: {e}")


# Convenience decorators for common patterns

def with_progress_bar(progress_bar_widget):
    """Decorator to automatically update a progress bar during operation"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Start progress
            safe_ui_update(progress_bar_widget, 'start')

            try:
                result = func(self, *args, **kwargs)
                # Stop and reset progress on success
                safe_ui_update(progress_bar_widget, 'stop')
                return result
            except Exception as e:
                # Stop progress on error
                safe_ui_update(progress_bar_widget, 'stop')
                raise

        return wrapper
    return decorator


def with_status_update(status_label_widget, running_text: str = "Running...",
                       success_text: str = "Complete", error_text: str = "Error"):
    """Decorator to automatically update status labels during operation"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Set running status
            safe_ui_update(status_label_widget, 'config',
                           text=running_text, foreground="blue")

            try:
                result = func(self, *args, **kwargs)
                # Set success status
                safe_ui_update(status_label_widget, 'config',
                               text=success_text, foreground="green")
                return result
            except Exception as e:
                # Set error status
                safe_ui_update(status_label_widget, 'config',
                               text=f"{error_text}: {e}", foreground="red")
                raise

        return wrapper
    return decorator
