"""
StandardFormLayout - Consistent form layout component

A form layout widget for creating consistent forms with labels and fields.

Parameters:
    label_width (Optional[int]): Fixed label width in pixels (default: 120px)
    parent (Optional[QWidget]): Parent widget

Methods:
    add_row(label: str, field: QWidget): Adds a labeled field row
    add_widget(widget: QWidget): Adds a widget spanning both columns
    add_section(title: str): Adds a section header
    add_spacing(height: int): Adds vertical spacing
    clear(): Removes all rows from the form

Example:
    >>> form = StandardFormLayout()
    >>> 
    >>> # Add section
    >>> form.add_section("Basic Settings")
    >>> 
    >>> # Add labeled fields
    >>> name_input = StandardInput(placeholder="Enter name...")
    >>> form.add_row("Name:", name_input)
    >>> 
    >>> version_combo = StandardComboBox(size=ComboSize.SINGLE)
    >>> form.add_row("Version:", version_combo)
    >>> 
    >>> # Add another section
    >>> form.add_section("Advanced Options")
    >>> 
    >>> # Add checkbox
    >>> enable_check = StandardCheckBox("Enable feature")
    >>> form.add_widget(enable_check)
    >>> 
    >>> # Add spacing
    >>> form.add_spacing(10)
"""

from PySide6.QtWidgets import QFormLayout, QWidget, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt
from typing import Optional
from .constants import COMPONENT_SIZES
from .label import StandardLabel
from .enums import TextStyle


class StandardFormLayout(QFormLayout):
    """A form layout widget for consistent forms"""

    def __init__(
        self,
        label_width: Optional[int] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self._label_width = label_width or COMPONENT_SIZES["form_label_width"]
        self._setup_form_layout()

    def _setup_form_layout(self):
        """Configure form layout properties"""
        self.setVerticalSpacing(COMPONENT_SIZES["form_row_spacing"])
        self.setHorizontalSpacing(12)
        self.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def add_row(self, label: str, field: QWidget):
        """Adds a labeled field row to the form

        Args:
            label: Label text (will be right-aligned)
            field: Widget to place in field column

        Example:
            >>> form.add_row("Name:", StandardInput())
        """
        label_widget = StandardLabel(label, style=TextStyle.LABEL)
        label_widget.setFixedWidth(self._label_width)
        super().addRow(label_widget, field)

    def add_widget(self, widget: QWidget):
        """Adds a widget spanning both columns

        Args:
            widget: Widget to add (spans label and field columns)

        Example:
            >>> form.add_widget(StandardCheckBox("Enable option"))
        """
        # Create empty label for alignment
        empty_label = QLabel()
        empty_label.setFixedWidth(self._label_width)
        super().addRow(empty_label, widget)

    def add_section(self, title: str):
        """Adds a section header to the form

        Args:
            title: Section title text

        Example:
            >>> form.add_section("Advanced Settings")
        """
        # Add spacing before section
        if self.rowCount() > 0:
            self.addItem(QSpacerItem(
                1, COMPONENT_SIZES["form_section_spacing"]))

        # Add section header spanning both columns
        section_label = StandardLabel(title, style=TextStyle.SECTION)
        super().addRow(section_label)

        # Add smaller spacing after section
        self.addItem(QSpacerItem(1, COMPONENT_SIZES["form_row_spacing"]))

    def add_spacing(self, height: int):
        """Adds vertical spacing

        Args:
            height: Height of spacing in pixels

        Example:
            >>> form.add_spacing(20)
        """
        spacer = QSpacerItem(
            1, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.addItem(spacer)

    def clear(self):
        """Removes all rows from the form"""
        while self.rowCount() > 0:
            self.removeRow(0)
