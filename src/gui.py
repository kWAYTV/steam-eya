from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QListWidget,
)
from .steam_login import SteamLoginManager
from .steam_utils import SteamUtils, SteamFiles
from .steam_config import UserCache
from .jwt_utils import JWTValidator
import subprocess


class SteamLoginGUI(QWidget):
    def __init__(self, version: str):
        super().__init__()
        self.version = version
        self.login_manager = SteamLoginManager()
        self.selected_account = None
        self.init_ui()
        self.load_accounts()

    def init_ui(self):
        self.setWindowTitle(f"Wavius Market Cache Login v{self.version}")
        self.setup_window()
        self.setup_layout()

    def setup_window(self):
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#FAF9F6"))
        self.setPalette(palette)
        self.setFixedSize(440, 440)

    def setup_layout(self):
        layout = QVBoxLayout()

        # Input section
        layout.addWidget(QLabel("Enter account information:"))
        self.entry = QLineEdit()
        layout.addWidget(self.entry)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)

        # Accounts list
        self.accounts_list = QListWidget()
        self.accounts_list.itemClicked.connect(self.on_account_selected)
        layout.addWidget(self.accounts_list)

        # Action buttons
        for label, handler in [
            ("Restore", self.handle_restore),
            ("Delete", self.handle_delete),
            ("Reset Steam", self.handle_reset),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        self.setLayout(layout)

    def load_accounts(self):
        self.accounts_list.clear()
        for account in UserCache.load():
            self.accounts_list.addItem(account)

    def on_account_selected(self, item):
        self.selected_account = item.text()

    def handle_login(self):
        user_input = self.entry.text().replace(
            "EyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0",
            "eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0",
        )

        parts = user_input.split("----")
        eya = next(
            (
                part
                for part in parts
                if "eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0." in part
            ),
            "",
        )

        if not eya:
            QMessageBox.critical(None, "Error", "Invalid input format.")
            return

        account_name = parts[0].lower()
        expire_time = JWTValidator.verify_steam_jwt(eya)

        if expire_time < 0:
            QMessageBox.critical(None, "Error", "Token has expired.")
            return

        if self.login_manager.login(eya, account_name):
            days = expire_time // 86400
            hours = (expire_time % 86400) // 3600
            minutes = (expire_time % 3600) // 60
            seconds = expire_time % 60
            QMessageBox.information(
                None,
                "Token Valid",
                f"Token is valid for {days} days, {hours} hours, {minutes} "
                f"minutes, and {seconds} seconds.",
            )

    def handle_restore(self):
        if not self.selected_account:
            QMessageBox.warning(None, "Error", "No account selected.")
            return

        cache = UserCache.load()
        if jwt := cache.get(self.selected_account):
            self.login_manager.login(jwt, self.selected_account)

    def handle_delete(self):
        if not self.selected_account:
            QMessageBox.warning(None, "Error", "No account selected.")
            return

        UserCache.remove_user(self.selected_account)
        self.load_accounts()
        QMessageBox.information(
            None, "Success", f"Deleted account: {self.selected_account}"
        )

    def handle_reset(self):
        paths = SteamUtils.get_steam_paths()

        for path in [paths.install_path / "userdata", paths.config_path]:
            SteamFiles.remove_directory(path)

        if paths.local_vdf_path.exists():
            paths.local_vdf_path.unlink()

        subprocess.Popen(str(paths.install_path / "steam.exe"), shell=True)
        QMessageBox.information(
            None, "Reset Completed", "Steam has been reset successfully."
        )
