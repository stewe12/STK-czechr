import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_NAME, CONF_VIN

@callback
def configured_cars(hass):
    """Return a set of configured VINs."""
    return set(entry.data["vin"] for entry in hass.config_entries.async_entries(DOMAIN))

class STKczechrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STK czechr."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            if user_input["vin"] in configured_cars(self.hass):
                errors["base"] = "vin_exists"
            else:
                return self.async_create_entry(title=user_input["name"], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_VIN): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
