"""Setup Report Panel - Main panel for configuring report inputs"""
from typing import List, Dict
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PySide6.QtCore import Signal
from .header import ReportHeader
from .summary_tab import SummaryTab
from .document_tab import DocumentTab
from .settings_tab import SettingsTab
from .footer import ReportFooter
from .styles import PANEL_STYLE, TAB_STYLE


class SetupReportPanel(QWidget):
    """Main panel for report configuration (replaces modal dialog)"""

    report_executed = Signal(str, dict)  # Emits (report_title, parameters)
    cancelled = Signal()

    def __init__(self, report_title: str, report_description: str,
                 required_inputs: List[str], parent=None):
        super().__init__(parent)
        self.report_title = report_title
        self.report_description = report_description
        self.required_inputs = required_inputs
        self.input_values: Dict[str, str] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup panel UI"""
        self.setStyleSheet(PANEL_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header = ReportHeader(self.report_title, self.report_description)
        layout.addWidget(header)

        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(TAB_STYLE)
        layout.addWidget(self.tabs, stretch=1)

        # Summary tab
        self.summary_tab = SummaryTab(self.required_inputs)
        self.tabs.addTab(self.summary_tab, "Summary")

        # Document tabs
        self.document_tabs = {}
        for input_name in self.required_inputs:
            doc_tab = DocumentTab(input_name, is_required=True)
            doc_tab.file_selected.connect(self._on_file_selected)
            self.document_tabs[input_name] = doc_tab
            self.tabs.addTab(doc_tab, input_name)

        # Settings tab
        self.settings_tab = SettingsTab()
        self.tabs.addTab(self.settings_tab, "Settings")

        # Footer
        self.footer = ReportFooter()
        self.footer.cancel_clicked.connect(self.cancelled.emit)
        self.footer.save_draft_clicked.connect(self._on_save_draft)
        self.footer.run_report_clicked.connect(self._on_run_report)
        layout.addWidget(self.footer)

        # Initial state
        self._update_footer_state()

    def _on_file_selected(self, input_name: str, file_path: str):
        """Handle file selection from document tab"""
        self.input_values[input_name] = file_path
        self.summary_tab.update_input_value(input_name, file_path)
        self._update_footer_state()

    def _update_footer_state(self):
        """Update footer based on input completion"""
        all_filled = all(
            self.input_values.get(inp, "") for inp in self.required_inputs
        )
        missing_count = sum(
            1 for inp in self.required_inputs
            if not self.input_values.get(inp, "")
        )
        self.footer.set_ready_state(all_filled, missing_count)

    def _on_save_draft(self):
        """Handle Save as Draft"""
        # TODO: Implement draft saving
        print(f"[SetupReportPanel] Save as draft: {self.input_values}")

    def _on_run_report(self):
        """Handle Run Report"""
        # Collect all parameters
        parameters = self.input_values.copy()
        parameters.update(self.settings_tab.get_settings())

        print(f"[SetupReportPanel] Running report: {self.report_title}")
        print(f"[SetupReportPanel] Parameters: {parameters}")

        self.report_executed.emit(self.report_title, parameters)

    def get_parameters(self) -> Dict[str, str]:
        """Get all configured parameters"""
        parameters = self.input_values.copy()
        parameters.update(self.settings_tab.get_settings())
        return parameters
