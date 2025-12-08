"""
Connector Filter Engine - Pure filtering logic extracted for testability

This module contains the core filtering algorithms used by the connector
lookup feature. Extracted from SearchWorker to enable unit testing without
Qt threading dependencies.
"""
import pandas as pd
from typing import Dict, List, Any, Optional


def apply_text_search(df: pd.DataFrame, search_text: str) -> pd.DataFrame:
    """
    Apply text search filter to dataframe.
    
    Supports:
    - Single term: searches all columns for the term
    - Comma-separated terms: OR logic (matches any term)
    
    Args:
        df: Source dataframe to filter
        search_text: Search text (may contain comma-separated terms)
        
    Returns:
        Filtered dataframe
    """
    if not search_text or not search_text.strip():
        return df
    
    search_text = search_text.strip()
    
    # Check if comma-separated (multiple search terms)
    if ',' in search_text:
        # Split by comma and trim each term
        search_terms = [term.strip().lower() for term in search_text.split(',') if term.strip()]
        
        if not search_terms:
            return df
        
        # Create OR condition - match any term
        mask = pd.Series([False] * len(df), index=df.index)
        for term in search_terms:
            term_mask = df.apply(
                lambda row: row.astype(str).str.lower().str.contains(term, regex=False).any(),
                axis=1
            )
            mask = mask | term_mask
        
        return df[mask]
    else:
        # Single search term
        search_text_lower = search_text.lower()
        mask = df.apply(
            lambda row: row.astype(str).str.lower().str.contains(search_text_lower, regex=False).any(),
            axis=1
        )
        return df[mask]


def apply_column_filter(df: pd.DataFrame, column_name: str, values: List[str]) -> pd.DataFrame:
    """
    Apply a column-based filter (exact match from list of values).
    
    Args:
        df: Source dataframe to filter
        column_name: Name of column to filter on
        values: List of acceptable values (rows matching any value are kept)
        
    Returns:
        Filtered dataframe
    """
    if not values:
        return df
    
    # Filter out empty strings
    clean_values = [v for v in values if v and v.strip()]
    
    if not clean_values:
        return df
    
    if column_name not in df.columns:
        return df
    
    return df[df[column_name].isin(clean_values)]


def apply_all_filters(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply all connector filters to a dataframe.
    
    Filter keys:
    - search_text: Free text search across all columns
    - standard: Filter by 'Family' column
    - shell_type: Filter by 'Shell Type' column
    - material: Filter by 'Material' column
    - shell_size: Filter by 'Shell Size' column
    - insert_arrangement: Filter by 'Insert Arrangement' column
    - socket_type: Filter by 'Socket Type' column
    - keying: Filter by 'Keying' column
    
    Args:
        df: Source dataframe to filter
        filters: Dictionary of filter criteria
        
    Returns:
        Filtered dataframe
    """
    if df is None or df.empty:
        return df
    
    filtered_df = df.copy()
    
    # Text search filter
    if filters.get('search_text'):
        filtered_df = apply_text_search(filtered_df, filters['search_text'])
    
    # Column-based filters with their corresponding dataframe column names
    column_filter_mapping = {
        'standard': 'Family',
        'shell_type': 'Shell Type',
        'material': 'Material',
        'shell_size': 'Shell Size',
        'insert_arrangement': 'Insert Arrangement',
        'socket_type': 'Socket Type',
        'keying': 'Keying',
    }
    
    for filter_key, column_name in column_filter_mapping.items():
        if filters.get(filter_key):
            filtered_df = apply_column_filter(filtered_df, column_name, filters[filter_key])
    
    return filtered_df


def get_unique_values(df: pd.DataFrame, column_name: str) -> List[str]:
    """
    Get sorted unique values from a column.
    
    Args:
        df: Source dataframe
        column_name: Column to get unique values from
        
    Returns:
        Sorted list of unique non-null values
    """
    if df is None or df.empty or column_name not in df.columns:
        return []
    
    values = df[column_name].dropna().unique().tolist()
    return sorted([str(v) for v in values])


def get_available_filter_options(
    df: pd.DataFrame,
    current_filters: Optional[Dict[str, Any]] = None
) -> Dict[str, List[str]]:
    """
    Get available filter options based on current data and applied filters.
    
    This enables "cascading" filters where selecting one filter updates
    the available options in other filters.
    
    Args:
        df: Source dataframe
        current_filters: Currently applied filters (to calculate remaining options)
        
    Returns:
        Dictionary mapping filter keys to their available values
    """
    if df is None or df.empty:
        return {
            'standard': [],
            'shell_type': [],
            'material': [],
            'shell_size': [],
            'insert_arrangement': [],
            'socket_type': [],
            'keying': [],
        }
    
    # If filters are applied, get options from filtered data
    if current_filters:
        filtered_df = apply_all_filters(df, current_filters)
    else:
        filtered_df = df
    
    return {
        'standard': get_unique_values(filtered_df, 'Family'),
        'shell_type': get_unique_values(filtered_df, 'Shell Type'),
        'material': get_unique_values(filtered_df, 'Material'),
        'shell_size': get_unique_values(filtered_df, 'Shell Size'),
        'insert_arrangement': get_unique_values(filtered_df, 'Insert Arrangement'),
        'socket_type': get_unique_values(filtered_df, 'Socket Type'),
        'keying': get_unique_values(filtered_df, 'Keying'),
    }
