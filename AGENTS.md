# AGENTS.md

Guidance for AI coding agents working in this repository. (Human contributors:
see [CONTRIBUTING.md](CONTRIBUTING.md).)

## Project Overview

ESPHome configuration for integrating the ED1 Citilab ESP32 educational board
with Home Assistant. The ED1 is a Spanish educational board with a TFT display,
touch buttons, buzzer, IR, light sensor, and optional LED matrix / stepper
accessories.

## Commands

```bash
# Validate ESPHome configuration
esphome config ed1-message.sample.yaml

# Compile without uploading
esphome compile ed1-message.sample.yaml

# Compile and upload via USB
esphome run ed1-message.sample.yaml

# Compile and upload OTA (over-the-air)
esphome run ed1-message.sample.yaml --device <ip-address>

# Monitor device logs
esphome logs ed1-message.sample.yaml
```

CI pins a specific ESPHome version (`ESPHOME_VERSION` in
`.github/workflows/esphome-check.yml`) — validate against that version when
possible.

## Architecture

This is an ESPHome project using a **modular package system**. Reusable
components live in `packages/` and are included via ESPHome's `!include`
directive. The packages are also consumable as **remote packages**
(`github://glifocat/ed1-hoas/packages/<file>.yaml@<tag>`) — see the README's
"Use as Remote Packages" section.

### Rules that follow from remote-package support

- **Never use `!secret` inside `packages/`.** ESPHome forbids secret lookups
  in remote packages. Credentials enter packages via substitutions
  (`${wifi_ssid}`, `${api_encryption_key}`, ...) that consuming configs map
  from their own `secrets.yaml`.
- **Local file paths in packages resolve against the CONSUMER's config dir,
  not this repo.** That's why `fonts.yaml` exposes a `pixelmix_font`
  substitution (local path by default, raw GitHub URL for remote consumers).
  Apply the same pattern to any new package that references repo files.
- **Renaming a substitution or component ID is a breaking change** for remote
  consumers. Releases follow SemVer; such renames require a major version.

### Sample Configurations

- `ed1-message.sample.yaml` - Message display with chat log (HA API)
- `ed1-scene-deck.sample.yaml` - 6-button HA action deck; companion blueprint in `ha/blueprints/`
- `ed1-mqtt.sample.yaml` - Dashboard with MQTT messaging
- `ed1-status.sample.yaml` - Status display showing WiFi, sensors, uptime (optional IR)
- `ed1-smartir-detector.yaml` - IR code detector for SmartIR (Rev 2.3)
- `ed1-smartir-detector-rev1.yaml` - IR code detector for SmartIR (Rev 1.0)
- `ed1-robot-demo.yaml` - Interactive stepper motor robot demo
- `ed1-stepper-test.yaml` - Stepper motor testing and calibration
- `ed1-gpio-test.yaml` - MCP23009 GPIO diagnostic tool
- `ed1-hardware-test.yaml` - On-device hardware self-test firmware
- `ed1-wokwi.yaml` - Virtual ED1 board for the Wokwi simulator (no secrets, GPIO buttons)

When adding a new config, add it to the CI compile matrix in
`.github/workflows/esphome-check.yml` (validation picks up `ed1-*.yaml`
automatically; compilation does not).

### Package Structure

```
packages/
├── core.yaml          # ESP32, logger, API, OTA, WiFi, captive portal
├── hardware.yaml      # SPI and I2C bus configuration
├── display.yaml       # TFT ST7735 display (128x128)
├── display-colors.yaml   # Color palette definitions
├── display-layout.yaml   # Screen layout constants
├── display-settings.yaml # Runtime display theme settings
├── fonts.yaml         # Pixelmix font + Material Symbols icons
├── buzzer.yaml        # PWM output + RTTTL melodies + sound buttons
├── buttons.yaml       # 6 capacitive touch buttons
├── buttons-gpio.yaml  # GPIO button variant (Wokwi simulator)
├── sensors.yaml       # WiFi signal, uptime, CPU temp, light sensor
├── bluetooth.yaml     # BLE tracker + Bluetooth proxy
├── ir-receiver.yaml   # 38kHz IR remote receiver
├── ir-transmitter.yaml # IR LED emitter (Rev 1.0 only)
├── led-matrix.yaml    # 32x8 WS2812B LED matrix (256 LEDs)
├── mqtt.yaml          # MQTT broker connectivity (optional)
└── stepper.yaml       # 28BYJ-48 stepper motors via MCP23009
```

Package dependencies: `buttons.yaml` requires `buzzer.yaml` (button sounds);
`display.yaml` requires `hardware.yaml`, `fonts.yaml`, `display-colors.yaml`,
and `display-layout.yaml`.

### Using Packages

Sample configs use substitutions and include packages:

```yaml
substitutions:
  device_name: ed1-mydevice
  friendly_name: ED1 My Device
  ap_ssid: ED1-MyDevice-Rescue
  # Credentials injected into packages (remote packages cannot use !secret)
  wifi_ssid: !secret wifi_ssid
  wifi_password: !secret wifi_password
  fallback_ap_password: !secret fallback_ap_password
  api_encryption_key: !secret api_encryption_key
  ota_password: !secret ota_password

packages:
  core: !include packages/core.yaml
  hardware: !include packages/hardware.yaml
  display: !include packages/display.yaml
  # ... other packages as needed
```

To override or extend package components, use `!extend`:

```yaml
display:
  - id: !extend internal_display
    lambda: |-
      // Custom display code here

binary_sensor:
  - id: !extend btn_ok
    on_press:
      - logger.log: "Custom OK action"
```

### Key Hardware Details

- **MCU**: ESP32-SIP
- **USB-UART**: CP2102N (requires Silicon Labs driver)
- **SPI bus**: CLK GPIO18, MOSI GPIO23, MISO GPIO19; **I2C bus**: SDA GPIO21, SCL GPIO22
- **TFT Display**: ST7735 128x128 — CS GPIO5, DC GPIO9, RESET GPIO10
- **LED Matrix**: optional external accessory, 256 WS2812 LEDs in serpentine pattern, connects to a D header (S/+/−). Design pin GPIO12; hardware verification inconclusive (see packages/led-matrix.yaml). GPIO12 is the MTDI strapping pin — a panel pulling DIN high at reset prevents boot.
- **Buzzer**: GPIO26 via PAM8301 amplifier
- **IR Receiver**: GPIO35 (TSOP75438TT); Rev 1.0 uses GPIO33
- **IR Emitter**: GPIO32 (Rev 1.0 only)
- **Touch Buttons**: GPIO4, GPIO13, GPIO2, GPIO27, GPIO15, GPIO14
- **Light Sensor**: GPIO34 (ADC)
- **I2C Address 0x15**: MXC6655XA accelerometer (not yet implemented)
- **I2C Address 0x20**: MCP23009 I/O expander (stepper motor control)
- **Power Switch**: SW1 slide switch (mechanical only, no GPIO)
- **Battery Monitoring**: Not available (VBAT/charging status not connected to any GPIO)

### Secrets

Credentials are stored in `secrets.yaml` (git-ignored). Use
`secrets.sample.yaml` as the template — configs and CI use exactly those key
names. Reference with `!secret key_name` syntax in device configs only (never
in `packages/`).

## Commit Conventions

Use prefixes: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`

## Hardware Documentation

Original KiCad schematics are in `docs/ED1 2.3/`, component datasheets in
`docs/datasheets/`. The full hardware reference (pinouts, revision
differences) lives at [docs.glifo.cat](https://docs.glifo.cat/ed1-hoas/hardware/overview).
