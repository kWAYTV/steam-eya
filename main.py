import sys
from loguru import logger
from PyQt5.QtWidgets import QApplication
from src.gui import SteamLoginGUI

if __name__ == "__main__":
    logger.add("logs/app.log", mode="w")

    logger.info("Starting application...")

    app = QApplication(sys.argv)
    ex = SteamLoginGUI("1.0")

    ex.show()

    sys.exit(app.exec_())
