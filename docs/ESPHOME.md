# ESPHome Configuration Guide

Detailed explanation of the ESPHome configuration for the ED1 board.

## File Structure

```
ed1-hoas/
├── ed1-rev23-a.yaml      # Main configuration
├── secrets.yaml          # Credentials (git-ignored)
├── secrets.yaml.sample   # Template
└── pixelmix.ttf          # Font file
```

## Secrets Setup

1. Copy the sample file:
   ```bash
   cp secrets.yaml.sample secrets.yaml
   ```

2. Edit `secrets.yaml` with your values:
   ```yaml
   wifi_ssid: "YourNetworkName"
   wifi_password: "YourWiFiPassword"
   api_encryption_key: "base64-encoded-key"
   ota_password: "secure-ota-password"
   fallback_ap_password: "fallback-password"
   ```

3. Generate an API key:
   ```bash
   openssl rand -base64 32
   ```

## Configuration Sections

### 1. Core Configuration

```yaml
esphome:
  name: ed1-rev23-a
  friendly_name: ED1 Rev 2.3 A

esp32:
  board: esp32dev
  framework:
    type: arduino
```

- **name**: Device hostname (lowercase, hyphens only)
- **friendly_name**: Display name in Home Assistant
- **board**: Generic ESP32 dev board
- **framework**: Arduino for best compatibility

### 2. Connectivity

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "ED1-Rev23-Rescue"
    password: !secret fallback_ap_password

captive_portal:
```

- **ap**: Fallback access point if WiFi fails
- **captive_portal**: Web config when in AP mode

### 3. Hardware Buses

```yaml
spi:
  clk_pin: GPIO18
  mosi_pin: GPIO23
  miso_pin: GPIO19

i2c:
  sda: GPIO21
  scl: GPIO22
  scan: true
  id: bus_i2c
```

- **scan: true**: Logs detected I2C devices on boot

### 4. Fonts

```yaml
font:
  - file: "pixelmix.ttf"
    id: fuente_pixel
    size: 8
  - file: "pixelmix.ttf"
    id: fuente_grande
    size: 16
```

Download `pixelmix.ttf` and place it in your ESPHome config directory.

### 5. TFT Display (ST7735)

```yaml
display:
  - platform: st7735
    id: pantalla_interna
    cs_pin: GPIO5
    dc_pin: GPIO9
    reset_pin: GPIO10
    rotation: 0
    model: "INITR_GREENTAB"
    device_width: 128
    device_height: 128
    update_interval: 1s
    lambda: |-
      // Drawing code here
```

**Display Layout:**
```
┌────────────────────────┐
│     "ED1 PRO"          │  <- Green, large font
│                        │
│    192.168.1.100       │  <- IP address
│                        │
│     T: 45.2 C          │  <- CPU temp
│                        │
│   [Matrix Text]        │  <- Yellow, or "Matriz Lista"
└────────────────────────┘
```

**Model Options:**
- `INITR_GREENTAB`: Most common for 1.44" displays
- `INITR_BLACKTAB`: Alternative initialization
- `INITR_144GREENTAB`: Specific 144x144 variant

### 6. LED Matrix Display

```yaml
display:
  - platform: addressable_light
    id: led_matrix_display
    addressable_light_id: led_matrix_light
    width: 32
    height: 8
    pixel_mapper: |-
      if (x % 2 == 0) return (x * 8) + y;
      return (x * 8) + (7 - y);
    update_interval: 50ms
    lambda: |-
      // Text rendering
```

**pixel_mapper**: Handles the serpentine wiring pattern where odd columns are reversed.

### 7. LED Matrix Light

```yaml
light:
  - platform: neopixelbus
    type: GRB
    variant: WS2812X
    pin: GPIO12
    num_leds: 256
    name: "ED1 Luz Matriz"
    id: led_matrix_light
    method: esp32_rmt
    default_transition_length: 0s
    color_correct: [40%, 40%, 40%]
```

- **type: GRB**: Color order (Green-Red-Blue)
- **method: esp32_rmt**: Uses RMT peripheral for precise timing
- **color_correct**: Reduces brightness to 40% (power savings)

### 8. Bluetooth Proxy

```yaml
esp32_ble_tracker:
  scan_parameters:
    interval: 1100ms
    window: 1100ms

bluetooth_proxy:
  active: true
```

Extends Home Assistant's Bluetooth range. The ED1 acts as a BLE relay.

### 9. Touch Buttons

```yaml
esp32_touch:
  setup_mode: false

binary_sensor:
  - platform: esp32_touch
    id: btn_up
    name: "ED1 Botón Arriba"
    pin: GPIO4
    threshold: 500
    on_press:
      - logger.log: "Botón Arriba PRESSED"
```

**Threshold Tuning:**
- Default: 500
- If too sensitive: Increase threshold
- If not responding: Decrease threshold
- Enable `setup_mode: true` temporarily to see raw values

### 10. Sensors

```yaml
sensor:
  - platform: wifi_signal
    name: "ED1 Señal WiFi"
    update_interval: 60s

  - platform: internal_temperature
    name: "ED1 Temperatura CPU"
    id: temp_cpu

  - platform: adc
    pin: GPIO34
    name: "ED1 Luz (%)"
    attenuation: 12db
    filters:
      - multiply: 30.3  # Scale to 0-100%
```

### 11. Text Input

```yaml
text:
  - platform: template
    name: "Escribir en Matriz"
    id: mi_texto_input
    optimistic: true
    min_length: 0
    max_length: 20
    mode: text
```

Allows Home Assistant to send text to display on the LED matrix.

## Customization

### Change Display Content

Modify the `lambda` in the display section:

```yaml
lambda: |-
  it.fill(Color(0, 0, 0));
  it.print(0, 0, id(fuente_pixel), Color(255, 0, 0), "Custom Text");
```

### Add Button Actions

```yaml
binary_sensor:
  - platform: esp32_touch
    id: btn_ok
    name: "ED1 Botón OK"
    pin: GPIO15
    threshold: 500
    on_press:
      - light.toggle: led_matrix_light
```

### Adjust Matrix Brightness

Change `color_correct` values (0-100%):
```yaml
color_correct: [20%, 20%, 20%]  # Dimmer
color_correct: [100%, 100%, 100%]  # Full brightness
```

## Troubleshooting

### Display Shows Garbage
- Check `model` setting matches your display
- Try adjusting `col_start` and `row_start` offsets
- Verify SPI pins are correct

### Touch Buttons Not Working
- Enable `setup_mode: true` in `esp32_touch`
- Check logs for raw touch values
- Adjust threshold based on idle vs touched values

### LED Matrix Wrong Colors
- Change `type` from `GRB` to `RGB` or `BRG`
- Some strips use different color orders

### WiFi Connection Issues
- Check signal strength sensor
- Reduce `update_interval` on sensors to reduce traffic
- Try static IP configuration

### Device Not Discovered
- Ensure API encryption key matches
- Check Home Assistant logs for connection attempts
- Verify device is on same network subnet
