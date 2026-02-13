"""Config flow for Ubbink Ubiflux Vigor integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant

from .const import (
    BRIDGE_MBUSD,
    BRIDGE_SER2NET,
    CONF_CONNECTION_TYPE,
    CONF_MODBUS_HOST,
    CONF_MODBUS_PORT,
    CONF_SERIAL_BAUDRATE,
    CONF_SERIAL_PARITY,
    CONF_SERIAL_PORT,
    CONF_SLAVE_ID,
    CONF_TCP_BRIDGE_TYPE,
    CONN_SERIAL,
    CONN_TCP,
    DEFAULT_BAUDRATE,
    DEFAULT_PARITY,
    DEFAULT_SLAVE_ID,
    DEFAULT_TCP_PORT,
    DOMAIN,
)
from .modbus_client import UbbinkModbusClient

_LOGGER = logging.getLogger(__name__)

STEP_CONNECTION_TYPE = vol.Schema(
    {
        vol.Required(CONF_CONNECTION_TYPE, default=CONN_TCP): vol.In(
            {CONN_TCP: "TCP (via ser2net / mbusd on remote device)", CONN_SERIAL: "Serial (direct USB on this machine)"}
        ),
    }
)

STEP_TCP = vol.Schema(
    {
        vol.Required(CONF_MODBUS_HOST): str,
        vol.Required(CONF_MODBUS_PORT, default=DEFAULT_TCP_PORT): int,
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
            int, vol.Range(min=1, max=247)
        ),
        vol.Required(CONF_TCP_BRIDGE_TYPE, default=BRIDGE_SER2NET): vol.In(
            {
                BRIDGE_SER2NET: "ser2net (raw serial tunnel → RTU framing)",
                BRIDGE_MBUSD: "mbusd (protocol converter → Modbus TCP framing)",
            }
        ),
    }
)

STEP_SERIAL = vol.Schema(
    {
        vol.Required(CONF_SERIAL_PORT, default="/dev/ttyUSB0"): str,
        vol.Required(CONF_SERIAL_BAUDRATE, default=DEFAULT_BAUDRATE): vol.In(
            {1200: "1200", 2400: "2400", 4800: "4800", 9600: "9600", 19200: "19200", 38400: "38400", 56000: "56000", 115200: "115200"}
        ),
        vol.Required(CONF_SERIAL_PARITY, default=DEFAULT_PARITY): vol.In(
            {"N": "None", "E": "Even", "O": "Odd"}
        ),
        vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): vol.All(
            int, vol.Range(min=1, max=247)
        ),
    }
)


async def _test_connection(hass: HomeAssistant, user_input: dict[str, Any]) -> str | None:
    """Test the Modbus connection. Returns error string or None on success."""
    conn_type = user_input[CONF_CONNECTION_TYPE]
    client = UbbinkModbusClient(
        connection_type=conn_type,
        slave_id=user_input[CONF_SLAVE_ID],
        serial_port=user_input.get(CONF_SERIAL_PORT),
        baudrate=user_input.get(CONF_SERIAL_BAUDRATE, DEFAULT_BAUDRATE),
        parity=user_input.get(CONF_SERIAL_PARITY, DEFAULT_PARITY),
        host=user_input.get(CONF_MODBUS_HOST),
        port=user_input.get(CONF_MODBUS_PORT, DEFAULT_TCP_PORT),
        bridge_type=user_input.get(CONF_TCP_BRIDGE_TYPE, BRIDGE_SER2NET),
    )
    try:
        connected = await client.connect()
        if not connected:
            return "cannot_connect"
        if not await client.test_connection():
            return "cannot_connect"
        return None
    except Exception:
        _LOGGER.exception("Connection test failed")
        return "cannot_connect"
    finally:
        await client.close()


class UbbinkVigorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ubbink Vigor."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step: choose connection type."""
        if user_input is not None:
            self._data[CONF_CONNECTION_TYPE] = user_input[CONF_CONNECTION_TYPE]
            if user_input[CONF_CONNECTION_TYPE] == CONN_TCP:
                return await self.async_step_tcp()
            return await self.async_step_serial()

        return self.async_show_form(step_id="user", data_schema=STEP_CONNECTION_TYPE)

    async def async_step_tcp(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle TCP connection details."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            error = await _test_connection(self.hass, self._data)
            if error:
                errors["base"] = error
            else:
                title = f"Vigor ({self._data[CONF_MODBUS_HOST]}:{self._data[CONF_MODBUS_PORT]})"
                return self.async_create_entry(title=title, data=self._data)

        return self.async_show_form(
            step_id="tcp", data_schema=STEP_TCP, errors=errors
        )

    async def async_step_serial(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle serial connection details."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            error = await _test_connection(self.hass, self._data)
            if error:
                errors["base"] = error
            else:
                title = f"Vigor ({self._data[CONF_SERIAL_PORT]})"
                return self.async_create_entry(title=title, data=self._data)

        return self.async_show_form(
            step_id="serial", data_schema=STEP_SERIAL, errors=errors
        )
