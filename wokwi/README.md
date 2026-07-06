# Virtual ED1 — Wokwi Simulator

Run the ED1 firmware on an emulated ESP32 in [Wokwi](https://wokwi.com),
no hardware required. The simulated board mirrors the physical ED1 layout
(see `docs/images/ed1-front.png`): TFT display in the center, the four
arrow buttons around it, OK bottom-left, X bottom-right, and the light
sensor and IR receiver top-right.

The emulator executes the real compiled firmware binary — the same bytes
you would flash to a physical board.

## What is (and isn't) emulated

| ED1 feature | Virtual board | Notes |
|---|---|---|
| ST7735 128x128 TFT | ✅ | Community [ST7735 custom chip](https://github.com/martysweet/st7735-wokwi-chip), driven by the same `st7735` ESPHome driver as the real board; its canvas is 128x160, so the 128x128 image may sit with a small offset |
| 6 buttons | ⚠️ pushbuttons | Wokwi does not emulate the ESP32 capacitive-touch peripheral, so `ed1-wokwi.yaml` uses `packages/buttons-gpio.yaml` (same pins, same IDs) |
| Buzzer (GPIO26) | ✅ | LEDC PWM is simulated; RTTTL beeps are audible |
| Light sensor (GPIO34) | ✅ | Photoresistor part; drag its slider to change the LIGHT bar on the display |
| IR receiver (GPIO35) | ✅ part present | Enable `packages/ir-receiver.yaml` in the config to use it |
| WiFi | ✅ | Connects to the built-in open `Wokwi-GUEST` network |
| Native API → Home Assistant | ✅ | Port 6053 is forwarded to `localhost:6053` (see `wokwi.toml`) |
| Bluetooth proxy | ❌ | Not supported by the simulator |
| Stepper motors (MCP23009) | ❌ | No I2C expander part; would need a custom chip |
| 32x8 LED matrix | ❌ (yet) | Wokwi has a WS2812 matrix part, but its serpentine layout hasn't been verified against the ED1 mapping |

## Quick start

1. **Build the firmware** (from the repo root):

   ```bash
   esphome compile ed1-wokwi.yaml
   ```

2. **Run the simulation**, either way:

   - **VS Code**: install the [Wokwi extension](https://docs.wokwi.com/vscode/getting-started),
     activate the free license (`F1` → *Wokwi: Request a new License*), then
     `F1` → *Wokwi: Start Simulator* with this folder's `diagram.json` open.

   - **CLI**: install [wokwi-cli](https://docs.wokwi.com/wokwi-ci/getting-started),
     set `WOKWI_CLI_TOKEN` (free token from <https://wokwi.com/dashboard/ci>),
     then from the repo root:

     ```bash
     wokwi-cli wokwi --timeout 120000
     ```

3. Watch the boot splash, then the status dashboard. Click the buttons
   (they beep; keyboard shortcuts U/D/L/R/O/X while a button is focused),
   drag the photoresistor value, and check the serial monitor for the
   ESPHome log.

## Connecting to Home Assistant

With the simulation running, the ESPHome native API is reachable at
`localhost:6053`. Add the device in Home Assistant with
*Settings → Devices & Services → Add integration → ESPHome*, host
`localhost` (or your machine's IP), port `6053`. The API is unencrypted in
`ed1-wokwi.yaml`; add an `encryption:` key there if you expose the port
beyond your machine.

## CI use (optional)

`wokwi-cli` supports scripted scenarios (`--scenario`), serial assertions
(`--expect-text`) and display screenshots (`--screenshot-part display`),
and there is a GitHub Action (`wokwi/wokwi-ci-action`). A smoke test like
"boots and connects to WiFi" would need the `WOKWI_CLI_TOKEN` repo secret;
it is not wired into this repo's CI yet.

## Files

- `diagram.json` — the virtual board: parts, ED1-style placement, wiring
- `wokwi.toml` — points Wokwi at the compiled firmware and forwards the API port
