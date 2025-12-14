# ED1 Citilab Board - Home Assistant Integration

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![ESPHome](https://img.shields.io/badge/ESPHome-2024.x-brightgreen.svg)](https://esphome.io)
[![ESP32](https://img.shields.io/badge/ESP32-supported-blue.svg)](https://www.espressif.com/en/products/socs/esp32)

ESPHome configuration for integrating the [ED1 Citilab](https://citilab.eu) ESP32 educational board with Home Assistant.

![ED1 Board](docs/images/ed1-board.png)

<p align="center">
  <img src="docs/images/ed1-front-angle.png" width="45%" alt="ED1 Front View">
  <img src="docs/images/ed1-back-angle.png" width="45%" alt="ED1 Back View">
</p>

## Features

### Built-in Hardware
- **1.44" TFT Display** (ST7735) - Shows device status, IP, temperature
- **6 Capacitive Touch Buttons** - Exposed as binary sensors
- **Light Sensor** - Ambient light percentage
- **Buzzer** - PWM audio output
- **IR Receiver** (38kHz) - Remote control support
- **WiFi Signal & Uptime Sensors**
- **CPU Temperature Monitoring**
- **Bluetooth Proxy** - Extends Home Assistant BLE range

### Expansion Support (External Peripherals)
- **LED Matrix** (WS2812) - GPIO12 output for LED strips (e.g., 32x8 = 256 LEDs)
- **Stepper Motors** (2x 28BYJ-48) - Via MCP23009 I/O expander and ULN2004A drivers

### Planned
- Accelerometer (MXC6655XA on Rev 2.3, LIS3DH on Rev 1.0)

## Prerequisites

- [Home Assistant](https://www.home-assistant.io/) with [ESPHome Add-on](https://esphome.io/guides/getting_started_hassio.html)
- ED1 Citilab Board (Rev 1.0 or Rev 2.3)
- USB-C cable
- [CP210x USB Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) (required for USB communication)

> **Note**: Core packages work on both revisions. The stepper motor package is designed for Rev 2.3's MCP23009. See [Hardware Reference](docs/HARDWARE.md#hardware-revisions) for revision differences.

## Quick Start

1. **Clone this repository**
   ```bash
   git clone https://github.com/glifocat/ed1-hoas.git
   ```

2. **Configure secrets**
   ```bash
   cp secrets.sample.yaml secrets.yaml
   # Edit secrets.yaml with your credentials
   ```

3. **Copy to ESPHome**

   Choose a sample configuration:
   - `ed1-message.sample.yaml` - Message display with chat log (recommended)
   - `ed1-mqtt.sample.yaml` - Dashboard with MQTT messaging
   - `ed1-status.sample.yaml` - Status display (WiFi, sensors, uptime, optional IR)
   - `ed1-smartir-detector.yaml` - **Tool:** Identifies IR remote codes for [SmartIR](https://github.com/smartHomeHub/SmartIR) integration.

   Copy your chosen sample, `secrets.yaml`, the `fonts/` folder, and the `packages/` folder to your ESPHome config directory.

4. **Install on device**

   In Home Assistant ESPHome add-on:
   - Click "+ NEW DEVICE"
   - Select "Pick file" and choose the YAML
   - Connect ED1 via USB and flash

5. **Add to Home Assistant**

   The device will be auto-discovered. Accept the integration to add all entities.

## File Structure

```
ed1-hoas/
├── ed1-message.sample.yaml        # Message display with chat log (recommended)
├── ed1-mqtt.sample.yaml           # Dashboard with MQTT messaging
├── ed1-status.sample.yaml         # Status display (WiFi, sensors, uptime, optional IR)
├── ed1-smartir-detector.yaml      # IR analysis tool (SmartIR compatible)
├── secrets.sample.yaml            # Template for secrets
├── secrets.yaml                   # Your credentials (git-ignored)
├── packages/                      # Modular ESPHome components
│   ├── core.yaml                  # ESP32, logger, API, OTA, WiFi
│   ├── hardware.yaml              # SPI and I2C buses
│   ├── display.yaml               # TFT ST7735 display
│   ├── display-colors.yaml        # Color palette definitions
│   ├── display-layout.yaml        # Screen layout constants
│   ├── fonts.yaml                 # Fonts + Material Symbols icons
│   ├── buzzer.yaml                # PWM output + RTTTL melodies
│   ├── buttons.yaml               # 6 capacitive touch buttons
│   ├── sensors.yaml               # WiFi, uptime, temp, light sensors
│   ├── bluetooth.yaml             # BLE tracker + proxy
│   ├── ir-receiver.yaml           # 38kHz IR receiver
│   ├── led-matrix.yaml            # 32x8 WS2812B LED matrix
│   ├── mqtt.yaml                  # MQTT broker connectivity (optional)
│   └── stepper.yaml               # 28BYJ-48 stepper motors via MCP23009
├── fonts/
│   └── pixelmix/                  # Pixelmix font (CC BY-NC-ND 3.0)
├── docs/
│   ├── HARDWARE.md                # Hardware reference
│   ├── PINOUT.md                  # GPIO mapping
│   ├── ESPHOME.md                 # Configuration guide
│   ├── HOME-ASSISTANT.md          # Integration guide
│   ├── images/                    # Board images (CC BY-SA 4.0)
│   └── datasheets/                # Component PDFs
├── CONTRIBUTING.md
└── LICENSE
```

## Documentation

- [Hardware Reference](docs/HARDWARE.md) - Board specifications and components
- [GPIO Pinout](docs/PINOUT.md) - Pin mapping quick reference
- [ESPHome Configuration](docs/ESPHOME.md) - Configuration explained
- [Home Assistant Integration](docs/HOME-ASSISTANT.md) - Dashboards & automations

## Home Assistant Entities

| Entity | Type | Description |
|--------|------|-------------|
| `light.ed1_led_matrix` | Light | LED matrix with RGB control |
| `text.ed1_matrix_text` | Text | Send text to LED matrix |
| `binary_sensor.ed1_button_*` | Binary Sensor | Touch buttons (up/down/left/right/ok/x) |
| `sensor.ed1_light_level` | Sensor | Light level (%) |
| `sensor.ed1_wifi_signal` | Sensor | WiFi signal strength |
| `sensor.ed1_cpu_temperature` | Sensor | CPU temperature |
| `sensor.ed1_uptime` | Sensor | Device uptime |
| `switch.ed1_buzzer` | Switch | Buzzer on/off control |
| `number.ed1_motor_*_steps` | Number | Stepper motor control (steps) |
| `button.ed1_motor_*_cw/ccw` | Button | Stepper motor rotation buttons |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.

## Credits

- **Created & Maintained by**: [glifocat](https://github.com/glifocat)
- **Original Hardware Documentation & Advice**: [vcasado](https://github.com/vcasado)
- **ED1 Board**: [Citilab Edutec](https://citilab.eu)
- **Board Images**: [Citilab Market](https://market.citilab.eu/es/producte/placa-ed1/) (CC BY-SA 4.0)
- **ESPHome**: [esphome.io](https://esphome.io)
- **Pixelmix Font**: [Andrew Tyler](https://www.andrewtyler.net) (CC BY-NC-ND 3.0)

## Links

- [ESPHome Documentation](https://esphome.io/)
- [Home Assistant](https://www.home-assistant.io/)
- [Citilab](https://citilab.eu)
