from typing import Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
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

    async_add_entities([UmbrelUpdateEntity(coordinator)])

class UmbrelUpdateEntity(CoordinatorEntity, UpdateEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "system_update"
    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.PROGRESS
    _attr_unique_id = "umbrel_system_update"

    def __init__(self, coordinator: UmbrelCoordinator) -> None:
        super().__init__(coordinator)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "system")},
            "name": "Umbrel System",
            "manufacturer": "Umbrel",
        }

    @property
    def installed_version(self) -> str | None:
        return self.coordinator.data["system"].get("version")

    @property
    def latest_version(self) -> str | None:
        update = self.coordinator.data.get("update", {})
        if update.get("available"):
            return update.get("version")
        return self.installed_version

    @property
    def release_notes(self) -> str | None:
        return self.coordinator.data.get("update", {}).get("releaseNotes")

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        await self.coordinator.client.update_system()
        await self.coordinator.async_request_refresh()