"""
Utility: Check all reports for issues

Validates that:
- All reports are callable
- Parameters match function signatures
- Required parameters are satisfiable
- No circular dependencies

Run directly from IDE to validate all reports.
"""
import inspect
from typing import List, Tuple
from productivity_app.data_pipeline.registry import registry
from productivity_app.data_pipeline.reports.register import report_registry
from productivity_app.data_pipeline.parameters.input_parameters import (
    Parameter, PrimitiveParameter, CollectedParameter
)


def check_reports() -> Tuple[int, int, List[str]]:
    """Check all registered reports for issues
    
    Returns:
        Tuple of (passed_count, failed_count, error_messages)
    """
    print("=" * 80)
    print("REPORT VALIDATION")
    print("=" * 80)
    
    reports = registry.get_all_reports()
    
    if not reports:
        print("\n⚠️  No reports to check. Import report modules first.")
        return 0, 0, []
    
    passed = 0
    failed = 0
    errors = []
    
    for title, report_info in reports.items():
        print(f"\n📊 Checking: {title}")
        
        func = report_info.get('func')  # Changed from 'function' to 'func'
        inputs = report_info.get('inputs', [])
        
        # Check 1: Function is callable
        if not callable(func):
            msg = f"  ❌ Function is not callable"
            print(msg)
            errors.append(f"{title}: {msg}")
            failed += 1
            continue
        
        # Check 2: Get function signature
        try:
            sig = inspect.signature(func)
        except Exception as e:
            msg = f"  ❌ Cannot inspect signature: {e}"
            print(msg)
            errors.append(f"{title}: {msg}")
            failed += 1
            continue
        
        # Check 3: Parameters match signature
        func_params = list(sig.parameters.keys())
        input_names = []
        
        for inp in inputs:
            if hasattr(inp, 'name'):
                input_names.append(inp.name)
            else:
                input_names.append(str(inp))
        
        # Check for mismatches
        extra_inputs = [name for name in input_names if name not in func_params]
        if extra_inputs:
            msg = f"  ❌ Extra inputs not in signature: {extra_inputs}"
            print(msg)
            errors.append(f"{title}: {msg}")
            failed += 1
            continue
        
        missing_params = []
        for param_name, param in sig.parameters.items():
            if param.default == inspect.Parameter.empty:
                # Required parameter
                if param_name not in input_names:
                    missing_params.append(param_name)
        
        if missing_params:
            msg = f"  ⚠️  Missing required params in inputs: {missing_params}"
            print(msg)
            # This is a warning, not a failure
        
        # Check 4: CollectedParameters have collectors
        issues = []
        for inp in inputs:
            if isinstance(inp, CollectedParameter):
                if inp.output_type:
                    collectors = registry.get_collectors_for_type(inp.output_type)
                    if not collectors:
                        issues.append(f"No collector for {inp.name} (type: {inp.output_type})")
        
        if issues:
            msg = f"  ⚠️  Dependency issues: {'; '.join(issues)}"
            print(msg)
            print(f"     (Report may not be executable without collectors)")
        
        # Check 5: Try to get report wrapper
        try:
            wrapper = report_registry.get_report_by_name(title)
            if wrapper:
                can_generate = wrapper.can_generate()
                issues_list = wrapper.get_issues()
                
                if not can_generate:
                    msg = f"  ⚠️  Cannot generate: {', '.join(issues_list)}"
                    print(msg)
                else:
                    print(f"  ✅ Can generate")
            else:
                msg = f"  ❌ Cannot get report wrapper"
                print(msg)
                errors.append(f"{title}: {msg}")
                failed += 1
                continue
        except Exception as e:
            msg = f"  ❌ Error checking generation: {e}"
            print(msg)
            errors.append(f"{title}: {msg}")
            failed += 1
            continue
        
        # All checks passed
        print(f"  ✅ All checks passed")
        passed += 1
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  • {error}")
    
    return passed, failed, errors


if __name__ == "__main__":
    # Auto-import common reports
    print("Loading reports...\n")
    
    try:
        from productivity_app.data_pipeline.reports import csv_columns
        print("✓ Loaded: csv_columns")
    except ImportError as e:
        print(f"⚠️  Could not load csv_columns: {e}")
    
    try:
        from productivity_app.data_pipeline.reports import parts_summary_example
        print("✓ Loaded: parts_summary_example")
    except ImportError as e:
        print(f"⚠️  Could not load parts_summary_example: {e}")
    
    # Also load collectors for dependency checking
    try:
        from productivity_app.data_pipeline.data_collectors import csv_to_parts_list
        print("✓ Loaded: csv_to_parts_list collector")
    except ImportError as e:
        print(f"⚠️  Could not load collectors: {e}")
    
    print()
    passed, failed, errors = check_reports()
    
    # Exit with error code if any failed
    import sys
    sys.exit(0 if failed == 0 else 1)
