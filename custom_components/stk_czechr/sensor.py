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
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),  # 1 minute
        )
        self.name = name
        self.vin = vin
        self.api_key = api_key
        self._session = aiohttp.ClientSession()
        self._last_request_time = None
        self._cached_data = None  # Cache for storing last successful data

    async def _async_update_data(self):
        """Fetch data using official API with rate limiting."""
        try:
            # Check if we should make a request (rate limiting)
            if not self._should_make_request():
                _LOGGER.debug("Rate limit active, skipping request for VIN %s", self.vin)
                if self._cached_data:
                    _LOGGER.debug("Using cached data for VIN %s", self.vin)
                    return self._cached_data
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
            
            # Make API call
            new_data = await self._call_api()
            
            # Only update cache and timestamp if API call was successful
            if new_data and "error" not in new_data:
                # Check if data has actually changed
                if self._has_data_changed(new_data):
                    _LOGGER.info("Data changed for VIN %s, updating cache", self.vin)
                    self._cached_data = new_data
                    self._last_request_time = datetime.now()
                else:
                    _LOGGER.debug("No data changes for VIN %s, keeping existing cache", self.vin)
                    # Still update timestamp to respect rate limiting
                    self._last_request_time = datetime.now()
            else:
                _LOGGER.warning("API call failed for VIN %s, keeping cached data", self.vin)
                # Return cached data if available, otherwise return error
                if self._cached_data:
                    return self._cached_data
                else:
                    return new_data
            
            return self._cached_data or new_data
            
        except Exception as err:
            _LOGGER.error("Error fetching data for VIN %s: %s", self.vin, err)
            # Return cached data if available, otherwise return error
            if self._cached_data:
                _LOGGER.debug("Returning cached data due to error for VIN %s", self.vin)
                return self._cached_data
            else:
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
            
            # Process data with better handling of missing values
            processed_data = {}
            
            # Core STK data - always try to get these
            processed_data["valid_until"] = self._format_date(vehicle_data.get("PravidelnaTechnickaProhlidkaDo"))
            processed_data["brand"] = vehicle_data.get("TovarniZnacka") or ""
            processed_data["model"] = vehicle_data.get("ObchodniOznaceni") or ""
            processed_data["vin"] = vehicle_data.get("VIN") or ""
            processed_data["color"] = vehicle_data.get("VozidloKaroserieBarva") or ""
            
            # Numeric values with proper handling
            processed_data["weight"] = self._safe_numeric(vehicle_data.get("HmotnostiProvozni"))
            processed_data["max_weight"] = self._safe_numeric(vehicle_data.get("HmotnostiPripPov"))
            processed_data["max_speed"] = self._safe_numeric(vehicle_data.get("NejvyssiRychlost"))
            processed_data["engine_displacement"] = self._safe_numeric(vehicle_data.get("MotorZdvihObjem"))
            processed_data["wheelbase"] = self._safe_numeric(vehicle_data.get("RozmeryRozvor"))
            processed_data["noise_driving"] = self._safe_numeric(vehicle_data.get("HlukJizda"))
            processed_data["owners_count"] = self._safe_numeric(vehicle_data.get("PocetVlastniku"))
            processed_data["operators_count"] = self._safe_numeric(vehicle_data.get("PocetProvozovatelu"))
            
            # Text values with fallback
            processed_data["tp_number"] = vehicle_data.get("CisloTp") or ""
            processed_data["orv_number"] = vehicle_data.get("CisloOrv") or ""
            processed_data["engine_power"] = vehicle_data.get("MotorMaxVykon") or ""
            processed_data["fuel_type"] = vehicle_data.get("Palivo") or ""
            processed_data["vehicle_type"] = vehicle_data.get("VozidloDruh") or ""
            processed_data["category"] = vehicle_data.get("Kategorie") or ""
            processed_data["status_name"] = vehicle_data.get("StatusNazev") or ""
            
            # Dates
            processed_data["first_registration"] = self._format_date(vehicle_data.get("DatumPrvniRegistrace"))
            processed_data["first_registration_cz"] = self._format_date(vehicle_data.get("DatumPrvniRegistraceVCr"))
            
            # Dimensions
            processed_data["length"] = self._safe_numeric(self._extract_dimension(vehicle_data.get("Rozmery"), 0))
            processed_data["width"] = self._safe_numeric(self._extract_dimension(vehicle_data.get("Rozmery"), 1))
            processed_data["height"] = self._safe_numeric(self._extract_dimension(vehicle_data.get("Rozmery"), 2))
            
            # Consumption and emissions
            processed_data["consumption_city"] = self._safe_numeric(self._clean_consumption(vehicle_data.get("SpotrebaNa100Km")))
            processed_data["consumption_highway"] = self._safe_numeric(self._clean_consumption(vehicle_data.get("SpotrebaNa100Km")))
            processed_data["consumption_combined"] = self._safe_numeric(self._clean_consumption(vehicle_data.get("SpotrebaNa100Km")))
            processed_data["co2_emissions"] = self._safe_numeric(self._clean_emissions(vehicle_data.get("EmiseCO2")))
            
            # Noise
            processed_data["noise_stationary"] = self._safe_numeric(self._clean_noise(vehicle_data.get("HlukStojiciOtacky")))
            
            # Tires
            processed_data["tires_front"] = self._extract_tire_info(vehicle_data.get("NapravyPneuRafky"), 0) or ""
            processed_data["tires_rear"] = self._extract_tire_info(vehicle_data.get("NapravyPneuRafky"), 1) or ""
            
            # Raw data for debugging
            processed_data["dimensions"] = vehicle_data.get("Rozmery") or ""
            
            # Calculate derived values
            if processed_data.get("valid_until"):
                processed_data["days_remaining"] = self._calculate_days_remaining(processed_data["valid_until"])
                processed_data["status"] = self._determine_status(processed_data["valid_until"])
            else:
                processed_data["days_remaining"] = 0
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

    def _safe_numeric(self, value):
        """Safely convert value to numeric, return 0 if conversion fails."""
        if value is None:
            return 0
        
        try:
            if isinstance(value, (int, float)):
                return value
            if isinstance(value, str):
                # Try to extract numeric value from string
                cleaned = value.strip()
                if cleaned and cleaned != "":
                    return float(cleaned)
        except (ValueError, TypeError):
            pass
        
        return 0

    async def async_unload(self):
        """Clean up resources."""
        await self._session.close()

    def _has_data_changed(self, new_data):
        """Check if new data is different from cached data."""
        if not self._cached_data:
            return True  # First time, consider it changed
        
        # Compare important fields that should trigger updates
        important_fields = [
            "valid_until", "days_remaining", "status", "weight", "max_speed",
            "engine_displacement", "length", "width", "height"
        ]
        
        for field in important_fields:
            old_value = self._cached_data.get(field)
            new_value = new_data.get(field)
            
            if old_value != new_value:
                _LOGGER.debug("Field %s changed: %s -> %s", field, old_value, new_value)
                return True
        
        return False

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
            return self._get_default_value()
            
        if "error" in self.coordinator.data:
            error = self.coordinator.data["error"]
            if error == ERROR_API_KEY_MISSING:
                return "API key required"
            _LOGGER.warning("Error in data for sensor %s: %s", self._attr_name, error)
            return self._get_default_value()
            
        data = self.coordinator.data
        if self._sensor_type == "status":
            return data.get("status", STKStatus.UNKNOWN)
        
        value = data.get(self._sensor_type)
        
        # Handle None values consistently
        if value is None:
            return self._get_default_value()
        
        _LOGGER.debug("Sensor %s value: %s", self._attr_name, value)
        return value

    def _get_default_value(self):
        """Get default value based on sensor type."""
        # For numeric sensors, return 0
        if hasattr(self, '_attr_unit_of_measurement') and self._attr_unit_of_measurement:
            return 0
        # For text sensors, return empty string
        return ""

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
