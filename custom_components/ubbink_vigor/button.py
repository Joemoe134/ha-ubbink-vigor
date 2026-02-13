"""Button platform for Ubbink Vigor."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import UbbinkVigorCoordinator
from .entity import UbbinkVigorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities."""
    coordinator: UbbinkVigorCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        UbbinkFilterResetButton(coordinator),
        UbbinkApplianceResetButton(coordinator),
    ])


class UbbinkFilterResetButton(UbbinkVigorEntity, ButtonEntity):
    """Button to reset the filter warning.

    Writes 1 to register 8010.
    """

    _attr_name = "Reset Filter Warning"
    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator: UbbinkVigorCoordinator) -> None:
        """Initialise."""
        super().__init__(coordinator, "filter_reset")

    async def async_press(self) -> None:
        """Handle the button press."""
        ok = await self.coordinator.client.reset_filter()
        if ok:
            _LOGGER.info("Filter warning reset sent")
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to reset filter warning")


class UbbinkApplianceResetButton(UbbinkVigorEntity, ButtonEntity):
    """Button to reset the appliance.

    Writes 1 to register 8011. Use with caution.
    """

    _attr_name = "Appliance Reset"
    _attr_icon = "mdi:restart"
    _attr_device_class = ButtonDeviceClass.RESTART
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: UbbinkVigorCoordinator) -> None:
        """Initialise."""
        super().__init__(coordinator, "appliance_reset")

    async def async_press(self) -> None:
        """Handle the button press."""
        ok = await self.coordinator.client.reset_appliance()
        if ok:
            _LOGGER.info("Appliance reset sent")
        else:
            _LOGGER.error("Failed to reset appliance")
