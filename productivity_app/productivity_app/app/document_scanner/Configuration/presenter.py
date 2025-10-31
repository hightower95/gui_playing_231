"""
Document Scanner Configuration Presenter
"""
import json
from pathlib import Path
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog, QMessageBox
from app.document_scanner.Configuration.view import ConfigurationView


class ConfigurationPresenter(QObject):
    """Presenter for document scanner configuration"""

    def __init__(self, context, model):
        super().__init__()
        self.context = context
        self.model = model
        self.view = ConfigurationView()

        # Connect view signals
        self.view.add_document_requested.connect(self.on_add_document)
        self.view.remove_document_requested.connect(self.on_remove_document)
        self.view.edit_document_requested.connect(self.on_edit_document)
        self.view.export_config_requested.connect(self.on_export_config)

    def start_loading(self):
        """Initialize the configuration tab"""
        print("Document Scanner Configuration: Ready")

    def on_add_document(self, config: dict):
        """Handle adding a new document

        Args:
            config: Document configuration from dialog
        """
        print(f"\n{'='*60}")
        print(f"ADDING DOCUMENT")
        print(f"{'='*60}")
        print(f"File Name: {config['file_name']}")
        print(f"File Path: {config['file_path']}")
        print(f"Header Row: {config['header_row']}")
        print(f"Search Columns: {config['search_columns']}")
        print(f"Return Columns: {config['return_columns']}")

        # Add to model (saves and loads in background)
        self.model.add_document(config)

        print(f"✓ Document queued for loading")
        print(f"{'='*60}\n")

    def on_remove_document(self, row: int):
        """Handle removing a document

        Args:
            row: Row index in the table
        """
        configs = self.model.get_document_configs()
        if 0 <= row < len(configs):
            config = configs[row]
            print(f"Removing document: {config['file_name']}")

            # Remove from model (saves and reloads)
            self.model.remove_document(row)

    def on_edit_document(self, row: int, config: dict):
        """Handle editing a document

        Args:
            row: Row index in the table
            config: Updated configuration
        """
        # TODO: Implement edit functionality
        print(f"Edit document at row {row}: {config}")

    def on_documents_changed(self, searchable_documents: list):
        """Called when model finishes loading documents - update view

        Args:
            searchable_documents: List of SearchableDocument objects
        """
        print(
            f"CONFIG: Updating view with {len(searchable_documents)} document(s)")

        # Clear view
        self.view.documents_model.removeRows(
            0, self.view.documents_model.rowCount())

        # Populate view with loaded documents
        configs = self.model.get_document_configs()
        for config in configs:
            self.view.add_document_row(config)

    def on_export_config(self):
        """Export current configuration to a JSON file"""
        try:
            # Get current configurations
            configs = self.model.get_document_configs()

            if not configs:
                QMessageBox.information(
                    self.view,
                    "No Configuration",
                    "There are no documents configured to export."
                )
                return

            # Ask user for save location
            file_path, _ = QFileDialog.getSaveFileName(
                self.view,
                "Export Configuration",
                "document_scanner_config.json",
                "JSON Files (*.json);;All Files (*.*)"
            )

            if not file_path:
                return  # User cancelled

            # Prepare export data
            export_data = {
                'version': '1.0',
                'exported_at': self._get_timestamp(),
                'document_count': len(configs),
                'documents': configs
            }

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            QMessageBox.information(
                self.view,
                "Export Successful",
                f"Configuration exported successfully to:\n{file_path}\n\n"
                f"Exported {len(configs)} document(s)."
            )

            print(f"✓ Configuration exported to: {file_path}")

        except Exception as e:
            QMessageBox.critical(
                self.view,
                "Export Failed",
                f"Failed to export configuration:\n{str(e)}"
            )
            print(f"✗ Export failed: {e}")
            import traceback
            traceback.print_exc()

    def _get_timestamp(self):
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
