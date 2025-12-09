"""
Start Page Tab - Welcome page with app overview shown on each startup
"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QPushButton
from PySide6.QtCore import Qt, QUrl
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
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Text browser with HTML content
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)  # Handle links ourselves
        self.text_browser.anchorClicked.connect(self._on_link_clicked)
        self.text_browser.setHtml(self._get_content_html())
        layout.addWidget(self.text_browser)

        # Close button
        close_button = QPushButton("Close (hide until next run)")
        close_button.clicked.connect(self._on_close_clicked)
        close_button.setMaximumWidth(250)
        layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)

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

    def _on_link_clicked(self, url: QUrl):
        """Handle link clicks - navigate to tabs or open guides

        Args:
            url: The URL that was clicked
        """
        url_str = url.toString()

        # Handle "Go To" links (navigate to tab)
        if url_str.startswith('#') and not url_str.endswith('-guide'):
            tab_id = url_str[1:]  # Remove the #

            # Use TabVisibilityService to switch tabs
            if self.services:
                tab_visibility_service = self.services.get('tab_visibility')
                if tab_visibility_service:
                    # Ensure tab is visible
                    tab_visibility_service.set_tab_as_visible(tab_id)
                    # Switch focus to it
                    tab_visibility_service.set_focus(tab_id)
                    print(f"[StartPageTab] Navigated to {tab_id} tab")

        # Handle "User Guide" links (placeholder for now)
        elif url_str.endswith('-guide'):
            print(f"[StartPageTab] User guide link clicked: {url_str}")
            # TODO: Open help documentation when available

    @staticmethod
    def should_show_on_startup() -> bool:
        """Check if start page should be shown on startup

        Returns:
            True if should be shown, False if user closed it this session
        """
        return not AppSettingsConfig.get_setting(StartPageTab.CONFIG_KEY, False)
