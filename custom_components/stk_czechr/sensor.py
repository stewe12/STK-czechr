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
    API_BASE_URL,
    API_REGISTRATION_URL,
    API_DOCUMENTATION_URL,
    API_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    ERROR_API_FAILED,
    ERROR_API_KEY_MISSING,
    CONF_API_KEY,
    STKStatus,
    CONF_NAME,
    CONF_VIN,
)

_LOGGER = logging.getLogger(__name__)

class STKczechrDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, name, vin, api_key):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{name} STK Data",
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),  # 24 hours
        )
        self.name = name
        self.vin = vin
        self.api_key = api_key
        self._session = aiohttp.ClientSession()
        self._last_request_time = None

    async def _async_update_data(self):
        """Fetch data using official API with rate limiting."""
        try:
            # Check if we should make a request (rate limiting)
            if not self._should_make_request():
                _LOGGER.debug("Rate limit active, skipping request for VIN %s", self.vin)
                if self.coordinator.data:
                    _LOGGER.debug("Using cached data for VIN %s", self.vin)
                    return self.coordinator.data
                else:
                    _LOGGER.warning("No cached data available for VIN %s", self.vin)
                    return {"error": "Rate limited and no cached data"}
            
            if not self.api_key:
                _LOGGER.warning("No API key provided for VIN %s", self.vin)
                return {
                    "error": ERROR_API_KEY_MISSING,
                    "api_registration_url": API_REGISTRATION_URL,
                    "api_documentation_url": API_DOCUMENTATION_URL,
                    "message": "Please register for API access at dataovozidlech.cz"
                }
            
            _LOGGER.info("Fetching data via official API for VIN %s", self.vin)
            
            # TODO: Implement actual API call once documentation is available
            # For now, return placeholder data
            data = await self._call_api()
            
            # Update last request time
            self._last_request_time = datetime.now()
            
            return data
            
        except Exception as err:
            _LOGGER.error("Error fetching data for VIN %s: %s", self.vin, err)
            return {"error": str(err)}

    async def _call_api(self):
        """Call the official API."""
        try:
            # TODO: Replace with actual API endpoint once documentation is available
            # This is a placeholder implementation
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "HomeAssistant-STK-czechr/0.4.0"
            }
            
            # Placeholder API call - will be replaced with actual endpoint
            url = f"{API_BASE_URL}/vehicle/{self.vin}"
            
            async with async_timeout.timeout(API_TIMEOUT):
                response = await self._session.get(url, headers=headers)
                
                if response.status == 200:
                    data = await response.json()
                    return self._process_api_data(data)
                elif response.status == 401:
                    return {"error": "Invalid API key"}
                elif response.status == 404:
                    return {"error": "Vehicle not found"}
                else:
                    return {"error": f"API request failed: {response.status}"}
                    
        except Exception as e:
            _LOGGER.error("API call failed: %s", e)
            return {"error": f"API call failed: {str(e)}"}

    def _process_api_data(self, data):
        """Process API response data."""
        try:
            # TODO: Implement actual data processing once API format is known
            # This is a placeholder implementation
            processed_data = {
                "valid_until": data.get("PravidelnaTechnickaProhlidkaDo"),
                "brand": data.get("TovarniZnacka"),
                "model": data.get("ObchodniOznaceni"),
                "vin": data.get("VIN"),
                "tp_number": data.get("CisloTp"),
                "orv_number": data.get("CisloOrv"),
                "color": data.get("VozidloKaroserieBarva"),
                "weight": data.get("HmotnostiProvozni"),
                "max_weight": data.get("HmotnostiPov"),
                "engine_power": data.get("MotorMaxVykon"),
                "fuel_type": data.get("Palivo"),
                "first_registration": data.get("DatumPrvniRegistrace"),
                "first_registration_cz": data.get("DatumPrvniRegistraceVCr"),
            }
            
            # Calculate derived values
            if processed_data.get("valid_until"):
                processed_data["days_remaining"] = self._calculate_days_remaining(processed_data["valid_until"])
                processed_data["status"] = self._determine_status(processed_data["valid_until"])
            else:
                processed_data["days_remaining"] = None
                processed_data["status"] = STKStatus.UNKNOWN
            
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

    def _should_make_request(self):
        """Check if we should make a request based on rate limiting."""
        if self._last_request_time is None:
            return True
        
        time_since_last = datetime.now() - self._last_request_time
        # Ensure at least 24 hours between requests
        return time_since_last.total_seconds() >= DEFAULT_UPDATE_INTERVAL

    async def async_unload(self):
        """Clean up resources."""
        await self._session.close()

class STKczechrSensor(CoordinatorEntity, SensorEntity):
    """Representation of a STK czechr sensor."""

    def __init__(self, coordinator, sensor_type):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator  # Store coordinator reference
        self._sensor_type = sensor_type
        self._attr_name = f"{coordinator.name} {SENSOR_TYPES[sensor_type]['name']}"
        self._attr_unique_id = f"{coordinator.vin}_{sensor_type}"  # Set unique_id directly
        self._attr_icon = SENSOR_TYPES[sensor_type]['icon']
        if "device_class" in SENSOR_TYPES[sensor_type]:
            self._attr_device_class = SENSOR_TYPES[sensor_type]['device_class']
        if "unit_of_measurement" in SENSOR_TYPES[sensor_type]:
            self._attr_unit_of_measurement = SENSOR_TYPES[sensor_type]['unit_of_measurement']

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.vin)},
            "name": self.coordinator.name,
            "manufacturer": "STK Czechr",
            "model": "Vehicle Information",
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            _LOGGER.debug("No data available for sensor %s", self._attr_name)
            return None
            
        if "error" in self.coordinator.data:
            error = self.coordinator.data["error"]
            if error == ERROR_API_KEY_MISSING:
                return "API key required"
            _LOGGER.warning("Error in data for sensor %s: %s", self._attr_name, error)
            return None
            
        data = self.coordinator.data
        if self._sensor_type == "status":
            return data.get("status", STKStatus.UNKNOWN)
        
        value = data.get(self._sensor_type)
        _LOGGER.debug("Sensor %s value: %s", self._attr_name, value)
        return value

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        if not self.coordinator.data or "error" not in self.coordinator.data:
            return None
            
        error = self.coordinator.data["error"]
        if error == ERROR_API_KEY_MISSING:
            return {
                "api_registration_url": self.coordinator.data.get("api_registration_url"),
                "api_documentation_url": self.coordinator.data.get("api_documentation_url"),
                "message": self.coordinator.data.get("message")
            }
        return None

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up STK czechr sensors from a config entry."""
    name = entry.data[CONF_NAME]
    vin = entry.data[CONF_VIN]
    api_key = entry.data.get(CONF_API_KEY, "")

    coordinator = STKczechrDataUpdateCoordinator(hass, name, vin, api_key)
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for sensor_type in SENSOR_TYPES:
        entities.append(STKczechrSensor(coordinator, sensor_type))

    async_add_entities(entities)
