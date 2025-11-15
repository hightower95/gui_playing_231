"""
Threaded Context Manager for non-blocking context enrichment
"""
from PySide6.QtCore import QObject, QThread, Signal
from typing import List, Dict
from .context_provider import ContextProvider
from ..document_scanner.search_result import SearchResult, Context


class ContextWorker(QObject):
    """Worker that runs context enrichment in a separate thread"""

    # Signal emitted when a single result is enriched with context
    result_enriched = Signal(int, SearchResult)  # index, enriched_result

    # Signal emitted when all context enrichment is complete
    enrichment_complete = Signal()

    # Signal emitted on error
    error_occurred = Signal(str, str)  # provider_name, error_message

    def __init__(self, providers: List[ContextProvider], results: List[SearchResult]):
        super().__init__()
        self.providers = providers
        self.results = results
        self._should_stop = False

    def stop(self):
        """Request the worker to stop processing"""
        self._should_stop = True

    def process(self):
        """Process all results with all context providers (runs in thread)"""
        if not self.providers or not self.results:
            self.enrichment_complete.emit()
            return

        print(
            f"\n[ContextWorker] Starting enrichment of {len(self.results)} result(s) with {len(self.providers)} provider(s)")

        for idx, result in enumerate(self.results):
            if self._should_stop:
                print("[ContextWorker] Stopped by request")
                return

            # Make a working copy to avoid threading issues
            enriched_result = result
            contexts_added = 0

            for provider in self.providers:
                if self._should_stop:
                    return

                if not provider.is_enabled():
                    continue

                try:
                    # Call the context provider (this is the potentially slow part)
                    contexts = provider.get_context(enriched_result)

                    for ctx in contexts:
                        enriched_result.add_context(ctx)
                        contexts_added += 1
                        print(
                            f"  [ContextWorker] ✓ Added context from {ctx.context_owner} for '{ctx.term}'")

                except Exception as e:
                    error_msg = str(e)
                    print(
                        f"  [ContextWorker] ⚠️  Error from {provider.get_context_name()}: {error_msg}")
                    self.error_occurred.emit(
                        provider.get_context_name(), error_msg)

            # Emit enriched result (even if no contexts were added)
            if contexts_added > 0:
                print(
                    f"  [ContextWorker] Result {idx+1}/{len(self.results)} enriched with {contexts_added} context(s)")

            self.result_enriched.emit(idx, enriched_result)

        print(f"[ContextWorker] ✓ Enrichment complete")
        self.enrichment_complete.emit()


class ThreadedContextManager(QObject):
    """Manages context enrichment in a separate thread to avoid blocking UI"""

    # Signal emitted when a result is enriched (forwarded from worker)
    result_enriched = Signal(int, SearchResult)

    # Signal emitted when all enrichment is complete (forwarded from worker)
    enrichment_complete = Signal()

    # Signal emitted on error
    error_occurred = Signal(str, str)  # provider_name, error_message

    def __init__(self):
        super().__init__()
        self.providers: List[ContextProvider] = []
        self._thread = None
        self._worker = None

    def register_provider(self, provider: ContextProvider):
        """Register a context provider

        Args:
            provider: ContextProvider implementation
        """
        if provider not in self.providers:
            self.providers.append(provider)
            print(
                f"[ThreadedContextManager] ✓ Registered provider: {provider.get_context_name()}")

    def unregister_provider(self, provider: ContextProvider):
        """Unregister a context provider

        Args:
            provider: ContextProvider to remove
        """
        if provider in self.providers:
            self.providers.remove(provider)
            print(
                f"[ThreadedContextManager] Unregistered provider: {provider.get_context_name()}")

    def enrich_results_async(self, results: List[SearchResult]):
        """Enrich search results with context in a background thread

        This method returns immediately. Connect to the signals to receive results:
        - result_enriched: emitted for each enriched result
        - enrichment_complete: emitted when all processing is done
        - error_occurred: emitted if a provider encounters an error

        Args:
            results: List of SearchResult objects to enrich
        """
        # Stop any existing work (with safety check)
        try:
            self.stop_enrichment()
        except RuntimeError:
            # Thread already deleted, clear references
            self._thread = None
            self._worker = None

        if not self.providers:
            print("[ThreadedContextManager] No providers registered")
            self.enrichment_complete.emit()
            return

        if not results:
            print("[ThreadedContextManager] No results to enrich")
            self.enrichment_complete.emit()
            return

        # Create thread and worker
        self._thread = QThread()
        self._worker = ContextWorker(self.providers, results)

        # Move worker to thread
        self._worker.moveToThread(self._thread)

        # Connect signals
        self._thread.started.connect(self._worker.process)
        self._worker.result_enriched.connect(self._on_result_enriched)
        self._worker.enrichment_complete.connect(self._on_enrichment_complete)
        self._worker.error_occurred.connect(self._on_error)

        # Cleanup when done
        self._worker.enrichment_complete.connect(self._thread.quit)
        self._worker.enrichment_complete.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self._clear_references)

        # Start processing
        print(
            f"[ThreadedContextManager] Starting background enrichment of {len(results)} result(s)")
        self._thread.start()

    def _clear_references(self):
        """Clear thread and worker references after cleanup"""
        self._thread = None
        self._worker = None

    def stop_enrichment(self):
        """Stop any ongoing enrichment work"""
        if self._worker:
            try:
                self._worker.stop()
            except RuntimeError:
                pass  # Worker already deleted

        if self._thread:
            try:
                if self._thread.isRunning():
                    print(
                        "[ThreadedContextManager] Stopping background enrichment...")
                    self._thread.quit()
                    self._thread.wait(1000)  # Wait up to 1 second
            except RuntimeError:
                # Thread already deleted
                pass

    def _on_result_enriched(self, idx: int, result: SearchResult):
        """Handle enriched result from worker (runs in main thread)"""
        # Forward signal
        self.result_enriched.emit(idx, result)

    def _on_enrichment_complete(self):
        """Handle completion from worker (runs in main thread)"""
        print("[ThreadedContextManager] ✓ Background enrichment complete")
        # Forward signal
        self.enrichment_complete.emit()

    def _on_error(self, provider_name: str, error_msg: str):
        """Handle error from worker (runs in main thread)"""
        # Forward signal
        self.error_occurred.emit(provider_name, error_msg)

    def is_enriching(self) -> bool:
        """Check if enrichment is currently in progress

        Returns:
            True if enrichment thread is running
        """
        return self._thread is not None and self._thread.isRunning()

    def cleanup(self):
        """Clean up resources (call on shutdown)"""
        self.stop_enrichment()
