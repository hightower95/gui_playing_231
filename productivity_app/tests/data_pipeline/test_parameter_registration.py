"""
Tests for report parameter registration
"""
import pytest
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.reports.register import report_registry
from productivity_app.data_pipeline.parameters import DataSource, InputParameter


def test_register_1_parameter():
    """Registering 1 parameter results in 1 parameter registered"""

    @report(
        title="Test Report 1 Param",
        description="Test with 1 parameter",
        inputs=[DataSource.FilePath]
    )
    def test_report_1(filepath: str):
        return filepath

    registered = report_registry.get_report_by_name("Test Report 1 Param")
    params = registered.get_parameters()

    assert len(params) == 1
    assert params[0].name == "filepath"


def test_registered_unnamed_inputs_is_ok():
    """Report function can have parameters not in inputs list"""

    @report(
        title="Test Unnamed Inputs OK",
        description="Function has extra params not in inputs",
        inputs=[DataSource.FilePath]
    )
    def test_extra_params(filepath: str, extra_param: str = "default"):
        return f"{filepath},{extra_param}"

    registered = report_registry.get_report_by_name("Test Unnamed Inputs OK")

    # Only filepath is in inputs
    assert len(registered.get_parameters()) == 1

    # But function can be called with just the registered param
    result = registered.generate(filepath="test.csv")
    assert result == "test.csv,default"


def test_register_too_many_inputs_gets_error():
    """Registering more inputs than function params causes error at registration time"""

    with pytest.raises(ValueError, match="inputs .* not found in function signature"):
        @report(
            title="Test Too Many Inputs",
            description="Inputs list has more params than function",
            inputs=[
                InputParameter(name="param1", required=True),
                InputParameter(name="param2", required=True),
                InputParameter(name="param3", required=True)
            ]
        )
        def test_too_many(param1: str, param2: str):
            return f"{param1},{param2}"


def test_register_4_parameters():
    """Registering 4 parameters results in 4 parameters registered"""

    param1 = InputParameter(name="param1", required=True)
    param2 = InputParameter(name="param2", required=True)
    param3 = InputParameter(name="param3", required=True)
    param4 = InputParameter(name="param4", required=True)

    @report(
        title="Test Report 4 Params",
        description="Test with 4 parameters",
        inputs=[param1, param2, param3, param4]
    )
    def test_report_4(param1: str, param2: str, param3: str, param4: str):
        return f"{param1},{param2},{param3},{param4}"

    registered = report_registry.get_report_by_name("Test Report 4 Params")
    params = registered.get_parameters()

    assert len(params) == 4
    assert [p.name for p in params] == ["param1", "param2", "param3", "param4"]


def test_register_2_parameters_1_optional():
    """Register 2 parameters, 1 required and 1 optional"""

    @report(
        title="Test Report 2 Params 1 Optional",
        description="Test with 1 required and 1 optional parameter",
        inputs=[DataSource.InputPath, DataSource.OutputPath(required=False)]
    )
    def test_report_mixed(input_path: str, output_path: str = None):
        return f"{input_path},{output_path}"

    registered = report_registry.get_report_by_name(
        "Test Report 2 Params 1 Optional")

    all_params = registered.get_parameters()
    required_params = registered.get_required_parameters()
    optional_params = registered.get_optional_parameters()

    assert len(all_params) == 2
    assert len(required_params) == 1
    assert len(optional_params) == 1

    assert required_params[0].name == "input_path"
    assert required_params[0].required is True

    assert optional_params[0].name == "output_path"
    assert optional_params[0].required is False


def test_register_2_parameters_both_optional():
    """Register 2 parameters, both optional"""

    opt1 = InputParameter(name="optional1", required=False)
    opt2 = InputParameter(name="optional2", required=False)

    @report(
        title="Test Report 2 Optional",
        description="Test with 2 optional parameters",
        inputs=[opt1, opt2]
    )
    def test_report_all_optional(optional1: str = None, optional2: str = None):
        return f"{optional1},{optional2}"

    registered = report_registry.get_report_by_name("Test Report 2 Optional")

    all_params = registered.get_parameters()
    required_params = registered.get_required_parameters()
    optional_params = registered.get_optional_parameters()

    assert len(all_params) == 2
    assert len(required_params) == 0
    assert len(optional_params) == 2

    assert optional_params[0].name == "optional1"
    assert optional_params[1].name == "optional2"


def test_named_parameters_land_correctly():
    """Named parameters are correctly passed to function"""

    @report(
        title="Test Named Params",
        description="Test that named params route correctly",
        inputs=[
            InputParameter(name="first_param", required=True),
            InputParameter(name="second_param", required=False)
        ]
    )
    def test_named_routing(first_param: str, third_param: str = "ignore", second_param: str = "default"):
        return {"first": first_param, "second": second_param}

    registered = report_registry.get_report_by_name("Test Named Params")

    # Call with only required parameter
    result1 = registered.generate(first_param="value1")
    assert result1["first"] == "value1"
    assert result1["second"] == "default"

    # Call with both parameters
    result2 = registered.generate(first_param="value1", second_param="value2")
    assert result2["first"] == "value1"
    assert result2["second"] == "value2"

    # Call with parameters in different order (kwargs work)
    result3 = registered.generate(second_param="value2", first_param="value1")
    assert result3["first"] == "value1"
    assert result3["second"] == "value2"


def test_parameter_names_match_function_signature():
    """Parameter names must match function argument names"""

    @report(
        title="Test Name Matching",
        description="Parameter names match function args",
        inputs=[
            InputParameter(name="input_file", required=True),
            InputParameter(name="output_file", required=False)
        ]
    )
    def test_matching(input_file: str, output_file: str = None):
        return {"in": input_file, "out": output_file}

    registered = report_registry.get_report_by_name("Test Name Matching")
    params = registered.get_parameters()

    # Verify parameter names
    assert params[0].name == "input_file"
    assert params[1].name == "output_file"

    # Verify they route correctly
    result = registered.generate(input_file="test.txt", output_file="out.txt")
    assert result["in"] == "test.txt"
    assert result["out"] == "out.txt"
