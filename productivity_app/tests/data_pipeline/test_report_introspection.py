"""
Test report introspection API - get_all_reports and parameter iteration
"""
import pytest
from productivity_app.data_pipeline.reports import report, get_all_reports
from productivity_app.data_pipeline.parameters import FilePath, InputPath, ParameterRegistry

# Import parameters to trigger registration
import productivity_app.data_pipeline.parameters.file_path
import productivity_app.data_pipeline.parameters.input_path


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


def test_get_all_reports_empty():
    """Test get_all_reports returns empty list when no reports registered"""
    
    registry = ParameterRegistry()
    all_reports = get_all_reports()
    assert all_reports == []
    assert isinstance(all_reports, list)


def test_get_all_reports_single_report():
    """Test get_all_reports with one report"""
    
    registry = ParameterRegistry()

    @report(
        title="Test Report",
        description="A test report",
        inputs=[registry.get('FilePath')]
    )
    def test_report(file_path):
        return f"Report for {file_path}"

    all_reports = get_all_reports()

    assert len(all_reports) == 1
    assert all_reports[0].title == "Test Report"
    assert all_reports[0].description == "A test report"


def test_get_all_reports_multiple():
    """Test get_all_reports with multiple reports"""
    
    registry = ParameterRegistry()

    @report(
        title="Report 1",
        description="First report",
        inputs=[registry.get('FilePath')]
    )
    def report1(file_path):
        return "Report 1"

    @report(
        title="Report 2",
        description="Second report",
        inputs=[registry.get('InputPath')]
    )
    def report2(input_path):
        return "Report 2"

    @report(
        title="Report 3",
        description="Third report",
        inputs=[]
    )
    def report3():
        return "Report 3"

    all_reports = get_all_reports()

    assert len(all_reports) == 3
    titles = {r.title for r in all_reports}
    assert titles == {"Report 1", "Report 2", "Report 3"}


def test_report_required_parameters():
    """Test accessing required_parameters on a report"""
    
    registry = ParameterRegistry()

    @report(
        title="Test Report",
        description="Report with required params",
        inputs=[
            registry.get('FilePath'),
            registry.get('InputPath')
        ]
    )
    def test_report(file_path, input_path):
        return "Report"

    all_reports = get_all_reports()
    test_report_wrapper = all_reports[0]

    required = test_report_wrapper.get_required_parameters()

    assert len(required) == 2
    param_names = [p.name for p in required]
    assert 'file_path' in param_names
    assert 'input_path' in param_names


def test_iterate_required_parameters():
    """Test iterating over required_parameters"""
    
    registry = ParameterRegistry()

    @report(
        title="Multi-Param Report",
        description="Report with multiple parameters",
        inputs=[
            registry.get('FilePath'),
            registry.get('InputPath')
        ]
    )
    def multi_report(file_path, input_path):
        return "Report"

    all_reports = get_all_reports()
    report_wrapper = all_reports[0]

    required_params = report_wrapper.get_required_parameters()

    # Test iteration
    param_names = []
    for param in required_params:
        param_names.append(param.name)
        # Verify param attributes exist
        assert hasattr(param, 'title')
        assert hasattr(param, 'description')
        assert hasattr(param, 'required')

    assert len(param_names) == 2
    assert 'file_path' in param_names
    assert 'input_path' in param_names


def test_multiple_parameters_same_type():
    """Test report with multiple FilePath parameters"""
    
    registry = ParameterRegistry()

    # Create two separate FilePath parameters
    file_path_1 = FilePath(
        name='input_file',
        title='Input File',
        description='First file to process',
        required=True
    )

    file_path_2 = FilePath(
        name='reference_file',
        title='Reference File',
        description='Reference file for comparison',
        required=True
    )

    @report(
        title="Dual File Report",
        description="Report comparing two files",
        inputs=[file_path_1, file_path_2]
    )
    def dual_file_report(input_file, reference_file):
        return f"Comparing {input_file} with {reference_file}"

    all_reports = get_all_reports()
    report_wrapper = all_reports[0]

    # Get all parameters
    all_params = report_wrapper.get_parameters()
    assert len(all_params) == 2

    # Verify both are FilePath
    assert all(isinstance(p, FilePath) for p in all_params)

    # Verify they have different names
    param_names = [p.name for p in all_params]
    assert 'input_file' in param_names
    assert 'reference_file' in param_names

    # Verify both are required
    required_params = report_wrapper.get_required_parameters()
    assert len(required_params) == 2

    # Test iteration and access
    for param in required_params:
        assert param.required is True
        assert param.name in ['input_file', 'reference_file']
        assert isinstance(param, FilePath)


def test_report_wrapper_attributes():
    """Test that ReportWrapper exposes all necessary attributes"""
    
    registry = ParameterRegistry()

    @report(
        title="Attribute Test",
        description="Testing wrapper attributes",
        inputs=[registry.get('FilePath')]
    )
    def attr_report(file_path):
        return "Report"

    all_reports = get_all_reports()
    wrapper = all_reports[0]

    # Test all expected attributes
    assert hasattr(wrapper, 'title')
    assert hasattr(wrapper, 'description')
    assert hasattr(wrapper, 'func')
    assert hasattr(wrapper, 'inputs')
    assert hasattr(wrapper, 'get_parameters')
    assert hasattr(wrapper, 'get_required_parameters')
    assert hasattr(wrapper, 'get_optional_parameters')
    assert hasattr(wrapper, 'get_base_inputs')
    assert hasattr(wrapper, 'can_generate')
    assert hasattr(wrapper, 'get_issues')
    assert hasattr(wrapper, 'get_dependency_tree')
    assert hasattr(wrapper, 'generate')

    # Verify attribute values
    assert wrapper.title == "Attribute Test"
    assert wrapper.description == "Testing wrapper attributes"
    assert callable(wrapper.func)


def test_optional_parameters():
    """Test report with both required and optional parameters"""
    
    registry = ParameterRegistry()

    required_param = FilePath(
        name='required_file',
        title='Required File',
        description='Must be provided',
        required=True
    )

    optional_param = FilePath(
        name='optional_file',
        title='Optional File',
        description='Can be omitted',
        required=False
    )

    @report(
        title="Mixed Params Report",
        description="Report with required and optional params",
        inputs=[required_param, optional_param]
    )
    def mixed_report(required_file, optional_file=None):
        return f"Required: {required_file}, Optional: {optional_file}"

    all_reports = get_all_reports()
    wrapper = all_reports[0]

    # Test required parameters
    required = wrapper.get_required_parameters()
    assert len(required) == 1
    assert required[0].name == 'required_file'

    # Test optional parameters
    optional = wrapper.get_optional_parameters()
    assert len(optional) == 1
    assert optional[0].name == 'optional_file'

    # Test all parameters
    all_params = wrapper.get_parameters()
    assert len(all_params) == 2
