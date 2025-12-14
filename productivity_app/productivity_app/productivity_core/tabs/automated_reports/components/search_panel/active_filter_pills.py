"""
Active Filter Pills - Display active filters as removable pills

Shows currently active filters with X buttons to remove them.
"""
from typing import Optional, Dict, Set
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, Signal, QByteArray


class ActiveFilterPills(QWidget):
    """Display active filters as pills with remove buttons"""

    # Signals
    filter_removed = Signal(str, str)  # Emits (filter_key, filter_value)
    clear_all_clicked = Signal()  # Emits when clear all is clicked

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize active filter pills"""
        super().__init__(parent)
        self._setup_ui()
        self.hide()  # Hidden by default when no filters

    def _setup_ui(self):
        """Setup pills UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 5, 0, 0)
        main_layout.setSpacing(8)

        # Pills row
        pills_row = QWidget()
        self.pills_layout = QHBoxLayout(pills_row)
        self.pills_layout.setContentsMargins(0, 0, 0, 0)
        self.pills_layout.setSpacing(8)
        self.pills_layout.addStretch()
        main_layout.addWidget(pills_row)

        # Clear all button row
        clear_row = QWidget()
        clear_layout = QHBoxLayout(clear_row)
        clear_layout.setContentsMargins(0, 0, 0, 0)

        self.clear_all_btn = QPushButton("Clear all filters")
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
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
        self.clear_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_all_btn.clicked.connect(self.clear_all_clicked.emit)
        self.clear_all_btn.hide()
        clear_layout.addWidget(self.clear_all_btn)
        clear_layout.addStretch()
        main_layout.addWidget(clear_row)

    def update_filters(self, filters: Dict[str, Set[str]]):
        """Update displayed filter pills - one pill per selection

        Args:
            filters: Dict of active filters {key: set_of_values}
        """
        # Clear existing pills
        while self.pills_layout.count() > 1:  # Keep the stretch
            item = self.pills_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Count total selections
        total_selections = sum(len(values)
                               for values in filters.values() if values)

        if total_selections == 0:
            self.hide()
            self.clear_all_btn.hide()
            return

        self.show()
        self.clear_all_btn.show()
        self.clear_all_btn.setText(f"Clear all filters ({total_selections})")

        # Add individual pills for each selection
        for key, values in filters.items():
            if values:  # Only if there are selected values
                for value in values:
                    pill = self._create_pill(key, value)
                    self.pills_layout.insertWidget(
                        self.pills_layout.count() - 1, pill)

    def _create_pill(self, key: str, value: str) -> QWidget:
        """Create a filter pill widget

        Args:
            key: Filter key (e.g., 'project')
            value: Filter value (e.g., 'Gamma')

        Returns:
            Pill widget with label and remove button
        """
        container = QWidget()
        container.setObjectName("pillContainer")
        container.setStyleSheet("""
            QWidget#pillContainer {
                background-color: rgba(79, 195, 247, 0.15);
                border: 1px solid rgba(79, 195, 247, 0.3);
                border-radius: 14px;
                padding: 4px 8px;
            }
        """)
        container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(container)
        layout.setContentsMargins(6, 2, 4, 2)
        layout.setSpacing(6)

        # Filter label
        label = QLabel(f"{key.replace('_', ' ').title()}: {value}")
        label.setStyleSheet("""
            QLabel {
                color: #90caf9;
                font-size: 9pt;
                background: transparent;
                border: none;
                padding: 0;
            }
        """)
        layout.addWidget(label)

        # Remove button with SVG icon
        icon_path = Path(__file__).parent / \
            "close_small_28dp_E3E3E3_FILL0_wght200_GRAD0_opsz24.svg"
        with open(icon_path, 'rb') as f:
            close_data = QByteArray(f.read())

        close_icon = QSvgWidget()
        close_icon.load(close_data)
        close_icon.setFixedSize(14, 14)
        close_icon.setCursor(Qt.CursorShape.PointingHandCursor)
        close_icon.setStyleSheet("""
            QSvgWidget:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 7px;
            }
        """)

        # Make icon clickable
        close_icon.mousePressEvent = lambda e: self.filter_removed.emit(
            key, value)
        layout.addWidget(close_icon)

        return container

    def show_clear_all_filters(self):
        """Show the clear all filters button"""
        self.clear_all_btn.show()

    def hide_clear_all_filters(self):
        """Hide the clear all filters button"""
        self.clear_all_btn.hide()
