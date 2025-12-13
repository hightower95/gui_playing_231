"""
Left Panel - Topic/category navigation

Displays categorized topics with counts for filtering reports.
"""
from typing import List, Tuple, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal


class LeftPanel(QFrame):
    """Left navigation panel with topic categories"""

    # Signals
    topic_selected = Signal(str)  # Emits topic name when selected

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize left panel"""
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the panel UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-right: 1px solid #3a3a3a;
            }
        """)
        self.setMinimumWidth(150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 15)
        layout.setSpacing(5)

        # Header
        header = QLabel("Topics")
        header.setStyleSheet("""
            font-size: 11pt;
            font-weight: bold;
            color: #ffffff;
            padding: 5px;
        """)
        layout.addWidget(header)

        # Topic buttons
        self.topics = self._get_topics()
        self.topic_buttons = []

        for topic, count in self.topics:
            btn = self._create_topic_button(topic, count)
            self.topic_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

    def _get_topics(self) -> List[Tuple[str, int]]:
        """Get list of topics with counts"""
        return [
            ("All Reports", 10),
            ("Project Management", 6),
            ("Team & Resources", 6),
            ("Financial", 3),
            ("Quality & Testing", 3),
            ("Customer", 2),
            ("Technical", 2)
        ]

    def _create_topic_button(self, text: str, count: int) -> QPushButton:
        """Create a topic navigation button

        Args:
            text: Topic name
            count: Number of reports in topic

        Returns:
            Configured QPushButton
        """
        btn = QPushButton(f"  {text}    {count}")
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 10px;
                border: none;
                border-radius: 4px;
                background-color: transparent;
                color: #b0b0b0;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #353535;
            }
        """)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.topic_selected.emit(text))

        return btn

    def update_topic_counts(self, topic_counts: dict):
        """Update the count badges on topic buttons

        Args:
            topic_counts: Dict mapping topic names to counts
        """
        for i, (topic, _) in enumerate(self.topics):
            if topic in topic_counts and i < len(self.topic_buttons):
                count = topic_counts[topic]
                self.topic_buttons[i].setText(f"  {topic}    {count}")
