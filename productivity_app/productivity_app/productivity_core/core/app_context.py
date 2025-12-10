"""
Application Context - Central dependency injection and state management
"""
from typing import Dict, Any, Optional, TypeVar, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from ..tabs.tab_visibility_service import TabVisibilityService
    from .feature_flags_manager import FeatureFlagsManager

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
        self._context_providers: Dict[str, Any] = {}
        self._initialize_services()

    def _initialize_services(self):
        """Initialize core application services

        Override this method or call register() after instantiation
        to add services.
        """
        # Core services can be registered here
        # Example:
        # from ..core.config_manager import ConfigManager
        # self.register('config', ConfigManager())

        # Register global managers
        from .feature_flags_manager import FeatureFlagsManager
        from ..tabs.tab_visibility_service import TabVisibilityService

        self.register('feature_flags', FeatureFlagsManager())
        self.register('tab_visibility', TabVisibilityService())

    @property
    def tab_visibility(self) -> 'TabVisibilityService':
        """Get the tab visibility service with full type hints"""
        from ..tabs.tab_visibility_service import TabVisibilityService
        return self.get('tab_visibility', TabVisibilityService)

    @property
    def feature_flags(self) -> 'FeatureFlagsManager':
        """Get the feature flags manager with full type hints"""
        from .feature_flags_manager import FeatureFlagsManager
        return self.get('feature_flags', FeatureFlagsManager)

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

    def register_context_provider(self, name: str, provider: Any) -> 'AppContext':
        """Register or update a context provider

        Supports two-phase initialization:
        - Phase 1: Register default/stub provider immediately
        - Phase 2: Update with actual provider when async data loads

        Args:
            name: Provider name/key
            provider: Provider instance (can replace existing provider)

        Returns:
            Self for method chaining
        """
        self._context_providers[name] = provider
        if provider:
            print(f"[AppContext] ✓ Context provider registered: {name}")
        return self

    def get_context_provider(self, name: str, default: Any = None) -> Any:
        """Get a registered context provider

        Args:
            name: Provider name/key
            default: Default value if provider not found

        Returns:
            Provider instance or default if not found
        """
        return self._context_providers.get(name, default)

    def has_context_provider(self, name: str) -> bool:
        """Check if a context provider is registered

        Args:
            name: Provider name/key

        Returns:
            True if provider exists, False otherwise
        """
        return name in self._context_providers
