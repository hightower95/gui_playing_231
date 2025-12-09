"""
Tests for connector filter engine

Tests the core filtering logic used by the connector lookup feature.
These tests verify that filtering works correctly without Qt dependencies.
"""
import pytest
import pandas as pd
from productivity_app.productivity_core.connector.Lookup.filter_engine import (
    apply_text_search,
    apply_column_filter,
    apply_all_filters,
    get_unique_values,
    get_available_filter_options,
)


class TestTextSearch:
    """Tests for text search functionality"""

    def test_single_term_finds_match_in_any_column(self, connector_df):
        """Single search term should match any column"""
        result = apply_text_search(connector_df, 'D38999')

        # Should find all D38999 family connectors
        assert len(result) == 3
        assert all(result['Family'] == 'D38999')

    def test_single_term_case_insensitive(self, connector_df):
        """Search should be case-insensitive"""
        result_upper = apply_text_search(connector_df, 'ALUMINUM')
        result_lower = apply_text_search(connector_df, 'aluminum')
        result_mixed = apply_text_search(connector_df, 'AluMiNum')

        assert len(result_upper) == len(result_lower) == len(result_mixed)
        assert len(result_upper) == 4  # 4 aluminum connectors

    def test_comma_separated_terms_or_logic(self, connector_df):
        """Comma-separated terms should use OR logic"""
        # Search for D38999 OR VG family
        result = apply_text_search(connector_df, 'D38999, VG')

        # Should find all D38999 (3) + VG (2) = 5 connectors
        assert len(result) == 5
        families = result['Family'].unique().tolist()
        assert 'D38999' in families
        assert 'VG' in families

    def test_comma_separated_with_whitespace(self, connector_df):
        """Comma-separated terms should handle various whitespace"""
        result1 = apply_text_search(connector_df, 'D38999,VG')
        result2 = apply_text_search(connector_df, 'D38999, VG')
        result3 = apply_text_search(connector_df, 'D38999 , VG')
        result4 = apply_text_search(connector_df, '  D38999  ,  VG  ')

        assert len(result1) == len(result2) == len(result3) == len(result4)

    def test_empty_search_returns_all(self, connector_df):
        """Empty search text should return all rows"""
        result1 = apply_text_search(connector_df, '')
        result2 = apply_text_search(connector_df, '   ')
        result3 = apply_text_search(connector_df, None)

        assert len(result1) == len(connector_df)
        assert len(result2) == len(connector_df)
        # None should also return all

    def test_no_match_returns_empty(self, connector_df):
        """Search with no matches should return empty dataframe"""
        result = apply_text_search(connector_df, 'NONEXISTENT12345')

        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_partial_match_works(self, connector_df):
        """Partial text should match"""
        result = apply_text_search(connector_df, '26WA')

        # Should find part numbers containing '26WA'
        assert len(result) > 0
        for part_num in result['Part Number']:
            assert '26WA' in part_num.upper()

    def test_searches_all_columns(self, connector_df):
        """Search should check all columns, not just Part Number"""
        # Search for a material
        result = apply_text_search(connector_df, 'Composite')
        assert len(result) == 2  # VG composite and EN composite

        # Search for a status
        result = apply_text_search(connector_df, 'Obsolete')
        assert len(result) == 1


class TestColumnFilter:
    """Tests for column-based filtering"""

    def test_single_value_filter(self, connector_df):
        """Single value filter should work"""
        result = apply_column_filter(connector_df, 'Family', ['D38999'])

        assert len(result) == 3
        assert all(result['Family'] == 'D38999')

    def test_multiple_values_filter(self, connector_df):
        """Multiple values should use OR logic"""
        result = apply_column_filter(connector_df, 'Family', ['D38999', 'VG'])

        assert len(result) == 5
        families = result['Family'].unique().tolist()
        assert 'D38999' in families
        assert 'VG' in families

    def test_empty_values_returns_all(self, connector_df):
        """Empty filter list should return all rows"""
        result = apply_column_filter(connector_df, 'Family', [])

        assert len(result) == len(connector_df)

    def test_invalid_column_returns_all(self, connector_df):
        """Invalid column name should return all rows (graceful handling)"""
        result = apply_column_filter(
            connector_df, 'NonExistentColumn', ['value'])

        assert len(result) == len(connector_df)

    def test_filters_out_empty_strings(self, connector_df):
        """Empty strings in filter values should be ignored"""
        result = apply_column_filter(
            connector_df, 'Family', ['D38999', '', '  '])

        assert len(result) == 3
        assert all(result['Family'] == 'D38999')

    def test_no_match_returns_empty(self, connector_df):
        """Filter with no matches should return empty dataframe"""
        result = apply_column_filter(connector_df, 'Family', ['NONEXISTENT'])

        assert len(result) == 0


class TestCombinedFilters:
    """Tests for applying multiple filters together"""

    def test_text_and_column_filter(self, connector_df):
        """Text search combined with column filter"""
        filters = {
            'search_text': 'Plug',
            'standard': ['D38999'],
        }
        result = apply_all_filters(connector_df, filters)

        # Should be D38999 family plugs only
        assert all(result['Family'] == 'D38999')
        assert all('Plug' in st for st in result['Shell Type'])

    def test_multiple_column_filters(self, connector_df):
        """Multiple column filters should all apply (AND logic)"""
        filters = {
            'standard': ['D38999'],
            'material': ['Aluminum'],
        }
        result = apply_all_filters(connector_df, filters)

        # D38999 AND Aluminum
        assert len(result) == 2  # Two D38999 aluminum connectors
        assert all(result['Family'] == 'D38999')
        assert all(result['Material'] == 'Aluminum')

    def test_all_filters_at_once(self, connector_df):
        """All filter types applied simultaneously"""
        filters = {
            'search_text': 'D38999',
            'standard': ['D38999'],
            'shell_type': ['26 - Plug'],
            'material': ['Aluminum'],
        }
        result = apply_all_filters(connector_df, filters)

        # Very specific filter
        assert len(result) == 2  # Two matching connectors
        assert all(result['Family'] == 'D38999')
        assert all(result['Shell Type'] == '26 - Plug')
        assert all(result['Material'] == 'Aluminum')

    def test_empty_filters_returns_all(self, connector_df):
        """Empty filter dict should return all rows"""
        result = apply_all_filters(connector_df, {})

        assert len(result) == len(connector_df)

    def test_none_df_returns_none(self):
        """None dataframe should return None"""
        result = apply_all_filters(None, {'search_text': 'test'})

        assert result is None

    def test_empty_df_returns_empty(self):
        """Empty dataframe should return empty"""
        empty_df = pd.DataFrame()
        result = apply_all_filters(empty_df, {'search_text': 'test'})

        assert len(result) == 0


class TestFilterOptions:
    """Tests for getting available filter options"""

    def test_get_unique_values(self, connector_df):
        """Should return sorted unique values"""
        families = get_unique_values(connector_df, 'Family')

        assert 'D38999' in families
        assert 'VG' in families
        assert 'MS' in families
        assert families == sorted(families)  # Should be sorted

    def test_get_unique_values_empty_df(self):
        """Empty dataframe should return empty list"""
        empty_df = pd.DataFrame()
        result = get_unique_values(empty_df, 'Family')

        assert result == []

    def test_get_unique_values_invalid_column(self, connector_df):
        """Invalid column should return empty list"""
        result = get_unique_values(connector_df, 'NonExistent')

        assert result == []

    def test_available_options_no_filter(self, connector_df):
        """Without filters, should return all unique values"""
        options = get_available_filter_options(connector_df)

        assert 'D38999' in options['standard']
        assert 'VG' in options['standard']
        assert 'Aluminum' in options['material']
        assert 'Stainless Steel' in options['material']

    def test_available_options_with_filter(self, connector_df):
        """With filter applied, options should reflect filtered data"""
        # Filter to D38999 only
        filters = {'standard': ['D38999']}
        options = get_available_filter_options(connector_df, filters)

        # Materials available for D38999 only
        materials = options['material']
        assert 'Aluminum' in materials
        assert 'Stainless Steel' in materials
        # Composite is not in D38999 family
        assert 'Composite' not in materials


class TestEdgeCases:
    """Tests for edge cases and potential bugs"""

    def test_special_characters_in_search(self, connector_df):
        """Special characters in search should not cause regex errors"""
        # Part numbers contain special chars like / and -
        result = apply_text_search(connector_df, 'D38999/26')

        assert len(result) > 0

    def test_filter_preserves_index(self, connector_df):
        """Filtering should preserve original index for tracking"""
        original_indices = connector_df.index.tolist()
        result = apply_text_search(connector_df, 'D38999')

        # Result indices should be subset of original
        for idx in result.index:
            assert idx in original_indices

    def test_filter_does_not_modify_original(self, connector_df):
        """Filtering should not modify the original dataframe"""
        original_len = len(connector_df)

        apply_text_search(connector_df, 'D38999')
        apply_column_filter(connector_df, 'Family', ['VG'])
        apply_all_filters(connector_df, {'standard': ['MS']})

        # Original should be unchanged
        assert len(connector_df) == original_len

    def test_unicode_in_data(self):
        """Unicode characters should be handled"""
        df = pd.DataFrame([
            {'Part Number': 'PART-001', 'Family': 'Test',
                'Description': 'Mller connector'},
            {'Part Number': 'PART-002', 'Family': 'Test', 'Description': 'Standard'}
        ])

        result = apply_text_search(df, 'Mller')
        assert len(result) == 1
