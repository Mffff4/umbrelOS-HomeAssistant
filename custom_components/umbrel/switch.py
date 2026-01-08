"""Switch platform for Umbrel."""
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import UmbrelCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Umbrel app switches."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    apps = coordinator.data.get("apps", [])
    entities = []
    
    for app in apps:
        entities.append(UmbrelAppSwitch(coordinator, app))
    
    async_add_entities(entities)

class UmbrelAppSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control an Umbrel App."""

    def __init__(self, coordinator: UmbrelCoordinator, app_data: dict) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.app_id = app_data.get("id")
        self._attr_name = app_data.get("name", self.app_id)
        self._attr_unique_id = f"umbrel_app_{self.app_id}"
        self._attr_icon = "mdi:application"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "system")},
            "name": "Umbrel System",
            "manufacturer": "Umbrel",
        }

    @property
    def is_on(self) -> bool:
        """Return true if app is running."""
        apps = self.coordinator.data.get("apps", [])
        for app in apps:
            if app.get("id") == self.app_id:
                # Umbrel uses "ready" or "running" for active apps
                state = app.get("state", "").lower()
                return state in ["running", "ready", "starting"]
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the app on."""
        if await self.coordinator.client.set_app_state(self.app_id, "start"):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the app off."""
        if await self.coordinator.client.set_app_state(self.app_id, "stop"):
            await self.coordinator.async_request_refresh()