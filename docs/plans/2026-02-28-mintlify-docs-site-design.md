# Mintlify Documentation Site Design

## Summary

Convert the existing `docs/` folder into a Mintlify documentation site for the ED1 Citilab board. Launch with current content, structured to accommodate future expansion (MicroBlocks, Arduino, community projects, Spanish localization).

## Decisions

- **Location**: Same repo, `docs/` folder (Mintlify deploys from subdirectory)
- **Language**: English only at launch; structure supports adding Spanish later
- **File format**: `.mdx` for Mintlify features, but keep content as plain Markdown for GitHub readability. Minimize use of JSX components.
- **Revision handling**: Inline callouts where behavior differs per revision. Summary table on hardware overview page for identifying your board.
- **Scope**: Existing 5 docs + 1 new introduction page. No new content beyond what exists.

## Site Structure

```
docs/
├── docs.json                         # Mintlify site configuration
├── .mintignore                       # Exclude KiCad, datasheets, plans
├── introduction.mdx                  # NEW: What is the ED1? (extracted from README)
├── getting-started.mdx               # NEW: Quick start (extracted from README)
├── hardware/
│   ├── overview.mdx                  # From HARDWARE.md
│   └── pinout.mdx                    # From PINOUT.md
├── esphome/
│   ├── configuration.mdx             # From ESPHOME.md
│   ├── home-assistant.mdx            # From HOME-ASSISTANT.md
│   └── smartir.mdx                   # From SMARTIR.md (translated to English)
├── images/                           # Existing board images (unchanged)
├── datasheets/                       # Ignored by Mintlify
├── plans/                            # Ignored by Mintlify
└── ED1 2.3/                          # Ignored by Mintlify
```

## Navigation (docs.json)

```json
{
  "navigation": {
    "tabs": [],
    "groups": [
      {
        "group": "Getting started",
        "pages": [
          "introduction",
          "getting-started"
        ]
      },
      {
        "group": "Hardware",
        "pages": [
          "hardware/overview",
          "hardware/pinout"
        ]
      },
      {
        "group": "ESPHome",
        "pages": [
          "esphome/configuration",
          "esphome/home-assistant",
          "esphome/smartir"
        ]
      }
    ]
  }
}
```

## .mintignore

```
ED1 2.3/
datasheets/
plans/
.DS_Store
.agents/
.claude/
.kilocode/
skills-lock.json
ED1 Stepper Motor.ubl
```

## Content Changes

### New pages

1. **introduction.mdx** - What is the ED1 board, photo, key features, link to Citilab. Extracted from README intro section.
2. **getting-started.mdx** - Prerequisites, clone, configure secrets, flash, add to HA. Extracted from README Quick Start section.

### Converted pages (minimal changes)

3. **hardware/overview.mdx** - From HARDWARE.md. Add frontmatter. Content unchanged.
4. **hardware/pinout.mdx** - From PINOUT.md. Add frontmatter. Content unchanged.
5. **esphome/configuration.mdx** - From ESPHOME.md. Add frontmatter. Content unchanged.
6. **esphome/home-assistant.mdx** - From HOME-ASSISTANT.md. Add frontmatter. Content unchanged.
7. **esphome/smartir.mdx** - From SMARTIR.md. Translate to English. Add frontmatter.

### Frontmatter format (all pages)

```yaml
---
title: "Page Title"
description: "One-line description for SEO and navigation."
---
```

## Future Expansion (not implemented now)

These groups can be added later without restructuring:

- **MicroBlocks** - `microblocks/` directory
- **Arduino** - `arduino/` directory
- **Community** - `community/` directory (projects, tutorials)
- **Spanish** - Mintlify localization feature

## What This Does NOT Change

- README.md continues linking to `docs/*.md` for GitHub readers
- KiCad files, datasheets, and images stay where they are
- No changes to ESPHome configs or packages
