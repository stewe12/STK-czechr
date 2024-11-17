import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_NAME, CONF_VIN

class STKczechrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for STK czechr."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Kontrola, zda VIN již existuje
            existing_entries = [entry.data[CONF_VIN] for entry in self._async_current_entries()]
            if user_input[CONF_VIN] in existing_entries:
                errors["base"] = "vin_exists"
            # Validace VIN
            elif len(user_input[CONF_VIN]) != 17 or not user_input[CONF_VIN].isalnum():
                errors["base"] = "invalid_vin"
            else:
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        # Definice formuláře
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME, description={"suggested_value": "Jméno vozidla"}): str,
                vol.Required(CONF_VIN, description={"suggested_value": "VIN (17 znaků)"}): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
