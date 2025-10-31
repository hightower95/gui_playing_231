# Remote Docs Module

## Overview

The Remote Docs tab provides functionality to view available remote documents and upload new versions. This allows users to access and manage shared documentation from a central location.

## Features

### Current Implementation

1. **View Available Documents**
   - Table display showing document name, version, and last update time
   - Sample data displayed for demonstration
   - Sortable and selectable rows

2. **Download Documents**
   - Download button for each document
   - File save dialog for choosing download location
   - Placeholder implementation (ready for backend integration)

3. **Upload New Versions**
   - File selection dialog
   - Upload button with confirmation
   - Placeholder implementation (ready for backend integration)

4. **Refresh**
   - Manually refresh the document list
   - Ready for API integration

## User Interface

### Available Documents Section
- **Table Columns:**
  - Document Name: Name of the remote document
  - Version: Current version number (e.g., v2.1.0)
  - Last Updated: Timestamp of last update
  - Actions: Download button

- **Features:**
  - Alternating row colors for readability
  - Stretch column for document name
  - Auto-sized columns for version and date
  - Single row selection

### Upload New Version Section
- **Controls:**
  - File selection button
  - Selected file display
  - Upload button (enabled only when file is selected)
  - Confirmation dialog before upload

## Implementation Status

### ✅ Completed
- Basic UI layout with StandardGroupBox
- Table for displaying documents
- File selection for uploads
- Download and upload button handlers
- Placeholder data for testing

### 🚧 TODO (Backend Integration)
- Connect to actual remote document server/API
- Implement real download functionality
- Implement real upload functionality
- Add authentication if required
- Add version history tracking
- Add document metadata (size, author, etc.)
- Add search/filter functionality
- Add document categories/tags

## File Structure

```
app/remote_docs/
├── __init__.py          # Module exports
├── presenter.py         # Business logic (TODO: add model integration)
└── view.py              # UI components
```

## Integration

The Remote Docs tab is integrated into the main window:

```python
from app.remote_docs import RemoteDocsPresenter

# In MainWindow.__init__:
self.remote_docs = RemoteDocsPresenter(context)
self.tabs.addTab(self.remote_docs.view, self.remote_docs.title)
```

## Future Enhancements

1. **Backend Integration**
   - REST API or file server connection
   - Real-time updates via WebSocket
   - Background download/upload with progress

2. **Enhanced Features**
   - Document preview
   - Version comparison
   - Access control/permissions
   - Document comments/notes
   - Download history
   - Automatic update notifications

3. **Advanced UI**
   - Drag-and-drop upload
   - Bulk operations
   - Advanced filtering
   - Document thumbnails
   - Search functionality

## Usage Example

```python
# Create presenter
remote_docs = RemoteDocsPresenter(context)

# Access view
view = remote_docs.view

# Future: Connect to model signals
# remote_docs.model.documents_updated.connect(view._load_documents)
```

## Notes

- Currently uses placeholder/sample data for demonstration
- Download and upload functions show dialogs but don't perform actual operations
- Ready for backend integration - just implement the model and connect signals
- Uses standard components for consistent UI (StandardButton, StandardLabel, etc.)
