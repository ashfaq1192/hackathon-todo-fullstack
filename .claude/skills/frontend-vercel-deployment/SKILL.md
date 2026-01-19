---
name: frontend-vercel-deployment
description: Deploy Next.js frontend to Vercel with correct configuration. Use when (1) Deploying frontend to Vercel, (2) Debugging Vercel build failures, (3) Setting up Vercel project linking, (4) Configuring Next.js for production builds, (5) Troubleshooting path alias resolution issues.
---

# Frontend Vercel Deployment

This skill provides step-by-step instructions for deploying the Next.js frontend to Vercel, including all configuration settings that work for this project.

## Project Configuration

### Verified Working Settings

| Setting | Value |
|---------|-------|
| **Platform** | Vercel |
| **Framework** | Next.js 16.x |
| **Package Manager** | npm (NOT pnpm) |
| **Root Directory** | `phase-3-chatbot/frontend` |
| **Build Command** | `npm run build` |
| **Install Command** | `npm install` |

### Environment Variables (Vercel Dashboard)

Set these in Vercel Dashboard → Project → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://hackathon-todo-fullstack-backend-production.up.railway.app
BETTER_AUTH_URL=https://hackathon-todo-fullstack.vercel.app
BETTER_AUTH_SECRET=<generate-secure-random-string>
JWT_SECRET_KEY=<must-match-backend-jwt-secret>
```

## Critical Configuration Files

### 1. vercel.json

**Location:** `phase-3-chatbot/frontend/vercel.json`

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "installCommand": "npm install",
  "devCommand": "npm run dev",
  "regions": ["iad1"],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

**IMPORTANT:** Do NOT include `env` section with `@secret-name` references. Use Vercel Dashboard for environment variables.

### 2. next.config.js

**Location:** `phase-3-chatbot/frontend/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Note: eslint config not supported in Next.js 16
  typescript: {
    ignoreBuildErrors: true,  // Remove after fixing type errors
  },
};

module.exports = nextConfig;
```

**IMPORTANT:**
- Do NOT use `eslint.ignoreDuringBuilds` in Next.js 16 (not supported)
- ESLint is skipped by default in production builds

### 3. tsconfig.json

**Location:** `phase-3-chatbot/frontend/tsconfig.json`

Critical settings for path alias resolution:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "moduleResolution": "node",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

**IMPORTANT:**
- `baseUrl: "."` is REQUIRED for `@/*` path aliases
- Use `moduleResolution: "node"` (NOT "bundler") for Webpack compatibility

### 4. package.json

**Location:** `phase-3-chatbot/frontend/package.json`

```json
{
  "scripts": {
    "build": "next build"
  },
  "dependencies": {
    "next": "^16.1.3"
  }
}
```

## Deployment Methods

### Method 1: Vercel CLI (Recommended for Debugging)

```bash
# Navigate to repo root (NOT frontend folder)
cd /path/to/hackathon-todo-fullstack

# Link to project (first time only)
vercel link --project hackathon-todo-fullstack --yes

# Deploy to production
vercel --prod
```

**Watch build logs in real-time** - This is faster for debugging than checking Vercel Dashboard.

### Method 2: GitHub Integration (Automatic)

1. Connect repo to Vercel
2. Set **Root Directory** to `phase-3-chatbot/frontend`
3. Commits to `main` auto-deploy

## Common Errors and Fixes

### Error: "Module not found: Can't resolve '@/lib/...'"

**Cause:** Path alias resolution failure

**Fix:**
1. Add `"baseUrl": "."` to tsconfig.json
2. Change `"moduleResolution": "bundler"` to `"moduleResolution": "node"`
3. Verify Root Directory is set correctly in Vercel

### Error: "Command 'pnpm install' exited with 1"

**Cause:** Wrong package manager

**Fix:** Update vercel.json:
```json
"installCommand": "npm install",
"buildCommand": "npm run build"
```

### Error: "Secret 'backend-url' does not exist"

**Cause:** vercel.json has `@secret-name` references

**Fix:** Remove `env` section from vercel.json. Set variables in Vercel Dashboard instead.

### Error: "Invalid next.config.js - Unrecognized key 'eslint'"

**Cause:** Next.js 16 doesn't support eslint config in next.config.js

**Fix:** Remove the `eslint` section from next.config.js

### Error: "ENOENT: no such file or directory '(dashboard)'"

**Cause:** Conflicting route groups in app directory

**Fix:** Check for duplicate folders like `app/(dashboard)` and `app/dashboard`. Remove the route group if not needed.

## Deployment Checklist

- [ ] Root Directory set to `phase-3-chatbot/frontend` in Vercel
- [ ] vercel.json uses `npm` (not `pnpm`)
- [ ] No `@secret-name` references in vercel.json
- [ ] tsconfig.json has `baseUrl: "."` and `moduleResolution: "node"`
- [ ] next.config.js has no `eslint` section
- [ ] Environment variables set in Vercel Dashboard
- [ ] No conflicting route groups in app directory

## Quick Deploy Command

From repo root:
```bash
cd /path/to/hackathon-todo-fullstack && vercel --prod
```

## URLs

- **Production:** https://hackathon-todo-fullstack.vercel.app
- **Vercel Dashboard:** https://vercel.com/ashfaq1192s-projects/hackathon-todo-fullstack
