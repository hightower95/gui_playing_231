"""
Tile data definitions for the start page

Each tile is represented as a tuple:
(title, subtitle, bullets, tab_id, is_visible)

TODO: Dynamically load from TAB_CONFIG for real tab visibility status
"""


def get_tile_data():
    """Get tile data for all tabs
    
    Returns:
        List of tuples: (title, subtitle, bullets_list, tab_id, is_visible)
    """
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
