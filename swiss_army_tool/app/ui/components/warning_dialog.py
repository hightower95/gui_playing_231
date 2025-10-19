"""
StandardWarningDialog - Consistent warning/message dialog component

A dialog for displaying warnings, confirmations, and messages with standard buttons.
Similar to C# MessageBox with predefined button configurations.

Static Methods:
    show_ok(parent, title, message) -> DialogResult:
        Shows dialog with OK button only
    
    show_yes_no(parent, title, message) -> DialogResult:
        Shows dialog with Yes and No buttons
    
    show_yes_no_cancel(parent, title, message) -> DialogResult:
        Shows dialog with Yes, No, and Cancel buttons
    
    show_info(parent, title, message) -> DialogResult:
        Shows informational dialog with OK button
    
    show_warning(parent, title, message) -> DialogResult:
        Shows warning dialog with OK button
    
    show_error(parent, title, message) -> DialogResult:
        Shows error dialog with OK button

Returns:
    DialogResult: OK, YES, NO, or CANCEL

Example:
    >>> # Simple OK dialog
    >>> result = StandardWarningDialog.show_info(
    ...     self, "Success", "Operation completed successfully!"
    ... )
    >>> 
    >>> # Yes/No confirmation
    >>> result = StandardWarningDialog.show_yes_no(
    ...     self, "Confirm", "Are you sure you want to delete this item?"
    ... )
    >>> if result == DialogResult.YES:
    ...     # Delete the item
    ...     pass
    >>> 
    >>> # Yes/No/Cancel with multiple options
    >>> result = StandardWarningDialog.show_yes_no_cancel(
    ...     self, "Save Changes", "Do you want to save your changes?"
    ... )
    >>> if result == DialogResult.YES:
    ...     save_changes()
    >>> elif result == DialogResult.NO:
    ...     discard_changes()
    >>> else:  # CANCEL
    ...     # Stay on current page
    ...     pass
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from typing import Optional
from .button import StandardButton
from .enums import ButtonRole, ButtonSize, DialogResult


class StandardWarningDialog(QDialog):
    """A dialog for warnings, confirmations, and messages"""

    def __init__(
        self,
        parent: Optional[QWidget],
        title: str,
        message: str,
        icon_type: str = "warning"
    ):
        super().__init__(parent)
        self._result = DialogResult.CANCEL
        self._setup_dialog(title, message, icon_type)

    def _setup_dialog(self, title: str, message: str, icon_type: str):
        """Configure dialog properties"""
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)

        # Create layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Add icon and message
        message_layout = QHBoxLayout()

        # Icon (optional - could add actual icons later)
        icon_label = QLabel(self._get_icon_text(icon_type))
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 32pt;
                padding: 10px;
            }
        """)
        message_layout.addWidget(icon_label)

        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #333333;
                padding: 10px;
            }
        """)
        message_layout.addWidget(message_label, 1)

        layout.addLayout(message_layout)

        # Store button layout reference for adding buttons
        self._button_layout = QHBoxLayout()
        self._button_layout.setSpacing(10)
        self._button_layout.addStretch()
        layout.addLayout(self._button_layout)

    def _get_icon_text(self, icon_type: str) -> str:
        """Returns emoji icon for dialog type"""
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "question": "❓"
        }
        return icons.get(icon_type, "⚠️")

    def _add_button(self, text: str, role: ButtonRole, result: DialogResult):
        """Adds a button to the dialog

        Args:
            text: Button text
            role: Button role (PRIMARY, SECONDARY, etc.)
            result: Result value when button is clicked
        """
        button = StandardButton(text, role=role, size=ButtonSize.COMPACT)
        button.clicked.connect(lambda: self._on_button_clicked(result))
        self._button_layout.addWidget(button)

    def _on_button_clicked(self, result: DialogResult):
        """Handles button click

        Args:
            result: Dialog result for this button
        """
        self._result = result
        self.accept()

    def get_result(self) -> DialogResult:
        """Returns the dialog result"""
        return self._result

    # ========================================================================
    # STATIC HELPER METHODS
    # ========================================================================

    @staticmethod
    def show_ok(parent: Optional[QWidget], title: str, message: str) -> DialogResult:
        """Shows dialog with OK button only

        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display

        Returns:
            DialogResult.OK or DialogResult.CANCEL (if closed)
        """
        dialog = StandardWarningDialog(parent, title, message, "warning")
        dialog._add_button("OK", ButtonRole.PRIMARY, DialogResult.OK)
        dialog.exec()
        return dialog.get_result()

    @staticmethod
    def show_yes_no(parent: Optional[QWidget], title: str, message: str) -> DialogResult:
        """Shows dialog with Yes and No buttons

        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display

        Returns:
            DialogResult.YES, DialogResult.NO, or DialogResult.CANCEL (if closed)
        """
        dialog = StandardWarningDialog(parent, title, message, "question")
        dialog._add_button("No", ButtonRole.SECONDARY, DialogResult.NO)
        dialog._add_button("Yes", ButtonRole.PRIMARY, DialogResult.YES)
        dialog.exec()
        return dialog.get_result()

    @staticmethod
    def show_yes_no_cancel(parent: Optional[QWidget], title: str, message: str) -> DialogResult:
        """Shows dialog with Yes, No, and Cancel buttons

        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display

        Returns:
            DialogResult.YES, DialogResult.NO, or DialogResult.CANCEL
        """
        dialog = StandardWarningDialog(parent, title, message, "question")
        dialog._add_button("Cancel", ButtonRole.SECONDARY, DialogResult.CANCEL)
        dialog._add_button("No", ButtonRole.SECONDARY, DialogResult.NO)
        dialog._add_button("Yes", ButtonRole.PRIMARY, DialogResult.YES)
        dialog.exec()
        return dialog.get_result()

    @staticmethod
    def show_info(parent: Optional[QWidget], title: str, message: str) -> DialogResult:
        """Shows informational dialog with OK button

        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display

        Returns:
            DialogResult.OK
        """
        dialog = StandardWarningDialog(parent, title, message, "info")
        dialog._add_button("OK", ButtonRole.PRIMARY, DialogResult.OK)
        dialog.exec()
        return dialog.get_result()

    @staticmethod
    def show_warning(parent: Optional[QWidget], title: str, message: str) -> DialogResult:
        """Shows warning dialog with OK button

        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display

        Returns:
            DialogResult.OK
        """
        dialog = StandardWarningDialog(parent, title, message, "warning")
        dialog._add_button("OK", ButtonRole.WARNING, DialogResult.OK)
        dialog.exec()
        return dialog.get_result()

    @staticmethod
    def show_error(parent: Optional[QWidget], title: str, message: str) -> DialogResult:
        """Shows error dialog with OK button

        Args:
            parent: Parent widget
            title: Dialog title
            message: Message to display

        Returns:
            DialogResult.OK
        """
        dialog = StandardWarningDialog(parent, title, message, "error")
        dialog._add_button("OK", ButtonRole.DANGER, DialogResult.OK)
        dialog.exec()
        return dialog.get_result()
