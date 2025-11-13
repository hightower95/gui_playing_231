"""
Component Demo - Phase 1 & 2 Components

This demo showcases all the newly created components from Phase 1 and 2.
Run this file to see the components in action.
"""

from productivity_core.ui.components import (
    StandardButton, ButtonRole, ButtonSize,
    StandardLabel, TextStyle,
    StandardCheckBox,
    StandardProgressBar,
    StandardRadioButton, create_radio_group,
    StandardTextArea,
    StandardSpinBox,
    StandardGroupBox,
    StandardFormLayout,
    StandardWarningDialog, DialogResult,
    StandardComboBox, ComboSize,
    StandardInput,
    create_button_row
)
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PySide6.QtCore import Qt
import sys

# Add parent directory to path for imports
sys.path.insert(
    0, 'c:/Users/peter/OneDrive/Documents/Coding/gui/swiss_army_tool')


class ComponentDemoWindow(QMainWindow):
    """Demo window showcasing all Phase 1 & 2 components"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Swiss Army Tool - Phase 1 & 2 Components Demo")
        self.setMinimumSize(1000, 700)

        # Set window background color for better contrast
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)

        # Create scroll area for main content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)

        # Create main widget and layout
        main_widget = QWidget()
        scroll.setWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Add title
        title = StandardLabel("🎨 Component Library Demo",
                              style=TextStyle.TITLE)
        main_layout.addWidget(title)

        instructions = StandardLabel(
            "Click section titles to expand/collapse", style=TextStyle.NOTES)
        main_layout.addWidget(instructions)
        main_layout.addSpacing(10)

        # Demo sections
        self._add_label_styles_demo(main_layout)
        self._add_checkbox_demo(main_layout)
        self._add_progress_bar_demo(main_layout)
        self._add_radio_button_demo(main_layout)
        self._add_text_area_demo(main_layout)
        self._add_spin_box_demo(main_layout)
        self._add_form_layout_demo(main_layout)
        self._add_dialog_demo(main_layout)

        main_layout.addStretch()

    def _create_collapsible_section(self, title, content_widget):
        """Create a collapsible section with a toggle button"""
        # Container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Toggle button
        toggle_btn = StandardButton(
            f"▼ {title}",
            role=ButtonRole.SECONDARY,
            size=ButtonSize.FULL
        )
        toggle_btn.setMinimumHeight(40)
        toggle_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
                font-weight: bold;
                font-size: 11pt;
            }
        """)

        # Content is initially visible
        content_widget.setVisible(True)
        toggle_btn._is_expanded = True

        def toggle():
            is_expanded = toggle_btn._is_expanded
            content_widget.setVisible(not is_expanded)
            toggle_btn.setText(f"{'▼' if not is_expanded else '▶'} {title}")
            toggle_btn._is_expanded = not is_expanded

        toggle_btn.clicked.connect(toggle)

        container_layout.addWidget(toggle_btn)
        container_layout.addWidget(content_widget)

        return container

    def _add_label_styles_demo(self, layout):
        """Demo all label text styles"""
        # Create content widget
        content = QWidget()
        content.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        group_layout = QVBoxLayout(content)
        group_layout.setSpacing(20)
        group_layout.setContentsMargins(20, 25, 20, 20)

        # Add descriptive header with background
        header_widget = QWidget()
        header_widget.setStyleSheet(
            "background-color: #e3f2fd; padding: 12px; border-radius: 4px;")
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(12, 12, 12, 12)
        header = StandardLabel(
            "📋 These labels demonstrate different text styles and sizes", style=TextStyle.SECTION)
        header_layout.addWidget(header)
        group_layout.addWidget(header_widget)

        # Helper function to create a styled example box
        def create_style_box(style_label, style_enum, description, bg_color="#ffffff"):
            widget = QWidget()
            widget.setStyleSheet(
                f"background-color: {bg_color}; padding: 15px; border-radius: 6px; border: 2px solid #ddd;")
            widget.setMinimumHeight(80)
            box_layout = QVBoxLayout(widget)
            box_layout.setContentsMargins(15, 15, 15, 15)
            box_layout.setSpacing(8)

            # The actual styled label
            label = StandardLabel(style_label, style=style_enum)
            label.setMinimumHeight(25)
            label.setWordWrap(True)
            box_layout.addWidget(label)

            # Description below
            desc = StandardLabel(description, style=TextStyle.NOTES)
            desc.setMinimumHeight(20)
            desc.setWordWrap(True)
            box_layout.addWidget(desc)

            box_layout.addStretch()

            return widget

        # Show all text styles with colored backgrounds for visibility
        group_layout.addWidget(create_style_box(
            "TITLE STYLE",
            TextStyle.TITLE,
            "→ 14pt bold black - Use for main page titles",
            "#fff3e0"
        ))

        group_layout.addWidget(create_style_box(
            "SECTION STYLE",
            TextStyle.SECTION,
            "→ 12pt bold black - Use for section headers",
            "#f3e5f5"
        ))

        group_layout.addWidget(create_style_box(
            "Subsection Style",
            TextStyle.SUBSECTION,
            "→ 11pt bold dark gray - Use for subsection headers",
            "#e8f5e9"
        ))

        group_layout.addWidget(create_style_box(
            "Label Style",
            TextStyle.LABEL,
            "→ 10pt normal black - Use for standard form labels",
            "#e1f5fe"
        ))

        group_layout.addWidget(create_style_box(
            "Notes Style - This text appears lighter and italic",
            TextStyle.NOTES,
            "→ 9pt italic light gray - Use for helper text and hints",
            "#fce4ec"
        ))

        group_layout.addWidget(create_style_box(
            "Status Style",
            TextStyle.STATUS,
            "→ 10pt normal gray - Use for status messages",
            "#fff9c4"
        ))

        # Separator
        group_layout.addSpacing(10)
        separator = StandardLabel("─" * 90, style=TextStyle.NOTES)
        group_layout.addWidget(separator)
        group_layout.addSpacing(10)

        # Color examples with colored backgrounds
        color_header_widget = QWidget()
        color_header_widget.setStyleSheet(
            "background-color: #e3f2fd; padding: 12px; border-radius: 4px;")
        color_header_layout = QVBoxLayout(color_header_widget)
        color_header_layout.setContentsMargins(12, 12, 12, 12)
        color_header = StandardLabel(
            "🎨 CUSTOM COLORS", style=TextStyle.SECTION)
        color_header_layout.addWidget(color_header)
        color_desc = StandardLabel(
            "Any style can have custom colors applied:", style=TextStyle.NOTES)
        color_header_layout.addWidget(color_desc)
        group_layout.addWidget(color_header_widget)
        group_layout.addSpacing(10)

        # Color examples with individual backgrounds
        success_widget = QWidget()
        success_widget.setStyleSheet(
            "background-color: #ffffff; padding: 12px; border-radius: 4px; border: 3px solid #28a745;")
        success_widget.setMinimumHeight(60)
        success_layout = QVBoxLayout(success_widget)
        success_layout.setContentsMargins(12, 12, 12, 12)
        success_label = StandardLabel(
            "✓ Success - Operation completed successfully", style=TextStyle.LABEL)
        success_label.set_color("#28a745")
        success_label.setMinimumHeight(25)
        success_label.setWordWrap(True)
        success_layout.addWidget(success_label)
        group_layout.addWidget(success_widget)

        error_widget = QWidget()
        error_widget.setStyleSheet(
            "background-color: #ffffff; padding: 12px; border-radius: 4px; border: 3px solid #dc3545;")
        error_widget.setMinimumHeight(60)
        error_layout = QVBoxLayout(error_widget)
        error_layout.setContentsMargins(12, 12, 12, 12)
        error_label = StandardLabel(
            "✗ Error - Something went wrong", style=TextStyle.LABEL)
        error_label.set_color("#dc3545")
        error_label.setMinimumHeight(25)
        error_label.setWordWrap(True)
        error_layout.addWidget(error_label)
        group_layout.addWidget(error_widget)

        warning_widget = QWidget()
        warning_widget.setStyleSheet(
            "background-color: #ffffff; padding: 12px; border-radius: 4px; border: 3px solid #ff8c00;")
        warning_widget.setMinimumHeight(60)
        warning_layout = QVBoxLayout(warning_widget)
        warning_layout.setContentsMargins(12, 12, 12, 12)
        warning_label = StandardLabel(
            "⚠ Warning - Please review this carefully", style=TextStyle.LABEL)
        warning_label.set_color("#ff8c00")
        warning_label.setMinimumHeight(25)
        warning_label.setWordWrap(True)
        warning_layout.addWidget(warning_label)
        group_layout.addWidget(warning_widget)

        info_widget = QWidget()
        info_widget.setStyleSheet(
            "background-color: #ffffff; padding: 12px; border-radius: 4px; border: 3px solid #0066cc;")
        info_widget.setMinimumHeight(60)
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(12, 12, 12, 12)
        info_label = StandardLabel(
            "ℹ Information - Additional details available", style=TextStyle.LABEL)
        info_label.set_color("#0066cc")
        info_label.setMinimumHeight(25)
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        group_layout.addWidget(info_widget)

        # Add collapsible section
        collapsible = self._create_collapsible_section(
            "StandardLabel - Text Styles", content)
        layout.addWidget(collapsible)

    def _add_checkbox_demo(self, layout):
        """Demo checkboxes"""
        content = QWidget()
        content.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        group_layout = QVBoxLayout(content)
        group_layout.setContentsMargins(20, 25, 20, 20)
        group_layout.setSpacing(15)

        # Basic checkboxes
        check1 = StandardCheckBox("Enable feature", checked=True)
        check1.toggled.connect(lambda c: print(f"Feature: {c}"))
        group_layout.addWidget(check1)

        check2 = StandardCheckBox("Auto-save")
        group_layout.addWidget(check2)

        # Tristate
        check3 = StandardCheckBox("Select All (tristate)", tristate=True)
        check3.state_changed.connect(lambda s: print(f"State: {s}"))
        group_layout.addWidget(check3)

        collapsible = self._create_collapsible_section(
            "StandardCheckBox", content)
        layout.addWidget(collapsible)

    def _add_progress_bar_demo(self, layout):
        """Demo progress bar"""
        content = QWidget()
        content.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        group_layout = QVBoxLayout(content)
        group_layout.setContentsMargins(20, 25, 20, 20)
        group_layout.setSpacing(15)

        # Progress bar
        self.progress = StandardProgressBar(show_percentage=True)
        self.progress.set_value(65)
        group_layout.addWidget(self.progress)

        # Buttons to control progress
        btn_layout = QHBoxLayout()
        btn_reset = StandardButton(
            "Reset", role=ButtonRole.SECONDARY, size=ButtonSize.COMPACT)
        btn_reset.clicked.connect(lambda: self.progress.reset())
        btn_layout.addWidget(btn_reset)

        btn_50 = StandardButton(
            "50%", role=ButtonRole.INFO, size=ButtonSize.COMPACT)
        btn_50.clicked.connect(lambda: self.progress.set_value(50))
        btn_layout.addWidget(btn_50)

        btn_100 = StandardButton(
            "100%", role=ButtonRole.SUCCESS, size=ButtonSize.COMPACT)
        btn_100.clicked.connect(lambda: self.progress.set_value(100))
        btn_layout.addWidget(btn_100)
        btn_layout.addStretch()

        group_layout.addLayout(btn_layout)

        collapsible = self._create_collapsible_section(
            "StandardProgressBar", content)
        layout.addWidget(collapsible)

    def _add_radio_button_demo(self, layout):
        """Demo radio buttons"""
        content = QWidget()
        content.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        group_layout = QVBoxLayout(content)
        group_layout.setContentsMargins(20, 25, 20, 20)
        group_layout.setSpacing(15)

        # Create radio buttons
        radio1 = StandardRadioButton("Use E3 Connect", checked=True)
        radio2 = StandardRadioButton("Use E3 Cache")
        radio3 = StandardRadioButton("Manual Mode")

        # Group them
        self.radio_group = create_radio_group(
            radio1, radio2, radio3, default_index=0)

        # Add to layout
        group_layout.addWidget(radio1)
        group_layout.addWidget(radio2)
        group_layout.addWidget(radio3)

        # Connect signals
        radio1.toggled.connect(lambda c: print(
            f"E3 Connect: {c}") if c else None)
        radio2.toggled.connect(lambda c: print(
            f"E3 Cache: {c}") if c else None)
        radio3.toggled.connect(lambda c: print(f"Manual: {c}") if c else None)

        collapsible = self._create_collapsible_section(
            "StandardRadioButton", content)
        layout.addWidget(collapsible)

    def _add_text_area_demo(self, layout):
        """Demo text area"""
        content = QWidget()
        content.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        group_layout = QVBoxLayout(content)
        group_layout.setContentsMargins(20, 25, 20, 20)
        group_layout.setSpacing(15)

        # Editable text area
        text_area = StandardTextArea(
            placeholder="Enter your notes here...",
            height=100
        )
        text_area.text_changed.connect(lambda: print("Text changed"))
        group_layout.addWidget(text_area)

        # Read-only display
        display = StandardTextArea(
            text="This is a read-only text area.\nYou can use it for logs or results.",
            read_only=True,
            height=80
        )
        group_layout.addWidget(display)

        collapsible = self._create_collapsible_section(
            "StandardTextArea", content)
        layout.addWidget(collapsible)

    def _add_spin_box_demo(self, layout):
        """Demo spin box"""
        content = QWidget()
        content.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        group_layout = QHBoxLayout(content)
        group_layout.setContentsMargins(20, 25, 20, 20)
        group_layout.setSpacing(15)

        # Basic spin box
        spin1 = StandardSpinBox(min_value=1, max_value=100, default_value=10)
        spin1.value_changed.connect(lambda v: print(f"Value: {v}"))
        group_layout.addWidget(StandardLabel("Row:", style=TextStyle.LABEL))
        group_layout.addWidget(spin1)

        # With suffix
        spin2 = StandardSpinBox(min_value=8, max_value=72,
                                default_value=12, suffix=" pt")
        group_layout.addWidget(StandardLabel(
            "Font Size:", style=TextStyle.LABEL))
        group_layout.addWidget(spin2)

        # Percentage
        spin3 = StandardSpinBox(
            min_value=0, max_value=100, default_value=50, suffix=" %")
        group_layout.addWidget(StandardLabel(
            "Progress:", style=TextStyle.LABEL))
        group_layout.addWidget(spin3)

        group_layout.addStretch()

        collapsible = self._create_collapsible_section(
            "StandardSpinBox", content)
        layout.addWidget(collapsible)

    def _add_form_layout_demo(self, layout):
        """Demo form layout"""
        content = QWidget()
        content.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 25, 20, 20)

        # Create form
        form = StandardFormLayout(label_width=120)

        # Add section
        form.add_section("Basic Settings")

        # Add rows
        form.add_row("Name:", StandardInput(placeholder="Enter name..."))
        form.add_row("Version:", StandardComboBox(
            size=ComboSize.SINGLE, items=["v1.0", "v2.0", "v3.0"]))
        form.add_row("Output:", StandardInput(placeholder="Output path..."))

        # Add another section
        form.add_section("Advanced Options")

        # Add checkboxes
        form.add_widget(StandardCheckBox("Enable advanced mode"))
        form.add_widget(StandardCheckBox("Use cache"))

        # Add spacing
        form.add_spacing(10)

        # Add spin box row
        form.add_row("Timeout:", StandardSpinBox(
            min_value=1, max_value=300, default_value=30, suffix=" sec"))

        content_layout.addLayout(form)

        collapsible = self._create_collapsible_section(
            "StandardFormLayout", content)
        layout.addWidget(collapsible)

    def _add_dialog_demo(self, layout):
        """Demo warning dialog"""
        content = QWidget()
        content.setStyleSheet(
            "background-color: white; border: 1px solid #ccc; border-radius: 4px;")
        group_layout = QHBoxLayout(content)
        group_layout.setContentsMargins(20, 25, 20, 20)
        group_layout.setSpacing(15)

        # Info button
        btn_info = StandardButton(
            "Info Dialog", role=ButtonRole.INFO, size=ButtonSize.COMPACT)
        btn_info.clicked.connect(self._show_info_dialog)
        group_layout.addWidget(btn_info)

        # Warning button
        btn_warning = StandardButton(
            "Warning Dialog", role=ButtonRole.WARNING, size=ButtonSize.COMPACT)
        btn_warning.clicked.connect(self._show_warning_dialog)
        group_layout.addWidget(btn_warning)

        # Error button
        btn_error = StandardButton(
            "Error Dialog", role=ButtonRole.DANGER, size=ButtonSize.COMPACT)
        btn_error.clicked.connect(self._show_error_dialog)
        group_layout.addWidget(btn_error)

        # Yes/No button
        btn_yes_no = StandardButton(
            "Yes/No Dialog", role=ButtonRole.PRIMARY, size=ButtonSize.COMPACT)
        btn_yes_no.clicked.connect(self._show_yes_no_dialog)
        group_layout.addWidget(btn_yes_no)

        # Yes/No/Cancel button
        btn_yes_no_cancel = StandardButton(
            "Yes/No/Cancel", role=ButtonRole.PRIMARY, size=ButtonSize.COMPACT)
        btn_yes_no_cancel.clicked.connect(self._show_yes_no_cancel_dialog)
        group_layout.addWidget(btn_yes_no_cancel)

        group_layout.addStretch()

        collapsible = self._create_collapsible_section(
            "StandardWarningDialog", content)
        layout.addWidget(collapsible)

    def _show_info_dialog(self):
        """Show info dialog"""
        StandardWarningDialog.show_info(
            self,
            "Information",
            "This is an informational message."
        )

    def _show_warning_dialog(self):
        """Show warning dialog"""
        StandardWarningDialog.show_warning(
            self,
            "Warning",
            "This is a warning message. Proceed with caution!"
        )

    def _show_error_dialog(self):
        """Show error dialog"""
        StandardWarningDialog.show_error(
            self,
            "Error",
            "An error has occurred. Please check the logs."
        )

    def _show_yes_no_dialog(self):
        """Show yes/no dialog"""
        result = StandardWarningDialog.show_yes_no(
            self,
            "Confirm Action",
            "Are you sure you want to proceed?"
        )
        if result == DialogResult.YES:
            print("User clicked YES")
        elif result == DialogResult.NO:
            print("User clicked NO")
        else:
            print("Dialog closed (CANCEL)")

    def _show_yes_no_cancel_dialog(self):
        """Show yes/no/cancel dialog"""
        result = StandardWarningDialog.show_yes_no_cancel(
            self,
            "Save Changes",
            "Do you want to save your changes before closing?"
        )
        if result == DialogResult.YES:
            print("User clicked YES - Save and close")
        elif result == DialogResult.NO:
            print("User clicked NO - Discard and close")
        else:
            print("User clicked CANCEL - Stay on page")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = ComponentDemoWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
