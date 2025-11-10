#!/usr/bin/env python3
"""
Test the venv step threading functionality in isolation to debug the hanging issue.
"""

import sys
import threading
import queue
import time
from pathlib import Path

# Add the installer path
sys.path.insert(0, str(Path(__file__).parent / "alternative_app_installer" / "installer"))

from install_gui.steps.venv_step import VenvCreationWorker

def test_worker_thread():
    """Test the worker thread functionality independently"""
    print("=== Testing VenvCreationWorker Threading ===")
    
    # Create queues
    progress_queue = queue.Queue()
    result_queue = queue.Queue()
    
    # Create a test directory
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        test_install_path = Path(temp_dir) / "test_installation"
        test_install_path.mkdir(exist_ok=True)
        venv_path = test_install_path / ".test_venv"
        
        print(f"Test installation path: {test_install_path}")
        print(f"Virtual environment path: {venv_path}")
        
        # Create worker
        worker = VenvCreationWorker(
            python_executable=sys.executable,
            venv_path=str(venv_path),
            installation_path=str(test_install_path),
            progress_queue=progress_queue,
            result_queue=result_queue
        )
        
        print(f"Worker created: {worker}")
        print(f"Worker daemon: {worker.daemon}")
        
        # Start worker
        print("Starting worker thread...")
        worker.start()
        print(f"Worker started, thread ID: {worker.ident}")
        
        # Monitor progress with timeout
        start_time = time.time()
        timeout = 150  # 2.5 minutes
        
        print("\n=== Monitoring Progress ===")
        finished = False
        
        while not finished and (time.time() - start_time) < timeout:
            # Check progress messages
            try:
                while True:
                    message = progress_queue.get_nowait()
                    print(f"PROGRESS: {message}")
            except queue.Empty:
                pass
            
            # Check for result
            try:
                success, message = result_queue.get_nowait()
                print(f"\nRESULT: Success={success}, Message={message}")
                finished = True
            except queue.Empty:
                pass
            
            # Check if worker is still alive
            if not worker.is_alive() and finished == False:
                print(f"\n❌ Worker thread died unexpectedly!")
                break
                
            time.sleep(0.5)  # Check every 500ms
        
        if not finished:
            print(f"\n⏰ Test timed out after {timeout} seconds")
            print(f"Worker is alive: {worker.is_alive()}")
            
        # Try to join worker
        try:
            worker.join(timeout=5)
            print("Worker joined successfully")
        except:
            print("Worker join failed")
        
        print(f"\nVenv exists: {venv_path.exists()}")
        if venv_path.exists():
            print(f"Venv contents: {list(venv_path.iterdir())}")

if __name__ == "__main__":
    test_worker_thread()