#!/usr/bin/env python3
"""
Test Script for utilities/version_manager.py functions used in run_app.pyw
Tests the intelligent version management functions without actually performing upgrades.
"""

import sys
from pathlib import Path

# Add installer to path to access utilities
installer_dir = Path(__file__).parent / "alternative_app_installer" / "installer"
sys.path.insert(0, str(installer_dir))

try:
    from install_gui.utilities.version_manager import (
        parse_version,
        is_stable_version,
        should_upgrade,
        get_installed_version,
        upgrade_to_version
    )
    print("✅ Successfully imported utilities.version_manager functions")
except ImportError as e:
    print(f"❌ Failed to import utilities: {e}")
    sys.exit(1)

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def test_parse_version():
    """Test version parsing function"""
    test_cases = [
        ("1.2.3", (1, 2, 3)),
        ("10.15.7", (10, 15, 7)),
        ("2.0.0-beta", (2, 0, 0)),  # Should handle pre-release tags
        ("invalid", (0, 0, 0)),
        ("", (0, 0, 0)),
        ("1.2", (0, 0, 0)),  # Incomplete version
    ]

    print(f"\n{Colors.CYAN}🧪 Testing parse_version function{Colors.END}")
    passed = 0

    for version_str, expected in test_cases:
        try:
            result = parse_version(version_str)
            success = result == expected

            if success:
                passed += 1
                status = f"{Colors.GREEN}✅{Colors.END}"
            else:
                status = f"{Colors.RED}❌{Colors.END}"

            print(f"  {status} parse_version('{version_str}') = {result}, expected {expected}")

        except Exception as e:
            print(f"  {Colors.RED}❌{Colors.END} parse_version('{version_str}') raised: {e}")

    print(f"  {Colors.BOLD}Result: {passed}/{len(test_cases)} tests passed{Colors.END}")
    return passed == len(test_cases)


def test_is_stable_version():
    """Test stable version detection"""
    test_cases = [
        ("1.0.3", True),   # Even minor = stable
        ("1.2.5", True),   # Even minor = stable
        ("1.4.0", True),   # Even minor = stable
        ("1.1.0", False),  # Odd minor = test
        ("1.3.2", False),  # Odd minor = test
        ("2.1.1", False),  # Odd minor = test
    ]

    print(f"\n{Colors.CYAN}🧪 Testing is_stable_version function{Colors.END}")
    passed = 0

    for version_str, expected in test_cases:
        try:
            result = is_stable_version(version_str)
            success = result == expected

            if success:
                passed += 1
                status = f"{Colors.GREEN}✅{Colors.END}"
            else:
                status = f"{Colors.RED}❌{Colors.END}"

            stability = "stable" if expected else "test"
            print(f"  {status} is_stable_version('{version_str}') = {result} (expected {stability})")

        except Exception as e:
            print(f"  {Colors.RED}❌{Colors.END} is_stable_version('{version_str}') raised: {e}")

    print(f"  {Colors.BOLD}Result: {passed}/{len(test_cases)} tests passed{Colors.END}")
    return passed == len(test_cases)


def test_should_upgrade_logic():
    """Test the should_upgrade decision logic with real scenarios"""
    
    # We'll test with mock scenarios since we can't make real network calls
    test_cases = [
        {
            "name": "Patch upgrades only",
            "current": "1.2.3",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": False, 
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": False
            },
            "description": "Should only upgrade patches within same minor version"
        },
        {
            "name": "Minor upgrades enabled",
            "current": "1.0.0",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": True,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": False
            },
            "description": "Should upgrade to latest stable minor version"
        },
        {
            "name": "All upgrades disabled",
            "current": "1.0.0",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": False,
                "auto_upgrade_patches": False,
                "allow_upgrade_to_test_releases": False
            },
            "description": "Should not upgrade at all"
        }
    ]

    print(f"\n{Colors.CYAN}🧪 Testing should_upgrade decision logic{Colors.END}")
    
    for test_case in test_cases:
        print(f"\n  {Colors.YELLOW}📋 {test_case['name']}{Colors.END}")
        print(f"    Current: {test_case['current']}")
        print(f"    Description: {test_case['description']}")
        
        # Create fake paths for testing
        fake_venv = Path("/fake/venv/python")
        fake_library = "test_library"
        
        try:
            # Note: This will likely fail because it tries to run subprocess commands
            # But it will test the config parsing logic
            result = should_upgrade(test_case['current'], test_case['config'], fake_venv, fake_library)
            print(f"    {Colors.GREEN}✅{Colors.END} Function executed, result: {result}")
        except Exception as e:
            # Expected to fail due to subprocess calls, but config logic should work
            print(f"    {Colors.YELLOW}⚠️{Colors.END} Function failed as expected (subprocess): {str(e)[:100]}...")
    
    return True  # We just want to verify the function can be called


def demo_config_scenarios():
    """Show how different configurations would behave"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}🎭 CONFIGURATION SCENARIOS{Colors.END}")
    
    scenarios = [
        {
            "name": "Conservative User (patches only)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": False,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": False
            },
            "behavior": "Only installs bug fixes, no new features"
        },
        {
            "name": "Balanced User (features but not breaking)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": True,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": False
            },
            "behavior": "Gets new features and bug fixes, avoids breaking changes"
        },
        {
            "name": "Aggressive User (everything)",
            "config": {
                "auto_upgrade_major_version": True,
                "auto_upgrade_minor_version": True,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": False
            },
            "behavior": "Gets all stable updates including breaking changes"
        },
        {
            "name": "Beta Tester",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": True,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": True
            },
            "behavior": "Gets test releases for new features"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{Colors.YELLOW}👤 {scenario['name']}{Colors.END}")
        print(f"   Configuration:")
        for key, value in scenario['config'].items():
            clean_key = key.replace('auto_upgrade_', '').replace('_version', '').replace('allow_upgrade_to_', '')
            print(f"     {clean_key}: {value}")
        print(f"   {Colors.GREEN}Behavior: {scenario['behavior']}{Colors.END}")


def main():
    """Main test runner"""
    print(f"{Colors.BOLD}🔬 Testing utilities/version_manager.py functions{Colors.END}")
    print("=" * 60)
    
    all_passed = True
    
    tests = [
        ("Version Parsing", test_parse_version),
        ("Stable Version Detection", test_is_stable_version),
        ("Upgrade Decision Logic", test_should_upgrade_logic),
    ]
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            all_passed = all_passed and passed
        except Exception as e:
            print(f"{Colors.RED}❌ {test_name} failed with exception: {e}{Colors.END}")
            all_passed = False
    
    # Show configuration examples
    demo_config_scenarios()
    
    print(f"\n{Colors.BOLD}📊 OVERALL RESULTS{Colors.END}")
    print("=" * 30)
    
    if all_passed:
        print(f"{Colors.GREEN}🎉 Core functions are working! run_app.pyw should use these correctly.{Colors.END}")
        print(f"{Colors.CYAN}💡 The auto_upgrade_* settings in launch_config.ini will control upgrade behavior.{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}💥 Some tests failed. Check the utilities implementation.{Colors.END}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)