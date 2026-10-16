# Living Weave — Design System Specification

**Product Codename:** Living Weave  
**Aesthetic Direction:** Editorial Cartography & Interconnected Fiber Structures  

---

## 1. Visual Metaphor
Living Weave departs from generic dark-mode SaaS dashboards and childish cartoon graphics. Instead, it embodies:
- **Editorial Composition:** High typographic hierarchy, warm paper surfaces, and deliberate spacing.
- **Cartographic Information Architecture:** Map-like grids, coordinates, nodes, and pathways.
- **Woven Structures:** Individual capabilities acting as colored threads that interlace into a balanced team tapestry.

---

## 2. Color Tokens

### Foundation Palette
- **Warm Paper Canvas:** `#F6F4ED` (`bg-canvas`) — Primary page surface evoking tactile archival paper.
- **White Surface:** `#FFFDF8` (`bg-surface`) — Elevated card and panel surface.
- **Deep Ink:** `#182724` (`text-ink`) — High-contrast text and primary buttons.
- **Secondary Ink:** `#68746E` (`text-secondary`) — Supporting descriptions and explanations.
- **Muted Ink:** `#87918B` (`text-muted`) — Minor metadata, timestamps, and captions.
- **Border Fiber:** `#E2E3DB` (`border-border`) — Delicate structural lines.

### Primary Brand Accents
- **Woven Teal:** `#17A982` (`text-teal-brand`, `bg-teal-brand`) — Primary action color and brand signature.
- **Pale Mint:** `#DDF4E9` (`bg-teal-mint`, `text-teal-dark`) — Subtle badges, highlights, and success states.

### Capability Domain Accents
- **Cobalt:** `#536FF1` (`text-cobalt`, `bg-cobalt-light`) — Architecture & Backend systems.
- **Soft Coral:** `#ED8B76` (`text-coral`, `bg-coral-light`) — Experience, Design & Gap Alerts.
- **Soft Gold:** `#D5A747` (`text-gold`, `bg-gold-light`) — Infrastructure, Streaks & Milestones.
- **Muted Violet:** `#8676D8` (`text-violet`, `bg-violet-light`) — Intelligence & Machine Learning.

---

## 3. Typography

- **Display Face:** Space Grotesk (`font-display`) — Expressive, technical geometry for prominent headings and score indexes.
- **Body Face:** Inter (`font-sans`) — Highly legible, neutral sans-serif for UI controls, inputs, and descriptions.
- **Monospace Face:** JetBrains Mono (`font-mono`) — Labels, status pills, IDs, and technical proficiency tags.

---

## 4. Key Components

1. **The Living Weave Canvas (`WeaveCanvas.jsx`):** Interactive SVG capability lattice connecting multi-disciplinary nodes with smooth bezier threads.
2. **The Team Blueprint (`TeamBlueprint.jsx`):** Complete team diagnostic matrix detailing:
   - Status & Overall Quality Score (0–100)
   - Requirement Coverage Matrix (Covered, Partially Covered, Missing)
   - Member Roster with Proficiency Badges (L1–L4)
   - Reshuffling & Replacement Modal
   - Algorithmic Rationale Card
