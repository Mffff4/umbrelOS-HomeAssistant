from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
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
    
    entities = [
        UmbrelUpdateBinarySensor(coordinator),
        Umbrel2faBinarySensor(coordinator),
        UmbrelBackupBinarySensor(coordinator),
    ]
    
    async_add_entities(entities)

class UmbrelBinarySensorBase(CoordinatorEntity, BinarySensorEntity):

    def __init__(self, coordinator: UmbrelCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "system")},
            "name": "Umbrel System",
            "manufacturer": "Umbrel",
        }

class UmbrelUpdateBinarySensor(UmbrelBinarySensorBase):

    _attr_translation_key = "update_available"
    _attr_device_class = BinarySensorDeviceClass.UPDATE
    _attr_unique_id = "umbrel_update_available"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("update", {}).get("available", False)

    @property
    def extra_state_attributes(self):
        update = self.coordinator.data.get("update", {})
        return {
            "version": update.get("version"),
            "name": update.get("name"),
            "release_notes": update.get("releaseNotes"),
        }

class Umbrel2faBinarySensor(UmbrelBinarySensorBase):

    _attr_translation_key = "2fa_enabled"
    _attr_device_class = BinarySensorDeviceClass.LOCK
    _attr_unique_id = "umbrel_2fa_enabled"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("2fa", False)

class UmbrelBackupBinarySensor(UmbrelBinarySensorBase):

    _attr_translation_key = "backup_in_progress"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_unique_id = "umbrel_backup_in_progress"

    @property
    def is_on(self) -> bool:
        progress_list = self.coordinator.data.get("backup_progress", [])
        return any(p.get("status") == "In Progress" for p in progress_list)