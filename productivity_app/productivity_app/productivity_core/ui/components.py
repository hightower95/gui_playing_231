"""
Standardized UI Components Library - Compatibility Import

This file provides backward compatibility for code that imports from:
    from productivity_core.ui.components import StandardButton, ...

All components have been moved to the app.ui.components package (folder).
This file simply re-exports everything from the new package structure.

Recommended import (same as before, works with both old and new structure):
    from productivity_core.ui.components import (
        StandardButton, ButtonRole, ButtonSize,
        StandardLabel, TextStyle,
        StandardComboBox, ComboSize,
        StandardInput,
        StandardDropArea,
        create_button_row,
        create_form_row
    )

See app/ui/components/README.md for complete documentation.
"""

# Re-export everything from the components package
from productivity_core.ui.components import (  # noqa: F401
    # Enums
    ButtonRole,
    ButtonSize,
    ComboSize,
    TextStyle,
    # Constants
    COMPONENT_SIZES,
    BUTTON_COLORS,
    # Components
    StandardButton,
    StandardLabel,
    StandardComboBox,
    StandardInput,
    StandardDropArea,
    # Helpers
    create_button_row,
    create_form_row,
)

__all__ = [
    'ButtonRole',
    'ButtonSize',
    'ComboSize',
    'TextStyle',
    'COMPONENT_SIZES',
    'BUTTON_COLORS',
    'StandardButton',
    'StandardLabel',
    'StandardComboBox',
    'StandardInput',
    'StandardDropArea',
    'create_button_row',
    'create_form_row',
]
