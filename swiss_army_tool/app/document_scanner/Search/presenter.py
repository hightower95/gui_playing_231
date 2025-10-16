"""
Document Scanner Search Presenter
"""
from PySide6.QtCore import QObject
from app.document_scanner.Search.view import SearchView
from app.document_scanner.search_result import SearchResult, Context
from app.document_scanner.searchable_document import SearchableDocument
from app.document_scanner.context_provider import ContextProvider
from typing import List


class SearchPresenter(QObject):
    """Presenter for document search functionality"""
    
    def __init__(self, context, model):
        super().__init__()
        self.context = context
        self.model = model
        self.view = SearchView()
        self.context_providers: List[ContextProvider] = []  # Modules that can add context
        
        # Connect view signals
        self.view.search_requested.connect(self.on_search)
        self.view.reload_requested.connect(self.on_reload_documents)
    
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
        print(f"SEARCH: Received {len(searchable_documents)} loaded document(s)")
        self.view.update_document_count(len(searchable_documents))
    
    def on_reload_documents(self):
        """Handle reload all documents request"""
        print("\n🔄 Reloading all documents...")
        self.view.update_status("Reloading all documents...", "blue")
        self.model.reload_documents()
        self.view.update_status("Documents reloaded successfully", "green")
    
    def register_context_provider(self, provider: ContextProvider):
        """Register a context provider (e.g., Connector tab, EPD tab)
        
        Args:
            provider: ContextProvider implementation
        """
        if provider not in self.context_providers:
            self.context_providers.append(provider)
            print(f"✓ Registered context provider: {provider.get_context_name()}")
    
    def _enrich_results_with_context(self, results: List[SearchResult]):
        """Add context from registered providers to search results
        
        Args:
            results: List of SearchResult objects to enrich
        """
        if not self.context_providers:
            return
        
        print(f"\n🔍 Enriching {len(results)} result(s) with context...")
        
        for result in results:
            for provider in self.context_providers:
                if not provider.is_enabled():
                    continue
                
                try:
                    contexts = provider.get_context(result)
                    for ctx in contexts:
                        result.add_context(ctx)
                        print(f"  ✓ Added context from {ctx.context_owner} for term '{ctx.term}'")
                except Exception as e:
                    print(f"  ⚠️  Error getting context from {provider.get_context_name()}: {e}")
    
    def on_search(self, search_term: str):
        """Handle search request
        
        Args:
            search_term: Term to search for
        """
        print(f"\n{'='*60}")
        print(f"SEARCH STARTED: '{search_term}'")
        print(f"{'='*60}")
        
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
        self.view.update_status(f"Searching {len(searchable_documents)} document(s)...", "blue")
        
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
        
        # Enrich results with context from other modules
        self._enrich_results_with_context(all_results)
        
        # Display results
        print(f"\n{'='*60}")
        print(f"SEARCH RESULTS: {len(all_results)} total match(es)")
        print(f"{'='*60}")
        
        for result in all_results:
            ctx_info = f" (+{len(result.contexts)} context)" if result.has_contexts() else ""
            print(f"  • {result.document_name}: {result.get_formatted_data()}{ctx_info}")
        
        # Use new display method
        self.view.display_results(all_results)
        
        # Update status
        self.view.update_progress(100)
        self.view.show_progress(False)
        
        if all_results:
            self.view.update_status(
                f"Found {len(all_results)} result(s) across {len(searchable_documents)} document(s)",
                "green"
            )
        else:
            self.view.update_status(
                f"No results found in {len(searchable_documents)} document(s)",
                "orange"
            )
        
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
