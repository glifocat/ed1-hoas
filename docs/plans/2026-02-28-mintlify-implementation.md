# Mintlify Documentation Site Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Convert the existing `docs/` folder into a Mintlify documentation site for the ED1 Citilab board.

**Architecture:** Mintlify site lives inside `docs/` alongside existing KiCad/datasheet files (excluded via `.mintignore`). Existing Markdown docs are converted to MDX with frontmatter, reorganized into `hardware/` and `esphome/` subdirectories. Two new pages (introduction, getting-started) are extracted from README content.

**Tech Stack:** Mintlify, MDX, Node.js (mint CLI for local validation)

**Design doc:** `docs/plans/2026-02-28-mintlify-docs-site-design.md`

---

### Task 1: Create branch and install Mintlify CLI

**Files:**
- None (setup only)

**Step 1: Create feature branch**

```bash
git checkout -b feature/mintlify-docs
```

**Step 2: Install Mintlify CLI globally**

```bash
npm i -g mint
```

**Step 3: Verify installation**

Run: `mint --version`
Expected: Version number printed (e.g., `4.x.x`)

---

### Task 2: Create Mintlify scaffolding (docs.json + .mintignore)

**Files:**
- Create: `docs/docs.json`
- Create: `docs/.mintignore`

**Step 1: Create docs.json**

```json
{
  "$schema": "https://mintlify.com/docs.json",
  "theme": "mint",
  "name": "ED1 Citilab",
  "description": "Documentation for integrating the ED1 Citilab ESP32 educational board with Home Assistant via ESPHome.",
  "colors": {
    "primary": "#10B981"
  },
  "logo": {
    "light": "/images/ed1-board.png",
    "dark": "/images/ed1-board.png"
  },
  "favicon": "/images/ed1-board.png",
  "navigation": {
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
  },
  "navbar": {
    "links": [
      {
        "label": "GitHub",
        "href": "https://github.com/glifocat/ed1-hoas"
      }
    ]
  },
  "footer": {
    "socials": {
      "github": "https://github.com/glifocat/ed1-hoas"
    }
  }
}
```

**Step 2: Create .mintignore**

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
HARDWARE.md
ESPHOME.md
HOME-ASSISTANT.md
PINOUT.md
SMARTIR.md
```

Note: The old `.md` files are excluded from Mintlify since their content will live in the new `.mdx` files. They remain in the repo for backwards compatibility with existing README links until Task 9.

**Step 3: Create subdirectories**

```bash
mkdir -p docs/hardware docs/esphome
```

**Step 4: Commit scaffolding**

```bash
git add docs/docs.json docs/.mintignore
git commit -m "feat(docs): add Mintlify scaffolding (docs.json + .mintignore)"
```

---

### Task 3: Create introduction.mdx

**Files:**
- Create: `docs/introduction.mdx`

**Step 1: Write introduction.mdx**

Extract content from the README's intro, features, and board image sections. Write as a landing page for the documentation site.

Content should include:
- Frontmatter with `title: "ED1 Citilab Board"` and `description`
- Board image (`/images/ed1-board.png`)
- Front/back angle photos
- Features list (built-in hardware + expansion support)
- Links to Citilab, ESPHome, Home Assistant
- Brief mention of board revisions (1.0 vs 2.3) with link to hardware overview

Source: `README.md` lines 1-46

**Step 2: Validate page renders**

Run: `cd docs && mint dev`
Expected: Page renders at `http://localhost:3000/introduction` with board image and feature list.
Stop the server after checking.

**Step 3: Commit**

```bash
git add docs/introduction.mdx
git commit -m "feat(docs): add introduction page"
```

---

### Task 4: Create getting-started.mdx

**Files:**
- Create: `docs/getting-started.mdx`

**Step 1: Write getting-started.mdx**

Extract from README's Prerequisites and Quick Start sections (lines 39-87).

Content should include:
- Frontmatter with `title: "Getting started"` and `description`
- Prerequisites list (Home Assistant, ESPHome, ED1 board, USB cable, CP210x driver)
- Clone repo step
- Configure secrets step (with code blocks)
- Sample config selection (list of available YAML files with descriptions)
- Flash device step
- Add to Home Assistant step
- Note about core packages working on both revisions

Source: `README.md` lines 39-87

**Step 2: Validate page renders**

Run: `cd docs && mint dev`
Expected: Page renders at `http://localhost:3000/getting-started` with steps.
Stop the server after checking.

**Step 3: Commit**

```bash
git add docs/getting-started.mdx
git commit -m "feat(docs): add getting started page"
```

---

### Task 5: Convert HARDWARE.md to hardware/overview.mdx

**Files:**
- Create: `docs/hardware/overview.mdx`
- Source: `docs/HARDWARE.md`

**Step 1: Create hardware/overview.mdx**

- Add frontmatter: `title: "Hardware reference"`, `description: "Board specifications, components, power system, and revision differences for the ED1 Citilab board."`
- Copy all content from `HARDWARE.md` after the H1 heading
- Remove the H1 heading (Mintlify uses frontmatter title)
- Fix image paths if any (currently none in this file)
- Fix internal links: `datasheets/` links should point to the GitHub repo since datasheets are mintignored

**Step 2: Commit**

```bash
git add docs/hardware/overview.mdx
git commit -m "feat(docs): convert hardware reference to Mintlify"
```

---

### Task 6: Convert PINOUT.md to hardware/pinout.mdx

**Files:**
- Create: `docs/hardware/pinout.mdx`
- Source: `docs/PINOUT.md`

**Step 1: Create hardware/pinout.mdx**

- Add frontmatter: `title: "GPIO pinout"`, `description: "GPIO assignments, bus configurations, and connector pinouts for the ED1 board."`
- Copy all content from `PINOUT.md` after the H1 heading
- Remove the H1 heading

**Step 2: Commit**

```bash
git add docs/hardware/pinout.mdx
git commit -m "feat(docs): convert GPIO pinout to Mintlify"
```

---

### Task 7: Convert ESPHOME.md to esphome/configuration.mdx

**Files:**
- Create: `docs/esphome/configuration.mdx`
- Source: `docs/ESPHOME.md`

**Step 1: Create esphome/configuration.mdx**

- Add frontmatter: `title: "ESPHome configuration"`, `description: "Package system, component reference, and customization guide for the ED1 ESPHome integration."`
- Copy all content from `ESPHOME.md` after the H1 heading
- Remove the H1 heading
- Fix any internal links (e.g., references to other docs should use Mintlify paths like `/hardware/pinout` instead of `PINOUT.md`)

**Step 2: Commit**

```bash
git add docs/esphome/configuration.mdx
git commit -m "feat(docs): convert ESPHome configuration guide to Mintlify"
```

---

### Task 8: Convert HOME-ASSISTANT.md to esphome/home-assistant.mdx

**Files:**
- Create: `docs/esphome/home-assistant.mdx`
- Source: `docs/HOME-ASSISTANT.md`

**Step 1: Create esphome/home-assistant.mdx**

- Add frontmatter: `title: "Home Assistant integration"`, `description: "Available entities, dashboard examples, automation recipes, and Bluetooth proxy setup for the ED1 board."`
- Copy all content from `HOME-ASSISTANT.md` after the H1 heading
- Remove the H1 heading
- Fix internal links: `ESPHOME.md#10-ir-receiver` becomes `/esphome/configuration` (anchor may change)

**Step 2: Commit**

```bash
git add docs/esphome/home-assistant.mdx
git commit -m "feat(docs): convert Home Assistant integration guide to Mintlify"
```

---

### Task 9: Convert and translate SMARTIR.md to esphome/smartir.mdx

**Files:**
- Create: `docs/esphome/smartir.mdx`
- Source: `docs/SMARTIR.md`

**Step 1: Create esphome/smartir.mdx**

- Add frontmatter: `title: "SmartIR integration"`, `description: "Control IR devices from Home Assistant using the ED1 board as a SmartIR bridge."`
- Translate all Spanish content to English
- Remove the H1 heading
- Keep the same structure: architecture diagram, hardware requirements, configuration steps, entities, services, troubleshooting

**Step 2: Commit**

```bash
git add docs/esphome/smartir.mdx
git commit -m "feat(docs): add SmartIR integration guide (translated from Spanish)"
```

---

### Task 10: Update README links and validate

**Files:**
- Modify: `README.md` (Documentation section, lines 132-138)

**Step 1: Update README documentation links**

Change the Documentation section links to point to the new `.mdx` file paths:

```markdown
## Documentation

- [Hardware Reference](docs/hardware/overview.mdx) - Board specifications and components
- [GPIO Pinout](docs/hardware/pinout.mdx) - Pin mapping quick reference
- [ESPHome Configuration](docs/esphome/configuration.mdx) - Configuration explained
- [Home Assistant Integration](docs/esphome/home-assistant.mdx) - Dashboards & automations
- [SmartIR Integration](docs/esphome/smartir.mdx) - Control IR devices with SmartIR
```

**Step 2: Run mint broken-links**

Run: `cd docs && mint broken-links`
Expected: No broken links reported.

**Step 3: Run mint validate**

Run: `cd docs && mint validate`
Expected: No validation errors.

**Step 4: Commit**

```bash
git add README.md
git commit -m "docs: update README links to new Mintlify file paths"
```

---

### Task 11: Clean up old Markdown files

**Files:**
- Delete: `docs/HARDWARE.md`
- Delete: `docs/PINOUT.md`
- Delete: `docs/ESPHOME.md`
- Delete: `docs/HOME-ASSISTANT.md`
- Delete: `docs/SMARTIR.md`
- Modify: `docs/.mintignore` (remove old .md exclusions)

**Step 1: Remove old .md files**

```bash
git rm docs/HARDWARE.md docs/PINOUT.md docs/ESPHOME.md docs/HOME-ASSISTANT.md docs/SMARTIR.md
```

**Step 2: Update .mintignore**

Remove the lines excluding old `.md` files (they no longer exist):

```
HARDWARE.md
ESPHOME.md
HOME-ASSISTANT.md
PINOUT.md
SMARTIR.md
```

**Step 3: Run mint validate**

Run: `cd docs && mint validate`
Expected: No validation errors.

**Step 4: Commit**

```bash
git add -A docs/.mintignore
git commit -m "chore(docs): remove old Markdown files replaced by Mintlify pages"
```

---

### Task 12: Final validation and local preview

**Files:**
- None (validation only)

**Step 1: Full validation**

```bash
cd docs && mint validate && mint broken-links
```

Expected: No errors.

**Step 2: Local preview**

```bash
cd docs && mint dev
```

Expected: Site loads at `http://localhost:3000` with:
- Sidebar showing 3 groups: Getting started, Hardware, ESPHome
- 7 pages total, all rendering correctly
- Board images visible on introduction page
- ASCII diagrams preserved in hardware pages
- Code blocks with proper syntax highlighting

**Step 3: Stop server and confirm done**

Stop the dev server. The branch `feature/mintlify-docs` is ready for review/PR.
