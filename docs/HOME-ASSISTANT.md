# Home Assistant Integration Guide

How to use the ED1 board with Home Assistant.

## Available Entities

After adding the device, these entities become available:

### Lights

| Entity ID | Type | Description |
|-----------|------|-------------|
| `light.ed1_luz_matriz` | RGB Light | 32x8 LED matrix |

### Sensors

| Entity ID | Type | Unit | Description |
|-----------|------|------|-------------|
| `sensor.ed1_luz` | Sensor | % | Ambient light level |
| `sensor.ed1_senal_wifi` | Sensor | dBm | WiFi signal strength |
| `sensor.ed1_temperatura_cpu` | Sensor | °C | ESP32 internal temperature |
| `sensor.ed1_tiempo_encendido` | Sensor | s | Device uptime |

### Binary Sensors (Touch Buttons)

| Entity ID | Type | Description |
|-----------|------|-------------|
| `binary_sensor.ed1_boton_arriba` | Binary Sensor | Up button |
| `binary_sensor.ed1_boton_abajo` | Binary Sensor | Down button |
| `binary_sensor.ed1_boton_izquierda` | Binary Sensor | Left button |
| `binary_sensor.ed1_boton_derecha` | Binary Sensor | Right button |
| `binary_sensor.ed1_boton_ok` | Binary Sensor | OK button |
| `binary_sensor.ed1_boton_x` | Binary Sensor | X button |

### Text

| Entity ID | Type | Description |
|-----------|------|-------------|
| `text.escribir_en_matriz` | Text | Send text to LED matrix |

### Diagnostic

| Entity ID | Type | Description |
|-----------|------|-------------|
| `text_sensor.ed1_ip_address` | Text Sensor | Device IP address |

## Dashboard Examples

### Basic Card

```yaml
type: entities
title: ED1 Board
entities:
  - entity: light.ed1_luz_matriz
  - entity: text.escribir_en_matriz
  - entity: sensor.ed1_luz
  - entity: sensor.ed1_temperatura_cpu
  - entity: sensor.ed1_senal_wifi
```

### LED Matrix Control Card

```yaml
type: vertical-stack
cards:
  - type: light
    entity: light.ed1_luz_matriz
    name: LED Matrix
  - type: entities
    entities:
      - entity: text.escribir_en_matriz
        name: Display Text
```

### Touch Buttons Status

```yaml
type: glance
title: ED1 Buttons
entities:
  - entity: binary_sensor.ed1_boton_arriba
    name: Up
  - entity: binary_sensor.ed1_boton_abajo
    name: Down
  - entity: binary_sensor.ed1_boton_izquierda
    name: Left
  - entity: binary_sensor.ed1_boton_derecha
    name: Right
  - entity: binary_sensor.ed1_boton_ok
    name: OK
  - entity: binary_sensor.ed1_boton_x
    name: X
```

### Sensor Gauges

```yaml
type: horizontal-stack
cards:
  - type: gauge
    entity: sensor.ed1_luz
    name: Light
    min: 0
    max: 100
    severity:
      green: 50
      yellow: 20
      red: 0
  - type: gauge
    entity: sensor.ed1_temperatura_cpu
    name: CPU Temp
    min: 20
    max: 80
    severity:
      green: 40
      yellow: 60
      red: 70
```

## Automation Examples

### Display Notification on Matrix

```yaml
alias: "Display notification on ED1"
trigger:
  - platform: state
    entity_id: binary_sensor.front_door
    to: "on"
action:
  - service: text.set_value
    target:
      entity_id: text.escribir_en_matriz
    data:
      value: "DOOR!"
  - delay:
      seconds: 10
  - service: text.set_value
    target:
      entity_id: text.escribir_en_matriz
    data:
      value: ""
```

### Button Controls Light

```yaml
alias: "ED1 OK button toggles living room"
trigger:
  - platform: state
    entity_id: binary_sensor.ed1_boton_ok
    to: "on"
action:
  - service: light.toggle
    target:
      entity_id: light.living_room
```

### Button Navigation Menu

```yaml
alias: "ED1 Up button - next scene"
trigger:
  - platform: state
    entity_id: binary_sensor.ed1_boton_arriba
    to: "on"
action:
  - service: input_select.select_next
    target:
      entity_id: input_select.scene_selector
```

### Light Level Automation

```yaml
alias: "Auto lights based on ED1 sensor"
trigger:
  - platform: numeric_state
    entity_id: sensor.ed1_luz
    below: 30
condition:
  - condition: state
    entity_id: sun.sun
    state: "below_horizon"
action:
  - service: light.turn_on
    target:
      entity_id: light.desk_lamp
```

### Display Current Time

```yaml
alias: "Update ED1 with time every minute"
trigger:
  - platform: time_pattern
    minutes: "/1"
action:
  - service: text.set_value
    target:
      entity_id: text.escribir_en_matriz
    data:
      value: "{{ now().strftime('%H:%M') }}"
```

### Display Weather

```yaml
alias: "Show weather on ED1"
trigger:
  - platform: state
    entity_id: weather.home
action:
  - service: text.set_value
    target:
      entity_id: text.escribir_en_matriz
    data:
      value: "{{ state_attr('weather.home', 'temperature') }}C"
```

## Scripts

### Flash Matrix Red (Alert)

```yaml
flash_ed1_alert:
  alias: "Flash ED1 Matrix Red"
  sequence:
    - repeat:
        count: 5
        sequence:
          - service: light.turn_on
            target:
              entity_id: light.ed1_luz_matriz
            data:
              rgb_color: [255, 0, 0]
              brightness: 255
          - delay:
              milliseconds: 200
          - service: light.turn_off
            target:
              entity_id: light.ed1_luz_matriz
          - delay:
              milliseconds: 200
```

### Cycle Through Colors

```yaml
ed1_color_cycle:
  alias: "ED1 Color Cycle"
  sequence:
    - service: light.turn_on
      target:
        entity_id: light.ed1_luz_matriz
      data:
        rgb_color: [255, 0, 0]
    - delay:
        seconds: 1
    - service: light.turn_on
      target:
        entity_id: light.ed1_luz_matriz
      data:
        rgb_color: [0, 255, 0]
    - delay:
        seconds: 1
    - service: light.turn_on
      target:
        entity_id: light.ed1_luz_matriz
      data:
        rgb_color: [0, 0, 255]
```

## Bluetooth Proxy

The ED1 acts as a Bluetooth proxy, extending Home Assistant's BLE range.

### Setup
1. Ensure `bluetooth_proxy` is enabled in ESPHome config
2. In Home Assistant, go to Settings > Devices & Services
3. Bluetooth integration will automatically use the ED1 as a proxy

### Use Cases
- Detect BLE devices further from HA server
- Track Bluetooth thermometers, plant sensors
- Connect to Bluetooth devices in other rooms

## Tips

### Reduce API Traffic
If the device disconnects frequently, reduce sensor update rates:
```yaml
sensor:
  - platform: wifi_signal
    update_interval: 300s  # 5 minutes instead of 60s
```

### Entity Naming
Entity IDs are derived from `name` fields. To customize:
```yaml
sensor:
  - platform: internal_temperature
    name: "ED1 CPU Temp"  # becomes sensor.ed1_cpu_temp
```

### Multiple Boards
For multiple ED1 boards, change the device name:
```yaml
esphome:
  name: ed1-kitchen
  friendly_name: ED1 Kitchen
```
