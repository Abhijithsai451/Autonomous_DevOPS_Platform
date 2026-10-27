---
id: KB-012
title: Web Performance and Security Guidelines
domain: web_performance · security · Core_Web_Vitals · application_hardening
target_agent: frontend_developer_agent · qa_reviewer_agent · devops_agent
version: 1.0.0
status: approved
description: Technical directives for optimizing web performance (Core Web Vitals), asset optimization, dependency security, input validation, and secure header configuration.
---

# Knowledge Base Document: KB-012
**Title:** Web Performance and Security Guidelines  
**Domain:** Web Performance · Security · Core Web Vitals · Application Hardening  

---

## 1. Purpose and Operational Mandate
The primary objective of `KB-012` is to establish web performance and security standards across generated web applications. 

High-resolution visual assets and interactive client components can easily degrade user experience and introduce security risks if unoptimized. `KB-012` instructs agents to build applications that achieve top Core Web Vitals metrics while enforcing robust baseline application security.

---

## 2. Core Web Vitals Performance Standards

Generated applications must achieve high performance benchmarks (Lighthouse Score >= 90/100) by targeting three core metrics:

### A. Largest Contentful Paint (LCP) <= 2.5s
* **Hero Image Priority:** Explicitly set `priority` (or `fetchpriority="high"`) on primary hero images so they bypass lazy-loading queues.
* **Modern Media Formats:** Serve images using WebP or AVIF image formats.
* **Font Subsetting & Display:** Preload critical Google Fonts or local font subsets using `font-display: swap` to prevent render-blocking visual delays.

### B. Interaction to Next Paint (INP) <= 200ms
* **Minimize Heavy Main-Thread Work:** Keep client JavaScript bundles lightweight by preferring Next.js Server Components for layout structure and static rendering.
* **Debounce Interactive Filters:** Debounce rapid user inputs (e.g., gallery search queries or live category filtering) to prevent main-thread UI freezing.

### C. Cumulative Layout Shift (CLS) <= 0.1
* **Reserved Aspect Ratio Containers:** Always specify explicit aspect ratios (`aspect-square`, `aspect-[4/3]`, `aspect-[16/9]`) or fill dimensions on image containers before media loads.
* **Font Preloading:** Preload custom web fonts to prevent layout shifts caused by unstyled text fallbacks (FOUT).

---

## 3. Web Application Security Standards

Agents must enforce baseline security controls across both static assets and API routes:

### A. Input Sanitization & Injection Defense
* **Schema Validation:** Enforce strict validation on all form inputs and route parameters via Zod schemas (`KB-010`).
* **XSS Prevention:** Avoid using `dangerouslySetInnerHTML` unless rendering sanitized content. React’s default JSX escaping must be preserved for user-facing copy.

### B. Security Headers Configuration (`next.config.js`)
Generated applications must configure secure HTTP headers by default:

```javascript
/** @type {import('next').NextType} */
const nextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;

```

---

## 4. Asset & Dependency Hardening Checklist

Before deployment handoff, agents must verify the build against this security and performance gate:

1. [ ] **Zero Vulnerable Dependencies:** Rely strictly on stable, modern packages without known critical vulnerability advisories.
2. [ ] **No Exposed Secrets:** Environment variables containing sensitive credentials must remain server-side and never use public client prefixes (e.g., `NEXT_PUBLIC_`) unless explicitly required.
3. [ ] **Optimized Bundle Size:** Keep client-side bundle sizes minimal by importing targeted icons or utility modules directly (e.g., tree-shakeable Lucide React icons).
4. [ ] **Secure External Links:** Ensure all external links targeting `target="_blank"` include `rel="noopener noreferrer"` to prevent reverse tab-nabbing vulnerabilities.

```