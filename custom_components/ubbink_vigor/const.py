"""Constants for the Ubbink Ubiflux Vigor integration."""
from __future__ import annotations

DOMAIN = "ubbink_vigor"
MANUFACTURER = "Ubbink / Brink"

# Config keys
CONF_CONNECTION_TYPE = "connection_type"
CONF_SERIAL_PORT = "serial_port"
CONF_SERIAL_BAUDRATE = "serial_baudrate"
CONF_SERIAL_PARITY = "serial_parity"
CONF_MODBUS_HOST = "modbus_host"
CONF_MODBUS_PORT = "modbus_port"
CONF_SLAVE_ID = "slave_id"
CONF_TCP_BRIDGE_TYPE = "tcp_bridge_type"

# Connection types
CONN_SERIAL = "serial"
CONN_TCP = "tcp"

# TCP bridge types — determines the Modbus framing on the TCP link.
# ser2net: raw serial tunnel, frames stay RTU-encoded.
# mbusd:   protocol-converting gateway, speaks Modbus TCP (MBAP header).
BRIDGE_SER2NET = "ser2net"
BRIDGE_MBUSD = "mbusd"

# Defaults
DEFAULT_SLAVE_ID = 20
DEFAULT_BAUDRATE = 19200
DEFAULT_PARITY = "E"
DEFAULT_TCP_PORT = 502
DEFAULT_SCAN_INTERVAL = 30

# Modbus register offsets - documentation uses absolute numbers.
# pymodbus uses 0-based protocol addresses, but these devices use the
# register numbers from the docs directly.

# ──────────────── Input Registers (FC 0x04) ────────────────
# Software / hardware info
REG_SW_VERSION_TYPE = 4000
REG_SW_VERSION_MINOR = 4001
REG_APPLIANCE_TYPE = 4004

# Serial number (BCD)
REG_SERIAL_0 = 4010
REG_SERIAL_1 = 4011
REG_SERIAL_2 = 4012

# Active function
REG_ACTIVE_FUNCTION = 4020
REG_FAN_CONTROL_TYPE = 4021
REG_VENTILATION_MODE = 4022
REG_SUPPLY_PRESSURE = 4023
REG_EXHAUST_PRESSURE = 4024

# Supply fan
REG_FAN_INLET_STATUS = 4030
REG_SUPPLY_AIRFLOW_SETPOINT = 4031
REG_SUPPLY_AIRFLOW_ACTUAL = 4032
REG_SUPPLY_MASSFLOW = 4033
REG_SUPPLY_FAN_SPEED = 4034
REG_SUPPLY_FAN_TEMPERATURE = 4036
REG_SUPPLY_FAN_HUMIDITY = 4037

# Exhaust fan
REG_FAN_EXHAUST_STATUS = 4040
REG_EXHAUST_AIRFLOW_ACTUAL = 4042
REG_EXHAUST_FAN_SPEED = 4044
REG_EXHAUST_FAN_TEMPERATURE = 4046
REG_EXHAUST_FAN_HUMIDITY = 4047

# Bypass
REG_BYPASS_STATUS = 4050
REG_BYPASS_STEP_POSITION = 4051

# Pre-heater
REG_PREHEATER_STATUS = 4060
REG_PREHEATER_CAPACITY = 4061

# Frost
REG_FROST_STATUS = 4070
REG_FROST_HEATER_POWER = 4071
REG_FROST_FAN_REDUCTION = 4072

# Misc sensors
REG_FLOW_SWITCH_POSITION = 4080
REG_OUTSIDE_TEMP = 4081
REG_DWELLING_TEMP = 4082
REG_RHT_HUMIDITY = 4083

# Filter / status
REG_FILTER_STATUS = 4100
REG_EBUS_POWER = 4101

# Time / operating hours
REG_OPERATING_HOURS_HI = 4113
REG_OPERATING_HOURS_LO = 4114
REG_FILTER_HOURS = 4115

# CO2 sensors
REG_CO2_SENSOR1_STATUS = 4200
REG_CO2_SENSOR1_VALUE = 4201
REG_CO2_SENSOR2_STATUS = 4202
REG_CO2_SENSOR2_VALUE = 4203

# Error status
REG_SYSTEM_ERROR_STATUS = 4800
REG_ACTIVE_INCIDENT = 4801

# ──────────────── Holding Registers (FC 0x03 / 0x06) ────────────────
# Flow presets
REG_FLOW_PRESET_0 = 6000  # Holiday
REG_FLOW_PRESET_1 = 6001  # Low
REG_FLOW_PRESET_2 = 6002  # Normal
REG_FLOW_PRESET_3 = 6003  # High

# Flow type
REG_FLOW_TYPE = 6030  # 0=PWM, 1=constant flow, 2=constant massflow

# Imbalance
REG_IMBALANCE_ALLOWED = 6033
REG_IMBALANCE_VALUE = 6034

# Bypass control
REG_BYPASS_MODE = 6100  # 0=Auto, 1=Closed, 2=Open
REG_BYPASS_TEMP_DWELLING = 6101  # tenths °C
REG_BYPASS_TEMP_OUTSIDE = 6102  # tenths °C
REG_BYPASS_TEMP_HYSTERESIS = 6103
REG_BYPASS_BOOST = 6104
REG_BYPASS_BOOST_SWITCH = 6105

# Frost control
REG_FROST_CONTROL_TEMP = 6110
REG_FROST_MIN_INLET_TEMP = 6111

# Filter
REG_FILTER_WARNING_DAYS = 6120

# External heater
REG_EXTERNAL_HEATER_MODE = 6130
REG_POSTHEATER_SETPOINT = 6131

# RHT / CO2
REG_RHT_SENSOR_MODE = 6140
REG_CO2_SENSOR_MODE = 6150

# ──────────────── Remote Control Registers (FC 0x03 / 0x06) ──────────
REG_MODBUS_CONTROL = 8000  # 0=off, 1=switch, 2=flow rate
REG_SWITCH_POSITION = 8001  # 0=holiday, 1=low, 2=normal, 3=high
REG_DESIRED_FLOW_RATE = 8002  # m³/h
REG_STANDBY = 8003  # 1=standby, 2=normal
REG_FILTER_RESET = 8010  # 1=reset
REG_APPLIANCE_RESET = 8011  # 1=reset

# ──────────────── Lookup tables ────────────────

ACTIVE_FUNCTION_MAP = {
    0: "Standby",
    1: "Bootloader",
    4: "Manual",
    5: "Holiday",
    6: "Night Ventilation",
    7: "Party",
    8: "Bypass Boost",
    9: "Normal Boost",
    10: "Auto CO2",
    11: "Auto eBus",
    12: "Auto Modbus",
    13: "Auto LAN/WLAN Portal",
    14: "Auto LAN/WLAN Local",
}

VENTILATION_MODE_MAP = {
    0: "Holiday",
    1: "Low",
    2: "Normal",
    3: "High",
    4: "Auto",
}

BYPASS_STATUS_MAP = {
    0: "Initializing",
    1: "Opening",
    2: "Closing",
    3: "Open",
    4: "Closed",
}

BYPASS_MODE_MAP = {
    0: "Automatic",
    1: "Closed",
    2: "Open",
}

BYPASS_MODE_REVERSE = {v: k for k, v in BYPASS_MODE_MAP.items()}

FILTER_STATUS_MAP = {
    0: "Clean",
    1: "Dirty",
}

SYSTEM_ERROR_MAP = {
    0: "No Error",
    1: "Warning",
    2: "Non-blocking Error",
    3: "Blocking Error",
}

FAN_STATUS_MAP = {
    2: "No Communication",
    3: "Idle",
    4: "Running",
    5: "Blocked",
    6: "Fan Error",
}

PREHEATER_STATUS_MAP = {
    0: "Initializing",
    1: "Inactive",
    2: "Active",
    3: "Test Mode",
}

AIRFLOW_MODE_OPTIONS = ["wall_unit", "holiday", "low", "normal", "high"]
BYPASS_MODE_OPTIONS = ["Automatic", "Closed", "Open"]

# Switch position mapping for remote control register 8001
AIRFLOW_MODE_TO_SWITCH = {
    "holiday": 0,
    "low": 1,
    "normal": 2,
    "high": 3,
}

SWITCH_TO_AIRFLOW_MODE = {v: k for k, v in AIRFLOW_MODE_TO_SWITCH.items()}

PLATFORMS: list[str] = ["sensor", "select", "number", "button"]
