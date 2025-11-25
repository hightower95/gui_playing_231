# Quick Start: Images in Lookup Context Display

## The 3 Ways to Add Images

### 1️⃣ Inline Base64 (Simplest)

```python
# Encode image once
import base64
with open('connector.png', 'rb') as f:
    image_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

# Add to data
row_data['image_base64'] = image_b64

# Displays automatically in context box!
```

**Best for**: Small images, embedded in data, portable

### 2️⃣ File Path (For Existing Images)

```python
# Add path to data
row_data['image_path'] = 'C:/connectors/d38999_12.png'

# Displays on right side in pinout_image_label
```

**Best for**: Large images, reused across many rows

### 3️⃣ HTML with Images (Maximum Control)

```python
# Custom HTML with styled layout
html = f"""
<div style="display: flex; gap: 15px;">
    <div>
        <h3>{row_data['Part Number']}</h3>
        <p>Material: {row_data['Material']}</p>
    </div>
    <div>
        <img src="{image_base64}" style="width: 150px; border-radius: 5px;" />
    </div>
</div>
"""
self.view.context_box.setHtml(html)
```

**Best for**: Custom layouts, multiple images

## Helper Functions

Import from `examples.context_images_example`:

```python
from examples.context_images_example import encode_image_to_base64, batch_encode_images_for_csv

# Encode single image
b64 = encode_image_to_base64('C:/connectors/connector.png')

# Encode all images in dataset
data = batch_encode_images_for_csv(data, image_dir='C:/connectors')
```

## Current Implementation

The context box now:
- ✅ Displays HTML-formatted text
- ✅ Shows inline images (base64)
- ✅ Supports file path images (via separate label)
- ✅ Uses professional dark theme styling
- ✅ Maintains text selection/copy

## What Your Data Needs

```python
row_data = {
    # Existing fields
    'Part Number': 'D38999/12',
    'Part Code': 'MSEK',
    'Material': 'Aluminum',
    'Family': 'D38999',
    'Shell Type': '26 - Plug',
    # ... other fields ...
    
    # Add ONE of these:
    'image_base64': 'data:image/png;base64,...'  # ← Inline
    # OR
    'image_path': 'C:/connectors/d38999.png'     # ← File
    # OR
    'image_url': 'https://example.com/d38999.png' # ← URL (future)
}
```

## Example: CSV with Images

```python
import pandas as pd
from examples.context_images_example import encode_image_to_base64

# Load connectors
df = pd.read_csv('connectors.csv')

# Add image paths based on Part Number
df['image_path'] = df['Part Number'].apply(
    lambda pn: f'C:/connectors/{pn.replace("/", "_")}.png'
)

# Convert paths to base64 (one-time)
data = df.to_dict('records')
for row in data:
    row['image_base64'] = encode_image_to_base64(row['image_path'])

# Now when rows are selected, images display automatically!
```

## Visual Result

```
┌─────────────────────────────┬──────────────┐
│ Connector Details           │              │
├─────────────────────────────┤   Pinout     │
│ Part Number: D38999/12      │   Image      │
│ Part Code: MSEK             │   (if path)  │
│ Material: Aluminum          │              │
│ [image_base64 shown here]   │──────────────│
└─────────────────────────────┴──────────────┘
```

## Tips

- **Size**: Keep images < 200x200 pixels
- **Format**: PNG for diagrams, JPG for photos  
- **Performance**: Encode base64 once, cache it
- **Fallback**: Images always have text fallback

## Documentation

- `docs/CONTEXT_DISPLAY_WITH_IMAGES.md` - Complete guide
- `examples/context_images_example.py` - Utility functions
- `docs/CONTEXT_IMAGES_SUMMARY.md` - Implementation details

---

**That's it!** Add `image_base64` to your connector data and it displays automatically in the context panel. ✨
