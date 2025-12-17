"""Shared styles for setup report interstitial components"""

PANEL_STYLE = """
    QWidget {
        background-color: #1e1e1e;
        color: #e3e3e3;
    }
"""

BUTTON_STYLE = """
    QPushButton {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        border-radius: 4px;
        color: #e3e3e3;
        padding: 8px 16px;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #3a3a3a;
        border: 1px solid #4a4a4a;
    }
    QPushButton:pressed {
        background-color: #252525;
    }
"""

PRIMARY_BUTTON_STYLE = """
    QPushButton {
        background-color: #0e639c;
        border: 1px solid #1177bb;
        border-radius: 4px;
        color: white;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1177bb;
    }
    QPushButton:pressed {
        background-color: #0d5a8c;
    }
    QPushButton:disabled {
        background-color: #3a3a3a;
        color: #666666;
        border: 1px solid #444444;
    }
"""

TAB_STYLE = """
    QTabWidget::pane {
        border: 1px solid #3a3a3a;
        background-color: #252525;
        border-radius: 4px;
    }
    QTabBar::tab {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        padding: 8px 16px;
        color: #a3a3a3;
        min-width: 80px;
    }
    QTabBar::tab:selected {
        background-color: #252525;
        color: #e3e3e3;
        border-bottom-color: #252525;
    }
    QTabBar::tab:hover:!selected {
        background-color: #3a3a3a;
    }
"""

SOURCE_BUTTON_SELECTED_STYLE = """
    QPushButton {
        background-color: #e8f0fe;
        border: 2px solid #1a73e8;
        border-radius: 8px;
        color: #1967d2;
        padding: 16px;
        font-size: 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #d2e3fc;
    }
"""

SOURCE_BUTTON_UNSELECTED_STYLE = """
    QPushButton {
        background-color: #2d2d2d;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        color: #a3a3a3;
        padding: 16px;
        font-size: 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #3a3a3a;
    }
"""

DROP_AREA_STYLE = """
    QFrame {
        background-color: transparent;
        border: 2px dashed #3a3a3a;
        border-radius: 8px;
        padding: 40px;
    }
"""

TABLE_STYLE = """
    QTableWidget {
        background-color: #252525;
        border: 1px solid #3a3a3a;
        gridline-color: #3a3a3a;
        color: #e3e3e3;
    }
    QTableWidget::item {
        padding: 4px;
    }
    QHeaderView::section {
        background-color: #2d2d2d;
        color: #e3e3e3;
        border: 1px solid #3a3a3a;
        padding: 4px;
    }
"""
