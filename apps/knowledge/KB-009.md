---
id: KB-009
title: SEO, Metadata, and Social Sharing
domain: frontend_engineering · seo · metadata · social_cards · discoverability
target_agent: frontend_developer_agent · planner_architect_agent
version: 1.0.0
status: approved
description: Engineering standards for implementing robust search engine optimization, Next.js metadata APIs, Open Graph social cards, semantic HTML structuring, and sitemap generation.
---

# Knowledge Base Document: KB-009
**Title:** SEO, Metadata, and Social Sharing  
**Domain:** Frontend Engineering · SEO · Metadata · Social Cards · Discoverability  

---

## 1. Purpose and Operational Mandate
The primary objective of `KB-009` is to ensure that generated applications are fully optimized for search engine indexing, social media link previews, and semantic accessibility. 

A visually stunning photography portfolio fails its commercial purpose if search engines cannot index its content or if shared links display generic, broken previews on platforms like LinkedIn, Twitter/X, or iMessage. `KB-009` dictates the exact technical patterns for metadata implementation.

---

## 2. Next.js App Router Metadata Standard

Generated applications must utilize the native Next.js App Router Metadata API to inject page-specific titles, descriptions, and crawler directives.

### A. Static Page Metadata (`layout.tsx` or `page.tsx`)
```tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    default: 'John Doe | Fine Art & Editorial Photographer',
    template: '%s | John Doe Photography',
  },
  description: 'Professional portfolio showcasing fine art, editorial, and commercial photography by John Doe.',
  keywords: ['photographer', 'fine art photography', 'editorial portfolio', 'commercial photography', 'John Doe'],
  authors: [{ name: 'John Doe', url: '[https://johndoe-portfolio.com](https://johndoe-portfolio.com)' }],
  creator: 'John Doe',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '[https://johndoe-portfolio.com](https://johndoe-portfolio.com)',
    title: 'John Doe | Fine Art & Editorial Photographer',
    description: 'Professional portfolio showcasing fine art, editorial, and commercial photography.',
    siteName: 'John Doe Photography',
    images: [
      {
        url: '[https://johndoe-portfolio.com/og-cover.jpg](https://johndoe-portfolio.com/og-cover.jpg)',
        width: 1200,
        height: 630,
        alt: 'John Doe Photography Portfolio Cover',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'John Doe | Fine Art & Editorial Photographer',
    description: 'Professional portfolio showcasing fine art, editorial, and commercial photography.',
    images: ['[https://johndoe-portfolio.com/og-cover.jpg](https://johndoe-portfolio.com/og-cover.jpg)'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

```

### B. Dynamic Metadata for Portfolio Shoots (`/portfolio/[slug]/page.tsx`)

For dynamic pages, agents must implement `generateMetadata` to pull specific project titles and cover images:

```tsx
import type { Metadata } from 'next';
import { getProjectBySlug } from '@/lib/data';

interface Props {
  params: { slug: string };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const project = await getProjectBySlug(params.slug);

  if (!project) {
    return { title: 'Project Not Found' };
  }

  return {
    title: project.title,
    description: project.description,
    openGraph: {
      title: `${project.title} | John Doe Photography`,
      description: project.description,
      url: `[https://johndoe-portfolio.com/portfolio/$](https://johndoe-portfolio.com/portfolio/$){project.slug}`,
      images: [{ url: project.coverImage, width: 1200, height: 630, alt: project.title }],
    },
  };
}

```

---

## 3. Semantic HTML Structure Requirements

To satisfy modern search engine crawlers and screen readers, React components must utilize correct semantic HTML5 landmarks rather than generic `div` elements:

* **`<header>`:** Contains top-level navigation, branding, and site header controls.
* **`<main>`:** Wraps the primary unique content of the active route. Exactly one `<main>` element per page.
* **`<nav>`:** Wraps primary navigation link lists or pagination controls.
* **`<section>`:** Defines distinct thematic groupings of content (e.g., Hero Section, Gallery Grid, Bio Section).
* **`<article>`:** Wraps independent, self-contained units of content (e.g., individual project showcase cards or blog posts).
* **`<footer>`:** Contains site-wide copyright, legal links, and secondary footer menus.

---

## 4. Automated Sitemap & Robots Configuration

Generated applications must provide programmatic sitemaps to accelerate search engine indexing.

### Dynamic Sitemap Generator (`app/sitemap.ts`)

```tsx
import { MetadataRoute } from 'next';
import { getAllProjects } from '@/lib/data';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  baseUrl = '[https://johndoe-portfolio.com](https://johndoe-portfolio.com)';

  // Fetch dynamic portfolio project slugs
  const projects = await getAllProjects();
  const projectUrls = projects.map((project) => ({
    url: `${baseUrl}/portfolio/${project.slug}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: 0.8,
  }));

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 1.0,
    },
    {
      url: `${baseUrl}/portfolio`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.9,
    },
    {
      url: `${baseUrl}/about`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    {
      url: `${baseUrl}/contact`,
      lastModified: new Date(),
      changeFrequency: 'yearly',
      priority: 0.5,
    },
    ...projectUrls,
  ];
}

