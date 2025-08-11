"""STK Czechr sensor platform."""
from datetime import datetime, timedelta
import logging
import asyncio
import aiohttp
import async_timeout
import re

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity

from .const import (
    DOMAIN,
    SENSOR_TYPES,
    WEB_SEARCH_URL,
    API_TIMEOUT,
    DEFAULT_UPDATE_INTERVAL,
    ERROR_WEB_SCRAPING_FAILED,
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
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),  # 24 hours
        )
        self.name = name
        self.vin = vin
        self._session = aiohttp.ClientSession()
        self._last_request_time = None

    async def _async_update_data(self):
        """Fetch data using web scraping with rate limiting."""
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
            
            _LOGGER.info("Fetching data via web scraping for VIN %s", self.vin)
            data = await self._scrape_web_data()
            
            # Update last request time
            self._last_request_time = datetime.now()
            
            if data and "error" not in data:
                _LOGGER.info("Successfully fetched data for VIN %s: %s", self.vin, list(data.keys()))
            else:
                _LOGGER.error("Failed to fetch data for VIN %s: %s", self.vin, data.get("error", "Unknown error"))
            
            return data
            
        except Exception as err:
            _LOGGER.error("Error fetching data for VIN %s: %s", self.vin, err)
            return {"error": str(err)}

    def _should_make_request(self):
        """Check if we should make a request based on rate limiting."""
        if self._last_request_time is None:
            return True
        
        time_since_last = datetime.now() - self._last_request_time
        # Ensure at least 24 hours between requests
        return time_since_last.total_seconds() >= DEFAULT_UPDATE_INTERVAL

    async def _scrape_web_data(self):
        """Scrape data from the web interface with proper delays."""
        try:
            # Add a small delay to be respectful to the server
            await asyncio.sleep(2)
            
            # First, get the search page to get any necessary tokens
            async with async_timeout.timeout(API_TIMEOUT):
                response = await self._session.get(WEB_SEARCH_URL)
                if response.status != 200:
                    return {"error": f"Failed to access search page: {response.status}"}
                
                html_content = await response.text()
                
                # Extract any CSRF tokens or session data if needed
                csrf_token = self._extract_csrf_token(html_content)
                
                # Add another delay before form submission
                await asyncio.sleep(1)
                
                # Prepare query parameters for GET request
                params = {
                    'vin': self.vin,
                    'search': 'Vyhledat'
                }
                
                if csrf_token:
                    params['_token'] = csrf_token
                
                # Submit the search form with GET method and proper headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Referer': WEB_SEARCH_URL,
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                search_response = await self._session.get(
                    WEB_SEARCH_URL,
                    params=params,
                    headers=headers
                )
                
                if search_response.status == 200:
                    result_html = await search_response.text()
                    return self._parse_html_data(result_html)
                else:
                    return {"error": f"Search request failed: {search_response.status}"}
                    
        except Exception as e:
            _LOGGER.error("Web scraping failed: %s", e)
            return {"error": f"Web scraping failed: {str(e)}"}

    def _extract_csrf_token(self, html_content):
        """Extract CSRF token from HTML content."""
        # Look for common CSRF token patterns
        patterns = [
            r'<meta name="csrf-token" content="([^"]+)"',
            r'<input[^>]*name="_token"[^>]*value="([^"]+)"',
            r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html_content)
            if match:
                return match.group(1)
        return None

    def _parse_html_data(self, html_content):
        """Parse vehicle data from HTML content."""
        try:
            _LOGGER.debug("Parsing HTML data for VIN %s", self.vin)
            
            # Extract data from HTML table
            data = {}
            
            # Look for STK expiration date
            stk_pattern = r'<tr><th><b>Pravidelná technická prohlídka do</b></th><td>([^<]+)</td></tr>'
            stk_match = re.search(stk_pattern, html_content)
            if stk_match:
                valid_until = stk_match.group(1).strip()
                _LOGGER.debug("Found STK date: %s", valid_until)
                if valid_until and valid_until != "":
                    # Convert date from DD.MM.YYYY to YYYY-MM-DD format
                    try:
                        date_obj = datetime.strptime(valid_until, "%d.%m.%Y")
                        data["valid_until"] = date_obj.strftime("%Y-%m-%d")
                        _LOGGER.debug("Converted STK date: %s", data["valid_until"])
                    except ValueError:
                        _LOGGER.error("Error parsing STK date: %s", valid_until)
                        data["valid_until"] = None
                else:
                    data["valid_until"] = None
            else:
                _LOGGER.warning("STK date not found in HTML content")
            
            # Extract other vehicle information
            patterns = {
                'brand': r'<tr><th><b>Tovární značka</b></th><td>([^<]+)</td></tr>',
                'model': r'<tr><th><b>Obchodní označení</b></th><td>([^<]+)</td></tr>',
                'vin': r'<tr><th><b>VIN</b></th><td>([^<]+)</td></tr>',
                'tp_number': r'<tr><th><b>Číslo TP</b></th><td>([^<]+)</td></tr>',
                'orv_number': r'<tr><th><b>Číslo ORV</b></th><td>([^<]+)</td></tr>',
                'color': r'<tr><th><b>Barva</b></th><td>([^<]+)</td></tr>',
                'weight': r'<tr><th><b>Provozní hmotnost</b></th><td>([^<]+)</td></tr>',
                'max_weight': r'<tr><th><b>Největší technicky přípustná/povolená hmotnost \[kg\]</b></th><td>([^<]+)</td></tr>',
                'engine_power': r'<tr><th><b>Max\. výkon \[kW\] / \[min⁻¹\]</b></th><td>([^<]+)</td></tr>',
                'fuel_type': r'<tr><th><b>Palivo</b></th><td>([^<]+)</td></tr>',
                'first_registration': r'<tr><th><b>Datum 1\. registrace</b></th><td>([^<]+)</td></tr>',
                'first_registration_cz': r'<tr><th><b>Datum 1\. registrace v ČR</b></th><td>([^<]+)</td></tr>',
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, html_content)
                if match:
                    value = match.group(1).strip()
                    if value and value != "":
                        data[key] = value
                        _LOGGER.debug("Found %s: %s", key, value)
            
            # Calculate derived values
            if "valid_until" in data and data["valid_until"]:
                data["days_remaining"] = self._calculate_days_remaining(data["valid_until"])
                data["status"] = self._determine_status(data["valid_until"])
                _LOGGER.debug("Calculated days_remaining: %s, status: %s", data["days_remaining"], data["status"])
            else:
                data["days_remaining"] = None
                data["status"] = STKStatus.UNKNOWN
                _LOGGER.warning("Could not calculate days_remaining and status - no valid_until date")
            
            _LOGGER.info("Successfully parsed data with %d fields", len(data))
            return data
            
        except Exception as err:
            _LOGGER.error("Error parsing HTML data: %s", err)
            return {"error": "HTML parsing error"}

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
            _LOGGER.warning("Error in data for sensor %s: %s", self._attr_name, self.coordinator.data["error"])
            return None
            
        data = self.coordinator.data
        if self._sensor_type == "status":
            return data.get("status", STKStatus.UNKNOWN)
        
        value = data.get(self._sensor_type)
        _LOGGER.debug("Sensor %s value: %s", self._attr_name, value)
        return value

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
