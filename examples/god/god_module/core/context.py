"""
Pipeline execution context for passing data between providers and reporters.
"""

from typing import Any, Dict, Optional


class PipelineContext:
    """
    Context object that flows through the pipeline.
    Stores data from providers and makes it available to reporters.
    """
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._metadata: Dict[str, Any] = {}
        self._logs: list = []
        
    def set(self, key: str, value: Any) -> None:
        """Store data in context"""
        self._data[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve data from context"""
        return self._data.get(key, default)
        
    def has(self, key: str) -> bool:
        """Check if key exists in context"""
        return key in self._data
        
    def set_metadata(self, key: str, value: Any) -> None:
        """Store metadata about the pipeline execution"""
        self._metadata[key] = value
        
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Retrieve metadata"""
        return self._metadata.get(key, default)
        
    def log(self, message: str, level: str = "INFO") -> None:
        """Add a log message to context"""
        self._logs.append({
            'level': level,
            'message': message
        })
        print(f"[{level}] {message}")
        
    def get_logs(self) -> list:
        """Get all log messages"""
        return self._logs.copy()
        
    def get_all_data(self) -> Dict[str, Any]:
        """Get all stored data (for debugging)"""
        return self._data.copy()
