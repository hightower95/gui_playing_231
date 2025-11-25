"""
Connector Lookup Filter Redux State Manager

Centralized state management for connector lookup filters.
Ensures consistent filter state across multiple UI components.

Tracks both:
- Filter state: which filters are currently active
- Available options: what filter options are available for each filter type
"""
from PySide6.QtCore import QObject, Signal
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from datetime import datetime


class FilterCommand(Enum):
    """Enum for tracking which component initiated a filter change"""
    SEARCH_BOX = "search_box"
    MULTISELECT = "multiselect"
    CLEAR_BUTTON = "clear_button"
    RESET_BUTTON = "reset_button"
    RECENT_SEARCH = "recent_search"
    STANDARD_CHANGED = "standard_changed"
    EXTERNAL = "external"


@dataclass
class FilterState:
    """Immutable representation of the current filter state"""
    search_text: str = ""
    standard: List[str] = field(default_factory=list)
    shell_type: List[str] = field(default_factory=list)
    material: List[str] = field(default_factory=list)
    shell_size: List[str] = field(default_factory=list)
    insert_arrangement: List[str] = field(default_factory=list)
    socket_type: List[str] = field(default_factory=list)
    keying: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert filter state to dictionary"""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FilterState':
        """Create FilterState from dictionary"""
        return FilterState(
            search_text=data.get('search_text', ''),
            standard=data.get('standard', []),
            shell_type=data.get('shell_type', []),
            material=data.get('material', []),
            shell_size=data.get('shell_size', []),
            insert_arrangement=data.get('insert_arrangement', []),
            socket_type=data.get('socket_type', []),
            keying=data.get('keying', [])
        )

    def is_empty(self) -> bool:
        """Check if all filters are empty"""
        return all([
            not self.search_text.strip(),
            not self.standard,
            not self.shell_type,
            not self.material,
            not self.shell_size,
            not self.insert_arrangement,
            not self.socket_type,
            not self.keying
        ])

    def merge(self, partial_update: Dict[str, Any]) -> 'FilterState':
        """Create new FilterState by merging partial update"""
        current_dict = self.to_dict()
        current_dict.update(partial_update)
        return FilterState.from_dict(current_dict)


class ConnectorFilterRedux(QObject):
    """
    Redux-style state manager for connector lookup filters.
    
    Provides centralized, predictable state management for filter operations.
    All filter updates flow through the reducer for consistency and debugging.
    """

    # Signals
    filters_changed = Signal(FilterState, FilterCommand, dict)  # new_state, command, metadata
    filters_cleared = Signal()
    filter_history_changed = Signal(list)  # List of (timestamp, command, state) tuples

    def __init__(self):
        """Initialize the filter redux state manager"""
        super().__init__()
        
        # Current filter state (immutable)
        self._current_state = FilterState()
        
        # Available filter options for each filter type
        self._available_options: Dict[str, List[str]] = {
            'standard': [],
            'shell_type': [],
            'material': [],
            'shell_size': [],
            'insert_arrangement': [],
            'socket_type': [],
            'keying': []
        }
        
        # History for undo/redo
        self._history_stack: List[tuple] = []  # (timestamp, command, state)
        self._redo_stack: List[tuple] = []     # For redo functionality
        self._max_history = 50  # Keep last 50 states
        
    @property
    def state(self) -> FilterState:
        """Get current filter state (read-only)"""
        return self._current_state
    
    def update_filters(self, 
                      filters_to_set: Dict[str, Any],
                      command: FilterCommand = FilterCommand.EXTERNAL,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update filters through the reducer.
        
        Args:
            filters_to_set: Dict of filter keys and values to update
            command: Which component initiated this change
            metadata: Optional metadata about the change (e.g., {"source": "user_click"})
            
        Returns:
            True if state changed, False if no change occurred
        """
        if metadata is None:
            metadata = {}
        
        # Create new state by merging update
        new_state = self._current_state.merge(filters_to_set)
        
        # Check if state actually changed
        if new_state.to_dict() == self._current_state.to_dict():
            return False
        
        # Store old state in history
        timestamp = datetime.now().isoformat()
        self._history_stack.append((timestamp, command, self._current_state))
        
        # Limit history size
        if len(self._history_stack) > self._max_history:
            self._history_stack.pop(0)
        
        # Clear redo stack when new change made
        self._redo_stack.clear()
        
        # Update current state
        self._current_state = new_state
        
        # Emit signal with new state
        self.filters_changed.emit(new_state, command, metadata)
        self.filter_history_changed.emit(self._get_history_summary())
        
        return True
    
    def clear_filters(self, 
                     include_keys: Optional[List[str]] = None,
                     command: FilterCommand = FilterCommand.CLEAR_BUTTON) -> bool:
        """
        Clear specific filters (only those listed in include_keys).
        
        Args:
            include_keys: List of filter keys to clear (defaults to all filter types)
            command: Which component initiated this change
            
        Returns:
            True if state changed, False if already cleared
        """
        # If no keys specified, clear all filter types
        if include_keys is None:
            include_keys = [
                'standard', 'shell_type', 'material', 'shell_size',
                'insert_arrangement', 'socket_type', 'keying'
            ]
        
        # Determine what to clear
        filters_to_clear = {}
        current_dict = self._current_state.to_dict()
        
        for key in include_keys:
            if key in current_dict:
                # Clear to empty list or empty string depending on type
                filters_to_clear[key] = [] if isinstance(current_dict[key], list) else ""
        
        # Update filters
        result = self.update_filters(filters_to_clear, command)
        
        if result:
            self.filters_cleared.emit()
        
        return result
    
    def reset_all_filters(self) -> bool:
        """Reset all filters to empty state"""
        new_state = FilterState()
        
        if new_state.to_dict() == self._current_state.to_dict():
            return False
        
        # Store old state
        timestamp = datetime.now().isoformat()
        self._history_stack.append((timestamp, FilterCommand.RESET_BUTTON, self._current_state))
        self._redo_stack.clear()
        
        if len(self._history_stack) > self._max_history:
            self._history_stack.pop(0)
        
        self._current_state = new_state
        
        self.filters_changed.emit(new_state, FilterCommand.RESET_BUTTON, {})
        self.filters_cleared.emit()
        self.filter_history_changed.emit(self._get_history_summary())
        
        return True
    
    def undo(self) -> Optional[FilterState]:
        """Undo last filter change"""
        if not self._history_stack:
            return None
        
        # Move current state to redo stack
        timestamp = datetime.now().isoformat()
        self._redo_stack.append((timestamp, FilterCommand.EXTERNAL, self._current_state))
        
        # Restore previous state
        timestamp, command, previous_state = self._history_stack.pop()
        self._current_state = previous_state
        
        self.filters_changed.emit(self._current_state, FilterCommand.EXTERNAL, {"action": "undo"})
        self.filter_history_changed.emit(self._get_history_summary())
        
        return self._current_state
    
    def redo(self) -> Optional[FilterState]:
        """Redo last undone filter change"""
        if not self._redo_stack:
            return None
        
        # Move current state to history
        timestamp = datetime.now().isoformat()
        self._history_stack.append((timestamp, FilterCommand.EXTERNAL, self._current_state))
        
        # Restore redo state
        timestamp, command, redo_state = self._redo_stack.pop()
        self._current_state = redo_state
        
        self.filters_changed.emit(self._current_state, FilterCommand.EXTERNAL, {"action": "redo"})
        self.filter_history_changed.emit(self._get_history_summary())
        
        return self._current_state
    
    def get_filter_value(self, key: str) -> Any:
        """Get a specific filter value"""
        return getattr(self._current_state, key, None)
    
    def set_filter_value(self, key: str, value: Any, 
                        command: FilterCommand = FilterCommand.EXTERNAL) -> bool:
        """Set a single filter value"""
        return self.update_filters({key: value}, command)
    
    def export_state(self) -> str:
        """Export current filter state as JSON string"""
        return json.dumps(self._current_state.to_dict(), indent=2)
    
    def import_state(self, json_str: str, 
                    command: FilterCommand = FilterCommand.EXTERNAL) -> bool:
        """Import filter state from JSON string"""
        try:
            data = json.loads(json_str)
            return self.update_filters(data, command, {"action": "import"})
        except json.JSONDecodeError:
            return False
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self._history_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return len(self._redo_stack) > 0
    
    def get_history(self) -> List[tuple]:
        """Get full history stack"""
        return [(ts, cmd.value, state.to_dict()) for ts, cmd, state in self._history_stack]
    
    def update_available_options(self, options_update: Dict[str, List[str]]) -> None:
        """
        Update the available filter options for one or more filter types.
        
        Args:
            options_update: Dict mapping filter keys to lists of available options
                           e.g., {'material': ['iron', 'copper', 'aluminum']}
        """
        for key, values in options_update.items():
            if key in self._available_options:
                self._available_options[key] = list(values)  # Create copy of list
    
    def get_available_options(self, filter_key: str) -> List[str]:
        """
        Get available options for a specific filter type.
        
        Args:
            filter_key: The filter key (e.g., 'material', 'standard')
            
        Returns:
            List of available options, or empty list if filter key not found
        """
        return self._available_options.get(filter_key, [])
    
    def get_all_available_options(self) -> Dict[str, List[str]]:
        """Get all available options for all filter types"""
        return dict(self._available_options)
    
    def get_filter_state(self, filter_key: str) -> Any:
        """
        Get the current state for a specific filter.
        Alias for get_filter_value() for clarity.
        
        Args:
            filter_key: The filter key (e.g., 'material', 'standard')
            
        Returns:
            The current value of the filter
        """
        return self.get_filter_value(filter_key)
    
    def get_all_filter_states(self) -> Dict[str, Any]:
        """Get all current filter states"""
        return self._current_state.to_dict()
    
    def _get_history_summary(self) -> List[tuple]:
        """Get history summary for signals"""
        return [(ts, cmd.value) for ts, cmd, _ in self._history_stack[-10:]]  # Last 10 items


# Example usage documentation
"""
USAGE EXAMPLES:

1. Initialize Redux and populate available options:
    redux = ConnectorFilterRedux()
    redux.update_available_options({
        'material': ['iron', 'copper', 'aluminum', 'steel'],
        'standard': ['D38999', 'VG95234', 'MIL-DTL']
    })

2. Update filter state:
    redux.update_filters(
        {'material': ['copper', 'aluminum']},
        command=FilterCommand.MULTISELECT
    )

3. Query current state and available options:
    current_filters = redux.get_all_filter_states()
    # {'search_text': '', 'material': ['copper', 'aluminum'], ...}
    
    available_materials = redux.get_available_options('material')
    # ['iron', 'copper', 'aluminum', 'steel']
    
    selected_materials = redux.get_filter_state('material')
    # ['copper', 'aluminum']

4. Clear specific filters (keep search text):
    redux.clear_filters(include_keys=['standard', 'shell_type'])

5. Clear all filters:
    redux.clear_filters()  # include_keys defaults to all filter types

6. Reset completely:
    redux.reset_all_filters()

7. Undo/Redo:
    if redux.can_undo():
        redux.undo()
    
    if redux.can_redo():
        redux.redo()

8. Connect to View:
    redux.filters_changed.connect(
        lambda state, cmd, meta: on_filters_changed(state)
    )
    redux.filters_cleared.connect(lambda: on_filters_cleared())

9. Export/Import State:
    state_json = redux.export_state()
    # ... later ...
    redux.import_state(state_json)

10. Complete workflow example:
    # Initialize
    redux = ConnectorFilterRedux()
    redux.update_available_options({
        'material': ['iron', 'copper'],
        'standard': ['D38999', 'VG']
    })
    
    # User selects filters
    redux.update_filters(
        {'material': ['copper']},
        command=FilterCommand.MULTISELECT
    )
    
    # Query what's selected and what's available
    all_states = redux.get_all_filter_states()
    selected = redux.get_filter_state('material')  # ['copper']
    available = redux.get_available_options('material')  # ['iron', 'copper']
    
    # Undo if needed
    redux.undo()
    
    # Clear specific filters
    redux.clear_filters(include_keys=['material'])
"""
