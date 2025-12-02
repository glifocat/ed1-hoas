# ED1 Hardware Reference

Complete hardware documentation for the ED1 Citilab Board Rev 2.3.

## Board Overview

The ED1 is an ESP32-based educational development board designed by [Citilab Edutec](https://citilab.eu). It integrates multiple peripherals for learning embedded systems and IoT development.

### Specifications

| Parameter | Value |
|-----------|-------|
| MCU | ESP32-SIP (dual-core, 240MHz) |
| Flash | Integrated in SIP |
| RAM | 520KB SRAM |
| WiFi | 2.4GHz 802.11 b/g/n |
| Bluetooth | BLE 4.2 |
| Power Input | USB-C (5V) |
| Battery | 16340/CR123A Li-Ion (3.7V) |
| Dimensions | ~80mm x 60mm |

## Block Diagram

```
                           ┌─────────────────────────────────────┐
                           │           ED1 Board                 │
    ┌─────────┐            │                                     │
    │  USB-C  │──►[NCP347]─┼──►[MP2607DL]──►[PAM2401]──►5V      │
    └─────────┘  Overvolt  │   Li-Po Chrg    Boost               │
                 Protect   │       │                              │
                           │       ▼         [ADP2108]──►3.3V    │
                           │   ┌───────┐     Step-down           │
                           │   │Battery│                          │
                           │   │16340  │                          │
                           │   └───────┘                          │
                           │                                      │
    ┌─────────┐            │   ┌─────────────────┐               │
    │CP2102N  │◄──────────►│   │    ESP32-SIP    │               │
    │USB-UART │            │   │                 │               │
    └─────────┘            │   │  GPIO  I2C  SPI │               │
                           │   └──┬──────┬────┬──┘               │
                           │      │      │    │                   │
              ┌────────────┼──────┘      │    └───────┐          │
              │            │             │            │          │
              ▼            │             ▼            ▼          │
    ┌─────────────────┐    │    ┌─────────────┐  ┌────────┐     │
    │  Touch Buttons  │    │    │ I2C Devices │  │  TFT   │     │
    │  (6x capacitive)│    │    │ MXC6655XA   │  │ST7735  │     │
    └─────────────────┘    │    │ MCP23009    │  │128x128 │     │
                           │    └─────────────┘  └────────┘     │
              ┌────────────┼─────────────────────────┐          │
              │            │                         │          │
              ▼            │                         ▼          │
    ┌─────────────────┐    │               ┌─────────────────┐  │
    │   LED Matrix    │    │               │   Peripherals   │  │
    │  32x8 WS2812    │    │               │ IR RX, LDR,     │  │
    │  (256 LEDs)     │    │               │ Buzzer, Steppers│  │
    └─────────────────┘    │               └─────────────────┘  │
                           └─────────────────────────────────────┘
```

## Components

### Main Controller

| Component | Part Number | Description |
|-----------|-------------|-------------|
| U5 | ESP32-SIP | Main MCU with integrated flash |

### Power Management

| Component | Part Number | Function | Notes |
|-----------|-------------|----------|-------|
| J1 | 105450-0101 | USB-C Connector | Power + data |
| U2 | NCP347 | USB Overvoltage Protection | Protects against >5.5V |
| U1 | MP2607DL-LF-Z | Li-Po Charger | 1A charge rate, load sharing |
| IC1 | PAM2401SCADJ | 5V Buck-Boost | From battery to 5V |
| U9 | ADP2108 | 3.3V Step-Down | System 3.3V rail |
| Q1, Q2 | NMOS/PMOS | Battery Protection | Reverse polarity protection |
| BT1 | 16340/CR123A | Battery Holder | 3.7V Li-Ion |

### Communication

| Component | Part Number | Function | Notes |
|-----------|-------------|----------|-------|
| U6 | CP2102N | USB to UART | Auto-programming support |
| ANT1 | PRO-OB-440 | 2.4GHz Antenna | PCB antenna |

### Display

| Component | Part Number | Interface | Notes |
|-----------|-------------|-----------|-------|
| TFT1 | TFT-Z144SN005 | SPI | 1.44" 128x128 ST7735 |
| LED Matrix | WS2812X | GPIO12 | 32x8 (256 LEDs) external |

### Sensors

| Component | Part Number | Interface | Address | Notes |
|-----------|-------------|-----------|---------|-------|
| U13 | MXC6655XA | I2C | 0x15 | 3-axis accelerometer |
| Q5 | ALS-PT19-315C | ADC (GPIO34) | - | Light sensor |
| U12 | TSOP75438TT | GPIO35 | - | IR receiver 38kHz |

### Input/Output

| Component | Part Number | Function | Notes |
|-----------|-------------|----------|-------|
| T1-T6 | Capacitive pads | Touch buttons | 6 buttons around display |
| SW2 | PTS820 | Reset button | Hardware reset |
| U11 | MCP23009 | I2C GPIO Expander | 8 additional GPIO @ 0x20 |
| U7, U8 | ULN2004A | Stepper Drivers | For 28BYJ-48 motors |
| U10 | PAM8301AAF | Audio Amplifier | For buzzer/speaker |
| Z1 | MLT-8530 | Buzzer | Driven by amplifier |

### Connectors

| Connector | Type | Pins | Function |
|-----------|------|------|----------|
| J2-J10 | 2.54mm Header | 4 | GPIO expansion |
| J11 | Grove | 4 | I2C Grove connector |
| M1, M2 | JST-XH | 5 | Stepper motor (28BYJ-48) |

## Power System

### Power Sources
1. **USB-C (5V)**: Primary power, also charges battery
2. **Battery (3.7V)**: 16340/CR123A Li-Ion cell

### Power Rails
- **VBUS**: Raw USB voltage (5V)
- **VDD_IN**: After overvoltage protection
- **VBAT**: Battery voltage (3.0-4.2V)
- **VDD5**: Regulated 5V (from buck-boost)
- **VDD33**: Regulated 3.3V (system rail)
- **VDD3A**: Analog 3.3V (for ESP32)

### Charging
- **Charge IC**: MP2607DL with load sharing
- **Charge Rate**: 1000mA (set by R6)
- **Status LEDs**: STAT1, STAT2, DONE, CHR

### Battery Protection
When battery is inserted with wrong polarity, Q1 and Q2 transistors isolate the battery from the system, preventing damage.

## Datasheets

Component datasheets are included in `docs/datasheets/`:

- [MXC6655XA Accelerometer](datasheets/MXC6655XA-accelerometer.pdf)
- [PAM2401 Buck-Boost](datasheets/PAM2401-buck-boost.pdf)
- [CP2102N USB-UART](datasheets/CP2102N-usb-uart.pdf)

## Hardware Revision

This documentation covers **ED1 Rev 2.3**.

The original KiCad design files and full schematics are available from [Citilab](https://citilab.eu).
