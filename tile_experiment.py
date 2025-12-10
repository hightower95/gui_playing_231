"""
Experiment with tile-based layout using pure Qt widgets
"""
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFrame, QScrollArea, QGridLayout, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class TileExperiment(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tile Layout Experiment")
        self.setGeometry(100, 100, 1000, 700)

        central = QWidget()
        self.setCentralWidget(central)
        central.setStyleSheet("background-color: #1e1e1e;")
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 20, 0, 20)

        # Title
        title = QLabel("Engineering Productivity Toolkit")
        title.setStyleSheet(
            "font-size: 14pt; font-weight: bold; color: #4fc3f7; padding: 10px;")
        title.setFrameStyle(0)
        layout.addWidget(title)

        # Scroll area for tiles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                border-top: 1px solid #363535;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3a3a3a;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a4a4a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        # Container widget for tiles
        tiles_container = QWidget()
        tiles_container.setStyleSheet("background-color: transparent;")
        scroll.setWidget(tiles_container)

        # Grid layout for tiles (3 columns)
        tiles_layout = QGridLayout(tiles_container)
        tiles_layout.setSpacing(12)
        tiles_layout.setContentsMargins(40, 10, 40, 0)

        # Create 12 tiles
        tiles_data = [
            ("🔌 Connector Search", "Search for connectors",
             ["Quick search by name or part number", "Filter by connector type", "View detailed pinout diagrams"], True),
            ("⚡ EPD Browser", "Browse engineering product data",
             ["Search EPD database", "Compare product versions", "Export technical specifications"], True),
            ("📄 Document Scanner", "Scan and search documents",
             ["Register document sources", "Quick text search across files", "View document history"], False),
            ("⚙️ Settings", "Configure application behavior",
             ["Toggle tab visibility", "Configure sub-tab displays", "Enable/disable feature flags"], True),
            ("🔍 Fault Finding", "Diagnostic tools and workflows",
             ["Guided fault finding procedures", "Common issue reference", "Diagnostic flowcharts"], True),
            ("📚 Remote Docs", "Remote documentation access",
             ["Search remote document stores", "Upload and sync documents", "Offline caching"], True),
            ("🚀 DevOps", "Development operations integration",
             ["Azure DevOps integration", "Work item tracking", "Build and release monitoring"], True),
            ("📊 Reports", "Generate and view reports",
             ["Create custom reports", "Export to PDF or Excel", "Schedule automated reports"], True),
            ("🔧 Tools", "Utility tools collection",
             ["Unit converters", "Calculators", "Quick reference guides"], True),
            ("📈 Analytics", "Data analysis and visualization",
             ["View usage statistics", "Performance metrics", "Trend analysis"], False),
            ("💾 Backup", "Backup and restore data",
             ["Automatic backups", "Manual backup creation", "Restore from backup"], True),
            ("🌐 Network", "Network diagnostics and tools",
             ["Ping and trace routes", "Port scanning", "Connection monitoring"], True),
        ]

        # Add tiles to grid (3 columns)
        for idx, (title, subtitle, bullets, is_visible) in enumerate(tiles_data):
            row = idx // 3
            col = idx % 3
            tile = self._create_tile(title, subtitle, bullets, is_visible)
            tiles_layout.addWidget(tile, row, col)

        layout.addWidget(scroll)

        # Version subtitle (at bottom)
        version = QLabel("Version 1.2.3")
        version.setStyleSheet(
            "font-size: 9pt; color: #909090; padding: 10px;")
        version.setFrameStyle(0)
        layout.addWidget(version)

    def _create_shadow(self, hover=False):
        """Create a subtle shadow effect for tiles"""
        shadow = QGraphicsDropShadowEffect()
        if hover:
            shadow.setBlurRadius(40)
            shadow.setXOffset(0)
            shadow.setYOffset(10)
            shadow.setColor(QColor(0, 0, 0, 120))
        else:
            shadow.setBlurRadius(25)
            shadow.setXOffset(0)
            shadow.setYOffset(6)
            shadow.setColor(QColor(0, 0, 0, 100))
        return shadow

    class TileFrame(QFrame):
        """Custom frame with hover animations"""

        def __init__(self, parent_window, parent=None):
            super().__init__(parent)
            self.parent_window = parent_window
            self._base_margins = None

        def enterEvent(self, event):
            """Handle mouse enter - elevate tile"""
            self.setStyleSheet("""
                background-color: #353535;
                border: 1px solid #3a3a3a;
                border-radius: 16px;
            """)
            self.setGraphicsEffect(
                self.parent_window._create_shadow(hover=True))
            # Use negative top margin to create upward movement
            if self._base_margins is None:
                layout = self.layout()
                if layout:
                    self._base_margins = layout.contentsMargins()
            if self._base_margins:
                self.layout().setContentsMargins(
                    self._base_margins.left(),
                    self._base_margins.top() - 4,
                    self._base_margins.right(),
                    self._base_margins.bottom() + 4
                )
            super().enterEvent(event)

        def leaveEvent(self, event):
            """Handle mouse leave - return tile to normal"""
            self.setStyleSheet("""
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 16px;
            """)
            self.setGraphicsEffect(
                self.parent_window._create_shadow(hover=False))
            # Restore original margins
            if self._base_margins:
                self.layout().setContentsMargins(self._base_margins)
            super().leaveEvent(event)

    def _create_tile(self, title: str, subtitle: str, bullets: list, is_visible: bool = True) -> QFrame:
        """Create a single tile widget"""
        tile = self.TileFrame(self)
        tile.setStyleSheet("""
            background-color: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 16px;
        """)
        tile.setGraphicsEffect(self._create_shadow())
        tile.setMinimumHeight(176)
        tile.setMaximumHeight(208)

        layout = QVBoxLayout(tile)
        layout.setSpacing(10)
        layout.setContentsMargins(18, 18, 18, 18)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 15pt; font-weight: bold; color: #FFFFFF; border: none; background-color: transparent;")
        title_label.setFrameStyle(0)
        print(f"Created title label: {title}")
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(
            "color: #b0b0b0; font-size: 10pt; border: none; background-color: transparent; margin-top: 2px;")
        subtitle_label.setWordWrap(True)
        subtitle_label.setFrameStyle(0)
        print(f"Created subtitle label: {subtitle}")
        layout.addWidget(subtitle_label)

        # Bullet points
        for bullet in bullets:
            bullet_label = QLabel(f"• {bullet}")
            bullet_label.setStyleSheet(
                "color: #c0c0c0; font-size: 9pt; border: none; background-color: transparent; padding-left: 2px;")
            bullet_label.setWordWrap(True)
            bullet_label.setFrameStyle(0)
            print(f"Created bullet: {bullet}")
            layout.addWidget(bullet_label)

        layout.addStretch()

        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        button_layout.addStretch()

        # Go To button
        goto_btn = QPushButton("Go To")
        goto_btn.setEnabled(is_visible)
        goto_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 181, 246, 0.1);
                color: #64b5f6;
                border: 1px solid rgba(100, 181, 246, 0.2);
                border-radius: 6px;
                text-align: center;
                padding: 6px 12px;
                font-size: 9pt;
            }
            QPushButton:hover:enabled {
                background-color: rgba(100, 181, 246, 0.2);
                color: #90caf9;
                border-color: rgba(144, 202, 249, 0.3);
            }
            QPushButton:disabled {
                background-color: rgba(80, 80, 80, 0.1);
                color: #505050;
                border-color: rgba(80, 80, 80, 0.2);
            }
        """)
        goto_btn.setCursor(
            Qt.CursorShape.PointingHandCursor if is_visible else Qt.CursorShape.ArrowCursor)
        goto_btn.clicked.connect(lambda: print(f"Go to: {title}"))
        button_layout.addWidget(goto_btn)

        button_layout.addSpacing(8)

        # User Guide button
        guide_btn = QPushButton("User Guide")
        guide_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(100, 181, 246, 0.1);
                color: #64b5f6;
                border: 1px solid rgba(100, 181, 246, 0.2);
                border-radius: 6px;
                text-align: center;
                padding: 6px 12px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: rgba(100, 181, 246, 0.2);
                color: #90caf9;
                border-color: rgba(144, 202, 249, 0.3);
            }
        """)
        guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        guide_btn.clicked.connect(lambda: print(f"User guide: {title}"))
        button_layout.addWidget(guide_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)
        return tile


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TileExperiment()
    window.show()
    sys.exit(app.exec())
