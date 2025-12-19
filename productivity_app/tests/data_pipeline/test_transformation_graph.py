"""
Tests for the transformation graph system that routes data from primitives 
(FilePath, QueryID) through transformers to report parameters.
"""
import pytest
from productivity_app.data_pipeline.parameters import Variables
from productivity_app.data_pipeline.parameters.input_parameters import PrimitiveParameter, CollectedParameter
from productivity_app.data_pipeline.pipeline_graph import (
    TransformationStep,
    TransformationPath,
    TransformationGraph
)


# Create test-only parameters
QueryID = PrimitiveParameter(
    name='query_id',
    description='Database query identifier',
    title='Query ID'
)

ComparisonResult = CollectedParameter(
    name='comparison_result',
    description='Comparison analysis result',
    title='Comparison Result'
)


# Mock transformation functions for testing
def mock_csv_collector(filepath):
    """FilePath(CSV) -> DataFrame"""
    return {"type": "dataframe", "source": "csv"}


def mock_excel_collector(filepath):
    """FilePath(XLSX) -> DataFrame"""
    return {"type": "dataframe", "source": "excel"}


def mock_df_to_parts(dataframe):
    """DataFrame -> PartsList"""
    return {"type": "parts_list", "from": dataframe}


def mock_df_to_street_price(dataframe):
    """DataFrame -> StreetPriceList"""
    return {"type": "street_price_list", "from": dataframe}


def mock_parts_to_comparison(parts_list):
    """PartsList -> ComparisonResult"""
    return {"type": "comparison", "from": parts_list}


class TestTransformationGraph:
    """Test suite for transformation graph pathfinding"""

    @pytest.fixture
    def empty_graph(self):
        """Empty graph for testing"""
        return TransformationGraph()

    @pytest.fixture
    def basic_graph(self):
        """Graph with single route: FilePath -> DataFrame -> PartsList"""
        graph = TransformationGraph()

        # Add CSV collector
        graph.add_collector(
            name="CSVCollector",
            func=mock_csv_collector,
            inputs=[Variables.FilePath],
            outputs=[Variables.DataFrame]
        )

        # Add DataFrame to PartsList transformer
        graph.add_transformer(
            name="DataFrameToPartsList",
            func=mock_df_to_parts,
            input_type=Variables.DataFrame,
            output_type=Variables.PartsList
        )

        return graph

    @pytest.fixture
    def multi_path_graph(self):
        """Graph with multiple routes to same target"""
        graph = TransformationGraph()

        # Two collectors: CSV and Excel
        graph.add_collector(
            name="CSVCollector",
            func=mock_csv_collector,
            inputs=[Variables.FilePath],
            outputs=[Variables.DataFrame]
        )
        graph.add_collector(
            name="ExcelCollector",
            func=mock_excel_collector,
            inputs=[Variables.FilePath],
            outputs=[Variables.DataFrame]
        )

        # Transformer: DataFrame -> PartsList
        graph.add_transformer(
            name="DataFrameToPartsList",
            func=mock_df_to_parts,
            input_type=Variables.DataFrame,
            output_type=Variables.PartsList
        )

        return graph

    @pytest.fixture
    def complex_graph(self):
        """Graph with multiple routes of different lengths"""
        graph = TransformationGraph()

        # Collector: FilePath -> DataFrame
        graph.add_collector(
            name="CSVCollector",
            func=mock_csv_collector,
            inputs=[Variables.FilePath],
            outputs=[Variables.DataFrame]
        )

        # Transformer chain: DataFrame -> PartsList -> ComparisonResult
        graph.add_transformer(
            name="DataFrameToPartsList",
            func=mock_df_to_parts,
            input_type=Variables.DataFrame,
            output_type=Variables.PartsList
        )
        graph.add_transformer(
            name="PartsListToComparison",
            func=mock_parts_to_comparison,
            input_type=Variables.PartsList,
            output_type=ComparisonResult
        )

        return graph

    # ==================== Test 1: Single Route Available ====================

    def test_single_route_found(self, basic_graph):
        """Test finding a single transformation route from FilePath to PartsList"""
        paths = basic_graph.find_all_paths(
            source=Variables.FilePath,
            target=Variables.PartsList
        )

        assert len(paths) == 1, "Should find exactly one path"

        path = paths[0]
        assert path.source_type.matches(Variables.FilePath)
        assert path.target_type.matches(Variables.PartsList)
        assert path.length == 2, "Path should have 2 steps: collector + transformer"

        # Verify steps
        assert path.steps[0].name == "CSVCollector"
        assert path.steps[0].step_type == "collector"
        assert path.steps[1].name == "DataFrameToPartsList"
        assert path.steps[1].step_type == "transformer"

    def test_single_route_execution(self, basic_graph):
        """Test executing a single transformation path"""
        paths = basic_graph.find_all_paths(
            source=Variables.FilePath,
            target=Variables.PartsList
        )

        path = paths[0]
        result = path.execute("fake_file.csv")

        # Should execute: csv_collector -> df_to_parts
        assert result["type"] == "parts_list"
        assert result["from"]["type"] == "dataframe"
        assert result["from"]["source"] == "csv"

    # ==================== Test 2: No Routes Available ====================

    def test_no_route_to_unreachable_target(self, basic_graph):
        """Test that no paths are found for unreachable target type"""
        paths = basic_graph.find_all_paths(
            source=Variables.FilePath,
            target=Variables.StreetPriceList  # Not in graph
        )

        assert len(paths) == 0, "Should find no paths to unreachable target"

    def test_no_route_from_invalid_source(self, basic_graph):
        """Test that no paths are found from invalid source"""
        paths = basic_graph.find_all_paths(
            source=QueryID,  # Not a primitive in this graph
            target=Variables.PartsList
        )

        assert len(paths) == 0, "Should find no paths from non-existent source"

    def test_empty_graph_no_routes(self, empty_graph):
        """Test that empty graph returns no routes"""
        paths = empty_graph.find_all_paths(
            source=Variables.FilePath,
            target=Variables.PartsList
        )

        assert len(paths) == 0, "Empty graph should have no paths"

    # ==================== Test 3: Duplicate Step Detection ====================

    def test_no_duplicate_steps_in_path(self, complex_graph):
        """Test that paths never contain the same step twice (loop prevention)"""
        paths = complex_graph.find_all_paths(
            source=Variables.FilePath,
            target=ComparisonResult
        )

        for path in paths:
            step_names = [step.name for step in path.steps]
            unique_steps = set(step_names)
            assert len(step_names) == len(unique_steps), \
                f"Path contains duplicate steps: {step_names}"

    def test_loop_prevention_with_cycle(self):
        """Test that graph prevents infinite loops when cycles exist"""
        graph = TransformationGraph()

        # Create a cycle: A -> B -> C -> A
        graph.add_transformer("AtoB", lambda x: x,
                              Variables.DataFrame, Variables.PartsList)
        graph.add_transformer("BtoC", lambda x: x,
                              Variables.PartsList, Variables.StreetPriceList)
        graph.add_transformer("CtoA", lambda x: x,
                              Variables.StreetPriceList, Variables.DataFrame)

        # Should not infinite loop
        paths = graph.find_all_paths(
            source=Variables.DataFrame,
            target=Variables.StreetPriceList,
            max_depth=10
        )

        # Should find the direct path A -> B -> C
        assert len(paths) == 1
        assert paths[0].length == 2

    # ==================== Test 4: Pruning Slower Routes ====================

    def test_multiple_paths_sorted_by_length(self, complex_graph):
        """Test that multiple paths to same target are sorted shortest-first"""
        # Add a longer alternative route
        complex_graph.add_transformer(
            name="DataFrameToStreetPrice",
            func=mock_df_to_street_price,
            input_type=Variables.DataFrame,
            output_type=Variables.StreetPriceList
        )
        complex_graph.add_transformer(
            name="StreetPriceToPartsList",
            func=lambda x: x,
            input_type=Variables.StreetPriceList,
            output_type=Variables.PartsList
        )

        paths = complex_graph.find_all_paths(
            source=Variables.FilePath,
            target=Variables.PartsList
        )

        # Should find 2 paths:
        # Path 1 (length 2): FilePath -> DataFrame -> PartsList
        # Path 2 (length 3): FilePath -> DataFrame -> StreetPrice -> PartsList
        assert len(paths) == 2

        # Verify sorted by length
        assert paths[0].length < paths[1].length
        assert paths[0].length == 2
        assert paths[1].length == 3

    def test_shortest_path_selection(self, complex_graph):
        """Test selecting the shortest path from multiple options"""
        # Add longer alternative
        complex_graph.add_transformer(
            name="DataFrameToStreetPrice",
            func=mock_df_to_street_price,
            input_type=Variables.DataFrame,
            output_type=Variables.StreetPriceList
        )
        complex_graph.add_transformer(
            name="StreetPriceToPartsList",
            func=lambda x: x,
            input_type=Variables.StreetPriceList,
            output_type=Variables.PartsList
        )

        paths = complex_graph.find_all_paths(
            source=Variables.FilePath,
            target=Variables.PartsList
        )

        # First path should be shortest
        shortest = paths[0]
        assert shortest.length == 2
        assert shortest.steps[0].name == "CSVCollector"
        assert shortest.steps[1].name == "DataFrameToPartsList"

    def test_prune_longer_paths_from_same_primitive(self, multi_path_graph):
        """Test that when multiple collectors exist, all paths have same length"""
        paths = multi_path_graph.find_all_paths(
            source=Variables.FilePath,
            target=Variables.PartsList
        )

        # Both CSV and Excel collectors should produce paths of length 2
        assert len(paths) == 2
        assert all(p.length == 2 for p in paths)

        # Both should use different collectors but same transformer
        collectors = {p.steps[0].name for p in paths}
        assert collectors == {"CSVCollector", "ExcelCollector"}

        transformers = {p.steps[1].name for p in paths}
        assert transformers == {"DataFrameToPartsList"}

    # ==================== Test 5: Primitive Identification ====================

    def test_primitives_identified_from_collectors(self, basic_graph):
        """Test that primitives are correctly identified from collector inputs"""
        assert Variables.FilePath.get_type_key() in basic_graph.primitives
        assert len(basic_graph.primitives) == 1

    def test_multiple_primitives_identified(self):
        """Test identifying multiple primitive types"""
        graph = TransformationGraph()

        graph.add_collector(
            name="CSVCollector",
            func=mock_csv_collector,
            inputs=[Variables.FilePath],
            outputs=[Variables.DataFrame]
        )
        graph.add_collector(
            name="QueryCollector",
            func=lambda x: x,
            inputs=[QueryID],
            outputs=[Variables.DataFrame]
        )

        assert Variables.FilePath.get_type_key() in graph.primitives
        assert QueryID.get_type_key() in graph.primitives
        assert len(graph.primitives) == 2

    def test_filter_paths_by_primitive(self, multi_path_graph):
        """Test filtering paths that start from specific primitive"""
        all_paths = multi_path_graph.find_all_paths(
            source=Variables.FilePath,
            target=Variables.PartsList
        )

        # All paths should start from FilePath
        for path in all_paths:
            assert path.source_type.matches(Variables.FilePath)
