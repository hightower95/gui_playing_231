"""
Unit tests for LibraryInstallationStep - Test pip report parsing and worker behavior

Tests:
- _parse_install_report with various JSON scenarios
- LibraryInstallationWorker result tuple behavior
- Mock pip command execution and report generation
"""
import unittest
import json
import queue
import threading
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

# Import the classes to test
from .libray_step import InstallLibraryStep, LibraryInstallationWorker


class TestParseInstallReport(unittest.TestCase):
    """Test the _parse_install_report method with various JSON scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a mock step instance with minimal required attributes
        self.mock_settings = Mock()
        self.mock_shared_state = {}
        self.step = InstallLibraryStep(self.mock_settings, self.mock_shared_state)

    def test_parse_install_report_pypi_only(self):
        """Test parsing report with only PyPI URLs"""
        report_data = {
            "install": [
                {
                    "download_info": {
                        "url": "https://files.pythonhosted.org/packages/requests-2.31.0-py3-none-any.whl"
                    },
                    "metadata": {
                        "name": "requests"
                    }
                }
            ],
            "environment_info": {
                "implementation_name": "cpython",
                "implementation_version": "3.11.0"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report_data, f)
            report_path = f.name

        try:
            result = self.step._parse_install_report(report_path)
            self.assertEqual(result, 'PyPI')
        finally:
            Path(report_path).unlink()

    def test_parse_install_report_local_index(self):
        """Test parsing report with local index URL"""
        report_data = {
            "install": [
                {
                    "download_info": {
                        "url": "http://local-pypi.company.com/simple/requests/requests-2.31.0-py3-none-any.whl"
                    },
                    "metadata": {
                        "name": "requests"
                    }
                }
            ],
            "pip_version": "23.0.1"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report_data, f)
            report_path = f.name

        try:
            result = self.step._parse_install_report(report_path)
            self.assertEqual(result, 'local-pypi.company.com')
        finally:
            Path(report_path).unlink()

    def test_parse_install_report_mixed_urls(self):
        """Test parsing report with both PyPI and local URLs (should prefer local)"""
        report_data = {
            "install": [
                {
                    "download_info": {
                        "url": "https://files.pythonhosted.org/packages/urllib3-1.26.16-py2.py3-none-any.whl"
                    }
                },
                {
                    "download_info": {
                        "url": "http://nexus.internal.company/repository/pypi-proxy/simple/requests/requests-2.31.0-py3-none-any.whl"
                    }
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report_data, f)
            report_path = f.name

        try:
            result = self.step._parse_install_report(report_path)
            self.assertEqual(result, 'nexus.internal.company')
        finally:
            Path(report_path).unlink()

    def test_parse_install_report_no_urls(self):
        """Test parsing report with no URLs"""
        report_data = {
            "install": [],
            "metadata": {"pip_version": "23.0.1"}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report_data, f)
            report_path = f.name

        try:
            result = self.step._parse_install_report(report_path)
            self.assertIsNone(result)
        finally:
            Path(report_path).unlink()

    def test_parse_install_report_invalid_json(self):
        """Test parsing invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            report_path = f.name

        try:
            result = self.step._parse_install_report(report_path)
            self.assertIsNone(result)
        finally:
            Path(report_path).unlink()

    def test_parse_install_report_missing_file(self):
        """Test parsing non-existent file"""
        result = self.step._parse_install_report("/path/that/does/not/exist.json")
        self.assertIsNone(result)

    def test_parse_install_report_none_path(self):
        """Test parsing with None path"""
        result = self.step._parse_install_report(None)
        self.assertIsNone(result)

    def test_parse_install_report_complex_local_index(self):
        """Test parsing report with complex local index structure"""
        report_data = {
            "install": [
                {
                    "download_info": {
                        "url": "https://artifactory.company.com:8443/artifactory/api/pypi/pypi-virtual/simple/requests/requests-2.31.0-py3-none-any.whl"
                    },
                    "metadata": {
                        "name": "requests",
                        "version": "2.31.0"
                    }
                }
            ],
            "environment": {
                "implementation_name": "cpython"
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report_data, f)
            report_path = f.name

        try:
            result = self.step._parse_install_report(report_path)
            self.assertEqual(result, 'artifactory.company.com:8443')
        finally:
            Path(report_path).unlink()


class TestLibraryInstallationWorker(unittest.TestCase):
    """Test the LibraryInstallationWorker thread behavior"""

    def setUp(self):
        """Set up test fixtures"""
        self.progress_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.mock_venv_python = Path("/test/venv/Scripts/python.exe")
        self.libraries = ["requests", "urllib3"]

    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    def test_worker_successful_installation(self, mock_mkdir, mock_subprocess_run):
        """Test successful library installation worker behavior"""
        # Mock successful subprocess result
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.stdout = "Successfully installed requests-2.31.0 urllib3-1.26.16"
        mock_process.stderr = ""
        mock_subprocess_run.return_value = mock_process

        # Create worker
        worker = LibraryInstallationWorker(
            self.mock_venv_python,
            self.libraries,
            self.progress_queue,
            self.result_queue
        )

        # Run worker
        worker.run()

        # Verify subprocess was called correctly
        mock_subprocess_run.assert_called_once()
        call_args = mock_subprocess_run.call_args
        cmd = call_args[0][0]
        
        # Check command structure
        self.assertEqual(cmd[0], str(self.mock_venv_python))
        self.assertEqual(cmd[1:4], ["-m", "pip", "install"])
        self.assertEqual(cmd[4], "--report")
        self.assertTrue(cmd[5].endswith(".json"))  # Report path
        self.assertEqual(cmd[6:], self.libraries)

        # Check progress messages
        progress_messages = []
        while not self.progress_queue.empty():
            progress_messages.append(self.progress_queue.get_nowait())
        
        self.assertTrue(any("Starting library installation" in msg for msg in progress_messages))
        self.assertTrue(any("Successfully installed" in msg for msg in progress_messages))

        # Check result tuple
        self.assertFalse(self.result_queue.empty())
        success, message, report_path, stdout, stderr = self.result_queue.get_nowait()
        
        self.assertTrue(success)
        self.assertEqual(message, "Libraries installed successfully")
        self.assertTrue(report_path.endswith(".json"))
        self.assertEqual(stdout, "Successfully installed requests-2.31.0 urllib3-1.26.16")
        self.assertEqual(stderr, "")

    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    def test_worker_failed_installation(self, mock_mkdir, mock_subprocess_run):
        """Test failed library installation worker behavior"""
        # Mock failed subprocess result
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "ERROR: Could not find a version that satisfies the requirement nonexistent-package"
        mock_subprocess_run.return_value = mock_process

        # Create worker
        worker = LibraryInstallationWorker(
            self.mock_venv_python,
            ["nonexistent-package"],
            self.progress_queue,
            self.result_queue
        )

        # Run worker
        worker.run()

        # Check progress messages
        progress_messages = []
        while not self.progress_queue.empty():
            progress_messages.append(self.progress_queue.get_nowait())
        
        self.assertTrue(any("Library installation failed" in msg for msg in progress_messages))

        # Check result tuple
        self.assertFalse(self.result_queue.empty())
        success, message, report_path, stdout, stderr = self.result_queue.get_nowait()
        
        self.assertFalse(success)
        self.assertTrue(message.startswith("Installation failed:"))
        self.assertTrue(report_path.endswith(".json"))
        self.assertEqual(stdout, "")
        self.assertTrue("Could not find a version" in stderr)

    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    def test_worker_timeout(self, mock_mkdir, mock_subprocess_run):
        """Test worker behavior when subprocess times out"""
        # Mock timeout exception
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired("pip", 600)

        # Create worker
        worker = LibraryInstallationWorker(
            self.mock_venv_python,
            self.libraries,
            self.progress_queue,
            self.result_queue
        )

        # Run worker
        worker.run()

        # Check progress messages
        progress_messages = []
        while not self.progress_queue.empty():
            progress_messages.append(self.progress_queue.get_nowait())
        
        self.assertTrue(any("installation timed out" in msg for msg in progress_messages))

        # Check result tuple
        self.assertFalse(self.result_queue.empty())
        success, message, report_path, stdout, stderr = self.result_queue.get_nowait()
        
        self.assertFalse(success)
        self.assertEqual(message, "Installation timed out")
        self.assertTrue(report_path.endswith(".json"))
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "")

    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    def test_worker_general_exception(self, mock_mkdir, mock_subprocess_run):
        """Test worker behavior when unexpected exception occurs"""
        # Mock general exception
        mock_subprocess_run.side_effect = Exception("Unexpected error occurred")

        # Create worker
        worker = LibraryInstallationWorker(
            self.mock_venv_python,
            self.libraries,
            self.progress_queue,
            self.result_queue
        )

        # Run worker
        worker.run()

        # Check progress messages
        progress_messages = []
        while not self.progress_queue.empty():
            progress_messages.append(self.progress_queue.get_nowait())
        
        self.assertTrue(any("Installation error:" in msg for msg in progress_messages))

        # Check result tuple
        self.assertFalse(self.result_queue.empty())
        success, message, report_path, stdout, stderr = self.result_queue.get_nowait()
        
        self.assertFalse(success)
        self.assertTrue(message.startswith("Installation error:"))
        self.assertTrue(report_path.endswith(".json"))
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Unexpected error occurred")

    def test_worker_result_tuple_structure(self):
        """Test that worker always returns a 5-tuple with correct types"""
        with patch('subprocess.run') as mock_subprocess_run:
            # Mock successful result
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = "Success"
            mock_process.stderr = ""
            mock_subprocess_run.return_value = mock_process

            worker = LibraryInstallationWorker(
                self.mock_venv_python,
                ["test-package"],
                self.progress_queue,
                self.result_queue
            )

            with patch('pathlib.Path.mkdir'):
                worker.run()

            # Get result tuple
            result = self.result_queue.get_nowait()
            
            # Verify tuple structure
            self.assertEqual(len(result), 5)
            success, message, report_path, stdout, stderr = result
            
            # Verify types
            self.assertIsInstance(success, bool)
            self.assertIsInstance(message, str)
            self.assertIsInstance(report_path, str)
            self.assertIsInstance(stdout, str)
            self.assertIsInstance(stderr, str)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)