"""
Experiment with tile-based layout using pure Qt widgets
"""
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt


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
        
        # Version subtitle
        version = QLabel("Version 1.2.3")
        version.setStyleSheet(
            "font-size: 9pt; color: #909090; padding: 0px 10px 10px 10px;")
        version.setFrameStyle(0)
        layout.addWidget(version)

        # Horizontal layout for tiles
        tiles_layout = QHBoxLayout()
        tiles_layout.setSpacing(12)
        tiles_layout.setContentsMargins(40, 0, 40, 0)

        # Create 3 tiles with different visibility states
        tile1 = self._create_tile(
            "🔌 Connector Search",
            "Search for connectors",
            ["Quick search by name or part number",
                "Filter by connector type", "View detailed pinout diagrams"],
            is_visible=True
        )
        tiles_layout.addWidget(tile1)

        tile2 = self._create_tile(
            "⚡ EPD Browser",
            "Browse engineering product data",
            ["Search EPD database", "Compare product versions",
                "Export technical specifications"],
            is_visible=True
        )
        tiles_layout.addWidget(tile2)

        tile3 = self._create_tile(
            "📄 Document Scanner",
            "Scan and search documents",
            ["Register document sources",
                "Quick text search across files", "View document history"],
            is_visible=False  # Example of disabled tab
        )
        tiles_layout.addWidget(tile3)

        layout.addLayout(tiles_layout)
        layout.addStretch()

    def _create_tile(self, title: str, subtitle: str, bullets: list, is_visible: bool = True) -> QFrame:
        """Create a single tile widget"""
        tile = QFrame()
        tile.setStyleSheet("""
            background-color: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 12px;
        """)
        tile.setMinimumHeight(176)
        tile.setMaximumHeight(208)

        layout = QVBoxLayout(tile)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; color: #FFFFFF; border: none;")
        title_label.setFrameStyle(0)
        print(f"Created title label: {title}")
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #FFFFFF; font-size: 10pt; border: none;")
        subtitle_label.setWordWrap(True)
        subtitle_label.setFrameStyle(0)
        print(f"Created subtitle label: {subtitle}")
        layout.addWidget(subtitle_label)

        # Bullet points
        for bullet in bullets:
            bullet_label = QLabel(f"• {bullet}")
            bullet_label.setStyleSheet("color: #FFFFFF; font-size: 10pt; border: none;")
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
                background-color: transparent;
                color: #64b5f6;
                border: none;
                text-align: center;
                padding: 4px;
                font-size: 9pt;
            }
            QPushButton:hover:enabled {
                color: #90caf9;
                text-decoration: underline;
            }
            QPushButton:disabled {
                color: #505050;
            }
        """)
        goto_btn.setCursor(
            Qt.CursorShape.PointingHandCursor if is_visible else Qt.CursorShape.ArrowCursor)
        goto_btn.clicked.connect(lambda: print(f"Go to: {title}"))
        button_layout.addWidget(goto_btn)

        # Separator
        sep1 = QLabel("|")
        sep1.setStyleSheet(
            "color: #3a3a3a; background-color: transparent; border: none;")
        sep1.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        button_layout.addWidget(sep1)

        # User Guide button
        guide_btn = QPushButton("User Guide")
        guide_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64b5f6 ;
                border: none;
                text-align: center;
                padding: 4px;
                font-size: 9pt;
            }
            QPushButton:hover {
                color: #90caf9;
                text-decoration: underline;
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
