# Pending workflow update

`esphome-check.yml` in this folder is the updated version of
`.github/workflows/esphome-check.yml`. It was staged here because the
automation that prepared this branch does not have the GitHub `workflow`
scope required to modify files under `.github/workflows/`.

To apply it (requires a user with workflow permissions):

```bash
git mv .github/workflows-update/esphome-check.yml .github/workflows/esphome-check.yml
git rm .github/workflows-update/README.md
git commit -m "ci: bump ESPHome to 2026.6.4, widen coverage, cache builds"
```

Changes relative to the current workflow:

- Pin ESPHome 2026.6.4 (was 2025.2.0) and Python 3.13
- Validate all `ed1-*.yaml` configs instead of only the three samples
- Add `ed1-robot-demo.yaml`, `ed1-smartir-detector.yaml`, and `ed1-wokwi.yaml` to the compile matrix
- Cache PlatformIO/ESPHome build dirs and raise the compile timeout to 30 min
  (Arduino is built as an ESP-IDF component since ESPHome 2025.10, so cold
  builds compile the entire framework)
- Weekly version check now compares the pinned CI version against PyPI, so it
  catches minor releases too (it previously only compared the README badge
  major version); the unused version-file artifact steps were removed
- LF line endings, matching the repo-wide normalization

Note: `packages/core.yaml` on this branch sets `min_version: 2026.1.0`, so the
validate job will fail until this workflow update (which bumps the pinned
ESPHome past that floor) is applied.
