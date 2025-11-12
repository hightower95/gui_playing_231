"""
Remote Docs Module

Provides functionality for viewing and managing remote documents.
"""
from .presenter import RemoteDocsPresenter
from .view import RemoteDocsView
from .model import RemoteDocsModel, Document, DocumentVersion

__all__ = ['RemoteDocsPresenter', 'RemoteDocsView',
           'RemoteDocsModel', 'Document', 'DocumentVersion']
