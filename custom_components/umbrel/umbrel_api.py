import json
import logging
import urllib.parse
import aiohttp

_LOGGER = logging.getLogger(__name__)

class UmbrelApiClient:

    def __init__(self, host: str, password: str, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._host = host.rstrip("/")
        if not self._host.startswith("http"):
            self._host = f"http://{self._host}"
        self._password = password
        self._token = None

    async def login(self) -> bool:
        url = f"{self._host}/trpc/user.login"
        payload = {"password": self._password}

        try:
            async with self._session.post(
                url, json=payload, ssl=False, timeout=10
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data and "data" in data["result"]:
                        self._token = data["result"]["data"]
                        return True
        except Exception as exception:
            _LOGGER.error("Failed to login to Umbrel: %s", exception)
            raise

        return False

    async def _request(self, method: str, endpoint: str, params: dict = None) -> dict:
        if not self._token:
            await self.login()

        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        url = f"{self._host}{endpoint}"

        if method == "GET" and params:
            input_obj = {"json": params}
            encoded_input = urllib.parse.quote(json.dumps(input_obj))
            url = f"{url}?input={encoded_input}"
            params = None

        try:
            async with self._session.request(
                method,
                url,
                json=params if method == "POST" else None,
                headers=headers,
                ssl=False,
                timeout=20,
            ) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as exception:
            _LOGGER.error("Error communicating with Umbrel: %s", exception)
            raise

    async def get_system_info(self) -> dict:
        data = {}
        try:
            version_resp = await self._request("GET", "/trpc/system.version")
            data["version"] = version_resp.get("result", {}).get("data")
            
            uptime_resp = await self._request("GET", "/trpc/system.uptime")
            data["uptime"] = uptime_resp.get("result", {}).get("data")

            temp_resp = await self._request("GET", "/trpc/system.cpuTemperature")
            data["temperature"] = temp_resp.get("result", {}).get("data")
            

            cpu_resp = await self._request("GET", "/trpc/system.cpuUsage")
            data["cpu_usage"] = cpu_resp.get("result", {}).get("data")
            
            mem_resp = await self._request("GET", "/trpc/system.memoryUsage")
            data["memory"] = mem_resp.get("result", {}).get("data")
            
            disk_resp = await self._request("GET", "/trpc/system.diskUsage")
            data["disk"] = disk_resp.get("result", {}).get("data")
            
        except Exception as e:
            _LOGGER.error("Error fetching system info: %s", e)
            
        return data

    async def check_update(self) -> dict:
        try:
            response = await self._request("GET", "/trpc/system.checkUpdate")
            return response.get("result", {}).get("data", {})
        except Exception as e:
            _LOGGER.error("Error checking for updates: %s", e)
            return {"available": False}

    async def update_system(self) -> bool:
        try:
            await self._request("POST", "/trpc/system.update")
            return True
        except Exception:
            return False

    async def get_update_status(self) -> dict:
        try:
            response = await self._request("GET", "/trpc/system.updateStatus")
            return response.get("result", {}).get("data", {})
        except Exception:
            return {}

    async def is_2fa_enabled(self) -> bool:
        try:
            response = await self._request("GET", "/trpc/user.is2faEnabled")
            return response.get("result", {}).get("data", False)
        except Exception:
            return False

    async def get_external_devices(self) -> list:
        try:
            response = await self._request("GET", "/trpc/files.externalDevices")
            return response.get("result", {}).get("data", [])
        except Exception:
            return []

    async def get_backup_progress(self) -> list:
        try:
            response = await self._request("GET", "/trpc/backups.backupProgress")
            return response.get("result", {}).get("data", [])
        except Exception:
            return []

    async def get_apps(self) -> list:
        try:
            response = await self._request("GET", "/trpc/apps.list")
            apps_list = response.get("result", {}).get("data", [])
            return apps_list
        except Exception as e:
            _LOGGER.error("Error fetching apps: %s", e)
            return []

    async def get_app_state(self, app_id: str) -> dict:
        try:
            response = await self._request("GET", "/trpc/apps.state", {"appId": app_id})
            return response.get("result", {}).get("data", {})
        except Exception:
            return {}

    async def update_app(self, app_id: str) -> bool:
        try:
            await self._request("POST", "/trpc/apps.update", {"appId": app_id})
            return True
        except Exception as e:
            _LOGGER.error("Error updating app %s: %s", app_id, e)
            return False

    async def set_app_state(self, app_id: str, action: str) -> bool:
        endpoint = f"/trpc/apps.{action}"
        try:
            await self._request("POST", endpoint, {"appId": app_id})
            return True
        except Exception as e:
            _LOGGER.error("Error setting app state %s for %s: %s", action, app_id, e)
            return False

    async def reboot(self) -> bool:
        try:
            await self._request("POST", "/trpc/system.restart")
            return True
        except Exception:
            return False

    async def shutdown(self) -> bool:
        try:
            await self._request("POST", "/trpc/system.shutdown")
            return True
        except Exception:
            return False