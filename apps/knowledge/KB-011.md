---
id: KB-011
title: Accessibility and Responsive Quality Standards
domain: quality_assurance · accessibility · wcag · responsive_testing
target_agent: frontend_developer_agent · qa_reviewer_agent
version: 1.0.0
status: approved
description: Rigorous accessibility (WCAG 2.1 AA) and responsive quality standards ensuring keyboard navigation, screen reader compatibility, color contrast compliance, and cross-device view stability.
---

# Knowledge Base Document: KB-011
**Title:** Accessibility and Responsive Quality Standards  
**Domain:** Quality Assurance · Accessibility · WCAG · Responsive Testing  

---

## 1. Purpose and Operational Mandate
The primary objective of `KB-011` is to establish strict accessibility (a11y) and responsive quality benchmarks for all generated applications. 

An enterprise-grade application must be fully usable by individuals relying on assistive technologies (screen readers, keyboard-only navigation) and render flawlessly across mobile, tablet, and desktop viewports. `KB-011` provides actionable rules that the Frontend and QA Reviewer Agents must enforce.

---

## 2. WCAG 2.1 AA Accessibility Standards

Generated applications must satisfy **WCAG 2.1 AA** compliance criteria across all user interfaces:

### A. Keyboard Navigation & Focus Management
* **Visible Focus Rings:** Every interactive element (buttons, links, form inputs, modal controls) must display a clear, high-contrast focus indicator when navigated via keyboard (`focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2`). Never remove outline rings (`outline-none`) without replacing them with a custom focus state.
* **Logical Tab Order:** DOM elements must follow a logical reading order. Interactive modals must trap keyboard focus internally until dismissed.
* **Skip Links:** Multi-page layouts should include a hidden "Skip to main content" link for screen reader and keyboard accessibility.

### B. Color Contrast & Visual Semantics
* **Contrast Ratio Compliance:** Normal body text must maintain a minimum contrast ratio of `4.5:1` against its background. Large headings (`>= 18pt` bold or `>= 24pt` regular) must maintain at least `3:1`.
* **Non-Color State Indicators:** Never rely solely on color to communicate interactive status or errors (e.g., form validation errors must include text labels and icons, not just red border outlines).
* **Semantic Landmarks:** Use proper landmark elements (`<header>`, `<main>`, `<nav>`, `<aside>`, `<footer>`) to allow screen readers to navigate page regions instantly.

---

## 3. Responsive Quality & Cross-Device Viewports

Agents must verify that layouts adapt dynamically without breaking across the standard viewport range:

### A. Mobile & Tablet Verification Rules
* **No Horizontal Overflow:** Containers must strictly enforce `max-w-full` and `overflow-x-hidden`. Content must never clip or force horizontal scrolling on `320px` width screens (iPhone SE viewport baseline).
* **Touch Target Minimums:** Interactive touch targets (buttons, gallery filters, mobile nav items) must have a minimum interactive surface area of `44px x 44px` to prevent misclicks on touch devices.
* **Readable Font Sizing:** Base mobile body text must never drop below `16px` (`1rem`) to prevent automatic browser zoom inflation on iOS Safari.

---

## 4. Automated QA Checklist for Agents

Before handing off code to the Deployment Agent, the QA Reviewer Agent must evaluate the build against this accessibility and responsiveness checklist:

1. [ ] **HTML Validation:** All semantic tags are properly opened, closed, and nested without validation errors.
2. [ ] **Image Alt Text:** 100% of informational images and portfolio photographs include descriptive `alt` attributes.
3. [ ] **Form Label Association:** Every form input has an explicit, associated `<label>` or `aria-label`.
4. [ ] **Keyboard Trap Check:** Modals and lightboxes successfully trap keyboard focus and dismiss cleanly on `ESC`.
5. [ ] **Responsive Breakpoint Check:** Layouts scale smoothly from `320px` mobile viewports up to `1536px` ultra-wide displays without overlapping elements or broken text wraps.

```
