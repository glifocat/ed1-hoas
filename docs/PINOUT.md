# ED1 GPIO Pinout Reference

Quick reference for GPIO assignments on the ED1 Citilab Board.

## GPIO Assignment Table

| GPIO | Function | ESPHome ID | Direction | Notes |
|------|----------|------------|-----------|-------|
| 0 | Boot/Flash | - | I | Boot mode select |
| 2 | Touch Left | `btn_left` | I | Capacitive touch |
| 4 | Touch Up | `btn_up` | I | Capacitive touch |
| 5 | TFT CS | `pantalla_interna` | O | SPI chip select |
| 9 | TFT DC | `pantalla_interna` | O | Data/Command |
| 10 | TFT Reset | `pantalla_interna` | O | Display reset |
| 12 | LED Matrix | `led_matrix_light` | O | WS2812 data |
| 13 | Touch Down | `btn_down` | I | Capacitive touch |
| 14 | Touch X | `btn_x` | I | Capacitive touch |
| 15 | Touch OK | `btn_ok` | I | Capacitive touch |
| 18 | SPI CLK | `spi` | O | SPI clock |
| 19 | SPI MISO | `spi` | I | SPI data in |
| 21 | I2C SDA | `bus_i2c` | I/O | I2C data |
| 22 | I2C SCL | `bus_i2c` | O | I2C clock |
| 23 | SPI MOSI | `spi` | O | SPI data out |
| 26 | Buzzer | - | O | Via PAM8301 amp |
| 27 | Touch Right | `btn_right` | I | Capacitive touch |
| 34 | Light Sensor | `light_sensor` | I | ADC input |
| 35 | IR Receiver | - | I | TSOP75438TT |

## Bus Assignments

### SPI Bus
```
CLK:  GPIO18
MOSI: GPIO23
MISO: GPIO19
```

Used by: TFT Display (ST7735)

### I2C Bus
```
SDA: GPIO21
SCL: GPIO22
```

| Device | Address | Function |
|--------|---------|----------|
| MXC6655XA | 0x15 | Accelerometer |
| MCP23009 | 0x20 | I/O Expander |

## Touch Button Mapping

```
              ┌─────────────┐
              │     UP      │
              │   GPIO4     │
              └─────────────┘
┌─────────┐   ┌───────────┐   ┌─────────┐
│  LEFT   │   │           │   │  RIGHT  │
│ GPIO2   │   │    TFT    │   │ GPIO27  │
└─────────┘   │  Display  │   └─────────┘
              │           │
┌─────────┐   └───────────┘   ┌─────────┐
│   OK    │                   │    X    │
│ GPIO15  │                   │ GPIO14  │
└─────────┘   ┌─────────────┐ └─────────┘
              │    DOWN     │
              │   GPIO13    │
              └─────────────┘
```

## Analog Inputs

| GPIO | Function | ADC Channel | Attenuation |
|------|----------|-------------|-------------|
| 34 | Light Sensor | ADC1_CH6 | 12dB (0-3.3V) |

## LED Matrix

- **Data Pin**: GPIO12
- **Type**: WS2812X (GRB color order)
- **Count**: 256 LEDs (32 columns x 8 rows)
- **Layout**: Serpentine (zigzag) pattern

### Pixel Mapping
```
Column:  0   1   2   3  ...
Row 0:   0   15  16  31 ...
Row 1:   1   14  17  30 ...
Row 2:   2   13  18  29 ...
...
Row 7:   7   8   23  24 ...
```

Formula:
```cpp
if (x % 2 == 0)
    pixel = (x * 8) + y;
else
    pixel = (x * 8) + (7 - y);
```

## Expansion Connectors

### Analog Ports (Left Side)
```
A1: [S] [+] [-]    A2: [S] [+] [-]
A3: [S] [+] [-]    A4: [S] [+] [-]
```

### Digital Ports (Right Side)
```
D1: [S] [+] [-]    D2: [S] [+] [-]
D3: [S] [+] [-]    D4: [S] [+] [-]
```

### I2C/Serial (Bottom Left)
```
DA: [DA] [CL] [TX] [RX]
```

### Grove Connector (J11)
```
Pin 1: VDD33 (3.3V)
Pin 2: GND
Pin 3: SDA (GPIO21)
Pin 4: SCL (GPIO22)
```

## Stepper Motor Connectors

### M1 & M2 (28BYJ-48)
```
Pin 1: Coil A
Pin 2: Coil B
Pin 3: Coil C
Pin 4: Coil D
Pin 5: VDD5 (common)
```

Controlled via MCP23009 I/O expander and ULN2004A drivers.

## Reserved/Internal GPIOs

These GPIOs are used internally by the ESP32 or board hardware:

| GPIO | Internal Use |
|------|--------------|
| 6-11 | Flash (do not use) |
| 16, 17 | Flash CS/SDO |
| 36, 39 | Sensor VP/VN |
