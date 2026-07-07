# Remote Packages Support — Design

**Date:** 2026-07-07
**Status:** Approved

## Goal

Let anyone use the ED1 packages directly from GitHub via ESPHome remote packages
(`github://glifocat/ed1-hoas/packages/<file>.yaml@<tag>`), without cloning the
repo. Establish release tags so consumers can pin stable versions.

## Constraint driving the design

ESPHome forbids `!secret` lookups inside remote packages — secrets resolve
against the consumer's `secrets.yaml`, which a remote package cannot assume
anything about. Remote packages must receive credentials via substitutions
provided by the consuming config.

Today, two packages violate this:

- `packages/core.yaml`: `api_encryption_key_full`, `ota_password`, `wifi_ssid`,
  `wifi_password`, `fallback_ap_password`
- `packages/mqtt.yaml`: `mqtt_broker`, `mqtt_user`, `mqtt_password`

## Design

### 1. Package refactor (substitution injection)

Replace every `!secret` in `packages/core.yaml` and `packages/mqtt.yaml` with a
substitution of the same conceptual name:

| Package | Substitution | Replaces |
| ------- | ------------ | -------- |
| core.yaml | `${wifi_ssid}` | `!secret wifi_ssid` |
| core.yaml | `${wifi_password}` | `!secret wifi_password` |
| core.yaml | `${fallback_ap_password}` | `!secret fallback_ap_password` |
| core.yaml | `${api_encryption_key}` | `!secret api_encryption_key_full` |
| core.yaml | `${ota_password}` | `!secret ota_password` |
| mqtt.yaml | `${mqtt_broker}` | `!secret mqtt_broker` |
| mqtt.yaml | `${mqtt_user}` | `!secret mqtt_user` |
| mqtt.yaml | `${mqtt_password}` | `!secret mqtt_password` |

No defaults for credentials: a missing substitution fails validation with a
clear "undefined substitution" error, which is the desired behavior. Package
header comments document the new required substitutions.

### 2. Sample config updates

Every `ed1-*.yaml` that includes `core.yaml` (all of them) adds to its
existing `substitutions:` block:

```yaml
substitutions:
  # Credentials injected into packages (remote packages cannot use !secret)
  wifi_ssid: !secret wifi_ssid
  wifi_password: !secret wifi_password
  fallback_ap_password: !secret fallback_ap_password
  api_encryption_key: !secret api_encryption_key_full
  ota_password: !secret ota_password
```

`ed1-mqtt.sample.yaml` additionally maps the three MQTT secrets. Behavior for
existing clone-and-flash users is unchanged: same `secrets.yaml`, same keys.

### 3. README: "Use as remote packages" section

Minimal consumer example (substitutions + `github://` refs pinned to
`v1.0.0`), plus notes on `refresh:` and pinning tags vs tracking `@main`.

### 4. Release process

After merge: tag `v1.0.0`, publish a GitHub Release. SemVer from here on —
renaming substitutions, changing component IDs, or removing packages is a
major bump; new packages/features are minor.

## Verification

- `esphome config` on every `ed1-*.yaml` (CI validate step, run locally first)
- `esphome compile` on one representative sample locally; CI compiles the
  full matrix
- Consumer-style test config (scratchpad, not committed) pointing at the PR
  branch via `@feat/remote-packages`, compiled locally, to verify:
  - cross-package includes resolve inside ESPHome's clone of the repo
  - `fonts.yaml` local font-file paths resolve remotely
  - **Fallback if fonts fail remotely:** document `fonts.yaml` (and its
    dependents) as local-only in the README section

## Out of scope

- CI job consuming packages remotely (fetches `main`, not the PR branch, so
  it can't test PR changes; revisit if remote consumers report breakage)
- `ed1-smartir-bridge.yaml` (untracked; updated locally to keep compiling but
  not committed in this PR)
- CLAUDE.md drift fix ships as a separate docs PR
