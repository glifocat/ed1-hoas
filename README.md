# ED1 Citilab Board - Home Assistant Integration

ESPHome configuration for integrating the [ED1 Citilab](https://citilab.eu) ESP32 educational board with Home Assistant.

![ED1 Board Front](docs/images/ed1-front.png)

## Features

### Implemented
- **1.44" TFT Display** (ST7735) - Shows device status, IP, temperature
- **32x8 LED Matrix** (WS2812) - Controllable from Home Assistant
- **6 Capacitive Touch Buttons** - Exposed as binary sensors
- **Light Sensor** - Ambient light percentage
- **Bluetooth Proxy** - Extends Home Assistant BLE range
- **WiFi Signal & Uptime Sensors**
- **CPU Temperature Monitoring**

### Planned (Hardware Available)
- Accelerometer (MXC6655XA)
- IR Receiver (38kHz)
- Buzzer/Speaker
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
   git clone https://github.com/YOUR_USERNAME/ed1-hoas.git
   ```

2. **Configure secrets**
   ```bash
   cp secrets.sample.yaml secrets.yaml
   # Edit secrets.yaml with your credentials
   ```

3. **Copy to ESPHome**

   Copy `ed1-rev23-a.yaml` and `secrets.yaml` to your ESPHome configuration directory.

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
├── ed1-rev23-a.yaml      # Main ESPHome configuration
├── secrets.yaml          # Your credentials (git-ignored)
├── secrets.sample.yaml   # Template for secrets
├── fonts/
│   └── pixelmix/         # Pixelmix font (CC BY-NC-ND 3.0)
├── docs/
│   ├── HARDWARE.md       # Hardware reference
│   ├── PINOUT.md         # GPIO mapping
│   ├── ESPHOME.md        # Configuration guide
│   ├── HOME-ASSISTANT.md # Integration guide
│   ├── images/           # Board images
│   └── datasheets/       # Component PDFs
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
| `light.ed1_luz_matriz` | Light | LED matrix with RGB control |
| `text.escribir_en_matriz` | Text | Send text to LED matrix |
| `binary_sensor.ed1_boton_*` | Binary Sensor | Touch buttons (6x) |
| `sensor.ed1_luz` | Sensor | Light level (%) |
| `sensor.ed1_senal_wifi` | Sensor | WiFi signal strength |
| `sensor.ed1_temperatura_cpu` | Sensor | CPU temperature |
| `sensor.ed1_tiempo_encendido` | Sensor | Device uptime |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.

## Credits

- **Created & Maintained by**: [glifocat](https://github.com/glifocat)
- **ED1 Board**: [Citilab Edutec](https://citilab.eu)
- **ESPHome**: [esphome.io](https://esphome.io)
- **Pixelmix Font**: [Andrew Tyler](https://www.andrewtyler.net) (CC BY-NC-ND 3.0)

## Links

- [ESPHome Documentation](https://esphome.io/)
- [Home Assistant](https://www.home-assistant.io/)
- [Citilab](https://citilab.eu)
