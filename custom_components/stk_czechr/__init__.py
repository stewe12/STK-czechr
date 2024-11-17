from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the STK czechr component."""
    hass.data.setdefault(DOMAIN, {})
    _LOGGER.info("STK czechr integration setup completed.")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up STK czechr from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    # Uložení konfigurace konkrétního vstupu
    hass.data[DOMAIN][entry.entry_id] = entry.data

    _LOGGER.info("Setting up STK czechr for entry: %s", entry.entry_id)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Unloading STK czechr for entry: %s", entry.entry_id)

    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    return True
