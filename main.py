import sys
from loguru import logger
from PyQt5.QtWidgets import QApplication
from src.gui import SteamLoginGUI

if __name__ == "__main__":
    logger.info("Starting application...")
    sys.stdout.write("\x1b]2;Steam EYA\x07")

    app = QApplication(sys.argv)
    ex = SteamLoginGUI("1.0")

    ex.show()

    sys.exit(app.exec_())
