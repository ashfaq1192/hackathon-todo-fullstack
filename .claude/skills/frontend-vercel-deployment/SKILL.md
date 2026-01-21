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
| **Node.js Version** | 20 (must match package.json engines) |

### Environment Variables (Vercel Dashboard)

Set these in Vercel Dashboard → Project → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://hackathon-todo-fullstack-backend-production.up.railway.app
NEXT_PUBLIC_BETTER_AUTH_URL=https://hackathon-todo-fullstack.vercel.app
BETTER_AUTH_URL=https://hackathon-todo-fullstack.vercel.app
BETTER_AUTH_SECRET=<generate-secure-random-string>
JWT_SECRET_KEY=<must-match-backend-jwt-secret>
DATABASE_URL=<neon-postgresql-connection-string>
```

## Critical Configuration Files

### 1. vercel.json (Simplified - Recommended)

**Location:** `phase-3-chatbot/frontend/vercel.json`

```json
{
  "framework": "nextjs",
  "installCommand": "npm install",
  "buildCommand": "npm run build",
  "outputDirectory": ".next"
}
```

**IMPORTANT:**
- Keep vercel.json minimal - Vercel auto-detects most settings
- Do NOT include `env` section with `@secret-name` references
- Use Vercel Dashboard for environment variables
- Avoid custom headers/regions unless specifically needed

### 2. .nvmrc (Required)

**Location:** `phase-3-chatbot/frontend/.nvmrc`

```
20
```

**IMPORTANT:** Node version must match `package.json` engines field. If package.json requires `>=20.0.0 <21.0.0`, use `20` in .nvmrc (NOT `22`).

### 3. next.config.js

**Location:** `phase-3-chatbot/frontend/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  typescript: {
    ignoreBuildErrors: true,  // Remove after fixing type errors
  },
  turbopack: {
    resolveAlias: {
      '@': require('path').join(__dirname, '.'),
    },
  },
};

module.exports = nextConfig;
```

**IMPORTANT:**
- Do NOT use `eslint.ignoreDuringBuilds` in Next.js 16 (not supported)
- ESLint is skipped by default in production builds

### 4. tsconfig.json

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

## Deployment Methods

### Method 1: Vercel CLI (Recommended)

Deploy from the **repository root** (NOT the frontend folder):

```bash
# Navigate to repo root
cd /path/to/hackathon-todo-fullstack

# Link to project (first time only)
vercel link --project hackathon-todo-fullstack --yes

# Deploy to production
vercel --prod
```

**Why deploy from repo root?** Vercel project settings have `Root Directory: phase-3-chatbot/frontend`. If you run `vercel` from within the frontend folder, Vercel looks for `phase-3-chatbot/frontend/phase-3-chatbot/frontend` (doubled path).

### Method 2: GitHub Integration (Automatic)

1. Connect repo to Vercel
2. Set **Root Directory** to `phase-3-chatbot/frontend`
3. Commits to `main` auto-deploy

**Caveat:** GitHub-triggered builds clone the repo fresh, so:
- `.vercel` folder doesn't exist (gitignored)
- Environment variables must be set in Vercel Dashboard
- Build settings come from project configuration

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

### Error: "ENOENT: no such file or directory lstat '.../.claude/settings.local.json'"

**Cause:** Corrupted file permissions (common in WSL)

**Fix:**
```bash
rm -f .claude/settings.local.json
echo "{}" > .claude/settings.local.json
```

### Error: "The provided path does not exist" (doubled path)

**Cause:** Running `vercel` from frontend folder when Root Directory is already set

**Fix:** Run `vercel --prod` from **repository root**, not from `phase-3-chatbot/frontend`

### Error: "EBADENGINE Unsupported engine" warnings

**Cause:** Node version mismatch between .nvmrc and package.json

**Fix:** Ensure .nvmrc contains `20` (not `22`) to match `package.json` engines: `>=20.0.0 <21.0.0`

### Error: "Invalid next.config.js - Unrecognized key 'eslint'"

**Cause:** Next.js 16 doesn't support eslint config in next.config.js

**Fix:** Remove the `eslint` section from next.config.js

## Deployment Checklist

- [ ] Root Directory set to `phase-3-chatbot/frontend` in Vercel Dashboard
- [ ] vercel.json uses `npm` (not `pnpm`)
- [ ] vercel.json is minimal (no env, no headers unless needed)
- [ ] .nvmrc contains `20` (matches package.json engines)
- [ ] tsconfig.json has `baseUrl: "."` and `moduleResolution: "node"`
- [ ] next.config.js has no `eslint` section
- [ ] Environment variables set in Vercel Dashboard
- [ ] Deploy from repo root (not frontend folder)

## Quick Deploy Command

From repo root:
```bash
cd /path/to/hackathon-todo-fullstack && vercel --prod
```

## URLs

- **Production:** https://hackathon-todo-fullstack.vercel.app
- **Vercel Dashboard:** https://vercel.com/ashfaq1192s-projects/hackathon-todo-fullstack
- **Backend API:** https://hackathon-todo-fullstack-backend-production.up.railway.app
