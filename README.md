# ED1 Citilab Board - Home Assistant Integration

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![ESPHome](https://img.shields.io/badge/ESPHome-2024.x-brightgreen.svg)](https://esphome.io)
[![ESP32](https://img.shields.io/badge/ESP32-supported-blue.svg)](https://www.espressif.com/en/products/socs/esp32)

ESPHome configuration for integrating the [ED1 Citilab](https://citilab.eu) ESP32 educational board with Home Assistant.

![ED1 Board Front](docs/images/ed1-front.png)

## Features

### Implemented
- **1.44" TFT Display** (ST7735) - Shows device status, IP, temperature
- **32x8 LED Matrix** (WS2812) - Controllable from Home Assistant
- **6 Capacitive Touch Buttons** - Exposed as binary sensors
- **Light Sensor** - Ambient light percentage
- **Buzzer** - PWM audio output
- **IR Receiver** (38kHz) - Remote control support
- **Bluetooth Proxy** - Extends Home Assistant BLE range
- **WiFi Signal & Uptime Sensors**
- **CPU Temperature Monitoring**

### Planned (Hardware Available)
- Accelerometer (MXC6655XA)
- Stepper Motor Control (2x 28BYJ-48)
- I/O Expander (MCP23009)

## Prerequisites

- [Home Assistant](https://www.home-assistant.io/) with [ESPHome Add-on](https://esphome.io/guides/getting_started_hassio.html)
- ED1 Citilab Board (Rev 2.3)
- USB-C cable
- [CP210x USB Driver](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers) (required for USB communication)

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
   - `ed1-status.sample.yaml` - Status display showing WiFi, sensors, uptime
   - `ed1-rev23-a.sample.yaml` - Status display with IR receiver
   - `ed1-full-features.sample.yaml` - All features (TFT + LED matrix + IR)

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
├── ed1-status.sample.yaml         # Status display (WiFi, sensors, uptime)
├── ed1-rev23-a.sample.yaml        # Status display with IR receiver
├── ed1-full-features.sample.yaml  # All features (TFT + LED matrix + IR)
├── secrets.sample.yaml            # Template for secrets
├── secrets.yaml                   # Your credentials (git-ignored)
├── packages/                      # Modular ESPHome components
│   ├── core.yaml                  # ESP32, logger, API, OTA, WiFi
│   ├── hardware.yaml              # SPI and I2C buses
│   ├── display.yaml               # TFT ST7735 display
│   ├── fonts.yaml                 # Fonts + Material Symbols icons
│   ├── buzzer.yaml                # PWM output + RTTTL melodies
│   ├── buttons.yaml               # 6 capacitive touch buttons
│   ├── sensors.yaml               # WiFi, uptime, temp, light sensors
│   ├── bluetooth.yaml             # BLE tracker + proxy
│   ├── ir-receiver.yaml           # 38kHz IR receiver
│   ├── led-matrix.yaml            # 32x8 WS2812B LED matrix
│   └── mqtt.yaml                  # MQTT broker connectivity (optional)
├── fonts/
│   └── pixelmix/                  # Pixelmix font (CC BY-NC-ND 3.0)
├── docs/
│   ├── HARDWARE.md                # Hardware reference
│   ├── PINOUT.md                  # GPIO mapping
│   ├── ESPHOME.md                 # Configuration guide
│   ├── HOME-ASSISTANT.md          # Integration guide
│   ├── images/                    # Board images
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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.

## Credits

- **Created & Maintained by**: [glifocat](https://github.com/glifocat)
- **Original Hardware Documentation & Advice**: [vcasado](https://github.com/vcasado)
- **ED1 Board**: [Citilab Edutec](https://citilab.eu)
- **ESPHome**: [esphome.io](https://esphome.io)
- **Pixelmix Font**: [Andrew Tyler](https://www.andrewtyler.net) (CC BY-NC-ND 3.0)

## Links

- [ESPHome Documentation](https://esphome.io/)
- [Home Assistant](https://www.home-assistant.io/)
- [Citilab](https://citilab.eu)
