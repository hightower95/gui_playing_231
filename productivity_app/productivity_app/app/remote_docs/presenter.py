"""
Remote Docs Presenter

Handles business logic for remote document management.
"""
from PySide6.QtCore import QObject
from .view import RemoteDocsView


class RemoteDocsPresenter(QObject):
    """Presenter for Remote Docs tab"""

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.title = "Remote Docs"

        # Create view
        self.view = RemoteDocsView()

        # Initialize upload section visibility based on feature flag
        self._update_upload_visibility()

        # TODO: Initialize model when ready
        # self.model = RemoteDocsModel()

        # TODO: Connect signals when model is ready
        # self.view.upload_requested.connect(self.on_upload)
        # self.view.download_requested.connect(self.on_download)

    def _update_upload_visibility(self):
        """Update upload section visibility based on feature flag"""
        from app.tabs.settings_tab import FeatureFlagsConfig

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
        # TODO: Implement download logic
        pass
