"""
Filter Buttons - Dropdown filters and clear button

Provides filter comboboxes for Project, Focus Area, Report Type, and Scope.
"""
from typing import Optional, List
from PySide6.QtWidgets import QWidget, QHBoxLayout, QComboBox, QPushButton
from PySide6.QtCore import Qt, Signal


class FilterButtons(QWidget):
    """Filter dropdown buttons and clear filters button"""

    # Signals
    filters_changed = Signal(dict)  # Emits dict with filter values
    filters_cleared = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize filter buttons"""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup filter buttons UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Project filter
        self.project_combo = self._create_filter_combo("Project")
        self.project_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self.project_combo)

        # Focus Area filter
        self.focus_area_combo = self._create_filter_combo("Focus Area")
        self.focus_area_combo.currentIndexChanged.connect(
            self._on_filter_changed)
        layout.addWidget(self.focus_area_combo)

        # Report Type filter
        self.report_type_combo = self._create_filter_combo("Report Type")
        self.report_type_combo.currentIndexChanged.connect(
            self._on_filter_changed)
        layout.addWidget(self.report_type_combo)

        # Scope filter
        self.scope_combo = self._create_filter_combo("Scope")
        self.scope_combo.currentIndexChanged.connect(self._on_filter_changed)
        layout.addWidget(self.scope_combo)

        layout.addStretch()

        # Clear filters button
        clear_btn = QPushButton("Clear all filters")
        clear_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                background-color: transparent;
                color: #4fc3f7;
                font-size: 9pt;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self._on_clear_clicked)
        layout.addWidget(clear_btn)

    def _create_filter_combo(self, label: str) -> QComboBox:
        """Create a styled filter combobox

        Args:
            label: Label for the combobox

        Returns:
            Configured QComboBox
        """
        combo = QComboBox()
        combo.addItem(label)
        combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                background-color: #2a2a2a;
                color: #b0b0b0;
                font-size: 9pt;
                min-width: 120px;
            }
            QComboBox:hover {
                border: 1px solid #4a4a4a;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                selection-background-color: #353535;
                color: #ffffff;
            }
        """)
        combo.setCursor(Qt.CursorShape.PointingHandCursor)
        return combo

    def _on_filter_changed(self):
        """Handle filter change and emit signal"""
        filters = self.get_current_filters()
        self.filters_changed.emit(filters)

    def _on_clear_clicked(self):
        """Clear all filters"""
        self.project_combo.setCurrentIndex(0)
        self.focus_area_combo.setCurrentIndex(0)
        self.report_type_combo.setCurrentIndex(0)
        self.scope_combo.setCurrentIndex(0)
        self.filters_cleared.emit()

    def get_current_filters(self) -> dict:
        """Get current filter values

        Returns:
            Dict with filter keys and values
        """
        return {
            'project': self.project_combo.currentText() if self.project_combo.currentIndex() > 0 else None,
            'focus_area': self.focus_area_combo.currentText() if self.focus_area_combo.currentIndex() > 0 else None,
            'report_type': self.report_type_combo.currentText() if self.report_type_combo.currentIndex() > 0 else None,
            'scope': self.scope_combo.currentText() if self.scope_combo.currentIndex() > 0 else None,
        }

    def populate_options(self, projects: List[str] = None, focus_areas: List[str] = None):
        """Populate dropdown options

        Args:
            projects: List of project names
            focus_areas: List of focus area names
        """
        if projects:
            current = self.project_combo.currentIndex()
            self.project_combo.clear()
            self.project_combo.addItem("Project")
            self.project_combo.addItems(projects)
            self.project_combo.setCurrentIndex(
                0 if current == 0 else min(current, len(projects)))

        if focus_areas:
            current = self.focus_area_combo.currentIndex()
            self.focus_area_combo.clear()
            self.focus_area_combo.addItem("Focus Area")
            self.focus_area_combo.addItems(focus_areas)
            self.focus_area_combo.setCurrentIndex(
                0 if current == 0 else min(current, len(focus_areas)))
