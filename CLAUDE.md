# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ESPHome configuration for integrating the ED1 Citilab ESP32 educational board with Home Assistant. The ED1 is a Spanish educational board with TFT display, LED matrix, touch buttons, and various sensors.

## Commands

```bash
# Validate ESPHome configuration
esphome config ed1-rev23-a-yaml

# Compile without uploading
esphome compile ed1-rev23-a-yaml

# Compile and upload via USB
esphome run ed1-rev23-a-yaml

# Monitor device logs
esphome logs ed1-rev23-a-yaml
```

## Architecture

This is an ESPHome project, not a traditional codebase. The main configuration file is `ed1-rev23-a-yaml`.

### Configuration Structure

The ESPHome YAML is organized into numbered sections:
1. Hardware buses (SPI, I2C)
2. Displays (TFT ST7735 + 32x8 LED matrix)
3. LED matrix light entity (NeoPixel)
4. Bluetooth proxy
5. Touch buttons (6 capacitive)
6. Sensors (light, WiFi, temperature)
7. Text input for matrix display

### Key Hardware Details

- **MCU**: ESP32-SIP
- **USB-UART**: CP2102N (requires Silicon Labs driver)
- **I2C Address 0x15**: MXC6655XA accelerometer (not yet implemented)
- **I2C Address 0x20**: MCP23009 I/O expander (not yet implemented)
- **LED Matrix**: 256 WS2812 LEDs in serpentine pattern on GPIO12

### Secrets

Credentials are stored in `secrets.yaml` (git-ignored). Use `secrets.yaml.sample` as template. Reference with `!secret key_name` syntax.

## Hardware Documentation

Original KiCad schematics are in `docs/ED1 2.3/` (git-ignored). Key pinouts and component info are documented in `docs/HARDWARE.md` and `docs/PINOUT.md`.
