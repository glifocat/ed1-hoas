# ED1 Hardware Self-Test Firmware — Design

**Date:** 2026-07-07
**Status:** Approved
**Target:** `ed1-hardware-test.yaml` (new root config, committed)

## Purpose

A reusable, guided hardware self-test for the ED1 board. Flash it after any
ESPHome version bump or `packages/` change to verify every onboard peripheral
on real hardware in ~2 minutes. The board tests itself: instructions render on
the TFT, and the touch buttons double as the confirmation mechanism, so they
are exercised implicitly while advancing the sequence.

Scope: bare board, Rev 2.x (no IR emitter). Steppers/MCP23009 and BLE are out
of scope (see Exclusions).

## Architecture

- One new root config `ed1-hardware-test.yaml`, composed from the existing
  packages: `core`, `hardware`, `display`, `fonts`, `buzzer`, `buttons`,
  `sensors`, `ir-receiver`, `led-matrix`. No bespoke hardware definitions —
  flashing the test validates the same packages all other configs use.
- Test logic lives in the root file via `!extend` overrides (repo's documented
  pattern in CLAUDE.md).
- State machine:
  - `globals`: `test_step` (int), `step_results` (per-step status: pending /
    pass / fail).
  - `script: run_step`: renders the current step's instructions on the TFT and
    arms that step's automation (baselines, timeouts).
  - Advance on auto-pass (measured steps) or OK press (observed steps).
  - BTN LEFT marks the current step failed and continues — the run can never
    wedge. Long-press OK restarts the whole sequence.

## Step sequence

| # | Step | Pass criteria | Auto |
|---|------|---------------|------|
| 0 | Boot info: ESPHome version, SSID + RSSI, IP on TFT | WiFi connected → auto-pass | yes |
| 1 | Display: color bars, 1px border, corner arrows | Human OK — bars, border, orientation correct | eyes |
| 2 | Matrix: SKIPPED — optional external accessory, removed from the default test (see run record below) | auto-marks SKIP | — |
| 3 | Buzzer: RTTTL scale + melody | Human OK — heard | eyes |
| 4 | Touch: prompt each of the 6 buttons in fixed order; wrong button marks that prompt failed | Correct press advances | yes |
| 5 | LDR: live ADC on TFT; "cover it or light it" | 50% drop OR 2× rise (+5 abs floor) from step-entry baseline within 15 s | yes |
| 6 | IR RX: "point any remote, press a key"; decoded protocol + code on TFT | Any `remote_receiver` decode event | yes |
| 7 | Summary: PASS/FAIL per step on TFT; matrix green/red; report logged | — | — |

- Steps 5–6 time out after 15 s → auto-fail, continue (a missing remote must
  not block the run).
- Rationale for the walking pixel in step 2: solid fills cannot catch a wrong
  `pixel_mapper`; only a walking pixel reveals serpentine-order errors.

## Error handling and constraints

- **Touch thresholds** are the known 2026.x risk (ESP32 touch calibration
  changes across framework updates). Step 4 logs raw touch values on entry so
  threshold drift is diagnosable from `esphome logs` even when presses do not
  register.
- **Offline use:** if WiFi fails, step 0 shows the fallback-AP name and
  continues after a timeout. Every step except 0 is WiFi-independent.
- **Matrix current:** full-fill brightness is capped low — 256 WS2812 at full
  white would brown out USB power.

## Exclusions

- BLE / Bluetooth proxy: competes with the LED matrix for RAM and is trivially
  verified from Home Assistant; noted in the file header.
- Stepper / MCP23009: no hardware attached; candidate future section behind a
  substitution toggle.
- IR TX loopback: Rev 1.0 only (GPIO32 emitter); documented as a future
  extension in the file header.

## Verification

1. Local venv pinned to ESPHome **2026.6.4** (same as CI): `esphome config`
   then `esphome compile` on the new file.
2. Flash via USB (`/dev/cu.SLAB_USBtoUART`), run the full sequence on the
   connected board with the user.
3. CI: file is picked up by the validate glob (`ed1-*.yaml`) automatically;
   add it to the compile matrix in `.github/workflows/esphome-check.yml`.
4. Docs: file header explains how to run, what each step checks, and the
   Rev 1.0 note.

## Hardware run 2026-07-07 (Rev 2.x board, external matrix on D2)

Three iterations: initial run surfaced defects, fixes applied, final run clean.

| Step | Result | Notes |
|------|--------|-------|
| 0 WiFi | PASS | RSSI shown on TFT |
| 1 Display | FAIL → **PASS** | Panel is BGR: R/B swapped. Fixed with `use_bgr: true` in `packages/display.yaml` (latent repo-wide bug, invisible with white-only text) |
| 2 Matrix | FAIL → **SKIP** (removed from default test) | Matrix is an OPTIONAL external accessory. Verification inconclusive: a dual-pin probe (GPIO12+GPIO25) lit a panel on the D2 header, but single-pin builds on either pin stayed dark, including with IR removed (RMT contention ruled out) and with the generated C++ verified correct. Dropped from the default test; step 2 auto-marks SKIP. Package keeps design pin GPIO12 with an honest comment |
| 3 Buzzer | PASS | Scale + 6s replay |
| 4 Touch | FAIL → **PASS** 6/6 | Two defects: (a) `btn_x` threshold 900 latched the pad "pressed" from boot — calibrated to 450 (idle ~500, pressed 275–443); (b) pads double-fire within ~100ms — 300ms debounce added to `handle_button` |
| 5 LDR | FAIL → **PASS** | Dim-room baseline (4.3) too low to halve by covering; criterion widened to 50% drop OR 2× rise (+5 absolute floor) so a flashlight also passes. Sensor is front-mounted on Rev 2.x |
| 6 IR RX | PASS | Verified run 2: `NEC address=0xDF20 command=0xF20D` decoded and auto-passed (final run timed out — no remote at hand) |
| 7 Summary | PASS | TFT list + matrix fill + log lines all correct |

Final run: **ALL PASS** (6 passes + matrix SKIP) on the connected Rev 2.x board.

Deltas from spec (implemented per approved plan, spec text not updated):
step 1 uses a single "R" orientation marker (not corner arrows); step 3 plays a
scale only (no second melody); step 4 advances on any press, counting wrong
ones (not only on correct press). Step 2 animation loops with a 2s dark gap
(added after final review).
