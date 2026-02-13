"""Sensor platform for Ubbink Vigor."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import UbbinkVigorCoordinator
from .entity import UbbinkVigorEntity


@dataclass(frozen=True, kw_only=True)
class UbbinkSensorDescription(SensorEntityDescription):
    """Describe an Ubbink sensor."""

    data_key: str
    value_fn: Any | None = None  # optional transform


SENSOR_DESCRIPTIONS: tuple[UbbinkSensorDescription, ...] = (
    # ── Airflow ──
    UbbinkSensorDescription(
        key="supply_airflow",
        name="Supply Airflow",
        data_key="supply_airflow_actual",
        native_unit_of_measurement="m³/h",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    UbbinkSensorDescription(
        key="exhaust_airflow",
        name="Exhaust Airflow",
        data_key="exhaust_airflow_actual",
        native_unit_of_measurement="m³/h",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    UbbinkSensorDescription(
        key="supply_airflow_setpoint",
        name="Supply Airflow Setpoint",
        data_key="supply_airflow_setpoint",
        native_unit_of_measurement="m³/h",
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan-chevron-up",
    ),
    # ── Pressure ──
    UbbinkSensorDescription(
        key="supply_pressure",
        name="Supply Pressure",
        data_key="supply_pressure",
        native_unit_of_measurement=UnitOfPressure.PA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    UbbinkSensorDescription(
        key="exhaust_pressure",
        name="Exhaust Pressure",
        data_key="exhaust_pressure",
        native_unit_of_measurement=UnitOfPressure.PA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ── Temperatures ──
    UbbinkSensorDescription(
        key="supply_temperature",
        name="Supply Temperature",
        data_key="supply_fan_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    UbbinkSensorDescription(
        key="exhaust_temperature",
        name="Exhaust Temperature",
        data_key="exhaust_fan_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    UbbinkSensorDescription(
        key="outside_temperature",
        name="Outside Temperature",
        data_key="outside_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    UbbinkSensorDescription(
        key="dwelling_temperature",
        name="Dwelling Temperature",
        data_key="dwelling_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ── Fan speeds ──
    UbbinkSensorDescription(
        key="supply_fan_speed",
        name="Supply Fan Speed",
        data_key="supply_fan_speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    UbbinkSensorDescription(
        key="exhaust_fan_speed",
        name="Exhaust Fan Speed",
        data_key="exhaust_fan_speed",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    # ── Humidity ──
    UbbinkSensorDescription(
        key="supply_humidity",
        name="Supply Humidity",
        data_key="supply_fan_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    UbbinkSensorDescription(
        key="exhaust_humidity",
        name="Exhaust Humidity",
        data_key="exhaust_fan_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    UbbinkSensorDescription(
        key="rht_humidity",
        name="RHT Humidity",
        data_key="rht_humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ── Preheater ──
    UbbinkSensorDescription(
        key="preheater_capacity",
        name="Preheater Capacity",
        data_key="preheater_capacity",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:radiator",
    ),
    UbbinkSensorDescription(
        key="frost_heater_power",
        name="Frost Heater Power",
        data_key="frost_heater_power",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake-alert",
    ),
    UbbinkSensorDescription(
        key="frost_fan_reduction",
        name="Frost Fan Reduction",
        data_key="frost_fan_reduction",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:snowflake",
    ),
    # ── CO2 ──
    UbbinkSensorDescription(
        key="co2_sensor1",
        name="CO₂ Sensor 1",
        data_key="co2_sensor1",
        native_unit_of_measurement="ppm",
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    UbbinkSensorDescription(
        key="co2_sensor2",
        name="CO₂ Sensor 2",
        data_key="co2_sensor2",
        native_unit_of_measurement="ppm",
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ── Operating ──
    UbbinkSensorDescription(
        key="operating_hours",
        name="Operating Hours",
        data_key="operating_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:clock-outline",
    ),
    UbbinkSensorDescription(
        key="filter_hours",
        name="Filter Hours",
        data_key="filter_hours",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:air-filter",
    ),
    # ── Status sensors (diagnostic) ──
    UbbinkSensorDescription(
        key="active_function",
        name="Active Function",
        data_key="active_function",
        icon="mdi:information-outline",
        entity_registry_enabled_default=True,
    ),
    UbbinkSensorDescription(
        key="ventilation_mode_sensor",
        name="Ventilation Mode",
        data_key="ventilation_mode",
        icon="mdi:hvac",
    ),
    UbbinkSensorDescription(
        key="bypass_status",
        name="Bypass Status",
        data_key="bypass_status",
        icon="mdi:valve",
    ),
    UbbinkSensorDescription(
        key="filter_status",
        name="Filter Status",
        data_key="filter_status",
        icon="mdi:air-filter",
    ),
    UbbinkSensorDescription(
        key="preheater_status",
        name="Preheater Status",
        data_key="preheater_status",
        icon="mdi:radiator",
    ),
    UbbinkSensorDescription(
        key="system_error",
        name="System Error",
        data_key="system_error",
        icon="mdi:alert-circle-outline",
    ),
    UbbinkSensorDescription(
        key="active_incident",
        name="Active Error Code",
        data_key="active_incident",
        icon="mdi:alert",
    ),
    UbbinkSensorDescription(
        key="fan_inlet_status",
        name="Supply Fan Status",
        data_key="fan_inlet_status",
        icon="mdi:fan",
        entity_registry_enabled_default=False,
    ),
    UbbinkSensorDescription(
        key="fan_exhaust_status",
        name="Exhaust Fan Status",
        data_key="fan_exhaust_status",
        icon="mdi:fan",
        entity_registry_enabled_default=False,
    ),
    UbbinkSensorDescription(
        key="serial_number",
        name="Serial Number",
        data_key="serial_number",
        icon="mdi:identifier",
        entity_registry_enabled_default=False,
    ),
    # ── Bypass config read-back ──
    UbbinkSensorDescription(
        key="bypass_temp_dwelling",
        name="Bypass Temp Dwelling",
        data_key="bypass_temp_dwelling",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=False,
    ),
    UbbinkSensorDescription(
        key="bypass_temp_outside",
        name="Bypass Temp Outside",
        data_key="bypass_temp_outside",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator: UbbinkVigorCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[UbbinkVigorSensor] = []

    for desc in SENSOR_DESCRIPTIONS:
        # Only add sensor if data key exists in coordinator data
        if desc.data_key in coordinator.data:
            entities.append(UbbinkVigorSensor(coordinator, desc))

    async_add_entities(entities)


class UbbinkVigorSensor(UbbinkVigorEntity, SensorEntity):
    """Sensor entity for Ubbink Vigor."""

    entity_description: UbbinkSensorDescription

    def __init__(
        self, coordinator: UbbinkVigorCoordinator, description: UbbinkSensorDescription
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        value = self.coordinator.data.get(self.entity_description.data_key)
        if self.entity_description.value_fn and value is not None:
            return self.entity_description.value_fn(value)
        return value
