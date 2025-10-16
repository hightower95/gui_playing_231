"""
Search Result Data Class
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class Context:
    """Additional context for a search result from other sources"""
    term: str  # The term that is relevant
    context_owner: str  # Who provided the context (e.g., "Connector", "EPD")
    data_context: Dict[str, str]  # Key-value pairs of contextual data
    
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
