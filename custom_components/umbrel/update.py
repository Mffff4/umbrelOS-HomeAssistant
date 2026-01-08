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
    
    entities = [UmbrelUpdateEntity(coordinator)]
    

    apps = coordinator.data.get("apps", [])
    for app in apps:
        entities.append(UmbrelAppUpdateEntity(coordinator, app))

    async_add_entities(entities)

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

class UmbrelAppUpdateEntity(CoordinatorEntity, UpdateEntity):

    _attr_has_entity_name = True
    _attr_device_class = UpdateDeviceClass.FIRMWARE

    _attr_supported_features = UpdateEntityFeature.INSTALL 

    def __init__(self, coordinator: UmbrelCoordinator, app_data: dict) -> None:
        super().__init__(coordinator)
        self.app_id = app_data.get("id")
        self._attr_name = f"{app_data.get('name', self.app_id)} Update"
        self._attr_unique_id = f"umbrel_app_update_{self.app_id}"
        self._initial_version = app_data.get("version")

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "system")},
            "name": "Umbrel System",
            "manufacturer": "Umbrel",
        }

    @property
    def installed_version(self) -> str | None:

        for app in self.coordinator.data.get("apps", []):
            if app.get("id") == self.app_id:
                return app.get("version")
        return self._initial_version

    @property
    def latest_version(self) -> str | None:

        return self.installed_version

    async def async_install(
        self, version: str | None, backup: bool, **kwargs: Any
    ) -> None:
        await self.coordinator.client.update_app(self.app_id)
        await self.coordinator.async_request_refresh()