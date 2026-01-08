"""Sensor platform for Umbrel."""
import logging
from datetime import datetime, timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import UmbrelCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Umbrel sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        UmbrelCpuSensor(coordinator),
        UmbrelMemorySensor(coordinator),
        UmbrelDiskSensor(coordinator),
        UmbrelTempSensor(coordinator),
        UmbrelUptimeSensor(coordinator),
    ]
    
    # Add external devices
    for device in coordinator.data.get("external_devices", []):
        entities.append(UmbrelExternalDeviceSensor(coordinator, device))

    # Add per-app sensors (Memory)
    apps_mem = coordinator.data.get("system", {}).get("memory", {}).get("apps", [])
    if apps_mem:
        # Map IDs to Names from apps list
        app_names = {a["id"]: a.get("name", a["id"]) for a in coordinator.data.get("apps", [])}
        for app_stat in apps_mem:
            entities.append(UmbrelAppMemorySensor(coordinator, app_stat["id"], app_names.get(app_stat["id"], app_stat["id"])))

    async_add_entities(entities)

class UmbrelSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for Umbrel sensors."""

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
            "model": self.coordinator.data["system"].get("version", "Unknown"),
        }

class UmbrelExternalDeviceSensor(UmbrelSensorBase):
    """Sensor for external storage device size."""

    def __init__(self, coordinator: UmbrelCoordinator, device: dict) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.device_id = device.get("id")
        self._attr_name = f"Storage {device.get('name', self.device_id)}"
        self._attr_native_unit_of_measurement = UnitOfInformation.GIGABYTES
        self._attr_device_class = SensorDeviceClass.DATA_SIZE
        self._attr_unique_id = f"umbrel_storage_{self.device_id}"

    @property
    def native_value(self):
        """Return disk size of the external device."""
        for device in self.coordinator.data.get("external_devices", []):
            if device.get("id") == self.device_id:
                return device.get("size")
        return None

    @property
    def extra_state_attributes(self):
        """Return device details."""
        for device in self.coordinator.data.get("external_devices", []):
            if device.get("id") == self.device_id:
                return {
                    "size_gb": device.get("size"),
                    "filesystem": device.get("filesystem"),
                    "mounted": device.get("mounted"),
                    "mount_path": device.get("mountPath"),
                }
        return {}

class UmbrelCpuSensor(UmbrelSensorBase):
    """CPU Usage Sensor."""

    _attr_translation_key = "cpu_usage"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unique_id = "umbrel_cpu_usage"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
             data = self.coordinator.data["system"].get("cpu_usage")
             if isinstance(data, dict):
                 return data.get("totalUsed")
             if isinstance(data, (int, float)):
                 return data
             return None
        except (KeyError, TypeError):
            return None

class UmbrelMemorySensor(UmbrelSensorBase):
    """Memory Usage Sensor."""

    _attr_translation_key = "memory_usage"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unique_id = "umbrel_memory_usage"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            data = self.coordinator.data["system"].get("memory")
            if isinstance(data, dict):
                pct = data.get("percentage")
                if pct is not None: return pct
                
                used = data.get("used") or data.get("totalUsed")
                total = data.get("total") or data.get("size")
                if used is not None and total:
                     return round((used / total) * 100, 1)
            return data
        except (KeyError, TypeError):
            return None

class UmbrelDiskSensor(UmbrelSensorBase):
    """Disk Usage Sensor."""

    _attr_translation_key = "disk_usage"
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unique_id = "umbrel_disk_usage"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            data = self.coordinator.data["system"].get("disk")
            if isinstance(data, dict):
                pct = data.get("percentage")
                if pct is not None: return pct
                
                used = data.get("used") or data.get("totalUsed")
                total = data.get("total") or data.get("size")
                if used is not None and total:
                     return round((used / total) * 100, 1)
            return data
        except (KeyError, TypeError):
            return None

class UmbrelTempSensor(UmbrelSensorBase):
    """Temperature Sensor."""

    _attr_translation_key = "temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_unique_id = "umbrel_temperature"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        try:
            data = self.coordinator.data["system"].get("temperature")
            if isinstance(data, dict):
                return data.get("temperature")
            return data
        except (KeyError, TypeError):
            return None

class UmbrelUptimeSensor(UmbrelSensorBase):
    """Uptime Sensor reported as timestamp of boot."""

    _attr_translation_key = "uptime"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_unique_id = "umbrel_uptime"

    @property
    def native_value(self):
        """Return the boot time of the system."""
        try:
            uptime_seconds = self.coordinator.data["system"].get("uptime")
            if uptime_seconds is not None:
                boot_time = dt_util.utcnow() - timedelta(seconds=float(uptime_seconds))
                return boot_time
            return None
        except (KeyError, TypeError, ValueError):
            return None

class UmbrelAppMemorySensor(UmbrelSensorBase):
    """Sensor for App Memory usage."""

    _attr_native_unit_of_measurement = UnitOfInformation.MEGABYTES
    _attr_device_class = SensorDeviceClass.DATA_SIZE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: UmbrelCoordinator, app_id: str, app_name: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.app_id = app_id
        self._attr_name = f"{app_name} Memory"
        self._attr_unique_id = f"umbrel_app_memory_{app_id}"

    @property
    def native_value(self):
        """Return memory usage in MB."""
        try:
            apps_mem = self.coordinator.data["system"].get("memory", {}).get("apps", [])
            for app in apps_mem:
                if app["id"] == self.app_id:
                    # Value is in bytes, convert to MB
                    return round(app["used"] / 1024 / 1024, 1)
            return 0
        except (KeyError, TypeError):
            return None
