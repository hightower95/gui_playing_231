"""Data transformers module"""
from productivity_app.data_pipeline.data_transformers.decorator import data_transformer

# Don't import transformers here to avoid circular imports
# Transformers are auto-registered via their decorators when imported elsewhere

__all__ = [
    'data_transformer',
]
