"""
Test script to debug tab visibility issues
"""
import sys
import traceback

try:
    from PySide6.QtWidgets import QApplication
    from app.core.app_context import AppContext
    from app.core.config_manager import ConfigManager
    from app.tabs.main_window import MainWindow

    print("="*60)
    print("Starting Tab Visibility Test")
    print("="*60)

    app = QApplication(sys.argv)

    print("\n1. Initializing ConfigManager...")
    ConfigManager.initialize()
    print("   ✓ ConfigManager initialized")

    print("\n2. Creating AppContext...")
    context = AppContext()
    print("   ✓ AppContext created")

    print("\n3. Creating MainWindow...")
    window = MainWindow(context)
    print("   ✓ MainWindow created")

    print("\n4. Showing window...")
    window.show()
    print("   ✓ Window shown")

    print("\n5. Tab registry contents:")
    for tab_name, info in window.tab_registry.items():
        print(f"   - {tab_name}: {info['title']}")

    print("\n6. Current visible tabs:")
    for i in range(window.tabs.count()):
        print(f"   - Tab {i}: {window.tabs.tabText(i)}")

    print("\n" + "="*60)
    print("Application started successfully!")
    print("Try toggling tab visibility in the Settings tab")
    print("Watch the console for debug output")
    print("="*60 + "\n")

    sys.exit(app.exec())

except Exception as e:
    print("\n" + "="*60)
    print("ERROR OCCURRED!")
    print("="*60)
    print(f"\nError: {e}")
    print(f"\nError type: {type(e).__name__}")
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n" + "="*60)
    sys.exit(1)
