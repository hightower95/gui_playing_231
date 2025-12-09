"""
Experiment with different HTML/CSS approaches for 3-column tile layout in QTextBrowser
"""
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout


class TileExperiment(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tile Layout Experiment")
        self.setGeometry(100, 100, 1000, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Buttons to switch between approaches
        button_layout = QHBoxLayout()
        
        btn1 = QPushButton("Approach 1: Table")
        btn1.clicked.connect(lambda: self.show_approach(1))
        button_layout.addWidget(btn1)
        
        btn2 = QPushButton("Approach 2: Inline-block")
        btn2.clicked.connect(lambda: self.show_approach(2))
        button_layout.addWidget(btn2)
        
        btn3 = QPushButton("Approach 3: Flex")
        btn3.clicked.connect(lambda: self.show_approach(3))
        button_layout.addWidget(btn3)
        
        btn4 = QPushButton("Approach 4: Float")
        btn4.clicked.connect(lambda: self.show_approach(4))
        button_layout.addWidget(btn4)
        
        layout.addLayout(button_layout)
        
        # Text browser
        self.browser = QTextBrowser()
        layout.addWidget(self.browser)
        
        # Show first approach by default
        self.show_approach(1)
    
    def show_approach(self, num: int):
        """Show different layout approach"""
        if num == 1:
            self.browser.setHtml(self.approach_table())
        elif num == 2:
            self.browser.setHtml(self.approach_inline_block())
        elif num == 3:
            self.browser.setHtml(self.approach_flex())
        elif num == 4:
            self.browser.setHtml(self.approach_float())
    
    def approach_table(self) -> str:
        """Approach 1: HTML Table (current approach)"""
        return """
        <html>
        <head>
            <style>
                body { background-color: #1e1e1e; color: #e0e0e0; font-family: Arial; margin: 10px; }
                h2 { color: #4fc3f7; }
                table { width: 100%; border-collapse: separate; border-spacing: 0; }
                td { width: 33.33%; padding: 12px; vertical-align: top; }
                .tile {
                    background-color: #2a2a2a;
                    border-radius: 12px;
                    padding: 15px;
                    border: 1px solid #3a3a3a;
                    height: 140px;
                }
                .tile:hover { background-color: #353535; }
                .title { font-weight: bold; color: #4fc3f7; font-size: 14pt; }
            </style>
        </head>
        <body>
            <h2>Approach 1: Table Layout</h2>
            <table>
                <tr>
                    <td><div class="tile"><div class="title">Tile 1</div>Content here</div></td>
                    <td><div class="tile"><div class="title">Tile 2</div>Content here</div></td>
                    <td><div class="tile"><div class="title">Tile 3</div>Content here</div></td>
                </tr>
            </table>
        </body>
        </html>
        """
    
    def approach_inline_block(self) -> str:
        """Approach 2: Inline-block with calc width"""
        return """
        <html>
        <head>
            <style>
                body { background-color: #1e1e1e; color: #e0e0e0; font-family: Arial; margin: 10px; }
                h2 { color: #4fc3f7; }
                .container { width: 100%; }
                .tile {
                    display: inline-block;
                    width: calc(33.33% - 16px);
                    background-color: #2a2a2a;
                    border-radius: 12px;
                    padding: 15px;
                    border: 1px solid #3a3a3a;
                    height: 140px;
                    margin: 8px;
                    vertical-align: top;
                    box-sizing: border-box;
                }
                .tile:hover { background-color: #353535; }
                .title { font-weight: bold; color: #4fc3f7; font-size: 14pt; }
            </style>
        </head>
        <body>
            <h2>Approach 2: Inline-Block</h2>
            <div class="container">
                <div class="tile"><div class="title">Tile 1</div>Content here</div>
                <div class="tile"><div class="title">Tile 2</div>Content here</div>
                <div class="tile"><div class="title">Tile 3</div>Content here</div>
            </div>
        </body>
        </html>
        """
    
    def approach_flex(self) -> str:
        """Approach 3: Flexbox"""
        return """
        <html>
        <head>
            <style>
                body { background-color: #1e1e1e; color: #e0e0e0; font-family: Arial; margin: 10px; }
                h2 { color: #4fc3f7; }
                .container {
                    display: flex;
                    gap: 12px;
                    width: 100%;
                }
                .tile {
                    flex: 1;
                    background-color: #2a2a2a;
                    border-radius: 12px;
                    padding: 15px;
                    border: 1px solid #3a3a3a;
                    height: 140px;
                }
                .tile:hover { background-color: #353535; }
                .title { font-weight: bold; color: #4fc3f7; font-size: 14pt; }
            </style>
        </head>
        <body>
            <h2>Approach 3: Flexbox</h2>
            <div class="container">
                <div class="tile"><div class="title">Tile 1</div>Content here</div>
                <div class="tile"><div class="title">Tile 2</div>Content here</div>
                <div class="tile"><div class="title">Tile 3</div>Content here</div>
            </div>
        </body>
        </html>
        """
    
    def approach_float(self) -> str:
        """Approach 4: Float (old school)"""
        return """
        <html>
        <head>
            <style>
                body { background-color: #1e1e1e; color: #e0e0e0; font-family: Arial; margin: 10px; }
                h2 { color: #4fc3f7; }
                .container { width: 100%; overflow: auto; }
                .tile {
                    float: left;
                    width: 30%;
                    background-color: #2a2a2a;
                    border-radius: 12px;
                    padding: 15px;
                    border: 1px solid #3a3a3a;
                    height: 140px;
                    margin: 0 1.5%;
                    box-sizing: border-box;
                }
                .tile:hover { background-color: #353535; }
                .title { font-weight: bold; color: #4fc3f7; font-size: 14pt; }
            </style>
        </head>
        <body>
            <h2>Approach 4: Float Layout</h2>
            <div class="container">
                <div class="tile"><div class="title">Tile 1</div>Content here</div>
                <div class="tile"><div class="title">Tile 2</div>Content here</div>
                <div class="tile"><div class="title">Tile 3</div>Content here</div>
            </div>
        </body>
        </html>
        """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TileExperiment()
    window.show()
    sys.exit(app.exec())
