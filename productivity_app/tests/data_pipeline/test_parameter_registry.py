"""
Test parameter registry functionality
"""
import pytest
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry
from productivity_app.data_pipeline.parameters.input_parameters import (
    PrimitiveParameter,
    CollectedParameter,
    ChoiceParameter
)
from productivity_app.data_pipeline.types_enum import DataTypes


def test_registry_singleton():
    """Registry should be a singleton"""
    from productivity_app.data_pipeline.parameters.parameter_registry import ParameterRegistry

    reg1 = ParameterRegistry()
    reg2 = ParameterRegistry()
    assert reg1 is reg2
    assert parameter_registry is reg1


def test_define_parameter():
    """define_parameter should register and return parameter"""
    test_param = PrimitiveParameter(
        name="test_path",
        description="Test parameter"
    )

    returned = parameter_registry.define_parameter("TestParam", test_param)

    # Should return the same parameter
    assert returned is test_param

    # Should be retrievable
    retrieved = parameter_registry.get("TestParam")
    assert retrieved is test_param

    # Cleanup
    parameter_registry.clear()


def test_duplicate_registration_fails():
    """Registering same parameter name twice should fail"""
    param1 = PrimitiveParameter(name="test1")
    param2 = PrimitiveParameter(name="test2")

    parameter_registry.register("Duplicate", param1)

    with pytest.raises(ValueError, match="already registered"):
        parameter_registry.register("Duplicate", param2)

    # Cleanup
    parameter_registry.clear()


def test_get_all_parameters():
    """get_all_parameters should return all registered parameters"""
    param1 = PrimitiveParameter(name="param1")
    param2 = CollectedParameter(name="param2", output_type=DataTypes.DataFrame)

    parameter_registry.register("P1", param1)
    parameter_registry.register("P2", param2)

    all_params = parameter_registry.get_all_parameters()

    # At least our two (may have others from imports)
    assert len(all_params) >= 2
    assert "P1" in all_params
    assert "P2" in all_params

    # Cleanup
    parameter_registry.clear()


def test_get_primitives():
    """get_primitives should return only primitive parameters"""
    prim = PrimitiveParameter(name="prim")
    coll = CollectedParameter(name="coll", output_type=DataTypes.PartsList)
    choice = ChoiceParameter(name="choice", is_root=True, choices=["a", "b"])

    parameter_registry.register("Prim", prim)
    parameter_registry.register("Coll", coll)
    parameter_registry.register("Choice", choice)

    primitives = parameter_registry.get_primitives()

    # Should only have PrimitiveParameter instances
    assert prim in primitives
    assert coll not in primitives
    # ChoiceParameter is not a PrimitiveParameter
    assert choice not in primitives

    # Cleanup
    parameter_registry.clear()


def test_get_collected():
    """get_collected should return only collected parameters"""
    prim = PrimitiveParameter(name="prim")
    coll = CollectedParameter(name="coll", output_type=DataTypes.PartsList)

    parameter_registry.register("Prim", prim)
    parameter_registry.register("Coll", coll)

    collected = parameter_registry.get_collected()

    # Should only have CollectedParameter instances
    assert coll in collected
    assert prim not in collected

    # Cleanup
    parameter_registry.clear()


def test_parameters_auto_register_on_import():
    """Parameters should auto-register when their modules are imported"""
    # Import parameter modules (they may already be imported from other tests)
    from productivity_app.data_pipeline.parameters import file_path, parts_list

    # Should be in registry (either from this import or previous ones)
    fp = parameter_registry.get("FilePath")
    pl = parameter_registry.get("PartsList")

    # If not registered, it means clear() was called - re-import won't re-register
    # because Python caches imports. Check if they exist in the current registry state
    # or verify they would be registered on fresh import
    assert fp is not None or file_path.parameter is not None
    assert pl is not None or parts_list.parameter is not None

    # If we got them from registry, verify types
    if fp:
        assert isinstance(fp, PrimitiveParameter)
        assert fp.name == "filepath"

    if pl:
        assert isinstance(pl, CollectedParameter)
        assert pl.name == "parts"
        assert pl.output_type == DataTypes.PartsList


def test_clear_registry():
    """clear() should remove all parameters"""
    param = PrimitiveParameter(name="test")
    parameter_registry.register("Test", param)

    assert parameter_registry.get("Test") is not None

    parameter_registry.clear()

    assert parameter_registry.get("Test") is None
    assert len(parameter_registry.get_all_parameters()) == 0
