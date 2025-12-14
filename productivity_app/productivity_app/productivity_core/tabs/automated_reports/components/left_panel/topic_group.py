"""Topic group widget - expandable folder items for left panel"""
from typing import Optional
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtCore import Qt, Signal, QByteArray


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

        # Get icon directory
        icon_dir = Path(__file__).parent

        # Cache SVG data for performance
        self.arrow_collapsed_path = icon_dir / \
            "arrow_forward_ios_22dp_E3E3E3_FILL0_wght100_GRAD200_opsz24.svg"
        self.arrow_expanded_path = icon_dir / \
            "keyboard_arrow_down_22dp_E3E3E3_FILL0_wght100_GRAD200_opsz24.svg"  # Same for now, will rotate
        self.closed_icon_path = icon_dir / \
            "folder_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"
        self.open_icon_path = icon_dir / \
            "folder_open_24dp_E3E3E3_FILL0_wght400_GRAD0_opsz24.svg"

        # Read and cache SVG data
        with open(self.arrow_collapsed_path, 'rb') as f:
            self.arrow_collapsed_data = QByteArray(f.read())
        with open(self.arrow_expanded_path, 'rb') as f:
            self.arrow_expanded_data = QByteArray(f.read())
        with open(self.closed_icon_path, 'rb') as f:
            self.folder_closed_data = QByteArray(f.read())
        with open(self.open_icon_path, 'rb') as f:
            self.folder_open_data = QByteArray(f.read())

        # Expand/collapse arrow (SVG)
        self.arrow_label = QSvgWidget()
        self.arrow_label.setFixedSize(16, 16)
        self.arrow_label.load(self.arrow_collapsed_data)
        layout.addWidget(self.arrow_label)

        # Folder icon (SVG)
        self.folder_icon = QSvgWidget()
        self.folder_icon.setFixedSize(20, 20)
        self.folder_icon.load(self.folder_closed_data)
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
        """Update expand arrow and folder icon using cached SVG data"""
        # Swap arrow icon (for now using same icon, could add rotation transform)
        # TODO: Add rotated version for expanded

        # Swap folder icon
        if self.is_expanded:
            self.folder_icon.load(self.folder_open_data)
            self.arrow_label.load(self.arrow_expanded_data)
        else:
            self.arrow_label.load(self.arrow_collapsed_data)
            self.folder_icon.load(self.folder_closed_data)

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
        """Handle mouse click - only toggles expansion, doesn't trigger filter"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_expand()
            super().mousePressEvent(event)

    def update_count(self, new_count: int):
        """Update the count display

        Args:
            new_count: New count value
        """
        self.count = new_count
        self.count_label.setText(str(new_count))

    def set_expanded(self):
        """Expand this topic group"""
        if not self.is_expanded:
            self.is_expanded = True
            self._update_expand_button()
            self.expand_toggled.emit(self.topic_name, self.is_expanded)

    def set_not_expanded(self):
        """Collapse this topic group"""
        if self.is_expanded:
            self.is_expanded = False
            self._update_expand_button()
            self.expand_toggled.emit(self.topic_name, self.is_expanded)

    def select(self):
        """Select this group - shows selected state"""
        # TopicGroup doesn't have is_selected state yet, but method exists for API consistency
        # Could be implemented if parent groups can be selected
        pass

    def deselect(self):
        """Deselect this group - returns to normal state"""
        # TopicGroup doesn't have is_selected state yet, but method exists for API consistency
        pass
