---
id: KB-015
title: Deployment and Hosting Blueprints
domain: devops · deployment · hosting · cicd · production_infrastructure
target_agent: devops_agent
version: 1.0.0
status: approved
description: Operational directives for deploying Next.js applications to production infrastructure, configuring automated CI/CD pipelines, managing environment variables, and executing post-deployment health checks.
---

# Knowledge Base Document: KB-015
**Title:** Deployment and Hosting Blueprints  
**Domain:** DevOps · Deployment · Hosting · CI/CD · Production Infrastructure  

---

## 1. Purpose and Operational Mandate
The primary objective of `KB-015` is to establish standard operating procedures for deploying generated applications to production hosting environments. 

It ensures that code passing the QA gates (`KB-013`) is automatically built, tested, and published to enterprise-grade cloud hosting platforms (such as Vercel or containerized cloud targets) with zero downtime and verified environment security.

---

## 2. Production Hosting Target Specification

For modern Next.js (App Router) applications, the DevOps Agent must default to **Vercel** or an equivalent serverless edge platform optimized for Next.js framework features (Server Actions, Server Components, Image Optimization, and Incremental Static Regeneration).

### Target Infrastructure Requirements:
* **Edge Routing & Global CDN:** Automatic edge caching and global asset distribution.
* **Serverless Execution:** Server-side functions auto-scaling seamlessly on demand.
* **Preview Deployments:** Automatic generation of unique preview URLs for every pull request or feature branch push.

---

## 3. Continuous Integration & Deployment (CI/CD) Pipeline (`.github/workflows/ci.yml`)

The DevOps agent must inject an automated GitHub Actions CI/CD workflow into `.github/workflows/ci.yml` to ensure every code change is validated before merging into `main` and deploying to production.

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate-and-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Install Dependencies
        run: npm ci

      - name: Run Type Checking
        run: npx tsc --noEmit

      - name: Run Linter
        run: npm run lint

      - name: Run Unit Tests
        run: npm run test -- --run

      - name: Build Production Bundle
        run: npm run build
        env:
          NEXT_PUBLIC_SITE_URL: [https://production-preview.internal](https://production-preview.internal)

  deploy-production:
    needs: validate-and-test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Deploy to Production Hosting
        uses: vercel/action@v3
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'

```

---

## 4. Environment Variables & Secrets Management

Production deployments require secure configuration of environment variables without exposing sensitive credentials in version control:

1. **Template Provisioning:** A documented `.env.example` file must exist in the root directory listing all required variables (`KB-014`).
2. **Platform Secret Injection:** Production secrets (`DATABASE_URL`, API private keys, service webhook secrets) must be injected directly through the hosting provider's secure dashboard or CLI secret manager (e.g., `vercel env add`).
3. **Public vs. Private Scope:** Variables intended for browser consumption must strictly use the `NEXT_PUBLIC_` prefix. All other variables must remain private server-side secrets.

---

## 5. Post-Deployment Verification & Health Checks

Once a deployment finishes publishing, the DevOps and QA agents must execute a final verification checklist:

1. **Live URL Availability:** Send a `GET` request to the production URL and verify a `200 OK` response code.
2. **SSL / TLS Validation:** Ensure HTTPS is strictly enforced and SSL certificates are valid.
3. **Asset Loading Check:** Confirm that CSS styles, font files, and image assets load correctly without 404 errors or mixed-content warnings.
4. **Interactive Smoke Test:** Verify that critical paths (such as portfolio navigation, lightbox inspection, and contact form submissions) function correctly in the live production environment.

```