# Remote Packages Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make all `packages/*.yaml` consumable as ESPHome remote packages (`github://glifocat/ed1-hoas/...@v1.0.0`) by removing `!secret` lookups, then document and release v1.0.0.

**Architecture:** Replace `!secret` lookups in `packages/core.yaml` and `packages/mqtt.yaml` with `${...}` substitutions; consuming configs (our samples and remote consumers alike) inject credentials via their `substitutions:` block, where `!secret` is allowed. Spec: `docs/superpowers/specs/2026-07-07-remote-packages-design.md`.

**Tech Stack:** ESPHome 2026.6.4, GitHub Actions CI, `gh` CLI.

## Global Constraints

- ESPHome pinned at `2026.6.4` in CI (`.github/workflows/esphome-check.yml`); `min_version: 2026.1.0` in `packages/core.yaml`
- No `!secret` anywhere under `packages/` after this change (ESPHome forbids it in remote packages)
- Substitution names: `wifi_ssid`, `wifi_password`, `fallback_ap_password`, `api_encryption_key`, `ota_password`, `mqtt_broker`, `mqtt_user`, `mqtt_password` — no credential defaults in packages
- The secret KEY names in `secrets.yaml` are unchanged (`api_encryption_key_full` stays `api_encryption_key_full`; only the substitution is named `api_encryption_key`)
- `ed1-wokwi.yaml` does NOT include `core.yaml` (it inlines a secret-free core) — do not touch it
- `ed1-smartir-bridge.yaml` is untracked: edit locally so it keeps compiling, but never `git add` it
- All outputs in English; commits use `feat:`/`docs:` prefixes

---

### Task 1: Refactor packages to substitutions and update all consuming configs

**Files:**
- Modify: `packages/core.yaml:40-55` (api/ota/wifi blocks) and `:6-14` (header comment)
- Modify: `packages/mqtt.yaml:16-19` (mqtt block) and `:5-9` (header comment)
- Modify (add substitutions): `ed1-gpio-test.yaml`, `ed1-hardware-test.yaml`, `ed1-message.sample.yaml`, `ed1-mqtt.sample.yaml`, `ed1-robot-demo.yaml`, `ed1-smartir-detector-rev1.yaml`, `ed1-smartir-detector.yaml`, `ed1-status.sample.yaml`, `ed1-stepper-test.yaml`, and (local-only, no commit) `ed1-smartir-bridge.yaml`

**Interfaces:**
- Produces: packages requiring substitutions `wifi_ssid`, `wifi_password`, `fallback_ap_password`, `api_encryption_key`, `ota_password` (core) and `mqtt_broker`, `mqtt_user`, `mqtt_password` (mqtt). Tasks 2–3 rely on these exact names.

- [ ] **Step 1: Create a local `secrets.yaml` check baseline (failing-test equivalent)**

Verify current state validates, so any later failure is caused by this change:

Run: `esphome config ed1-message.sample.yaml >/dev/null && echo BASELINE-OK`
Expected: `BASELINE-OK`

- [ ] **Step 2: Edit `packages/core.yaml`**

Replace the api/ota/wifi credential lines:

```yaml
api:
  encryption:
    key: ${api_encryption_key}

ota:
  - platform: esphome
    password: ${ota_password}

wifi:
  ssid: ${wifi_ssid}
  password: ${wifi_password}
  power_save_mode: ${wifi_power_save}
  fast_connect: true
  ap:
    ssid: ${ap_ssid}
    password: ${fallback_ap_password}
```

Update the header's "Required substitutions" list to add:

```
#   - wifi_ssid / wifi_password: WiFi credentials
#   - fallback_ap_password: Rescue AP password
#   - api_encryption_key: HA API encryption key (base64)
#   - ota_password: OTA update password
#   (Packages cannot use !secret — consumers inject these via substitutions,
#    typically `wifi_ssid: !secret wifi_ssid` in the device config.)
```

- [ ] **Step 3: Edit `packages/mqtt.yaml`**

```yaml
mqtt:
  broker: ${mqtt_broker}
  username: ${mqtt_user}
  password: ${mqtt_password}
```

Update header: "Required secrets" becomes "Required substitutions: mqtt_broker, mqtt_user, mqtt_password (inject via `mqtt_broker: !secret mqtt_broker` etc.)".

- [ ] **Step 4: Verify validation now fails (undefined substitution)**

Run: `esphome config ed1-message.sample.yaml 2>&1 | tail -3`
Expected: FAIL mentioning undefined substitution (e.g. `api_encryption_key`)

- [ ] **Step 5: Add credential substitutions to every consuming config**

Append to the `substitutions:` block of each of the 10 files listed above:

```yaml
  # Credentials injected into packages (remote packages cannot use !secret)
  wifi_ssid: !secret wifi_ssid
  wifi_password: !secret wifi_password
  fallback_ap_password: !secret fallback_ap_password
  api_encryption_key: !secret api_encryption_key_full
  ota_password: !secret ota_password
```

`ed1-mqtt.sample.yaml` additionally gets:

```yaml
  mqtt_broker: !secret mqtt_broker
  mqtt_user: !secret mqtt_user
  mqtt_password: !secret mqtt_password
```

- [ ] **Step 6: Validate all configs**

Run: `for f in ed1-*.yaml; do esphome config "$f" >/dev/null 2>&1 && echo "OK  $f" || echo "FAIL $f"; done`
Expected: `OK` for all files

- [ ] **Step 7: Confirm no `!secret` remains in packages**

Run: `grep -rn '!secret' packages/ && echo LEAK || echo CLEAN`
Expected: `CLEAN`

- [ ] **Step 8: Commit (excluding ed1-smartir-bridge.yaml)**

```bash
git add packages/core.yaml packages/mqtt.yaml ed1-gpio-test.yaml ed1-hardware-test.yaml ed1-message.sample.yaml ed1-mqtt.sample.yaml ed1-robot-demo.yaml ed1-smartir-detector-rev1.yaml ed1-smartir-detector.yaml ed1-status.sample.yaml ed1-stepper-test.yaml
git commit -m "feat: inject credentials via substitutions so packages work remotely"
```

### Task 2: Verify remote consumption from the pushed branch

**Files:**
- Create (scratchpad, NOT in repo): `<scratchpad>/remote-consumer/ed1-remote-test.yaml`

**Interfaces:**
- Consumes: substitution names produced by Task 1.
- Produces: confirmation that cross-package includes and `fonts.yaml` font paths resolve remotely; README claims in Task 3 depend on this result.

- [ ] **Step 1: Push the branch**

```bash
git push -u origin feat/remote-packages
```

- [ ] **Step 2: Write the consumer config in the scratchpad**

```yaml
substitutions:
  device_name: ed1-remote-test
  friendly_name: ED1 Remote Test
  ap_ssid: ED1-Remote-Rescue
  wifi_ssid: "test-network"
  wifi_password: "test-password"
  fallback_ap_password: "test-fallback"
  api_encryption_key: "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
  ota_password: "test-ota-password"

packages:
  ed1:
    url: https://github.com/glifocat/ed1-hoas
    ref: feat/remote-packages
    refresh: 0s
    files:
      - packages/display-colors.yaml
      - packages/display-layout.yaml
      - packages/core.yaml
      - packages/hardware.yaml
      - packages/display.yaml
      - packages/fonts.yaml
      - packages/buttons.yaml
      - packages/sensors.yaml
```

- [ ] **Step 3: Validate, then compile the consumer config**

Run (from the scratchpad dir): `esphome config ed1-remote-test.yaml >/dev/null && echo CONFIG-OK && esphome compile ed1-remote-test.yaml 2>&1 | tail -3`
Expected: `CONFIG-OK`, then `Successfully compiled program.` — proving remote includes AND font files resolve. If fonts fail: remove `fonts.yaml`+`display.yaml` from files list, re-run; if that passes, document fonts as local-only in Task 3's README section.

### Task 3: README "Use as remote packages" section

**Files:**
- Modify: `README.md` (new section after "Quick Start", before "Prerequisites")

**Interfaces:**
- Consumes: verified consumer config shape from Task 2.

- [ ] **Step 1: Add the section**

```markdown
## Use as Remote Packages

You don't need to clone this repo — ESPHome can pull the packages straight
from GitHub. Credentials are injected via substitutions (remote packages
cannot read your `secrets.yaml` directly):

​```yaml
substitutions:
  device_name: ed1-livingroom
  friendly_name: ED1 Living Room
  ap_ssid: ED1-LivingRoom-Rescue
  # Credentials injected into the packages
  wifi_ssid: !secret wifi_ssid
  wifi_password: !secret wifi_password
  fallback_ap_password: !secret fallback_ap_password
  api_encryption_key: !secret api_encryption_key
  ota_password: !secret ota_password

packages:
  ed1:
    url: https://github.com/glifocat/ed1-hoas
    ref: v1.0.0  # pin a release tag (or use main to track latest)
    refresh: 1d
    files:
      - packages/display-colors.yaml
      - packages/display-layout.yaml
      - packages/core.yaml
      - packages/hardware.yaml
      - packages/display.yaml
      - packages/fonts.yaml
      - packages/buttons.yaml
      - packages/sensors.yaml
​```

Pin `ref:` to a release tag for reproducible builds; releases follow SemVer,
so substitution or ID renames only happen in major versions. Add any other
package from `packages/` to the `files:` list the same way (`mqtt.yaml`
additionally needs `mqtt_broker`, `mqtt_user`, `mqtt_password`
substitutions).
​```

(Adjust per Task 2 findings if fonts turned out local-only.)

- [ ] **Step 2: Validate markdown renders (spot-check) and commit**

```bash
git add README.md
git commit -m "docs: document remote packages usage"
```

### Task 4: Open PR, monitor CI, merge

- [ ] **Step 1: Push and open the PR with metadata**

```bash
git push
gh pr create --title "feat: remote packages support (github:// refs)" \
  --body "<summary + verification evidence>" \
  --label enhancement --assignee glifocat
```
(Check available labels/milestones with `gh label list` / `gh api repos/{owner}/{repo}/milestones` and apply what exists.)

- [ ] **Step 2: Watch CI (validate + 7-config compile matrix) until green**

Run: `gh pr checks --watch`
Expected: all checks pass

- [ ] **Step 3: Merge (squash, per repo history) and pull main**

```bash
gh pr merge --squash --delete-branch
git checkout main && git pull
```

### Task 5: Tag v1.0.0 and create the GitHub Release

- [ ] **Step 1: Tag merged main**

```bash
git tag v1.0.0 && git push origin v1.0.0
```

- [ ] **Step 2: Create the release**

```bash
gh release create v1.0.0 --title "v1.0.0 — first stable release" \
  --notes "<notes: remote packages usage, SemVer policy, hardware support summary>"
```

- [ ] **Step 3: Re-verify consumer config against the tag**

Change `ref: feat/remote-packages` → `ref: v1.0.0` in the scratchpad consumer config, re-run `esphome config`.
Expected: `CONFIG-OK`
