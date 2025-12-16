"""
Tests for FilterState

Tests:
- Topic selection (single and multi)
- Filter dimension management
- Search text handling
- Sort parameter management
- State queries
- State chaining
"""
import pytest
from productivity_app.productivity_core.tabs.automated_reports.filter_state import FilterState


class TestTopicSelection:
    """Test topic selection operations"""

    def test_select_single_topic(self):
        """Selecting single topic without multi-select clears others"""
        state = FilterState()

        state.select_topic("Topic A", is_multi_select=False)
        assert state.selected_topics == {"Topic A"}

        state.select_topic("Topic B", is_multi_select=False)
        assert state.selected_topics == {"Topic B"}

    def test_select_multiple_topics(self):
        """Multi-select should accumulate topics"""
        state = FilterState()

        state.select_topic("Topic A", is_multi_select=True)
        state.select_topic("Topic B", is_multi_select=True)

        assert state.selected_topics == {"Topic A", "Topic B"}

    def test_toggle_topic_in_multi_select(self):
        """Selecting same topic again in multi-select should deselect"""
        state = FilterState()

        state.select_topic("Topic A", is_multi_select=True)
        assert "Topic A" in state.selected_topics

        state.select_topic("Topic A", is_multi_select=True)
        assert "Topic A" not in state.selected_topics

    def test_deselect_all_topics(self):
        """Should clear all topic selections"""
        state = FilterState()

        state.select_topic("Topic A", is_multi_select=True)
        state.select_topic("Topic B", is_multi_select=True)

        state.deselect_all_topics()

        assert len(state.selected_topics) == 0


class TestFilterDimensions:
    """Test filter dimension management"""

    def test_set_filter_single_dimension(self):
        """Should set filter for a dimension"""
        state = FilterState()

        state.set_filter("project", {"Project A", "Project B"})

        filters = state.active_filters
        assert "project" in filters
        assert filters["project"] == {"Project A", "Project B"}

    def test_set_filter_multiple_dimensions(self):
        """Should handle multiple filter dimensions"""
        state = FilterState()

        state.set_filter("project", {"Project A"})
        state.set_filter("type", {"Report", "Analysis"})

        filters = state.active_filters
        assert len(filters) == 2
        assert "project" in filters
        assert "type" in filters

    def test_set_filter_overwrites_dimension(self):
        """Setting filter again should overwrite previous value"""
        state = FilterState()

        state.set_filter("project", {"Project A"})
        state.set_filter("project", {"Project B"})

        filters = state.active_filters
        assert filters["project"] == {"Project B"}

    def test_set_filter_empty_removes_dimension(self):
        """Setting empty set should remove dimension"""
        state = FilterState()

        state.set_filter("project", {"Project A"})
        state.set_filter("project", set())

        filters = state.active_filters
        assert "project" not in filters

    def test_clear_filters(self):
        """Should clear all filter dimensions"""
        state = FilterState()

        state.set_filter("project", {"Project A"})
        state.set_filter("type", {"Report"})

        state.clear_filters()

        assert len(state.active_filters) == 0

    def test_clear_filters_preserves_topics(self):
        """Clear filters should preserve topic selection"""
        state = FilterState()

        state.select_topic("Topic A", is_multi_select=True)
        state.set_filter("project", {"Project A"})

        state.clear_filters()

        assert len(state.active_filters) == 0
        assert state.selected_topics == {"Topic A"}


class TestSearchText:
    """Test search text management"""

    def test_set_search_text(self):
        """Should set search text"""
        state = FilterState()

        state.set_search("test query")

        assert state._search_text == "test query"

    def test_set_search_overwrites(self):
        """Setting search again should overwrite"""
        state = FilterState()

        state.set_search("first query")
        state.set_search("second query")

        assert state._search_text == "second query"

    def test_set_search_none_clears(self):
        """Setting None should clear search"""
        state = FilterState()

        state.set_search("test query")
        state.set_search(None)

        assert state._search_text is None

    def test_set_search_empty_string_clears(self):
        """Setting empty string should clear search"""
        state = FilterState()

        state.set_search("test query")
        state.set_search("")

        assert state._search_text is None


class TestSortParameters:
    """Test sort parameter management"""

    def test_default_sort_is_name_ascending(self):
        """Default sort should be by name, ascending"""
        state = FilterState()

        assert state._sort_field == "name"
        assert state._sort_ascending is True

    def test_set_sort_field(self):
        """Should set sort field"""
        state = FilterState()

        state.set_sort("project", True)

        assert state._sort_field == "project"

    def test_set_sort_direction(self):
        """Should set sort direction"""
        state = FilterState()

        state.set_sort("name", False)

        assert state._sort_ascending is False

    def test_set_sort_both_parameters(self):
        """Should set both field and direction"""
        state = FilterState()

        state.set_sort("type", False)

        assert state._sort_field == "type"
        assert state._sort_ascending is False


class TestClearAll:
    """Test complete state clearing"""

    def test_clear_all_removes_everything(self):
        """Should clear topics, filters, and search"""
        state = FilterState()

        # Set everything
        state.select_topic("Topic A", is_multi_select=True)
        state.set_filter("project", {"Project A"})
        state.set_search("test query")

        # Clear all
        state.clear_all()

        assert len(state.selected_topics) == 0
        assert len(state.active_filters) == 0
        assert state._search_text is None

    def test_clear_all_preserves_sort(self):
        """Clear all should preserve sort settings"""
        state = FilterState()

        state.set_sort("project", False)
        state.clear_all()

        # Sort should still be set
        assert state._sort_field == "project"
        assert state._sort_ascending is False


class TestStateQueries:
    """Test state query methods"""

    def test_has_active_filters_false_initially(self):
        """Should return False when no filters"""
        state = FilterState()

        assert state.has_active_filters is False

    def test_has_active_filters_true_with_filters(self):
        """Should return True when filters exist"""
        state = FilterState()

        state.set_filter("project", {"Project A"})

        assert state.has_active_filters is True

    def test_has_active_filters_false_after_clear(self):
        """Should return False after clearing filters"""
        state = FilterState()

        state.set_filter("project", {"Project A"})
        state.clear_filters()

        assert state.has_active_filters is False

    def test_to_query_dict(self):
        """Should generate complete query dictionary"""
        state = FilterState()

        state.select_topic("Topic A", is_multi_select=True)
        state.set_filter("project", {"Project A"})
        state.set_search("test")
        state.set_sort("type", False)

        query = state.to_query_dict()

        assert "topics" in query
        assert "project" in query
        assert "search_text" in query
        assert "sort_by" in query
        assert "ascending" in query

        assert query["topics"] == ["Topic A"]
        assert query["project"] == ["Project A"]
        assert query["search_text"] == "test"
        assert query["sort_by"] == "type"
        assert query["ascending"] is False

    def test_to_query_dict_with_defaults(self):
        """Query dict should handle empty/default values"""
        state = FilterState()

        query = state.to_query_dict()

        assert query["topics"] is None
        assert query["search_text"] is None
        assert query["sort_by"] == "name"
        assert query["ascending"] is True


class TestMethodChaining:
    """Test that methods support chaining"""

    def test_select_topic_returns_self(self):
        """select_topic should return self for chaining"""
        state = FilterState()

        result = state.select_topic("Topic A")

        assert result is state

    def test_set_filter_returns_self(self):
        """set_filter should return self for chaining"""
        state = FilterState()

        result = state.set_filter("project", {"Project A"})

        assert result is state

    def test_set_search_returns_self(self):
        """set_search should return self for chaining"""
        state = FilterState()

        result = state.set_search("test")

        assert result is state

    def test_set_sort_returns_self(self):
        """set_sort should return self for chaining"""
        state = FilterState()

        result = state.set_sort("name", True)

        assert result is state

    def test_chaining_multiple_operations(self):
        """Should be able to chain multiple operations"""
        state = FilterState()

        state.select_topic("Topic A", True) \
             .set_filter("project", {"Project A"}) \
             .set_search("test") \
             .set_sort("type", False)

        assert "Topic A" in state.selected_topics
        assert state.active_filters["project"] == {"Project A"}
        assert state._search_text == "test"
        assert state._sort_field == "type"
        assert state._sort_ascending is False


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_filter_set_removes_dimension(self):
        """Empty set should remove dimension, not add empty entry"""
        state = FilterState()

        state.set_filter("project", set())

        assert "project" not in state.active_filters

    def test_select_same_topic_twice_single_select(self):
        """Selecting same topic twice in single-select mode"""
        state = FilterState()

        state.select_topic("Topic A", is_multi_select=False)
        state.select_topic("Topic A", is_multi_select=False)

        assert state.selected_topics == {"Topic A"}

    def test_deselect_nonexistent_topic_in_multi_select(self):
        """Toggling nonexistent topic in multi-select should add it"""
        state = FilterState()

        state.select_topic("Topic A", is_multi_select=True)

        # Should just have Topic A
        assert state.selected_topics == {"Topic A"}

    def test_multiple_clear_operations(self):
        """Multiple clears should not cause errors"""
        state = FilterState()

        state.clear_filters()
        state.clear_filters()
        state.clear_all()
        state.clear_all()

        # Should just be empty
        assert len(state.selected_topics) == 0
        assert len(state.active_filters) == 0

    def test_query_dict_immutability(self):
        """Modifying query dict should not affect state"""
        state = FilterState()

        state.set_filter("project", {"Project A"})

        query = state.to_query_dict()
        query["project"].append("Project B")

        # State should be unchanged
        assert state.active_filters["project"] == {"Project A"}
