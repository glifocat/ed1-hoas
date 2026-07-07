# ED1 Scene Deck Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `ed1-scene-deck.sample.yaml` (6-button HA action deck with live display labels) plus the companion HA blueprint `ha/blueprints/ed1_scene_deck.yaml`.

**Architecture:** Firmware fires `esphome.deck_button` events and renders 6 label text entities; the blueprint provides action pickers and dispatches events to actions. Spec: `docs/superpowers/specs/2026-07-07-scene-deck-design.md`.

**Tech Stack:** ESPHome 2026.6.4 (CI pin), HA blueprint schema (automation domain).

## Global Constraints

- No changes under `packages/` (remote-package SemVer surface)
- No `!secret` outside the device config's `substitutions:` block
- `!extend` on a button REPLACES its `on_press` — re-add the beep
- Button IDs from `packages/buttons.yaml`: `btn_up`, `btn_down`, `btn_left`, `btn_right`, `btn_ok`, `btn_x`
- Event data must be static per button (no lambdas in `homeassistant.event` data)
- New config goes into the CI compile matrix in `.github/workflows/esphome-check.yml`

---

### Task 1: Firmware config `ed1-scene-deck.sample.yaml`

**Files:** Create `ed1-scene-deck.sample.yaml`

**Interfaces:**
- Produces: HA event `esphome.deck_button` with data `{button: up|down|left|right|ok|x, device: ${device_name}}`; 6 text entities named `${friendly_name} <Btn> Label`.

- [ ] **Step 1:** Write the config: standard substitutions + credential block (as in `ed1-message.sample.yaml`); packages colors/layout/core/hardware/display/fonts/buzzer/buttons/sensors; `api` connect/disconnect tracking into `ha_connected` global; SNTP time (Europe/Madrid); globals `boot_complete`, `ha_connected`, `flash_row` (int, -1), `flash_until` (uint32); 6 template `text` entities (optimistic, restore_value, initial `-`, max_length 18); 6 `!extend btn_*` blocks each doing: beep + set flash globals + `if api.connected` → `homeassistant.event` (static data) else error rtttl; display lambda: boot splash → header (dot/OFFLINE/clock) → 6 rows (`^ v < > OK X` + label, dimmed when `-`, inverted while flashing) → footer light %.
- [ ] **Step 2:** `esphome config ed1-scene-deck.sample.yaml` → exit 0.
- [ ] **Step 3:** `esphome compile ed1-scene-deck.sample.yaml` → `Successfully compiled program.`
- [ ] **Step 4:** Commit `feat: add scene deck sample config`.

### Task 2: Blueprint `ha/blueprints/ed1_scene_deck.yaml`

**Files:** Create `ha/blueprints/ed1_scene_deck.yaml`

**Interfaces:**
- Consumes: the `esphome.deck_button` event shape from Task 1 (exact data keys).

- [ ] **Step 1:** Write blueprint: `domain: automation`; `source_url` to the repo blob; inputs `deck_device` (text selector) + 6 `*_action` (action selector, default `[]`); trigger `event_type: esphome.deck_button` with `event_data: {device: !input deck_device}`; action `choose:` with template shorthand conditions on `trigger.event.data.button`; `mode: queued`, `max: 10`.
- [ ] **Step 2:** Validate YAML parses (`python -c "import yaml, sys; yaml.safe_load(open('ha/blueprints/ed1_scene_deck.yaml'))"` — note `!input` needs a permissive loader: use `yaml.add_multi_constructor` shim or yamllint instead).
- [ ] **Step 3:** Commit `feat: add HA blueprint for the scene deck`.

### Task 3: Docs + CI

**Files:** Modify `README.md` (sample table + blueprint import note), `AGENTS.md` (sample list), `.github/workflows/esphome-check.yml` (compile matrix)

- [ ] **Step 1:** README sample table row + a short "Scene deck setup" note (flash → import blueprint URL → create automation → edit labels on device page). AGENTS.md sample list row. CI matrix entry `ed1-scene-deck.sample.yaml`.
- [ ] **Step 2:** `esphome config` all `ed1-*.yaml` → all OK; yamllint on changed files.
- [ ] **Step 3:** Commit `docs: document scene deck; add to CI matrix`.

### Task 4: PR

- [ ] **Step 1:** Push, `gh pr create` (label `enhancement`, assignee glifocat), body with verification evidence + blueprint import URL.
- [ ] **Step 2:** Watch CI to green. STOP — merge is Ethan's call (real-device smoke test pending).
