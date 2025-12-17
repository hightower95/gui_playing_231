"""
Report registry - tracks registered reports
"""
from typing import Dict, Any, Callable, List


class ReportRegistry:
    """Registry for reports"""

    def __init__(self):
        self._reports: Dict[str, Dict[str, Any]] = {}

    def register(self, title: str, func: Callable, description: str, inputs: List[Any]):
        """Register a report"""
        self._reports[title] = {
            'func': func,
            'description': description,
            'inputs': inputs
        }

    def get_report_by_name(self, title: str):
        """Get report wrapper by name"""
        report_info = self._reports.get(title)
        if report_info:
            return ReportWrapper(
                title=title,
                func=report_info['func'],
                inputs=report_info['inputs']
            )
        return None


class ReportWrapper:
    """Wrapper around report function"""

    def __init__(self, title: str, func: Callable, inputs: List[Any]):
        self.title = title
        self.func = func
        self.inputs = inputs

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


# Global registry
report_registry = ReportRegistry()
