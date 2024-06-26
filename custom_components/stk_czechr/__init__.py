"""STK czechr integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

DOMAIN = "stk_czechr"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the STK czechr component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up STK czechr from a config entry."""
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup, entry, "sensor"
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
