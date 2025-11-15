"""
Document Scanner Model - Manages searchable documents
"""
from PySide6.QtCore import QObject, Signal, QThread
from typing import List, Dict, Any
from ..document_scanner.searchable_document import SearchableDocument
from ..core.config_manager import DocumentScannerConfig


class DocumentLoaderThread(QThread):
    """Background thread for loading documents"""

    # Signals
    documents_loaded = Signal(list)  # List of SearchableDocument objects
    progress = Signal(int, str)  # Progress (index, file_name)
    error = Signal(str)  # Error message

    def __init__(self, document_configs: List[Dict[str, Any]]):
        super().__init__()
        self.document_configs = document_configs

    def run(self):
        """Load documents in background thread"""
        try:
            searchable_docs = []
            total = len(self.document_configs)

            for idx, config in enumerate(self.document_configs):
                file_name = config.get('file_name', 'Unknown')
                self.progress.emit(idx + 1, file_name)

                # Create SearchableDocument (loads the file)
                searchable_doc = SearchableDocument(config)
                searchable_docs.append(searchable_doc)

            # Emit loaded documents
            self.documents_loaded.emit(searchable_docs)

        except Exception as e:
            self.error.emit(f"Error loading documents: {str(e)}")
            import traceback
            traceback.print_exc()


class DocumentScannerModel(QObject):
    """Model for managing document scanner data"""

    # Signals
    documents_changed = Signal(list)  # List of SearchableDocument objects
    loading_started = Signal()
    loading_finished = Signal()
    loading_progress = Signal(int, int, str)  # current, total, message
    search_history_changed = Signal()  # Emitted when search history is updated

    def __init__(self):
        super().__init__()
        self.searchable_documents = []  # List of SearchableDocument objects
        self.document_configs = []  # Raw config data
        self.loader_thread = None

    def load_from_config(self):
        """Load documents from configuration file"""
        print("\n" + "="*60)
        print("MODEL: Loading documents from config")
        print("="*60)

        # Load config data
        self.document_configs = DocumentScannerConfig.load_documents()

        if not self.document_configs:
            print("ℹ️  No saved document configurations found")
            self.searchable_documents = []
            self.documents_changed.emit(self.searchable_documents)
            return

        print(f"Found {len(self.document_configs)} document(s) in config")

        # Start background loading
        self._load_documents_async(self.document_configs)

    def _load_documents_async(self, configs: List[Dict[str, Any]]):
        """Load documents in background thread"""
        if self.loader_thread and self.loader_thread.isRunning():
            print("⚠️  Loader thread already running, waiting...")
            self.loader_thread.wait()

        self.loading_started.emit()

        # Create and start loader thread
        self.loader_thread = DocumentLoaderThread(configs)
        self.loader_thread.documents_loaded.connect(self._on_documents_loaded)
        self.loader_thread.progress.connect(self._on_loading_progress)
        self.loader_thread.error.connect(self._on_loading_error)
        self.loader_thread.finished.connect(self._on_thread_finished)

        print(
            f"🚀 Starting background thread to load {len(configs)} document(s)")
        self.loader_thread.start()

    def _on_documents_loaded(self, searchable_docs: List[SearchableDocument]):
        """Handle documents loaded from thread"""
        self.searchable_documents = searchable_docs

        print(f"\n✅ Loaded {len(searchable_docs)} document(s) into memory")
        for doc in searchable_docs:
            print(f"   • {doc.get_info()}")

        self.documents_changed.emit(self.searchable_documents)

    def _on_loading_progress(self, current: int, file_name: str):
        """Handle loading progress update"""
        total = len(self.document_configs)
        print(f"  [{current}/{total}] Loading: {file_name}")
        self.loading_progress.emit(current, total, file_name)

    def _on_loading_error(self, error_msg: str):
        """Handle loading error"""
        print(f"❌ {error_msg}")

    def _on_thread_finished(self):
        """Handle thread completion"""
        print("✓ Background loading thread finished")
        self.loading_finished.emit()

    def add_document(self, config: Dict[str, Any]):
        """Add a new document configuration"""
        from datetime import datetime

        # Add timestamp
        config['added_date'] = datetime.now().isoformat()

        # Add to configs
        self.document_configs.append(config)

        # Save to file
        DocumentScannerConfig.save_documents(self.document_configs)

        # Reload all documents
        self._load_documents_async(self.document_configs)

    def remove_document(self, index: int):
        """Remove a document by index"""
        if 0 <= index < len(self.document_configs):
            removed = self.document_configs.pop(index)
            print(f"Removed document: {removed.get('file_name', 'Unknown')}")

            # Save to file
            DocumentScannerConfig.save_documents(self.document_configs)

            # Reload all documents
            self._load_documents_async(self.document_configs)

    def get_searchable_documents(self) -> List[SearchableDocument]:
        """Get list of searchable documents"""
        return self.searchable_documents

    def get_document_configs(self) -> List[Dict[str, Any]]:
        """Get raw document configurations"""
        return self.document_configs

    def reload_documents(self):
        """Reload all documents from disk"""
        if self.document_configs:
            print("♻️  Reloading documents...")
            self._load_documents_async(self.document_configs)

    # History Management
    def get_search_history(self) -> List[str]:
        """Get search history (most recent first)

        Returns:
            List of search terms (max 10)
        """
        from ..core.config_manager import DocumentScannerConfig
        history = DocumentScannerConfig.load_search_history()
        return history

    def add_to_search_history(self, search_term: str):
        """Add a search term to history

        Args:
            search_term: The search term to add
        """
        from ..core.config_manager import DocumentScannerConfig

        # Get current history
        history = DocumentScannerConfig.load_search_history()

        # Remove if already exists (to move to front)
        if search_term in history:
            history.remove(search_term)

        # Add to front
        history.insert(0, search_term)

        # Keep only last 10
        history = history[:10]

        # Save
        DocumentScannerConfig.save_search_history(history)

        # Emit signal to notify History view
        self.search_history_changed.emit()

    def clear_search_history(self):
        """Clear all search history"""
        from ..core.config_manager import DocumentScannerConfig
        DocumentScannerConfig.save_search_history([])

        # Emit signal to notify History view
        self.search_history_changed.emit()
