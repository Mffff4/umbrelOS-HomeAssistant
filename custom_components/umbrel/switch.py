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
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    apps = coordinator.data.get("apps", [])
    entities = []
    
    for app in apps:
        entities.append(UmbrelAppSwitch(coordinator, app))
    
    async_add_entities(entities)

class UmbrelAppSwitch(CoordinatorEntity, SwitchEntity):

    def __init__(self, coordinator: UmbrelCoordinator, app_data: dict) -> None:
        super().__init__(coordinator)
        self.app_id = app_data.get("id")
        self._attr_name = app_data.get("name", self.app_id)
        self._attr_unique_id = f"umbrel_app_{self.app_id}"
        self._attr_icon = "mdi:application"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "system")},
            "name": "Umbrel System",
            "manufacturer": "Umbrel",
        }

    @property
    def is_on(self) -> bool:
        apps = self.coordinator.data.get("apps", [])
        for app in apps:
            if app.get("id") == self.app_id:

                state = app.get("state", "").lower()
                return state in ["running", "ready", "starting"]
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        if await self.coordinator.client.set_app_state(self.app_id, "start"):
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if await self.coordinator.client.set_app_state(self.app_id, "stop"):
            await self.coordinator.async_request_refresh()