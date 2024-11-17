"""STK Czechr sensor platform."""
from datetime import datetime, timedelta
import logging
import asyncio
import aiohttp
import async_timeout

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    API_ENDPOINT,
    API_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    ERROR_API_TIMEOUT,
    STKStatus,
    CONF_NAME,
    CONF_VIN,
)

_LOGGER = logging.getLogger(__name__)

class STKczechrDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, name, vin):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{name} STK Data",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        self.name = name
        self.vin = vin
        self._session = aiohttp.ClientSession()

    async def _async_update_data(self):
        """Fetch data from API."""
        try:
            async with async_timeout.timeout(API_TIMEOUT):
                response = await self._session.get(
                    f"{API_ENDPOINT}?vin={self.vin}"
                )
                if response.status == 200:
                    data = await response.json()
                    return self._process_api_data(data)
                else:
                    _LOGGER.error("API returned status %s", response.status)
                    return {"error": f"HTTP {response.status}"}
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout fetching data for VIN %s", self.vin)
            return {"error": ERROR_API_TIMEOUT}
        except Exception as err:
            _LOGGER.error("Error fetching data for VIN %s: %s", self.vin, err)
            return {"error": str(err)}

    def _process_api_data(self, data):
        """Process the API response data."""
        try:
            processed_data = {
                "last_check_date": data.get("lastCheckDate"),
                "valid_until": data.get("validUntil"),
                "days_remaining": self._calculate_days_remaining(data.get("validUntil")),
                "status": self._determine_status(data.get("validUntil")),
            }
            return processed_data
        except Exception as err:
            _LOGGER.error("Error processing API data: %s", err)
            return {"error": "Data processing error"}

    def _calculate_days_remaining(self, valid_until):
        """Calculate days remaining until expiration."""
        if not valid_until:
            return None
        try:
            expiry_date = datetime.strptime(valid_until, "%Y-%m-%d")
            remaining = expiry_date - datetime.now()
            return max(0, remaining.days)
        except ValueError:
            return None

    def _determine_status(self, valid_until):
        """Determine the status based on valid_until date."""
        if not valid_until:
            return STKStatus.UNKNOWN
            
        days_remaining = self._calculate_days_remaining(valid_until)
        if days_remaining is None:
            return STKStatus.UNKNOWN
        elif days_remaining <= 0:
            return STKStatus.EXPIRED
        elif days_remaining <= 30:
            return STKStatus.WARNING
        return STKStatus.VALID

    async def async_unload(self):
        """Clean up resources."""
        await self._session.close()

class STKczechrSensor(CoordinatorEntity, SensorEntity):
    """Representation of a STK czechr sensor."""

    def __init__(self, coordinator, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"{coordinator.name} {SENSOR_TYPES[sensor_type]['name']}"
        self._attr_icon = SENSOR_TYPES[sensor_type]['icon']
        if "device_class" in SENSOR_TYPES[sensor_type]:
            self._attr_device_class = SENSOR_TYPES[sensor_type]['device_class']
        if "unit_of_measurement" in SENSOR_TYPES[sensor_type]:
            self._attr_unit_of_measurement = SENSOR_TYPES[sensor_type]['unit_of_measurement']

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._coordinator.vin}_{self._sensor_type}"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._coordinator.vin)},
            "name": self._coordinator.name,
            "manufacturer": "STK Czechr",
            "model": "Vehicle Information",
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        if not self._coordinator.data or "error" in self._coordinator.data:
            return None
            
        data = self._coordinator.data
        if self._sensor_type == "status":
            return data.get("status", STKStatus.UNKNOWN)
        return data.get(self._sensor_type)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up STK czechr sensors from a config entry."""
    name = entry.data[CONF_NAME]
    vin = entry.data[CONF_VIN]

    coordinator = STKczechrDataUpdateCoordinator(hass, name, vin)
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for sensor_type in SENSOR_TYPES:
        entities.append(STKczechrSensor(coordinator, sensor_type))

    async_add_entities(entities)
