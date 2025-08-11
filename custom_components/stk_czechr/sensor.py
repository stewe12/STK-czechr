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
            # API call according to official documentation
            headers = {
                "API_KEY": self.api_key,  # Correct header name
                "Content-Type": "application/json",
                "User-Agent": "HomeAssistant-STK-czechr/0.4.1"
            }
            
            # Correct API endpoint with vin parameter
            url = f"{API_BASE_URL}?vin={self.vin}"
            
            _LOGGER.debug("Calling API: %s", url)
            
            async with async_timeout.timeout(API_TIMEOUT):
                response = await self._session.get(url, headers=headers)
                
                _LOGGER.debug("API response status: %s", response.status)
                
                if response.status == 200:
                    data = await response.json()
                    _LOGGER.debug("API response data: %s", data)
                    return self._process_api_data(data)
                elif response.status == 401:
                    return {"error": "Invalid API key"}
                elif response.status == 404:
                    return {"error": "Vehicle not found"}
                elif response.status == 429:
                    return {"error": "Rate limited - too many requests"}
                else:
                    error_text = await response.text()
                    _LOGGER.error("API error %s: %s", response.status, error_text)
                    return {"error": f"API request failed: {response.status}"}
                    
        except Exception as e:
            _LOGGER.error("API call failed: %s", e)
            return {"error": f"API call failed: {str(e)}"}

    def _process_api_data(self, data):
        """Process API response data."""
        try:
            _LOGGER.debug("Processing API data: %s", data)
            
            # Check if data is empty or has error
            if not data or not isinstance(data, dict):
                return {"error": "No data received from API"}
            
            # Extract vehicle data from API response
            # The API returns data in a specific structure with Status and Data fields
            if "Status" in data and data["Status"] == 1 and "Data" in data:
                vehicle_data = data["Data"]
            else:
                return {"error": "Invalid API response format"}
            
            processed_data = {
                "valid_until": self._format_date(vehicle_data.get("PravidelnaTechnickaProhlidkaDo")),
                "brand": vehicle_data.get("TovarniZnacka"),
                "model": vehicle_data.get("ObchodniOznaceni"),
                "vin": vehicle_data.get("VIN"),
                "tp_number": vehicle_data.get("CisloTp"),
                "orv_number": vehicle_data.get("CisloOrv"),
                "color": vehicle_data.get("VozidloKaroserieBarva"),
                "weight": vehicle_data.get("HmotnostiProvozni"),
                "max_weight": vehicle_data.get("HmotnostiPripPov"),
                "engine_power": vehicle_data.get("MotorMaxVykon"),
                "fuel_type": vehicle_data.get("Palivo"),
                "first_registration": self._format_date(vehicle_data.get("DatumPrvniRegistrace")),
                "first_registration_cz": self._format_date(vehicle_data.get("DatumPrvniRegistraceVCr")),
                "max_speed": vehicle_data.get("NejvyssiRychlost"),
                "consumption_city": self._clean_consumption(vehicle_data.get("SpotrebaNa100Km")),
                "consumption_highway": self._clean_consumption(vehicle_data.get("SpotrebaNa100Km")),
                "consumption_combined": self._clean_consumption(vehicle_data.get("SpotrebaNa100Km")),
                "co2_emissions": self._clean_emissions(vehicle_data.get("EmiseCO2")),
                "vehicle_type": vehicle_data.get("VozidloDruh"),
                "category": vehicle_data.get("Kategorie"),
                "engine_displacement": vehicle_data.get("MotorZdvihObjem"),
                "dimensions": vehicle_data.get("Rozmery"),
                "wheelbase": vehicle_data.get("RozmeryRozvor"),
                "noise_stationary": self._clean_noise(vehicle_data.get("HlukStojiciOtacky")),
                "noise_driving": vehicle_data.get("HlukJizda"),
                "status_name": vehicle_data.get("StatusNazev"),
                "owners_count": vehicle_data.get("PocetVlastniku"),
                "operators_count": vehicle_data.get("PocetProvozovatelu"),
                "tires_front": self._extract_tire_info(vehicle_data.get("NapravyPneuRafky"), 0),
                "tires_rear": self._extract_tire_info(vehicle_data.get("NapravyPneuRafky"), 1),
                "length": self._extract_dimension(vehicle_data.get("Rozmery"), 0),
                "width": self._extract_dimension(vehicle_data.get("Rozmery"), 1),
                "height": self._extract_dimension(vehicle_data.get("Rozmery"), 2),
            }
            
            # Calculate derived values
            if processed_data.get("valid_until"):
                processed_data["days_remaining"] = self._calculate_days_remaining(processed_data["valid_until"])
                processed_data["status"] = self._determine_status(processed_data["valid_until"])
            else:
                processed_data["days_remaining"] = None
                processed_data["status"] = STKStatus.UNKNOWN
            
            _LOGGER.debug("Processed data: %s", processed_data)
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
        # Ensure at least 1 minute between requests
        return time_since_last.total_seconds() >= DEFAULT_UPDATE_INTERVAL

    def _extract_dimension(self, dimensions_str, index):
        """Extract specific dimension from dimensions string."""
        if not dimensions_str:
            return None
        
        try:
            # Format: "2210/ 780/ 1305" -> ["2210", "780", "1305"]
            parts = [part.strip() for part in dimensions_str.split('/')]
            if len(parts) > index and parts[index].strip():
                return parts[index].strip()
        except Exception:
            pass
        
        return None

    def _format_date(self, date_str):
        """Format date string for Home Assistant."""
        if not date_str:
            return None
        
        try:
            # Parse ISO date format and return YYYY-MM-DD
            if 'T' in date_str:
                date_part = date_str.split('T')[0]
                return date_part
            return date_str
        except Exception:
            return None

    def _clean_consumption(self, consumption_str):
        """Clean consumption string and extract numeric value."""
        if not consumption_str:
            return None
        
        try:
            # Format: " / / 3.5" -> extract "3.5"
            parts = [part.strip() for part in consumption_str.split('/')]
            for part in parts:
                if part and part.strip() and part.strip() != "":
                    try:
                        return float(part.strip())
                    except ValueError:
                        continue
        except Exception:
            pass
        
        return None

    def _clean_emissions(self, emissions_str):
        """Clean emissions string and extract numeric value."""
        if not emissions_str:
            return None
        
        try:
            # Format: " / / " -> return None
            parts = [part.strip() for part in emissions_str.split('/')]
            for part in parts:
                if part and part.strip() and part.strip() != "":
                    try:
                        return float(part.strip())
                    except ValueError:
                        continue
        except Exception:
            pass
        
        return None

    def _clean_noise(self, noise_str):
        """Clean noise string and extract numeric value."""
        if not noise_str:
            return None
        
        try:
            # Format: "87/ 3750" -> extract "87"
            parts = [part.strip() for part in noise_str.split('/')]
            if parts and parts[0].strip():
                return float(parts[0].strip())
        except Exception:
            pass
        
        return None

    def _extract_tire_info(self, tires_str, index):
        """Extract tire information from tires string."""
        if not tires_str:
            return None
        
        try:
            # Format: "120/70-15 M/C 56S TL/ 3.5 x 15;\n150/70-14 M/C 66S TL/ 4.25 x 14;\n/ ;\n/ ;\n"
            lines = [line.strip() for line in tires_str.split(';') if line.strip()]
            if len(lines) > index and lines[index].strip():
                return lines[index].strip()
        except Exception:
            pass
        
        return None

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
        
        # Handle None values consistently
        if value is None:
            # For numeric sensors, return 0 instead of None to avoid state changes
            if hasattr(self, '_attr_unit_of_measurement') and self._attr_unit_of_measurement:
                return 0
            # For text sensors, return empty string instead of None
            return ""
        
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
