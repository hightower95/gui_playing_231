"""
Application Context - Central dependency injection and state management
"""
from typing import Dict, Any, Optional, TypeVar, Type

T = TypeVar('T')


class AppContext:
    """Central application context for dependency injection and shared state

    Usage:
        # Register services
        context = AppContext()
        context.register('config', ConfigManager())
        context.register('epd_model', EpdModel())

        # Get services
        config = context.get('config')
        epd_model = context.get('epd_model', EpdModel)  # With type hint

        # Check if service exists
        if context.has('epd_model'):
            model = context.get('epd_model')
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._state: Dict[str, Any] = {}
        self._initialize_services()

    def _initialize_services(self):
        """Initialize core application services

        Override this method or call register() after instantiation
        to add services.
        """
        # Core services can be registered here
        # Example:
        # from app.core.config_manager import ConfigManager
        # self.register('config', ConfigManager())
        pass

    def register(self, name: str, service: Any) -> 'AppContext':
        """Register a service with the context

        Args:
            name: Service name/key
            service: Service instance

        Returns:
            Self for method chaining
        """
        self._services[name] = service
        return self

    def get(self, name: str, expected_type: Optional[Type[T]] = None) -> Any:
        """Get a registered service

        Args:
            name: Service name/key
            expected_type: Optional type hint for better IDE support

        Returns:
            Service instance or None if not found

        Example:
            model = context.get('epd_model', EpdModel)
        """
        return self._services.get(name)

    def has(self, name: str) -> bool:
        """Check if a service is registered

        Args:
            name: Service name/key

        Returns:
            True if service exists, False otherwise
        """
        return name in self._services

    def unregister(self, name: str) -> bool:
        """Remove a service from the context

        Args:
            name: Service name/key

        Returns:
            True if service was removed, False if it didn't exist
        """
        if name in self._services:
            del self._services[name]
            return True
        return False

    def set_state(self, key: str, value: Any) -> 'AppContext':
        """Set application state

        Args:
            key: State key
            value: State value

        Returns:
            Self for method chaining
        """
        self._state[key] = value
        return self

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get application state

        Args:
            key: State key
            default: Default value if key doesn't exist

        Returns:
            State value or default
        """
        return self._state.get(key, default)

    def has_state(self, key: str) -> bool:
        """Check if a state key exists

        Args:
            key: State key

        Returns:
            True if state exists, False otherwise
        """
        return key in self._state

    def clear_state(self, key: Optional[str] = None) -> 'AppContext':
        """Clear application state

        Args:
            key: Optional specific key to clear. If None, clears all state.

        Returns:
            Self for method chaining
        """
        if key is None:
            self._state.clear()
        elif key in self._state:
            del self._state[key]
        return self

    def get_all_services(self) -> Dict[str, Any]:
        """Get all registered services (for debugging)

        Returns:
            Dictionary of all services
        """
        return self._services.copy()

    def get_all_state(self) -> Dict[str, Any]:
        """Get all application state (for debugging)

        Returns:
            Dictionary of all state
        """
        return self._state.copy()
