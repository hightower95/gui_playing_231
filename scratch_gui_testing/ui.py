"""
Simple Ping GUI - Live ping monitoring application
"""
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QLineEdit, QLabel, QGroupBox, QMessageBox
)
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QFont, QIcon
from ping import PingController


class PingOutputHandler(QObject):
    """Handler for ping output that emits Qt signals"""
    output_received = Signal(str)

    def __init__(self):
        super().__init__()

    def write_output(self, text: str):
        """Write output (called from ping module)"""
        self.output_received.emit(text)


class PingGUI(QMainWindow):
    """Main GUI window for ping monitoring"""

    def __init__(self):
        super().__init__()
        self.ping_controller = None
        self.output_handler = PingOutputHandler()

        # Connect the output handler signal to our update method
        self.output_handler.output_received.connect(self.update_output)

        self.setup_ui()
        self.setup_styling()

    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Live Ping Monitor")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("🌐 Live Ping Monitor")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Control panel
        control_group = QGroupBox("Ping Controls")
        control_layout = QVBoxLayout(control_group)

        # IP input row
        ip_layout = QHBoxLayout()
        ip_label = QLabel("Target IP/Hostname:")
        ip_label.setMinimumWidth(130)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText(
            "Enter IP address or hostname (e.g., 8.8.8.8, google.com)")
        self.ip_input.setText("8.8.8.8")  # Default to Google DNS

        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.ip_input)
        control_layout.addLayout(ip_layout)

        # Button row
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("🚀 Start Ping")
        self.start_button.setMinimumHeight(35)
        self.start_button.clicked.connect(self.start_ping)

        self.stop_button = QPushButton("🛑 Stop Ping")
        self.stop_button.setMinimumHeight(35)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_ping)

        self.clear_button = QPushButton("🗑️ Clear Output")
        self.clear_button.setMinimumHeight(35)
        self.clear_button.clicked.connect(self.clear_output)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()

        control_layout.addLayout(button_layout)
        layout.addWidget(control_group)

        # Output area
        output_group = QGroupBox("Ping Output")
        output_layout = QVBoxLayout(output_group)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setPlaceholderText("Ping output will appear here...")

        # Set monospace font for better ping output formatting
        output_font = QFont("Consolas", 10)
        if not output_font.exactMatch():
            output_font = QFont("Courier New", 10)
        self.output_area.setFont(output_font)

        output_layout.addWidget(self.output_area)
        layout.addWidget(output_group)

        # Status bar
        self.statusBar().showMessage("Ready to ping")

        # Allow Enter key to start ping
        self.ip_input.returnPressed.connect(self.start_ping)

    def setup_styling(self):
        """Apply styling to the application"""
        pass
        # self.setStyleSheet("""
        #     QMainWindow {
        #         background-color: #f0f0f0;
        #     }
        #     QGroupBox {
        #         font-weight: bold;
        #         border: 2px solid #cccccc;
        #         border-radius: 5px;
        #         margin-top: 10px;
        #         padding-top: 10px;
        #     }
        #     QGroupBox::title {
        #         subcontrol-origin: margin;
        #         left: 10px;
        #         padding: 0 5px 0 5px;
        #     }
        #     QPushButton {
        #         background-color: #4CAF50;
        #         border: none;
        #         color: white;
        #         padding: 8px 16px;
        #         text-align: center;
        #         font-size: 12px;
        #         border-radius: 4px;
        #     }
        #     QPushButton:hover {
        #         background-color: #45a049;
        #     }
        #     QPushButton:pressed {
        #         background-color: #3d8b40;
        #     }
        #     QPushButton:disabled {
        #         background-color: #cccccc;
        #         color: #666666;
        #     }
        #     QLineEdit {
        #         padding: 8px;
        #         border: 2px solid #ddd;
        #         border-radius: 4px;
        #         font-size: 11px;
        #     }
        #     QLineEdit:focus {
        #         border-color: #4CAF50;
        #     }
        #     QTextEdit {
        #         border: 2px solid #ddd;
        #         border-radius: 4px;
        #         background-color: #ffffff;
        #     }
        # """)

    def start_ping(self):
        """Start the ping operation"""
        ip = self.ip_input.text().strip()

        if not ip:
            QMessageBox.warning(self, "Input Error",
                                "Please enter an IP address or hostname.")
            return

        if self.ping_controller and self.ping_controller.is_running:
            QMessageBox.information(
                self, "Ping Running", "Ping is already running. Stop it first.")
            return

        # Create new ping controller
        self.ping_controller = PingController(self.output_handler.write_output)

        # Update UI state
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.ip_input.setEnabled(False)

        # Start pinging
        success = self.ping_controller.start_pinging(ip)

        if success:
            self.statusBar().showMessage(f"Pinging {ip}...")
        else:
            # Reset UI if ping failed to start
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.ip_input.setEnabled(True)
            self.statusBar().showMessage("Failed to start ping")

    def stop_ping(self):
        """Stop the ping operation"""
        if self.ping_controller:
            self.ping_controller.stop_pinging()

        # Update UI state
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.ip_input.setEnabled(True)
        self.statusBar().showMessage("Ping stopped")

    def clear_output(self):
        """Clear the output area"""
        self.output_area.clear()
        self.statusBar().showMessage("Output cleared")

    def update_output(self, text: str):
        """Update the output area with new text (called from signal)"""
        # Insert text at the end and scroll to bottom
        self.output_area.insertPlainText(text)

        # Auto-scroll to bottom to show latest output
        cursor = self.output_area.textCursor()
        cursor.movePosition(cursor.End)
        self.output_area.setTextCursor(cursor)

        # Limit output length to prevent memory issues
        # Keep only last 10000 characters
        if len(self.output_area.toPlainText()) > 10000:
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, 2000)
            cursor.removeSelectedText()

    def closeEvent(self, event):
        """Handle window close event"""
        if self.ping_controller and self.ping_controller.is_running:
            self.ping_controller.stop_pinging()
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Live Ping Monitor")

    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("ping_icon.ico"))
    except:
        pass  # Icon file not found, continue without it

    # Create and show main window
    window = PingGUI()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
