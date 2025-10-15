"""
Application Context - Central dependency injection and state management
"""
from typing import Dict, Any


class AppContext:
    """Central application context for dependency injection and shared state"""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._state: Dict[str, Any] = {}
        self._initialize_services()

    def _initialize_services(self):
        """Initialize core application services"""
        # Initialize any core services here
        pass

    def register_service(self, name: str, service: Any):
        """Register a service with the context"""
        self._services[name] = service

    def get_service(self, name: str) -> Any:
        """Get a registered service"""
        return self._services.get(name)

    def set_state(self, key: str, value: Any):
        """Set application state"""
        self._state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get application state"""
        return self._state.get(key, default)

    def clear_state(self):
        """Clear all application state"""
        self._state.clear()
