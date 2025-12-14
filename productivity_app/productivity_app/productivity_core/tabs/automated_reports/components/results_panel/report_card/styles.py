"""Shared styling constants for report card components"""

# Card container styles
CARD_STYLE = """
    QFrame#reportCard {
        background-color: #2a2a2a;
        border: 1px solid #3a3a3a;
        border-radius: 12px;
    }
    
    QFrame#reportCard:hover {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
    }
"""

# Header section styles
HEADER_STYLE = """
    QLabel#cardIcon {
        font-size: 16pt;
        background: transparent;
        border: none;
    }
    
    QLabel#headerTitle {
        color: #E0E0E0;
        font-size: 12pt;
        font-weight: 600;
        background: transparent;
        border: none;
    }
    
    QLabel#locationText, QLabel#locationIcon {
        color: #909090;
        font-size: 9pt;
        background: transparent;
        border: none;
    }
"""

# Report summary styles
SUMMARY_STYLE = """
    QLabel#cardTitle {
        color: #E0E0E0;
        font-size: 14pt;
        font-weight: 600;
        background: transparent;
        border: none;
    }
    
    QLabel#cardDescription {
        color: #909090;
        font-size: 10pt;
        background: transparent;
        border: none;
    }
"""

# Tags/metadata styles
TAGS_STYLE = """
    QLabel#metadataLabel {
        color: #909090;
        font-size: 9pt;
        background: transparent;
        border: none;
    }
    
    QLabel#sectionLabel {
        color: #B0B0B0;
        font-size: 9pt;
        background: transparent;
        border: none;
    }
"""

# Badge styles
BADGE_STYLE = """
    QLabel[objectName^="badge_highlight"] {
        background-color: rgba(79, 195, 247, 0.15);
        color: #90caf9;
        border-radius: 8px;
        padding: 4px 12px;
        font-size: 9pt;
        border: none;
        min-height: 24px;
        max-height: 24px;
    }
    
    QLabel[objectName^="badge_muted"] {
        background-color: rgba(144, 144, 144, 0.12);
        color: #a0a0a0;
        border-radius: 8px;
        padding: 4px 12px;
        font-size: 9pt;
        border: none;
        min-height: 24px;
        max-height: 24px;
    }
    
    QLabel[objectName^="badge_orange"] {
        background-color: rgba(255, 152, 0, 0.15);
        color: #ffb74d;
        border-radius: 8px;
        padding: 4px 12px;
        font-size: 9pt;
        border: none;
        min-height: 24px;
        max-height: 24px;
    }
    
    QLabel[objectName^="badge_green"] {
        background-color: rgba(102, 187, 106, 0.15);
        color: #81c784;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 8pt;
        border: none;
        min-height: 20px;
        max-height: 20px;
    }
    
    QLabel[objectName^="badge_secondaryHighlight"] {
        background-color: rgba(79, 195, 247, 0.08);
        color: #7fb3d5;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 8pt;
        border: none;
        min-height: 20px;
        max-height: 20px;
    }
    
    QLabel[badgeSize="small"] {
        font-size: 8pt;
        padding: 2px 8px;
    }
"""

# Divider styles
DIVIDER_STYLE = """
    QFrame#cardDivider {
        background-color: #3a3a3a;
        border: none;
    }
"""

# Combined stylesheet
COMPLETE_CARD_STYLE = (
    CARD_STYLE +
    HEADER_STYLE +
    SUMMARY_STYLE +
    TAGS_STYLE +
    BADGE_STYLE +
    DIVIDER_STYLE
)
