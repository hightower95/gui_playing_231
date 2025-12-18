"""
Central Registry for Reports and Data Collectors

Unified singleton registry for the data pipeline system.
"""
from typing import Dict, List, Any, Callable
from productivity_app.data_pipeline.types_enum import DataTypes


class CentralRegistry:
    """Singleton registry for reports and collectors"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._collectors: Dict[str, Dict[str, Any]] = {}
        self._transformers: Dict[str, Dict[str, Any]] = {}
        self._reports: Dict[str, Dict[str, Any]] = {}

    # ==================== Collector Methods ====================

    def register_collector(self,
                           name: str,
                           func: Callable,
                           inputs: List[Any],
                           outputs: List[DataTypes]):
        """Register a data collector

        Args:
            name: Collector name
            func: The collector function
            inputs: List of input parameter types
            outputs: List of DataTypes this collector provides
        """
        self._collectors[name] = {
            'func': func,
            'inputs': inputs,
            'outputs': outputs
        }

    def get_collectors_for_type(self, data_type: DataTypes) -> List[str]:
        """Find collectors that provide a specific data type

        Args:
            data_type: The DataType to search for

        Returns:
            List of collector names that provide this type
        """
        return [
            name for name, info in self._collectors.items()
            if data_type in info['outputs']
        ]

    def get_collector(self, name: str) -> Dict[str, Any]:
        """Get collector info by name"""
        return self._collectors.get(name)

    def get_collector_by_name(self, name: str) -> Callable:
        """Get the actual collector function by name

        Args:
            name: Collector name

        Returns:
            The collector function that can be called
        """
        collector_info = self._collectors.get(name)
        if collector_info:
            return collector_info['func']
        return None

    def get_all_collectors(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered collectors"""
        return self._collectors.copy()

    # ==================== Transformer Methods ====================

    def register_transformer(self,
                            name: str,
                            func: Callable,
                            input_type: DataTypes,
                            output_type: DataTypes):
        """Register a data transformer

        Args:
            name: Transformer name
            func: The transformer function
            input_type: DataType this transformer consumes
            output_type: DataType this transformer produces
        """
        self._transformers[name] = {
            'func': func,
            'input_type': input_type,
            'output_type': output_type
        }

    def get_transformers_for_input(self, input_type: DataTypes) -> List[str]:
        """Find transformers that accept a specific input type

        Args:
            input_type: The input DataType to search for

        Returns:
            List of transformer names that accept this type
        """
        return [
            name for name, info in self._transformers.items()
            if info['input_type'] == input_type
        ]

    def get_transformers_for_output(self, output_type: DataTypes) -> List[str]:
        """Find transformers that produce a specific output type

        Args:
            output_type: The output DataType to search for

        Returns:
            List of transformer names that produce this type
        """
        return [
            name for name, info in self._transformers.items()
            if info['output_type'] == output_type
        ]
transformers.clear()
        self._
    def get_transformer(self, name: str) -> Dict[str, Any]:
        """Get transformer info by name"""
        return self._transformers.get(name)

    def get_transformer_by_name(self, name: str) -> Callable:
        """Get the actual transformer function by name

        Args:
            name: Transformer name

        Returns:
            The transformer function that can be called
        """
        transformer_info = self._transformers.get(name)
        if transformer_info:
            return transformer_info['func']
        return None

    def get_all_transformers(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered transformers"""
        return self._transformers.copy()

    # ==================== Report Methods ====================

    def register_report(self,
                        title: str,
                        func: Callable,
                        description: str,
                        inputs: List[Any]):
        """Register a report

        Args:
            title: Report title
            func: The report function
            description: Report description
            inputs: List of input parameters
        """
        self._reports[title] = {
            'func': func,
            'description': description,
            'inputs': inputs
        }

    def get_report(self, title: str):
        """Get report wrapper by title

        Returns:
            ReportWrapper instance with generate() method, or None if not found
        """
        from productivity_app.data_pipeline.reports.register import ReportWrapper

        report_info = self._reports.get(title)
        if report_info:
            return ReportWrapper(
                title=title,
                func=report_info['func'],
                inputs=report_info['inputs'],
                description=report_info.get('description', '')
            )
        return None

    def get_all_reports(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered reports"""
        return self._reports.copy()

    # ==================== Utility Methods ====================

    def clear(self):
        """Clear all registrations (useful for testing)"""
        self._collectors.clear()
        self._reports.clear()


# Global singleton instance
registry = CentralRegistry()
