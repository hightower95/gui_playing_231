"""Topic group widget - expandable folder items for left panel"""
from typing import Optional
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, Signal


class TopicGroup(QWidget):
    """Expandable topic group (parent folder) with arrow and count"""

    # Signals
    clicked = Signal(str)  # Emits topic name
    expand_toggled = Signal(str, bool)  # Emits topic name and expanded state

    def __init__(
        self,
        topic_name: str,
        count: int = 0,
        parent: Optional[QWidget] = None
    ):
        """Initialize topic group

        Args:
            topic_name: Name of the topic group
            count: Number of items in this group
            parent: Parent widget
        """
        super().__init__(parent)
        self.topic_name = topic_name
        self.count = count
        self.is_expanded = False
        self._setup_ui()

    def _setup_ui(self):
        """Setup the topic group UI"""
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(8)

        # Expand/collapse arrow (visual indicator only)
        self.arrow_label = QLabel("▸")
        self.arrow_label.setFixedSize(16, 16)
        self.arrow_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #b0b0b0;
                font-size: 11pt;
                padding: 0;
            }
        """)
        layout.addWidget(self.arrow_label)

        # Folder icon (SVG)
        icon_dir = Path(__file__).parent
        self.closed_icon_path = icon_dir / \
            "folder_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
        self.open_icon_path = icon_dir / \
            "folder_open_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"

        self.folder_icon = QSvgWidget(str(self.closed_icon_path))
        self.folder_icon.setFixedSize(20, 20)
        layout.addWidget(self.folder_icon)

        # Topic name - prominent typography
        self.name_label = QLabel(self.topic_name)
        self.name_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: #E0E0E0;
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
                color: #909090;
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

    def _toggle_expand(self):
        """Toggle expand/collapse state"""
        self.is_expanded = not self.is_expanded
        self._update_expand_button()
        self.expand_toggled.emit(self.topic_name, self.is_expanded)

    def _update_expand_button(self):
        """Update expand arrow and folder icon"""
        self.arrow_label.setText("▾" if self.is_expanded else "▸")
        # Update folder icon
        icon_path = self.open_icon_path if self.is_expanded else self.closed_icon_path
        self.folder_icon.load(str(icon_path))

    def _update_style(self, hovered: bool):
        """Update widget styling based on hover state

        Args:
            hovered: Whether the widget is being hovered
        """
        if hovered:
            self.setStyleSheet("""
                QWidget {
                    background-color: #2a2a2a;
                    border-radius: 6px;
                }
            """)
            self.name_label.setStyleSheet("""
                QLabel {
                    font-size: 12pt;
                    color: #ffffff;
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
                    font-size: 12pt;
                    color: #E0E0E0;
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
        """Handle mouse click - triggers both expansion and selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_expand()
            self.clicked.emit(self.topic_name)
        super().mousePressEvent(event)

    def update_count(self, new_count: int):
        """Update the count display

        Args:
            new_count: New count value
        """
        self.count = new_count
        self.count_label.setText(str(new_count))

    def set_expanded(self, expanded: bool):
        """Set the expanded state programmatically

        Args:
            expanded: Whether to expand or collapse
        """
        if self.is_expanded != expanded:
            self.is_expanded = expanded
            self._update_expand_button()
