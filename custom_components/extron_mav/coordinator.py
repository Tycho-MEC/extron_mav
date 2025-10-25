"""Data update coordinator for Extron MAV."""
import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, CONF_NUM_INPUTS, CONF_NUM_OUTPUTS, UPDATE_INTERVAL
from .extron_client import ExtronClient

_LOGGER = logging.getLogger(__name__)


class ExtronDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Extron MAV data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.client = ExtronClient(
            entry.data[CONF_HOST],
            entry.data[CONF_PORT],
            entry.data.get(CONF_PASSWORD),
        )
        self.num_inputs = entry.data[CONF_NUM_INPUTS]
        self.num_outputs = entry.data[CONF_NUM_OUTPUTS]
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def async_connect(self):
        """Connect to the Extron device."""
        try:
            await self.client.connect()
        except Exception as err:
            _LOGGER.error("Failed to connect to Extron MAV: %s", err)
            raise

    async def async_disconnect(self):
        """Disconnect from the Extron device."""
        await self.client.disconnect()

    async def _async_update_data(self):
        """Fetch data from Extron MAV."""
        try:
            # Get all output ties
            ties = await self.client.get_all_ties(self.num_outputs)
            return {"ties": ties}
        except Exception as err:
            _LOGGER.error("Error fetching data from Extron MAV: %s", err)
            raise UpdateFailed(f"Error communicating with device: {err}")

    async def async_set_output_tie(self, output: int, input_num: int):
        """Set an output to a specific input."""
        try:
            await self.client.set_output_tie(input_num, output)
            # Give the matrix a moment to process before refreshing
            await asyncio.sleep(0.2)
            # Update the data immediately
            await self.async_request_refresh()
        except Exception as err:
            _LOGGER.error("Error setting output tie: %s", err)
            raise