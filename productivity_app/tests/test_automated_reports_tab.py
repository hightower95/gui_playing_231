"""Quick test to verify automated reports tab loads in the main app"""
import sys
from PySide6.QtWidgets import QApplication
from productivity_app.productivity_core.core.app_context import AppContext
from productivity_app.productivity_core.tabs.tab_config import TAB_CONFIG, get_tab_config_by_id


def test_automated_reports_config():
    """Test that automated reports is in tab config"""
    print("\n=== Testing Automated Reports Configuration ===")
    
    # Check if tab exists in config
    config = get_tab_config_by_id('automated_reports')
    assert config is not None, "❌ automated_reports not found in TAB_CONFIG"
    print("✓ Tab config found")
    
    # Verify required fields
    assert 'presenter_class' in config, "❌ Missing presenter_class"
    print(f"✓ Presenter class: {config['presenter_class'].__name__}")
    
    assert 'tile' in config, "❌ Missing tile config"
    print(f"✓ Tile title: {config['tile']['title']}")
    
    assert config['tile']['show_in_start_page'], "❌ Not visible in start page"
    print("✓ Will show in start page")
    
    print(f"\nTab order position: {[t['id'] for t in TAB_CONFIG].index('automated_reports') + 1} of {len(TAB_CONFIG)}")


def test_automated_reports_instantiation():
    """Test that automated reports view can be instantiated"""
    print("\n=== Testing Automated Reports Instantiation ===")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        from productivity_app.productivity_core.tabs.automated_reports import AutomatedReportsView
        
        # Create view
        view = AutomatedReportsView()
        print(f"✓ View created: {view.__class__.__name__}")
        print(f"✓ Module ID: {view.MODULE_ID}")
        print(f"✓ Tab Title: {view.TAB_TITLE}")
        
        # Check if presenter exists
        assert hasattr(view, 'presenter'), "❌ View missing presenter"
        print(f"✓ Presenter attached: {view.presenter.__class__.__name__}")
        
        # Check if main components exist
        assert hasattr(view, 'left_panel'), "❌ Missing left_panel"
        assert hasattr(view, 'search_panel'), "❌ Missing search_panel"
        assert hasattr(view, 'results_panel'), "❌ Missing results_panel"
        print("✓ All main components present")
        
        view.close()
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    test_automated_reports_config()
    success = test_automated_reports_instantiation()
    sys.exit(0 if success else 1)
