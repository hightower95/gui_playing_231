"""
Compare Two Parts Lists Report

EXAMPLE: How to build a report that compares two CSV files containing parts.

This demonstrates:
1. Using multiple inputs of the same type
2. Automatic CSV→Parts conversion
3. Simple diff logic
4. Type hints for IDE support
"""
from typing import List, Dict, Any
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.parameters import ParameterEnum
from productivity_app.data_pipeline.models.part import Part


@report(
    title="Compare Two Parts Lists",
    description="Find added, removed, and common parts between two CSV files",
    inputs=[
        ParameterEnum.PartsList(
            name="old_parts",
            description="Original/baseline parts list (CSV file)"
        ),
        ParameterEnum.PartsList(
            name="new_parts", 
            description="Updated parts list (CSV file)"
        )
    ]
)
def compare_two_parts_lists(
    old_parts: List[Part], 
    new_parts: List[Part]
) -> Dict[str, Any]:
    """Compare two parts lists and find differences
    
    Args:
        old_parts: First parts list (auto-converted from CSV)
        new_parts: Second parts list (auto-converted from CSV)
        
    Returns:
        Dictionary with comparison results:
        - added: parts in new_parts but not in old_parts
        - removed: parts in old_parts but not in new_parts  
        - common: parts in both lists
        - summary: human-readable text
        
    Example Usage:
        # The system will prompt for two CSV files
        # Both will be automatically converted to Part objects
        result = compare_two_parts_lists(old_parts, new_parts)
        print(result['summary'])
    """
    
    # Create lookup dictionaries by part number
    old_dict = {p.part_number: p for p in old_parts}
    new_dict = {p.part_number: p for p in new_parts}
    
    # Find differences
    old_numbers = set(old_dict.keys())
    new_numbers = set(new_dict.keys())
    
    added_numbers = new_numbers - old_numbers
    removed_numbers = old_numbers - new_numbers
    common_numbers = old_numbers & new_numbers
    
    # Build result
    added = [new_dict[num] for num in added_numbers]
    removed = [old_dict[num] for num in removed_numbers]
    common = [new_dict[num] for num in common_numbers]
    
    # Generate summary
    summary_lines = [
        "═" * 60,
        "PARTS LIST COMPARISON",
        "═" * 60,
        f"Original list: {len(old_parts)} parts",
        f"Updated list:  {len(new_parts)} parts",
        "",
        f"✅ Added:     {len(added)} parts",
        f"❌ Removed:   {len(removed)} parts", 
        f"➡️  Unchanged: {len(common)} parts",
        "═" * 60,
    ]
    
    if added:
        summary_lines.append("\n📥 ADDED PARTS:")
        for part in sorted(added, key=lambda p: p.part_number):
            summary_lines.append(f"  + {part.part_number}: {part.part_name}")
            
    if removed:
        summary_lines.append("\n📤 REMOVED PARTS:")
        for part in sorted(removed, key=lambda p: p.part_number):
            summary_lines.append(f"  - {part.part_number}: {part.part_name}")
    
    summary = "\n".join(summary_lines)
    
    # Print for immediate feedback
    print(summary)
    
    return {
        "added": added,
        "removed": removed,
        "common": common,
        "added_count": len(added),
        "removed_count": len(removed),
        "common_count": len(common),
        "summary": summary
    }


@report(
    title="Parts Comparison - Detailed",
    description="Compare two parts lists with field-level differences",
    inputs=[
        ParameterEnum.PartsList(name="baseline", description="Baseline parts"),
        ParameterEnum.PartsList(name="current", description="Current parts")
    ]
)
def compare_parts_detailed(
    baseline: List[Part],
    current: List[Part]
) -> Dict[str, Any]:
    """Compare parts with detailed field changes
    
    Args:
        baseline: Baseline parts list
        current: Current parts list
        
    Returns:
        Detailed comparison including field-level changes
    """
    baseline_dict = {p.part_number: p for p in baseline}
    current_dict = {p.part_number: p for p in current}
    
    baseline_numbers = set(baseline_dict.keys())
    current_numbers = set(current_dict.keys())
    
    # Parts only in one list
    added = current_numbers - baseline_numbers
    removed = baseline_numbers - current_numbers
    common = baseline_numbers & current_numbers
    
    # Check for field changes in common parts
    modified = []
    for part_num in common:
        old_part = baseline_dict[part_num]
        new_part = current_dict[part_num]
        
        changes = {}
        
        # Compare fields
        if old_part.part_name != new_part.part_name:
            changes['part_name'] = (old_part.part_name, new_part.part_name)
            
        if getattr(old_part, 'quantity', None) != getattr(new_part, 'quantity', None):
            changes['quantity'] = (
                getattr(old_part, 'quantity', None),
                getattr(new_part, 'quantity', None)
            )
        
        if changes:
            modified.append({
                'part_number': part_num,
                'changes': changes
            })
    
    # Build summary
    summary_lines = [
        "═" * 70,
        "DETAILED PARTS COMPARISON",
        "═" * 70,
        f"📊 Statistics:",
        f"  Total in baseline: {len(baseline)}",
        f"  Total in current:  {len(current)}",
        f"  Added:             {len(added)}",
        f"  Removed:           {len(removed)}",
        f"  Modified:          {len(modified)}",
        f"  Unchanged:         {len(common) - len(modified)}",
        "═" * 70,
    ]
    
    if added:
        summary_lines.append(f"\n➕ ADDED ({len(added)}):")
        for num in sorted(added):
            part = current_dict[num]
            summary_lines.append(f"  + {num}: {part.part_name}")
    
    if removed:
        summary_lines.append(f"\n➖ REMOVED ({len(removed)}):")
        for num in sorted(removed):
            part = baseline_dict[num]
            summary_lines.append(f"  - {num}: {part.part_name}")
            
    if modified:
        summary_lines.append(f"\n📝 MODIFIED ({len(modified)}):")
        for item in modified:
            num = item['part_number']
            summary_lines.append(f"  ~ {num}:")
            for field, (old_val, new_val) in item['changes'].items():
                summary_lines.append(f"      {field}: '{old_val}' → '{new_val}'")
    
    summary = "\n".join(summary_lines)
    print(summary)
    
    return {
        "added": [current_dict[n] for n in added],
        "removed": [baseline_dict[n] for n in removed],
        "modified": modified,
        "unchanged": len(common) - len(modified),
        "summary": summary
    }


# ============================================================================
# HOW TO USE
# ============================================================================
"""
1. Save this file in: productivity_app/data_pipeline/reports/

2. Run from anywhere:
   from productivity_app.data_pipeline.reports import compare_parts
   from productivity_app.data_pipeline.registry import registry
   
   report = registry.get_report("Compare Two Parts Lists")
   result = report.generate(
       old_parts="path/to/parts_v1.csv",
       new_parts="path/to/parts_v2.csv"
   )
   
3. The system automatically:
   - Reads both CSV files
   - Converts them to Part objects
   - Validates schemas
   - Passes to your function
   
4. Your CSV files just need columns: part_name, part_number
   (optional: quantity, manufacturer, etc.)
"""
