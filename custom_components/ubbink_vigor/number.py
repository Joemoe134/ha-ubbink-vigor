"""Number platform for Ubbink Vigor."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
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
    """Set up number entities."""
    coordinator: UbbinkVigorCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[NumberEntity] = [
        UbbinkFlowRateNumber(coordinator),
        UbbinkBypassTempDwellingNumber(coordinator),
        UbbinkBypassTempOutsideNumber(coordinator),
    ]
    async_add_entities(entities)


class UbbinkFlowRateNumber(UbbinkVigorEntity, NumberEntity):
    """Number entity for custom flow rate (m³/h).

    Writing to this entity sets Modbus control mode to 2 (flow rate)
    and writes the desired value to register 8002.

    Note: While in custom flow rate mode, the wall unit and humidity
    sensors cannot control the device. Use the Airflow Mode select
    to switch back to preset or wall_unit control.
    """

    _attr_name = "Custom Flow Rate"
    _attr_icon = "mdi:fan-speed-3"
    _attr_native_min_value = 50
    _attr_native_max_value = 400
    _attr_native_step = 5
    _attr_native_unit_of_measurement = "m³/h"
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: UbbinkVigorCoordinator) -> None:
        """Initialise."""
        super().__init__(coordinator, "custom_flow_rate")

    @property
    def native_value(self) -> float | None:
        """Return the current flow rate."""
        # If in flow rate control mode, show the set value
        if self.coordinator.data.get("modbus_control") == 2:
            return self.coordinator.data.get("desired_flow_rate")
        # Otherwise show the actual supply airflow
        return self.coordinator.data.get("supply_airflow_actual")

    async def async_set_native_value(self, value: float) -> None:
        """Set the custom flow rate."""
        ok = await self.coordinator.client.set_custom_flow_rate(int(value))
        if ok:
            _LOGGER.debug("Flow rate set to %s m³/h", value)
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to set flow rate to %s", value)


class UbbinkBypassTempDwellingNumber(UbbinkVigorEntity, NumberEntity):
    """Number entity for bypass dwelling temperature threshold.

    The bypass opens when the dwelling temperature exceeds this threshold
    AND the outside temperature meets its own threshold.
    Register 6101, range 15.0-35.0 °C.
    """

    _attr_name = "Bypass Dwelling Temp Threshold"
    _attr_icon = "mdi:thermometer"
    _attr_native_min_value = 15.0
    _attr_native_max_value = 35.0
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_mode = NumberMode.BOX
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: UbbinkVigorCoordinator) -> None:
        """Initialise."""
        super().__init__(coordinator, "bypass_temp_dwelling")

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get("bypass_temp_dwelling")

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        ok = await self.coordinator.client.set_bypass_temp_dwelling(value)
        if ok:
            await self.coordinator.async_request_refresh()


class UbbinkBypassTempOutsideNumber(UbbinkVigorEntity, NumberEntity):
    """Number entity for bypass outside temperature threshold.

    The bypass opens when the outside temperature exceeds this threshold.
    Register 6102, range 7.0-15.0 °C.
    """

    _attr_name = "Bypass Outside Temp Threshold"
    _attr_icon = "mdi:thermometer"
    _attr_native_min_value = 7.0
    _attr_native_max_value = 15.0
    _attr_native_step = 0.5
    _attr_native_unit_of_measurement = "°C"
    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_mode = NumberMode.BOX
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: UbbinkVigorCoordinator) -> None:
        """Initialise."""
        super().__init__(coordinator, "bypass_temp_outside")

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.coordinator.data.get("bypass_temp_outside")

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        ok = await self.coordinator.client.set_bypass_temp_outside(value)
        if ok:
            await self.coordinator.async_request_refresh()
