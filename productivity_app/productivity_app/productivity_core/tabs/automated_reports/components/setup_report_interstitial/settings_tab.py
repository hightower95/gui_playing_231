"""Settings tab - Report configuration options"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QCheckBox


class SettingsTab(QWidget):
    """Settings tab for report options"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup settings tab UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Output file name
        output_label = QLabel("Output File Name (Optional)")
        output_label.setStyleSheet("font-weight: bold; color: #e3e3e3;")
        layout.addWidget(output_label)

        self.output_filename = QLineEdit()
        self.output_filename.setPlaceholderText("Enter output file name")
        self.output_filename.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                color: #e3e3e3;
                padding: 6px;
            }
            QLineEdit:focus {
                border: 1px solid #0e639c;
            }
        """)
        layout.addWidget(self.output_filename)

        # Case sensitive comparison
        self.case_sensitive_checkbox = QCheckBox(
            "Case Sensitive Comparison (Optional)")
        self.case_sensitive_checkbox.setStyleSheet(
            "font-weight: bold; color: #e3e3e3;")
        self.case_sensitive_checkbox.setChecked(False)
        layout.addWidget(self.case_sensitive_checkbox)

        case_desc = QLabel("Match text case exactly")
        case_desc.setStyleSheet(
            "color: #a3a3a3; font-size: 11px; margin-left: 24px;")
        layout.addWidget(case_desc)

        # Timestamp checkbox
        self.timestamp_checkbox = QCheckBox("Include Timestamp (Optional)")
        self.timestamp_checkbox.setStyleSheet(
            "font-weight: bold; color: #e3e3e3;")
        self.timestamp_checkbox.setChecked(True)
        layout.addWidget(self.timestamp_checkbox)

        timestamp_desc = QLabel("Add timestamp to report output")
        timestamp_desc.setStyleSheet(
            "color: #a3a3a3; font-size: 11px; margin-left: 24px;")
        layout.addWidget(timestamp_desc)

        layout.addStretch()

    def get_settings(self) -> dict:
        """Get all settings values"""
        return {
            'output_filename': self.output_filename.text(),
            'case_sensitive': self.case_sensitive_checkbox.isChecked(),
            'include_timestamp': self.timestamp_checkbox.isChecked()
        }
