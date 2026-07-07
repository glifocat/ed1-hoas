# ED1 Hardware Self-Test Firmware Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A committed `ed1-hardware-test.yaml` that turns the ED1 into its own guided test rig: 8 steps rendered on the TFT, touch buttons as the confirmation mechanism, auto-pass where measurable.

**Architecture:** Single new root config composed from the existing `packages/` (core, hardware, display, fonts, buzzer, buttons, sensors, ir-receiver, led-matrix). All test logic lives in the root file via `!extend` overrides. State machine = `test_step` global + `step_results` vector + a handful of scripts (`pass_step`, `fail_step`, `next_step`, `step_watchdog`, `handle_button`, `restart_test`).

**Tech Stack:** ESPHome 2026.6.4 (pinned, same as CI), Arduino framework, board `esp32dev`. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-07-07-ed1-hardware-test-design.md`

## Global Constraints

- ESPHome version for all local validation/compilation: **2026.6.4** in a dedicated venv (`packages/core.yaml` floor is `min_version: 2026.1.0`).
- Real `secrets.yaml` exists in the repo root — do NOT overwrite it.
- All YAML must be LF line endings and pass yamllint with: `line-length: max 150`, `document-start/truthy/comments: disable`.
- LED matrix full-fills must stay dim: never brighter than `Color(40, 40, 40)` per channel (256 WS2812 at full white browns out USB power). Single walking pixel may be bright.
- Commit prefixes: `feat:`, `fix:`, `docs:`, `chore:` (repo convention).
- Working branch: `feat/hardware-test` (already created, holds the spec commit).
- Test cycle for every task: `esphome config ed1-hardware-test.yaml` (validate) then `esphome compile ed1-hardware-test.yaml`. There is no unit-test framework for ESPHome YAML — validate+compile IS the test.
- Button index convention used everywhere: `0=UP, 1=DOWN, 2=LEFT, 3=RIGHT, 4=OK, 5=X` (order also used for the step-4 prompts).
- Step result convention: `0=pending, 1=pass, 2=fail` in `step_results` (size 8, indices = step numbers).

---

### Task 1: Toolchain + skeleton with complete step engine

**Files:**
- Create: `ed1-hardware-test.yaml`
- Use (do not modify): `packages/*.yaml`, `secrets.yaml`

**Interfaces:**
- Consumes: package IDs — `internal_display`, `pixel_font`, `message_font`, `large_font`, `buzzer_rtttl`, `sound_success`, `sound_alert`, `sound_notify`, `sound_startup`, `btn_up/btn_down/btn_left/btn_right/btn_ok/btn_x`, `light_sensor`, `wifi_rssi` (global int), `wifi_ssid`/`wifi_ip` (text sensors), `led_matrix_light`, `led_matrix_display`, `ir_receiver`.
- Produces (later tasks rely on these exact names): globals `test_step` (int), `step_results` (std::vector<int>, size 8), `btn_index` (int), `step4_fails` (int), `ldr_baseline` (float), `walk_pos` (int), `last_ir` (std::string); scripts `pass_step`, `fail_step`, `next_step`, `step_watchdog`, `handle_button(btn: int)`, `restart_test`.

- [ ] **Step 1: Create the pinned toolchain venv**

```bash
python3 -m venv /private/tmp/claude-501/-Users-ethanmunoz-Projects-personal-ed1-hoas/a1bf9a99-68eb-45bd-a2e5-2a9a1b5bf21b/scratchpad/esphome-venv
/private/tmp/claude-501/-Users-ethanmunoz-Projects-personal-ed1-hoas/a1bf9a99-68eb-45bd-a2e5-2a9a1b5bf21b/scratchpad/esphome-venv/bin/pip install esphome==2026.6.4
```

Expected: pip resolves esphome 2026.6.4. Define `ESPHOME=<venv>/bin/esphome` for all later commands.

- [ ] **Step 2: Write the skeleton config**

Create `ed1-hardware-test.yaml` with exactly this content (header comment kept short here; Task 5 expands it):

```yaml
# ==============================================================================
# ED1 Hardware Self-Test - guided on-device test sequence (see Task 5 header)
# ==============================================================================

substitutions:
  device_name: ed1-hwtest
  friendly_name: ED1 HW Test
  ap_ssid: ED1-HWTest-Rescue

packages:
  core: !include packages/core.yaml
  hardware: !include packages/hardware.yaml
  display: !include packages/display.yaml
  fonts: !include packages/fonts.yaml
  buzzer: !include packages/buzzer.yaml
  buttons: !include packages/buttons.yaml
  sensors: !include packages/sensors.yaml
  ir_receiver: !include packages/ir-receiver.yaml
  led_matrix: !include packages/led-matrix.yaml

esphome:
  on_boot:
    priority: -100
    then:
      # Matrix light must be ON for the addressable_light display to render.
      # Low brightness: 256 WS2812 at full white would brown out USB power.
      - light.turn_on:
          id: led_matrix_light
          brightness: 25%
          red: 100%
          green: 100%
          blue: 100%
      - script.execute: sound_startup
      - script.execute: step_watchdog

globals:
  - id: test_step          # current step 0..7
    type: int
    initial_value: '0'
  - id: step_results       # 0=pending 1=pass 2=fail, index = step
    type: std::vector<int>
    initial_value: 'std::vector<int>(8, 0)'
  - id: btn_index          # step 4: which button is currently prompted (0..5)
    type: int
    initial_value: '0'
  - id: step4_fails        # step 4: count of wrong presses
    type: int
    initial_value: '0'
  - id: ldr_baseline       # step 5: light level captured on step entry
    type: float
    initial_value: '0'
  - id: walk_pos           # step 2: walking pixel 0..255, then fill phases
    type: int
    initial_value: '0'
  - id: last_ir            # step 6: last decoded IR code, for the TFT
    type: std::string

script:
  - id: pass_step
    then:
      - lambda: 'id(step_results)[id(test_step)] = 1;'
      - script.execute: sound_success
      - script.execute: next_step

  - id: fail_step
    then:
      - lambda: 'id(step_results)[id(test_step)] = 2;'
      - script.execute: sound_alert
      - script.execute: next_step

  - id: next_step
    then:
      - lambda: |-
          id(test_step) += 1;
          switch (id(test_step)) {
            case 2:
              id(walk_pos) = 0;
              break;
            case 3:
              id(buzzer_rtttl).play("scale:d=8,o=5,b=160:c,d,e,f,g,a,b,c6");
              break;
            case 4:
              id(btn_index) = 0;
              id(step4_fails) = 0;
              // esp32_touch raw values only appear in setup_mode builds; leave a
              // diagnosis breadcrumb for 2026.x threshold drift.
              ESP_LOGI("hwtest", "Touch step: if presses do not register, rebuild "
                       "with esp32_touch setup_mode: true to read raw values");
              break;
            case 5:
              id(ldr_baseline) = isnan(id(light_sensor).state) ? 0.0f : id(light_sensor).state;
              ESP_LOGI("hwtest", "LDR baseline: %.1f", id(ldr_baseline));
              break;
            case 6:
              id(last_ir) = "";
              break;
            case 7: {
              bool all = true;
              for (int i = 0; i < 7; i++) {
                ESP_LOGI("hwtest", "Step %d: %s", i, id(step_results)[i] == 1 ? "PASS" : "FAIL");
                if (id(step_results)[i] != 1) all = false;
              }
              ESP_LOGI("hwtest", "RESULT: %s", all ? "ALL PASS" : "FAILURES PRESENT");
              break;
            }
          }
      - script.execute: step_watchdog

  # Timeouts: step 0 (WiFi) 20s, steps 5/6 (LDR, IR) 15s. mode: restart means
  # every step change re-arms it; steps without a timeout just fall through.
  - id: step_watchdog
    mode: restart
    then:
      - if:
          condition:
            lambda: 'return id(test_step) == 0;'
          then:
            - delay: 20s
            - if:
                condition:
                  lambda: 'return id(test_step) == 0;'
                then:
                  - script.execute: fail_step
      - if:
          condition:
            lambda: 'return id(test_step) == 5 || id(test_step) == 6;'
          then:
            - delay: 15s
            - if:
                condition:
                  lambda: 'return id(test_step) == 5 || id(test_step) == 6;'
                then:
                  - script.execute: fail_step

  # btn: 0=UP 1=DOWN 2=LEFT 3=RIGHT 4=OK 5=X
  - id: handle_button
    parameters:
      btn: int
    then:
      - lambda: |-
          int step = id(test_step);
          if (step == 4) {
            if (btn == id(btn_index)) {
              ESP_LOGI("hwtest", "Touch button %d OK", btn);
            } else {
              ESP_LOGW("hwtest", "Touch: expected %d, got %d", id(btn_index), btn);
              id(step4_fails) += 1;
            }
            id(btn_index) += 1;
            if (id(btn_index) >= 6) {
              if (id(step4_fails) == 0) id(pass_step).execute();
              else id(fail_step).execute();
            }
            return;
          }
          if (btn == 2) {  // LEFT: mark current step failed, move on
            if (step <= 6) id(fail_step).execute();
            return;
          }
          if (btn == 4) {  // OK: confirm observed steps
            if (step >= 1 && step <= 3) id(pass_step).execute();
          }

  - id: restart_test
    then:
      - lambda: |-
          for (int i = 0; i < 8; i++) id(step_results)[i] = 0;
          id(test_step) = 0;
          id(btn_index) = 0;
          id(step4_fails) = 0;
          id(walk_pos) = 0;
          id(last_ir) = "";
      - script.execute: sound_notify
      - script.execute: step_watchdog

interval:
  # Step 0 auto-pass when WiFi connects
  - interval: 1s
    then:
      - if:
          condition:
            and:
              - lambda: 'return id(test_step) == 0;'
              - wifi.connected:
          then:
            - script.execute: pass_step

binary_sensor:
  - id: !extend btn_up
    on_press:
      - script.execute:
          id: handle_button
          btn: 0
  - id: !extend btn_down
    on_press:
      - script.execute:
          id: handle_button
          btn: 1
  - id: !extend btn_left
    on_press:
      - script.execute:
          id: handle_button
          btn: 2
  - id: !extend btn_right
    on_press:
      - script.execute:
          id: handle_button
          btn: 3
  - id: !extend btn_ok
    on_press:
      - script.execute:
          id: handle_button
          btn: 4
    # Hold OK >=1.5s restarts the whole sequence (intended from the summary
    # screen; mid-test it will first register a normal OK press).
    on_multi_click:
      - timing:
          - ON for at least 1.5s
        then:
          - script.execute: restart_test
  - id: !extend btn_x
    on_press:
      - script.execute:
          id: handle_button
          btn: 5

display:
  - id: !extend internal_display
    update_interval: 250ms
    lambda: |-
      it.fill(Color(0, 0, 0));
      it.printf(2, 2, id(message_font), "HW TEST %d/7", id(test_step));
      // Task 2 replaces this stub with full per-step screens.
```

Note for the implementer: `!extend` on a `binary_sensor` id **appends** to list options like `on_press` — the base beep from `packages/buttons.yaml` stays, our handler is added after it. That is intended (beep = tactile feedback that the touch registered).

- [ ] **Step 3: Validate**

```bash
$ESPHOME config ed1-hardware-test.yaml
```

Expected: `Configuration is valid!` (INFO lines about packages are fine). If `std::vector<int>` in globals fails validation, replace `step_results` with `type: std::vector<int>` → keep, but move initializer to `initial_value: 'std::vector<int>(8, 0)'` exactly as shown — this form is the one that validates; a brace literal does not.

- [ ] **Step 4: Compile**

```bash
$ESPHOME compile ed1-hardware-test.yaml
```

Expected: `Successfully compiled program.` First compile is cold (Arduino-as-IDF-component builds the framework, ~10–20 min locally).

- [ ] **Step 5: Commit**

```bash
git add ed1-hardware-test.yaml
git commit -m "feat: add hardware self-test skeleton with step engine"
```

---

### Task 2: TFT per-step screens + buzzer replay

**Files:**
- Modify: `ed1-hardware-test.yaml` (the `display:` block's `internal_display` lambda; add one interval entry)

**Interfaces:**
- Consumes: globals and scripts from Task 1 (exact names above); fonts `pixel_font`/`message_font`; text sensors `wifi_ssid`, `wifi_ip`; global `wifi_rssi`; sensor `light_sensor`; global `last_ir`; rtttl `buzzer_rtttl`.
- Produces: the complete UI. No new names.

- [ ] **Step 1: Replace the internal_display stub lambda**

Replace the whole `display:` block for `internal_display` with:

```yaml
display:
  - id: !extend internal_display
    update_interval: 250ms
    lambda: |-
      static const char *BTN_NAMES[6] = {"UP", "DOWN", "LEFT", "RIGHT", "OK", "X"};
      it.fill(Color(0, 0, 0));
      switch (id(test_step)) {
        case 0: {
          it.print(2, 2, id(message_font), "HW TEST 0/7 WIFI");
          it.print(2, 18, id(pixel_font), "ESPHome " ESPHOME_VERSION);
          if (wifi::global_wifi_component->is_connected()) {
            it.printf(2, 32, id(pixel_font), "SSID: %s", id(wifi_ssid).state.c_str());
            it.printf(2, 42, id(pixel_font), "IP: %s", id(wifi_ip).state.c_str());
            it.printf(2, 52, id(pixel_font), "RSSI: %d dBm", id(wifi_rssi));
          } else {
            it.print(2, 32, id(pixel_font), "Connecting...");
            it.print(2, 42, id(pixel_font), "Fallback AP:");
            it.print(2, 52, id(pixel_font), "${ap_ssid}");
          }
          break;
        }
        case 1: {
          static const Color BARS[4] = {
            Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255), Color(255, 255, 255)
          };
          it.print(4, 4, id(pixel_font), "1/7 DISPLAY");
          for (int i = 0; i < 4; i++)
            it.filled_rectangle(8 + i * 28, 20, 24, 40, BARS[i]);
          it.rectangle(0, 0, 128, 128, Color(255, 255, 0));   // 1px border
          it.print(118, 4, id(pixel_font), "R");              // orientation marker top-right
          it.print(4, 70, id(pixel_font), "Bars R G B W?");
          it.print(4, 80, id(pixel_font), "Border + R top-right?");
          it.print(4, 110, id(pixel_font), "OK=pass  LEFT=fail");
          break;
        }
        case 2: {
          it.print(4, 4, id(pixel_font), "2/7 LED MATRIX");
          it.print(4, 24, id(pixel_font), "Watch the matrix:");
          it.print(4, 36, id(pixel_font), "1 pixel walks every");
          it.print(4, 46, id(pixel_font), "row, no jumps, then");
          it.print(4, 56, id(pixel_font), "R / G / B fills");
          it.print(4, 110, id(pixel_font), "OK=pass  LEFT=fail");
          break;
        }
        case 3: {
          it.print(4, 4, id(pixel_font), "3/7 BUZZER");
          it.print(4, 24, id(pixel_font), "You should hear a");
          it.print(4, 34, id(pixel_font), "scale every 6s");
          it.print(4, 110, id(pixel_font), "OK=pass  LEFT=fail");
          break;
        }
        case 4: {
          it.print(4, 4, id(pixel_font), "4/7 TOUCH");
          it.printf(20, 40, id(message_font), "Press %s", BTN_NAMES[id(btn_index)]);
          it.printf(4, 70, id(pixel_font), "%d/6  wrong press = fail", id(btn_index));
          break;
        }
        case 5: {
          it.print(4, 4, id(pixel_font), "5/7 LIGHT SENSOR");
          it.print(4, 24, id(pixel_font), "Cover the sensor!");
          it.printf(4, 44, id(pixel_font), "now:  %.1f", id(light_sensor).state);
          it.printf(4, 54, id(pixel_font), "base: %.1f", id(ldr_baseline));
          it.print(4, 70, id(pixel_font), "auto-pass at -50%%");
          it.print(4, 110, id(pixel_font), "15s timeout");
          break;
        }
        case 6: {
          it.print(4, 4, id(pixel_font), "6/7 IR RECEIVER");
          it.print(4, 24, id(pixel_font), "Point any remote,");
          it.print(4, 34, id(pixel_font), "press a key");
          if (!id(last_ir).empty())
            it.printf(4, 54, id(pixel_font), "%s", id(last_ir).c_str());
          it.print(4, 110, id(pixel_font), "15s timeout");
          break;
        }
        default: {
          static const char *STEP_NAMES[7] = {
            "WiFi", "Display", "Matrix", "Buzzer", "Touch", "Light", "IR"
          };
          it.print(4, 4, id(message_font), "SUMMARY");
          bool all = true;
          for (int i = 0; i < 7; i++) {
            bool ok = id(step_results)[i] == 1;
            if (!ok) all = false;
            it.printf(4, 22 + i * 10, id(pixel_font), "%s %s",
                      ok ? "PASS" : "FAIL", STEP_NAMES[i]);
          }
          it.print(4, 100, id(message_font), all ? "ALL PASS" : "CHECK LOG");
          it.print(4, 116, id(pixel_font), "hold OK = restart");
          break;
        }
      }
```

- [ ] **Step 2: Add the buzzer replay interval**

Append to the existing `interval:` list (keep the 1s WiFi entry):

```yaml
  # Step 3: replay the scale every 6s so the user can listen again
  - interval: 6s
    then:
      - if:
          condition:
            lambda: 'return id(test_step) == 3;'
          then:
            - lambda: 'id(buzzer_rtttl).play("scale:d=8,o=5,b=160:c,d,e,f,g,a,b,c6");'
```

- [ ] **Step 3: Validate + compile**

```bash
$ESPHOME config ed1-hardware-test.yaml && $ESPHOME compile ed1-hardware-test.yaml
```

Expected: valid + `Successfully compiled program.` (warm build, ~1–3 min). If `wifi::global_wifi_component` fails to compile, replace the condition with `id(wifi_ssid).has_state() && !id(wifi_ssid).state.empty()`.

- [ ] **Step 4: Commit**

```bash
git add ed1-hardware-test.yaml
git commit -m "feat: add per-step TFT screens and buzzer replay to hardware test"
```

---

### Task 3: LED matrix walking pixel + R/G/B fills

**Files:**
- Modify: `ed1-hardware-test.yaml` (add `led_matrix_display` extend block; add one interval entry)

**Interfaces:**
- Consumes: globals `test_step`, `walk_pos`, `step_results`; display `led_matrix_display` (32x8, serpentine `pixel_mapper` defined in `packages/led-matrix.yaml`).
- Produces: no new names. Fill phases derived from `walk_pos`: 0–255 walk, 256–345 fills (30 ticks = 1.5 s per color), ≥346 idle.

- [ ] **Step 1: Add the walk driver interval**

Append to `interval:`:

```yaml
  # Step 2: advance the walking pixel (50ms/LED = 12.8s walk) then fill phases
  - interval: 50ms
    then:
      - lambda: |-
          if (id(test_step) == 2 && id(walk_pos) < 346) id(walk_pos) += 1;
```

- [ ] **Step 2: Add the matrix display override**

Append to the `display:` list (after `internal_display`):

```yaml
  # The walking pixel is drawn in DISPLAY coordinates - the package's serpentine
  # pixel_mapper translates them. A wrong mapper shows as jumps/zigzags in what
  # must look like a continuous row-by-row sweep. Solid fills can't catch that.
  - id: !extend led_matrix_display
    update_interval: 50ms
    lambda: |-
      it.fill(Color(0, 0, 0));
      if (id(test_step) == 2) {
        if (id(walk_pos) < 256) {
          int p = id(walk_pos);
          it.draw_pixel_at(p % 32, p / 32, Color(255, 255, 255));
        } else if (id(walk_pos) < 346) {
          int f = (id(walk_pos) - 256) / 30;   // 0=R 1=G 2=B, 1.5s each
          // Dim fills: 256 LEDs at full white would brown out USB power
          Color c = f == 0 ? Color(40, 0, 0) : (f == 1 ? Color(0, 40, 0) : Color(0, 0, 40));
          it.fill(c);
        }
      } else if (id(test_step) >= 7) {
        bool all = true;
        for (int i = 0; i < 7; i++)
          if (id(step_results)[i] != 1) all = false;
        it.fill(all ? Color(0, 40, 0) : Color(40, 0, 0));
      }
```

Note: `!extend` replaces scalar keys, so this lambda fully replaces the package's matrix-text lambda — `matrix_text_input` still exists but is unused here. That is intended.

- [ ] **Step 3: Validate + compile**

```bash
$ESPHOME config ed1-hardware-test.yaml && $ESPHOME compile ed1-hardware-test.yaml
```

Expected: valid + compiled.

- [ ] **Step 4: Commit**

```bash
git add ed1-hardware-test.yaml
git commit -m "feat: add LED matrix walk and fill test to hardware test"
```

---

### Task 4: LDR auto-pass + IR decode hooks

**Files:**
- Modify: `ed1-hardware-test.yaml` (add `sensor:` extend block; add `remote_receiver:` extend block)

**Interfaces:**
- Consumes: sensor `light_sensor` (ADC %, package updates it at 5s — we override to 500ms); `ir_receiver`; globals `test_step`, `ldr_baseline`, `last_ir`; script `pass_step`.
- Produces: no new names.

- [ ] **Step 1: Add the LDR override**

```yaml
sensor:
  - id: !extend light_sensor
    update_interval: 500ms
    on_value:
      - lambda: |-
          // Auto-pass when covered: reading drops below 50% of the step-entry
          // baseline. Guard: baseline must be meaningful (>1%) - in a dark room
          // the step falls through to the 15s timeout instead.
          if (id(test_step) == 5 && id(ldr_baseline) > 1.0f && x < id(ldr_baseline) * 0.5f) {
            ESP_LOGI("hwtest", "LDR covered: %.1f < 50%% of %.1f", x, id(ldr_baseline));
            id(pass_step).execute();
          }
```

- [ ] **Step 2: Add the IR decode hooks**

The per-protocol trigger set below is the same one `ed1-smartir-detector.yaml` uses (proven to compile on 2026.6.4 in this repo's CI). `on_raw` is the catch-all for unlisted protocols.

```yaml
remote_receiver:
  id: !extend ir_receiver
  on_nec:
    - lambda: |-
        char buf[40];
        snprintf(buf, sizeof(buf), "NEC %04X/%04X", (unsigned) x.address, (unsigned) x.command);
        id(last_ir) = buf;
        if (id(test_step) == 6) id(pass_step).execute();
  on_samsung:
    - lambda: |-
        char buf[40];
        snprintf(buf, sizeof(buf), "SAMSUNG %08X", (uint32_t) (x.data >> 16));
        id(last_ir) = buf;
        if (id(test_step) == 6) id(pass_step).execute();
  on_lg:
    - lambda: |-
        char buf[40];
        snprintf(buf, sizeof(buf), "LG %08X/%u", (unsigned) x.data, x.nbits);
        id(last_ir) = buf;
        if (id(test_step) == 6) id(pass_step).execute();
  on_sony:
    - lambda: |-
        char buf[40];
        snprintf(buf, sizeof(buf), "SONY %08X/%u", (unsigned) x.data, x.nbits);
        id(last_ir) = buf;
        if (id(test_step) == 6) id(pass_step).execute();
  on_rc5:
    - lambda: |-
        char buf[40];
        snprintf(buf, sizeof(buf), "RC5 %02X/%02X", x.address, x.command);
        id(last_ir) = buf;
        if (id(test_step) == 6) id(pass_step).execute();
  on_raw:
    - lambda: |-
        char buf[40];
        snprintf(buf, sizeof(buf), "RAW %u edges", (unsigned) x.size());
        id(last_ir) = buf;
        if (id(test_step) == 6) id(pass_step).execute();
```

**Fallback:** if `esphome config` rejects `on_raw` (unknown key), delete only the `on_raw:` block — the five protocol triggers remain the pass mechanism and cover essentially all household remotes. Record the removal in the commit message.

- [ ] **Step 3: Validate + compile**

```bash
$ESPHOME config ed1-hardware-test.yaml && $ESPHOME compile ed1-hardware-test.yaml
```

Expected: valid + compiled.

- [ ] **Step 4: Commit**

```bash
git add ed1-hardware-test.yaml
git commit -m "feat: add LDR auto-pass and IR decode hooks to hardware test"
```

---

### Task 5: File header docs + CI compile matrix + lint

**Files:**
- Modify: `ed1-hardware-test.yaml` (expand header comment)
- Modify: `.github/workflows/esphome-check.yml` (compile matrix, ~line 109)

**Interfaces:**
- Consumes: everything above, finished.
- Produces: CI coverage for the new file.

- [ ] **Step 1: Expand the file header**

Replace the short header comment at the top of `ed1-hardware-test.yaml` with:

```yaml
# ==============================================================================
# ED1 Hardware Self-Test - guided on-device test sequence
# ==============================================================================
# Flash this after an ESPHome version bump or packages/ change to verify every
# onboard peripheral in ~2 minutes. Instructions render on the TFT; the touch
# buttons double as the confirmation mechanism (testing them implicitly).
#
#   esphome run ed1-hardware-test.yaml   # USB flash + logs
#
# Steps (auto = pass/fail measured, eyes = confirm with OK / fail with LEFT):
#   0 WiFi     auto - connect within 20s (offline: shows fallback AP, continues)
#   1 Display  eyes - color bars, 1px border, "R" marker top-right
#   2 Matrix   eyes - single pixel sweeps row by row (catches pixel_mapper
#                     errors solid fills can't), then dim R/G/B fills
#   3 Buzzer   eyes - RTTTL scale replayed every 6s
#   4 Touch    auto - press each button as prompted; wrong press = fail
#   5 LDR      auto - cover sensor, pass at <50% of entry baseline (15s limit)
#   6 IR RX    auto - any decoded signal from any remote passes (15s limit)
#   7 Summary  TFT list + matrix green/red + PASS/FAIL lines in the log
#
# Controls: LEFT = fail current step and continue. Hold OK >=1.5s = restart.
# Out of scope: BLE (RAM contention with the matrix; verify from HA),
# stepper/MCP23009 (no hardware attached), IR TX loopback (Rev 1.0 only,
# emitter on GPIO32 - future extension).
# Touch issues on new ESPHome? Rebuild with esp32_touch setup_mode: true and
# compare raw values against the thresholds in packages/buttons.yaml.
# ==============================================================================
```

- [ ] **Step 2: Add to the CI compile matrix**

In `.github/workflows/esphome-check.yml`, in the `compile-configs` matrix, after `- ed1-wokwi.yaml` add:

```yaml
          - ed1-hardware-test.yaml
```

- [ ] **Step 3: Lint + final validate/compile**

```bash
$ESPHOME config ed1-hardware-test.yaml && $ESPHOME compile ed1-hardware-test.yaml
<venv>/bin/pip install yamllint
<venv>/bin/yamllint -d "{extends: default, rules: {line-length: {max: 150}, document-start: disable, truthy: disable, comments: disable}}" ed1-hardware-test.yaml .github/workflows/esphome-check.yml
```

Expected: no yamllint errors (warnings acceptable — CI runs non-strict).

- [ ] **Step 4: Commit**

```bash
git add ed1-hardware-test.yaml .github/workflows/esphome-check.yml
git commit -m "feat: document hardware test and add it to CI compile matrix"
```

---

### Task 6: Flash and run on the connected board (with the user)

**Files:** none (hardware session)

**Interfaces:**
- Consumes: the finished firmware; board on `/dev/cu.SLAB_USBtoUART`.

- [ ] **Step 1: Flash via USB**

```bash
$ESPHOME run ed1-hardware-test.yaml --device /dev/cu.SLAB_USBtoUART
```

Expected: flashes, then log stream starts. Keep logs open for the whole run.

- [ ] **Step 2: Run the guided sequence with the user at the board**

Walk the user through steps 0–7. For each step record PASS/FAIL from the TFT summary AND the `hwtest:` log lines. Specifically watch for:
- Step 0: RSSI value sane (> -80 dBm at desk range).
- Step 2: the walking pixel must sweep continuously row by row — any jump = `pixel_mapper` regression (also invalidates the planned Wokwi matrix diagram).
- Step 4: if any press doesn't register, note which button — threshold drift on 2026.x; capture with a setup_mode build afterwards.
- Step 6: any household remote.

- [ ] **Step 3: Record results**

Append a `## Hardware run YYYY-MM-DD` section with the PASS/FAIL table and any anomalies to `docs/superpowers/specs/2026-07-07-ed1-hardware-test-design.md`, commit:

```bash
git add docs/superpowers/specs/2026-07-07-ed1-hardware-test-design.md
git commit -m "docs: record first hardware test run results"
```

- [ ] **Step 4: Push branch and open PR**

Only with the user's go-ahead:

```bash
git push -u origin feat/hardware-test
gh pr create --title "feat: on-device hardware self-test firmware" --fill
```
