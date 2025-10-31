"""
Helper Functions

Utility functions for creating common UI patterns.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout


def create_button_row(*buttons, stretch_after: int = -1) -> QWidget:
    """Create a horizontal row of buttons with optional stretch

    Args:
        *buttons: Button widgets to add
        stretch_after: Index after which to add stretch (-1 for right-align)

    Returns:
        QWidget containing the button row

    Stretch Behavior:
        - stretch_after=-1: Buttons right-aligned (stretch before)
        - stretch_after=0: Buttons left-aligned (stretch after first button)
        - stretch_after=1: Stretch after second button

    Example:
        >>> # Left-aligned buttons
        >>> row = create_button_row(save_btn, cancel_btn, stretch_after=1)
        >>> 
        >>> # Right-aligned buttons
        >>> row = create_button_row(save_btn, cancel_btn, stretch_after=-1)
        >>> 
        >>> # Custom positioning
        >>> row = create_button_row(btn1, btn2, btn3, stretch_after=1)
    """
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)

    if stretch_after == -1:
        layout.addStretch()

    for i, button in enumerate(buttons):
        layout.addWidget(button)

        if stretch_after == i:
            layout.addStretch()

    return widget


def create_form_row(label_text: str, widget: QWidget, label_width: int = 100) -> QWidget:
    """Create a form row with label and input widget

    Args:
        label_text: Label text (will be styled as LABEL)
        widget: Input widget (StandardInput, StandardComboBox, etc.)
        label_width: Fixed width for label (for alignment across rows)

    Returns:
        QWidget containing the form row

    Example:
        >>> # Basic form row
        >>> row = create_form_row("Name:", StandardInput(placeholder="Enter name"))
        >>> 
        >>> # With combo box
        >>> row = create_form_row("Version:", StandardComboBox(size=ComboSize.SINGLE))
        >>> 
        >>> # Custom label width for longer labels
        >>> row = create_form_row(
        ...     "Document Name:",
        ...     StandardComboBox(size=ComboSize.DOUBLE),
        ...     label_width=150
        ... )
    """
    from .label import StandardLabel
    from .enums import TextStyle

    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)

    label = StandardLabel(label_text, style=TextStyle.LABEL)
    label.setFixedWidth(label_width)

    layout.addWidget(label)
    layout.addWidget(widget, 1)

    return container
