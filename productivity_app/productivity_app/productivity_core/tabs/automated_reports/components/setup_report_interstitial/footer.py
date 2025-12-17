"""Footer component - Action buttons and status"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal
from .styles import BUTTON_STYLE, PRIMARY_BUTTON_STYLE


class ReportFooter(QWidget):
    """Footer with action buttons"""

    cancel_clicked = Signal()
    save_draft_clicked = Signal()
    run_report_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup footer UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(12)

        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(BUTTON_STYLE)
        self.cancel_btn.clicked.connect(self.cancel_clicked.emit)
        layout.addWidget(self.cancel_btn)

        # Info label
        self.info_label = QLabel("⓵ Complete required inputs to run report")
        self.info_label.setStyleSheet("color: #a3a3a3; font-size: 11px;")
        layout.addWidget(self.info_label, stretch=1)

        # Save as Draft button
        self.draft_btn = QPushButton("Save as Draft")
        self.draft_btn.setStyleSheet(BUTTON_STYLE)
        self.draft_btn.clicked.connect(self.save_draft_clicked.emit)
        layout.addWidget(self.draft_btn)

        # Run Report button
        self.run_btn = QPushButton("Run Report")
        self.run_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.run_btn.setEnabled(False)
        self.run_btn.clicked.connect(self.run_report_clicked.emit)
        layout.addWidget(self.run_btn)

    def set_ready_state(self, is_ready: bool, missing_count: int = 0):
        """Update footer state based on input completion"""
        self.run_btn.setEnabled(is_ready)

        if is_ready:
            self.info_label.setText("✓ Ready to run")
            self.info_label.setStyleSheet("color: #4ec9b0; font-size: 11px;")
        else:
            self.info_label.setText(
                f"⓵ Complete required inputs to run report ({missing_count} remaining)"
            )
            self.info_label.setStyleSheet("color: #a3a3a3; font-size: 11px;")
