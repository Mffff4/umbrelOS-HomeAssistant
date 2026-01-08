"""Binary sensor platform for Umbrel."""
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
    """Set up Umbrel binary sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        UmbrelUpdateBinarySensor(coordinator),
        Umbrel2faBinarySensor(coordinator),
        UmbrelBackupBinarySensor(coordinator),
    ]
    
    async_add_entities(entities)

class UmbrelBinarySensorBase(CoordinatorEntity, BinarySensorEntity):
    """Base class for Umbrel binary sensors."""

    def __init__(self, coordinator: UmbrelCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, "system")},
            "name": "Umbrel System",
            "manufacturer": "Umbrel",
        }

class UmbrelUpdateBinarySensor(UmbrelBinarySensorBase):
    """Binary sensor for update availability."""

    _attr_translation_key = "update_available"
    _attr_device_class = BinarySensorDeviceClass.UPDATE
    _attr_unique_id = "umbrel_update_available"

    @property
    def is_on(self) -> bool:
        """Return true if update is available."""
        return self.coordinator.data.get("update", {}).get("available", False)

    @property
    def extra_state_attributes(self):
        """Return version info."""
        update = self.coordinator.data.get("update", {})
        return {
            "version": update.get("version"),
            "name": update.get("name"),
            "release_notes": update.get("releaseNotes"),
        }

class Umbrel2faBinarySensor(UmbrelBinarySensorBase):
    """Binary sensor for 2FA status."""

    _attr_translation_key = "2fa_enabled"
    _attr_device_class = BinarySensorDeviceClass.LOCK
    _attr_unique_id = "umbrel_2fa_enabled"

    @property
    def is_on(self) -> bool:
        """Return true if 2FA is enabled."""
        return self.coordinator.data.get("2fa", False)

class UmbrelBackupBinarySensor(UmbrelBinarySensorBase):
    """Binary sensor for backup progress."""

    _attr_translation_key = "backup_in_progress"
    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_unique_id = "umbrel_backup_in_progress"

    @property
    def is_on(self) -> bool:
        """Return true if any backup is in progress."""
        progress_list = self.coordinator.data.get("backup_progress", [])
        return any(p.get("status") == "In Progress" for p in progress_list)
