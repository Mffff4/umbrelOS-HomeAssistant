"""DataUpdateCoordinator for Umbrel."""
import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .umbrel_api import UmbrelApiClient
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class UmbrelCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Umbrel data."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: UmbrelApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            # Parallel fetching for better performance
            system_info, apps, update_info, is_2fa_enabled, external_devices, backup_progress = await asyncio.gather(
                self.client.get_system_info(),
                self.client.get_apps(),
                self.client.check_update(),
                self.client.is_2fa_enabled(),
                self.client.get_external_devices(),
                self.client.get_backup_progress(),
                return_exceptions=True
            )
            
            # Handle potential exceptions in gather
            if isinstance(system_info, Exception): 
                _LOGGER.warning("Error fetching system info: %s", system_info)
                system_info = {}
            if isinstance(apps, Exception): 
                _LOGGER.warning("Error fetching apps: %s", apps)
                apps = []
            if isinstance(update_info, Exception): update_info = {"available": False}
            if isinstance(is_2fa_enabled, Exception): is_2fa_enabled = False
            if isinstance(external_devices, Exception): external_devices = []
            if isinstance(backup_progress, Exception): backup_progress = []

            return {
                "system": system_info,
                "apps": apps,
                "update": update_info,
                "2fa": is_2fa_enabled,
                "external_devices": external_devices,
                "backup_progress": backup_progress
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
