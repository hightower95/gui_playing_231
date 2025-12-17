"""
Report registry - tracks registered reports
"""
from typing import Dict, Any, Callable, List

from productivity_app.data_pipeline.parameters.input_parameters import Parameter
from productivity_app.data_pipeline.registry import registry as central_registry


class ReportRegistry:
    """Registry for reports - delegates to central registry"""

    def __init__(self):
        pass  # All state is in central registry

    def register(self, title: str, func: Callable, description: str, inputs: List[Parameter]):
        """Register a report"""
        central_registry.register_report(title, func, description, inputs)

    def get_report_by_name(self, title: str):
        """Get report wrapper by name"""
        report_info = central_registry.get_report(title)
        if report_info:
            return ReportWrapper(
                title=title,
                func=report_info['func'],
                inputs=report_info['inputs'],
                description=report_info.get('description', '')
            )
        return None
    
    def get_all_reports(self):
        """Get all reports as wrappers
        
        Returns:
            List of ReportWrapper objects
        """
        all_reports = central_registry.get_all_reports()
        return [
            ReportWrapper(
                title=title,
                func=info['func'],
                inputs=info['inputs'],
                description=info.get('description', '')
            )
            for title, info in all_reports.items()
        ]


class ReportWrapper:
    """Wrapper around report function"""

    def __init__(self, title: str, func: Callable, inputs: List[Any], description: str = ""):
        self.title = title
        self.func = func
        self.inputs = inputs
        self.description = description

    def generate(self, **kwargs):
        """Generate the report"""
        return self.func(**kwargs)

    def get_dependency_tree(self) -> str:
        """Get dependency tree showing report and inputs"""
        lines = [f"{self.title}"]
        for input_param in self.inputs:
            if hasattr(input_param, 'name'):
                required_marker = "" if input_param.required else " (optional)"
                lines.append(
                    f"      Input: {input_param.name}{required_marker}")
            else:
                lines.append(f"      Input: {input_param}")
        return "\n".join(lines)

    def get_parameters(self) -> List[Any]:
        """Get list of input parameters"""
        return self.inputs

    def get_required_parameters(self) -> List[Any]:
        """Get only required input parameters"""
        return [p for p in self.inputs if getattr(p, 'required', True)]

    def get_optional_parameters(self) -> List[Any]:
        """Get only optional input parameters"""
        return [p for p in self.inputs if not getattr(p, 'required', True)]

    def get_base_inputs(self) -> List[Any]:
        """Get root-level inputs (raw materials like FilePath)

        Traces through collectors to find the primitive inputs needed.
        For derived inputs (like PartsList), finds which collectors can provide them
        and returns their root inputs.

        Returns:
            List of root Parameter objects needed to run this report
        """
        from productivity_app.data_pipeline.registry import registry as central_registry
        from productivity_app.data_pipeline.parameters.input_parameters import (
            PrimitiveParameter,
            CollectedParameter
        )

        root_inputs = []
        to_process = list(self.inputs)
        processed = set()

        while to_process:
            param = to_process.pop(0)

            # Skip if already processed
            param_id = getattr(param, 'name', str(param))
            if param_id in processed:
                continue
            processed.add(param_id)

            # Check if it's a primitive parameter (user-provided)
            if isinstance(param, PrimitiveParameter):
                root_inputs.append(param)
                continue

            # For collected parameters, find collectors that produce them
            if isinstance(param, CollectedParameter):
                if param.output_type:
                    # Get collectors that output this type
                    collectors = central_registry.get_collectors_for_type(
                        param.output_type)
                    if collectors:
                        # Get inputs from first collector (could check all paths)
                        collector_info = central_registry.get_collector(
                            collectors[0])
                        if collector_info:
                            # Add collector's inputs to processing queue
                            to_process.extend(collector_info['inputs'])
                    else:
                        # No collectors available, treat as unsatisfiable (not root)
                        pass
                else:
                    # CollectedParameter without output_type, treat as root
                    root_inputs.append(param)
            else:
                # Unknown parameter type, treat as root for safety
                root_inputs.append(param)

        return root_inputs

    def can_generate(self) -> bool:
        """Check if report can be generated with available collectors

        Returns:
            True if all required inputs can be satisfied, False otherwise
        """
        issues = self.get_issues()
        return len(issues) == 0

    def get_issues(self) -> List[str]:
        """Get list of issues preventing report generation

        Checks if all required inputs can be satisfied either directly (root inputs)
        or through available collectors (derived inputs).

        Returns:
            List of issue descriptions, empty if no issues
        """
        from productivity_app.data_pipeline.registry import registry as central_registry
        from productivity_app.data_pipeline.parameters.input_parameters import (
            PrimitiveParameter,
            CollectedParameter
        )

        issues = []
        required_params = self.get_required_parameters()

        for param in required_params:
            # Primitive parameters are always satisfiable (user provides them)
            if isinstance(param, PrimitiveParameter):
                continue

            # For collected parameters, check if collectors exist
            if isinstance(param, CollectedParameter):
                param_name = getattr(param, 'name', str(param))

                if param.output_type:
                    # Check if any collectors provide this type
                    collectors = central_registry.get_collectors_for_type(
                        param.output_type)
                    if not collectors:
                        issues.append(
                            f"No collector available to provide '{param_name}' "
                            f"(requires DataType: {param.output_type.name})"
                        )
                    else:
                        # Check if collector's inputs can be satisfied
                        # For now, just verify collector exists (could recurse deeper)
                        pass
                else:
                    # CollectedParameter without output_type
                    issues.append(
                        f"Parameter '{param_name}' is a CollectedParameter but "
                        f"has no output_type specified"
                    )
            else:
                # Unknown parameter type
                param_name = getattr(param, 'name', str(param))
                issues.append(
                    f"Cannot determine how to satisfy parameter '{param_name}' "
                    f"(unknown parameter type)"
                )

        return issues


# Global registry
report_registry = ReportRegistry()
