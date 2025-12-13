"""
Active Filter Pills - Display active filters as removable pills

Shows currently active filters with X buttons to remove them.
"""
from typing import Optional, Dict
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal


class ActiveFilterPills(QWidget):
    """Display active filters as pills with remove buttons"""

    # Signals
    filter_removed = Signal(str)  # Emits filter key to remove

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize active filter pills"""
        super().__init__(parent)
        self._setup_ui()
        self.hide()  # Hidden by default when no filters

    def _setup_ui(self):
        """Setup pills UI"""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)
        self.layout.setSpacing(8)
        self.layout.addStretch()

    def update_filters(self, filters: Dict[str, str]):
        """Update displayed filter pills

        Args:
            filters: Dict of active filters {key: value}
        """
        # Clear existing pills
        while self.layout.count() > 1:  # Keep the stretch
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new pills
        active_filters = {k: v for k, v in filters.items() if v}

        if not active_filters:
            self.hide()
            return

        self.show()

        for key, value in active_filters.items():
            pill = self._create_pill(key, value)
            self.layout.insertWidget(self.layout.count() - 1, pill)

    def _create_pill(self, key: str, value: str) -> QWidget:
        """Create a filter pill widget

        Args:
            key: Filter key (e.g., 'project')
            value: Filter value (e.g., 'Gamma')

        Returns:
            Pill widget with label and remove button
        """
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(79, 195, 247, 0.15);
                border: 1px solid rgba(79, 195, 247, 0.3);
                border-radius: 12px;
                padding: 4px 8px;
            }
        """)

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

        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #90caf9;
                font-size: 12pt;
                font-weight: bold;
                padding: 0;
                width: 16px;
                height: 16px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(lambda: self.filter_removed.emit(key))
        layout.addWidget(remove_btn)

        return container
