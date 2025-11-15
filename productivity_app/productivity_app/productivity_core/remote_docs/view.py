"""
Remote Docs View

UI for viewing available remote documents and uploading new versions.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from ..ui.components import (
    StandardLabel, TextStyle, StandardButton, ButtonRole,
    StandardGroupBox
)


class RemoteDocsView(QWidget):
    """View for managing remote documents"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = StandardLabel("Remote Documents", style=TextStyle.TITLE)
        layout.addWidget(title)

        # Description
        description = StandardLabel(
            "View available remote documents and upload new versions.",
            style=TextStyle.NOTES
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Documents table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Name", "Version", "Last Updated", "Actions"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        # Upload Section
        self.upload_group = StandardGroupBox("Upload New Version")
        upload_layout = QVBoxLayout()

        upload_info = StandardLabel(
            "Select a document file to upload as a new version.",
            style=TextStyle.NOTES
        )
        upload_info.setWordWrap(True)
        upload_layout.addWidget(upload_info)

        # Upload controls
        upload_controls = QHBoxLayout()

        self.selected_file_label = StandardLabel(
            "No file selected", style=TextStyle.LABEL)
        upload_controls.addWidget(self.selected_file_label)
        upload_controls.addStretch()

        self.select_file_btn = StandardButton(
            "Select File", role=ButtonRole.SECONDARY)
        self.select_file_btn.clicked.connect(self._on_select_file)
        upload_controls.addWidget(self.select_file_btn)

        self.upload_btn = StandardButton("Upload", role=ButtonRole.PRIMARY)
        self.upload_btn.clicked.connect(self._on_upload)
        self.upload_btn.setEnabled(False)
        upload_controls.addWidget(self.upload_btn)

        upload_layout.addLayout(upload_controls)
        self.upload_group.setLayout(upload_layout)
        layout.addWidget(self.upload_group)

        # Refresh button at bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.refresh_btn = StandardButton("Refresh", role=ButtonRole.SECONDARY)
        self.refresh_btn.clicked.connect(self._on_refresh)
        button_layout.addWidget(self.refresh_btn)

        layout.addLayout(button_layout)

        # Load initial data
        self._load_documents()

    def set_upload_visible(self, visible: bool):
        """Show or hide the upload section

        Args:
            visible: True to show upload section, False to hide
        """
        self.upload_group.setVisible(visible)

    def _load_documents(self):
        """Load available remote documents"""
        self.table.setRowCount(0)

        # TODO: Replace with actual remote document fetching
        # For now, add placeholder data
        sample_docs = [
            ("EPD Database", "v2.1.0", "2025-10-15 14:30"),
            ("Connector Specifications", "v1.5.2", "2025-10-10 09:15"),
            ("Troubleshooting Guide", "v3.0.1", "2025-10-18 16:45"),
        ]

        for name, version, last_updated in sample_docs:
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(version))
            self.table.setItem(row, 2, QTableWidgetItem(last_updated))

            # Add download button
            download_btn = StandardButton("Download", role=ButtonRole.PRIMARY)
            download_btn.clicked.connect(
                lambda checked, n=name: self._on_download(n))
            self.table.setCellWidget(row, 3, download_btn)

    def _on_refresh(self):
        """Handle refresh button click"""
        self._load_documents()
        QMessageBox.information(
            self,
            "Refreshed",
            "Document list has been refreshed."
        )

    def _on_select_file(self):
        """Handle select file button click"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Document File",
            "",
            "All Files (*.*)"
        )

        if file_path:
            self.selected_file_path = file_path
            # Extract filename from path
            import os
            filename = os.path.basename(file_path)
            self.selected_file_label.setText(f"Selected: {filename}")
            self.upload_btn.setEnabled(True)
        else:
            self.selected_file_path = None
            self.selected_file_label.setText("No file selected")
            self.upload_btn.setEnabled(False)

    def _on_upload(self):
        """Handle upload button click"""
        if not hasattr(self, 'selected_file_path') or not self.selected_file_path:
            QMessageBox.warning(
                self,
                "No File Selected",
                "Please select a file to upload."
            )
            return

        # TODO: Implement actual upload logic
        import os
        filename = os.path.basename(self.selected_file_path)

        reply = QMessageBox.question(
            self,
            "Confirm Upload",
            f"Upload '{filename}' as a new version?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # TODO: Actual upload implementation
            QMessageBox.information(
                self,
                "Upload Successful",
                f"'{filename}' has been uploaded successfully.\n\n"
                "(This is a placeholder - actual upload not yet implemented)"
            )

            # Reset selection
            self.selected_file_path = None
            self.selected_file_label.setText("No file selected")
            self.upload_btn.setEnabled(False)

            # Refresh list
            self._load_documents()

    def _on_download(self, doc_name: str):
        """Handle download button click

        Args:
            doc_name: Name of document to download
        """
        # TODO: Implement actual download logic
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Save {doc_name}",
            doc_name.replace(" ", "_") + ".pdf",
            "All Files (*.*)"
        )

        if save_path:
            QMessageBox.information(
                self,
                "Download Successful",
                f"'{doc_name}' has been downloaded to:\n{save_path}\n\n"
                "(This is a placeholder - actual download not yet implemented)"
            )
