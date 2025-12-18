"""
Central Registry for Reports and Data Collectors

Unified singleton registry for the data pipeline system.
"""
from typing import Dict, List, Any, Callable, Optional
from productivity_app.data_pipeline.parameters.input_parameters import Parameter
from productivity_app.data_pipeline.pipeline_graph import (
    TransformationGraph,
    TransformationPath
)


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
        self._graph: Optional[TransformationGraph] = None

    # ==================== Collector Methods ====================

    def register_collector(self,
                           name: str,
                           func: Callable,
                           inputs: List[Parameter],
                           outputs: List[Parameter]):
        """Register a data collector

        Args:
            name: Collector name
            func: The collector function
            inputs: List of input parameters
            outputs: List of Parameters this collector provides
        """
        self._collectors[name] = {
            'func': func,
            'inputs': inputs,
            'outputs': outputs
        }

    def get_collectors_for_type(self, param_type: Parameter) -> List[str]:
        """Find collectors that provide a compatible parameter type

        Args:
            param_type: The Parameter type to search for

        Returns:
            List of collector names that provide compatible type
        """
        return [
            name for name, info in self._collectors.items()
            if any(output.matches(param_type) for output in info['outputs'])
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
                             input_type: Parameter,
                             output_type: Parameter):
        """Register a data transformer

        Args:
            name: Transformer name
            func: The transformer function
            input_type: Parameter this transformer consumes
            output_type: Parameter this transformer produces
        """
        self._transformers[name] = {
            'func': func,
            'input_type': input_type,
            'output_type': output_type
        }

    def get_transformers_for_input(self, input_param: Parameter) -> List[str]:
        """Find transformers that accept a compatible input type

        Args:
            input_param: The input Parameter to search for

        Returns:
            List of transformer names that accept compatible type
        """
        return [
            name for name, info in self._transformers.items()
            if info['input_type'].matches(input_param)
        ]

    def get_transformers_for_output(self, output_param: Parameter) -> List[str]:
        """Find transformers that produce a compatible output type

        Args:
            output_param: The output Parameter to search for

        Returns:
            List of transformer names that produce compatible type
        """
        return [
            name for name, info in self._transformers.items()
            if info['output_type'].matches(output_param)
        ]

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

    # ==================== Graph Methods ====================

    def build_graph(self) -> TransformationGraph:
        """Construct transformation graph from registered collectors and transformers

        Returns:
            TransformationGraph with all registered transformations
        """
        graph = TransformationGraph()

        # Add collectors to graph
        for name, info in self._collectors.items():
            graph.add_collector(
                name, info['func'], info['inputs'], info['outputs'])

        # Add transformers to graph
        for name, info in self._transformers.items():
            graph.add_transformer(
                name, info['func'], info['input_type'], info['output_type'])

        self._graph = graph
        return graph

    def get_graph(self) -> TransformationGraph:
        """Get the transformation graph, building it if necessary

        Returns:
            TransformationGraph instance
        """
        if self._graph is None:
            self.build_graph()
        return self._graph

    def get_paths_for_parameter(self, target_param: Parameter,
                                max_depth: int = 10) -> List[TransformationPath]:
        """Get all transformation paths from any primitive to target parameter

        Args:
            target_param: The parameter type needed by report
            max_depth: Maximum path length

        Returns:
            List of paths sorted by length (shortest first)
        """
        graph = self.get_graph()
        return graph.find_paths_to_target(target_param, max_depth)

    def get_shortest_path(self, source: Parameter, target: Parameter) -> Optional[TransformationPath]:
        """Get the shortest transformation path from source to target

        Args:
            source: Starting parameter (usually a primitive)
            target: Target parameter

        Returns:
            Shortest path, or None if no path exists
        """
        graph = self.get_graph()
        return graph.get_shortest_path(source, target)

    def invalidate_graph(self):
        """Invalidate cached graph (call after registering new collectors/transformers)"""
        self._graph = None

    # ==================== Utility Methods ====================

    def clear(self):
        """Clear all registrations (useful for testing)"""
        self._collectors.clear()
        self._transformers.clear()
        self._reports.clear()
        self._graph = None


# Global singleton instance
registry = CentralRegistry()
