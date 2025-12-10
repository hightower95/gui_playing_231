"""
Remote Docs Presenter

Handles business logic for remote document management.
"""
from PySide6.QtCore import QObject
from .view import RemoteDocsView
from .model import RemoteDocsModel


class RemoteDocsPresenter(QObject):
    """Presenter for Remote Docs tab"""

    MODULE_ID = 'remote_docs'

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.title = "Remote Docs"

        # Initialize model
        self.model = RemoteDocsModel()

        # Create view
        self.view = RemoteDocsView()

        # Initialize upload section visibility based on feature flag
        self._update_upload_visibility()

        # Connect model signals
        self.model.documents_updated.connect(self._on_documents_updated)
        self.model.document_uploaded.connect(self._on_document_uploaded)
        self.model.document_downloaded.connect(self._on_document_downloaded)
        self.model.error_occurred.connect(self._on_error_occurred)
        self.model.operation_started.connect(self._on_operation_started)
        self.model.operation_progress.connect(self._on_operation_progress)
        self.model.operation_completed.connect(self._on_operation_completed)

        # TODO: Connect view signals when view is ready
        # self.view.upload_requested.connect(self.on_upload)
        # self.view.download_requested.connect(self.on_download)

        # Load initial data
        self._refresh_view()

    def _update_upload_visibility(self):
        """Update upload section visibility based on feature flag"""
        from ..tabs.settings_tab import FeatureFlagsConfig

        upload_enabled = FeatureFlagsConfig.is_enabled('remote_docs_upload')
        self.view.set_upload_visible(upload_enabled)
        print(
            f"[RemoteDocsPresenter] Upload section visibility: {upload_enabled}")

    def on_feature_flag_changed(self, flag_id: str, enabled: bool):
        """Handle feature flag change

        Args:
            flag_id: ID of the feature flag that changed
            enabled: New state of the flag
        """
        if flag_id == 'remote_docs_upload':
            self.view.set_upload_visible(enabled)
            print(
                f"[RemoteDocsPresenter] Upload visibility changed to: {enabled}")

    def on_upload(self, file_path: str):
        """Handle upload request

        Args:
            file_path: Path to file to upload
        """
        # TODO: Implement upload logic
        pass

    def on_download(self, doc_name: str, save_path: str):
        """Handle download request

        Args:
            doc_name: Name of document to download
            save_path: Path where to save the file
        """
        # TODO: Get version from view or default to latest
        doc = self.model.get_document_by_name(doc_name)
        if doc and doc.latest_version:
            version = doc.latest_version.version
            success = self.model.download_document(
                doc_name, version, save_path)
            if not success:
                print(f"[RemoteDocsPresenter] Failed to download {doc_name}")
        else:
            print(f"[RemoteDocsPresenter] Document not found: {doc_name}")

    def _on_documents_updated(self):
        """Handle documents list update from model"""
        print("[RemoteDocsPresenter] Documents updated, refreshing view")
        self._refresh_view()

    def _on_document_uploaded(self, doc_name: str):
        """Handle successful document upload

        Args:
            doc_name: Name of uploaded document
        """
        print(
            f"[RemoteDocsPresenter] Document uploaded successfully: {doc_name}")
        # TODO: Show success message in view

    def _on_document_downloaded(self, doc_name: str, local_path: str):
        """Handle successful document download

        Args:
            doc_name: Name of downloaded document
            local_path: Local path where file was saved
        """
        print(
            f"[RemoteDocsPresenter] Document downloaded: {doc_name} -> {local_path}")
        # TODO: Show success message in view

    def _on_error_occurred(self, error_message: str):
        """Handle error from model

        Args:
            error_message: Error message to display
        """
        print(f"[RemoteDocsPresenter] Error: {error_message}")
        # TODO: Show error message in view

    def _refresh_view(self):
        """Refresh the view with current model data"""
        documents = self.model.list_documents
        print(
            f"[RemoteDocsPresenter] Refreshing view with {len(documents)} documents")

        # TODO: Update view with documents when view methods are ready
        # For now, just log the documents
        for doc in documents:
            latest = doc.latest_version
            version_info = f"v{latest.version}" if latest else "No versions"
            print(
                f"  - {doc.name} ({doc.category}) - {version_info} - {doc.version_count} version(s)")

    def refresh_documents(self):
        """Refresh documents from remote source (async)"""
        if self.model.is_refreshing:
            print("[RemoteDocsPresenter] Refresh already in progress")
            return

        print("[RemoteDocsPresenter] Starting async document refresh...")
        self.model.refresh_documents()

    def get_document_categories(self):
        """Get list of available document categories"""
        return self.model.get_categories()

    def search_documents(self, query: str):
        """Search for documents matching the query

        Args:
            query: Search query string
        """
        results = self.model.search_documents(query)
        print(
            f"[RemoteDocsPresenter] Search for '{query}' found {len(results)} results")
        return results

    def _on_operation_started(self, operation_description: str):
        """Handle operation start

        Args:
            operation_description: Description of the operation that started
        """
        print(
            f"[RemoteDocsPresenter] Operation started: {operation_description}")
        # TODO: Show progress indicator in view
        # self.view.show_progress(operation_description)

    def _on_operation_progress(self, description: str, percentage: int):
        """Handle operation progress update

        Args:
            description: Current operation description
            percentage: Progress percentage (0-100)
        """
        print(f"[RemoteDocsPresenter] Progress: {description} ({percentage}%)")
        # TODO: Update progress indicator in view
        # self.view.update_progress(description, percentage)

    def _on_operation_completed(self):
        """Handle operation completion"""
        print("[RemoteDocsPresenter] Operation completed")
        # TODO: Hide progress indicator in view
        # self.view.hide_progress()
