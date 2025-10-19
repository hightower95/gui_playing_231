"""
Search Result Data Class
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable


@dataclass
class ContextCallback:
    """Represents an interactive action in a context"""
    label: str  # Button label
    callback: Callable  # Function to call when clicked
    tooltip: Optional[str] = None  # Optional tooltip


@dataclass
class Context:
    """Additional context for a search result from other sources"""
    term: str  # The term that triggered this context
    context_owner: str  # Who provided the context (e.g., "Connector", "EPD")
    data_context: Dict[str, str] = field(
        default_factory=dict)  # Key-value pairs
    callbacks: List[ContextCallback] = field(
        default_factory=list)  # Interactive actions

    def add_callback(self, label: str, callback: Callable, tooltip: Optional[str] = None):
        """Add an interactive callback/action button"""
        self.callbacks.append(ContextCallback(label, callback, tooltip))

    def add_data(self, key: str, value: str):
        """Add a data field"""
        self.data_context[key] = value

    def has_callbacks(self) -> bool:
        """Check if context has any callbacks"""
        return len(self.callbacks) > 0

    def has_data(self) -> bool:
        """Check if context has any data"""
        return len(self.data_context) > 0

    def get_formatted_data(self) -> str:
        """Get formatted string of context data"""
        return ", ".join([f"{k}: {v}" for k, v in self.data_context.items()])


@dataclass
class SearchResult:
    """Data class for search results"""
    search_term: str
    document_name: str
    document_type: str
    matched_row_data: Dict[str, Any]  # Column: Value pairs from return columns
    contexts: List[Context] = None  # Additional context from other sources

    def __post_init__(self):
        """Initialize contexts list if None"""
        if self.contexts is None:
            self.contexts = []

    def add_context(self, context: Context):
        """Add context to this result"""
        self.contexts.append(context)

    def get_formatted_data(self) -> str:
        """Get formatted string of matched data"""
        return ", ".join([f"{k}: {v}" for k, v in self.matched_row_data.items()])

    def has_contexts(self) -> bool:
        """Check if result has any contexts"""
        return len(self.contexts) > 0
