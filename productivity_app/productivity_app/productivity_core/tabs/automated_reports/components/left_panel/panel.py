"""
Left Panel - Topic/category navigation

Displays categorized topics with counts in a folder-tree structure.
"""
from typing import List, Tuple, Optional, Dict
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal
from .topic_group import TopicGroup
from .topic_item import TopicItem
from .all_reports_item import AllReportsItem
from .debug_widget import DebugWidget


class LeftPanel(QFrame):
    """Left navigation panel with expandable topic categories"""

    # Signals
    topic_selected = Signal(str)  # Emits topic name when selected
    show_count_requested = Signal(int, int)  # Debug: show count
    hide_count_requested = Signal()  # Debug: hide count
    debug_topic_selected = Signal(str)  # Debug: topic selected from debug menu

    def __init__(self, parent: Optional[QWidget] = None, debug_mode: bool = False):
        """Initialize left panel

        Args:
            parent: Parent widget
            debug_mode: Enable debug widget
        """
        super().__init__(parent)
        self.debug_mode = debug_mode
        # Special all reports item
        self.all_reports_item: Optional[AllReportsItem] = None
        # Map group name to widget
        self.topic_groups: Dict[str, TopicGroup] = {}
        self.topic_items: Dict[str, TopicItem] = {}  # Map item name to widget
        # Map parent to children
        self.child_items: Dict[str, List[TopicItem]] = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup the panel UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-right: 1px solid #3a3a3a;
            }
        """)
        # Calculate minimum width to fit "Project Management12345"
        # Approximate: 10 (margin) + 16 (arrow) + 8 (space) + 20 (icon) + 8 (space)
        #              + 180 (text ~18 chars) + 40 (count) + 10 (margin) = 292px minimum
        self.setMinimumWidth(280)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 15, 5, 15)
        self.main_layout.setSpacing(2)

        # Header
        header = QLabel("Topics")
        header.setStyleSheet("""
            font-size: 11pt;
            font-weight: bold;
            color: #ffffff;
            padding: 5px;
        """)
        self.main_layout.addWidget(header)

        # Build topic hierarchy
        self._build_topic_tree()

        self.main_layout.addStretch()

        # Debug widget at bottom if debug_mode
        if self.debug_mode:
            # Get all available topic names
            available_topics = self._get_all_topic_names()
            self.debug_widget = DebugWidget(available_topics=available_topics)
            self.debug_widget.show_count_requested.connect(
                self.show_count_requested.emit)
            self.debug_widget.hide_count_requested.connect(
                self.hide_count_requested.emit)
            self.debug_widget.topic_selected.connect(
                self._on_debug_topic_selected)
            self.main_layout.addWidget(self.debug_widget)

    def _get_topic_hierarchy(self) -> List[Tuple[str, int, Optional[List[Tuple[str, int]]]]]:
        """Get hierarchical topic structure

        Returns:
            List of (topic_name, count, optional_children)
            where children is a list of (child_name, child_count)
        """
        return [
            ("All Reports", 10, None),
            ("Project Management", 6, [
                ("Gamma", 3),
                ("Alpha", 2),
                ("Beta", 1)
            ]),
            ("Team & Resources", 6, [
                ("Team Velocity", 3),
                ("Resource Allocation", 3)
            ]),
            ("Financial", 3, [
                ("Budget Reports", 2),
                ("Cost Analysis", 1)
            ]),
        ]

    def _build_topic_tree(self):
        """Build the topic tree with groups and items"""
        hierarchy = self._get_topic_hierarchy()

        for topic_name, count, children in hierarchy:

            if topic_name == "All Reports":
                # Special case: All Reports gets its own widget
                self.all_reports_item = AllReportsItem(count)
                self.all_reports_item.clicked.connect(self._on_topic_clicked)
                self.main_layout.addWidget(self.all_reports_item)
            elif children:
                # Create TopicGroup for parents with children
                group = TopicGroup(topic_name, count)
                group.clicked.connect(self._on_topic_clicked)
                group.expand_toggled.connect(self._on_expand_toggled)

                self.topic_groups[topic_name] = group
                self.main_layout.addWidget(group)

                # Create TopicItem widgets for children
                child_widgets = []
                for child_name, child_count in children:
                    child_item = TopicItem(child_name, child_count)
                    child_item.clicked.connect(self._on_topic_clicked)
                    child_item.hide()  # Initially hidden
                    child_widgets.append(child_item)
                    self.topic_items[child_name] = child_item
                    self.main_layout.addWidget(child_item)

                self.child_items[topic_name] = child_widgets
            else:
                # Create TopicItem for standalone topics (no children)
                item = TopicItem(topic_name, count)
                item.clicked.connect(self._on_topic_clicked)
                self.topic_items[topic_name] = item
                self.main_layout.addWidget(item)

    def _on_topic_clicked(self, topic_name: str):
        """Handle topic item click

        Args:
            topic_name: Name of clicked topic
        """
        self.topic_selected.emit(topic_name)

    def _on_expand_toggled(self, topic_name: str, expanded: bool):
        """Handle expand/collapse toggle

        Args:
            topic_name: Name of parent topic
            expanded: Whether expanded or collapsed
        """
        if topic_name in self.child_items:
            for child in self.child_items[topic_name]:
                child.setVisible(expanded)

    def _on_debug_topic_selected(self, topic_name: str):
        """Handle topic selection from debug menu

        Args:
            topic_name: Name of topic to select
        """
        # Select the topic item
        if topic_name in self.topic_items:
            self.topic_items[topic_name].select()
        elif self.all_reports_item and topic_name == "All Reports":
            # For All Reports, just emit the signal
            pass

        # Emit both signals
        self.debug_topic_selected.emit(topic_name)
        self.topic_selected.emit(topic_name)

    def _get_all_topic_names(self) -> list:
        """Get all available topic names

        Returns:
            List of all topic names (groups and items)
        """
        topics = []

        # Add All Reports
        if self.all_reports_item:
            topics.append("All Reports")

        # Add all group names
        topics.extend(self.topic_groups.keys())

        # Add all individual items
        topics.extend(self.topic_items.keys())

        return sorted(topics)

    def update_topic_counts(self, topic_counts: dict):
        """Update the count badges on topic groups and items

        Args:
            topic_counts: Dict mapping topic names to counts
        """
        for topic_name, count in topic_counts.items():
            if topic_name == "All Reports" and self.all_reports_item:
                self.all_reports_item.update_count(count)
            elif topic_name in self.topic_groups:
                self.topic_groups[topic_name].update_count(count)
            elif topic_name in self.topic_items:
                self.topic_items[topic_name].update_count(count)
