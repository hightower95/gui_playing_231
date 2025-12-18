"""
Utility: Generate parameter documentation

Creates markdown documentation for all available parameters.
Run directly from IDE to generate docs.
"""
from productivity_app.data_pipeline.parameters.parameter_registry import parameter_registry
from productivity_app.data_pipeline.parameters.input_parameters import (
    Parameter, PrimitiveParameter, CollectedParameter, ChoiceParameter
)


def generate_parameter_docs(output_file: str = None):
    """Generate markdown documentation for parameters
    
    Args:
        output_file: Path to save markdown file (optional)
    """
    print("=" * 80)
    print("PARAMETER DOCUMENTATION GENERATOR")
    print("=" * 80)
    
    all_params = parameter_registry.get_all_parameters()
    
    if not all_params:
        print("\n⚠️  No parameters registered.")
        return
    
    # Build documentation
    lines = ["# Data Pipeline Parameters\n"]
    lines.append("Auto-generated parameter documentation.\n\n")
    
    # Group by type
    primitives = parameter_registry.get_primitives()
    collected = parameter_registry.get_collected()
    
    # Build table of contents
    lines.append("## Contents\n\n")
    
    if primitives:
        lines.append("**Primitive Parameters:**\n")
        for param in primitives:
            param_name = None
            for name, p in all_params.items():
                if p == param:
                    param_name = name
                    break
            display_name = param_name if param_name else param.name
            lines.append(f"- [{display_name}](#{param.name})\n")
        lines.append("\n")
    
    if collected:
        lines.append("**Collected Parameters:**\n")
        for param in collected:
            param_name = None
            for name, p in all_params.items():
                if p == param:
                    param_name = name
                    break
            display_name = param_name if param_name else param.name
            lines.append(f"- [{display_name}](#{param.name})\n")
        lines.append("\n")
    
    lines.append("---\n\n")
    
    # Primitive Parameters section
    if primitives:
        for param in primitives:
            # Find the parameter name in registry
            param_name = None
            for name, p in all_params.items():
                if p == param:
                    param_name = name
                    break
            
            lines.append(f"## {param_name if param_name else param.name}\n\n")
            lines.append(f"**Name:** `{param.name}`  \n")
            if hasattr(param, 'title') and param.title:
                lines.append(f"**Title:** {param.title}  \n")
            if hasattr(param, 'description') and param.description:
                lines.append(f"**Description:** {param.description}  \n")
            
            # Additional details
            details = []
            details.append(f"Type: `{type(param).__name__}`")
            details.append(f"Required: `{param.required}`")
            
            # Special handling for ChoiceParameter
            if isinstance(param, ChoiceParameter):
                details.append(f"Choices: {', '.join(map(str, param.choices))}")
                if param.default is not None:
                    details.append(f"Default: `{param.default}`")
                if param.multiselect:
                    details.append("Multiselect: `True`")
            
            if details:
                lines.append(f"**Details:** {' | '.join(details)}  \n")
            
            lines.append("\n")
    
    # Collected Parameters section
    if collected:
        for param in collected:
            param_name = None
            for name, p in all_params.items():
                if p == param:
                    param_name = name
                    break
            
            lines.append(f"## {param_name if param_name else param.name}\n\n")
            lines.append(f"**Name:** `{param.name}`  \n")
            if hasattr(param, 'title') and param.title:
                lines.append(f"**Title:** {param.title}  \n")
            if hasattr(param, 'description') and param.description:
                lines.append(f"**Description:** {param.description}  \n")
            
            # Additional details
            details = []
            details.append(f"Type: `{type(param).__name__}`")
            details.append(f"Required: `{param.required}`")
            if param.output_type:
                details.append(f"Output Type: `{param.output_type}`")
            
            if details:
                lines.append(f"**Details:** {' | '.join(details)}  \n")
            
            # Check for collectors
            from productivity_app.data_pipeline.registry import registry
            collectors = registry.get_collectors_for_type(param.output_type) if param.output_type else []
            if collectors:
                lines.append(f"**Available Collectors:** {', '.join(collectors)}  \n")
            
            lines.append("\n")
    
    # Join all lines
    doc_text = "\n".join(lines)
    
    # Output
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(doc_text)
            print(f"\n✅ Documentation written to: {output_file}")
        except Exception as e:
            print(f"\n❌ Error writing file: {e}")
            print("\nDocumentation preview:")
            print(doc_text)
    else:
        print("\n" + doc_text)
    
    print("\n" + "=" * 80)
    print(f"Generated documentation for {len(all_params)} parameters")
    print("=" * 80)


if __name__ == "__main__":
    import os
    
    # Auto-import parameters to ensure registration
    print("Loading parameters...\n")
    try:
        from productivity_app.data_pipeline import parameters
        print("✓ Parameters loaded\n")
    except ImportError as e:
        print(f"⚠️  Could not load parameters: {e}\n")
    
    # Load collectors for dependency info
    try:
        from productivity_app.data_pipeline.parameters.resolution import resolve_parts_list_from_file
        print("✓ Collectors loaded\n")
    except ImportError:
        pass
    
    # Determine output path
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'PARAMETERS.md'
    )
    
    generate_parameter_docs(output_path)
