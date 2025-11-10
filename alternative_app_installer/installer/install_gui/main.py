

"""
Install GUI - Simple installation wizard interface

Design Principles:
- Provides a clean frame for each installation step
- Handles step navigation (Next/Cancel buttons)
- Displays step information and progress
- Delegates all installation logic to the InstallConductor
"""
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QFrame, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from .conductor import InstallConductor


class InstallGUI(QMainWindow):
    """
    Simple installation wizard GUI that provides a framework for steps.

    The GUI is responsible only for presentation and user interaction,
    while all installation logic is handled by the InstallConductor.
    """

    def __init__(self, installation_settings):
        """Initialize the installation GUI

        Args:
            installation_settings: Configuration from install_settings.ini
        """
        super().__init__()
        self.installation_settings = installation_settings

        # Create the conductor to manage installation steps
        self.conductor = InstallConductor(installation_settings)

        # Setup the GUI
        self.setup_ui()
        self.refresh_step_display()

    def setup_ui(self):
        """Setup the main installation wizard interface"""
        self.setWindowTitle("Application Installer")
        self.setGeometry(100, 100, 840, 700)  # 40% larger (was 600x500)
        self.setFixedSize(840, 700)  # Fixed size for consistent layout

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)  # Reduced from 20
        layout.setContentsMargins(20, 15, 20, 15)  # Reduced from 30

        # Header section
        self.create_header_section(layout)

        # Progress section
        self.create_progress_section(layout)

        # Step content frame (where each step displays its UI)
        self.create_step_frame(layout)

        # Navigation buttons
        self.create_navigation_section(layout)

    def create_header_section(self, layout):
        """Create the header with title and description"""
        # Title
        self.title_label = QLabel("Installing Application")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Description
        self.description_label = QLabel("Setting up your application...")
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)

    def create_progress_section(self, layout):
        """Create the step indicator combined with title"""
        # Combined title and step progress layout
        title_progress_frame = QFrame()
        title_progress_layout = QHBoxLayout(title_progress_frame)
        title_progress_layout.setContentsMargins(0, 0, 0, 0)
        title_progress_layout.setSpacing(15)

        # Title (moved from header)
        self.step_title_label = QLabel("Step Title")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.step_title_label.setFont(title_font)
        title_progress_layout.addWidget(self.step_title_label)

        title_progress_layout.addStretch()  # Push step indicator to right

        # Step progress label
        self.progress_label = QLabel("Step 1 of 5")
        title_progress_layout.addWidget(self.progress_label)

        layout.addWidget(title_progress_frame)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)  # Slightly smaller
        layout.addWidget(self.progress_bar)

    def create_step_frame(self, layout):
        """Create the frame where individual steps display their content"""
        # Step frame with border - remove explicit colors to use system defaults
        self.step_frame = QFrame()
        self.step_frame.setFrameStyle(QFrame.Shape.Box)
        self.step_frame.setLineWidth(1)

        # Layout for step content
        self.step_layout = QVBoxLayout(self.step_frame)
        self.step_layout.setSpacing(10)  # Reduced from 15
        self.step_layout.setContentsMargins(15, 15, 15, 15)  # Reduced padding

        # Hint text area - smaller font
        self.hint_label = QLabel()
        self.hint_label.setWordWrap(True)
        hint_font = QFont()
        hint_font.setPointSize(9)  # Smaller font for hints
        hint_font.setItalic(True)
        self.hint_label.setFont(hint_font)
        self.step_layout.addWidget(self.hint_label)

        # Content area where steps can add their widgets
        self.step_content_frame = QFrame()
        self.step_content_layout = QVBoxLayout(self.step_content_frame)
        self.step_content_layout.setSpacing(8)  # Reduced spacing
        self.step_layout.addWidget(self.step_content_frame)

        # Add step frame to main layout with more space allocation
        layout.addWidget(self.step_frame, 1)  # Expand to fill available space

    def create_navigation_section(self, layout):
        """Create the navigation buttons (Complete Step / Cancel)"""
        # Button layout with reduced spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)  # Reduced spacing between buttons
        button_layout.addStretch()  # Push buttons to the right

        # Cancel button
        self.cancel_button = QPushButton("Cancel Installation")
        self.cancel_button.setMinimumSize(140, 35)
        self.cancel_button.clicked.connect(self.cancel_installation)
        button_layout.addWidget(self.cancel_button)

        # Complete step button
        self.complete_button = QPushButton("Complete Step")
        self.complete_button.setMinimumSize(140, 35)
        self.complete_button.setDefault(True)  # Default button for Enter key
        self.complete_button.clicked.connect(self.complete_current_step)
        button_layout.addWidget(self.complete_button)

        layout.addLayout(button_layout)

    def refresh_step_display(self):
        """Refresh the display to show current step information"""
        step_info = self.conductor.get_step_info()

        # Update header (main app title stays the same)
        self.title_label.setText("Installing Application")
        self.description_label.setText(step_info.get(
            "description", "Setting up your application..."))

        # Update step title and progress on same line
        self.step_title_label.setText(step_info.get("title", "Step"))
        step_num = step_info.get("step_number", 1)
        total_steps = step_info.get("total_steps", 1)
        self.progress_label.setText(f"Step {step_num} of {total_steps}")

        progress_percent = int((step_num / total_steps) * 100)
        self.progress_bar.setValue(progress_percent)

        # Update hint text
        hint_text = step_info.get("hint_text", "")
        self.hint_label.setText(hint_text)
        self.hint_label.setVisible(bool(hint_text))

        # Update button states
        self.complete_button.setEnabled(step_info.get("can_complete", False))
        self.cancel_button.setEnabled(step_info.get("can_cancel", True))

        # Update button text for final step
        if self.conductor.is_installation_complete():
            self.complete_button.setText("Finish")
        else:
            self.complete_button.setText("Complete Step")

        # Clear and populate step content
        self.clear_step_content()
        self.populate_step_content()

    def clear_step_content(self):
        """Clear the step content area"""
        # Remove all widgets from step content layout
        while self.step_content_layout.count():
            child = self.step_content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def populate_step_content(self):
        """Populate the step content area with current step's widgets"""
        current_step = self.conductor.get_current_step()
        if current_step and hasattr(current_step, 'create_widgets'):
            # Let the step create its own widgets in the provided frame
            current_step.create_widgets(
                self.step_content_frame, self.step_content_layout)
        else:
            # Default content if step doesn't provide widgets
            default_label = QLabel("Step content will appear here...")
            default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.step_content_layout.addWidget(default_label)

    def complete_current_step(self):
        """Handle Complete Step button click"""
        if self.conductor.is_installation_complete():
            # Installation is complete, close the installer
            self.finish_installation()
            return

        # Try to complete the current step
        success = self.conductor.complete_current_step()

        if success:
            # Step completed, refresh display for next step
            self.refresh_step_display()

            # Check if installation is now complete
            if self.conductor.is_installation_complete():
                self.show_completion_message()
        else:
            # Step could not be completed, show error
            QMessageBox.warning(
                self,
                "Step Incomplete",
                "Please complete all required fields before proceeding to the next step."
            )

    def cancel_installation(self):
        """Handle Cancel Installation button click"""
        reply = QMessageBox.question(
            self,
            "Cancel Installation",
            "Are you sure you want to cancel the installation?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.conductor.cancel_installation()
            self.close()

    def show_completion_message(self):
        """Show installation completion message"""
        QMessageBox.information(
            self,
            "Installation Complete",
            "The application has been installed successfully!\n\nYou can now close this installer."
        )

    def finish_installation(self):
        """Finish the installation and close the installer"""
        self.close()

    def launch(self):
        """Launch the installation GUI"""
        self.show()
        return True


def launch_installer_gui(installation_settings):
    """Launch the installer GUI application

    Args:
        installation_settings: Configuration from install_settings.ini

    Returns:
        bool: True if installation completed successfully, False otherwise
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create and show installer GUI
    installer_gui = InstallGUI(installation_settings)
    installer_gui.launch()

    # Run the application event loop
    result = app.exec()

    # Return success based on whether installation completed
    return installer_gui.conductor.is_installation_complete()
