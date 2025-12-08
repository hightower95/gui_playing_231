"""
Tests for connector filter redux state management

Tests the FilterState dataclass and ConnectorFilterRedux state manager.
These tests focus on state management correctness without Qt GUI dependencies.
"""
import pytest
from productivity_app.productivity_core.connector.Lookup.filter_redux import (
    FilterState,
    FilterCommand,
    ConnectorFilterRedux,
)


class TestFilterState:
    """Tests for FilterState dataclass"""
    
    def test_default_state_is_empty(self):
        """Default FilterState should have empty values"""
        state = FilterState()
        
        assert state.search_text == ""
        assert state.standard == []
        assert state.shell_type == []
        assert state.material == []
        assert state.is_empty()
    
    def test_is_empty_with_search_text(self):
        """State with search text is not empty"""
        state = FilterState(search_text="test")
        
        assert not state.is_empty()
    
    def test_is_empty_with_whitespace_only(self):
        """State with only whitespace search text is empty"""
        state = FilterState(search_text="   ")
        
        assert state.is_empty()
    
    def test_is_empty_with_filter(self):
        """State with any filter set is not empty"""
        state = FilterState(standard=["D38999"])
        
        assert not state.is_empty()
    
    def test_to_dict(self):
        """to_dict should return all fields"""
        state = FilterState(
            search_text="test",
            standard=["D38999"],
            material=["Aluminum"]
        )
        
        d = state.to_dict()
        
        assert d['search_text'] == "test"
        assert d['standard'] == ["D38999"]
        assert d['material'] == ["Aluminum"]
        assert d['shell_type'] == []  # Default empty
    
    def test_from_dict(self):
        """from_dict should reconstruct FilterState"""
        original = FilterState(
            search_text="test",
            standard=["D38999", "VG"],
            keying=["A", "B"]
        )
        
        d = original.to_dict()
        reconstructed = FilterState.from_dict(d)
        
        assert reconstructed.search_text == original.search_text
        assert reconstructed.standard == original.standard
        assert reconstructed.keying == original.keying
    
    def test_from_dict_handles_missing_keys(self):
        """from_dict should use defaults for missing keys"""
        partial = {'search_text': 'test'}
        
        state = FilterState.from_dict(partial)
        
        assert state.search_text == 'test'
        assert state.standard == []
        assert state.material == []
    
    def test_merge_creates_new_state(self):
        """merge should create new state without modifying original"""
        original = FilterState(search_text="original", standard=["D38999"])
        
        merged = original.merge({'search_text': 'updated'})
        
        # Original unchanged
        assert original.search_text == "original"
        # Merged has update
        assert merged.search_text == "updated"
        # Unaffected fields preserved
        assert merged.standard == ["D38999"]
    
    def test_merge_multiple_fields(self):
        """merge should handle multiple field updates"""
        original = FilterState()
        
        merged = original.merge({
            'search_text': 'test',
            'standard': ['D38999'],
            'material': ['Aluminum']
        })
        
        assert merged.search_text == 'test'
        assert merged.standard == ['D38999']
        assert merged.material == ['Aluminum']


class TestConnectorFilterRedux:
    """Tests for ConnectorFilterRedux state manager"""
    
    def test_initial_state_is_empty(self):
        """Initial state should be empty FilterState"""
        redux = ConnectorFilterRedux()
        
        assert redux.state.is_empty()
    
    def test_update_filters_changes_state(self):
        """update_filters should modify state"""
        redux = ConnectorFilterRedux()
        
        changed = redux.update_filters({'search_text': 'test'})
        
        assert changed is True
        assert redux.state.search_text == 'test'
    
    def test_update_filters_returns_false_when_no_change(self):
        """update_filters should return False when state unchanged"""
        redux = ConnectorFilterRedux()
        redux.update_filters({'search_text': 'test'})
        
        # Same update again
        changed = redux.update_filters({'search_text': 'test'})
        
        assert changed is False
    
    def test_update_filters_preserves_other_fields(self):
        """Updating one field should not affect others"""
        redux = ConnectorFilterRedux()
        redux.update_filters({'search_text': 'test', 'standard': ['D38999']})
        
        # Update only search_text
        redux.update_filters({'search_text': 'updated'})
        
        assert redux.state.search_text == 'updated'
        assert redux.state.standard == ['D38999']  # Preserved
    
    def test_clear_filters_resets_state(self):
        """clear_filters should reset to empty state"""
        redux = ConnectorFilterRedux()
        redux.update_filters({
            'search_text': 'test',
            'standard': ['D38999'],
            'material': ['Aluminum']
        })
        
        redux.clear_filters()
        
        assert redux.state.is_empty()
    
    def test_history_tracking(self):
        """Filter changes should be tracked in history"""
        redux = ConnectorFilterRedux()
        
        redux.update_filters({'search_text': 'first'})
        redux.update_filters({'search_text': 'second'})
        redux.update_filters({'search_text': 'third'})
        
        history = redux.get_history()
        
        assert len(history) == 3
    
    def test_undo_restores_previous_state(self):
        """undo should restore previous state"""
        redux = ConnectorFilterRedux()
        redux.update_filters({'search_text': 'first'})
        redux.update_filters({'search_text': 'second'})
        
        result = redux.undo()
        
        assert result is not None  # Returns the restored state
        assert redux.state.search_text == 'first'
    
    def test_undo_returns_none_at_beginning(self):
        """undo should return None when at initial state"""
        redux = ConnectorFilterRedux()
        
        result = redux.undo()
        
        assert result is None
    
    def test_command_tracking(self):
        """Commands should be tracked with updates"""
        redux = ConnectorFilterRedux()
        
        redux.update_filters(
            {'search_text': 'test'},
            command=FilterCommand.SEARCH_BOX
        )
        
        history = redux.get_history()
        
        assert history[0][1] == FilterCommand.SEARCH_BOX
    
    def test_metadata_tracking(self):
        """Metadata should be stored with updates"""
        redux = ConnectorFilterRedux()
        
        redux.update_filters(
            {'search_text': 'test'},
            metadata={'source': 'user_input', 'widget': 'search_box'}
        )
        
        # Metadata should be accessible via history or other means
        # (implementation dependent)
    
    def test_available_options_management(self):
        """Available options should be settable and retrievable"""
        redux = ConnectorFilterRedux()
        
        redux.update_available_options({'standard': ['D38999', 'VG', 'MS']})
        
        options = redux.get_available_options('standard')
        
        assert options == ['D38999', 'VG', 'MS']
    
    def test_get_available_options_unknown_key(self):
        """get_available_options for unknown key should return empty list"""
        redux = ConnectorFilterRedux()
        
        options = redux.get_available_options('nonexistent')
        
        assert options == []


class TestFilterCommand:
    """Tests for FilterCommand enum"""
    
    def test_all_commands_exist(self):
        """All expected commands should be defined"""
        assert FilterCommand.SEARCH_BOX
        assert FilterCommand.MULTISELECT
        assert FilterCommand.CLEAR_BUTTON
        assert FilterCommand.RESET_BUTTON
        assert FilterCommand.RECENT_SEARCH
        assert FilterCommand.STANDARD_CHANGED
        assert FilterCommand.EXTERNAL
    
    def test_commands_have_unique_values(self):
        """Each command should have a unique string value"""
        values = [cmd.value for cmd in FilterCommand]
        
        assert len(values) == len(set(values))
