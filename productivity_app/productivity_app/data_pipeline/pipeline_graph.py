"""
Transformation graph for routing data from primitives (FilePath, QueryID) 
through collectors and transformers to report parameters.

The graph is a directed acyclic graph (DAG) where:
- Nodes are Parameters
- Edges are transformation steps (collectors or transformers)
- Paths are sequences of steps from primitive to target
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Literal
from collections import defaultdict

from .parameters.input_parameters import Parameter


@dataclass
class TransformationStep:
    """A single transformation (collector or transformer)"""
    name: str
    input_type: Parameter
    output_type: Parameter
    func: Callable
    step_type: Literal["collector", "transformer"]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformationPath:
    """A sequence of steps from primitive to target (no loops)"""
    source_type: Parameter
    target_type: Parameter
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
        self.nodes: Set[str] = set()  # Store parameter type keys
        self.edges: Dict[str, List[TransformationStep]] = defaultdict(list)
        self.primitives: Set[str] = set()  # Store primitive type keys
        # Store groups by type key
        self.primitive_groups: Dict[str, Set[str]] = {}

    def add_collector(self, name: str, func: Callable,
                      inputs: List[Parameter], outputs: List[Parameter]):
        """Add collector edges (primitives -> data types)

        Collectors define entry points (primitives) for the graph.

        Args:
            name: Collector name
            func: Collector function
            inputs: List of primitive parameters
            outputs: List of data type parameters this collector produces
        """
        for input_param in inputs:
            input_key = input_param.get_type_key()
            self.primitives.add(input_key)
            self.nodes.add(input_key)

            for output_param in outputs:
                output_key = output_param.get_type_key()
                self.nodes.add(output_key)
                step = TransformationStep(
                    name=name,
                    input_type=input_param,
                    output_type=output_param,
                    func=func,
                    step_type="collector"
                )
                self.edges[input_key].append(step)

    def add_transformer(self, name: str, func: Callable,
                        input_type: Parameter, output_type: Parameter):
        """Add transformer edge (data type -> data type)

        Args:
            name: Transformer name
            func: Transformer function
            input_type: Input parameter type
            output_type: Output parameter type
        """
        input_key = input_type.get_type_key()
        output_key = output_type.get_type_key()

        self.nodes.add(input_key)
        self.nodes.add(output_key)
        step = TransformationStep(
            name=name,
            input_type=input_type,
            output_type=output_type,
            func=func,
            step_type="transformer"
        )
        self.edges[input_key].append(step)

    def find_all_paths(self, source: Parameter, target: Parameter,
                       max_depth: int = 10) -> List[TransformationPath]:
        """Find all non-cyclic paths using DFS with depth limit

        Args:
            source: Starting parameter (usually a primitive)
            target: Target parameter (report parameter type)
            max_depth: Maximum path length to prevent infinite recursion

        Returns:
            List of paths sorted by length (shortest first)
        """
        all_paths = []
        visited_steps = set()
        source_key = source.get_type_key()

        def dfs(current_key: str, path: List[TransformationStep], depth: int):
            # Base case: check if current type matches target
            if path and path[-1].output_type.matches(target):
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
            for step in self.edges[current_key]:
                if step.name not in visited_steps:
                    visited_steps.add(step.name)
                    path.append(step)
                    next_key = step.output_type.get_type_key()
                    dfs(next_key, path, depth + 1)
                    path.pop()
                    visited_steps.remove(step.name)

        dfs(source_key, [], 0)

        # Sort by length (shortest paths first)
        return sorted(all_paths, key=lambda p: p.length)

    def find_paths_to_target(self, target: Parameter,
                             max_depth: int = 10) -> List[TransformationPath]:
        """Find all paths from any primitive to target

        Args:
            target: Target parameter type
            max_depth: Maximum path length

        Returns:
            List of paths from all primitives, sorted by length
        """
        all_paths = []

        # Need to reconstruct Parameter objects from stored keys
        # For now, we'll iterate through edges to find actual primitives
        primitive_params = set()
        for prim_key in self.primitives:
            # Find first step that has this primitive as input
            for steps in self.edges.values():
                for step in steps:
                    if step.input_type.get_type_key() == prim_key:
                        primitive_params.add(step.input_type)
                        break

        for primitive in primitive_params:
            paths = self.find_all_paths(primitive, target, max_depth)
            all_paths.extend(paths)

        # Sort by length
        return sorted(all_paths, key=lambda p: p.length)

    def get_shortest_path(self, source: Parameter, target: Parameter) -> Optional[TransformationPath]:
        """Get the shortest path from source to target

        Args:
            source: Starting parameter type
            target: Target parameter type

        Returns:
            Shortest path, or None if no path exists
        """
        paths = self.find_all_paths(source, target)
        return paths[0] if paths else None

    def group_primitives(self, group_name: str, primitives: Set[Parameter]):
        """Define logical groups (e.g., 'file_inputs': {CSV, XLSX})

        Args:
            group_name: Name of the group
            primitives: Set of primitive parameter types in this group
        """
        self.primitive_groups[group_name] = {
            p.get_type_key() for p in primitives}
