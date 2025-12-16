"""
Type Hints Example - Simple Version (without decorator)

This shows how to use type hints in report functions.
"""
from typing import Dict, Any, Union
from pathlib import Path
import pandas as pd


def generate_parts_summary(input_parts: pd.DataFrame) -> Dict[str, Any]:
    """Generate summary from parts list

    Args:
        input_parts: DataFrame with columns 'Part Name', 'Part Number' (and optional others)

    Returns:
        Summary statistics dictionary containing:
            - total_parts: int - Total number of parts
            - unique_part_numbers: int - Number of unique part numbers
            - part_names: list[str] - List of all part names
            - total_quantity: int (optional, if 'Quantity' column present)

    Example:
        >>> df = pd.DataFrame({
        ...     'Part Name': ['Resistor', 'Capacitor'],
        ...     'Part Number': ['R001', 'C002'],
        ...     'Quantity': [100, 50]
        ... })
        >>> result = generate_parts_summary(df)
        >>> result['total_parts']
        2
    """
    # The parameter's schema automatically validates that
    # 'Part Name' and 'Part Number' columns exist

    summary: Dict[str, Any] = {
        'total_parts': len(input_parts),
        'unique_part_numbers': input_parts['Part Number'].nunique(),
        'part_names': input_parts['Part Name'].tolist()
    }

    if 'Quantity' in input_parts.columns:
        summary['total_quantity'] = int(input_parts['Quantity'].sum())

    return summary


def import_parts_file(parts_file: Union[str, Path]) -> pd.DataFrame:
    """Import parts from file

    Args:
        parts_file: Path to Excel file (string or Path object)

    Returns:
        DataFrame with parts data containing at least 'Part Name' and 'Part Number' columns

    Example:
        >>> df = import_parts_file('parts.xlsx')
        >>> df.columns
        Index(['Part Name', 'Part Number', 'Quantity'], dtype='object')
    """
    # Load the file
    df = pd.read_excel(parts_file)

    # Process...
    return df


def compare_parts_lists(
    list_a: pd.DataFrame,
    list_b: pd.DataFrame,
    include_details: bool = False
) -> Dict[str, Union[list, Dict[str, Any]]]:
    """Compare two parts lists

    Args:
        list_a: First DataFrame with parts
        list_b: Second DataFrame with parts
        include_details: If True, include detailed comparison info

    Returns:
        Dictionary with comparison results:
            - only_in_a: list - Part numbers only in list A
            - only_in_b: list - Part numbers only in list B
            - in_both: list - Part numbers in both lists
            - details: dict (optional) - Additional comparison details

    Example:
        >>> df1 = pd.DataFrame({'Part Number': ['R001', 'C001']})
        >>> df2 = pd.DataFrame({'Part Number': ['R001', 'L001']})
        >>> result = compare_parts_lists(df1, df2)
        >>> result['in_both']
        ['R001']
    """
    parts_a = set(list_a['Part Number'])
    parts_b = set(list_b['Part Number'])

    result: Dict[str, Union[list, Dict[str, Any]]] = {
        'only_in_a': sorted(parts_a - parts_b),
        'only_in_b': sorted(parts_b - parts_a),
        'in_both': sorted(parts_a & parts_b)
    }

    if include_details:
        result['details'] = {
            'total_a': len(parts_a),
            'total_b': len(parts_b),
            'overlap_percentage': len(parts_a & parts_b) / max(len(parts_a), len(parts_b)) * 100
        }

    return result


# Example with more complex types
from typing import List, Optional, Tuple


def filter_parts_by_criteria(
    parts: pd.DataFrame,
    min_quantity: Optional[int] = None,
    part_name_filter: Optional[str] = None,
    exclude_parts: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Filter parts based on multiple criteria

    Args:
        parts: DataFrame with parts data
        min_quantity: Minimum quantity threshold (optional)
        part_name_filter: String to filter part names (optional)
        exclude_parts: List of part numbers to exclude (optional)

    Returns:
        Tuple containing:
            - Filtered DataFrame
            - Statistics dictionary with filter counts

    Example:
        >>> df = pd.DataFrame({
        ...     'Part Name': ['Resistor', 'Capacitor', 'LED'],
        ...     'Part Number': ['R001', 'C001', 'L001'],
        ...     'Quantity': [100, 50, 200]
        ... })
        >>> filtered, stats = filter_parts_by_criteria(df, min_quantity=75)
        >>> len(filtered)
        2
        >>> stats['filtered_out']
        1
    """
    filtered = parts.copy()
    stats: Dict[str, int] = {
        'original_count': len(parts),
        'filtered_out': 0
    }

    if min_quantity is not None:
        mask = filtered['Quantity'] >= min_quantity
        stats['filtered_out'] += (~mask).sum()
        filtered = filtered[mask]

    if part_name_filter is not None:
        mask = filtered['Part Name'].str.contains(part_name_filter, case=False)
        stats['filtered_out'] += (~mask).sum()
        filtered = filtered[mask]

    if exclude_parts is not None:
        mask = ~filtered['Part Number'].isin(exclude_parts)
        stats['filtered_out'] += (~mask).sum()
        filtered = filtered[mask]

    stats['final_count'] = len(filtered)

    return filtered, stats


if __name__ == '__main__':
    # Test the functions
    test_data = pd.DataFrame({
        'Part Name': ['Resistor', 'Capacitor', 'LED'],
        'Part Number': ['R001', 'C002', 'L003'],
        'Quantity': [100, 50, 200]
    })

    print("Testing generate_parts_summary:")
    summary = generate_parts_summary(test_data)
    print(f"  Total parts: {summary['total_parts']}")
    print(f"  Unique parts: {summary['unique_part_numbers']}")

    print("\nTesting compare_parts_lists:")
    test_data2 = pd.DataFrame({
        'Part Number': ['R001', 'D004']
    })
    comparison = compare_parts_lists(test_data, test_data2, include_details=True)
    print(f"  In both: {comparison['in_both']}")
    print(f"  Details: {comparison['details']}")

    print("\nTesting filter_parts_by_criteria:")
    filtered, stats = filter_parts_by_criteria(test_data, min_quantity=75)
    print(f"  Filtered count: {stats['final_count']}")
    print(f"  Filtered out: {stats['filtered_out']}")
