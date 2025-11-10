"""
Test script for the ping module
"""
import time
from ping import PingController


def test_output_handler(text):
    """Simple output handler for testing"""
    print(f"RECEIVED: {text.strip()}")


def main():
    """Test the ping functionality"""
    print("🧪 Testing ping module...")
    print("=" * 50)

    # Create ping controller
    controller = PingController(test_output_handler)

    # Test with Google DNS
    print("Starting ping to 8.8.8.8...")
    success = controller.start_pinging("8.8.8.8")

    if success:
        print("✅ Ping started successfully!")
        print("⏱️ Running for 10 seconds...")

        # Let it run for 10 seconds
        time.sleep(10)

        print("🛑 Stopping ping...")
        controller.stop_pinging()

        print("✅ Test completed!")
    else:
        print("❌ Failed to start ping")

    print("=" * 50)


if __name__ == "__main__":
    main()
