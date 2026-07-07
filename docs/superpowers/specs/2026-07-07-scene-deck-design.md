# ED1 Scene Deck — Design

**Date:** 2026-07-07
**Status:** Approved

## Goal

A "Stream Deck lite" sample config: the ED1's 6 touch buttons trigger Home
Assistant actions, with a live label per button on the TFT display. Configured
entirely from the HA UI — real entity/action pickers, no entity_id copying, no
reflashing to change what buttons do.

## Architecture

Two halves, connected by HA events:

### Firmware: `ed1-scene-deck.sample.yaml` (sample config only, no `packages/` changes)

- **6 label `text` entities** (`mode: text`, `optimistic`, `restore_value`),
  one per button. Users edit them directly on the device page in HA — that's
  the label UX (no ID copying; you're already on the device page). The display
  renders their state live.
- **Button events**: each button press (via `!extend btn_up` … `btn_x`) fires
  `esphome.deck_button` with data `{button: "up", device: "${device_name}"}`.
  The `device` field lets several decks share one blueprint (one automation
  per deck).
- **Local feedback**: press beep (from buttons.yaml) + ~1.5s inverted flash of
  the pressed row. If the HA API is disconnected: error melody instead of the
  event, header shows OFFLINE.
- **Display**: reuses `display-colors` / `display-layout` substitutions.
  Header = connection dot + device name + clock (SNTP). Content = 6 rows in
  physical button order (`^ v < > OK X` ASCII symbols + label). Rows with the
  default "-" label render dimmed. Footer = light level.

### Blueprint: `ha/blueprints/ed1_scene_deck.yaml`

- **Inputs**: `deck_device` (text; must match the ESPHome `device_name`
  substitution) + 6 `action` selectors (full HA action picker UI — scenes,
  scripts, arbitrary sequences).
- **Trigger**: `event: esphome.deck_button` filtered by
  `event_data: {device: <deck_device>}`.
- **Dispatch**: `choose:` on `trigger.event.data.button` → run the
  corresponding input's actions. `mode: queued` so rapid presses don't drop.
- **Import**: via HA's blueprint importer with the raw GitHub URL, documented
  in README.

## Design decision log

- **Blueprint-only action path** (no direct service calls from firmware).
  Chosen for the picker UX; the firmware carries zero dispatch logic.
- **Labels on the device page, not blueprint inputs** — simplification vs. the
  discussed "blueprint pushes labels": ESPHome `text` entities are already
  editable fields on the device page, giving the same no-ID-copying UX with 6
  fewer blueprint inputs and no entity-derivation fragility. The blueprint
  (or any automation) can still `text.set_value` them.
- Events require HA 2024.x+ `esphome.` event convention — standard.

## Smoke test findings (2026-07-07, real board + HA)

- Event → blueprint → action: PASS (1 press = 1 trace = 1 action)
- Label round-trip HA → display: PASS — but HA text fields only commit on
  Enter (documented in README; user's first attempt silently sent nothing)
- Offline press → error melody: PASS
- **`!extend` APPENDS to `on_press`, it does not replace it.** The config
  originally re-added the press beep (assuming replacement), causing a
  duplicate play rejected with "Already playing" per press. Fixed by removing
  the redundant plays; semantics documented in AGENTS.md. NOTE:
  `ed1-message.sample.yaml` re-adds beeps in its extends too (pre-existing,
  same cosmetic warning) — follow-up candidate.

## Verification

- `esphome config` on all `ed1-*.yaml`; `esphome compile` on the new config
  locally (ESPHome 2026.6.4); CI compile matrix gains the config.
- Blueprint: YAML-lint clean; structural review against HA blueprint schema.
  Live behavior (event → action dispatch) needs a real HA instance —
  flagged for a manual smoke test on Ethan's board after merge.

## Out of scope

- Pushing labels from the blueprint (possible later without firmware changes)
- Icons per row (needs glyph additions to shared fonts.yaml — SemVer surface)
- Multi-page decks
