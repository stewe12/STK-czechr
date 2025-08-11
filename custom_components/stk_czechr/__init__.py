"""The STK czechr integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from homeassistant.components.http import HomeAssistantView
from aiohttp import web
import aiohttp
import async_timeout
import json
import logging

from .const import DOMAIN, CONF_VIN, CONF_API_KEY, API_BASE_URL, API_TIMEOUT

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]

class STKApiDebugView(HomeAssistantView):
    """View to handle API debug requests."""

    url = "/api/stk_czechr/debug"
    name = "api:stk_czechr:debug"

    async def post(self, request):
        """Handle debug API request."""
        try:
            data = await request.json()
            vin = data.get("vin")
            api_key = data.get("api_key")
            
            if not vin or not api_key:
                return web.json_response({
                    "error": "Missing VIN or API key"
                }, status=400)
            
            # Make API call
            headers = {
                "API_KEY": api_key,
                "Content-Type": "application/json",
                "User-Agent": "HomeAssistant-STK-czechr-Debug/0.4.3"
            }
            
            url = f"{API_BASE_URL}?vin={vin}"
            
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(API_TIMEOUT):
                    response = await session.get(url, headers=headers)
                    
                    response_data = {
                        "status": response.status,
                        "headers": dict(response.headers),
                        "url": str(response.url)
                    }
                    
                    if response.status == 200:
                        try:
                            json_data = await response.json()
                            response_data["data"] = json_data
                            response_data["raw_text"] = await response.text()
                        except Exception as e:
                            response_data["error"] = f"JSON parsing failed: {str(e)}"
                            response_data["raw_text"] = await response.text()
                    else:
                        response_data["error"] = f"HTTP {response.status}"
                        response_data["raw_text"] = await response.text()
                    
                    return web.json_response(response_data)
                    
        except Exception as e:
            return web.json_response({
                "error": f"Debug request failed: {str(e)}"
            }, status=500)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the STK czechr component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up STK czechr from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register HTTP endpoint for API debugging
    hass.http.register_view(STKApiDebugView())

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
