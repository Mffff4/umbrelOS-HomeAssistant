import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .umbrel_api import UmbrelApiClient
from .const import DOMAIN
from .coordinator import UmbrelCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR, 
    Platform.BINARY_SENSOR, 
    Platform.SWITCH, 
    Platform.BUTTON, 
    Platform.UPDATE
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    password = entry.data[CONF_PASSWORD]
    session = async_get_clientsession(hass)

    client = UmbrelApiClient(host, password, session)
    

    try:
        if not await client.login():
            _LOGGER.error("Could not log in to Umbrel: Invalid credentials or host")
            return False
    except Exception as ex:
        _LOGGER.error("Error connecting to Umbrel at %s: %s", host, ex)
        raise ConfigEntryNotReady(f"Timeout while connecting to {host}") from ex

    coordinator = UmbrelCoordinator(hass, client)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as ex:
        _LOGGER.error("Error fetching initial data from Umbrel: %s", ex)
        raise ConfigEntryNotReady(f"Error fetching initial data: {ex}") from ex

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok