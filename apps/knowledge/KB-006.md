---
id: KB-006
title: Domain Blueprint Catalog & Portfolio Patterns
domain: website_generation · domain_blueprints · industry_patterns
target_agent: planner_architect_agent · designer_agent · frontend_developer_agent
version: 1.0.0
status: approved
description: Generalized domain blueprint framework covering multiple industry verticals (Creative/Visual, Local Services, Professional Services, E-Commerce/Product Showcase, SaaS/Tech, and Personal/Academic) with detailed specifications for galleries, project pages, services, biographies, and lead generation workflows.
---

# Knowledge Base Document: KB-006
**Title:** Domain Blueprint Catalog & Portfolio Patterns  
**Domain:** Website Generation · Domain Blueprints · Industry Patterns  

---

## 1. Purpose and Operational Mandate
The primary objective of `KB-006` is to provide a comprehensive, domain-agnostic blueprint catalog for multi-agent website generation. While `KB-002` classifies high-level website types and mandatory page taxonomies, `KB-006` supplies the **deep domain-specific content modeling, visual art direction rules, UX workflows, and operational blueprints** across diverse industry verticals.

This document equips the Planner and Engineering Agents to autonomously configure tailored user experiences for photography, local services, corporate consulting, e-commerce showcases, software platforms, and personal portfolios without relying on single-vertical hardcoding.

---

## 2. Vertical Taxonomy & Domain Blueprints

When `KB-001` identifies an industry vertical, the Planner Agent must match it against one of six core domain blueprints to establish mandatory functional specs and UX models:

---

### Blueprint Vertical A: Visual & Creative Arts (e.g., Photography, Architecture, Fine Art, Interior Design)
* **Primary Objective:** High-impact visual storytelling, aesthetic immersion, portfolio presentation, and client inquiry generation.
* **Core Information Architecture:**
  * `Home`: Immersive hero visual, curated featured works grid, artist statement/philosophy snippet, quick inquiry CTA.
  * `Portfolio / Gallery`: Multi-category filtered gallery (e.g., Editorial, Portrait, Commercial, Architecture) with lightbox modal engine.
  * `Project / Case Detail (/portfolio/[slug])`: Dedicated deep dive featuring shot lists/photo series, metadata (location, camera/gear, date, client), and contextual storytelling.
  * `About / Artist Bio`: Artistic journey, awards, client roster, press features, gear/studio specs, personal portrait.
  * `Services / Packages (Optional)`: Commission tiers, licensing terms, session options.
  * `Contact`: Specialized booking/inquiry form (capturing shoot scope, preferred date, budget tier).
* **Art Direction & UI Rules:**
  * Minimalist, unobtrusive framing (obsidian dark mode or crisp gallery white) letting visual assets dictate color.
  * High-contrast serif headings paired with clean, ultra-legible sans-serif UI typography.
  * Zero image distortion (`object-cover` with explicit reserved aspect ratios).

---

### Blueprint Vertical B: Local & Field Services (e.g., Restaurants, Legal Practice, Dental/Medical, Construction, Salon/Spa)
* **Primary Objective:** Local trust generation, clear service discovery, operational information (location, hours), and direct lead/booking conversions.
* **Core Information Architecture:**
  * `Home`: Trust-building hero with primary CTA ("Book Appointment", "Call Now", "Reserve Table"), core service highlights, customer ratings/reviews, location summary.
  * `Services / Menu / Offerings`: Categorized breakdown of services, pricing estimates, procedure details, or food menus.
  * `About / Team / Facility`: Practice history, team bios/credentials, certifications, studio or facility virtual tour.
  * `Reviews / Testimonials`: Verified client feedback, before-and-after transformations, or star rating aggregates.
  * `Contact & Locations`: Dynamic map embed, physical address, business hours, emergency contact, integrated booking/reservation widget.
* **Art Direction & UI Rules:**
  * High-accessibility contrast, warm and authoritative tones (navy, slate, emerald, or warm terracotta).
  * Prominent, persistent contact buttons (sticky header/footer CTAs for mobile click-to-call).
  * Clean, scannable accordions for FAQs and clear price/service tables.

---

### Blueprint Vertical C: Professional Services & Enterprise (e.g., Consulting, Creative Agencies, Law Firms, Finance)
* **Primary Objective:** Value proposition communication, social proof, B2B lead generation, and thought leadership.
* **Core Information Architecture:**
  * `Home`: Value proposition hero, strategic service pillars, client logo cloud, featured case studies, consultation CTA.
  * `Services / Solutions`: Comprehensive breakdowns of capabilities, methodologies, and engagement models.
  * `Case Studies / Work`: Problem-Solution-Result narrative structures with quantifiable metric highlights (e.g., "+140% Conversion Growth").
  * `About / Leadership`: Mission statement, executive leadership bios, firm values, company history timeline.
  * `Insights / Blog (Optional)`: Whitepapers, articles, and industry analyses with newsletter signup.
  * `Contact / Consultation`: Structured discovery call form (capturing company size, scope, timeline, budget).
* **Art Direction & UI Rules:**
  * Polished, structured layout with multi-column card grids, subtle border dividers, and subtle multi-layer elevation shadows.
  * Professional corporate color palettes with high-contrast typography.

---

### Blueprint Vertical D: E-Commerce & Product Showcase (e.g., Direct-to-Consumer, Artisanal Brands, Digital Goods)
* **Primary Objective:** Product discovery, feature highlighting, brand story immersion, and friction-free purchase/inquiry flows.
* **Core Information Architecture:**
  * `Home`: Highlighting hero banner, featured collections, bestsellers carousel, value props (e.g., "Free Shipping", "Handcrafted").
  * `Catalog / Shop Grid`: Filterable product catalog (by collection, price, tag, availability).
  * `Product Detail View (/product/[slug])`: High-res product media gallery, variant selectors (color, size), inventory status, detailed specs, customer reviews, "Add to Cart" / "Inquire" CTA.
  * `Brand Story / About`: Craftsmanship details, material sourcing, ethical standards.
  * `Cart / Checkout / Inquiry Modal`: Cart drawer or quote request workflow.
* **Art Direction & UI Rules:**
  * Product-first layout with high-density grid structures and rich product zoom/hover preview states.
  * Subtle urgency indicators (e.g., "Limited Edition", "In Stock").

---

### Blueprint Vertical E: SaaS & Technology Platforms (e.g., Developer Tools, B2B Software, Mobile Apps)
* **Primary Objective:** Product feature explanation, interactive demo/preview, conversion through free trial or demo requests.
* **Core Information Architecture:**
  * `Home / Landing`: High-converting headline, product UI mock-up/video preview, feature grid, interactive pricing calculator/table, FAQ, lead CTA.
  * `Features / Product Deep Dive`: Granular breakdown of software capabilities, integration ecosystem, API docs link.
  * `Pricing`: Clear tier cards (Free, Pro, Enterprise) with feature comparison checklist and billing toggle (Monthly vs. Annual).
  * `Customers / Wall of Love`: Testimonials, logo grids, customer success stories.
* **Art Direction & UI Rules:**
  * Modern tech aesthetics: Dark mode default options, glowing accent highlights, monospaced tech metadata font pairings, subtle backdrop blur containers (`backdrop-blur`).

---

### Blueprint Vertical F: Personal, Academic, & Executive Portfolios (e.g., Software Engineers, Researchers, Executives, Writers)
* **Primary Objective:** Highlighting individual career milestones, publication records, technical expertise, and personal branding.
* **Core Information Architecture:**
  * `Home / Bio`: Personal elevator pitch, role/title badge, quick links (Resume PDF, GitHub, LinkedIn, Email).
  * `Experience / Curriculum Vitae`: Interactive career timeline detailing key roles, responsibilities, and measurable achievements.
  * `Projects / Research / Publications`: Selected engineering projects, research papers, or written publications with external links.
  * `Skills & Competencies`: Grouped technical skills, domain expertise, or speaker engagements.
  * `Contact`: Direct contact form or calendly scheduling link integration.
* **Art Direction & UI Rules:**
  * Clean, highly readable, typography-focused layout with minimal visual clutter and accessible contrast.

---

## 3. Shared Cross-Domain Component Specifications

Regardless of the selected domain blueprint, all generated applications must implement these standard component patterns:

### A. The Master Inquiry & Lead Workflow Pattern
Every domain must support an inquiry/booking workflow matching its operational model:
1. **Field Schemas:** Enforce strict Zod schema validation (`KB-010`) customized to the vertical (e.g., shoot date for photographers, patient details for medical, company size for SaaS).
2. **State Machine:** Manage four clean submission lifecycle states: `Idle` ➔ `Submitting` ➔ `Success` / `Error`.
3. **No Fake Stubs:** Provide working Server Actions or API routes for form dispatches.

### B. Media & Asset Pipeline Standards
* **Aspect Ratio Protection:** Enforce strict CSS aspect ratios (`aspect-square`, `aspect-[4/3]`, `aspect-[16/9]`) and `object-fit: cover` across all vertical imagery (`KB-008`).
* **Performance:** Above-the-fold media must prioritize loading (`priority`), while below-the-fold assets rely on lazy loading (`loading="lazy"`).

### C. Content Authenticity Rule (Zero Fabrication Guardrail)
* Do not generate fake testimonials, fictional client logos, or false awards unless explicitly flagged in `assumptions_log` as placeholder data.

---

## 4. Manifest Resolution Rules
When building the Project Manifest (`KB-001`), the Planner Agent must select one primary domain blueprint from `KB-006` and populate `architecture.routing_structure` and `functional_features` accordingly. For hybrid prompts, synthesize routing cleanly while maintaining strict component isolation.

```