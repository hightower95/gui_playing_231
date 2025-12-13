"""Topic item widget - simple child items for left panel"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal


class TopicItem(QWidget):
    """Simple topic item (child) with label and count - no icon or arrow"""

    # Signals
    clicked = Signal(str)  # Emits topic name

    def __init__(
        self,
        topic_name: str,
        count: int = 0,
        parent: Optional[QWidget] = None
    ):
        """Initialize topic item

        Args:
            topic_name: Name of the topic
            count: Number of items in this topic
            parent: Parent widget
        """
        super().__init__(parent)
        self.topic_name = topic_name
        self.count = count
        self.is_selected = False
        self._setup_ui()

    def _setup_ui(self):
        """Setup the topic item UI"""
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Main layout with left indentation
        layout = QHBoxLayout(self)
        # Indented to align under parent text
        layout.setContentsMargins(34, 2, 10, 2)
        layout.setSpacing(8)

        # Topic name (no icon for child items)
        self.name_label = QLabel(self.topic_name)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #a0a0a0;
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.name_label, stretch=1)

        # Count badge (fixed width for alignment)
        self.count_label = QLabel(str(self.count))
        self.count_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #808080;
                background: transparent;
                border: none;
            }
        """)
        self.count_label.setFixedWidth(40)
        self.count_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.count_label)

        # Initial styling
        self._update_style(False)

    def _update_style(self, hovered: bool = False):
        """Update widget styling based on hover and selected state

        Args:
            hovered: Whether the widget is being hovered
        """
        if self.is_selected:
            # Selected state - distinct visual feedback
            self.setStyleSheet("""
                QWidget {
                    background-color: #4fc3f7;
                    border-radius: 6px;
                }
            """)
            self.name_label.setStyleSheet("""
                QLabel {
                    font-size: 10pt;
                    color: #1e1e1e;
                    background: transparent;
                    border: none;
                    font-weight: bold;
                }
            """)
            self.count_label.setStyleSheet("""
                QLabel {
                    font-size: 9pt;
                    color: #1e1e1e;
                    background: transparent;
                    border: none;
                }
            """)
        elif hovered:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2a2a2a;
                    border-radius: 6px;
                }
            """)
            self.name_label.setStyleSheet("""
                QLabel {
                    font-size: 10pt;
                    color: #e0e0e0;
                    background: transparent;
                    border: none;
                }
            """)
            self.count_label.setStyleSheet("""
                QLabel {
                    font-size: 9pt;
                    color: #b0b0b0;
                    background: transparent;
                    border: none;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border-radius: 6px;
                }
            """)
            self.name_label.setStyleSheet("""
                QLabel {
                    font-size: 10pt;
                    color: #a0a0a0;
                    background: transparent;
                    border: none;
                }
            """)
            self.count_label.setStyleSheet("""
                QLabel {
                    font-size: 9pt;
                    color: #808080;
                    background: transparent;
                    border: none;
                }
            """)

    def enterEvent(self, event):
        """Handle mouse enter"""
        self._update_style(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave"""
        self._update_style(False)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.topic_name)
        super().mousePressEvent(event)

    def update_count(self, new_count: int):
        """Update the count display

        Args:
            new_count: New count value
        """
        self.count = new_count
        self.count_label.setText(str(new_count))

    def select(self):
        """Select this item - shows selected state"""
        self.is_selected = True
        self._update_style()

    def deselect(self):
        """Deselect this item - returns to normal state"""
        self.is_selected = False
        self._update_style()
        self.count_label.setText(str(new_count))
