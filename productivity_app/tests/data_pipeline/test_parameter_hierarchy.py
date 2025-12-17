"""
Test parameter class hierarchy functionality
"""
import pytest
from dataclasses import FrozenInstanceError
from productivity_app.data_pipeline.parameters.input_parameters import (
    Parameter,
    PrimitiveParameter,
    CollectedParameter,
    ChoiceParameter
)
from productivity_app.data_pipeline.types_enum import DataTypes


def test_parameter_base_class():
    """Test Parameter base class attributes"""
    param = Parameter(
        name="test",
        description="Test parameter",
        title="Test Title"
    )
    
    assert param.name == "test"
    assert param.description == "Test parameter"
    assert param.title == "Test Title"
    assert param.required is True  # Default
    assert param.is_root is False  # Default


def test_primitive_parameter_defaults():
    """PrimitiveParameter should have is_root=True by default"""
    param = PrimitiveParameter(
        name="test_path",
        description="Test path parameter"
    )
    
    assert param.is_root is True
    assert param.required is True
    assert isinstance(param, Parameter)


def test_collected_parameter_defaults():
    """CollectedParameter should have is_root=False by default"""
    param = CollectedParameter(
        name="test_collected",
        description="Test collected parameter",
        output_type=DataTypes.PartsList
    )
    
    assert param.is_root is False
    assert param.required is True
    assert param.output_type == DataTypes.PartsList
    assert isinstance(param, Parameter)


def test_collected_parameter_output_type_optional():
    """CollectedParameter can have None output_type"""
    param = CollectedParameter(
        name="test",
        description="Test"
    )
    
    assert param.output_type is None


def test_choice_parameter():
    """Test ChoiceParameter attributes"""
    param = ChoiceParameter(
        name="test_choice",
        description="Test choice",
        choices=["option1", "option2", "option3"],
        default="option1"
    )
    
    assert param.choices == ["option1", "option2", "option3"]
    assert param.default == "option1"
    assert param.multiselect is False  # Default
    assert param.required is True


def test_choice_parameter_multiselect():
    """Test ChoiceParameter with multiselect"""
    param = ChoiceParameter(
        name="test_multi",
        description="Test multiselect",
        choices=["a", "b", "c"],
        multiselect=True
    )
    
    assert param.multiselect is True
    assert param.default is None  # Default when not specified


def test_parameter_callable_modification():
    """Test __call__() method for creating modified copies"""
    original = PrimitiveParameter(
        name="original",
        description="Original description",
        required=True
    )
    
    # Create modified copy
    modified = original(required=False, description="New description")
    
    # Original should be unchanged
    assert original.required is True
    assert original.description == "Original description"
    
    # Modified should have new values
    assert modified.required is False
    assert modified.description == "New description"
    assert modified.name == "original"  # Unchanged attribute
    assert modified.is_root is True  # Inherited from PrimitiveParameter


def test_parameter_callable_with_multiple_changes():
    """Test modifying multiple attributes at once"""
    param = CollectedParameter(
        name="test",
        description="Original",
        required=True,
        output_type=DataTypes.DataFrame
    )
    
    modified = param(
        required=False,
        description="Updated description",
        output_type=DataTypes.PartsList
    )
    
    assert modified.required is False
    assert modified.description == "Updated description"
    assert modified.output_type == DataTypes.PartsList
    assert modified.name == "test"


def test_parameter_frozen_dataclass():
    """Parameters should be frozen (immutable)"""
    param = PrimitiveParameter(name="test", description="Test")
    
    # Direct attribute modification should fail
    with pytest.raises(FrozenInstanceError):
        param.name = "new_name"
    
    with pytest.raises(FrozenInstanceError):
        param.required = False


def test_parameter_call_preserves_type():
    """Calling parameter should preserve its type"""
    prim = PrimitiveParameter(name="prim", description="Primitive")
    coll = CollectedParameter(name="coll", description="Collected", output_type=DataTypes.PartsList)
    choice = ChoiceParameter(name="choice", description="Choice", choices=["a", "b"])
    
    # Modified copies should maintain their types
    modified_prim = prim(required=False)
    modified_coll = coll(required=False)
    modified_choice = choice(default="a")
    
    assert isinstance(modified_prim, PrimitiveParameter)
    assert isinstance(modified_coll, CollectedParameter)
    assert isinstance(modified_choice, ChoiceParameter)


def test_primitive_parameter_is_root_override():
    """PrimitiveParameter allows is_root override (though unusual)"""
    param = PrimitiveParameter(
        name="test",
        description="Test",
        is_root=False  # Override default
    )
    
    assert param.is_root is False


def test_collected_parameter_is_root_override():
    """CollectedParameter allows is_root override (though unusual)"""
    param = CollectedParameter(
        name="test",
        description="Test",
        is_root=True  # Override default
    )
    
    assert param.is_root is True


def test_parameter_title_optional():
    """Title defaults to name if not provided"""
    param = Parameter(name="test")
    assert param.title == "test"  # Defaults to name in __post_init__
    
    param_with_title = Parameter(name="test", title="Test Title")
    assert param_with_title.title == "Test Title"


def test_parameter_description_optional():
    """Description defaults to empty string if not provided"""
    param = Parameter(name="test")
    assert param.description == ""  # Default empty string
    
    param_with_desc = Parameter(name="test", description="Test description")
    assert param_with_desc.description == "Test description"


def test_choice_parameter_with_is_root():
    """ChoiceParameter can have is_root set"""
    param = ChoiceParameter(
        name="test",
        choices=["a", "b"],
        is_root=True
    )
    
    assert param.is_root is True
    assert isinstance(param, Parameter)
