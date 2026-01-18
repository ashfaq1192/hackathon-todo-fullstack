# Quickstart Guide: Next.js Frontend Development

**Feature**: 004-frontend-nextjs
**Last Updated**: 2025-12-24

## Overview

This quickstart guide helps developers set up the Next.js 16+ frontend for local development, run tests, and deploy to Vercel. Follow these steps sequentially to get the application running.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Node.js 18+ installed (`node --version`)
- ✅ pnpm installed (`npm install -g pnpm` if not present)
- ✅ Git configured
- ✅ Backend API running at `http://localhost:8000` (from Stage 2: 003-backend-api)
- ✅ Text editor (VS Code recommended)

---

## Initial Setup

### 1. Create Frontend Directory

```bash
# From repository root
mkdir -p frontend
cd frontend
```

### 2. Initialize Next.js Project

```bash
# Create Next.js 16+ project with TypeScript
pnpm create next-app@latest . --typescript --tailwind --app --eslint

# Answer prompts:
# ✓ Use TypeScript? Yes
# ✓ Use ESLint? Yes
# ✓ Use Tailwind CSS? Yes
# ✓ Use `src/` directory? No
# ✓ Use App Router? Yes
# ✓ Customize import alias? No (@/* is default)
```

### 3. Install Dependencies

```bash
# Core dependencies
pnpm add better-auth react-hook-form zod @hookform/resolvers axios

# Development dependencies
pnpm add -D @types/node @types/react @types/react-dom
pnpm add -D vitest @vitejs/plugin-react @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
pnpm add -D playwright @playwright/test
pnpm add -D @vitest/coverage-v8
```

### 4. Configure Environment Variables

Create `.env.local`:
```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

Create `.env.example`:
```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth (NEVER commit .env.local with real secrets)
BETTER_AUTH_SECRET=your-secret-key-minimum-32-characters-long
BETTER_AUTH_URL=http://localhost:3000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

**Security Note**: Never commit `.env.local` to version control. Add to `.gitignore`:
```bash
echo ".env.local" >> .gitignore
```

---

## Project Structure Setup

### 5. Create Directory Structure

```bash
# Create all required directories
mkdir -p app/{api/auth/[...betterauth],'(auth)'/login,'(auth)'/signup,'(dashboard)'}
mkdir -p components/{auth,tasks,layout,ui}
mkdir -p lib/{api,auth,utils,validation}
mkdir -p types
mkdir -p __tests__/{components,lib}
mkdir -p e2e
mkdir -p public
```

### 6. Configure TypeScript

Update `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "paths": {
      "@/*": ["./*"]
    },
    "plugins": [
      {
        "name": "next"
      }
    ]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 7. Configure Tailwind CSS

Update `tailwind.config.ts`:
```typescript
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

### 8. Configure Vitest

Create `vitest.config.ts`:
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './__tests__/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        '__tests__/',
        '*.config.ts',
        '.next/',
      ],
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
});
```

Create `__tests__/setup.ts`:
```typescript
import '@testing-library/jest-dom';
import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);

afterEach(() => {
  cleanup();
});
```

### 9. Configure Playwright

```bash
# Initialize Playwright
pnpm create playwright
```

Update `playwright.config.ts`:
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

### 10. Update package.json Scripts

Add these scripts to `package.json`:
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "format": "prettier --write \"**/*.{ts,tsx,md,json}\"",
    "format:check": "prettier --check \"**/*.{ts,tsx,md,json}\""
  }
}
```

---

## Development Workflow

### 11. Start Development Server

```bash
# Terminal 1: Backend API (from repository root)
cd backend
source .venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2: Frontend (from repository root)
cd frontend
pnpm dev
```

**Verify**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 12. Run Type Checking

```bash
# Check TypeScript errors
pnpm type-check

# Expected output: No errors (exit code 0)
```

### 13. Run Linting

```bash
# Run ESLint
pnpm lint

# Fix auto-fixable issues
pnpm lint --fix
```

### 14. Run Unit Tests

```bash
# Run all unit tests
pnpm test

# Run tests in watch mode
pnpm test

# Run tests with coverage
pnpm test:coverage

# View coverage report
open coverage/index.html  # macOS
xdg-open coverage/index.html  # Linux
start coverage/index.html  # Windows
```

**Coverage Thresholds**:
- MVP: 70%+ coverage
- Production-Ready: 75%+ coverage

### 15. Run E2E Tests

```bash
# Run E2E tests (headless)
pnpm test:e2e

# Run E2E tests with UI
pnpm test:e2e:ui

# Run specific test file
pnpm test:e2e e2e/auth.spec.ts
```

---

## Building for Production

### 16. Build Application

```bash
# Create production build
pnpm build

# Expected output:
# ✓ Compiled successfully
# ✓ Collecting page data
# ✓ Generating static pages
# ✓ Finalizing page optimization
```

### 17. Test Production Build Locally

```bash
# Start production server
pnpm start

# Access at http://localhost:3000
```

### 18. Verify Production Build

**Checklist**:
- [ ] No build errors
- [ ] No TypeScript errors (`pnpm type-check`)
- [ ] No console errors in browser
- [ ] All pages load correctly
- [ ] Authentication flow works
- [ ] CRUD operations functional
- [ ] Responsive design verified (mobile, tablet, desktop)

---

## Deployment to Vercel

### 19. Install Vercel CLI (Optional)

```bash
# Install globally
npm install -g vercel

# Login to Vercel
vercel login
```

### 20. Deploy via GitHub Integration (Recommended)

**Steps**:
1. Push code to GitHub:
   ```bash
   git add .
   git commit -m "feat(frontend): complete Next.js implementation"
   git push origin 004-frontend-nextjs
   ```

2. Go to https://vercel.com/dashboard
3. Click "Import Project"
4. Select your GitHub repository
5. Configure project:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `pnpm build`
   - Output Directory: `.next`
6. Add environment variables:
   - `NEXT_PUBLIC_API_URL`: Your production backend API URL
   - `BETTER_AUTH_SECRET`: Your production secret (min 32 chars)
   - `BETTER_AUTH_URL`: Your Vercel app URL (e.g., https://hackathon-todo.vercel.app)
   - `NEXT_PUBLIC_BETTER_AUTH_URL`: Same as BETTER_AUTH_URL
7. Click "Deploy"

**Post-Deployment**:
- Copy deployed URL (e.g., https://hackathon-todo.vercel.app)
- Update backend CORS settings to allow this origin
- Test authentication flow on deployed URL
- Verify all API integrations work

### 21. Deploy via Vercel CLI

```bash
# From frontend directory
cd frontend

# Deploy to production
vercel --prod

# Follow prompts to configure deployment
```

---

## Troubleshooting

### Issue: Backend API Not Reachable

**Symptoms**: Network errors, "Failed to fetch"

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS settings in backend allow `http://localhost:3000`
4. Check browser console for specific error messages

### Issue: Authentication Fails

**Symptoms**: Login returns 401, JWT not attached

**Solutions**:
1. Verify `BETTER_AUTH_SECRET` matches between frontend and backend
2. Check Better Auth configuration in `lib/auth/better-auth.ts`
3. Verify httpOnly cookies are enabled
4. Clear browser cookies and try again
5. Check browser console for JWT token in Authorization header

### Issue: Tests Failing

**Symptoms**: Unit tests or E2E tests fail

**Solutions**:
1. Run `pnpm install` to ensure dependencies are installed
2. Check `vitest.config.ts` and `playwright.config.ts` configurations
3. Verify test setup file exists: `__tests__/setup.ts`
4. Clear test cache: `rm -rf node_modules/.vitest`
5. Run single test to isolate issue: `pnpm test LoginForm.test.tsx`

### Issue: Build Fails

**Symptoms**: `pnpm build` exits with error

**Solutions**:
1. Run type check: `pnpm type-check` and fix TypeScript errors
2. Run lint: `pnpm lint --fix` to auto-fix issues
3. Check for missing dependencies: `pnpm install`
4. Clear Next.js cache: `rm -rf .next`
5. Rebuild: `pnpm build`

---

## Development Checklist

### Before Starting Implementation
- [ ] Backend API running at `http://localhost:8000`
- [ ] `.env.local` created with correct values
- [ ] Dependencies installed (`pnpm install`)
- [ ] Directory structure created
- [ ] Configuration files in place (tsconfig, tailwind, vitest, playwright)

### During Development
- [ ] Run type check frequently (`pnpm type-check`)
- [ ] Write tests alongside components (TDD)
- [ ] Test in browser at multiple breakpoints (320px, 768px, 1440px)
- [ ] Check console for errors/warnings
- [ ] Commit after each completed task

### Before Deployment
- [ ] All tests passing (`pnpm test` and `pnpm test:e2e`)
- [ ] 70%+ test coverage achieved
- [ ] No TypeScript errors (`pnpm type-check`)
- [ ] No lint errors (`pnpm lint`)
- [ ] Production build succeeds (`pnpm build`)
- [ ] Manual testing complete (auth, CRUD, responsive)
- [ ] Environment variables documented in `.env.example`

---

## Useful Commands Reference

```bash
# Development
pnpm dev                  # Start dev server
pnpm build                # Build for production
pnpm start                # Start production server

# Code Quality
pnpm type-check           # TypeScript check
pnpm lint                 # Run ESLint
pnpm lint --fix           # Fix ESLint issues
pnpm format               # Format code with Prettier

# Testing
pnpm test                 # Run unit tests
pnpm test:coverage        # Run tests with coverage
pnpm test:e2e             # Run E2E tests
pnpm test:e2e:ui          # Run E2E tests with UI

# Deployment
vercel                    # Deploy to Vercel (preview)
vercel --prod             # Deploy to Vercel (production)
```

---

## Next Steps

After completing this quickstart:

1. **Implement Core Components**: Follow `tasks.md` (generated by `/sp.tasks`)
2. **Write Tests**: Achieve 70%+ coverage per Development Standards
3. **Test Integration**: Verify frontend ↔ backend communication
4. **Deploy**: Push to Vercel and test in production
5. **Demo Video**: Record <90 second demo showing all features

---

## Resources

- [Next.js 16 Documentation](https://nextjs.org/docs)
- [Better Auth Docs](https://www.better-auth.com/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Vitest Docs](https://vitest.dev/)
- [Playwright Docs](https://playwright.dev/)
- [React Hook Form](https://react-hook-form.com/)
- [Zod Validation](https://zod.dev/)

---

**Questions?** Check `specs/004-frontend-nextjs/spec.md` for requirements or `specs/004-frontend-nextjs/contracts/backend-api.md` for API details.
