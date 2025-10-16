"""
Feature Toggles - Centralized feature flags for the application

This module contains all feature toggles/flags that can be used to enable or disable
features across the application without changing code.

Usage:
    from app.shared.feature_toggles import ENABLE_PINOUT_IMAGE
    
    if ENABLE_PINOUT_IMAGE:
        # Show pinout image
        pass
"""

# ============================================================================
# CONNECTOR LOOKUP FEATURES
# ============================================================================

# Enable/disable connector pinout image in context area
# When disabled, context area uses full width
# When enabled, shows 200x200px image placeholder on the right side
ENABLE_PINOUT_IMAGE = False

# ============================================================================
# EPD FEATURES
# ============================================================================

# Add EPD feature toggles here as needed
# Example:
# ENABLE_EPD_ADVANCED_SEARCH = True

# ============================================================================
# GENERAL UI FEATURES
# ============================================================================

# Add general UI feature toggles here as needed
# Example:
# ENABLE_DARK_MODE = True
# ENABLE_ANIMATIONS = False
