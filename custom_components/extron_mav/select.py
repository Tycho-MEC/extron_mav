"""Select platform for Extron MAV Matrix Switcher."""
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ExtronDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Extron MAV select entities."""
    coordinator: ExtronDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # Create a select entity for each output
    for output in range(1, coordinator.num_outputs + 1):
        entities.append(ExtronOutputSelect(coordinator, output))
    
    async_add_entities(entities)


class ExtronOutputSelect(CoordinatorEntity, SelectEntity):
    """Representation of an Extron MAV output selector."""

    def __init__(self, coordinator: ExtronDataUpdateCoordinator, output: int) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._output = output
        self._attr_name = f"Output {output}"
        self._attr_unique_id = f"{coordinator.entry.entry_id}_output_{output}"
        
        # Create options list: "None" (untied) plus all inputs
        self._attr_options = ["None"] + [
            f"Input {i}" for i in range(1, coordinator.num_inputs + 1)
        ]

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.entry.entry_id)},
            "name": f"Extron MAV ({self.coordinator.client.host})",
            "manufacturer": "Extron",
            "model": "MAV Plus",
        }

    @property
    def current_option(self) -> str:
        """Return the current selected input."""
        if self.coordinator.data and "ties" in self.coordinator.data:
            tied_input = self.coordinator.data["ties"].get(self._output, 0)
            if tied_input == 0:
                return "None"
            return f"Input {tied_input}"
        return "None"

    async def async_select_option(self, option: str) -> None:
        """Change the selected input."""
        if option == "None":
            input_num = 0
        else:
            # Extract input number from "Input X"
            input_num = int(option.split()[-1])
        
        await self.coordinator.async_set_output_tie(self._output, input_num)
