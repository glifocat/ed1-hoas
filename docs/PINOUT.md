# ED1 GPIO Pinout Reference

Quick reference for GPIO assignments on the ED1 Citilab Board.

## GPIO Assignment Table

| GPIO  | Function       | ESPHome ID           | Direction | Notes                                        |
| ----- | -------------- | -------------------- | --------- | -------------------------------------------- |
| 0     | Boot/Flash     | -                    | I         | Boot mode select                             |
| 2     | Touch Left     | `btn_left`           | I         | Capacitive touch                             |
| 4     | Touch Up       | `btn_up`             | I         | Capacitive touch                             |
| 5     | TFT CS         | `internal_display`   | O         | SPI chip select                              |
| 9     | TFT DC         | `internal_display`   | O         | Data/Command                                 |
| 10    | TFT Reset      | `internal_display`   | O         | Display reset                                |
| 12    | LED Matrix     | `led_matrix_light`   | O         | WS2812 data                                  |
| 13    | Touch Down     | `btn_down`           | I         | Capacitive touch                             |
| 14    | Touch X        | `btn_x`              | I         | Capacitive touch                             |
| 15    | Touch OK       | `btn_ok`             | I         | Capacitive touch                             |
| 18    | SPI CLK        | `spi`                | O         | SPI clock                                    |
| 19    | SPI MISO       | `spi`                | I         | SPI data in                                  |
| 21    | I2C SDA        | `bus_i2c`            | I/O       | I2C data                                     |
| 22    | I2C SCL        | `bus_i2c`            | O         | I2C clock                                    |
| 23    | SPI MOSI       | `spi`                | O         | SPI data out                                 |
| 26    | Buzzer         | `buzzer_output`      | O         | Via PAM8301 amp                              |
| 27    | Touch Right    | `btn_right`          | I         | Capacitive touch                             |
| 34    | Light Sensor   | `light_sensor`       | I         | ADC input                                    |
| 32    | IR Transmitter | `remote_transmitter` | O         | Rev 1.0 only                                 |
| 33/35 | IR Receiver    | `remote_receiver`    | I         | TSOP75438TT (GPIO33 Rev 1.0, GPIO35 Rev 2.3) |

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

**Rev 2.3:**
| Device | Address | Function |
|--------|---------|----------|
| MXC6655XA | 0x15 | Accelerometer |
| MCP23009 | 0x20 | I/O Expander (stepper motors) |

**Rev 1.0:**
| Device | Address | Function |
|--------|---------|----------|
| LIS3DH | 0x19 | Accelerometer |
| MCP23017 | 0x20 | I/O Expander (16 GPIO pins) |

### MCP23009 GPIO Mapping (Stepper Motors)

```
GP0: Motor 2 Coil D ──► ULN2004A U8 ──► M2
GP1: Motor 2 Coil C ──► ULN2004A U8 ──► M2
GP2: Motor 2 Coil B ──► ULN2004A U8 ──► M2
GP3: Motor 2 Coil A ──► ULN2004A U8 ──► M2
GP4: Motor 1 Coil D ──► ULN2004A U7 ──► M1
GP5: Motor 1 Coil C ──► ULN2004A U7 ──► M1
GP6: Motor 1 Coil B ──► ULN2004A U7 ──► M1
GP7: Motor 1 Coil A ──► ULN2004A U7 ──► M1
```

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

| GPIO | Function     | ADC Channel | Attenuation   |
| ---- | ------------ | ----------- | ------------- |
| 34   | Light Sensor | ADC1_CH6    | 12dB (0-3.3V) |

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

### Analog Ports - J5 (Left Side)

Input-only ADC pins, directly connected to ESP32. Active-low.

| Port | GPIO   | ADC Channel | Notes           |
| ---- | ------ | ----------- | --------------- |
| A1   | GPIO36 | ADC1_CH0    | SVP (Sensor VP) |
| A2   | GPIO37 | ADC1_CH1    | -               |
| A3   | GPIO38 | ADC1_CH2    | -               |
| A4   | GPIO39 | ADC1_CH3    | SVN (Sensor VN) |

```
A1: [S=GPIO36] [+=3.3V] [-=GND]
A2: [S=GPIO37] [+=3.3V] [-=GND]
A3: [S=GPIO38] [+=3.3V] [-=GND]
A4: [S=GPIO39] [+=3.3V] [-=GND]
```

### Digital Ports - J2 (Right Side)

| Port | GPIO   | ADC Channel | Notes                |
| ---- | ------ | ----------- | -------------------- |
| D1   | GPIO12 | ADC2_CH5    | Also LED matrix data |
| D2   | GPIO25 | ADC2_CH8    | DAC1                 |
| D3   | GPIO32 | ADC1_CH4    | -                    |
| D4   | GPIO26 | ADC2_CH9    | Also buzzer output   |

```
D1: [S=GPIO12] [+=5V] [-=GND]
D2: [S=GPIO25] [+=5V] [-=GND]
D3: [S=GPIO32] [+=5V] [-=GND]
D4: [S=GPIO26] [+=5V] [-=GND]
```

**Note:** D1 (GPIO12) and D4 (GPIO26) are used internally. D2 (GPIO25) and D3 (GPIO32) are available for external use.

### I2C/Serial - J6 (Bottom Left)

| Pin | Label | GPIO   | Function |
| --- | ----- | ------ | -------- |
| 1   | DA    | GPIO21 | I2C SDA  |
| 2   | CL    | GPIO22 | I2C SCL  |
| 3   | TX    | GPIO1  | UART TX  |
| 4   | RX    | GPIO3  | UART RX  |

```
DA: [DA=GPIO21] [CL=GPIO22] [TX=GPIO1] [RX=GPIO3]
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

| GPIO   | Internal Use       |
| ------ | ------------------ |
| 6-11   | Flash (do not use) |
| 16, 17 | Flash CS/SDO       |
| 36, 39 | Sensor VP/VN       |
