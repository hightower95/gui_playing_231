#!/usr/bin/env python3
"""
Template Validation Script
Validates all template files in the templates directory for syntax correctness
and template engine compatibility.

Usage:
    python validate_templates.py
    
Returns exit code 0 if all templates are valid, 1 if any issues found.
"""

import argparse
import ast
import configparser
import io
from pathlib import Path
import sys
from typing import Dict, List, Tuple, Any


def get_template_variables() -> Dict[str, Any]:
    """Get standard template variables for testing"""
    return {
        'app_name': 'TestApp',
        'library_name': 'test_lib',
        'venv_dir_name': '.test_venv',
        'help_page': 'https://example.com/help',
        'version': '1.0.0',
        'token_url': 'https://example.com/token',
        'core_libraries': 'test_lib>=1.0.0'
    }


def validate_python_template(template_path: Path, template_vars: Dict[str, Any], verbose: bool = False) -> Tuple[bool, str]:
    """
    Validate a Python template file (.pyw.template, .py.template)

    Returns:
        (is_valid, error_message)
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Test template formatting
        try:
            formatted_content = template_content.format(**template_vars)
        except Exception as e:
            return False, f"Template formatting error: {e}"

        # Test Python syntax
        try:
            ast.parse(formatted_content)
        except SyntaxError as e:
            return False, f"Generated Python syntax error: {e}"

        result_msg = f"Valid Python template ({len(formatted_content)} chars)"
        if verbose:
            result_msg += f"\n    Generated {len(formatted_content.splitlines())} lines of Python code"

        return True, result_msg

    except Exception as e:
        return False, f"File reading error: {e}"


def validate_ini_template(template_path: Path, template_vars: Dict[str, Any], verbose: bool = False) -> Tuple[bool, str]:
    """
    Validate an INI template file (.ini.template)

    Returns:
        (is_valid, error_message)
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Test template formatting
        try:
            formatted_content = template_content.format(**template_vars)
        except Exception as e:
            return False, f"Template formatting error: {e}"

        # Test INI syntax
        try:
            config = configparser.ConfigParser()
            config.read_string(formatted_content)
            sections = list(config.sections())
        except Exception as e:
            return False, f"Generated INI syntax error: {e}"

        result_msg = f"Valid INI template ({len(sections)} sections)"
        if verbose:
            result_msg += f"\n    Sections: {', '.join(sections) if sections else 'DEFAULT only'}"

        return True, result_msg

    except Exception as e:
        return False, f"File reading error: {e}"


def validate_text_template(template_path: Path, template_vars: Dict[str, Any], verbose: bool = False) -> Tuple[bool, str]:
    """
    Validate a generic text template file

    Returns:
        (is_valid, error_message)
    """
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Test template formatting
        try:
            formatted_content = template_content.format(**template_vars)
        except Exception as e:
            return False, f"Template formatting error: {e}"

        result_msg = f"Valid text template ({len(formatted_content)} chars)"
        if verbose:
            result_msg += f"\n    Generated {len(formatted_content.splitlines())} lines"

        return True, result_msg

    except Exception as e:
        return False, f"File reading error: {e}"


def get_validator_for_template(template_path: Path):
    """Get the appropriate validator function for a template file"""
    if template_path.name.endswith('.pyw.template') or template_path.name.endswith('.py.template'):
        return validate_python_template
    elif template_path.name.endswith('.ini.template'):
        return validate_ini_template
    else:
        return validate_text_template


def validate_all_templates(templates_dir: Path = None, verbose: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate all template files in the templates directory

    Returns:
        (all_valid, results_list)
    """
    if templates_dir is None:
        templates_dir = Path(__file__).parent

    template_vars = get_template_variables()
    results = []
    all_valid = True

    # Find all .template files
    template_files = list(templates_dir.glob('*.template'))

    if not template_files:
        results.append("⚠️  No template files found")
        return False, results

    results.append(f"🔍 Validating {len(template_files)} template files...")
    if verbose:
        results.append(f"📂 Templates directory: {templates_dir.absolute()}")
        results.append(
            f"🔧 Using template variables: {', '.join(template_vars.keys())}")
    results.append("")

    for template_path in sorted(template_files):
        validator = get_validator_for_template(template_path)
        is_valid, message = validator(template_path, template_vars, verbose)

        if is_valid:
            results.append(f"✅ {template_path.name}: {message}")
        else:
            results.append(f"❌ {template_path.name}: {message}")
            all_valid = False

    results.append("")
    if all_valid:
        results.append("🎉 All templates are valid!")
    else:
        results.append("💥 Some templates have issues - see details above")

    return all_valid, results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate template files for syntax and compatibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python validate_templates.py           # Basic validation
    python validate_templates.py -v        # Verbose mode with details
    python validate_templates.py --help    # Show this help
        """
    )
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Show detailed validation information')

    args = parser.parse_args()

    print("Template Validation Script")
    print("=" * 50)

    templates_dir = Path(__file__).parent
    all_valid, results = validate_all_templates(templates_dir, args.verbose)

    for result in results:
        print(result)

    # Exit with appropriate code
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
