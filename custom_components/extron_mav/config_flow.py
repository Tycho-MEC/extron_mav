"""Config flow for Extron MAV Matrix Switcher."""
import logging
import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_NUM_INPUTS, CONF_NUM_OUTPUTS, DEFAULT_PORT
from .extron_client import ExtronClient

_LOGGER = logging.getLogger(__name__)


class ExtronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Extron MAV."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Test connection
            try:
                client = ExtronClient(
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input.get(CONF_PASSWORD),
                )
                
                # Try to connect and get basic info
                await client.connect()
                info = await client.get_info()
                await client.disconnect()
                
                # Create unique ID based on host
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                
                # Add matrix size to config
                user_input[CONF_NUM_INPUTS] = user_input.get(CONF_NUM_INPUTS, 8)
                user_input[CONF_NUM_OUTPUTS] = user_input.get(CONF_NUM_OUTPUTS, 8)
                
                return self.async_create_entry(
                    title=f"Extron MAV ({user_input[CONF_HOST]})",
                    data=user_input,
                )
            except Exception as err:
                _LOGGER.error("Error connecting to Extron MAV: %s", err)
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
                vol.Optional(CONF_PASSWORD): str,
                vol.Required(CONF_NUM_INPUTS, default=8): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=32)
                ),
                vol.Required(CONF_NUM_OUTPUTS, default=8): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=32)
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )