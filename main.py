import sys
from PyQt5.QtWidgets import QApplication
from src.gui import SteamLoginGUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SteamLoginGUI("1.0")
    ex.show()
    sys.exit(app.exec_())
