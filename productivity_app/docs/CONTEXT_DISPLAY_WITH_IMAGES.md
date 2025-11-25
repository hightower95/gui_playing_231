# Context Display with Images - Implementation Guide

## Overview

The Lookup module's context display now supports rich HTML formatting with inline images and text. This allows you to display connector details alongside pinout diagrams, family logos, or other relevant images.

## Architecture

### Components

1. **RichTextBrowser** (`ui/components/rich_text_browser.py`)
   - QTextBrowser-based widget with HTML support
   - Displays formatted content with images
   - Read-only for safe content display

2. **Enhanced Context Display** (Lookup presenter)
   - `_update_context_display()` - Main update method
   - `_generate_context_html()` - HTML generation with image support
   - `_load_image_to_label()` - Image loading utility

3. **Base Tab View** (`ui/base_sub_tab_view.py`)
   - `context_box` now uses QTextBrowser (not QTextEdit)
   - Supports HTML content natively

### Flow

```
row selected → _update_context_display()
    ├→ _generate_context_html() - Creates HTML with images
    ├→ context_box.setHtml() - Display formatted text
    └→ _load_image_to_label() - Display pinout image (if separate)
```

## Usage Methods

### Method 1: Inline Image in HTML (Recommended for small images)

Include image data directly in the row data with `image_base64` or `image_url`:

```python
# In your data source, add image_base64 field
row_data = {
    'Part Number': 'D38999/12',
    'Part Code': 'MSEK',
    'Material': 'Aluminum',
    'image_base64': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
}

# Or with URL
row_data = {
    'Part Number': 'D38999/12',
    'image_url': 'https://example.com/connectors/d38999_12.png'
}
```

The HTML will automatically embed the image:
```html
<img src="data:image/png;base64,..." style="width:150px; height:150px; border-radius:5px;" />
```

### Method 2: Separate Pinout Image Label

Use the existing `pinout_image_label` on the right side:

```python
row_data = {
    'Part Number': 'D38999/12',
    'Part Code': 'MSEK',
    'image_path': 'C:/path/to/connectors/d38999_12.png'  # Local file path
}

# Presenter automatically loads image to pinout_image_label via _load_image_to_label()
```

### Method 3: Custom HTML Content

Override `_update_context_display()` or `_generate_context_html()` for custom layouts:

```python
def _update_context_display(self, row_data: dict):
    """Custom implementation with special layout"""
    custom_html = f"""
    <html>
    <body style="font-family: Arial; color: #e0e0e0;">
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
            <div>
                <h2>Connector Details</h2>
                <p><b>Part Number:</b> {row_data.get('Part Number')}</p>
                <p><b>Shell Type:</b> {row_data.get('Shell Type')}</p>
            </div>
            <div>
                <img src="{row_data.get('image_base64')}" 
                     style="width: 100%; border-radius: 5px;" />
            </div>
        </div>
    </body>
    </html>
    """
    self.view.context_box.setHtml(custom_html)
```

## Supported Image Formats

### 1. Base64-Encoded Images (Best for web/portability)

```python
import base64

# Read image file and encode to base64
with open('connector.png', 'rb') as f:
    image_base64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

row_data = {'image_base64': image_base64}
```

### 2. File Paths (Local images)

```python
row_data = {'image_path': 'C:/connectors/d38999_12.png'}

# Loaded via _load_image_to_label() to pinout_image_label
```

### 3. URLs (Remote images)

```python
row_data = {'image_url': 'https://example.com/connectors/d38999.png'}

# Note: URL loading requires additional dependencies (requests/urllib)
# Currently shows placeholder text
```

## Data Integration

### Adding Images to Your Data Source

#### Example 1: From CSV/Excel

```python
import pandas as pd
import base64
from pathlib import Path

# Load connector data
df = pd.read_csv('connectors.csv')

# Add image paths based on Part Number
def get_image_path(part_number):
    path = Path(f'connectors_images/{part_number}.png')
    return str(path) if path.exists() else None

df['image_path'] = df['Part Number'].apply(get_image_path)

# Or encode images to base64
def get_image_base64(part_number):
    path = Path(f'connectors_images/{part_number}.png')
    if path.exists():
        with open(path, 'rb') as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return None

df['image_base64'] = df['Part Number'].apply(get_image_base64)
```

#### Example 2: From Database

```python
import base64
import sqlite3

conn = sqlite3.connect('connectors.db')
cursor = conn.cursor()

query = """
SELECT 
    part_number,
    material,
    shell_type,
    image_blob  -- BLOB column with image data
FROM connectors
WHERE family = 'D38999'
"""

for row in cursor.fetchall():
    row_dict = dict(zip([col[0] for col in cursor.description], row))
    
    # Convert image blob to base64
    if row_dict['image_blob']:
        row_dict['image_base64'] = f"data:image/png;base64,{base64.b64encode(row_dict['image_blob']).decode()}"
    
    # Display in context
    presenter._update_context_display(row_dict)
```

## HTML Styling Options

### Image Styling

```html
<!-- Size control -->
<img src="..." style="width: 150px; height: 150px;" />
<img src="..." style="max-width: 100%; height: auto;" />

<!-- Border and shadow -->
<img src="..." style="border: 2px solid #4a90e2; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);" />

<!-- Responsive sizing -->
<img src="..." style="width: 150px; border-radius: 5px;" />
```

### Layout Options

```html
<!-- Side-by-side (default) -->
<div style="display: flex; gap: 15px;">
    <div>Text content</div>
    <div><img .../></div>
</div>

<!-- Grid layout -->
<div style="display: grid; grid-template-columns: 1fr 1fr;">
    <div>Details</div>
    <div><img .../></div>
</div>

<!-- Centered image above text -->
<div style="text-align: center;">
    <img .../> 
    <p>Description</p>
</div>
```

## Enabling/Disabling Features

### Feature Flag: ENABLE_PINOUT_IMAGE

In `shared/feature_toggles.py`:

```python
ENABLE_PINOUT_IMAGE = True  # Show separate pinout image label

# When False:
# - pinout_image_label is None
# - Context layout is full width
# - Inline images still work in HTML
```

### Dynamic Toggle (Runtime)

```python
# In Lookup presenter
self.view.pinout_image_label.setVisible(False)  # Hide image label
self.view.context_box.setMinimumWidth(0)        # Full width text
```

## Troubleshooting

### Images Not Displaying

**Problem**: Inline images show as broken

**Solutions**:
1. Check base64 encoding is valid
2. Verify image format is PNG/JPG/GIF
3. Ensure image data is properly prefixed: `data:image/png;base64,...`

**Problem**: Image path not loading

**Solutions**:
1. Check path is absolute and exists
2. Verify file permissions
3. Use forward slashes in paths: `C:/path/to/image.png`

### Performance Issues

**Problem**: Large images slow down display

**Solutions**:
1. Resize images before encoding (keep < 500px width)
2. Compress PNG/JPG files
3. Use base64 only for small images (< 500KB)
4. Use file paths for large images

### HTML Rendering Issues

**Problem**: Custom HTML not displaying correctly

**Solutions**:
1. Test HTML validity - use HTML validator
2. Escape special characters in data
3. Check QTextBrowser CSS support (limited vs full HTML5)
4. Use simple CSS, avoid complex selectors

## Examples

### Complete Example: Connector with Logo

```python
def _update_context_display(self, row_data: dict):
    """Display connector with family logo and details"""
    
    # Get family logo (if available)
    family = row_data.get('Family', 'Unknown')
    logo_base64 = self._get_family_logo(family)  # Your method
    
    html = f"""
    <html>
    <body style="font-family: Arial; color: #e0e0e0; background: transparent;">
        <div style="display: flex; gap: 20px; align-items: center;">
            {'<div><img src=\"' + logo_base64 + '\" style=\"width: 60px; height: 60px;\" /></div>' if logo_base64 else ''}
            <div>
                <h3 style="margin: 0; color: #4a90e2;">{row_data.get('Part Number')}</h3>
                <p style="margin: 5px 0;"><b>Family:</b> {family}</p>
                <p style="margin: 5px 0;"><b>Material:</b> {row_data.get('Material')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    self.view.context_box.setHtml(html)
```

### Display Pinout Diagram

```python
def _update_context_display(self, row_data: dict):
    """Display connector details with pinout diagram"""
    
    # Generate HTML table of properties
    details_html = self._generate_context_html(row_data)
    
    # Load pinout image separately (if enabled)
    if self.view.pinout_image_label and 'pinout_image_path' in row_data:
        self._load_image_to_label(
            row_data['pinout_image_path'], 
            self.view.pinout_image_label
        )
    
    self.view.context_box.setHtml(details_html)
```

## Best Practices

1. **Image Size**: Keep images < 200x200 pixels for the context display
2. **Format**: Use PNG for diagrams, JPG for photos
3. **Compression**: Compress images to reduce base64 string size
4. **Caching**: Cache base64 encodings if same images are reused
5. **Fallbacks**: Always provide alternative text if image fails to load
6. **Styling**: Use consistent CSS for professional appearance
7. **Performance**: Load images asynchronously for large datasets

## Future Enhancements

1. **Image Gallery**: Display multiple images with navigation
2. **Zoom Control**: Pinch-to-zoom or scroll wheel zoom for images
3. **Image Upload**: Allow users to associate custom images with connectors
4. **SVG Support**: Use SVG for scalable pinout diagrams
5. **Lazy Loading**: Load images only when context is displayed
