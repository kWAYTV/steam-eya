import json
import time
import random
import string
import vdf
from typing import Dict


class SteamConfig:
    @staticmethod
    def build_config(mtbf: str, steam_id: str, account_name: str) -> str:
        config = {
            "InstallConfigStore": {
                "Software": {
                    "Valve": {
                        "Steam": {
                            "AutoUpdateWindowEnabled": "0",
                            "ipv6check_http_state": "bad",
                            "ipv6check_udp_state": "bad",
                            "ShaderCacheManager": {
                                "HasCurrentBucket": "1",
                                "CurrentBucketGPU": "b4799b250d4196b0;36174e7cc31a08f9",
                                "CurrentBucketDriver": "W2:c18b09d9c69329b41cdbbf3de627bc9f;W2:ee32edf67d134b7cc2ec0cdecbd00037",
                            },
                            "RecentWebSocket443Failures": "",
                            "RecentWebSocketNon443Failures": "",
                            "RecentUDPFailures": "",
                            "RecentTCPFailures": "",
                            "Accounts": {account_name: {"SteamID": steam_id}},
                            "CellIDServerOverride": "170",
                            "MTBF": mtbf,
                            "cip": "02000000507a6c24d6e96c6b00004021a356",
                            "SurveyDate": "2017-10-22",
                            "SurveyDateVersion": "-1724767764117155760",
                            "SurveyDateType": "3",
                            "Rate": "30000",
                        }
                    }
                }
            }
        }
        return vdf.dumps(config)

    @staticmethod
    def build_login_users(steam_id: str, account_name: str) -> str:
        login_users = {
            "users": {
                steam_id: {
                    "AccountName": account_name,
                    "PersonaName": account_name,
                    "RememberPassword": "1",
                    "WantsOfflineMode": "0",
                    "SkipOfflineModeWarning": "0",
                    "AllowAutoLogin": "1",
                    "MostRecent": "1",
                    "Timestamp": str(int(time.time())),
                }
            }
        }
        return vdf.dumps(login_users)

    @staticmethod
    def build_local(crc32: str, jwt: str) -> str:
        local = {
            "MachineUserConfigStore": {
                "Software": {"Valve": {"Steam": {"ConnectCache": {crc32: jwt}}}}
            }
        }
        return vdf.dumps(local)

    @staticmethod
    def generate_mtbf() -> str:
        return "".join(random.choices(string.digits, k=9))


class UserCache:
    CACHE_FILE = "user_backup.json"

    @classmethod
    def load(cls) -> Dict[str, str]:
        try:
            with open(cls.CACHE_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @classmethod
    def save(cls, data: Dict[str, str]):
        with open(cls.CACHE_FILE, "w") as f:
            json.dump(data, f)

    @classmethod
    def add_user(cls, account_name: str, eya: str):
        cache = cls.load()
        cache[account_name] = eya
        cls.save(cache)

    @classmethod
    def remove_user(cls, account_name: str):
        cache = cls.load()
        if account_name in cache:
            del cache[account_name]
            cls.save(cache)
