import os
import psutil
import subprocess
import winreg
import stat
import vdf
import json
import zlib
import base64
import win32crypt
import shutil
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class SteamPaths:
    install_path: Path
    local_vdf_path: Path
    config_path: Path


class SteamUtils:
    @staticmethod
    def get_steam_paths() -> SteamPaths:
        """Get all relevant Steam paths"""
        install_path = SteamUtils._get_steam_install_path()
        local_appdata = SteamUtils._read_registry_value(
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            "Local AppData",
        )

        return SteamPaths(
            install_path=Path(install_path),
            local_vdf_path=Path(local_appdata) / "Steam" / "local.vdf",
            config_path=Path(install_path) / "config",
        )

    @staticmethod
    def _get_steam_install_path() -> str:
        """Get Steam installation directory"""
        steam_pid = SteamUtils._get_process_pid("steam.exe")
        if steam_pid:
            process = psutil.Process(steam_pid)
            steam_path = process.exe()
            SteamUtils._kill_steam_processes()
            return os.path.dirname(steam_path)

        steam_path = SteamUtils._read_registry_value(
            r"Software\Classes\steam\Shell\Open\Command", ""
        ).strip('"')
        return os.path.dirname(steam_path)

    @staticmethod
    def _kill_steam_processes():
        """Kill running Steam processes"""
        subprocess.run("taskkill /f /im steam.exe", shell=True)
        subprocess.run("taskkill /f /im steamwebhelper.exe", shell=True)
        time.sleep(2)

    @staticmethod
    def _get_process_pid(process_name: str) -> int:
        """Get process PID by name"""
        for proc in psutil.process_iter(["name", "pid"]):
            if proc.info["name"] == process_name:
                return proc.info["pid"]
        return 0

    @staticmethod
    def _read_registry_value(key_path: str, value_name: str) -> str:
        """Read Windows registry value"""
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value.decode("utf-8") if isinstance(value, bytes) else value

    @staticmethod
    def compute_crc32(data: str) -> str:
        """Compute CRC32 hash of string"""
        crc32_value = zlib.crc32(data.encode("utf-8"))
        return f"{crc32_value:08x}".lstrip("0")


class SteamCrypto:
    """Handle Steam-specific encryption/decryption"""

    OBFUSCATE_BUFFER = b"B\x00O\x00b\x00f\x00u\x00s\x00c\x00a\x00t\x00e\x00B\x00u\x00f\x00f\x00e\x00r\x00\x00\x00"

    @classmethod
    def encrypt(cls, token: str, account_name: str) -> str:
        """Encrypt token using Windows CryptoAPI"""
        data = token.encode("utf-8")
        key = account_name.encode("utf-8")
        encrypted = win32crypt.CryptProtectData(
            data, cls.OBFUSCATE_BUFFER.decode("utf-8"), key, None, None, 17
        )
        return encrypted.hex()

    @classmethod
    def decrypt(cls, encrypted_hex: str, account_name: str) -> str:
        """Decrypt token using Windows CryptoAPI"""
        encrypted = bytes.fromhex(encrypted_hex)
        key = account_name.encode("utf-8")
        decrypted = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)
        return decrypted[1].decode("utf-8")


class SteamFiles:
    """Handle Steam configuration files"""

    @staticmethod
    def save_file(path: Path, content: str):
        """Safely save file with proper permissions"""
        if path.exists():
            path.chmod(stat.S_IWRITE)
            path.unlink()
        path.write_text(content, encoding="utf-8")

    @staticmethod
    def remove_directory(path: Path):
        """Recursively remove directory with readonly files"""
        if path.exists():
            shutil.rmtree(
                str(path),
                onerror=lambda f, p, e: (
                    Path(p).chmod(stat.S_IWRITE),
                    Path(p).unlink(),
                ),
            )
