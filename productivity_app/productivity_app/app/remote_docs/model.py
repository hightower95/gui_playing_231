"""
Remote Docs Model

Handles data management for remote document storage and retrieval.
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import time
from PySide6.QtCore import QObject, Signal, QThread, QTimer


class RemoteDocumentWorker(QThread):
    """Worker thread for remote document operations to prevent UI blocking"""

    # Signals for different operations
    refresh_completed = Signal(list)  # List of documents
    refresh_failed = Signal(str)  # Error message
    upload_completed = Signal(str)  # Document name
    upload_failed = Signal(str, str)  # Document name, error message
    download_completed = Signal(str, str)  # Document name, local path
    download_failed = Signal(str, str)  # Document name, error message
    # Operation description, progress percentage
    progress_updated = Signal(str, int)

    def __init__(self):
        super().__init__()
        self._operation = None
        self._operation_data = None

    def refresh_documents(self):
        """Start document refresh operation"""
        self._operation = "refresh"
        self._operation_data = None
        self.start()

    def upload_document(self, file_path: str, doc_name: str, category: str,
                        description: str = None, tags: List[str] = None):
        """Start document upload operation"""
        self._operation = "upload"
        self._operation_data = {
            'file_path': file_path,
            'doc_name': doc_name,
            'category': category,
            'description': description,
            'tags': tags or []
        }
        self.start()

    def download_document(self, doc_name: str, version: str, save_path: str):
        """Start document download operation"""
        self._operation = "download"
        self._operation_data = {
            'doc_name': doc_name,
            'version': version,
            'save_path': save_path
        }
        self.start()

    def run(self):
        """Execute the requested operation in background thread"""
        try:
            if self._operation == "refresh":
                self._do_refresh()
            elif self._operation == "upload":
                self._do_upload()
            elif self._operation == "download":
                self._do_download()
        except Exception as e:
            # Emit appropriate error signal based on operation
            if self._operation == "refresh":
                self.refresh_failed.emit(str(e))
            elif self._operation == "upload":
                doc_name = self._operation_data.get('doc_name', 'Unknown')
                self.upload_failed.emit(doc_name, str(e))
            elif self._operation == "download":
                doc_name = self._operation_data.get('doc_name', 'Unknown')
                self.download_failed.emit(doc_name, str(e))

    def _do_refresh(self):
        """Perform document refresh (simulated remote operation)"""
        self.progress_updated.emit("Connecting to remote server...", 20)
        time.sleep(1)  # Simulate network delay

        self.progress_updated.emit("Fetching document list...", 50)
        time.sleep(2)  # Simulate remote query

        self.progress_updated.emit("Processing documents...", 80)
        time.sleep(0.5)  # Simulate processing

        # TODO: Replace with actual remote API call
        # For now, return sample updated data
        from datetime import datetime
        updated_docs = self._create_sample_documents()

        self.progress_updated.emit("Refresh complete", 100)
        self.refresh_completed.emit(updated_docs)

    def _do_upload(self):
        """Perform document upload (simulated remote operation)"""
        data = self._operation_data
        doc_name = data['doc_name']

        self.progress_updated.emit(f"Preparing {doc_name} for upload...", 10)
        time.sleep(0.5)

        self.progress_updated.emit(f"Uploading {doc_name}...", 30)
        time.sleep(2)  # Simulate upload time

        self.progress_updated.emit(f"Processing {doc_name}...", 80)
        time.sleep(1)  # Simulate server processing

        # TODO: Replace with actual upload logic
        self.progress_updated.emit(f"Upload complete", 100)
        self.upload_completed.emit(doc_name)

    def _do_download(self):
        """Perform document download (simulated remote operation)"""
        data = self._operation_data
        doc_name = data['doc_name']
        save_path = data['save_path']

        self.progress_updated.emit(f"Locating {doc_name}...", 20)
        time.sleep(0.5)

        self.progress_updated.emit(f"Downloading {doc_name}...", 60)
        time.sleep(1.5)  # Simulate download time

        self.progress_updated.emit(f"Saving to {save_path}...", 90)
        time.sleep(0.5)

        # TODO: Replace with actual download logic
        self.progress_updated.emit("Download complete", 100)
        self.download_completed.emit(doc_name, save_path)

    def _create_sample_documents(self):
        """Create sample documents for testing (same as model's sample data)"""
        # This would be replaced by actual remote data parsing
        # For now, return the same sample structure as the model
        return []  # Will be populated by the actual refresh logic


@dataclass
class DocumentVersion:
    """Represents a single version of a document"""
    version: str
    upload_date: datetime
    size_bytes: int
    checksum: str
    uploader: str
    description: Optional[str] = None


@dataclass
class Document:
    """Represents a document with multiple versions"""
    name: str
    category: str
    description: Optional[str]
    versions: List[DocumentVersion]
    tags: List[str]

    @property
    def latest_version(self) -> Optional[DocumentVersion]:
        """Get the most recent version of this document"""
        if not self.versions:
            return None
        return max(self.versions, key=lambda v: v.upload_date)

    @property
    def version_count(self) -> int:
        """Get number of versions for this document"""
        return len(self.versions)


class RemoteDocsModel(QObject):
    """Model for managing remote documents and their versions"""

    # Signals
    documents_updated = Signal()
    document_uploaded = Signal(str)  # document name
    document_downloaded = Signal(str, str)  # document name, local path
    error_occurred = Signal(str)  # error message
    operation_started = Signal(str)  # operation description
    operation_progress = Signal(str, int)  # operation description, progress %
    operation_completed = Signal()  # operation finished

    def __init__(self):
        super().__init__()
        self._documents: List[Document] = []
        self._worker = RemoteDocumentWorker()
        self._is_refreshing = False
        self._initialize_sample_data()
        self._connect_worker_signals()

    def _connect_worker_signals(self):
        """Connect worker thread signals to model handlers"""
        self._worker.refresh_completed.connect(self._on_refresh_completed)
        self._worker.refresh_failed.connect(self._on_refresh_failed)
        self._worker.upload_completed.connect(self._on_upload_completed)
        self._worker.upload_failed.connect(self._on_upload_failed)
        self._worker.download_completed.connect(self._on_download_completed)
        self._worker.download_failed.connect(self._on_download_failed)
        self._worker.progress_updated.connect(self.operation_progress.emit)

    @property
    def is_refreshing(self) -> bool:
        """Check if a refresh operation is currently in progress"""
        return self._is_refreshing

    def _initialize_sample_data(self):
        """Initialize with some sample documents for development/testing"""
        # Sample document 1
        doc1_versions = [
            DocumentVersion(
                version="1.0",
                upload_date=datetime(2024, 10, 1, 10, 0),
                size_bytes=1024000,
                checksum="abc123",
                uploader="john.doe",
                description="Initial version"
            ),
            DocumentVersion(
                version="1.1",
                upload_date=datetime(2024, 11, 1, 14, 30),
                size_bytes=1056000,
                checksum="def456",
                uploader="jane.smith",
                description="Bug fixes and improvements"
            )
        ]

        doc1 = Document(
            name="User Manual",
            category="Documentation",
            description="Complete user manual for the application",
            versions=doc1_versions,
            tags=["manual", "documentation", "help"]
        )

        # Sample document 2
        doc2_versions = [
            DocumentVersion(
                version="2.0",
                upload_date=datetime(2024, 11, 5, 9, 15),
                size_bytes=2048000,
                checksum="ghi789",
                uploader="bob.wilson",
                description="Major update with new features"
            )
        ]

        doc2 = Document(
            name="API Reference",
            category="Technical",
            description="Complete API reference documentation",
            versions=doc2_versions,
            tags=["api", "reference", "technical"]
        )

        # Sample document 3
        doc3_versions = [
            DocumentVersion(
                version="1.0",
                upload_date=datetime(2024, 10, 15, 16, 45),
                size_bytes=512000,
                checksum="jkl012",
                uploader="alice.brown",
                description="First release"
            )
        ]

        doc3 = Document(
            name="Installation Guide",
            category="Documentation",
            description="Step-by-step installation instructions",
            versions=doc3_versions,
            tags=["installation", "setup", "guide"]
        )

        self._documents = [doc1, doc2, doc3]

    @property
    def list_documents(self) -> List[Document]:
        """Get list of all documents with their versions"""
        return self._documents.copy()

    def get_document_by_name(self, name: str) -> Optional[Document]:
        """Get a specific document by name

        Args:
            name: Name of the document to find

        Returns:
            Document if found, None otherwise
        """
        for doc in self._documents:
            if doc.name == name:
                return doc
        return None

    def get_documents_by_category(self, category: str) -> List[Document]:
        """Get all documents in a specific category

        Args:
            category: Category to filter by

        Returns:
            List of documents in the category
        """
        return [doc for doc in self._documents if doc.category == category]

    def get_documents_by_tag(self, tag: str) -> List[Document]:
        """Get all documents with a specific tag

        Args:
            tag: Tag to filter by

        Returns:
            List of documents with the tag
        """
        return [doc for doc in self._documents if tag in doc.tags]

    def add_document_version(self, doc_name: str, version: DocumentVersion) -> bool:
        """Add a new version to an existing document

        Args:
            doc_name: Name of the document
            version: New version to add

        Returns:
            True if successful, False if document not found
        """
        doc = self.get_document_by_name(doc_name)
        if doc:
            doc.versions.append(version)
            doc.versions.sort(key=lambda v: v.upload_date)
            self.documents_updated.emit()
            return True
        return False

    def create_document(self, document: Document) -> bool:
        """Create a new document

        Args:
            document: Document to create

        Returns:
            True if successful, False if document already exists
        """
        if self.get_document_by_name(document.name):
            return False  # Document already exists

        self._documents.append(document)
        self.documents_updated.emit()
        return True

    def delete_document(self, doc_name: str) -> bool:
        """Delete a document and all its versions

        Args:
            doc_name: Name of document to delete

        Returns:
            True if successful, False if document not found
        """
        doc = self.get_document_by_name(doc_name)
        if doc:
            self._documents.remove(doc)
            self.documents_updated.emit()
            return True
        return False

    def get_categories(self) -> List[str]:
        """Get list of all unique categories"""
        categories = {doc.category for doc in self._documents}
        return sorted(list(categories))

    def get_all_tags(self) -> List[str]:
        """Get list of all unique tags"""
        all_tags = set()
        for doc in self._documents:
            all_tags.update(doc.tags)
        return sorted(list(all_tags))

    def search_documents(self, query: str) -> List[Document]:
        """Search documents by name, description, or tags

        Args:
            query: Search query string

        Returns:
            List of matching documents
        """
        query = query.lower()
        results = []

        for doc in self._documents:
            # Search in name, description, and tags
            if (query in doc.name.lower()
                or (doc.description and query in doc.description.lower())
                    or any(query in tag.lower() for tag in doc.tags)):
                results.append(doc)

        return results

    def refresh_documents(self):
        """Refresh document list from remote source (async operation)"""
        if self._is_refreshing:
            print("[RemoteDocsModel] Refresh already in progress, ignoring request")
            return

        print("[RemoteDocsModel] Starting async document refresh...")
        self._is_refreshing = True
        self.operation_started.emit("Refreshing documents...")
        self._worker.refresh_documents()

    def upload_document(self, file_path: str, doc_name: str, category: str,
                        description: str = None, tags: List[str] = None):
        """Upload a new document (async operation)

        Args:
            file_path: Path to local file to upload
            doc_name: Name for the document
            category: Document category
            description: Optional description
            tags: Optional list of tags
        """
        if self._worker.isRunning():
            self.error_occurred.emit(
                "Another operation is in progress. Please wait.")
            return

        print(
            f"[RemoteDocsModel] Starting async upload: {file_path} -> {doc_name}")
        self.operation_started.emit(f"Uploading {doc_name}...")
        self._worker.upload_document(
            file_path, doc_name, category, description, tags)

    def download_document(self, doc_name: str, version: str, save_path: str):
        """Download a specific document version (async operation)

        Args:
            doc_name: Name of document to download
            version: Version to download
            save_path: Local path to save the file
        """
        if self._worker.isRunning():
            self.error_occurred.emit(
                "Another operation is in progress. Please wait.")
            return

        print(
            f"[RemoteDocsModel] Starting async download: {doc_name} v{version} -> {save_path}")
        self.operation_started.emit(f"Downloading {doc_name}...")
        self._worker.download_document(doc_name, version, save_path)

    def _on_refresh_completed(self, updated_documents: List):
        """Handle successful refresh completion"""
        print(
            f"[RemoteDocsModel] Refresh completed, got {len(updated_documents)} documents")
        # TODO: Update self._documents with the new data from remote
        self._is_refreshing = False
        self.operation_completed.emit()
        self.documents_updated.emit()

    def _on_refresh_failed(self, error_message: str):
        """Handle refresh failure"""
        print(f"[RemoteDocsModel] Refresh failed: {error_message}")
        self._is_refreshing = False
        self.operation_completed.emit()
        self.error_occurred.emit(
            f"Failed to refresh documents: {error_message}")

    def _on_upload_completed(self, doc_name: str):
        """Handle successful upload completion"""
        print(f"[RemoteDocsModel] Upload completed: {doc_name}")
        self.operation_completed.emit()
        self.document_uploaded.emit(doc_name)
        # Trigger refresh to get updated document list
        # Small delay before refresh
        QTimer.singleShot(500, self.refresh_documents)

    def _on_upload_failed(self, doc_name: str, error_message: str):
        """Handle upload failure"""
        print(
            f"[RemoteDocsModel] Upload failed for {doc_name}: {error_message}")
        self.operation_completed.emit()
        self.error_occurred.emit(
            f"Failed to upload {doc_name}: {error_message}")

    def _on_download_completed(self, doc_name: str, local_path: str):
        """Handle successful download completion"""
        print(
            f"[RemoteDocsModel] Download completed: {doc_name} -> {local_path}")
        self.operation_completed.emit()
        self.document_downloaded.emit(doc_name, local_path)

    def _on_download_failed(self, doc_name: str, error_message: str):
        """Handle download failure"""
        print(
            f"[RemoteDocsModel] Download failed for {doc_name}: {error_message}")
        self.operation_completed.emit()
        self.error_occurred.emit(
            f"Failed to download {doc_name}: {error_message}")
