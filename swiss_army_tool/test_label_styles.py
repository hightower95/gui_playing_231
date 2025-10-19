"""Test label styles rendering"""
from app.ui.components import StandardGroupBox, StandardLabel, TextStyle
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
import sys
sys.path.insert(
    0, 'c:/Users/peter/OneDrive/Documents/Coding/gui/swiss_army_tool')


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Label Styles Test")
        self.setMinimumSize(600, 400)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Create group box
        group = StandardGroupBox("Text Styles Test")
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(15, 25, 15, 15)
        group_layout.setSpacing(10)

        # Add labels with different styles
        title_label = StandardLabel(
            "TITLE STYLE - 14pt bold", style=TextStyle.TITLE)
        group_layout.addWidget(title_label)

        section_label = StandardLabel(
            "SECTION STYLE - 12pt bold", style=TextStyle.SECTION)
        group_layout.addWidget(section_label)

        subsection_label = StandardLabel(
            "Subsection Style - 11pt bold", style=TextStyle.SUBSECTION)
        group_layout.addWidget(subsection_label)

        label_label = StandardLabel(
            "Label Style - 10pt normal", style=TextStyle.LABEL)
        group_layout.addWidget(label_label)

        notes_label = StandardLabel(
            "Notes Style - 9pt italic gray", style=TextStyle.NOTES)
        group_layout.addWidget(notes_label)

        status_label = StandardLabel(
            "Status Style - 10pt gray", style=TextStyle.STATUS)
        group_layout.addWidget(status_label)

        # Set layout
        group.setLayout(group_layout)
        main_layout.addWidget(group)
        main_layout.addStretch()

        print("Labels added:", group_layout.count())
        print("Group has layout:", group.layout() is not None)
        print("Group is visible:", group.isVisible())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
