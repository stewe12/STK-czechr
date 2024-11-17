import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN, CONF_NAME, CONF_VIN, SENSOR_TYPES, ERROR_INVALID_VIN, ERROR_VIN_EXISTS

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
            else:
                return await self.async_step_select_sensors(user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_VIN): str,
            }),
            errors=errors,
        )

    async def async_step_select_sensors(self, user_input):
        """Step to select which sensors the user wants to enable."""
        errors = {}

        if user_input is not None:
            # Save the selected sensors into options
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
                options={"enabled_sensors": user_input["enabled_sensors"]}
            )

        # Display available sensors to select from
        return self.async_show_form(
            step_id="select_sensors",
            data_schema=vol.Schema({
                vol.Optional("enabled_sensors", default=[]): selector.SelectSelector(
                    options=[sensor_key for sensor_key, sensor in SENSOR_TYPES.items() if sensor["enabled_by_default"]],
                    multiple=True
                )
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
