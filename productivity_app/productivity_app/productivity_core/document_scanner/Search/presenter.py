"""
Document Scanner Search Presenter
"""
from PySide6.QtCore import QObject
from productivity_core.document_scanner.Search.view import SearchView
from productivity_core.document_scanner.search_result import SearchResult, Context
from productivity_core.document_scanner.searchable_document import SearchableDocument
from productivity_core.document_scanner.context_provider import ContextProvider
from productivity_core.document_scanner.threaded_context_manager import ThreadedContextManager
from typing import List


class SearchPresenter(QObject):
    """Presenter for document search functionality"""

    def __init__(self, context, model):
        super().__init__()
        self.context = context
        self.model = model
        self.view = SearchView()

        # Threaded context manager for non-blocking context enrichment
        self.context_manager = ThreadedContextManager()

        # Connect context manager signals
        self.context_manager.result_enriched.connect(self._on_result_enriched)
        self.context_manager.enrichment_complete.connect(
            self._on_enrichment_complete)
        self.context_manager.error_occurred.connect(self._on_enrichment_error)

        # Store current results for updating
        self.current_results: List[SearchResult] = []

        # Connect view signals
        self.view.search_requested.connect(self.on_search)
        self.view.reload_requested.connect(self.on_reload_documents)
        self.view.open_document_requested.connect(self.on_open_document)

    def start_loading(self):
        """Initialize the search tab"""
        print("Document Scanner Search: Ready")
        searchable_docs = self.model.get_searchable_documents()
        self.view.update_document_count(len(searchable_docs))

    def on_documents_changed(self, searchable_documents: list):
        """Called when model finishes loading documents

        Args:
            searchable_documents: List of SearchableDocument objects from model
        """
        print(
            f"SEARCH: Received {len(searchable_documents)} loaded document(s)")
        self.view.update_document_count(len(searchable_documents))

    def on_reload_documents(self):
        """Handle reload all documents request"""
        print("\n🔄 Reloading all documents...")
        self.view.update_status("Reloading all documents...", "blue")
        self.model.reload_documents()
        self.view.update_status("Documents reloaded successfully", "green")

    def on_open_document(self, document_name: str):
        """Handle request to open a document in the default application

        Args:
            document_name: Name of the document to open
        """
        import os
        import subprocess
        import platform

        print(f"\n📂 Opening document: {document_name}")

        # Get the file path from the model
        searchable_docs = self.model.get_searchable_documents()

        file_path = None
        for doc in searchable_docs:
            if doc.file_name == document_name:
                file_path = doc.file_path
                break

        if not file_path:
            print(f"❌ Could not find file path for: {document_name}")
            self.view.update_status(
                f"Error: Could not find {document_name}", "red")
            return

        if not os.path.exists(file_path):
            print(f"❌ File does not exist: {file_path}")
            self.view.update_status(
                f"Error: File not found at {file_path}", "red")
            return

        try:
            # Open file with default application (platform-independent)
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])

            print(f"✓ Opened: {file_path}")
            self.view.update_status(f"Opened: {document_name}", "green")

        except Exception as e:
            print(f"❌ Error opening file: {e}")
            self.view.update_status(f"Error opening file: {e}", "red")

    def register_context_provider(self, provider: ContextProvider):
        """Register a context provider (e.g., Connector tab, EPD tab)

        Args:
            provider: ContextProvider implementation
        """
        self.context_manager.register_provider(provider)
        print(f"✓ Registered context provider: {provider.get_context_name()}")

    def _on_result_enriched(self, idx: int, result: SearchResult):
        """Handle a result that has been enriched with context in background thread

        Args:
            idx: Index of the result in current_results
            result: Enriched SearchResult object
        """
        # Update stored result
        if idx < len(self.current_results):
            self.current_results[idx] = result

            # Update the display for this result
            self.view.update_result(idx, result)

    def _on_enrichment_complete(self):
        """Handle completion of background context enrichment"""
        print("\n✓ Context enrichment complete")

        # Count results with context
        enriched_count = sum(
            1 for r in self.current_results if r.has_contexts())

        if enriched_count > 0:
            self.view.update_status(
                f"Found {len(self.current_results)} result(s) ({enriched_count} with context)",
                "green"
            )

    def _on_enrichment_error(self, provider_name: str, error_msg: str):
        """Handle error during context enrichment

        Args:
            provider_name: Name of the provider that encountered an error
            error_msg: Error message
        """
        print(
            f"⚠️  Context enrichment error from {provider_name}: {error_msg}")

    def on_search(self, search_term: str):
        """Handle search request

        Args:
            search_term: Term to search for
        """
        print(f"\n{'='*60}")
        print(f"SEARCH STARTED: '{search_term}'")
        print(f"{'='*60}")

        # Add to search history
        self.model.add_to_search_history(search_term)

        # Get searchable documents from model
        searchable_documents = self.model.get_searchable_documents()

        if not searchable_documents:
            print("❌ No documents loaded")
            self.view.update_status("No documents configured", "orange")
            return

        print(f"📚 Searching {len(searchable_documents)} document(s)")

        # Clear previous results
        self.view.clear_results()
        self.view.show_progress(True)
        self.view.update_progress(0)
        self.view.update_status(
            f"Searching {len(searchable_documents)} document(s)...", "blue")

        # Search all documents
        all_results = []
        total_docs = len(searchable_documents)

        for idx, searchable_doc in enumerate(searchable_documents):
            # Update progress
            progress = int((idx / total_docs) * 100)
            self.view.update_progress(progress)

            print(f"\n[{idx+1}/{total_docs}] {searchable_doc.file_name}")

            # Search document (it handles preconditions internally)
            results = searchable_doc.search(search_term)
            if results:
                print(f"  ✅ Found {len(results)} result(s)")
            all_results.extend(results)

        # Display results immediately (without context)
        print(f"\n{'='*60}")
        print(f"SEARCH RESULTS: {len(all_results)} total match(es)")
        print(f"{'='*60}")

        for result in all_results:
            print(f"  • {result.document_name}: {result.get_formatted_data()}")

        # Store results
        self.current_results = all_results

        # Display results in view
        self.view.display_results(all_results)

        # Update status
        self.view.update_progress(100)
        self.view.show_progress(False)

        if all_results:
            self.view.update_status(
                f"Found {len(all_results)} result(s) - enriching with context...",
                "blue"
            )
        else:
            self.view.update_status(
                f"No results found in {len(searchable_documents)} document(s)",
                "orange"
            )

        # Start background context enrichment (non-blocking)
        if all_results:
            self.context_manager.enrich_results_async(all_results)

        print(f"\n{'='*60}")
        print(f"SEARCH COMPLETE")
        print(f"{'='*60}\n")

    def get_all_results(self) -> List[SearchResult]:
        """Get all current search results

        Returns:
            List of SearchResult dataclass objects
        """
        # TODO: Store results in presenter
        return []
