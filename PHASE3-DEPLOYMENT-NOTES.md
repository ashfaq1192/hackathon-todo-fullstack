# Phase-III Deployment Notes

> **Created**: 2026-01-18
> **Last Updated**: 2026-01-18 (Session End)
> **Purpose**: Resume deployment work in next session
> **Status**: Code pushed to GitHub, deployment configuration update needed

---

## Latest Progress (Session End - 2026-01-18)

### Completed Today

| Task | Status |
|------|--------|
| Improved chatbot-mcp-integration skill | ✅ Done |
| Committed all changes (422 files) | ✅ Done |
| Pushed phase-3-chatbot branch | ✅ Done |
| Merged to main branch | ✅ Done |
| Fixed exposed Gemini API key | ✅ Done |
| Pushed security fix | ✅ Done |

### Pending (Do Tomorrow)

| Task | Status |
|------|--------|
| Revoke old Gemini API key | ⚠️ **DO THIS FIRST** |
| Generate new Gemini API key | ⏳ Pending |
| Update Railway root directory | ⏳ Pending |
| Add GEMINI_API_KEY to Railway | ⏳ Pending |
| Update Vercel root directory | ⏳ Pending |
| Redeploy and test | ⏳ Pending |

---

## Why Deployments Failed

Railway and Vercel deployments failed because the **project structure changed**:

| Platform | Looking For | Actual Location |
|----------|-------------|-----------------|
| Railway (Backend) | `/backend/` | `/phase-3-chatbot/backend/` |
| Vercel (Frontend) | `/frontend/` | `/phase-3-chatbot/frontend/` |

**This is expected.** The deployments will work after updating the root directory settings.

---

## Security Issue Fixed

A Gemini API key was accidentally committed in `.env.example`:

```
# Exposed key (now in git history)
AIzaSyAKYVRrPQHmbEbu07oe0a-OKG12wKTm398
```

**Action Required:**
1. Go to https://makersuite.google.com/app/apikey
2. Delete/revoke the key starting with `AIzaSyAKYVRr...`
3. Generate a new API key
4. Use the new key for deployment

---

## Tomorrow's Deployment Steps

### Step 1: Revoke Old API Key (Security)
```
1. Go to https://makersuite.google.com/app/apikey
2. Find and delete the exposed key
3. Create a new API key
4. Save the new key for Step 3
```

### Step 2: Update Railway (Backend)

```
1. Go to Railway dashboard: https://railway.app/dashboard
2. Select your backend service
3. Go to Settings → Root Directory
4. Change from: (empty or "backend")
   Change to: phase-3-chatbot/backend
5. Go to Variables tab
6. Add new variable:
   - GEMINI_API_KEY = (your new key from Step 1)
   - GEMINI_MODEL = gemini-2.0-flash-exp
7. Click "Deploy" or wait for auto-deploy
```

### Step 3: Update Vercel (Frontend)

```
1. Go to Vercel dashboard: https://vercel.com/dashboard
2. Select your frontend project
3. Go to Settings → General → Root Directory
4. Change from: (empty or "frontend")
   Change to: phase-3-chatbot/frontend
5. Go to Settings → Environment Variables (optional)
6. Add if needed:
   - NEXT_PUBLIC_CHATKIT_API_ENDPOINT = (your Railway URL)
7. Click "Redeploy" from Deployments tab
```

### Step 4: Verify Deployment

```bash
# Test backend health
curl https://your-railway-url.up.railway.app/health

# Test chat endpoint (replace with actual values)
curl -X POST https://your-railway-url.up.railway.app/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'

# Test frontend
# Visit https://your-vercel-url.vercel.app
```

---

## Git Status

```
Repository: https://github.com/ashfaq1192/hackathon-todo-fullstack
Branch: main (up to date)
Last Commit: fix: Remove exposed Gemini API key from .env.example
Commit Hash: 9afae16
```

Both branches are in sync:
- `main` ✅
- `phase-3-chatbot` ✅

---

## Environment Variables Reference

### Railway (Backend) - Required

| Variable | Value | Notes |
|----------|-------|-------|
| `DATABASE_URL` | (existing) | Keep same Neon connection |
| `JWT_SECRET_KEY` | (existing) | Keep same secret |
| `CORS_ORIGINS` | (existing) | Keep same, update if frontend URL changes |
| `GEMINI_API_KEY` | (new key) | **Add new - get from Google AI Studio** |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | **Add new** |

### Vercel (Frontend) - Required

| Variable | Value | Notes |
|----------|-------|-------|
| `NEXT_PUBLIC_API_URL` | (existing) | Keep same Railway URL |
| `BETTER_AUTH_URL` | (existing) | Keep same |
| `DATABASE_URL` | (existing) | Keep same Neon connection |
| `JWT_SECRET_KEY` | (existing) | Must match backend |

---

## Checklist for Tomorrow

```
[ ] 1. Revoke exposed Gemini API key (SECURITY - DO FIRST)
[ ] 2. Generate new Gemini API key
[ ] 3. Update Railway root directory to: phase-3-chatbot/backend
[ ] 4. Add GEMINI_API_KEY to Railway environment variables
[ ] 5. Add GEMINI_MODEL to Railway environment variables
[ ] 6. Verify Railway deployment succeeds
[ ] 7. Update Vercel root directory to: phase-3-chatbot/frontend
[ ] 8. Verify Vercel deployment succeeds
[ ] 9. Test chat functionality end-to-end
[ ] 10. Submit GitHub URL and Vercel URL to instructor
```

---

## URLs to Submit to Instructor

After successful deployment:

| Resource | URL |
|----------|-----|
| GitHub Repository | https://github.com/ashfaq1192/hackathon-todo-fullstack |
| Frontend (Vercel) | https://your-project.vercel.app |
| Backend (Railway) | https://your-backend.up.railway.app |

---

## Resume Command for Next Session

When starting a new session, tell Claude:

```
Read PHASE3-DEPLOYMENT-NOTES.md and help me complete the Phase-III deployment.
The deployments failed because root directories need to be updated.
```

---

## Important Notes

1. **Deployments will fail until root directories are updated** - This is expected behavior after project restructuring.

2. **Database tables auto-create** - Conversation and Message tables will be created automatically on first request (handled by SQLModel lifespan manager).

3. **Gemini Rate Limits** - Free tier allows 15 requests/minute, 1500/day. Circuit breaker handles this gracefully.

4. **Cold Start** - First request after deploy takes 15-25 seconds (Vercel/Railway cold start + Gemini init).

5. **JWT must match** - Ensure `JWT_SECRET_KEY` is identical on both frontend and backend.
