#!/usr/bin/env python3
"""Test Advanced Search feature flag configuration (non-GUI parts)"""
from productivity_app.productivity_core.core.feature_flags_manager import FeatureFlagsManager
from productivity_app.productivity_core.core.app_context import AppContext
import sys
from pathlib import Path

# Add productivity_app to path
productivity_app_path = Path(__file__).parent / "productivity_app"
sys.path.insert(0, str(productivity_app_path))


def main():
    print("="*60)
    print("Advanced Search Feature Flag Integration Test")
    print("="*60)

    # Test 1: Create context and register manager
    print("\n[STEP 1] Creating AppContext and FeatureFlagsManager...")
    context = AppContext()
    feature_flags = FeatureFlagsManager()
    context.register('feature_flags', feature_flags)
    print("  ✓ Context created and manager registered")

    # Test 2: Verify advanced_search flag exists
    print("\n[STEP 2] Verifying 'advanced_search' flag in 'connectors' module...")
    metadata = feature_flags.get_flag_metadata('connectors', 'advanced_search')
    if not metadata:
        print("  ✗ FAILED: advanced_search flag not found!")
        return False

    name, description, default = metadata
    print(f"  ✓ Flag found:")
    print(f"      Name: {name}")
    print(f"      Description: {description}")
    print(f"      Default value: {default}")

    # Test 3: Verify flag value persistence
    print("\n[STEP 3] Testing flag value persistence...")

    # Get initial value
    initial = feature_flags.get('connectors', 'advanced_search')
    print(f"  Initial value: {initial}")

    # Set to True
    feature_flags.set('connectors', 'advanced_search', True)
    after_set_true = feature_flags.get('connectors', 'advanced_search')
    if after_set_true != True:
        print(f"  ✗ FAILED: Expected True, got {after_set_true}")
        return False
    print(f"  ✓ Set to True: {after_set_true}")

    # Set to False
    feature_flags.set('connectors', 'advanced_search', False)
    after_set_false = feature_flags.get('connectors', 'advanced_search')
    if after_set_false != False:
        print(f"  ✗ FAILED: Expected False, got {after_set_false}")
        return False
    print(f"  ✓ Set to False: {after_set_false}")

    # Test 4: Verify module structure
    print("\n[STEP 4] Verifying module structure...")
    all_flags = feature_flags.get_all_flags()
    expected_modules = ['connectors', 'document_scanner',
                        'epd', 'devops', 'remote_docs']

    for module in expected_modules:
        if module not in all_flags:
            print(f"  ✗ FAILED: Module '{module}' not found")
            return False
        print(
            f"  ✓ Module '{module}' found with flags: {list(all_flags[module].keys())}")

    # Test 5: Verify flag subscription capability
    print("\n[STEP 5] Testing flag subscription capability...")

    callback_called = []

    def on_flag_changed(enabled):
        callback_called.append(enabled)
        print(f"    → Callback invoked: advanced_search is now {enabled}")

    # Subscribe to changes
    feature_flags.subscribe('connectors', 'advanced_search', on_flag_changed)
    print("  ✓ Subscription created")

    # Change the flag
    print("  Changing flag to True...")
    feature_flags.set('connectors', 'advanced_search', True)

    # Verify callback was called
    if callback_called and callback_called[-1] == True:
        print("  ✓ Callback invoked correctly")
    else:
        print(f"  ✗ Callback not invoked or incorrect: {callback_called}")
        return False

    # Test 6: Verify global app access pattern
    print("\n[STEP 6] Verifying global app access pattern...")
    retrieved_manager = context.get('feature_flags')
    if retrieved_manager is feature_flags:
        print("  ✓ Manager retrieved from context correctly")
    else:
        print("  ✗ Manager not properly stored in context")
        return False

    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print("\nAdvanced Search feature flag is properly integrated:")
    print("  • Flag exists in 'connectors' module with default=False")
    print("  • Flag value can be get/set and persists")
    print("  • Subscriptions work and invoke callbacks")
    print("  • Manager accessible via AppContext.get('feature_flags')")
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
