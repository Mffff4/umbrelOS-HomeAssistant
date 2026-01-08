"""Button platform for Umbrel."""
from homeassistant.components.button import ButtonEntity
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
    """Set up Umbrel buttons."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        UmbrelRebootButton(coordinator),
        UmbrelShutdownButton(coordinator),
        UmbrelCheckUpdateButton(coordinator),
    ]

    apps = coordinator.data.get("apps", [])
    for app in apps:
        entities.append(UmbrelAppRestartButton(coordinator, app))
    
    async_add_entities(entities)

class UmbrelButtonBase(CoordinatorEntity, ButtonEntity):
    """Base class for Umbrel buttons."""

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

class UmbrelRebootButton(UmbrelButtonBase):
    """Button to reboot the system."""

    _attr_translation_key = "reboot"
    _attr_unique_id = "umbrel_reboot"
    _attr_icon = "mdi:restart"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.client.reboot()

class UmbrelShutdownButton(UmbrelButtonBase):
    """Button to shutdown the system."""

    _attr_translation_key = "shutdown"
    _attr_unique_id = "umbrel_shutdown"
    _attr_icon = "mdi:power"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.client.shutdown()

class UmbrelCheckUpdateButton(UmbrelButtonBase):
    """Button to check for updates."""

    _attr_translation_key = "check_update"
    _attr_unique_id = "umbrel_check_update"
    _attr_icon = "mdi:update"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.client.check_update()
        await self.coordinator.async_request_refresh()

class UmbrelAppRestartButton(UmbrelButtonBase):
    """Button to restart an app."""

    def __init__(self, coordinator: UmbrelCoordinator, app_data: dict) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.app_id = app_data.get("id")
        self._attr_name = f"Restart {app_data.get('name', self.app_id)}"
        self._attr_unique_id = f"umbrel_app_restart_{self.app_id}"
        self._attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.client.set_app_state(self.app_id, "restart")
        await self.coordinator.async_request_refresh()