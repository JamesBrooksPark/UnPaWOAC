# Loads Audio engine, convolution, and GUI
from src.gui.interface import GUI

from PyQt6.QtWidgets import QApplication

def main():
    window = GUI(AE)
    window.show()
    app.exec()
    
if __name__ == "__main__":
    main()