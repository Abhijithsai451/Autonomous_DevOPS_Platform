---
id: KB-007
title: Frontend Architecture and Component Patterns
domain: frontend_engineering · component_architecture · nextjs_patterns
target_agent: frontend_developer_agent
version: 1.0.0
status: approved
description: Software engineering standards for building modular, reusable React/Next.js components, scalable routing, layout wrappers, and robust interaction patterns.
---

# Knowledge Base Document: KB-007
**Title:** Frontend Architecture and Component Patterns  
**Domain:** Frontend Engineering · Component Architecture · Next.js Patterns  

---

## 1. Purpose and Operational Mandate
The primary objective of `KB-007` is to instruct the Frontend Engineering Agent on how to write modular, maintainable, and type-safe frontend code. It enforces component architecture standards, component file structures, Next.js App Router conventions, and interactive state patterns to ensure generated applications are clean, performant, and enterprise-ready.

---

## 2. Directory & Component Architecture Standard

Generated applications must strictly adhere to the modular **Next.js App Router** structure below:

```text
src/
├── app/                        # App Router Pages & Layouts
│   ├── layout.tsx              # Root Layout Shell
│   ├── page.tsx                # Home Page Route
│   ├── portfolio/
│   │   ├── page.tsx            # Portfolio Gallery Route
│   │   └── [slug]/
│   │       └── page.tsx        # Dynamic Project Detail Route
│   ├── about/
│   │   └── page.tsx            # About Route
│   └── contact/
│       └── page.tsx            # Contact Form Route
├── components/                 # Reusable UI Components
│   ├── ui/                     # Low-level primitive components (Button, Input, Modal)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── modal.tsx
│   ├── gallery/                # Domain-specific components
│   │   ├── gallery-grid.tsx
│   │   ├── gallery-filter.tsx
│   │   └── lightbox-modal.tsx
│   └── layout/                 # Global shell components
│       ├── navbar.tsx
│       ├── footer.tsx
│       └── container.tsx
├── lib/                        # Utility functions & API clients
│   ├── utils.ts                # Tailwind class merge (cn utility)
│   └── data.ts                 # Data fetching / mock data access
└── types/                      # TypeScript definitions
    └── index.ts
```
## 3. Server Components vs. Client Components Execution Strategy
Agents must implement Next.js Server Components (RSC) by default and isolate Client Components strictly to interactive trees:

### A. Server Components (page.tsx, layout.tsx)
* Default for all page views, layouts, and static content displays.
* Direct fetching of mock data or static JSON without sending JavaScript bundles to the browser.
* High SEO score and fast initial page render.

### B. Client Components ('use client')
* Required only for components with browser state or hooks (useState, useEffect, event listeners).
* Examples: lightbox-modal.tsx (handles click events/keyboard traps), gallery-filter.tsx (manages active tag filter), contact-form.tsx (manages input validation and form submission state).

## 4. Reusable UI Component Recipe Standards
Every primitive component in components/ui/ must follow strict TypeScript interface definitions and support tailwind utility merging using clsx / tailwind-merge (cn helper).

Example: Standard Button Primitive (components/ui/button.tsx)

```typescript
import * as React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50';
    
    const variants = {
      primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
      secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
      outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
      ghost: 'hover:bg-accent hover:text-accent-foreground',
    };

    const sizes = {
      sm: 'h-9 px-3 text-xs',
      md: 'h-10 px-4 py-2 text-sm',
      lg: 'h-11 px-8 text-base',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Button.displayName = 'Button';
```
## 5. Interaction Patterns & Error Boundaries
1. Loading & Empty States: Every dynamic gallery component or list view must include explicit loading skeleton components (Skeleton.tsx) and empty state fallbacks ("No images found in this category").
2. Accessible Modals: Lightbox and modal components must handle keydown ESC events, lock background scrolling (document.body.style.overflow = 'hidden'), and return focus to the trigger button when closed.
3. Form Actions: Contact forms must utilize client-side state hooks or Server Actions with clear feedback messaging (idle, submitting, success, error).