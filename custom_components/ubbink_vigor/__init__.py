"""The Ubbink Ubiflux Vigor integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    BRIDGE_SER2NET,
    CONF_CONNECTION_TYPE,
    CONF_MODBUS_HOST,
    CONF_MODBUS_PORT,
    CONF_SERIAL_BAUDRATE,
    CONF_SERIAL_PARITY,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_TCP_BRIDGE_TYPE,
    DEFAULT_BAUDRATE,
    DEFAULT_PARITY,
    DEFAULT_TCP_PORT,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import UbbinkVigorCoordinator
from .modbus_client import UbbinkModbusClient

_LOGGER = logging.getLogger(__name__)

type UbbinkVigorConfigEntry = ConfigEntry[UbbinkVigorCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: UbbinkVigorConfigEntry) -> bool:
    """Set up Ubbink Vigor from a config entry."""
    data = entry.data

    client = UbbinkModbusClient(
        connection_type=data[CONF_CONNECTION_TYPE],
        slave_id=data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID),
        serial_port=data.get(CONF_SERIAL_PORT),
        baudrate=data.get(CONF_SERIAL_BAUDRATE, DEFAULT_BAUDRATE),
        parity=data.get(CONF_SERIAL_PARITY, DEFAULT_PARITY),
        host=data.get(CONF_MODBUS_HOST),
        port=data.get(CONF_MODBUS_PORT, DEFAULT_TCP_PORT),
        bridge_type=data.get(CONF_TCP_BRIDGE_TYPE, BRIDGE_SER2NET),
    )

    connected = await client.connect()
    if not connected:
        _LOGGER.error("Failed to connect to Ubbink Vigor")
        return False

    coordinator = UbbinkVigorCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: UbbinkVigorCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.close()
    return unload_ok
