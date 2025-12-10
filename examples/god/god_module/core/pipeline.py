"""
Pipeline execution engine.
"""

from typing import Dict, Any, List, Optional
from .context import PipelineContext
from .registry import DataProviderRegistry, ReporterRegistry
from ..formats import DataFormat


class Pipeline:
    """
    Orchestrates execution of data providers and reporters.
    """
    
    def __init__(self):
        self.context = PipelineContext()
        
    def run_provider(self, provider_name: str, **kwargs) -> Any:
        """
        Execute a data provider and store results in context.
        
        Args:
            provider_name: Name of registered provider
            **kwargs: Parameters required by the provider
            
        Returns:
            The data returned by the provider
        """
        metadata = DataProviderRegistry.get(provider_name)
        if not metadata:
            raise ValueError(f"Data provider '{provider_name}' not found")
            
        self.context.log(f"Running data provider: {provider_name}")
        
        # Check preconditions
        for precondition in metadata.preconditions:
            if not precondition(self.context):
                raise RuntimeError(f"Precondition failed for provider '{provider_name}'")
        
        # Validate required parameters and apply defaults
        missing_params = []
        for param in metadata.requires:
            if param.name not in kwargs:
                if param.has_default():
                    kwargs[param.name] = param.get_default()
                elif param.required:
                    missing_params.append(param.name)
                    
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
        
        # Execute provider
        try:
            result = metadata.function(**kwargs)
            
            # Store result in context for each provided format
            for data_format in metadata.provides:
                self.context.set(data_format.value, result)
                
            self.context.log(f"Provider '{provider_name}' completed successfully")
            return result
            
        except Exception as e:
            self.context.log(f"Provider '{provider_name}' failed: {str(e)}", level="ERROR")
            raise
    
    def run_reporter(self, reporter_name: str, **kwargs) -> Any:
        """
        Execute a reporter using data from context.
        
        Args:
            reporter_name: Name of registered reporter
            **kwargs: Additional parameters/options for the reporter
            
        Returns:
            The output from the reporter
        """
        metadata = ReporterRegistry.get(reporter_name)
        if not metadata:
            raise ValueError(f"Reporter '{reporter_name}' not found")
            
        self.context.log(f"Running reporter: {reporter_name}")
        
        # Gather input data from context
        input_data = []
        missing_inputs = []
        
        for data_format in metadata.inputs:
            data = self.context.get(data_format.value)
            if data is None:
                missing_inputs.append(data_format.value)
            else:
                input_data.append(data)
                
        if missing_inputs:
            raise ValueError(f"Missing required input formats: {missing_inputs}")
        
        # Add parameters with defaults
        for param in metadata.parameters:
            if param.name not in kwargs:
                if param.has_default():
                    kwargs[param.name] = param.get_default()
                elif param.required:
                    raise ValueError(f"Missing required parameter: {param.name}")
        
        # Execute reporter
        try:
            result = metadata.function(*input_data, **kwargs)
            
            # Store result in context for each output format
            for data_format in metadata.outputs:
                self.context.set(data_format.value, result)
                
            self.context.log(f"Reporter '{reporter_name}' completed successfully")
            return result
            
        except Exception as e:
            self.context.log(f"Reporter '{reporter_name}' failed: {str(e)}", level="ERROR")
            raise
    
    def get_result(self, data_format: DataFormat) -> Any:
        """Get a result from the pipeline context"""
        return self.context.get(data_format.value)
    
    def get_all_results(self) -> Dict[str, Any]:
        """Get all results from the pipeline"""
        return self.context.get_all_data()
