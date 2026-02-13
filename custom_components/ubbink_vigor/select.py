"""Select platform for Ubbink Vigor."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import AIRFLOW_MODE_OPTIONS, BYPASS_MODE_OPTIONS, DOMAIN
from .coordinator import UbbinkVigorCoordinator
from .entity import UbbinkVigorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""
    coordinator: UbbinkVigorCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SelectEntity] = [
        UbbinkAirflowModeSelect(coordinator),
        UbbinkBypassModeSelect(coordinator),
    ]
    async_add_entities(entities)


class UbbinkAirflowModeSelect(UbbinkVigorEntity, SelectEntity):
    """Select entity for airflow mode control.

    Modes:
    - wall_unit: Hands control back to the wall unit / display
    - holiday / low / normal / high: Modbus switch presets (register 8001)
    """

    _attr_name = "Airflow Mode"
    _attr_icon = "mdi:hvac"
    _attr_options = AIRFLOW_MODE_OPTIONS

    def __init__(self, coordinator: UbbinkVigorCoordinator) -> None:
        """Initialise."""
        super().__init__(coordinator, "airflow_mode_select")

    @property
    def current_option(self) -> str | None:
        """Return the current airflow mode."""
        mode = self.coordinator.data.get("airflow_mode")
        if mode in self._attr_options:
            return mode
        # If control mode is 2 (custom flow rate), show as wall_unit equivalent
        return "wall_unit"

    async def async_select_option(self, option: str) -> None:
        """Set the airflow mode."""
        ok = await self.coordinator.client.set_airflow_mode(option)
        if ok:
            _LOGGER.debug("Airflow mode set to %s", option)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set airflow mode to %s", option)


class UbbinkBypassModeSelect(UbbinkVigorEntity, SelectEntity):
    """Select entity for bypass valve control.

    Modes:
    - Automatic: Bypass operates automatically based on temperature thresholds
    - Closed: Force bypass valve closed (heat recovery active)
    - Open: Force bypass valve open (free cooling / summer mode)

    Uses holding register 6100 (bypass mode):
    0 = Automatic, 1 = Closed, 2 = Open
    """

    _attr_name = "Bypass Mode"
    _attr_icon = "mdi:valve"
    _attr_options = BYPASS_MODE_OPTIONS

    def __init__(self, coordinator: UbbinkVigorCoordinator) -> None:
        """Initialise."""
        super().__init__(coordinator, "bypass_mode_select")

    @property
    def current_option(self) -> str | None:
        """Return the current bypass mode."""
        return self.coordinator.data.get("bypass_mode", "Automatic")

    async def async_select_option(self, option: str) -> None:
        """Set the bypass mode."""
        ok = await self.coordinator.client.set_bypass_mode(option)
        if ok:
            _LOGGER.debug("Bypass mode set to %s", option)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set bypass mode to %s", option)
