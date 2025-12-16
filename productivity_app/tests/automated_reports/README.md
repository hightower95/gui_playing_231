# Automated Reports Tests

Comprehensive test suite for the Automated Reports module.

## Test Coverage

### Model Tests (`test_model.py`) - 31 tests

#### Report Generation (3 tests)
- ✅ Generates correct number of reports
- ✅ Reports have valid metadata
- ✅ Report IDs are unique

#### Filter Operations (8 tests)
- ✅ Single project filtering
- ✅ Multiple project filtering (OR logic)
- ✅ Report type filtering
- ✅ Case-insensitive scope filtering
- ✅ Topic filtering
- ✅ Multiple dimension filtering (AND logic)
- ✅ Filter count reduction verification
- ✅ No matches returns empty list

#### Search Functionality (4 tests)
- ✅ Search by name
- ✅ Search by description
- ✅ Case-insensitive search
- ✅ Combined search with filters

#### Sort Operations (5 tests)
- ✅ Sort by name ascending
- ✅ Sort by name descending
- ✅ Sort by type (groups same types)
- ✅ Sort by project (groups same projects)
- ✅ Sort preserves count

#### Data Extraction (4 tests)
- ✅ Get unique projects
- ✅ Get unique report types (sorted)
- ✅ Get unique scopes (sorted)
- ✅ Get unique required inputs (sorted)

#### Topic Hierarchy (3 tests)
- ✅ "All Reports" includes all reports
- ✅ Hierarchy structure format validation
- ✅ Folder counts match children

#### Integration Scenarios (4 tests)
- ✅ Filter then sort workflow
- ✅ Multiple filters progressive reduction
- ✅ 10 reports with specific filters
- ✅ Progressive filtering scenario (real-world usage)

### Filter State Tests (`test_filter_state.py`) - 35 tests

#### Topic Selection (4 tests)
- ✅ Single topic selection clears others
- ✅ Multi-select accumulates topics
- ✅ Toggle topic in multi-select mode
- ✅ Deselect all topics

#### Filter Dimensions (6 tests)
- ✅ Set single dimension filter
- ✅ Set multiple dimension filters
- ✅ Overwrite dimension filter
- ✅ Empty set removes dimension
- ✅ Clear all filters
- ✅ Clear filters preserves topics

#### Search Text (4 tests)
- ✅ Set search text
- ✅ Overwrite search text
- ✅ Clear search with None
- ✅ Clear search with empty string

#### Sort Parameters (4 tests)
- ✅ Default sort is name ascending
- ✅ Set sort field
- ✅ Set sort direction
- ✅ Set both field and direction

#### Clear Operations (2 tests)
- ✅ Clear all removes everything
- ✅ Clear all preserves sort settings

#### State Queries (5 tests)
- ✅ Has active filters (initially false)
- ✅ Has active filters (true with filters)
- ✅ Has active filters (false after clear)
- ✅ Generate complete query dictionary
- ✅ Query dictionary with defaults

#### Method Chaining (5 tests)
- ✅ select_topic returns self
- ✅ set_filter returns self
- ✅ set_search returns self
- ✅ set_sort returns self
- ✅ Chain multiple operations

#### Edge Cases (5 tests)
- ✅ Empty filter set removes dimension
- ✅ Select same topic twice (single-select)
- ✅ Deselect nonexistent topic (multi-select)
- ✅ Multiple clear operations
- ✅ Query dict immutability

## Running Tests

### Run all tests
```bash
pytest productivity_app/productivity_core/tests/ -v
```

### Run specific test file
```bash
pytest productivity_app/productivity_core/tabs/automated_reports/tests/test_model.py -v
pytest productivity_app/productivity_core/tabs/automated_reports/tests/test_filter_state.py -v
```

### Run specific test class
```bash
pytest productivity_app/productivity_core/tabs/automated_reports/tests/test_model.py::TestFilterOperations -v
```

### Run specific test
```bash
pytest productivity_app/productivity_core/tabs/automated_reports/tests/test_model.py::TestFilterOperations::test_filter_by_project_single -v
```

### Run with coverage
```bash
pytest productivity_app/productivity_core/tabs/automated_reports/tests/ --cov=productivity_app/productivity_core/tabs/automated_reports --cov-report=html
```

## Test Scenarios

### Example: Testing Filter Reduction
```python
# With 15 reports generated
# Verify that filtering by a specific project reduces the count appropriately
def test_filter_reduces_count_appropriately(self):
    model = AutomatedReportsModel()
    all_reports = model.get_all_reports()
    
    # Filter by project
    test_project = all_reports[0].project
    filtered = model.filter_reports(project=[test_project])
    
    # Should have fewer reports
    assert len(filtered) < len(all_reports)
```

### Example: Testing Progressive Filtering
```python
# Real-world scenario: user adds filters one by one
def test_progressive_filtering_scenario(self):
    model = AutomatedReportsModel()
    
    # Step 1: Select project
    filtered_1 = model.filter_reports(project=[projects[0]])
    
    # Step 2: Add type filter
    filtered_2 = model.filter_reports(
        project=[projects[0]],
        report_type=[types[0]]
    )
    assert len(filtered_2) <= len(filtered_1)
    
    # Step 3: Add search
    filtered_3 = model.filter_reports(
        project=[projects[0]],
        report_type=[types[0]],
        search_text="Report"
    )
    assert len(filtered_3) <= len(filtered_2)
```

## Key Test Principles

1. **Model tests verify business logic**: Filtering, sorting, search, data extraction
2. **Filter state tests verify state management**: Immutability, chaining, query generation
3. **Integration tests verify workflows**: Real-world user scenarios
4. **All tests are independent**: Each test can run in isolation
5. **Comprehensive coverage**: Edge cases, error conditions, happy paths

## Test Data

- Model generates 15 fake reports by default
- Reports vary by:
  - Project (5 options: Gamma, Alpha, Beta, Delta, Epsilon)
  - Focus Area (6 options: Team Velocity, Resource Allocation, etc.)
  - Report Type (4 options: Report, Analysis, Graph, Assessment)
  - Topics (5 options: Project Management, Team & Resources, etc.)
  - Required Inputs (7 options: Team ID, Sprint Number, etc.)
  - Scope (currently all "local")

## Notes

- FilterState uses **properties** for read access (e.g., `state.selected_topics`, not `state.get_selected_topics()`)
- FilterState returns **self** from all setter methods for chaining
- `to_query_dict()` returns **lists**, not sets (for JSON serialization)
- Multiple filters use **AND logic** between dimensions, **OR logic** within dimensions
