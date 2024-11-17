import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_NAME, CONF_VIN
import logging

_LOGGER = logging.getLogger(__name__)

class STKczechrDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, name, vin):
        """Initialize the data coordinator."""
        self.name = name
        self.vin = vin
        super().__init__(
            hass,
            _LOGGER,
            name=f"{name} Data",
            update_interval=timedelta(days=1),  # Update daily
        )

    async def _async_update_data(self):
        """Fetch data from the API."""
        url = f"https://www.dataovozidlech.cz/api/Vozidlo/GetVehicleInfo?vin={self.vin}"
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(10):
                    response = await session.get(url)
                    if response.status == 200:
                        data = await response.json()
                        state = data[0]["value"]  # Assuming the first element represents the state
                        attributes = {item["label"]: item["value"] for item in data}
                        return {"state": state, "attributes": attributes}
                    else:
                        _LOGGER.error("Error fetching data for VIN %s: HTTP %d", self.vin, response.status)
                        return {"state": None, "attributes": {"error": f"HTTP {response.status}"}}
        except Exception as e:
            _LOGGER.error("Exception while fetching data for VIN %s: %s", self.vin, e)
            return {"state": None, "attributes": {"error": str(e)}}


class STKczechrSensor(CoordinatorEntity, SensorEntity):
    """Representation of a STK czechr sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._coordinator.name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._coordinator.data.get("state") if self._coordinator.data else None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._coordinator.data.get("attributes") if self._coordinator.data else {}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up STK czechr sensors from a config entry."""
    name = entry.data[CONF_NAME]
    vin = entry.data[CONF_VIN]

    # Create coordinator
    coordinator = STKczechrDataUpdateCoordinator(hass, name, vin)

    # Perform the initial data fetch
    await coordinator.async_refresh()

    # Create and add the sensor
    async_add_entities([STKczechrSensor(coordinator)], update_before_add=True)
