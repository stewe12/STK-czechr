import asyncio
import aiohttp
import async_timeout
from datetime import timedelta
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_NAME, CONF_VIN

class STKczechrDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, name, vin):
        self.hass = hass
        self.name = name
        self.vin = vin
        self._state = None
        self._attributes = {}
        super().__init__(
            hass,
            asyncio.get_event_loop(),
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
                    data = await response.json()
                    self._state = data[0]["value"]  # Assuming the first element represents the state
                    self._attributes = {item["label"]: item["value"] for item in data}
        except Exception as e:
            self._state = None
            self._attributes = {}
            self._attributes["error"] = str(e)
        
        return self._state, self._attributes

class STKczechrSensor(SensorEntity):
    """Representation of a STK czechr sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self._coordinator = coordinator

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._coordinator.name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._coordinator.data[0] if self._coordinator.data else None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._coordinator.data[1] if self._coordinator.data else {}

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await self._coordinator.async_request_refresh()

async def async_setup_entry(hass, entry, platform):
    """Set up STK czechr sensors from a config entry."""
    name = entry.data[CONF_NAME]
    vin = entry.data[CONF_VIN]

    # Define coordinator
    coordinator = STKczechrDataUpdateCoordinator(hass, name, vin)

    # Perform the initial data fetch
    await coordinator.async_refresh()

    # Define the update callback
    async def async_update_callback():
        await coordinator.async_refresh()

    # Register the update callback
    entry.async_on_unload(
        hass.config_entries.async_forward_entry_unload(entry, "sensor")
    )

    # Define the sensor entity
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )

    # Return True to indicate successful setup
    return True

