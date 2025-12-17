"""
Tests for ChoiceParameter
"""
import pytest
from productivity_app.data_pipeline.parameters import (
    ChoiceParameter, InputParameter, DataSource
)
from productivity_app.data_pipeline.reports.decorator import report
from productivity_app.data_pipeline.reports.register import report_registry


def test_choice_parameter_creation():
    """ChoiceParameter can be created with choices and default"""

    param = ChoiceParameter(
        name="level",
        choices=["low", "medium", "high"],
        default="medium"
    )

    assert param.name == "level"
    assert param.choices == ["low", "medium", "high"]
    assert param.default == "medium"


def test_choice_parameter_validates_default():
    """ChoiceParameter raises error if default not in choices"""

    with pytest.raises(ValueError, match="Default value .* not in choices"):
        ChoiceParameter(
            name="level",
            choices=["low", "medium", "high"],
            default="invalid"
        )


def test_choice_parameter_has_optional_default():
    """ChoiceParameter can have no default"""

    param = ChoiceParameter(
        name="level",
        choices=["low", "medium", "high"],
        default=None,
        required=False
    )

    assert param.default is None
    assert param.required is False


def test_choice_parameter_in_report():
    """ChoiceParameter works in report registration"""

    @report(
        title="Test Choice Report",
        description="Report with choice parameter",
        inputs=[
            DataSource.FilePath,
            DataSource.Strictness
        ]
    )
    def test_choice_report(filepath: str, strictness: str = "moderate"):
        return {"file": filepath, "strictness": strictness}

    registered = report_registry.get_report_by_name("Test Choice Report")
    params = registered.get_parameters()

    assert len(params) == 2

    # Second param is Strictness (ChoiceParameter)
    strictness_param = params[1]
    assert isinstance(strictness_param, ChoiceParameter)
    assert strictness_param.name == "strictness"
    assert strictness_param.choices == ["strict", "moderate", "lenient"]
    assert strictness_param.default == "moderate"


def test_choice_parameter_gui_properties():
    """ChoiceParameter has properties needed for GUI rendering"""

    param = DataSource.Strictness

    # Has all InputParameter properties
    assert hasattr(param, 'name')
    assert hasattr(param, 'required')
    assert hasattr(param, 'description')
    assert hasattr(param, 'title')

    # Has choice-specific properties
    assert hasattr(param, 'choices')
    assert hasattr(param, 'default')

    # Values are correct
    assert param.name == "strictness"
    assert param.title == "Strictness Level"
    assert param.choices == ["strict", "moderate", "lenient"]
    assert param.default == "moderate"


def test_choice_parameter_in_report_execution():
    """Report with ChoiceParameter executes correctly"""

    @report(
        title="Test Choice Execution",
        description="Execute report with choice",
        inputs=[DataSource.Strictness]
    )
    def test_execution(strictness: str = "moderate"):
        return f"Strictness: {strictness}"

    registered = report_registry.get_report_by_name("Test Choice Execution")

    # Call with default
    result1 = registered.generate()
    assert result1 == "Strictness: moderate"

    # Call with explicit value
    result2 = registered.generate(strictness="strict")
    assert result2 == "Strictness: strict"


def test_choice_parameter_can_be_modified():
    """ChoiceParameter supports modification like InputParameter"""

    original = ChoiceParameter(
        name="size",
        choices=["small", "large"],
        default="small"
    )

    # Modify to add more choices
    modified = original(choices=["small", "medium", "large"])

    assert modified.choices == ["small", "medium", "large"]
    assert modified.name == "size"  # Other properties preserved
    assert original.choices == ["small", "large"]  # Original unchanged

    @report(
        title="Test Choice Execution",
        description="Execute report with choice",
        inputs=[original]
    )
    def test_execution(strictness: str = "moderate", size="not small"):
        return f"Strictness: {strictness}, Size: {size}"

    registered = report_registry.get_report_by_name("Test Choice Execution")
    result = registered.generate()
    assert result == "Strictness: moderate, Size: not small"

    result = registered.generate(size="small")
    assert result == "Strictness: moderate, Size: small"


def test_choice_parameter_numeric_choices():
    """ChoiceParameter works with numeric choices"""

    param = ChoiceParameter(
        name="threshold",
        choices=[0.1, 0.5, 0.9],
        default=0.5,
        description="Threshold value"
    )

    assert param.choices == [0.1, 0.5, 0.9]
    assert param.default == 0.5


def test_gui_can_distinguish_parameter_types():
    """GUI can check parameter type to render appropriately"""

    @report(
        title="Test Mixed Params",
        description="Mix of parameter types",
        inputs=[
            DataSource.FilePath,           # InputParameter
            DataSource.Strictness          # ChoiceParameter
        ]
    )
    def test_mixed(filepath: str, strictness: str = "moderate"):
        pass

    registered = report_registry.get_report_by_name("Test Mixed Params")
    params = registered.get_parameters()

    # GUI can check types
    assert isinstance(params[0], InputParameter)
    assert not isinstance(params[0], ChoiceParameter)  # Plain input

    assert isinstance(params[1], ChoiceParameter)  # Has choices

    # GUI logic example
    for param in params:
        if isinstance(param, ChoiceParameter):
            # Render as dropdown/select
            assert param.choices is not None
        else:
            # Render as text input
            assert not hasattr(param, 'choices') or param.choices is None
