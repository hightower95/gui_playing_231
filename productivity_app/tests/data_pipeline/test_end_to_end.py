"""
End-to-end tests: Collector → Report pipeline
"""
import pytest
from productivity_app.data_pipeline.reports import report
from productivity_app.data_pipeline.data_collectors import data_collector
from productivity_app.data_pipeline.parameters import (
    FilePath,
    CollectedParameter,
    ParameterRegistry
)
from productivity_app.data_pipeline.types_enum import DataTypes


@pytest.fixture(autouse=True)
def clear_registries():
    """Clear registries before each test"""
    from productivity_app.data_pipeline.registry import registry

    # Clear central registry
    registry._reports = {}
    registry._collectors = {}

    yield

    # Clean up after test
    registry._reports = {}
    registry._collectors = {}


def test_simple_collector_to_report():
    """Test basic flow: collector generates data → report consumes it"""

    # Define a CollectedParameter type
    processed_data = CollectedParameter(
        name='processed_data',
        title='Processed Data',
        description='Data processed by collector',
        output_type=DataTypes.PROCESSED_TEXT
    )

    # Register the parameter
    ParameterRegistry.register(processed_data)

    # Create collector
    @data_collector(
        name="Data Processor",
        inputs=[ParameterRegistry.get_by_name('file_path')],
        outputs=[DataTypes.PROCESSED_TEXT]
    )
    def process_file(file_path):
        """Process a file and return data"""
        # Simulate processing
        with open(file_path, 'r') as f:
            content = f.read()
        return {'lines': content.split('\n'), 'length': len(content)}

    # Create report that uses the collected data
    @report(
        title="Data Analysis Report",
        description="Analyzes processed data",
        inputs=[processed_data]
    )
    def analyze_data(processed_data):
        """Generate report from processed data"""
        return f"Analyzed {len(processed_data['lines'])} lines, total length: {processed_data['length']}"

    # Test the flow
    test_file = "test_data.txt"

    # Simulate file creation
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Line 1\nLine 2\nLine 3")
        test_file = f.name

    try:
        # Execute collector
        collected = process_file(test_file)

        # Verify collector output
        assert 'lines' in collected
        assert 'length' in collected
        assert len(collected['lines']) == 3

        # Execute report
        result = analyze_data(collected)

        # Verify report output
        assert "Analyzed 3 lines" in result
        assert "total length:" in result
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_multiple_collectors_to_report():
    """Test report that uses data from multiple collectors"""

    # Define two collected parameter types
    stats_data = CollectedParameter(
        name='file_stats',
        title='File Statistics',
        description='Statistical data from file',
        output_type=DataTypes.FILE_STATS
    )

    content_data = CollectedParameter(
        name='file_content',
        title='File Content',
        description='Content extracted from file',
        output_type=DataTypes.TEXT_DATA
    )

    # Register parameters
    ParameterRegistry.register(stats_data)
    ParameterRegistry.register(content_data)

    # Create first collector - stats
    @data_collector(
        name="File Stats Collector",
        inputs=[ParameterRegistry.get_by_name('file_path')],
        outputs=[DataTypes.FILE_STATS]
    )
    def collect_stats(file_path):
        """Collect file statistics"""
        import os
        size = os.path.getsize(file_path)
        with open(file_path, 'r') as f:
            lines = f.readlines()
        return {
            'size': size,
            'line_count': len(lines),
            'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0
        }

    # Create second collector - content
    @data_collector(
        name="File Content Collector",
        inputs=[ParameterRegistry.get_by_name('file_path')],
        outputs=[DataTypes.TEXT_DATA]
    )
    def collect_content(file_path):
        """Collect file content"""
        with open(file_path, 'r') as f:
            content = f.read()
        return {
            'content': content,
            'words': content.split(),
            'characters': len(content)
        }

    # Create report using both
    @report(
        title="Comprehensive File Report",
        description="Report combining stats and content analysis",
        inputs=[stats_data, content_data]
    )
    def comprehensive_report(file_stats, file_content):
        """Generate comprehensive report"""
        return {
            'summary': f"{file_stats['line_count']} lines, {file_content['characters']} characters, {len(file_content['words'])} words",
            'stats': file_stats,
            'content_preview': file_content['words'][:5] if file_content['words'] else []
        }

    # Test the flow
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("This is a test file.\nIt has multiple lines.\nAnd some content.")
        test_file = f.name

    try:
        # Execute collectors
        stats = collect_stats(test_file)
        content = collect_content(test_file)

        # Verify collectors
        assert stats['line_count'] == 3
        assert 'words' in content

        # Execute report
        result = comprehensive_report(stats, content)

        # Verify report
        assert 'summary' in result
        assert '3 lines' in result['summary']
        assert 'stats' in result
        assert 'content_preview' in result
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_chained_collectors():
    """Test collector that uses output from another collector"""

    # First level: raw data
    raw_data = CollectedParameter(
        name='raw_file_data',
        title='Raw File Data',
        description='Unprocessed file data',
        output_type=DataTypes.RAW_DATA
    )

    # Second level: processed data
    processed_data = CollectedParameter(
        name='processed_file_data',
        title='Processed File Data',
        description='Cleaned and processed data',
        output_type=DataTypes.PROCESSED_TEXT
    )

    ParameterRegistry.register(raw_data)
    ParameterRegistry.register(processed_data)

    # First collector: read raw data
    @data_collector(
        name="Raw Data Collector",
        inputs=[ParameterRegistry.get_by_name('file_path')],
        outputs=[DataTypes.RAW_DATA]
    )
    def collect_raw(file_path):
        """Read raw file data"""
        with open(file_path, 'r') as f:
            return {'raw_lines': f.readlines()}

    # Second collector: process raw data
    @data_collector(
        name="Data Processor",
        inputs=[raw_data],
        outputs=[DataTypes.PROCESSED_TEXT]
    )
    def process_raw(raw_file_data):
        """Process raw data"""
        cleaned = [line.strip()
                   for line in raw_file_data['raw_lines'] if line.strip()]
        return {'cleaned_lines': cleaned, 'count': len(cleaned)}

    # Report uses processed data
    @report(
        title="Processed Data Report",
        description="Report on processed data",
        inputs=[processed_data]
    )
    def processed_report(processed_file_data):
        """Generate report from processed data"""
        return f"Processed {processed_file_data['count']} non-empty lines"

    # Test the chain
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Line 1\n\nLine 2\n   \nLine 3")
        test_file = f.name

    try:
        # Execute chain
        raw = collect_raw(test_file)
        processed = process_raw(raw)
        result = processed_report(processed)

        # Verify
        assert "Processed 3 non-empty lines" in result
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_report_with_mixed_inputs():
    """Test report with both primitive and collected parameters"""

    # Collected parameter
    analyzed_data = CollectedParameter(
        name='analysis_result',
        title='Analysis Result',
        description='Result of data analysis',
        output_type=DataTypes.ANALYSIS_RESULTS
    )

    ParameterRegistry.register(analyzed_data)

    # Collector
    @data_collector(
        name="Data Analyzer",
        inputs=[ParameterRegistry.get_by_name('file_path')],
        outputs=[DataTypes.ANALYSIS_RESULTS]
    )
    def analyze_file(file_path):
        """Analyze file"""
        with open(file_path, 'r') as f:
            content = f.read()
        return {'word_count': len(content.split())}

    # Report uses both collected data AND a primitive parameter
    output_file = FilePath(
        name='output_path',
        title='Output Path',
        description='Where to save report',
        required=True
    )

    @report(
        title="Mixed Input Report",
        description="Report using both collected and primitive inputs",
        inputs=[analyzed_data, output_file]
    )
    def mixed_report(analysis_result, output_path):
        """Generate report with mixed inputs"""
        report_text = f"Word count: {analysis_result['word_count']}"
        # In real scenario would write to output_path
        return {'report': report_text, 'output': output_path}

    # Test
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("One two three four five")
        test_file = f.name

    try:
        analyzed = analyze_file(test_file)
        result = mixed_report(analyzed, "/tmp/output.txt")

        assert "Word count: 5" in result['report']
        assert result['output'] == "/tmp/output.txt"
    finally:
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_get_base_inputs_e2e():
    """Test that get_base_inputs traces through collector chain"""
    from productivity_app.data_pipeline import reports

    # Create chain: file_path → collected1 → collected2 → report
    collected1 = CollectedParameter(
        name='level_1_data',
        title='Level 1 Data',
        description='First level',
        output_type=DataTypes.LEVEL_1
    )

    collected2 = CollectedParameter(
        name='level_2_data',
        title='Level 2 Data',
        description='Second level',
        output_type=DataTypes.LEVEL_2
    )

    ParameterRegistry.register(collected1)
    ParameterRegistry.register(collected2)

    @data_collector(
        name="Level 1 Collector",
        inputs=[ParameterRegistry.get_by_name('file_path')],
        outputs=[DataTypes.LEVEL_1]
    )
    def collect_level1(file_path):
        return {'data': 'level1'}

    @data_collector(
        name="Level 2 Collector",
        inputs=[collected1],
        outputs=[DataTypes.LEVEL_2]
    )
    def collect_level2(level_1_data):
        return {'data': 'level2'}

    @report(
        title="Chained Report",
        description="Uses deeply nested collected data",
        inputs=[collected2]
    )
    def chained_report(level_2_data):
        return "Report"

    # Get the report wrapper
    all_reports = reports.get_all_reports()
    report_wrapper = [r for r in all_reports if r.title == "Chained Report"][0]

    # Get base inputs - should trace back to file_path
    base_inputs = report_wrapper.get_base_inputs()

    # Should have traced through both collectors to find file_path
    assert len(base_inputs) > 0
    base_names = [p.name for p in base_inputs]
    assert 'file_path' in base_names
