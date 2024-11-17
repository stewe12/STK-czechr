"""The STK czechr integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORM_SENSOR

import logging

_LOGGER = logging.getLogger(__name__)

ICON = "https://raw.githubusercontent.com/stewe12/STK-czechr/refs/heads/main/custom_components/stk_czechr/www/STK.png"

PLATFORMS = [PLATFORM_SENSOR]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the STK czechr component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up STK czechr from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
