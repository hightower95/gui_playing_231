"""
Base class for modules that can provide context to search results
"""
from abc import ABC, abstractmethod
from typing import List
from app.document_scanner.search_result import SearchResult, Context


class ContextProvider(ABC):
    """Base class for modules that can provide additional context to search results"""
    
    @abstractmethod
    def get_context_name(self) -> str:
        """Get the name of this context provider (e.g., 'Connector', 'EPD')
        
        Returns:
            Name of the context provider
        """
        pass
    
    @abstractmethod
    def get_context(self, result: SearchResult) -> List[Context]:
        """Get additional context for a search result
        
        Args:
            result: The search result to provide context for
            
        Returns:
            List of Context objects (may be empty if no context available)
        """
        pass
    
    def is_enabled(self) -> bool:
        """Check if this context provider is enabled
        
        Returns:
            True if enabled, False otherwise
        """
        return True
