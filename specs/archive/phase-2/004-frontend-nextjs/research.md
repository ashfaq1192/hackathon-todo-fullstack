# Research: Next.js Frontend Application

**Date**: 2025-12-24
**Feature**: 004-frontend-nextjs
**Phase**: Phase 0 - Technical Research

## Overview

This document captures research findings for implementing the Next.js 16+ frontend with Better Auth authentication, Tailwind CSS 4+, and integration with the FastAPI backend. All unknowns from the Technical Context have been researched and decisions documented.

---

## Research Areas

### 1. Next.js 16+ App Router Best Practices

**Question**: What are the current best practices for Next.js 16+ App Router architecture, especially for authentication and API integration?

**Research Findings**:
- **App Router Structure**: Use route groups `(auth)` and `(dashboard)` to organize pages without affecting URL structure
- **Server vs Client Components**: Default to Server Components, use `'use client'` only for interactive components (forms, buttons with onClick)
- **Data Fetching**: Use Server Components for initial data loading, Client Components for mutations
- **Authentication**: Middleware pattern for route protection (check JWT, redirect if unauthenticated)
- **API Routes**: Use `app/api/` for backend-for-frontend patterns (e.g., Better Auth integration)

**Decision**:
- Structure: Use route groups for organization
- Authentication: Implement middleware for protected routes + Better Auth API routes
- Components: Server Components for layouts/pages, Client Components for forms/interactive UI
- API Integration: Client-side fetch in Client Components, Server Components can call backend directly

**Alternatives Considered**:
- Pages Router (legacy): Rejected - App Router is the current standard for Next.js 13+
- getServerSideProps pattern: Rejected - replaced by Server Components in App Router

**References**:
- Next.js 16 App Router Documentation
- Better Auth Next.js Integration Guide

---

### 2. Better Auth Integration with Next.js 16

**Question**: How does Better Auth integrate with Next.js 16 App Router, and what are the setup requirements?

**Research Findings**:
- **Installation**: `npm install better-auth`
- **Configuration**: Create `lib/auth/better-auth.ts` with Better Auth client configuration
- **API Route**: Create `app/api/auth/[...betterauth]/route.ts` to handle auth requests
- **Environment Variables**: Requires `BETTER_AUTH_SECRET` (min 32 characters), `BETTER_AUTH_URL`, `DATABASE_URL` (if using database sessions)
- **Token Storage**: Better Auth uses httpOnly cookies by default (XSS protection)
- **Session Management**: Provides `useSession()` hook for client-side, `getSession()` for server-side
- **User Model**: Better Auth manages its own user table (email, hashed password, sessions)

**Decision**:
- Use Better Auth with default httpOnly cookie storage (aligns with NFR-006)
- Configure API route at `/api/auth/[...betterauth]`
- Use `useSession()` hook in Client Components for user state
- Implement middleware to protect dashboard routes

**Alternatives Considered**:
- NextAuth.js: Rejected - Better Auth is lighter and more modern
- Custom JWT implementation: Rejected - Better Auth handles edge cases and security

**Implementation Notes**:
```typescript
// lib/auth/better-auth.ts
import { BetterAuth } from 'better-auth';

export const auth = new BetterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  database: {
    // Optional: Better Auth can use its own user DB or integrate with existing
    url: process.env.DATABASE_URL,
  },
  session: {
    cookieName: 'hackathon-todo-session',
    maxAge: 60 * 60 * 24 * 7, // 7 days
  },
});
```

**References**:
- Better Auth Documentation
- Better Auth Next.js Example

---

### 3. Tailwind CSS 4+ Setup and Configuration

**Question**: What are the key changes in Tailwind CSS 4 and how to configure it with Next.js 16?

**Research Findings**:
- **Installation**: `npm install tailwindcss@next postcss autoprefixer` (use `@next` tag for v4 beta)
- **Configuration**: `tailwind.config.ts` with `content` paths for purging unused styles
- **CSS Import**: Import in `app/globals.css` with `@tailwind base; @tailwind components; @tailwind utilities;`
- **JIT Mode**: Enabled by default in Tailwind 4 (generates styles on-demand)
- **New Features in v4**: Native CSS cascade layers, improved color palette, better dark mode support
- **Typography**: Use system font stack or install `@next/font` for web fonts

**Decision**:
- Use Tailwind CSS 4 beta (as specified in constitution Phase II requirements)
- Configure content paths to scan `app/**/*.tsx`, `components/**/*.tsx`
- Use default color palette with custom primary colors (blue) and semantic colors (success, danger)
- Use system font stack (Inter, system-ui, sans-serif) for performance

**Alternatives Considered**:
- Tailwind CSS 3: Rejected - requirements specify Tailwind 4+
- CSS Modules: Rejected - Tailwind provides utility-first approach preferred for rapid development
- Styled Components: Rejected - requires runtime CSS-in-JS, adds bundle size

**Configuration Example**:
```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          dark: '#2563eb',
        },
        success: '#10b981',
        danger: '#ef4444',
      },
    },
  },
  plugins: [],
};

export default config;
```

**References**:
- Tailwind CSS 4 Documentation
- Next.js + Tailwind Setup Guide

---

### 4. API Client with Retry Logic (Exponential Backoff)

**Question**: How to implement robust API client with 3 retries and exponential backoff (1s, 2s, 4s) per NFR-011?

**Research Findings**:
- **Axios vs Fetch**: Both support retry logic, Fetch is native and lighter
- **Retry Libraries**: `axios-retry` for Axios, `fetch-retry` for Fetch, or custom implementation
- **Exponential Backoff**: Delay increases exponentially: 1s, 2s, 4s (2^n * base delay)
- **Retry Conditions**: Retry on network errors (`Failed to fetch`), NOT on 4xx/5xx status codes
- **Circuit Breaker**: For production, consider circuit breaker pattern to prevent cascading failures

**Decision**:
- Use native `fetch` with custom retry logic (lighter than Axios)
- Implement retry wrapper function with exponential backoff
- Retry only on network errors, NOT on HTTP error status codes
- Max 3 retries with delays [1000, 2000, 4000] milliseconds

**Alternatives Considered**:
- Axios with axios-retry: Rejected - adds dependency when native fetch is sufficient
- No retry logic: Rejected - NFR-011 requires retry for resilience
- Infinite retries: Rejected - can hang the app

**Implementation**:
```typescript
// lib/api/client.ts
async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const maxRetries = 3;
  const retryDelays = [1000, 2000, 4000];

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.getAuthToken()}`,
          ...options?.headers,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'API request failed');
      }

      return response.json();
    } catch (error) {
      if (attempt < maxRetries && error.message === 'Failed to fetch') {
        await new Promise(resolve => setTimeout(resolve, retryDelays[attempt]));
        continue;
      }
      throw error;
    }
  }
}
```

**References**:
- MDN Fetch API
- Exponential Backoff Algorithm

---

### 5. Form Validation with React Hook Form and Zod

**Question**: What's the best approach for form validation in Next.js with TypeScript?

**Research Findings**:
- **React Hook Form**: Popular library (42k+ GitHub stars), minimal re-renders, TypeScript support
- **Zod**: Schema validation library that integrates with React Hook Form, provides TypeScript types
- **Integration**: Use `@hookform/resolvers/zod` to connect Zod schemas to React Hook Form
- **Validation Rules**:
  - Email: Zod `.email()` validator
  - Password: `.min(8)` for minimum length
  - Title: `.min(1).max(200)` for required title with max length
  - Description: `.max(1000).optional()` for optional description

**Decision**:
- Use React Hook Form for form state management
- Use Zod for schema validation
- Define validation schemas in separate files (`lib/validation/schemas.ts`)
- Display validation errors inline with form fields

**Alternatives Considered**:
- Formik: Rejected - React Hook Form has better performance (fewer re-renders)
- Yup: Rejected - Zod has better TypeScript integration and type inference
- Manual validation: Rejected - error-prone and verbose

**Implementation Example**:
```typescript
// lib/validation/schemas.ts
import { z } from 'zod';

export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export const createTaskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200, 'Title must be less than 200 characters'),
  description: z.string().max(1000, 'Description must be less than 1000 characters').optional(),
});

// components/auth/LoginForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const { register, handleSubmit, formState: { errors } } = useForm({
  resolver: zodResolver(loginSchema),
});
```

**References**:
- React Hook Form Documentation
- Zod Documentation
- @hookform/resolvers

---

### 6. Testing Strategy (Vitest + Playwright)

**Question**: How to set up testing for Next.js 16 with Vitest (unit tests) and Playwright (E2E tests)?

**Research Findings**:
- **Vitest**: Fast test runner compatible with Vite and Next.js, Jest-compatible API
- **React Testing Library**: De facto standard for React component testing
- **Playwright**: Modern E2E testing framework from Microsoft, supports all browsers
- **Coverage**: Vitest built-in coverage with `vitest --coverage` using v8 or istanbul

**Vitest Setup**:
```bash
npm install -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

**Playwright Setup**:
```bash
npm install -D playwright @playwright/test
npx playwright install
```

**Decision**:
- Unit Tests: Vitest + React Testing Library for components and utilities
- E2E Tests: Playwright for full user flows (auth, CRUD operations)
- Coverage Target: 70%+ for MVP, 75%+ for production-ready
- Test Structure: Mirror source structure (`__tests__/components/`, `e2e/`)

**Alternatives Considered**:
- Jest: Rejected - Vitest is faster and has better ES modules support
- Cypress: Rejected - Playwright has better developer experience and native TypeScript support

**Configuration Example**:
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './__tests__/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      threshold: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70,
      },
    },
  },
});
```

**References**:
- Vitest Documentation
- Playwright Documentation
- React Testing Library

---

### 7. Vercel Deployment Configuration

**Question**: How to configure Next.js 16 deployment to Vercel with environment variables?

**Research Findings**:
- **Build Command**: `next build` (automatic for Next.js projects)
- **Environment Variables**: Set in Vercel dashboard under Settings → Environment Variables
- **Variable Types**:
  - Build-time: Available during build (e.g., `NEXT_PUBLIC_API_URL`)
  - Runtime: Available at runtime (e.g., `BETTER_AUTH_SECRET`)
- **NEXT_PUBLIC_ Prefix**: Required for variables exposed to browser (client-side)
- **HTTPS**: Automatic with Vercel domains
- **Domains**: Custom domains supported with DNS configuration

**Decision**:
- Deploy via Vercel GitHub integration (auto-deploy on push)
- Configure environment variables in Vercel dashboard:
  - `NEXT_PUBLIC_API_URL` (backend API URL)
  - `BETTER_AUTH_SECRET` (server-side only)
  - `BETTER_AUTH_URL` (frontend URL)
- Use `.env.example` to document required variables

**Alternatives Considered**:
- Netlify: Rejected - Vercel has better Next.js integration (creators of Next.js)
- AWS Amplify: Rejected - more complex setup than needed
- Self-hosted: Rejected - Vercel provides HTTPS and CDN automatically

**Deployment Checklist**:
- [ ] Connect GitHub repository to Vercel
- [ ] Set environment variables in Vercel dashboard
- [ ] Configure build settings (default Next.js settings)
- [ ] Deploy and verify HTTPS works
- [ ] Test authentication flow on deployed URL
- [ ] Test API integration with backend

**References**:
- Vercel Next.js Deployment Guide
- Vercel Environment Variables Documentation

---

### 8. Responsive Design Breakpoints

**Question**: What breakpoint strategy should be used for mobile-first responsive design?

**Research Findings**:
- **Tailwind Default Breakpoints**:
  - `sm`: 640px (mobile landscape, small tablets)
  - `md`: 768px (tablets)
  - `lg`: 1024px (laptops, small desktops)
  - `xl`: 1280px (desktops)
  - `2xl`: 1536px (large desktops)
- **Mobile-First Approach**: Write base styles for mobile, use breakpoint prefixes for larger screens
- **Common Device Sizes**:
  - Mobile: 320px - 480px (iPhone SE, standard phones)
  - Tablet: 768px - 1024px (iPad, Android tablets)
  - Desktop: 1280px+ (laptops, monitors)

**Decision**:
- Use Tailwind's default breakpoints (no customization needed)
- Mobile-first approach: base styles for mobile (< 640px), `md:` for tablet, `lg:` for desktop
- Test at key breakpoints: 320px, 768px, 1440px
- Touch targets minimum 44x44px on mobile (WCAG accessibility)

**Alternatives Considered**:
- Custom breakpoints: Rejected - Tailwind defaults cover all common devices
- Desktop-first: Rejected - mobile-first is industry standard

**Responsive Patterns**:
```tsx
// Stack on mobile, grid on desktop
<div className="flex flex-col gap-4 md:grid md:grid-cols-2 lg:grid-cols-3">
  {tasks.map(task => <TaskItem key={task.id} task={task} />)}
</div>

// Full-width buttons on mobile, inline on tablet+
<div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
  <button className="w-full sm:w-auto">Cancel</button>
  <button className="w-full sm:w-auto">Save</button>
</div>
```

**References**:
- Tailwind Responsive Design Documentation
- WCAG 2.1 Touch Target Guidelines

---

## Summary

All technical unknowns have been researched and decisions documented. Key outcomes:

1. **Architecture**: Next.js 16 App Router with route groups, Server + Client Components
2. **Authentication**: Better Auth with httpOnly cookies, middleware for route protection
3. **Styling**: Tailwind CSS 4 with mobile-first responsive design
4. **API Integration**: Custom fetch wrapper with exponential backoff retry logic
5. **Forms**: React Hook Form + Zod for validation
6. **Testing**: Vitest (unit) + Playwright (E2E), 70%+ coverage target
7. **Deployment**: Vercel with environment variables, automatic HTTPS
8. **Responsive**: Tailwind default breakpoints (640px, 768px, 1024px, 1280px)

No blocking issues identified. All technologies are mature with strong documentation and community support. Ready to proceed to Phase 1: Design & Contracts.

---

**Next Phase**: Phase 1 - Generate data-model.md, contracts/, and quickstart.md
