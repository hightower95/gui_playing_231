"""
Start Page Tab - Welcome page with app overview shown on each startup
"""
from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                               QScrollArea, QGridLayout, QPushButton, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from ..core.app_context import AppContext
from ..core.config_manager import AppSettingsConfig


class StartPageTab(QWidget):
    """Start page tab shown on application startup"""

    TAB_TITLE = "🏠 Start Page"
    MODULE_ID = 'start_page'
    CONFIG_KEY = 'start_page_closed'

    def __init__(self, services: Optional[AppContext] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.services = services
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI with tile-based layout"""
        self.setStyleSheet("background-color: #1e1e1e;")
        layout = QVBoxLayout(self)
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

        # Create tiles with real tab data
        tiles_data = self._get_tiles_data()

        # Add tiles to grid (3 columns)
        for idx, (title_text, subtitle, bullets, tab_id, is_visible) in enumerate(tiles_data):
            row = idx // 3
            col = idx % 3
            tile = self._create_tile(title_text, subtitle, bullets, tab_id, is_visible)
            tiles_layout.addWidget(tile, row, col)

        layout.addWidget(scroll)

        # Version subtitle (at bottom)
        version = QLabel("Version 1.2.3")
        version.setStyleSheet(
            "font-size: 9pt; color: #909090; padding: 10px;")
        version.setFrameStyle(0)
        layout.addWidget(version)

    def _get_tiles_data(self):
        """Get tile data for all tabs"""
        # TODO: Dynamically load from TAB_CONFIG
        return [
            ("🔌 Connector Search", "Search for connectors",
             ["Quick search by name or part number", "Filter by connector type", "View detailed pinout diagrams"], 
             "connectors", True),
            ("⚡ EPD Browser", "Browse engineering product data",
             ["Search EPD database", "Compare product versions", "Export technical specifications"], 
             "epd", True),
            ("📄 Document Scanner", "Scan and search documents",
             ["Register document sources", "Quick text search across files", "View document history"], 
             "document_scanner", True),
            ("⚙️ Settings", "Configure application behavior",
             ["Toggle tab visibility", "Configure sub-tab displays", "Enable/disable feature flags"], 
             "settings", True),
            ("🔍 Fault Finding", "Diagnostic tools and workflows",
             ["Guided fault finding procedures", "Common issue reference", "Diagnostic flowcharts"], 
             "fault_finding", True),
            ("📚 Remote Docs", "Remote documentation access",
             ["Search remote document stores", "Upload and sync documents", "Offline caching"], 
             "remote_docs", True),
            ("🚀 DevOps", "Development operations integration",
             ["Azure DevOps integration", "Work item tracking", "Build and release monitoring"], 
             "devops", True),
            ("📊 Reports", "Generate and view reports",
             ["Create custom reports", "Export to PDF or Excel", "Schedule automated reports"], 
             "reports", False),
            ("🔧 Tools", "Utility tools collection",
             ["Unit converters", "Calculators", "Quick reference guides"], 
             "tools", False),
            ("📈 Analytics", "Data analysis and visualization",
             ["View usage statistics", "Performance metrics", "Trend analysis"], 
             "analytics", False),
            ("💾 Backup", "Backup and restore data",
             ["Automatic backups", "Manual backup creation", "Restore from backup"], 
             "backup", False),
            ("🌐 Network", "Network diagnostics and tools",
             ["Ping and trace routes", "Port scanning", "Connection monitoring"], 
             "network", False),
        ]

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

    def _create_tile(self, title: str, subtitle: str, bullets: list, tab_id: str, is_visible: bool = True) -> QFrame:
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
        layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(
            "color: #b0b0b0; font-size: 10pt; border: none; background-color: transparent; margin-top: 2px;")
        subtitle_label.setWordWrap(True)
        subtitle_label.setFrameStyle(0)
        layout.addWidget(subtitle_label)

        # Bullet points
        for bullet in bullets:
            bullet_label = QLabel(f"• {bullet}")
            bullet_label.setStyleSheet(
                "color: #c0c0c0; font-size: 9pt; border: none; background-color: transparent; padding-left: 2px;")
            bullet_label.setWordWrap(True)
            bullet_label.setFrameStyle(0)
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
        goto_btn.clicked.connect(lambda: self._navigate_to_tab(tab_id))
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
        guide_btn.clicked.connect(lambda: print(f"User guide for: {tab_id}"))
        button_layout.addWidget(guide_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)
        return tile

    def _navigate_to_tab(self, tab_id: str):
        """Navigate to a specific tab using tab_visibility_service
        
        Args:
            tab_id: The ID of the tab to navigate to
        """
        if not self.services:
            print(f"[StartPageTab] Cannot navigate - no services available")
            return
            
        tab_visibility_service = self.services.get('tab_visibility')
        if tab_visibility_service:
            # Ensure tab is visible
            if not tab_visibility_service.is_tab_visible(tab_id):
                tab_visibility_service.set_tab_as_visible(tab_id)
            # Switch focus to it
            tab_visibility_service.set_focus(tab_id)
            print(f"[StartPageTab] Navigated to {tab_id} tab")
        else:
            print(f"[StartPageTab] tab_visibility_service not available")

    def _get_content_html(self) -> str:
        """Get the HTML content for the start page"""
        return """
        <html>
        <head>
            <style>
                body {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 10pt;
                    line-height: 1.3;
                    color: #e0e0e0;
                    background-color: #1e1e1e;
                    margin: 0;
                    padding: 15px;
                }
                h1 {
                    color: #ffffff;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 8px;
                    margin-top: 0;
                    margin-bottom: 20px;
                    font-size: 16pt;
                }
                table {
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 0;
                }
                td {
                    width: 33.33%;
                    padding: 12px;
                    vertical-align: top;
                }
                .tile {
                    background-color: #2a2a2a;
                    border-radius: 12px;
                    padding: 15px;
                    border: 1px solid #3a3a3a;
                    height: 160px;
                    display: block;
                }
                .tile:hover {
                    background-color: #353535;
                    border-color: #4a4a4a;
                }
                .tab-name {
                    font-weight: bold;
                    color: #4fc3f7;
                    font-size: 12pt;
                    margin-bottom: 4px;
                }
                .tab-subtitle {
                    color: #b0b0b0;
                    font-size: 9pt;
                    margin-bottom: 8px;
                }
                ul {
                    margin: 0 0 8px 0;
                    padding-left: 18px;
                    color: #d0d0d0;
                }
                li {
                    margin: 3px 0;
                    font-size: 9pt;
                }
                .links {
                    margin-top: 8px;
                    padding-top: 8px;
                    font-size: 9pt;
                    border-top: 1px solid #3a3a3a;
                }
                .links a {
                    color: #64b5f6;
                    text-decoration: none;
                    margin-right: 12px;
                }
                .links a:hover {
                    color: #90caf9;
                    text-decoration: underline;
                }
                .footer {
                    margin-top: 10px;
                    padding-top: 10px;
                    border-top: 1px solid #3a3a3a;
                    color: #909090;
                    font-size: 9pt;
                    font-style: italic;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <h1>Welcome to Engineering Productivity Toolkit</h1>
            
            <table>
                <tr>
                    <td>
                        <div class="tile">
                            <div class="tab-name">⚙️ Settings</div>
                            <div class="tab-subtitle">Configure application behavior</div>
                            <ul>
                                <li>Toggle tab visibility</li>
                                <li>Configure sub-tab displays</li>
                                <li>Enable/disable feature flags</li>
                            </ul>
                            <div class="links">
                                <a href="#settings">Go To</a> | <a href="#settings-guide">User Guide</a>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="tile">
                            <div class="tab-name">🔌 Connectors</div>
                            <div class="tab-subtitle">Manage and search connectors</div>
                            <ul>
                                <li>View connector pinouts</li>
                                <li>Search by type or wire color</li>
                                <li>Generate breakout diagrams</li>
                            </ul>
                            <div class="links">
                                <a href="#connectors">Go To</a> | <a href="#connectors-guide">User Guide</a>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="tile">
                            <div class="tab-name">⚡ EPD Tool</div>
                            <div class="tab-subtitle">Engineering Product Data management</div>
                            <ul>
                                <li>Browse and filter EPD entries</li>
                                <li>Compare versions and changes</li>
                                <li>Export data for reports</li>
                            </ul>
                            <div class="links">
                                <a href="#epd">Go To</a> | <a href="#epd-guide">User Guide</a>
                            </div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <div class="tile">
                            <div class="tab-name">📄 Document Scanner</div>
                            <div class="tab-subtitle">Search across documents</div>
                            <ul>
                                <li>Quick search registered docs</li>
                                <li>Configure document sources</li>
                                <li>View history and compare</li>
                            </ul>
                            <div class="links">
                                <a href="#document_scanner">Go To</a> | <a href="#docs-guide">User Guide</a>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="tile">
                            <div class="tab-name">🔍 Fault Finding</div>
                            <div class="tab-subtitle">Diagnostic tools and workflows</div>
                            <ul>
                                <li>Guided fault finding procedures</li>
                                <li>Common issue reference</li>
                                <li>Diagnostic flowcharts</li>
                            </ul>
                            <div class="links">
                                <a href="#fault_finding">Go To</a> | <a href="#fault-guide">User Guide</a>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="tile">
                            <div class="tab-name">📚 Remote Docs</div>
                            <div class="tab-subtitle">Remote documentation access</div>
                            <ul>
                                <li>Search remote document stores</li>
                                <li>Upload and sync documents</li>
                                <li>Offline caching</li>
                            </ul>
                            <div class="links">
                                <a href="#remote_docs">Go To</a> | <a href="#remote-guide">User Guide</a>
                            </div>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        <div class="tile">
                            <div class="tab-name">🚀 DevOps</div>
                            <div class="tab-subtitle">Development operations integration</div>
                            <ul>
                                <li>Azure DevOps integration</li>
                                <li>Work item tracking</li>
                                <li>Build and release monitoring</li>
                            </ul>
                            <div class="links">
                                <a href="#devops">Go To</a> | <a href="#devops-guide">User Guide</a>
                            </div>
                        </div>
                    </td>
                    <td></td>
                    <td></td>
                </tr>
            </table>
            
            <div class="footer">
                Tip: Click "Close" below to hide this start page until the next time you run the application.
            </div>
        </body>
        </html>
        """

    def _on_close_clicked(self):
        """Handle close button clicked - hide tab until next run"""
        # Mark as closed for this session
        AppSettingsConfig.set_setting(self.CONFIG_KEY, True)

        # Hide the tab using TabVisibilityService
        if self.services:
            tab_visibility_service = self.services.get('tab_visibility')
            if tab_visibility_service:
                # Don't persist - we want it visible again on next run
                tab_visibility_service.set_tab_as_hidden(
                    self.MODULE_ID, persist=False)

        print(f"[StartPageTab] Closed for this session")

    @staticmethod
    def should_show_on_startup() -> bool:
        """Check if start page should be shown on startup

        Returns:
            True if should be shown, False if user closed it this session
        """
        return not AppSettingsConfig.get_setting(StartPageTab.CONFIG_KEY, False)
