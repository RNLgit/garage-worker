import os
import requests
import urllib3
from datetime import datetime
from zoneinfo import ZoneInfo


urllib3.disable_warnings()  # just to silence the warning while testing

NAS_PORT = 5001
DEFAULT_TIMEZONE = os.getenv("NAS_TIMEZONE", "Australia/Melbourne")


class SynologySampler:
    BASE_URL = "https://{nas_ip}:{port}/webapi/entry.cgi"

    def __init__(self, ip: str, port: int = None, username: str = None, password: str | None = None):
        self.ip = ip
        self.port = port if port is not None else NAS_PORT
        self.username = username or os.getenv("SYNOLOGY_USER_NAME")
        self.password = password or os.getenv("SYNOLOGY_USER_PASSWORD")
        self.base_url = self.BASE_URL.format(nas_ip=self.ip, port=self.port)
        self.session = requests.Session()
        self.sid = None
        self._login()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logout()

    def _login(self) -> None:
        """Login -> get SID"""
        login = self.session.get(
            self.base_url,
            params={
                "api": "SYNO.API.Auth",
                "version": "6",
                "method": "login",
                "account": self.username,
                "passwd": self.password,
                "session": "Core",
                "format": "sid",
            },
            verify=False,
        ).json()
        self.sid = login["data"]["sid"]

    def synology_get(self, params) -> dict:
        """helper to always include _sid"""
        return self.session.get(self.base_url, params={**params, "_sid": self.sid}, verify=False).json()

    def get_utilization(self) -> dict:
        """Get system utilization"""
        return self.synology_get(
            {
                "api": "SYNO.Core.System.Utilization",
                "version": "1",
                "method": "get",
            }
        )

    def get_storage_info(self) -> dict:
        """Get storage information"""
        return self.synology_get(
            {
                "api": "SYNO.Storage.CGI.Storage",
                "version": "1",
                "method": "load_info",
            }
        )

    def logout(self) -> dict:
        """Logout from the session"""
        return self.synology_get(
            {
                "api": "SYNO.API.Auth",
                "version": "6",
                "method": "logout",
                "session": "Core",
            }
        )

    @staticmethod
    def now_iso(ts_int):
        return datetime.fromtimestamp(ts_int, ZoneInfo(DEFAULT_TIMEZONE)).isoformat()

    def get_one_sample(self) -> dict:
        """Sample and return relevant information"""
        util = self.get_utilization()
        storage = self.get_storage_info()
        t = util["data"]["time"]

        payload = {
            "ts": self.now_iso(t),
            "cpu": {
                "user": util["data"]["cpu"]["user_load"],
                "system": util["data"]["cpu"]["system_load"],
                "other": util["data"]["cpu"]["other_load"],
                "load_1": util["data"]["cpu"]["1min_load"],
                "load_5": util["data"]["cpu"]["5min_load"],
                "load_15": util["data"]["cpu"]["15min_load"],
            },
            "memory": {
                "real_usage_pct": util["data"]["memory"]["real_usage"],
                "total_real": util["data"]["memory"]["total_real"],
                "avail_real": util["data"]["memory"]["avail_real"],
                "swap_usage_pct": util["data"]["memory"]["swap_usage"],
            },
            # Network (counters direct)
            "network": util["data"]["network"],
            # Disk I/O snapshot (counters)
            "disks_util": util["data"]["disk"]["disk"],
            "space": util["data"]["space"]["volume"],
            # Pools (RAID groups)
            "pools": [
                {
                    "id": p["id"],
                    "raid": p.get("raidType"),
                    "status": p["status"],
                    "used": p["size"]["used"],
                    "total": p["size"]["total"],
                }
                for p in storage["data"]["storagePools"]
            ],
            # Volumes (filesystems created inside those Pools)
            "volumes": [
                {
                    "id": v["id"],
                    "fs": v.get("fs_type"),
                    "status": v["status"],
                    "used": v["size"]["used"],
                    "total": v["size"]["total"],
                }
                for v in storage["data"]["volumes"]
            ],
            # Hardware monitoring: disks
            "hardware": [
                {
                    "id": d["id"],
                    "model": d["model"],
                    "serial": d["serial"],
                    "temp_c": d["temp"],
                    "smart_status": d["smart_status"],
                    "status": d["status"],
                }
                for d in storage["data"]["disks"]
            ],
            # System / chassis info
            "env": {
                "model_name": storage["data"]["env"]["model_name"],
                "bay_number": storage["data"]["env"]["bay_number"],
                "system_crashed": storage["data"]["env"]["status"]["system_crashed"],
                "system_need_repair": storage["data"]["env"]["status"]["system_need_repair"],
                "system_rebuilding": storage["data"]["env"]["status"]["system_rebuilding"],
            },
        }
        return payload
