"""
Filter State - Business logic for report filtering

Maintains the current filter state and provides methods for state transitions.
Completely independent of Qt framework for testability.
"""
from typing import Set, Dict, Optional, List


class FilterState:
    """Immutable-style filter state with validation

    Manages:
    - Selected topics (multi-select with OR logic)
    - Active filters by dimension (AND logic)
    - Search text
    - Sort parameters
    """

    def __init__(self):
        """Initialize empty filter state"""
        self._selected_topics: Set[str] = set()
        self._active_filters: Dict[str, Set[str]] = {}
        self._search_text: Optional[str] = None
        self._sort_field: str = "name"
        self._sort_ascending: bool = True

    def select_topic(self, name: str, is_multi_select: bool = False) -> 'FilterState':
        """Select topic, optionally preserving existing selections

        Args:
            name: Topic name to select
            is_multi_select: If False, clears other topics first

        Returns:
            Self for chaining
        """
        if not is_multi_select:
            self._selected_topics.clear()

        # Toggle behavior for multi-select
        if is_multi_select and name in self._selected_topics:
            self._selected_topics.remove(name)
        else:
            self._selected_topics.add(name)

        return self

    def deselect_all_topics(self) -> 'FilterState':
        """Clear all topic selections

        Returns:
            Self for chaining
        """
        self._selected_topics.clear()
        return self

    def set_filter(self, dimension: str, items: Set[str]) -> 'FilterState':
        """Set filter values for a dimension

        Args:
            dimension: Filter dimension (e.g., 'project', 'report_type', 'scope')
            items: Set of selected filter values (empty = clear this dimension)

        Returns:
            Self for chaining
        """
        if items:
            self._active_filters[dimension] = items.copy()
        else:
            self._active_filters.pop(dimension, None)
        return self

    def clear_filters(self) -> 'FilterState':
        """Clear all filter dimensions (but preserve topic selection)

        Returns:
            Self for chaining
        """
        self._active_filters.clear()
        return self

    def clear_all(self) -> 'FilterState':
        """Clear everything - topics, filters, search

        Returns:
            Self for chaining
        """
        self._selected_topics.clear()
        self._active_filters.clear()
        self._search_text = None
        return self

    def set_search(self, text: Optional[str]) -> 'FilterState':
        """Set search text

        Args:
            text: Search text (None or empty string = clear search)

        Returns:
            Self for chaining
        """
        self._search_text = text if text else None
        return self

    def set_sort(self, field: str, ascending: bool) -> 'FilterState':
        """Set sort parameters

        Args:
            field: Sort field ID (e.g., 'name', 'date', 'usage')
            ascending: Sort direction

        Returns:
            Self for chaining
        """
        self._sort_field = field
        self._sort_ascending = ascending
        return self

    def to_query_dict(self) -> Dict:
        """Convert to model query format

        Returns:
            Dict with keys: topics, filters, search_text, sort_by, ascending
        """
        return {
            'topics': list(self._selected_topics) if self._selected_topics else None,
            'project': list(self._active_filters.get('project', set())) if 'project' in self._active_filters else None,
            'focus_area': list(self._active_filters.get('focus_area', set())) if 'focus_area' in self._active_filters else None,
            'report_type': list(self._active_filters.get('report_type', set())) if 'report_type' in self._active_filters else None,
            'scope': list(self._active_filters.get('scope', set())) if 'scope' in self._active_filters else None,
            'search_text': self._search_text,
            'sort_by': self._sort_field,
            'ascending': self._sort_ascending
        }

    @property
    def selected_topics(self) -> Set[str]:
        """Get currently selected topics (read-only copy)"""
        return self._selected_topics.copy()

    @property
    def active_filters(self) -> Dict[str, Set[str]]:
        """Get active filters (read-only copy)"""
        return {k: v.copy() for k, v in self._active_filters.items()}

    @property
    def has_active_filters(self) -> bool:
        """Check if any filters are active"""
        return bool(self._active_filters)

    @property
    def has_active_topics(self) -> bool:
        """Check if any topics are selected"""
        return bool(self._selected_topics)

    @property
    def has_search(self) -> bool:
        """Check if search text is active"""
        return bool(self._search_text)

    @property
    def has_any_criteria(self) -> bool:
        """Check if any filtering criteria is active"""
        return self.has_active_topics or self.has_active_filters or self.has_search

    def get_state_summary(self) -> str:
        """Get human-readable summary of current state (for debugging)"""
        parts = []

        if self._selected_topics:
            parts.append(f"Topics: {sorted(self._selected_topics)}")

        if self._active_filters:
            for dim, items in sorted(self._active_filters.items()):
                parts.append(f"{dim}: {sorted(items)}")

        if self._search_text:
            parts.append(f"Search: '{self._search_text}'")

        parts.append(
            f"Sort: {self._sort_field} ({'↑' if self._sort_ascending else '↓'})")

        return " | ".join(parts) if parts else "No filters active"
