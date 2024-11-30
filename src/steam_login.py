import os
import vdf
import winreg
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox
from .jwt_utils import JWTValidator
from .steam_utils import SteamUtils, SteamCrypto, SteamFiles, SteamPaths
from .steam_config import SteamConfig, UserCache


class SteamLoginManager:
    def __init__(self):
        self.paths = SteamUtils.get_steam_paths()

    def login(self, eya: str, account_name: str) -> bool:
        try:
            # Validate token
            if JWTValidator.verify_steam_jwt(eya) < 0:
                QMessageBox.critical(None, "Error", "Token has expired or is invalid")
                return False

            json_data = JWTValidator.parse_eya(eya)
            if not json_data:
                return False

            # Prepare login data
            steam_id = json_data["sub"]
            mtbf = SteamConfig.generate_mtbf()
            jwt = SteamCrypto.encrypt(eya, account_name)
            crc32 = f"{SteamUtils.compute_crc32(account_name)}1"

            # Save current cache
            self._backup_current_cache()

            # Configure Steam
            self._prepare_directories()
            self._update_registry(account_name)
            self._write_config_files(account_name, steam_id, mtbf, jwt, crc32)

            # Update cache and launch Steam
            UserCache.add_user(account_name, eya)
            subprocess.Popen(str(self.paths.install_path / "steam.exe"), shell=True)

            QMessageBox.information(None, "Success", "Login initiated successfully")
            return True

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Login failed: {str(e)}")
            return False

    def _backup_current_cache(self):
        """Backup existing Steam login cache"""
        try:
            local_vdf = self.paths.local_vdf_path
            if not local_vdf.exists():
                return

            users = self._get_login_users()
            user_map = {f"{SteamUtils.compute_crc32(name)}1": name for name in users}

            if not user_map:
                return

            cache = UserCache.load()
            vdf_data = vdf.load(local_vdf.open("r", encoding="utf-8"))
            connect_cache = (
                vdf_data.get("MachineUserConfigStore", {})
                .get("Software", {})
                .get("Valve", {})
                .get("Steam", {})
                .get("ConnectCache", {})
            )

            for key, encrypted in connect_cache.items():
                try:
                    if account := user_map.get(key):
                        cache[account] = SteamCrypto.decrypt(encrypted, account)
                except Exception:
                    continue

            UserCache.save(cache)

        except Exception as e:
            print(f"Cache backup failed: {e}")

    def _get_login_users(self):
        """Get list of Steam login users"""
        try:
            login_file = self.paths.config_path / "loginusers.vdf"
            if not login_file.exists():
                return []

            data = vdf.load(login_file.open("r", encoding="utf-8"))
            return [user.get("AccountName") for user in data.get("users", {}).values()]

        except Exception:
            return []

    def _prepare_directories(self):
        """Prepare Steam directories"""
        if self.paths.local_vdf_path.exists():
            self.paths.local_vdf_path.unlink()
        self.paths.config_path.mkdir(parents=True, exist_ok=True)

    def _update_registry(self, account_name: str):
        """Update Steam registry for auto-login"""
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam", 0, winreg.KEY_WRITE
        )
        winreg.SetValueEx(key, "AutoLoginUser", 0, winreg.REG_SZ, account_name)
        winreg.CloseKey(key)

    def _write_config_files(
        self, account_name: str, steam_id: str, mtbf: str, jwt: str, crc32: str
    ):
        """Write Steam configuration files"""
        config_files = {
            self.paths.config_path
            / "config.vdf": SteamConfig.build_config(mtbf, steam_id, account_name),
            self.paths.config_path
            / "loginusers.vdf": SteamConfig.build_login_users(steam_id, account_name),
            self.paths.local_vdf_path: SteamConfig.build_local(crc32, jwt),
        }

        for path, content in config_files.items():
            SteamFiles.save_file(path, content)
