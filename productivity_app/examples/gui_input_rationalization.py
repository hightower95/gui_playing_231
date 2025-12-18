"""
Example: How GUI rationalizes input options from transformation paths

Shows how to group paths by primitive type and present options to user.
"""
from productivity_app.data_pipeline import registry, DataTypes
from collections import defaultdict

print("="*60)
print("GUI INPUT RATIONALIZATION EXAMPLE")
print("="*60)

# Build graph
graph = registry.build_graph()

# Simulate: Report needs PartsList parameter
target_type = DataTypes.PartsList
parameter_name = "parts_list"

print(f"\nReport Parameter: {parameter_name}")
print(f"Expected Type: {target_type}")
print("-"*60)

# Get all paths to this parameter
all_paths = graph.find_paths_to_target(target_type)

print(f"\nFound {len(all_paths)} transformation path(s):")
for i, path in enumerate(all_paths, 1):
    steps = ' → '.join([s.name for s in path.steps])
    print(f"  Path {i}: {path.source_type} → {steps}")

# ============================================================
# GUI RATIONALIZATION LOGIC
# ============================================================
print("\n" + "="*60)
print("STEP 1: Group paths by primitive type")
print("="*60)

input_options = defaultdict(list)

for path in all_paths:
    primitive_type = path.source_type  # e.g., DataTypes.FilePath
    input_options[primitive_type].append(path)

print(f"\nGrouped by primitive type:")
for primitive_type, paths in input_options.items():
    print(f"  {primitive_type}: {len(paths)} path(s)")

# ============================================================
# STEP 2: Extract collector options per primitive
# ============================================================
print("\n" + "="*60)
print("STEP 2: Extract collector options per primitive")
print("="*60)

for primitive_type, paths in input_options.items():
    print(f"\n{primitive_type} options:")
    
    # Group by first step (collector)
    collector_groups = defaultdict(list)
    for path in paths:
        collector_name = path.steps[0].name
        collector_groups[collector_name].append(path)
    
    for collector_name, collector_paths in collector_groups.items():
        print(f"  - {collector_name}")
        print(f"      Leads to: {[p.target_type.value for p in collector_paths]}")
        # In real GUI, this would check metadata for file extensions
        print(f"      File types: [detect from metadata]")

# ============================================================
# STEP 3: Simulate GUI widget rendering
# ============================================================
print("\n" + "="*60)
print("STEP 3: GUI Widget Rendering Logic")
print("="*60)

print("\nPseudo-code for GUI:")
print("""
for primitive_type, paths in input_options.items():
    # Create section for this primitive type
    section = QGroupBox(f"Provide {primitive_type.value}")
    
    # Determine widget type based on primitive
    if primitive_type == DataTypes.FilePath:
        # File selection widget
        file_widget = FilePickerWidget()
        
        # Add file type filter from collector metadata
        collectors = {p.steps[0] for p in paths}
        extensions = []
        for collector in collectors:
            exts = collector.metadata.get('extensions', [])
            extensions.extend(exts)
        
        file_widget.set_filter(f"Files ({' '.join(extensions)})")
        section.add_widget(file_widget)
    
    elif primitive_type == DataTypes.QueryID:
        # Dropdown or search widget
        query_widget = QuerySelectorWidget()
        section.add_widget(query_widget)
    
    layout.add_widget(section)
""")

# ============================================================
# STEP 4: Actual rendering structure
# ============================================================
print("\n" + "="*60)
print("STEP 4: Concrete Example - File Selection")
print("="*60)

for primitive_type, paths in input_options.items():
    if primitive_type == DataTypes.FilePath:
        print(f"\nWidget: File Picker for '{parameter_name}'")
        print(f"Label: 'Select {parameter_name.replace('_', ' ').title()}'")
        
        # Extract file extensions from all collectors
        collector_names = [p.steps[0].name for p in paths]
        print(f"\nSupported collectors: {collector_names}")
        
        # In real implementation, metadata would have extensions
        print(f"File filter: 'All supported (*.csv *.xlsx *.xls)'")
        print(f"             'CSV Files (*.csv)'")
        print(f"             'Excel Files (*.xlsx *.xls)'")
        
        print(f"\nWhen user selects file:")
        print(f"  1. Detect extension: '.csv'")
        print(f"  2. Filter paths to matching collectors: [CSVCollector → ...]")
        print(f"  3. Execute shortest filtered path")

# ============================================================
# STEP 5: Multiple primitive types example
# ============================================================
print("\n" + "="*60)
print("STEP 5: Multiple Primitive Types (Future)")
print("="*60)

print("""
If report had multiple input options:

input_options = {
    DataTypes.FilePath: [path1, path2],      # CSV or Excel file
    DataTypes.QueryID: [path3],              # Database query
    DataTypes.APIEndpoint: [path4]           # REST API call
}

GUI would render:
┌─────────────────────────────────────┐
│ Provide Data for 'parts_list'      │
├─────────────────────────────────────┤
│ ○ File Upload                       │
│   [Browse...] (*.csv, *.xlsx)       │
│                                     │
│ ○ Database Query                    │
│   [Select Query ▼]                  │
│                                     │
│ ○ API Endpoint                      │
│   [Enter URL: ____________]         │
└─────────────────────────────────────┘

User picks one option, GUI:
- Executes corresponding transformation path
- Passes result to report
""")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("""
GUI Rationalization Flow:
1. Get all paths to report parameter
2. Group by primitive type (source_type)
3. For each primitive, create appropriate widget
4. Detect user input specifics (file ext, etc)
5. Filter to matching path and execute

Key insight: Multiple paths = multiple input OPTIONS for user
""")
