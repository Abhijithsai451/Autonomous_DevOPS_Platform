---
id: KB-008
title: Image, Gallery, and Media Handling
domain: frontend_engineering · media_optimization · performance · accessibility
target_agent: frontend_developer_agent · designer_agent
version: 1.0.0
status: approved
description: Complete implementation guidelines for high-performance responsive media handling, aspect ratio enforcement, lazy loading strategies, lightbox interactions, and media accessibility.
---

# Knowledge Base Document: KB-008
**Title:** Image, Gallery, and Media Handling  
**Domain:** Frontend Engineering · Media Optimization · Performance · Accessibility  

---

## 1. Purpose and Operational Mandate
The primary objective of `KB-008` is to enforce strict engineering standards for visual asset presentation, performance optimization, and accessibility. 

Because photography and visual portfolios depend heavily on high-density imagery, improper media handling leads to high Cumulative Layout Shift (CLS), slow PageSpeed performance, broken layouts, and poor accessibility. `KB-008` provides deterministic blueprints to prevent these failures.

---

## 2. Responsive Image Optimization & Sizing Rules

Generated applications using framework image components (e.g., `next/image` or standard HTML `<picture>` elements) must follow explicit layout sizing rules:

### A. Non-Negotiable Sizing Directive
* **Explicit Aspect Ratio Containers:** Every image wrapper must define an explicit aspect ratio (`aspect-square`, `aspect-[4/3]`, `aspect-[3/2]`, `aspect-[16/9]`) or use relative fill properties (`fill` mode in Next.js) inside a relative parent.
* **`object-fit` Enforcements:** All gallery, grid, and hero images must apply `object-fit: cover` (`object-cover`) to guarantee zero stretched or distorted asset renders regardless of viewport scaling.
* **Preventing Cumulative Layout Shift (CLS):** Never render images without reserved space. Always reserve layout height using CSS aspect ratio utilities before media loads.

### B. Responsive `sizes` Attribute Mapping
When utilizing responsive image loaders, agents must configure the `sizes` string according to the active grid break points defined in `KB-004`:

```tsx
// Example Next.js Image component inside a responsive 3-column gallery
<Image alt="{image.altText}" 
       className="object-cover transition-transform duration-300 group-hover:scale-105" 
       fill loading="lazy" sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw" 
       src="{image.url}"/>
```
## 3. Loading Behaviors & Performance Strategies
1. Above-the-Fold Priority: High-impact hero images or the first 2 lead images on a homepage gallery must specify priority (or loading="eager" / fetchpriority="high"). 
2. Below-the-Fold Lazy Loading: All gallery thumbnails, grid items, and footer assets must use loading="lazy" to defer network overhead until viewports approach the asset. 
3. Blur Placeholder Strategy: Images must support smooth loading transitions (e.g., subtle skeleton pulse background bg-zinc-800 animate-pulse or low-resolution blur data URLs) to eliminate jarring white pop-in shifts.

## 4. Lightbox & Gallery Interaction Blueprint
A primary portfolio requirement is interactive full-screen visual inspection. Agents must implement the lightbox modal according to these interaction rules:

```Plaintext
[ Grid Thumbnail Click ] ──> [ Open Lightbox Modal ] 
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
[ ESC Key / Backdrop ]   [ Left/Right Arrow Keys ]   [ Touch Swipe Gestures ]
      │                           │                           │
      ▼                           ▼                           ▼
[ Close & Return Focus ]  [ Navigate Prev/Next ]      [ Mobile Slide Transition ]
```
### Lightbox Execution Requirements:
* Background Scroll Lock: When open, inject overflow: hidden onto document.body to prevent background page scrolling.
* Keyboard Control: Listen for KeyDown events:
  * Escape: Dismiss lightbox. 
  * ArrowRight: Advance to next image in collection.
  * ArrowLeft: Move to previous image in collection.

* Focus Management: Focus must automatically transition inside the modal on open and return to the clicked thumbnail element upon dismissal.

## 5. Accessibility (a11y) & Media Standards
1. Meaningful alt Text: Every image element must contain descriptive, meaningful alt attributes (e.g., "Black and white architectural shot of a minimalist concrete building by John Doe"). Never leave alt="" blank for portfolio works, and never use generic strings like alt="image".

2. Decorative vs. Informational Assets: Purely decorative ambient blur circles or background accent vectors must use aria-hidden="true".

3. High-Contrast Metadata Controls: Image caption overlays, camera EXIF details (e.g., ISO 100 · 35mm · f/1.8), and close buttons inside lightboxes must meet WCAG AA contrast standards against dark image backdrops using dark gradients (bg-gradient-to-t from-black/80 to-transparent).