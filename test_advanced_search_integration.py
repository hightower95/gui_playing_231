#!/usr/bin/env python3
"""Test Advanced Search feature flag integration"""
import sys
from pathlib import Path

# Add productivity_app to path
productivity_app_path = Path(__file__).parent / "productivity_app"
sys.path.insert(0, str(productivity_app_path))

from productivity_app.productivity_core.core.app_context import AppContext
from productivity_app.productivity_core.core.feature_flags_manager import FeatureFlagsManager

def test_feature_flags_manager():
    """Test that FeatureFlagsManager is properly configured"""
    print("[TEST] Testing FeatureFlagsManager...")
    
    context = AppContext()
    context.register('feature_flags', FeatureFlagsManager())
    feature_flags = context.get('feature_flags')
    
    # Test 1: Check advanced_search flag exists
    print("[TEST] Checking advanced_search flag in connectors...")
    metadata = feature_flags.get_flag_metadata('connectors', 'advanced_search')
    if metadata:
        name, description, default = metadata
        print(f"  ✓ Flag found: {name}")
        print(f"    Description: {description}")
        print(f"    Default: {default}")
    else:
        print("  ✗ Flag NOT found!")
        return False
    
    # Test 2: Get flag value
    print("[TEST] Getting flag value...")
    value = feature_flags.get('connectors', 'advanced_search')
    print(f"  Initial value: {value}")
    
    # Test 3: Set flag value
    print("[TEST] Setting flag to True...")
    feature_flags.set('connectors', 'advanced_search', True)
    value = feature_flags.get('connectors', 'advanced_search')
    print(f"  New value: {value}")
    if value != True:
        print("  ✗ Flag not set correctly!")
        return False
    print("  ✓ Flag set correctly")
    
    # Test 4: Set flag to False
    print("[TEST] Setting flag to False...")
    feature_flags.set('connectors', 'advanced_search', False)
    value = feature_flags.get('connectors', 'advanced_search')
    print(f"  New value: {value}")
    if value != False:
        print("  ✗ Flag not set correctly!")
        return False
    print("  ✓ Flag set correctly")
    
    # Test 5: Get all flags
    print("[TEST] Getting all flags...")
    all_flags = feature_flags.get_all_flags()
    print(f"  Modules: {list(all_flags.keys())}")
    if 'connectors' in all_flags:
        print(f"    Connectors flags: {list(all_flags['connectors'].keys())}")
    
    print("\n[TEST] All tests passed! ✓")
    return True

def test_settings_tab_structure():
    """Test that SettingsTab properly integrates with FeatureFlagsManager"""
    print("\n[TEST] Testing SettingsTab structure...")
    
    try:
        from productivity_app.productivity_core.tabs.settings_tab import SettingsTab
        
        context = AppContext()
        context.register('feature_flags', FeatureFlagsManager())
        
        # Create settings tab with context
        settings_tab = SettingsTab(context=context)
        print("  ✓ SettingsTab created successfully with context")
        
        # Check that feature_flags was injected
        if hasattr(settings_tab, 'feature_flags'):
            print("  ✓ feature_flags attribute found")
        else:
            print("  ✗ feature_flags attribute NOT found!")
            return False
        
        # Check that feature_flag_checkboxes is nested
        if isinstance(settings_tab.feature_flag_checkboxes, dict):
            print(f"  ✓ feature_flag_checkboxes is dict with keys: {list(settings_tab.feature_flag_checkboxes.keys())}")
        else:
            print("  ✗ feature_flag_checkboxes structure incorrect!")
            return False
        
        print("[TEST] SettingsTab structure tests passed! ✓")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = True
    
    success = test_feature_flags_manager() and success
    success = test_settings_tab_structure() and success
    
    if success:
        print("\n" + "="*50)
        print("All tests PASSED! ✓")
        print("="*50)
        sys.exit(0)
    else:
        print("\n" + "="*50)
        print("Some tests FAILED! ✗")
        print("="*50)
        sys.exit(1)
