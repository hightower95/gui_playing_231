"""
Transformation graph for routing data from primitives (FilePath, QueryID) 
through collectors and transformers to report parameters.

The graph is a directed acyclic graph (DAG) where:
- Nodes are DataTypes
- Edges are transformation steps (collectors or transformers)
- Paths are sequences of steps from primitive to target
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Literal
from collections import defaultdict

from .types_enum import DataTypes


@dataclass
class TransformationStep:
    """A single transformation (collector or transformer)"""
    name: str
    input_type: DataTypes
    output_type: DataTypes
    func: Callable
    step_type: Literal["collector", "transformer"]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformationPath:
    """A sequence of steps from primitive to target (no loops)"""
    source_type: DataTypes
    target_type: DataTypes
    steps: List[TransformationStep]

    @property
    def length(self) -> int:
        """Number of steps in this path"""
        return len(self.steps)

    def execute(self, input_data: Any) -> Any:
        """Execute all steps in sequence

        Args:
            input_data: Starting data (e.g., file path)

        Returns:
            Final transformed data
        """
        result = input_data
        for step in self.steps:
            result = step.func(result)
        return result


class TransformationGraph:
    """Directed graph of all possible transformations"""

    def __init__(self):
        self.nodes: Set[DataTypes] = set()
        self.edges: Dict[DataTypes,
                         List[TransformationStep]] = defaultdict(list)
        self.primitives: Set[DataTypes] = set()
        self.primitive_groups: Dict[str, Set[DataTypes]] = {}

    def add_collector(self, name: str, func: Callable,
                      inputs: List[Any], outputs: List[DataTypes]):
        """Add collector edges (primitives -> data types)

        Collectors define entry points (primitives) for the graph.
        Inputs can be DataTypes or PrimitiveParameter objects.

        Args:
            name: Collector name
            func: Collector function
            inputs: List of primitive types (DataTypes or PrimitiveParameter)
            outputs: List of data types this collector produces
        """
        for input_item in inputs:
            # Handle both DataTypes and PrimitiveParameter
            from productivity_app.data_pipeline.parameters.input_parameters import PrimitiveParameter
            if isinstance(input_item, PrimitiveParameter):
                # Extract DataType from PrimitiveParameter
                input_type = DataTypes.FilePath  # For now, all primitives map to FilePath
                self.primitives.add(input_type)
            else:
                input_type = input_item
                self.primitives.add(input_type)

            self.nodes.add(input_type)
            for output_type in outputs:
                self.nodes.add(output_type)
                step = TransformationStep(
                    name=name,
                    input_type=input_type,
                    output_type=output_type,
                    func=func,
                    step_type="collector"
                )
                self.edges[input_type].append(step)

    def add_transformer(self, name: str, func: Callable,
                        input_type: DataTypes, output_type: DataTypes):
        """Add transformer edge (data type -> data type)

        Args:
            name: Transformer name
            func: Transformer function
            input_type: Input data type
            output_type: Output data type
        """
        self.nodes.add(input_type)
        self.nodes.add(output_type)
        step = TransformationStep(
            name=name,
            input_type=input_type,
            output_type=output_type,
            func=func,
            step_type="transformer"
        )
        self.edges[input_type].append(step)

    def find_all_paths(self, source: DataTypes, target: DataTypes,
                       max_depth: int = 10) -> List[TransformationPath]:
        """Find all non-cyclic paths using DFS with depth limit

        Args:
            source: Starting data type (usually a primitive)
            target: Target data type (report parameter type)
            max_depth: Maximum path length to prevent infinite recursion

        Returns:
            List of paths sorted by length (shortest first)
        """
        all_paths = []
        visited_steps = set()

        def dfs(current_type: DataTypes, path: List[TransformationStep], depth: int):
            # Base case: reached target
            if current_type == target:
                all_paths.append(TransformationPath(
                    source_type=source,
                    target_type=target,
                    steps=path.copy()
                ))
                return

            # Depth limit to prevent infinite recursion
            if depth >= max_depth:
                return

            # Explore neighbors
            for step in self.edges[current_type]:
                if step.name not in visited_steps:
                    visited_steps.add(step.name)
                    path.append(step)
                    dfs(step.output_type, path, depth + 1)
                    path.pop()
                    visited_steps.remove(step.name)

        dfs(source, [], 0)

        # Sort by length (shortest paths first)
        return sorted(all_paths, key=lambda p: p.length)

    def find_paths_to_target(self, target: DataTypes,
                             max_depth: int = 10) -> List[TransformationPath]:
        """Find all paths from any primitive to target

        Args:
            target: Target data type
            max_depth: Maximum path length

        Returns:
            List of paths from all primitives, sorted by length
        """
        all_paths = []

        for primitive in self.primitives:
            paths = self.find_all_paths(primitive, target, max_depth)
            all_paths.extend(paths)

        # Sort by length
        return sorted(all_paths, key=lambda p: p.length)

    def get_shortest_path(self, source: DataTypes, target: DataTypes) -> Optional[TransformationPath]:
        """Get the shortest path from source to target

        Args:
            source: Starting data type
            target: Target data type

        Returns:
            Shortest path, or None if no path exists
        """
        paths = self.find_all_paths(source, target)
        return paths[0] if paths else None

    def group_primitives(self, group_name: str, primitives: Set[DataTypes]):
        """Define logical groups (e.g., 'file_inputs': {CSV, XLSX})

        Args:
            group_name: Name of the group
            primitives: Set of primitive types in this group
        """
        self.primitive_groups[group_name] = primitives
