#!/usr/bin/env python3
"""
Test Script for run_app.pyw Upgrade Logic
Tests the intelligent version management functions without actually performing upgrades.

Usage:
    python test_upgrade_logic.py           # Run all tests
    python test_upgrade_logic.py -v        # Verbose mode
    python test_upgrade_logic.py --demo    # Demo mode with examples
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util
import tempfile
import os

# Color codes for output


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def load_run_app_functions():
    """Dynamically load functions from run_app.pyw"""
    run_app_path = Path(__file__).parent / "run_app.pyw"

    if not run_app_path.exists():
        print(f"{Colors.RED}❌ run_app.pyw not found at: {run_app_path}{Colors.END}")
        return None

    # Load the module
    spec = importlib.util.spec_from_file_location("run_app", run_app_path)
    run_app_module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(run_app_module)
        return run_app_module
    except Exception as e:
        print(f"{Colors.RED}❌ Failed to load run_app.pyw: {e}{Colors.END}")
        return None


def test_parse_version(run_app, verbose=False):
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
            result = run_app.parse_version(version_str)
            success = result == expected

            if success:
                passed += 1
                status = f"{Colors.GREEN}✅{Colors.END}"
            else:
                status = f"{Colors.RED}❌{Colors.END}"

            if verbose or not success:
                print(
                    f"  {status} parse_version('{version_str}') = {result}, expected {expected}")

        except Exception as e:
            print(
                f"  {Colors.RED}❌{Colors.END} parse_version('{version_str}') raised: {e}")

    print(
        f"  {Colors.BOLD}Result: {passed}/{len(test_cases)} tests passed{Colors.END}")
    return passed == len(test_cases)


def test_is_stable_version(run_app, verbose=False):
    """Test stable version detection"""
    test_cases = [
        ("1.0.3", True),   # Even minor = stable
        ("1.2.5", True),   # Even minor = stable
        ("1.4.0", True),   # Even minor = stable
        ("1.1.0", False),  # Odd minor = test
        ("1.3.2", False),  # Odd minor = test
        ("2.1.1", False),  # Odd minor = test
        ("invalid", True),  # Should default to stable for safety
    ]

    print(f"\n{Colors.CYAN}🧪 Testing is_stable_version function{Colors.END}")
    passed = 0

    for version_str, expected in test_cases:
        try:
            result = run_app.is_stable_version(version_str)
            success = result == expected

            if success:
                passed += 1
                status = f"{Colors.GREEN}✅{Colors.END}"
            else:
                status = f"{Colors.RED}❌{Colors.END}"

            if verbose or not success:
                stability = "stable" if expected else "test"
                print(
                    f"  {status} is_stable_version('{version_str}') = {result} (expected {stability})")

        except Exception as e:
            print(
                f"  {Colors.RED}❌{Colors.END} is_stable_version('{version_str}') raised: {e}")

    print(
        f"  {Colors.BOLD}Result: {passed}/{len(test_cases)} tests passed{Colors.END}")
    return passed == len(test_cases)


def test_should_upgrade_logic(run_app, verbose=False):
    """Test the should_upgrade decision logic with mock data"""

    # Mock the version fetching functions
    def mock_get_all_versions(venv_python, library_name):
        return ["1.0.0", "1.0.1", "1.1.0", "1.1.1", "1.2.0", "1.2.1", "1.3.0", "2.0.0", "2.1.0"]

    # Temporarily replace the GLOBAL function in the run_app object's globals
    original_get_all = getattr(run_app, 'get_all_versions', None)
    setattr(run_app, 'get_all_versions', mock_get_all_versions)

    # Also need to patch globals if the function uses global scope
    run_app_globals = getattr(run_app.should_upgrade, '__globals__', {})
    original_global_get_all = run_app_globals.get('get_all_versions', None)
    if 'get_all_versions' in run_app_globals:
        run_app_globals['get_all_versions'] = mock_get_all_versions

    test_cases = [
        # (current_version, config, expected_result, description)
        ("1.0.0", {
            "auto_upgrade_major_version": False,
            "auto_upgrade_minor_version": False,
            "auto_upgrade_patches": False,
            "allow_upgrade_to_test_releases": False
        }, None, "No upgrade when all disabled"),

        ("1.0.0", {
            "auto_upgrade_major_version": False,
            "auto_upgrade_minor_version": False,
            "auto_upgrade_patches": True,
            "allow_upgrade_to_test_releases": False
        }, "1.0.1", "Patches only: 1.0.0 → 1.0.1"),

        ("1.0.0", {
            "auto_upgrade_major_version": False,
            "auto_upgrade_minor_version": True,
            "auto_upgrade_patches": True,
            "allow_upgrade_to_test_releases": False
        }, "1.2.0", "Minor+Patches: 1.0.0 → 1.2.0 (latest stable minor)"),

        ("1.0.0", {
            "auto_upgrade_major_version": True,
            "auto_upgrade_minor_version": True,
            "auto_upgrade_patches": True,
            "allow_upgrade_to_test_releases": False
        }, "2.0.0", "All upgrades: 1.0.0 → 2.0.0 (latest stable major)"),

        ("1.0.0", {
            "auto_upgrade_major_version": False,
            "auto_upgrade_minor_version": True,
            "auto_upgrade_patches": True,
            "allow_upgrade_to_test_releases": True
        }, "1.3.0", "Minor+Test: 1.0.0 → 1.3.0 (latest test minor)"),

        ("1.2.1", {
            "auto_upgrade_major_version": False,
            "auto_upgrade_minor_version": True,
            "auto_upgrade_patches": True,
            "allow_upgrade_to_test_releases": False
        }, None, "No upgrade when already latest stable minor"),

        ("2.0.0", {
            "auto_upgrade_major_version": False,
            "auto_upgrade_minor_version": True,
            "auto_upgrade_patches": True,
            "allow_upgrade_to_test_releases": True
        }, "2.1.0", "Within major 2: 2.0.0 → 2.1.0"),
    ]

    print(
        f"\n{Colors.CYAN}🧪 Testing granular should_upgrade decision logic{Colors.END}")
    passed = 0

    for current_version, config, expected, description in test_cases:
        try:
            # Create fake venv_python and library_name for the function call
            fake_venv = Path("/fake/venv/python")
            fake_library = "test_lib"

            result = run_app.should_upgrade(
                current_version, config, fake_venv, fake_library)
            success = result == expected

            if success:
                passed += 1
                status = f"{Colors.GREEN}✅{Colors.END}"
            else:
                status = f"{Colors.RED}❌{Colors.END}"

            if verbose or not success:
                result_str = result if result else "None"
                expected_str = expected if expected else "None"
                print(f"  {status} {description}")
                print(f"    Current: {current_version}, Config: {config}")
                print(f"    Result: {result_str}, Expected: {expected_str}")

        except Exception as e:
            print(f"  {Colors.RED}❌{Colors.END} should_upgrade test raised: {e}")

    # Restore original functions
    if original_get_all:
        setattr(run_app, 'get_all_versions', original_get_all)
    if original_global_get_all and 'get_all_versions' in run_app_globals:
        run_app_globals['get_all_versions'] = original_global_get_all

    print(
        f"  {Colors.BOLD}Result: {passed}/{len(test_cases)} tests passed{Colors.END}")
    return passed == len(test_cases)


def test_log_upgrade_event(run_app, verbose=False):
    """Test upgrade logging function"""
    print(f"\n{Colors.CYAN}🧪 Testing log_upgrade_event function{Colors.END}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        try:
            # Test logging
            run_app.log_upgrade_event(
                temp_path,
                "TEST_EVENT",
                current="1.0.0",
                target="1.0.1",
                reason="test"
            )

            log_file = temp_path / "upgrade_history.log"
            if log_file.exists():
                content = log_file.read_text()
                if "TEST_EVENT" in content and "current=1.0.0" in content:
                    print(
                        f"  {Colors.GREEN}✅{Colors.END} Logging works correctly")
                    if verbose:
                        print(f"    Log content: {content.strip()}")
                    return True
                else:
                    print(
                        f"  {Colors.RED}❌{Colors.END} Log content missing expected data")
                    return False
            else:
                print(f"  {Colors.RED}❌{Colors.END} Log file not created")
                return False

        except Exception as e:
            print(f"  {Colors.RED}❌{Colors.END} log_upgrade_event raised: {e}")
            return False


def demo_upgrade_scenarios(run_app):
    """Demonstrate upgrade scenarios with real-world examples"""
    print(
        f"\n{Colors.BLUE}{Colors.BOLD}🎭 GRANULAR UPGRADE SCENARIOS DEMO{Colors.END}")

    scenarios = [
        {
            "name": "Manual Feature Update - Auto Patch",
            "current": "1.2.3",
            "expected": "1.2.5 (latest patch in current minor)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": False,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": False
            },
            "available": ["1.2.4", "1.2.5", "1.3.0", "2.0.0"],
        },
        {
            "name": "Manual Feature Update - Manual Patch",
            "current": "1.2.3",
            "expected": "No upgrade (features and patches manual)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": False,
                "auto_upgrade_patches": False,
                "allow_upgrade_to_test_releases": False
            },
            "available": ["1.2.4", "1.2.5", "1.4.0", "2.0.0"],
        },
        {
            "name": "Auto Feature Update - Auto Patch",
            "current": "1.2.3",
            "expected": "1.4.0 (latest stable minor feature)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": True,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": False
            },
            "available": ["1.2.4", "1.2.5", "1.4.0", "1.5.1", "2.0.0"],
        },
        {
            "name": "Auto Feature Update - Manual Patch",
            "current": "1.2.3",
            "expected": "1.4.0 (latest stable feature, skips patches)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": True,
                "auto_upgrade_patches": False,
                "allow_upgrade_to_test_releases": False
            },
            "available": ["1.2.4", "1.2.5", "1.4.0", "1.5.1", "2.0.0"],
        },
        {
            "name": "Auto Major - Auto Feature - Auto Patch",
            "current": "1.2.3",
            "expected": "2.2.0 (latest stable major workflow)",
            "config": {
                "auto_upgrade_major_version": True,
                "auto_upgrade_minor_version": True,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": False
            },
            "available": ["1.2.4", "1.4.0", "2.0.0", "2.2.0"],
        },
        {
            "name": "Test User - Manual Feature Update - Auto Patch",
            "current": "1.2.3",
            "expected": "1.2.5 (latest patch, test releases allowed)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": False,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": True
            },
            "available": ["1.2.4", "1.2.5", "1.3.0", "1.4.0", "2.0.0"],
        },
        {
            "name": "Test User - Manual Feature Update - Manual Patch",
            "current": "1.2.3",
            "expected": "No upgrade (only test releases allowed, but features/patches manual)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": False,
                "auto_upgrade_patches": False,
                "allow_upgrade_to_test_releases": True
            },
            "available": ["1.2.4", "1.2.5", "1.3.0", "1.4.0", "2.0.0"],
        },
        {
            "name": "Test User - Auto Feature Update - Auto Patch",
            "current": "1.2.3",
            "expected": "1.5.1 (latest test feature with patches)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": True,
                "auto_upgrade_patches": True,
                "allow_upgrade_to_test_releases": True
            },
            "available": ["1.2.4", "1.3.0", "1.4.0", "1.5.1", "2.0.0"],
        },
        {
            "name": "Test User - Auto Feature Update - Manual Patch",
            "current": "1.2.3",
            "expected": "1.4.0 (latest stable feature, skips test 1.5.1 and patches)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": True,
                "auto_upgrade_patches": False,
                "allow_upgrade_to_test_releases": True
            },
            "available": ["1.2.4", "1.3.0", "1.4.0", "1.5.1", "2.0.0"],
        },
        {
            "name": "Manual Everything",
            "current": "1.2.3",
            "expected": "No upgrade (all auto-upgrade disabled)",
            "config": {
                "auto_upgrade_major_version": False,
                "auto_upgrade_minor_version": False,
                "auto_upgrade_patches": False,
                "allow_upgrade_to_test_releases": False
            },
            "available": ["1.2.4", "1.4.0", "2.0.0"],
        }
    ]

    # Mock get_all_versions for demo
    def mock_get_all_versions(venv_python, library_name):
        return current_scenario_versions

    original_get_all = getattr(run_app, 'get_all_versions', None)
    setattr(run_app, 'get_all_versions', mock_get_all_versions)

    # Also need to patch globals if the function uses global scope
    run_app_globals = getattr(run_app.should_upgrade, '__globals__', {})
    original_global_get_all = run_app_globals.get('get_all_versions', None)
    if 'get_all_versions' in run_app_globals:
        run_app_globals['get_all_versions'] = mock_get_all_versions

    for scenario in scenarios:
        print(f"\n{Colors.YELLOW}📋 Scenario: {scenario['name']}{Colors.END}")
        print(f"   Current version: {scenario['current']}")

        # Show config in a readable format
        config_str = []
        for key, value in scenario['config'].items():
            short_key = key.replace('auto_upgrade_', '').replace(
                '_version', '').replace('allow_upgrade_to_', '')
            config_str.append(f"{short_key}={value}")
        print(f"   Configuration: {', '.join(config_str)}")
        print(f"   Available versions: {scenario['available']}")
        print(
            f"   {Colors.YELLOW}Expected: {scenario['expected']}{Colors.END}")

        # Set up mock data for this scenario
        current_scenario_versions = scenario['available']

        # Get upgrade decision
        fake_venv = Path("/fake/venv/python")
        fake_library = "test_lib"

        try:
            decision = run_app.should_upgrade(
                scenario['current'], scenario['config'], fake_venv, fake_library)

            if decision:
                # Analyze the upgrade type
                current_major, current_minor, current_patch = run_app.parse_version(
                    scenario['current'])
                target_major, target_minor, target_patch = run_app.parse_version(
                    decision)

                if target_major > current_major:
                    upgrade_type = "major"
                elif target_minor > current_minor:
                    upgrade_type = "minor"
                else:
                    upgrade_type = "patch"

                is_test = not run_app.is_stable_version(decision)
                release_type = "test" if is_test else "stable"

                print(
                    f"   {Colors.GREEN}🚀 Actual: Upgrade to {decision} ({upgrade_type} {release_type}){Colors.END}")
            else:
                print(
                    f"   {Colors.CYAN}🔒 Actual: No upgrade (current version is optimal){Colors.END}")

        except Exception as e:
            print(f"   {Colors.RED}❌ Error: {e}{Colors.END}")

    # Restore original function
    if original_get_all:
        setattr(run_app, 'get_all_versions', original_get_all)
    if original_global_get_all and 'get_all_versions' in run_app_globals:
        run_app_globals['get_all_versions'] = original_global_get_all


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test the upgrade logic in run_app.pyw",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show detailed test output')
    parser.add_argument('--demo', action='store_true',
                        help='Run demo scenarios')

    args = parser.parse_args()

    print(f"{Colors.BOLD}🔬 run_app.pyw Upgrade Logic Tester{Colors.END}")
    print("=" * 50)

    # Load the run_app module
    run_app = load_run_app_functions()
    if not run_app:
        sys.exit(1)

    print(f"{Colors.GREEN}✅ Successfully loaded run_app.pyw{Colors.END}")

    if args.demo:
        demo_upgrade_scenarios(run_app)
        return

    # Run all tests
    all_passed = True

    tests = [
        ("Version Parsing", test_parse_version),
        ("Stable Version Detection", test_is_stable_version),
        ("Upgrade Decision Logic", test_should_upgrade_logic),
        ("Upgrade Logging", test_log_upgrade_event),
    ]

    for test_name, test_func in tests:
        try:
            passed = test_func(run_app, args.verbose)
            all_passed = all_passed and passed
        except Exception as e:
            print(f"{Colors.RED}❌ {test_name} failed with exception: {e}{Colors.END}")
            all_passed = False

    print(f"\n{Colors.BOLD}📊 OVERALL RESULTS{Colors.END}")
    print("=" * 30)

    if all_passed:
        print(
            f"{Colors.GREEN}🎉 All tests passed! Upgrade logic is working correctly.{Colors.END}")
        sys.exit(0)
    else:
        print(
            f"{Colors.RED}💥 Some tests failed. Check the upgrade logic implementation.{Colors.END}")
        sys.exit(1)


if __name__ == "__main__":
    main()
