import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_NAME, CONF_VIN

class STKczechrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STK czechr."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            self.logger.debug("User input received: %s", user_input)
            if user_input[CONF_VIN] in self.configured_vins:
                errors["base"] = "vin_exists"
            else:
                self.logger.debug("Creating entry with data: %s", user_input)
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required("name", description={"suggested_value": "Jméno vozidla"}): str,
                vol.Required("vin", description={"suggested_value": "VIN"}): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @property
    def configured_vins(self):
        """Return a set of configured VINs."""
        return {entry.data[CONF_VIN] for entry in self._async_current_entries()}
