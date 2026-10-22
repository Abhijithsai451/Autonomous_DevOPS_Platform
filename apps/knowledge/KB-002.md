---
id: KB-002
title: Website Type and Feature Catalog
domain: website_generation · product_architecture · taxonomy_mapping
target_agent: planner_architect_agent
version: 1.0.0
status: approved
description: Comprehensive catalog mapping website categories to standard page structures, core functional features, and domain-specific requirements.
---

# Knowledge Base Document: KB-002
**Title:** Website Type and Feature Catalog  
**Domain:** Website Generation · Product Architecture · Taxonomy Mapping  

---

## 1. Purpose and Operational Mandate
The primary function of `KB-002` is to provide the Planner Agent with an authoritative taxonomy of website categories. When `KB-001` extracts an industry domain or website type from a user prompt (e.g., a photographer portfolio, a SaaS landing page, or a local business site), `KB-002` dictates the exact baseline requirements: **mandatory pages, optional modules, core features, and architectural patterns** needed to ensure the delivered application feels authentic to its industry rather than generic.

---

## 2. Website Category Taxonomies & Feature Matrix

The agent must classify every incoming request into one of the core categories below and inject the corresponding structural and functional blueprint into the Project Manifest.

### Category A: Creative & Professional Portfolios (e.g., Photographer, Designer, Artist)
* **Core Objective:** Showcase visual assets, establish artistic identity, and facilitate client inquiries.
* **Mandatory Pages & Sections:**
  * `Home`: High-impact visual hero, featured works grid, brief bio intro, quick call-to-action (CTA).
  * `Portfolio / Gallery`: Categorized visual grid with filter options and detail view/lightbox.
  * `About`: Biography, philosophy, client list, or equipment/process details.
  * `Contact`: Inquiry form, direct email/social links, availability status.
* **Mandatory Functional Features:**
  * Responsive masonry or CSS grid layout.
  * Image optimization pipeline (lazy loading, explicit aspect ratios).
  * Modal/Lightbox viewer for deep-dive asset inspection.
  * Validated contact/booking inquiry form.

### Category B: Business & Agency Websites (e.g., Corporate, Creative Agency, Enterprise)
* **Core Objective:** Communicate value proposition, build brand trust, present services, and capture qualified leads.
* **Mandatory Pages & Sections:**
  * `Home`: Value proposition hero, core services preview, client social proof, CTA.
  * `Services`: Detailed breakdown of offerings, tiers, or solutions.
  * `About Us`: Company mission, team profiles, history or culture.
  * `Case Studies / Work`: Portfolio of past projects with quantifiable outcomes.
  * `Contact`: Enterprise contact form, office locations, consultation scheduler link.
* **Mandatory Functional Features:**
  * Clear service tier pricing tables or feature comparison grids.
  * Testimonial carousel or logo cloud for social proof.
  * Structured lead-capture form with validation.

### Category C: Personal Portfolios & Resumes
* **Core Objective:** Highlight an individual's professional experience, core competencies, and career history.
* **Mandatory Pages & Sections:**
  * `Home / Hero`: Name, professional title, elevator pitch, primary CTAs (Resume Download, Contact).
  * `Experience / Timeline`: Chronological career history and key achievements.
  * `Skills & Expertise`: Technical and domain competencies grouped by category.
  * `Projects`: Selected work samples or open-source contributions.
  * `Contact`: Direct contact options.
* **Mandatory Functional Features:**
  * Clean, scannable timeline layout.
  * Downloadable resume link (PDF asset handling).
  * Mobile-optimized reading view.

### Category D: Landing Pages & Marketing Sites
* **Core Objective:** Convert traffic for a single product, service, or event launch.
* **Mandatory Pages & Sections:**
  * Single-page scroll layout containing: Hero Section, Social Proof, Core Benefits/Features, Pricing/Offer, FAQ, Final Conversion CTA, Footer.
* **Mandatory Functional Features:**
  * High-converting sticky navigation or anchor-link jumping.
  * Email capture or signup form with instant validation feedback.
  * FAQ accordion component.

### Category E: Content & Media Sites (e.g., Blogs, Magazines)
* **Core Objective:** Present articles, posts, or editorial content in an easily readable format.
* **Mandatory Pages & Sections:**
  * `Home`: Recent articles feed, featured spotlight post, category navigation.
  * `Article / Post View`: Clean typography container, author metadata, publication date, reading time, share links.
  * `Category Archive`: Filtered view of posts by topic.
* **Mandatory Functional Features:**
  * Structured content typography hierarchy (optimized line lengths, heading spacing).
  * Search or tag filtering mechanism.

---

## 3. Manifest Integration Guidelines
When processing a prompt, the Planner Agent must cross-reference `KB-002` to populate the `architecture.routing_structure` and `functional_features` arrays in the Project Manifest (`KB-001` schema):

1. **Route Mapping:** Extract all mandatory pages listed in the matched category and assign standard component types.
2. **Feature Injection:** Automatically append all mandatory features for that category to the project's feature pipeline, preventing the creation of incomplete applications.

---

## 4. Edge Cases & Hybrid Classifications
* **Multiple Intents:** If a user prompt combines categories (e.g., *"a business website for a photography agency with a blog"*), the agent must synthesize a hybrid routing structure combining the core pages of both categories while maintaining clean architectural boundaries.
* **Minimalist Overrides:** If the user explicitly requests a minimalist MVP (e.g., *"a one-page photographer portfolio"*), override multi-page defaults into a single-page anchor-scrolled architecture while retaining the mandatory visual features.