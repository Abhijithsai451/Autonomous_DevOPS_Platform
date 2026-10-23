---
id: KB-004
title: Design Systems and Responsive Layouts
domain: design_systems · responsive_architecture · css_tokens
target_agent: designer_agent · frontend_developer_agent
version: 1.0.0
status: approved
description: Technical directives for constructing tokenized design systems, responsive grid layouts, fluid typography, and mobile-first container strategies.
---

# Knowledge Base Document: KB-004
**Title:** Design Systems and Responsive Layouts  
**Domain:** Design Systems · Responsive Architecture · CSS Tokens  

---

## 1. Purpose and Operational Mandate
The primary function of `KB-004` is to standardize the technical execution of design systems and responsive layout structures across generated codebase repositories. 

It defines exact **CSS variables, Tailwind CSS configuration tokens, responsive breakpoint behaviors, fluid spacing formulas, and container grid structures**. This ensures that generated frontends operate on a rigorous, deterministic design token system rather than ad-hoc inline styles.

---

## 2. Design Token Architecture & CSS Variable Contracts

Agents must organize design tokens into a centralized variable structure (e.g., inside `globals.css` or `tailwind.config.ts`). Every generated application must expose semantic theme tokens for background, foreground, surface, border, and brand states.

### A. Semantic Color Token Schema (CSS Variables)

```css
@layer base {
  :root {
    /* Base Canvas & Text Tokens */
    --background: 0 0% 100%;        /* #FFFFFF */
    --foreground: 240 10% 3.9%;     /* #09090B */
    
    /* Surface & Container Tokens */
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 240 10% 3.9%;

    /* Interactive & Brand Tokens */
    --primary: 240 5.9% 10%;        /* Deep Neutral or Brand Lead */
    --primary-foreground: 0 0% 98%;
    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;
    
    /* State & Utility Tokens */
    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;
    --accent: 240 4.8% 95.9%;
    --accent-foreground: 240 5.9% 10%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;

    /* Structural Tokens */
    --border: 240 5.9% 90%;
    --input: 240 5.9% 90%;
    --ring: 240 5.9% 10%;
    --radius: 0.5rem;
  }

  .dark {
    /* Dark Theme Overrides */
    --background: 240 10% 3.9%;     /* #09090B */
    --foreground: 0 0% 98%;         /* #FAFAFA */
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 240 10% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 240 5.9% 10%;
    --secondary: 240 3.7% 15.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 240 3.7% 15.9%;
    --muted-foreground: 240 5% 64.9%;
    --accent: 240 3.7% 15.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 3.7% 15.9%;
    --input: 240 3.7% 15.9%;
    --ring: 240 4.9% 83.9%;
  }
}
```
## 3. Responsive Breakpoint & Container Grid Matrix
Agents must build layout containers mobile-first using standardized grid and container rules:
### A. Enterprise Breakpoint Standard
* sm (640px): Mobile landscape & large smartphones.
* md (768px): Tablets & vertical displays.
* lg (1024px): Laptops & small desktop monitors.
* xl (1280px): Standard desktop displays.
* 2xl (1536px): Large widescreen displays & high-resolution monitors.

### B. Standard Container Layout Blueprint
* Layout wrappers must enforce horizontal padding gutters on mobile and fixed maximum widths on large viewports to preserve line lengths and legibility:
```tsx
// React / Tailwind Container Pattern
export function Container({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 ${className}`}>
      {children}
    </div>
  );
}
```

### C. Standard Grid Column Strategies

| Layout Section | Mobile (<640px) | Tablet (768px) | Desktop (>=1024px) |
| :--- | :--- | :--- | :--- |
| **Photo Gallery Grid** | `grid-cols-1` | `grid-cols-2` | `grid-cols-3` or Masonry |
| **Feature / Service Cards** | `grid-cols-1` | `grid-cols-2` | `grid-cols-3` |
| **Split Hero / Content** | `flex-col` | `flex-col` | `grid grid-cols-12` (7:5 or 8:4 split) |
| **Footer Navigation** | `grid-cols-2` | `grid-cols-4` | `grid-cols-5` |

---

## 4. Spacing, Elevation, and Typography Systems

### A. Spatial Rhythm Scale (8pt System)
Spacing for gaps, margins, and section padding must strictly utilize these fixed step values:

* **1 (0.25rem / 4px)** — Micro icon margins.
* **2 (0.5rem / 8px)** — Tight component inline padding.
* **4 (1rem / 16px)** — Standard button padding, form field spacing.
* **6 (1.5rem / 24px)** — Card internal padding, small grid gaps.
* **8 (2rem / 32px)** — Large card padding, standard section component gap.
* **12 (3rem / 48px)** — Section spacing on mobile displays.
* **16 (4rem / 64px)** — Standard desktop section vertical padding (`py-16`).
* **24 (6rem / 96px)** — Hero section / visual showcase vertical padding (`py-24`).

### B. Typography Modular Scale & Line Heights
```css
css /* Typography Scale Standards */ 
.text-hero { font-size: clamp(2.5rem, 5vw + 1rem, 4.5rem);
    line-height: 1.05; letter-spacing: -0.03em; } 
.text-h1 { font-size: clamp(2.0rem, 3vw + 1rem, 3.25rem);
    line-height: 1.15; letter-spacing: -0.02em; } 
.text-h2 { font-size: clamp(1.5rem, 2vw + 0.75rem, 2.25rem); 
    line-height: 1.25; letter-spacing: -0.01em; } 
.text-h3 { font-size: 1.5rem; line-height: 1.35; 
    letter-spacing: 0em; }
.text-body { font-size: 1rem; line-height: 1.6; 
    letter-spacing: 0em; } 
.text-caption { font-size: 0.875rem; 
    line-height: 1.4; letter-spacing: 0.01em; }
```


---

## 5. Mobile-First Responsive Safeguards
Frontend Agents must enforce these non-negotiable rules for responsive safety:

* **No Horizontal Scroll Overflow:** Apply `overflow-x-hidden` on top-level layout containers. Never hardcode pixel widths (`width: 800px`); use percentage or relative width (`w-full max-w-2xl`).
* **Touch Target Size:** Interactive elements (buttons, nav links, gallery filters) must meet minimum touch target sizes (`44px x 44px` or `p-3`) on mobile screens.
* **Mobile Navigation Overlay:** Views with more than 3 navigation links must automatically collapse into a responsive slide-over drawer or hamburger menu on viewports below `768px`.
* **Media Aspect Ratio Protection:** Always set explicit aspect ratios on containers wrapping responsive images to prevent Cumulative Layout Shift (CLS) during image download.