import aiohttp
import async_timeout
from homeassistant.components.sensor import SensorEntity
from .const import CONF_NAME, CONF_VIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up STK czechr sensors from a config entry."""
    name = entry.data[CONF_NAME]
    vin = entry.data[CONF_VIN]
    async_add_entities([STKczechrSensor(name, vin)], True)

class STKczechrSensor(SensorEntity):
    """Representation of a STK czechr sensor."""

    def __init__(self, name, vin):
        """Initialize the sensor."""
        self._name = name
        self._vin = vin
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    async def async_update(self):
        """Fetch new state data for the sensor."""
        url = f"https://www.dataovozidlech.cz/api/Vozidlo/GetVehicleInfo?vin={self._vin}"
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    response = await session.get(url)
                    data = await response.json()
                    self._state = data[0]["value"]  # Assuming the first element represents the state
                    self._attributes = {item["label"]: item["value"] for item in data}
        except Exception as e:
            self._state = None
            self._attributes = {}
            self._attributes["error"] = str(e)
