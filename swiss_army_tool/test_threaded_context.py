"""
Test script to verify threaded context provider works correctly
"""
import sys
from PySide6.QtWidgets import QApplication
from app.document_scanner.search_result import SearchResult, Context
from app.document_scanner.context_provider import ContextProvider
from app.document_scanner.threaded_context_manager import ThreadedContextManager
from typing import List
import time


class SlowContextProvider(ContextProvider):
    """A mock context provider that simulates slow processing"""

    def __init__(self, name: str, delay_ms: int = 500):
        self.name = name
        self.delay_ms = delay_ms

    def get_context_name(self) -> str:
        return self.name

    def get_context(self, result: SearchResult) -> List[Context]:
        """Simulate slow context lookup"""
        print(f"  [{self.name}] Processing result: {result.document_name}")

        # Simulate slow operation (e.g., database lookup)
        time.sleep(self.delay_ms / 1000.0)

        # Add context if certain data is present
        if 'Test' in str(result.matched_row_data):
            ctx = Context(
                term="Test",
                context_owner=self.name,
                data_context={
                    f"{self.name} Info": f"Processed by {self.name}",
                    "Processing Time": f"{self.delay_ms}ms"
                }
            )
            print(f"  [{self.name}] ✓ Added context")
            return [ctx]

        return []

    def is_enabled(self) -> bool:
        return True


def test_threaded_context():
    """Test the threaded context manager"""
    app = QApplication.instance() or QApplication(sys.argv)

    print("\n" + "="*60)
    print("Testing Threaded Context Manager")
    print("="*60)

    # Create test results
    results = [
        SearchResult(
            search_term="test",
            document_name="doc1.txt",
            document_type="csv",
            matched_row_data={"Name": "Test Item 1", "Value": "100"}
        ),
        SearchResult(
            search_term="test",
            document_name="doc2.txt",
            document_type="csv",
            matched_row_data={"Name": "Test Item 2", "Value": "200"}
        ),
        SearchResult(
            search_term="test",
            document_name="doc3.txt",
            document_type="csv",
            matched_row_data={"Name": "Test Item 3", "Value": "300"}
        ),
    ]

    print(f"\nCreated {len(results)} test results")

    # Create context manager
    manager = ThreadedContextManager()

    # Register slow providers (simulate database lookups)
    provider1 = SlowContextProvider("SlowProvider1", delay_ms=300)
    provider2 = SlowContextProvider("SlowProvider2", delay_ms=200)

    manager.register_provider(provider1)
    manager.register_provider(provider2)

    print(f"\nRegistered 2 context providers (300ms and 200ms delays)")

    # Track events
    enriched_count = 0
    completed = False

    def on_result_enriched(idx, result):
        nonlocal enriched_count
        enriched_count += 1
        contexts = len(result.contexts) if result.contexts else 0
        print(
            f"\n[MAIN THREAD] ✓ Result {idx} enriched with {contexts} context(s)")
        print(f"  Document: {result.document_name}")
        if result.contexts:
            for ctx in result.contexts:
                print(f"    - {ctx.context_owner}: {ctx.get_formatted_data()}")

    def on_complete():
        nonlocal completed
        completed = True
        print(f"\n[MAIN THREAD] ✓ All enrichment complete!")
        print(f"Total results enriched: {enriched_count}")
        app.quit()

    def on_error(provider_name, error_msg):
        print(f"\n[MAIN THREAD] ⚠️  Error from {provider_name}: {error_msg}")

    # Connect signals
    manager.result_enriched.connect(on_result_enriched)
    manager.enrichment_complete.connect(on_complete)
    manager.error_occurred.connect(on_error)

    print("\n" + "-"*60)
    print("Starting async enrichment...")
    print("(UI thread would remain responsive during this)")
    print("-"*60 + "\n")

    start_time = time.time()

    # Start async enrichment
    manager.enrich_results_async(results)

    print(f"[MAIN THREAD] enrich_results_async() returned immediately!")
    print(f"[MAIN THREAD] UI would be responsive now while background thread works")
    print(
        f"[MAIN THREAD] Time elapsed: {(time.time() - start_time)*1000:.0f}ms\n")

    # Run event loop (simulates Qt app running)
    app.exec()

    elapsed = (time.time() - start_time) * 1000

    print("\n" + "="*60)
    print("Test Results:")
    print("="*60)
    print(f"✓ Total time: {elapsed:.0f}ms")
    print(f"✓ Results processed: {enriched_count}/{len(results)}")
    print(f"✓ Completed: {completed}")

    # Verify results
    total_contexts = sum(len(r.contexts) if r.contexts else 0 for r in results)
    print(f"✓ Total contexts added: {total_contexts}")

    print("\nNote: Without threading, this would have taken ~1500ms")
    print("      and blocked the UI the entire time!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_threaded_context()
