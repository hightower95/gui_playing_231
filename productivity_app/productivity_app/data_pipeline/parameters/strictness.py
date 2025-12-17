"""
Strictness Parameter - Choice parameter for validation strictness
"""
from productivity_app.data_pipeline.parameters.input_parameters import ChoiceParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry


Name = "Strictness"

parameter = ChoiceParameter(
    name="strictness",
    required=False,
    description="Validation strictness level",
    title="Strictness Level",
    choices=["strict", "moderate", "lenient"],
    default="moderate",
    is_root=True  # User-provided choice
)

# Auto-register on import
parameter_registry.register(Name, parameter)
