# Loads Audio engine, convolution, and GUI
from src.gui.interface import GUI

from PyQt6.QtWidgets import QApplication

def main():
    window = GUI()
    window.show()
     app = QApplication([])
    app.exec()
    
if __name__ == "__main__":
    main()