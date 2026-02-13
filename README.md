# Ubbink Ubiflux Vigor – Home Assistant HACS Integration

A native Home Assistant integration for **Ubbink Ubiflux Vigor W325/W400** ventilation units (also sold as Brink Flair) via Modbus RTU. Communicates directly — no Docker middleware required.

## Features

| Category | Entities |
|---|---|
| **Sensors** | Supply/exhaust airflow (m³/h), pressures (Pa), temperatures (°C), fan speeds (RPM), humidity (%), CO₂ (ppm), filter status, operating hours, error codes |
| **Airflow Mode** (select) | `wall_unit` · `holiday` · `low` · `normal` · `high` |
| **Custom Flow Rate** (number) | 50 – 400 m³/h slider |
| **Bypass Mode** (select) | `Automatic` · `Closed` · `Open` |
| **Bypass Temp Thresholds** (number) | Dwelling (15–35 °C), Outside (7–15 °C) |
| **Buttons** | Reset filter warning · Appliance reset |

### Bypass Control

The integration writes to **holding register 6100** to control the bypass valve:

| Value | Mode | Effect |
|---|---|---|
| 0 | Automatic | Bypass opens/closes based on temperature thresholds |
| 1 | Closed | Force bypass closed → heat recovery active |
| 2 | Open | Force bypass open → free cooling / summer bypass |

---

## Hardware Setup

### What you need

- **Ubbink Ubiflux Vigor W325 or W400** (or Brink equivalent with UWA2-B PCB)
- **USB-to-RS485 adapter** (CH340 or FTDI chipset)
- **Raspberry Pi Zero W** (or any Linux device) as a Modbus TCP bridge
- Two wires (twisted pair recommended)

### Wiring

Connect the USB-RS485 dongle to the red Modbus connector **X15** on the UWA2-B PCB:

| Dongle Pin | Vigor X15 Pin |
|---|---|
| A | Pin 2 (RS485_A) |
| B | Pin 3 (RS485_B) |
| GND (optional) | Pin 1 (RS485 ground) |

> If you have the **Plus** version with UWA2-E board, use connector **X06** instead.

---

## Raspberry Pi Zero W – Bridge Setup

The Pi Zero acts as a Modbus TCP bridge, exposing the serial port over WiFi so Home Assistant (on a separate Pi or any machine) can reach it.

> **Important**: The integration asks you to choose between **ser2net** and **mbusd** during setup. This controls the Modbus *framing* used on the TCP link. Selecting the wrong one will cause every response to fail silently.
>
> | Bridge | Framing on TCP | What it does |
> |---|---|---|
> | **ser2net** | RTU (raw serial bytes tunnelled) | Simple byte pipe — no protocol awareness |
> | **mbusd** | Modbus TCP (MBAP header) | Converts between RTU on serial ↔ Modbus TCP on network |

### Option A: ser2net (recommended for simplicity)

```bash
sudo apt update && sudo apt install -y ser2net

# Create config
sudo tee /etc/ser2net.yaml << 'EOF'
connection: &vigor
    accepter: tcp,502
    connector: serialdev,/dev/ttyUSB0,19200n81,local
    options:
      kickolduser: true
EOF

sudo systemctl enable ser2net
sudo systemctl restart ser2net
```

In the HA integration setup, choose **ser2net** as bridge type.

### Option B: mbusd (protocol-converting gateway)

```bash
sudo apt update && sudo apt install -y git build-essential cmake
git clone https://github.com/3cky/mbusd.git
cd mbusd && mkdir build && cd build
cmake -DCMAKE_INSTALL_PREFIX=/usr ..
make && sudo make install

# Run mbusd  (-R enables RTU-to-TCP conversion)
sudo mbusd -d -L /var/log/mbusd.log -p /dev/ttyUSB0 -s 19200 -P 502 -R
```

In the HA integration setup, choose **mbusd** as bridge type.

### Verify the bridge

From your Home Assistant machine:

```bash
# Should connect without error
nc -zv <pi-zero-ip> 502
```

---

## Installation

### Via HACS

1. Open **HACS** → **Integrations** → ⋮ → **Custom repositories**
2. Add repository URL: `https://github.com/YOUR-USER/ha-ubbink-vigor`
3. Type: **Integration** → **Add**
4. Search "Ubbink" in HACS → **Download**
5. Restart Home Assistant

### Manual

Copy `custom_components/ubbink_vigor/` to your Home Assistant `config/custom_components/` directory and restart.

---

## Configuration

This integration is designed for setups where the USB-RS485 dongle and Home Assistant run on **separate devices** connected over the local network. A typical setup:

```
┌──────────────────┐         WiFi / LAN         ┌──────────────────────┐
│  Pi Zero W       │◄──────────────────────────►│  Raspberry Pi (HA)   │
│  USB-RS485 dongle│   TCP port 502              │  Home Assistant OS   │
│  ser2net / mbusd │                             │  Ubbink Vigor integ. │
└────────┬─────────┘                             └──────────────────────┘
         │ RS485 (2-wire)
┌────────┴─────────┐
│  Ubiflux Vigor   │
│  W400 (X15 port) │
└──────────────────┘
```

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **Ubbink Ubiflux Vigor**
3. Choose connection type:
   - **TCP** — enter the IP of your Pi Zero bridge, port (default 502), and select your bridge software (**ser2net** or **mbusd**)
   - **Serial** — only if Home Assistant has direct USB access to the dongle (same machine)
4. Set the Modbus slave address (default: **20**, configurable on the wall unit at step 14.2)
5. The integration tests the connection before saving — if it fails, double-check the bridge type selection, IP, and that the bridge service is running

---

## Entities Overview

### Sensors (read-only)

| Entity | Description | Unit |
|---|---|---|
| Supply Airflow | Measured supply air volume | m³/h |
| Exhaust Airflow | Measured exhaust air volume | m³/h |
| Supply / Exhaust Pressure | Duct pressures | Pa |
| Supply / Exhaust Temperature | Air temperatures in fan housing | °C |
| Outside Temperature | NTC1 sensor reading | °C |
| Dwelling Temperature | NTC2 sensor reading (if connected) | °C |
| Supply / Exhaust Fan Speed | Fan RPM | rpm |
| Supply / Exhaust Humidity | RH sensors in fan housing | % |
| CO₂ Sensor 1 / 2 | External CO₂ sensors (if connected) | ppm |
| Filter Status | Clean / Dirty | — |
| Filter Hours | Hours since last filter reset | h |
| Bypass Status | Initializing / Opening / Closing / Open / Closed | — |
| System Error | No Error / Warning / Non-blocking / Blocking | — |
| Active Error Code | Three-digit error code (0 = none) | — |

### Controls

| Entity | Type | Description |
|---|---|---|
| Airflow Mode | Select | Switch between wall unit / holiday / low / normal / high |
| Custom Flow Rate | Number | Set exact airflow in m³/h (50-400, step 5) |
| Bypass Mode | Select | Automatic / force Closed / force Open |
| Bypass Dwelling Temp Threshold | Number | Temperature above which bypass may open (15-35°C) |
| Bypass Outside Temp Threshold | Number | Outdoor temp above which bypass may open (7-15°C) |
| Reset Filter Warning | Button | Clears filter dirty indicator |
| Appliance Reset | Button | Restarts the unit (disabled by default) |

---

## Important Notes

- **After power loss**, Modbus registers 8000-8011 are reset. The integration will re-send the airflow mode on next update cycle.
- **Wall unit manual mode** overrides Modbus commands. Ensure the wall unit is in clock/auto program mode.
- A **minimum 5-second delay** between Modbus writes is recommended by the device. The integration enforces 150ms between frames.
- The default Modbus settings are: 19200 baud, 8 data bits, Even parity, 1 stop bit. If your unit uses No parity, set 2 stop bits.

---

## Example Automations

### Open bypass on warm summer evenings

```yaml
automation:
  - alias: "Summer bypass cooling"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ubbink_vigor_outside_temperature
        above: 18
    condition:
      - condition: numeric_state
        entity_id: sensor.ubbink_vigor_dwelling_temperature
        above: 24
    action:
      - service: select.select_option
        target:
          entity_id: select.ubbink_vigor_bypass_mode
        data:
          option: "Open"
      - service: select.select_option
        target:
          entity_id: select.ubbink_vigor_airflow_mode
        data:
          option: "high"
```

### CO₂-based ventilation

```yaml
automation:
  - alias: "CO2 based ventilation"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ubbink_vigor_co2_sensor_1
        above: 1000
    action:
      - service: select.select_option
        target:
          entity_id: select.ubbink_vigor_airflow_mode
        data:
          option: "high"

  - alias: "CO2 normalised"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ubbink_vigor_co2_sensor_1
        below: 700
    action:
      - service: select.select_option
        target:
          entity_id: select.ubbink_vigor_airflow_mode
        data:
          option: "normal"
```

---

## Modbus Register Reference

See the full register map in the [Brink Modbus UWA2-B/UWA2-E documentation (614882-H)](https://www.brinkclimatesystems.nl).

| Range | Type | Function | Access |
|---|---|---|---|
| 4000–4801 | Input registers | Sensor data, status | Read (FC 04) |
| 6000–7993 | Holding registers | Configuration parameters | Read/Write (FC 03/06) |
| 8000–8011 | Holding registers | Remote control commands | Read/Write (FC 03/06) |

---

## License

GNU GPL3.0
