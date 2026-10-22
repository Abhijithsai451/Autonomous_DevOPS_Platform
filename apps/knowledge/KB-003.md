---
id: KB-003
title: Professional UI/UX Design Principles
domain: ui_ux_design · visual_hierarchy · art_direction
target_agent: designer_agent · frontend_developer_agent
version: 1.0.0
status: approved
description: Professional design heuristics, art direction rules, visual hierarchy guidelines, and anti-patterns to generate bespoke, high-quality user interfaces rather than generic AI templates.
---

# Knowledge Base Document: KB-003
**Title:** Professional UI/UX Design Principles  
**Domain:** UI/UX Design · Visual Hierarchy · Art Direction  

---

## 1. Purpose and Operational Mandate
The primary objective of `KB-003` is to govern the visual quality and user experience standards of generated applications. AI coding models frequently default to generic, uninspired UI templates characterized by centered text blocks, overused purple/blue primary buttons, unrefined card grids, and flat visual hierarchy. 

`KB-003` instructs the Designer and Frontend Engineering agents to apply **professional art direction, intentional whitespace, distinct visual weight, and domain-appropriate design systems** that yield bespoke, premium digital experiences.

---

## 2. Core Visual Hierarchy Heuristics

Every generated page must strictly implement the following five visual hierarchy rules:

### 1. Scale & Contrast Ratios
* **Typography Scale:** Maintain a distinct typographic hierarchy using a high scale ratio (e.g., Major Third `1.250` or Perfect Fourth `1.333`).
* **Heading Dominance:** H1 elements must be dramatically larger and heavier than body copy to establish immediate focal points. Never rely on color alone to differentiate headings from body text.
* **Text Contrast:** Ensure all body text meets WCAG AA standards (minimum 4.5:1 contrast ratio against background). Never use low-contrast light grey text on white or dark grey on black for critical copy.

### 2. Spatial Cadence & Rhythms
* **Systematic Spacing Scale:** Use an 8pt grid system (`8px`, `16px`, `24px`, `32px`, `48px`, `64px`, `96px`, `128px`) for all padding, margins, and gaps.
* **Generous Whitespace:** Creative, editorial, and photography domains require explicit whitespace cushion (e.g., `section` padding of `py-16` to `py-32` in Tailwind). Avoid cramming elements together.
* **Proximity Principle:** Related items (e.g., a photo thumbnail and its caption) must sit significantly closer together than unrelated section blocks.

### 3. Layout Composition & Asymmetry
* **Grid Alignment:** Align all major layout sections to a clean 12-column or 6-column grid structure.
* **Avoid Monotonous Centering:** Never center-align long blocks of text or entire multi-column sections. Left-aligned body text is mandatory for legibility. Reserve center alignment strictly for short hero titles or simple empty states.
* **Visual Anchor Points:** Place primary focal elements (such as lead hero imagery or key conversion CTAs) at natural visual entry points (top-left or visual optical center).

---

## 3. Domain-Specific Art Direction Archetypes

When constructing interfaces, agents must apply design tokens tailored to the industry category specified in the Project Manifest (`KB-001` / `KB-002`):

### Archetype A: Creative / Editorial (e.g., Photography, Art, Architecture)
* **Visual Signature:** High contrast, dominant imagery, generous whitespace, subtle borders.
* **Color Palette:** Monochrome or near-monochrome canvas (e.g., `#09090B` background, `#FAFAFA` foreground) with a single subtle accent or high-contrast image focus.
* **Typography Pairing:** Elegant Serif for headings (`Playfair Display`, `Cormorant Garamond`, `Cinzel`) paired with a clean, neutral Sans-Serif for interface UI (`Inter`, `Plus Jakarta Sans`).
* **Imagery Rule:** Let the photographs supply color. The framing UI must remain clean, unobtrusive, and borderless or ultra-fine (`border-zinc-800`).

### Archetype B: Corporate & Business (e.g., Agencies, Enterprise Services)
* **Visual Signature:** Structured content cards, trustworthy tones, clear visual pathways, bold headlines.
* **Color Palette:** Deep slate or navy neutrals paired with a authoritative primary brand color (e.g., Deep Blue, Emerald, or Charcoal).
* **Typography Pairing:** Bold, modern Sans-Serif headings (`Plus Jakarta Sans`, `Outfit`) paired with readable body copy (`Inter`).
* **Borders & Shadows:** Subtle elevation using multi-layered box shadows and light borders (`border-slate-200` or `border-slate-800`).

### Archetype C: Modern Tech / Developer
* **Visual Signature:** Dark mode default, crisp borders, monospaced accents, subtle glowing highlights.
* **Color Palette:** Dark zinc/slate backgrounds (`#0C0C0E`), vibrant accent colors (Cyan, Emerald, Amber), translucent overlay surfaces (`backdrop-blur`).
* **Typography Pairing:** Geometric Sans-Serif (`Geist Sans`, `Inter`) paired with Monospace details (`Geist Mono`, `Fira Code`) for metrics and metadata.

---

## 4. Strict Anti-Pattern Catalog ("What NOT to Build")

The Design and Frontend Agents must explicitly avoid these common AI generation flaws:

* ❌ **The "Generic SaaS Purple" Trap:** Do not use default indigo/violet gradients or standard `#6366F1` button colors unless explicitly requested.
* ❌ **Auto-Playing Hero Carousels:** Do not implement sliding carousels for primary hero sections; they suffer from poor conversion rates and mobile Cumulative Layout Shift (CLS). Use static lead imagery, split heroes, or masonry preview grids instead.
* ❌ **Floating Cards Without Purpose:** Do not place every section inside a boxed card wrapper with heavy shadows. Use whitespace and typography to define boundaries before adding card containers.
* ❌ **Unstyled Default Browser Controls:** Every interactive element (buttons, form inputs, modals) must have custom hover, focus, active, and disabled states. Never leave raw browser defaults.
* ❌ **Centered Body Text:** Never center body paragraphs spanning wider than `400px`. It breaks reader eye scanning.
* ❌ **Stretched or Distorted Images:** Images must strictly enforce aspect ratios (`aspect-square`, `aspect-[4/3]`, `aspect-[16/9]`) and use `object-fit: cover` to prevent distortion.

---

## 5. Interaction & Micro-UX Standards

1. **State Completeness:** Every interactive component must define 5 core states:
   * **Default:** Resting visual representation.
   * **Hover:** Subtle background shift, scale transform (e.g., `scale-[1.02]`), or border highlight.
   * **Focus-Visible:** Clear focus ring (`ring-2 ring-offset-2`) for keyboard accessibility.
   * **Active / Pressed:** Visual depth press or subtle scale down (`scale-[0.98]`).
   * **Disabled:** Lowered opacity (`opacity-50`) and `cursor-not-allowed`.
2. **Smooth Transitions:** Apply explicit, subtle transitions (`transition-all duration-200 ease-out`) to hover and color changes. Avoid aggressive, slow animations (>300ms) that make the app feel sluggish.