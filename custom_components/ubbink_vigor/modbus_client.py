"""Modbus client wrapper for Ubbink Ubiflux Vigor."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from pymodbus.client import AsyncModbusSerialClient, AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.framer import FramerType

from .const import (
    CONN_SERIAL,
    CONN_TCP,
    BRIDGE_SER2NET,
    BRIDGE_MBUSD,
    DEFAULT_BAUDRATE,
    DEFAULT_PARITY,
    DEFAULT_SLAVE_ID,
    DEFAULT_TCP_PORT,
    # Input registers
    REG_SERIAL_0,
    REG_ACTIVE_FUNCTION,
    REG_VENTILATION_MODE,
    REG_SUPPLY_PRESSURE,
    REG_EXHAUST_PRESSURE,
    REG_SUPPLY_AIRFLOW_ACTUAL,
    REG_SUPPLY_AIRFLOW_SETPOINT,
    REG_EXHAUST_AIRFLOW_ACTUAL,
    REG_SUPPLY_FAN_SPEED,
    REG_EXHAUST_FAN_SPEED,
    REG_SUPPLY_FAN_TEMPERATURE,
    REG_EXHAUST_FAN_TEMPERATURE,
    REG_SUPPLY_FAN_HUMIDITY,
    REG_EXHAUST_FAN_HUMIDITY,
    REG_BYPASS_STATUS,
    REG_PREHEATER_STATUS,
    REG_PREHEATER_CAPACITY,
    REG_FROST_STATUS,
    REG_FROST_HEATER_POWER,
    REG_FROST_FAN_REDUCTION,
    REG_OUTSIDE_TEMP,
    REG_DWELLING_TEMP,
    REG_RHT_HUMIDITY,
    REG_FILTER_STATUS,
    REG_OPERATING_HOURS_HI,
    REG_FILTER_HOURS,
    REG_CO2_SENSOR1_VALUE,
    REG_CO2_SENSOR2_VALUE,
    REG_SYSTEM_ERROR_STATUS,
    REG_ACTIVE_INCIDENT,
    REG_FAN_INLET_STATUS,
    REG_FAN_EXHAUST_STATUS,
    # Holding registers
    REG_FLOW_PRESET_0,
    REG_BYPASS_MODE,
    REG_BYPASS_TEMP_DWELLING,
    REG_BYPASS_TEMP_OUTSIDE,
    REG_FILTER_WARNING_DAYS,
    # Remote control
    REG_MODBUS_CONTROL,
    REG_SWITCH_POSITION,
    REG_DESIRED_FLOW_RATE,
    REG_STANDBY,
    REG_FILTER_RESET,
    REG_APPLIANCE_RESET,
    # Maps
    ACTIVE_FUNCTION_MAP,
    VENTILATION_MODE_MAP,
    BYPASS_STATUS_MAP,
    BYPASS_MODE_MAP,
    FILTER_STATUS_MAP,
    SYSTEM_ERROR_MAP,
    FAN_STATUS_MAP,
    PREHEATER_STATUS_MAP,
    AIRFLOW_MODE_TO_SWITCH,
    SWITCH_TO_AIRFLOW_MODE,
)

_LOGGER = logging.getLogger(__name__)

# Minimum delay between Modbus operations (seconds).
# The Vigor devices can be slow to respond; rapid-fire requests may cause
# the device to drop frames or return errors.
MIN_REQUEST_DELAY = 0.15


class UbbinkModbusClient:
    """Async Modbus client for Ubbink Vigor devices."""

    def __init__(
        self,
        connection_type: str,
        slave_id: int = DEFAULT_SLAVE_ID,
        serial_port: str | None = None,
        baudrate: int = DEFAULT_BAUDRATE,
        parity: str = DEFAULT_PARITY,
        host: str | None = None,
        port: int = DEFAULT_TCP_PORT,
        bridge_type: str = BRIDGE_SER2NET,
    ) -> None:
        """Initialise the Modbus client."""
        self._connection_type = connection_type
        self._slave_id = slave_id
        self._serial_port = serial_port
        self._baudrate = baudrate
        self._parity = parity
        self._host = host
        self._port = port
        self._bridge_type = bridge_type
        self._client: AsyncModbusSerialClient | AsyncModbusTcpClient | None = None
        self._lock = asyncio.Lock()

    # ──────────── Connection ────────────

    async def connect(self) -> bool:
        """Open the Modbus connection."""
        try:
            if self._connection_type == CONN_SERIAL:
                stopbits = 1 if self._parity != "N" else 2
                self._client = AsyncModbusSerialClient(
                    port=self._serial_port,
                    baudrate=self._baudrate,
                    bytesize=8,
                    parity=self._parity,
                    stopbits=stopbits,
                    framer=FramerType.RTU,
                    timeout=3,
                    retries=2,
                )
            else:
                # ser2net tunnels raw serial bytes → RTU framing on TCP.
                # mbusd does protocol conversion → standard Modbus TCP (MBAP).
                if self._bridge_type == BRIDGE_MBUSD:
                    framer = FramerType.SOCKET
                else:
                    framer = FramerType.RTU
                self._client = AsyncModbusTcpClient(
                    host=self._host,
                    port=self._port,
                    framer=framer,
                    timeout=5,
                    retries=2,
                )
            connected = await self._client.connect()
            if connected:
                _LOGGER.info("Connected to Ubbink Vigor via %s", self._connection_type)
            return connected
        except Exception:
            _LOGGER.exception("Failed to connect to Ubbink Vigor")
            return False

    async def close(self) -> None:
        """Close the connection."""
        if self._client:
            self._client.close()

    @property
    def connected(self) -> bool:
        """Return True if connected."""
        return self._client is not None and self._client.connected

    # ──────────── Low-level helpers ────────────

    async def _read_input_registers(self, address: int, count: int = 1) -> list[int] | None:
        """Read input registers (FC 04)."""
        async with self._lock:
            await asyncio.sleep(MIN_REQUEST_DELAY)
            try:
                result = await self._client.read_input_registers(
                    address=address, count=count, slave=self._slave_id
                )
                if result.isError():
                    _LOGGER.warning("Error reading input register %s: %s", address, result)
                    return None
                return list(result.registers)
            except (ModbusException, asyncio.TimeoutError, ConnectionError) as exc:
                _LOGGER.warning("Modbus read input registers %s failed: %s", address, exc)
                return None

    async def _read_holding_registers(self, address: int, count: int = 1) -> list[int] | None:
        """Read holding registers (FC 03)."""
        async with self._lock:
            await asyncio.sleep(MIN_REQUEST_DELAY)
            try:
                result = await self._client.read_holding_registers(
                    address=address, count=count, slave=self._slave_id
                )
                if result.isError():
                    _LOGGER.warning("Error reading holding register %s: %s", address, result)
                    return None
                return list(result.registers)
            except (ModbusException, asyncio.TimeoutError, ConnectionError) as exc:
                _LOGGER.warning("Modbus read holding registers %s failed: %s", address, exc)
                return None

    async def _write_register(self, address: int, value: int) -> bool:
        """Write a single holding register (FC 06)."""
        async with self._lock:
            await asyncio.sleep(MIN_REQUEST_DELAY)
            try:
                result = await self._client.write_register(
                    address=address, value=value, slave=self._slave_id
                )
                if result.isError():
                    _LOGGER.error("Error writing register %s=%s: %s", address, value, result)
                    return False
                return True
            except (ModbusException, asyncio.TimeoutError, ConnectionError) as exc:
                _LOGGER.error("Modbus write register %s failed: %s", address, exc)
                return False

    # ──────────── Signed value helper ────────────

    @staticmethod
    def _to_signed(value: int) -> int:
        """Convert unsigned 16-bit to signed."""
        if value >= 0x8000:
            return value - 0x10000
        return value

    # ──────────── Read all data at once ────────────

    async def read_all_data(self) -> dict[str, Any] | None:
        """Read all relevant registers and return a parsed dict."""
        data: dict[str, Any] = {}

        # ── Input registers: batch read where possible ──

        # Batch 1: Registers 4020-4024 (active function, vent mode, pressures)
        regs = await self._read_input_registers(REG_ACTIVE_FUNCTION, 5)
        if regs is None:
            return None  # If we can't read basic data, bail out
        data["active_function"] = ACTIVE_FUNCTION_MAP.get(regs[0], f"Unknown ({regs[0]})")
        data["active_function_raw"] = regs[0]
        data["fan_control_type"] = regs[1]
        data["ventilation_mode"] = VENTILATION_MODE_MAP.get(regs[2], f"Unknown ({regs[2]})")
        data["ventilation_mode_raw"] = regs[2]
        data["supply_pressure"] = round(self._to_signed(regs[3]) / 10.0, 1)
        data["exhaust_pressure"] = round(self._to_signed(regs[4]) / 10.0, 1)

        # Batch 2: Registers 4030-4037 (supply fan block)
        regs = await self._read_input_registers(REG_FAN_INLET_STATUS, 8)
        if regs:
            data["fan_inlet_status"] = FAN_STATUS_MAP.get(regs[0], f"Unknown ({regs[0]})")
            data["supply_airflow_setpoint"] = regs[1]
            data["supply_airflow_actual"] = regs[2]
            data["supply_massflow"] = regs[3]
            data["supply_fan_speed"] = regs[4]
            # reg[5] is 4035 (anemometer), skip
            data["supply_fan_temperature"] = round(self._to_signed(regs[6]) / 10.0, 1)
            data["supply_fan_humidity"] = round(regs[7] / 10.0, 1) if regs[7] <= 1000 else None

        # Batch 3: Registers 4040-4047 (exhaust fan block)
        regs = await self._read_input_registers(REG_FAN_EXHAUST_STATUS, 8)
        if regs:
            data["fan_exhaust_status"] = FAN_STATUS_MAP.get(regs[0], f"Unknown ({regs[0]})")
            # 4041 = exhaust setpoint (not in doc explicitly)
            data["exhaust_airflow_actual"] = regs[2]
            # 4043 = exhaust massflow
            data["exhaust_fan_speed"] = regs[4]
            # reg[5] = 4045 exhaust anemometer
            data["exhaust_fan_temperature"] = round(self._to_signed(regs[6]) / 10.0, 1)
            data["exhaust_fan_humidity"] = round(regs[7] / 10.0, 1) if regs[7] <= 1000 else None

        # Batch 4: Bypass status (4050-4051)
        regs = await self._read_input_registers(REG_BYPASS_STATUS, 2)
        if regs:
            data["bypass_status"] = BYPASS_STATUS_MAP.get(regs[0], f"Unknown ({regs[0]})")
            data["bypass_status_raw"] = regs[0]
            data["bypass_step_position"] = regs[1]

        # Batch 5: Preheater (4060-4061)
        regs = await self._read_input_registers(REG_PREHEATER_STATUS, 2)
        if regs:
            data["preheater_status"] = PREHEATER_STATUS_MAP.get(regs[0], f"Unknown ({regs[0]})")
            data["preheater_capacity"] = regs[1]

        # Batch 6: Frost (4070-4072)
        regs = await self._read_input_registers(REG_FROST_STATUS, 3)
        if regs:
            data["frost_status_raw"] = regs[0]
            data["frost_heater_power"] = regs[1]
            data["frost_fan_reduction"] = regs[2]

        # Batch 7: Temperatures and humidity (4080-4083)
        regs = await self._read_input_registers(REG_OUTSIDE_TEMP - 1, 4)
        if regs:
            data["flow_switch_position"] = regs[0]
            data["outside_temperature"] = round(self._to_signed(regs[1]) / 10.0, 1)
            val = self._to_signed(regs[2])
            if val != 9999:
                data["dwelling_temperature"] = round(val / 10.0, 1)
            else:
                data["dwelling_temperature"] = None
            data["rht_humidity"] = round(regs[3] / 10.0, 1) if regs[3] <= 1000 else None

        # Filter status (4100)
        regs = await self._read_input_registers(REG_FILTER_STATUS, 1)
        if regs:
            data["filter_status"] = FILTER_STATUS_MAP.get(regs[0], f"Unknown ({regs[0]})")

        # Operating hours (4113-4115), two 16-bit words = 32-bit for hours
        regs = await self._read_input_registers(REG_OPERATING_HOURS_HI, 3)
        if regs:
            data["operating_hours"] = (regs[0] << 16) | regs[1]
            data["filter_hours"] = regs[2]

        # CO2 sensors (4200-4203)
        regs = await self._read_input_registers(REG_CO2_SENSOR1_VALUE - 1, 4)
        if regs:
            if regs[0] == 4:  # Running
                data["co2_sensor1"] = regs[1]
            else:
                data["co2_sensor1"] = None
            if regs[2] == 4:  # Running
                data["co2_sensor2"] = regs[3]
            else:
                data["co2_sensor2"] = None

        # Error status (4800-4801)
        regs = await self._read_input_registers(REG_SYSTEM_ERROR_STATUS, 2)
        if regs:
            data["system_error"] = SYSTEM_ERROR_MAP.get(regs[0], f"Unknown ({regs[0]})")
            data["system_error_raw"] = regs[0]
            data["active_incident"] = regs[1] if regs[1] != 0 else None

        # Serial number (4010-4012)
        regs = await self._read_input_registers(REG_SERIAL_0, 3)
        if regs:
            # BCD encoded digits
            serial = ""
            for reg in regs:
                serial += f"{(reg >> 12) & 0xF}{(reg >> 8) & 0xF}{(reg >> 4) & 0xF}{reg & 0xF}"
            data["serial_number"] = serial

        # ── Holding registers ──

        # Flow presets (6000-6003)
        regs = await self._read_holding_registers(REG_FLOW_PRESET_0, 4)
        if regs:
            data["flow_preset_holiday"] = regs[0]
            data["flow_preset_low"] = regs[1]
            data["flow_preset_normal"] = regs[2]
            data["flow_preset_high"] = regs[3]

        # Bypass mode (6100-6102)
        regs = await self._read_holding_registers(REG_BYPASS_MODE, 3)
        if regs:
            data["bypass_mode"] = BYPASS_MODE_MAP.get(regs[0], f"Unknown ({regs[0]})")
            data["bypass_mode_raw"] = regs[0]
            data["bypass_temp_dwelling"] = round(self._to_signed(regs[1]) / 10.0, 1)
            data["bypass_temp_outside"] = round(self._to_signed(regs[2]) / 10.0, 1)

        # Filter warning days (6120)
        regs = await self._read_holding_registers(REG_FILTER_WARNING_DAYS, 1)
        if regs:
            data["filter_warning_days"] = regs[0]

        # Remote control status (8000-8003)
        regs = await self._read_holding_registers(REG_MODBUS_CONTROL, 4)
        if regs:
            data["modbus_control"] = regs[0]
            data["switch_position"] = regs[1]
            data["desired_flow_rate"] = regs[2]
            data["standby_status"] = regs[3]

            # Determine current airflow mode
            if regs[0] == 0:
                data["airflow_mode"] = "wall_unit"
            elif regs[0] == 1:
                data["airflow_mode"] = SWITCH_TO_AIRFLOW_MODE.get(regs[1], "unknown")
            elif regs[0] == 2:
                data["airflow_mode"] = "custom"
            else:
                data["airflow_mode"] = "unknown"

        return data

    # ──────────── Write commands ────────────

    async def set_airflow_mode(self, mode: str) -> bool:
        """Set the airflow mode.

        mode: 'wall_unit', 'holiday', 'low', 'normal', 'high'
        """
        if mode == "wall_unit":
            return await self._write_register(REG_MODBUS_CONTROL, 0)

        if mode in AIRFLOW_MODE_TO_SWITCH:
            # Enable Modbus switch control
            ok = await self._write_register(REG_MODBUS_CONTROL, 1)
            if not ok:
                return False
            return await self._write_register(
                REG_SWITCH_POSITION, AIRFLOW_MODE_TO_SWITCH[mode]
            )

        _LOGGER.error("Invalid airflow mode: %s", mode)
        return False

    async def set_custom_flow_rate(self, rate: int) -> bool:
        """Set a custom flow rate in m³/h."""
        rate = max(0, min(rate, 400))
        # Enable Modbus flow rate control
        ok = await self._write_register(REG_MODBUS_CONTROL, 2)
        if not ok:
            return False
        return await self._write_register(REG_DESIRED_FLOW_RATE, rate)

    async def set_bypass_mode(self, mode: str) -> bool:
        """Set bypass mode: 'Automatic', 'Closed', 'Open'."""
        from .const import BYPASS_MODE_REVERSE
        if mode not in BYPASS_MODE_REVERSE:
            _LOGGER.error("Invalid bypass mode: %s", mode)
            return False
        return await self._write_register(REG_BYPASS_MODE, BYPASS_MODE_REVERSE[mode])

    async def reset_filter(self) -> bool:
        """Reset the filter warning."""
        return await self._write_register(REG_FILTER_RESET, 1)

    async def reset_appliance(self) -> bool:
        """Reset the appliance."""
        return await self._write_register(REG_APPLIANCE_RESET, 1)

    async def set_standby(self, standby: bool) -> bool:
        """Set standby mode (True = standby, False = normal)."""
        return await self._write_register(REG_STANDBY, 1 if standby else 2)

    async def set_bypass_temp_dwelling(self, temp: float) -> bool:
        """Set bypass dwelling temperature threshold (°C)."""
        value = int(temp * 10)
        value = max(150, min(350, value))
        return await self._write_register(REG_BYPASS_TEMP_DWELLING, value)

    async def set_bypass_temp_outside(self, temp: float) -> bool:
        """Set bypass outside temperature threshold (°C)."""
        value = int(temp * 10)
        value = max(70, min(150, value))
        return await self._write_register(REG_BYPASS_TEMP_OUTSIDE, value)

    # ──────────── Test connection ────────────

    async def test_connection(self) -> bool:
        """Test by reading a register."""
        regs = await self._read_input_registers(REG_ACTIVE_FUNCTION, 1)
        return regs is not None
