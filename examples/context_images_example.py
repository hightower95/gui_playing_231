"""
Example: Adding Images to Connector Lookup Context Display

This example demonstrates three ways to add images to the context display:
1. Inline base64-encoded images
2. Local file paths  
3. Remote URLs
"""
import base64
from pathlib import Path


def create_sample_connector_data_with_images():
    """Create sample connector data with image references"""
    
    # Method 1: Local file path
    sample_data_local = {
        'Part Number': 'D38999/12',
        'Part Code': 'MSEK',
        'Material': 'Aluminum',
        'Database Status': 'Active',
        'Family': 'D38999',
        'Shell Type': '26 - Plug',
        'Insert Arrangement': 'A - 1',
        'Socket Type': 'Type A',
        'Keying': 'A',
        'image_path': 'C:/connectors/d38999_12.png'  # File on disk
    }
    
    # Method 2: Base64-encoded image (create sample)
    sample_base64 = create_sample_base64_image()
    sample_data_inline = {
        'Part Number': 'D38999/24',
        'Part Code': 'MSEF',
        'Material': 'Stainless Steel',
        'Database Status': 'Active',
        'Family': 'D38999',
        'Shell Type': '24 - Receptacle',
        'Insert Arrangement': 'B - 2',
        'Socket Type': 'Type B',
        'Keying': 'B',
        'image_base64': sample_base64  # Inline data
    }
    
    # Method 3: Remote URL
    sample_data_url = {
        'Part Number': 'VG95234',
        'Part Code': 'VGSPEC',
        'Material': 'Titanium',
        'Database Status': 'Active',
        'Family': 'VG',
        'Shell Type': '20 - Receptacle B',
        'Insert Arrangement': 'C - 3',
        'Socket Type': 'Type C',
        'Keying': 'C',
        'image_url': 'https://example.com/connectors/vg95234.png'
    }
    
    return {
        'local_file': sample_data_local,
        'inline_base64': sample_data_inline,
        'remote_url': sample_data_url
    }


def create_sample_base64_image():
    """Create a minimal valid base64-encoded PNG for testing
    
    This is a tiny 1x1 transparent PNG for demonstration.
    In real use, encode your actual connector pinout diagrams.
    """
    # Minimal 1x1 transparent PNG (68 bytes)
    png_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    return f"data:image/png;base64,{base64.b64encode(png_bytes).decode()}"


def encode_image_to_base64(image_path: str) -> str:
    """Convert an image file to base64-encoded data URI
    
    Args:
        image_path: Path to image file (PNG, JPG, GIF, etc)
        
    Returns:
        Base64 data URI ready for use in HTML img src
        
    Example:
        data_uri = encode_image_to_base64('C:/connectors/d38999_12.png')
        row_data['image_base64'] = data_uri
    """
    path = Path(image_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Detect image type from extension
    suffix = path.suffix.lower()
    type_map = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.svg': 'image/svg+xml'
    }
    
    mime_type = type_map.get(suffix, 'image/png')
    
    with open(path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    return f"data:{mime_type};base64,{image_data}"


def batch_encode_images_for_csv(csv_data: list, image_dir: str, image_column: str = 'image_path') -> list:
    """Convert local image paths to base64 for all rows in a dataset
    
    Useful for preparation before displaying in context.
    
    Args:
        csv_data: List of dictionaries (one per row)
        image_dir: Directory containing images
        image_column: Column name to store base64 data ('image_base64')
        
    Returns:
        Modified list with base64 images added
        
    Example:
        df = pd.read_csv('connectors.csv')
        data = df.to_dict('records')
        
        # Add image paths based on Part Number
        for row in data:
            part_num = row['Part Number'].replace('/', '_')
            row['image_path'] = f'connectors_images/{part_num}.png'
        
        # Convert paths to base64
        data = batch_encode_images_for_csv(data, 'connectors_images')
    """
    for row in csv_data:
        image_path = row.get('image_path')
        if image_path:
            try:
                # Make path absolute if relative
                if not Path(image_path).is_absolute():
                    image_path = str(Path(image_dir) / Path(image_path).name)
                
                row['image_base64'] = encode_image_to_base64(image_path)
            except FileNotFoundError as e:
                print(f"Warning: {e}")
                row['image_base64'] = None
    
    return csv_data


def display_connector_with_image(presenter, row_data: dict):
    """Display a connector with image in the context box
    
    Args:
        presenter: LookupConnectorPresenter instance
        row_data: Dictionary with connector data and optional images
        
    Usage:
        # In your code when a row is selected:
        samples = create_sample_connector_data_with_images()
        display_connector_with_image(presenter, samples['inline_base64'])
    """
    presenter._update_context_display(row_data)


def example_usage():
    """Complete example of using images in context display"""
    
    print("=" * 70)
    print("CONTEXT DISPLAY WITH IMAGES - EXAMPLES")
    print("=" * 70)
    
    # Get sample data
    samples = create_sample_connector_data_with_images()
    
    print("\n1. LOCAL FILE PATH METHOD")
    print("-" * 70)
    print("Use when images are stored on disk")
    print(f"  image_path: {samples['local_file'].get('image_path')}")
    print("  Loaded by: _load_image_to_label() to pinout_image_label")
    
    print("\n2. INLINE BASE64 METHOD")
    print("-" * 70)
    print("Use for embedded images (portable, no file dependencies)")
    print(f"  image_base64 length: {len(samples['inline_base64'].get('image_base64', ''))} chars")
    print("  Displayed in: HTML via <img src=\"data:image/png;base64,...\"/>")
    
    print("\n3. REMOTE URL METHOD")
    print("-" * 70)
    print("Use for images hosted on web servers")
    print(f"  image_url: {samples['remote_url'].get('image_url')}")
    print("  Note: Requires additional setup for external URL loading")
    
    print("\n4. ENCODING LOCAL IMAGES")
    print("-" * 70)
    print("Convert local images to base64 for embedding:")
    print("  from examples.context_images_example import encode_image_to_base64")
    print("  b64 = encode_image_to_base64('C:/path/to/connector.png')")
    print("  row_data['image_base64'] = b64")
    
    print("\n5. BATCH ENCODING FROM CSV")
    print("-" * 70)
    print("Prepare images for a full dataset:")
    print("  import pandas as pd")
    print("  df = pd.read_csv('connectors.csv')")
    print("  data = df.to_dict('records')")
    print("  # Add image paths and convert to base64")
    print("  data = batch_encode_images_for_csv(data, 'connectors_images')")
    
    print("\n" + "=" * 70)
    print("See CONTEXT_DISPLAY_WITH_IMAGES.md for complete documentation")
    print("=" * 70)


if __name__ == "__main__":
    example_usage()
