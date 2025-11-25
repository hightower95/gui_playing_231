"""
Rich Text Browser Component - Supports HTML with images and styled content
"""
from PySide6.QtWidgets import QTextBrowser, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextDocument


class RichTextBrowser(QTextBrowser):
    """Enhanced text browser that supports HTML with images and custom styling

    Differences from QTextEdit:
    - Supports full HTML including images
    - Read-only by default (can be changed)
    - Better for displaying rich formatted content
    - Can display base64-encoded images and URLs

    Usage:
        browser = RichTextBrowser()
        browser.setHtml('<h2>Title</h2><p>With <b>formatting</b></p>')
        browser.setHtml('<img src="image.png" width="100" height="100"/>')
        browser.setHtml(f'<img src="data:image/png;base64,{base64_data}"/>')
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        # Enable external images if needed
        self.document().setBaseUrl("")

    def setPlaceholderText(self, text: str):
        """Set placeholder text (for compatibility with QTextEdit API)"""
        if not text:
            self.clear()
        else:
            self.setHtml(f"<p style='color: gray;'>{text}</p>")

    def setText(self, text: str):
        """Set plain text (will escape HTML)"""
        self.setPlainText(text)

    def setStyleSheet(self, css: str):
        """Override stylesheet to apply custom CSS"""
        super().setStyleSheet(css)


class HtmlContextBrowser(QTextBrowser):
    """Specialized browser for context display with image and text support

    Features:
    - Side-by-side layout of text and images
    - Dark theme support
    - Responsive sizing
    - Copy-friendly text selection
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        # Support for base64 images
        self.document().setBaseUrl("")

    def setContextHtml(self, html: str):
        """Set HTML content for context display"""
        self.setHtml(html)

    def setText(self, text: str):
        """Fallback to plain text if HTML not available"""
        self.setPlainText(text)
