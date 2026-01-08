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
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        UmbrelRebootButton(coordinator),
        UmbrelShutdownButton(coordinator),
        UmbrelCheckUpdateButton(coordinator),
    ]

    apps = coordinator.data.get("apps", [])
    for app in apps:
        entities.append(UmbrelAppRestartButton(coordinator, app))
        entities.append(UmbrelAppUpdateButton(coordinator, app))
    
    async_add_entities(entities)

class UmbrelButtonBase(CoordinatorEntity, ButtonEntity):

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

class UmbrelRebootButton(UmbrelButtonBase):

    _attr_translation_key = "reboot"
    _attr_unique_id = "umbrel_reboot"
    _attr_icon = "mdi:restart"

    async def async_press(self) -> None:
        await self.coordinator.client.reboot()

class UmbrelShutdownButton(UmbrelButtonBase):

    _attr_translation_key = "shutdown"
    _attr_unique_id = "umbrel_shutdown"
    _attr_icon = "mdi:power"

    async def async_press(self) -> None:
        await self.coordinator.client.shutdown()

class UmbrelCheckUpdateButton(UmbrelButtonBase):

    _attr_translation_key = "check_update"
    _attr_unique_id = "umbrel_check_update"
    _attr_icon = "mdi:update"

    async def async_press(self) -> None:
        await self.coordinator.client.check_update()
        await self.coordinator.async_request_refresh()

class UmbrelAppRestartButton(UmbrelButtonBase):

    def __init__(self, coordinator: UmbrelCoordinator, app_data: dict) -> None:
        super().__init__(coordinator)
        self.app_id = app_data.get("id")
        self._attr_name = f"Restart {app_data.get('name', self.app_id)}"
        self._attr_unique_id = f"umbrel_app_restart_{self.app_id}"
        self._attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        await self.coordinator.client.set_app_state(self.app_id, "restart")
        await self.coordinator.async_request_refresh()

class UmbrelAppUpdateButton(UmbrelButtonBase):

    def __init__(self, coordinator: UmbrelCoordinator, app_data: dict) -> None:
        super().__init__(coordinator)
        self.app_id = app_data.get("id")
        self._attr_name = f"Update {app_data.get('name', self.app_id)}"
        self._attr_unique_id = f"umbrel_app_update_{self.app_id}"
        self._attr_icon = "mdi:cloud-download"

    async def async_press(self) -> None:
        await self.coordinator.client.update_app(self.app_id)
        await self.coordinator.async_request_refresh()