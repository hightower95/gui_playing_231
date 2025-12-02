"""
Test script for FeatureFlagsManager and TelemetricsManager

Tests the new global managers accessible through app context.
"""
from productivity_app.productivity_core.core.app_context import AppContext
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent))


def test_feature_flags():
    """Test FeatureFlagsManager"""
    print("\n=== Testing FeatureFlagsManager ===\n")

    # Create context (auto-initializes managers)
    context = AppContext()
    feature_flags = context.get('feature_flags')

    # Test 1: Get flag value
    print("Test 1: Get flag value")
    advanced_search_enabled = feature_flags.get(
        'connectors', 'advanced_search')
    print(f"  Connector Advanced Search enabled: {advanced_search_enabled}")

    # Test 2: Set flag value
    print("\nTest 2: Set flag value")
    result = feature_flags.set('connectors', 'advanced_search', True)
    print(f"  Set result: {result}")
    new_value = feature_flags.get('connectors', 'advanced_search')
    print(f"  New value: {new_value}")

    # Test 3: Subscribe to changes
    print("\nTest 3: Subscribe to flag changes")

    def on_advanced_search_changed(enabled):
        print(f"  Callback: Advanced search changed to {enabled}")

    feature_flags.subscribe(
        'connectors', 'advanced_search', on_advanced_search_changed)

    # This should trigger the callback
    print("  Setting flag to False...")
    feature_flags.set('connectors', 'advanced_search', False)

    # Test 4: Get module flags
    print("\nTest 4: Get all flags for module")
    connector_flags = feature_flags.get_module_flags('connectors')
    print(f"  Connector flags: {connector_flags}")

    # Test 5: Get flag metadata
    print("\nTest 5: Get flag metadata")
    metadata = feature_flags.get_flag_metadata('connectors', 'advanced_search')
    print(f"  Metadata: {metadata}")

    print("\n✅ FeatureFlagsManager tests passed!")


def test_telemetrics():
    """Test TelemetricsManager"""
    print("\n=== Testing TelemetricsManager ===\n")

    context = AppContext()
    telemetrics = context.get('telemetrics')

    # Test 1: Record events
    print("Test 1: Record events")
    telemetrics.push('connector_search', {
        'connector_type': 'database',
        'query_time_ms': 250,
        'result_count': 42
    }, tags=['connector', 'search'])

    telemetrics.push('document_scan', {
        'documents': 5,
        'pages': 127
    }, tags=['document', 'scan'])

    telemetrics.push('connector_search', {
        'connector_type': 'api',
        'query_time_ms': 150,
        'result_count': 18
    }, tags=['connector', 'search', 'api'])

    print("  Pushed 3 events")

    # Test 2: Get event count
    print("\nTest 2: Get event counts")
    total_count = telemetrics.get_event_count()
    search_count = telemetrics.get_event_count('connector_search')
    print(f"  Total events: {total_count}")
    print(f"  Connector searches: {search_count}")

    # Test 3: Get events
    print("\nTest 3: Get events")
    events = telemetrics.get_events('connector_search')
    print(f"  Retrieved {len(events)} search events")
    for event in events:
        print(f"    - {event['data']}")

    # Test 4: Get events by tag
    print("\nTest 4: Get events by tag")
    api_events = telemetrics.get_events_by_tag('api')
    print(f"  Events with 'api' tag: {len(api_events)}")

    # Test 5: Session summary
    print("\nTest 5: Session summary")
    summary = telemetrics.get_session_summary()
    print(f"  Total events: {summary['total_events']}")
    print(f"  Event types: {summary['event_types']}")

    # Test 6: Event summary by type
    print("\nTest 6: Event summary by type")
    type_summary = telemetrics.get_event_summary_by_type()
    for event_type, stats in type_summary.items():
        print(
            f"  {event_type}: {stats['count']} occurrences, tags: {stats['tags']}")

    print("\n✅ TelemetricsManager tests passed!")


if __name__ == '__main__':
    try:
        test_feature_flags()
        test_telemetrics()
        print("\n" + "="*50)
        print("✅ All tests passed!")
        print("="*50)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
