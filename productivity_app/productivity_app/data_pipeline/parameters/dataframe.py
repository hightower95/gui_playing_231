"""
DataFrame Parameter Definition

CollectedParameter for pandas DataFrames produced by collectors.
"""
from productivity_app.data_pipeline.parameters.input_parameters import CollectedParameter
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry


# Define DataFrame as a CollectedParameter
parameter = parameter_registry.define_parameter(
    name="DataFrame",
    parameter=CollectedParameter(
        name='dataframe',
        description='Pandas DataFrame with tabular data',
        title='Data Frame'
    )
)
