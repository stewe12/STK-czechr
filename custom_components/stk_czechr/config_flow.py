"""Config flow for STK czechr integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import (
    DOMAIN, 
    CONF_NAME, 
    CONF_VIN, 
    CONF_API_KEY,
    ERROR_INVALID_VIN, 
    ERROR_VIN_EXISTS,
    ERROR_API_KEY_MISSING
)

class STKczechrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STK czechr."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Check if VIN already exists
            existing_entries = [entry.data[CONF_VIN] for entry in self._async_current_entries()]
            if user_input[CONF_VIN] in existing_entries:
                errors["base"] = ERROR_VIN_EXISTS
            # Validate VIN
            elif not self._validate_vin(user_input[CONF_VIN]):
                errors["base"] = ERROR_INVALID_VIN
            # Validate API key
            elif not user_input.get(CONF_API_KEY):
                errors["base"] = ERROR_API_KEY_MISSING
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_VIN): str,
                vol.Required(CONF_API_KEY): str,
            }),
            errors=errors,
        )

    @staticmethod
    def _validate_vin(vin):
        """Validate the VIN."""
        if len(vin) != 17:
            return False
        return vin.isalnum()

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return STKczechrOptionsFlow(config_entry)

class STKczechrOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_API_KEY,
                    default=self.config_entry.data.get(CONF_API_KEY, "")
                ): str,
            })
        )
