# Phase-III Deployment Notes

> **Created**: 2026-01-18
> **Purpose**: Resume deployment work in next session
> **Status**: Ready to deploy after merging to main

---

## Current State

- **Branch**: `phase-3-chatbot` (ready to merge to main)
- **Phase-II Deployment**: Backend on Railway, Frontend on Vercel
- **Project Structure Changed**: Code now in `phase-3-chatbot/` subdirectory

---

## What Changed from Phase-II to Phase-III

| Aspect | Phase-II | Phase-III |
|--------|----------|-----------|
| **Code Location** | `backend/`, `frontend/` | `phase-3-chatbot/backend/`, `phase-3-chatbot/frontend/` |
| **New Dependencies** | - | `openai`, `swarm`, `mcp`, `tiktoken`, `tenacity` |
| **New Env Vars** | - | `GEMINI_API_KEY`, `GEMINI_MODEL` |
| **Database Tables** | Task | Task + Conversation + Message |
| **New Features** | Task CRUD | AI Chatbot with MCP tools |

---

## Required Deployment Changes

### 1. Railway (Backend)

**Update Root Directory:**
```
Settings → Root Directory: phase-3-chatbot/backend
```

**Add New Environment Variables:**

| Variable | Value | Required |
|----------|-------|----------|
| `GEMINI_API_KEY` | Get from https://makersuite.google.com/app/apikey | **YES** |
| `GEMINI_MODEL` | `gemini-2.0-flash-exp` | **YES** |
| `CHAT_CONTEXT_WINDOW_SIZE` | `15` | Optional (has default) |
| `RATE_LIMIT_REQUESTS` | `15` | Optional (has default) |

**Keep Existing (no changes needed):**
- `DATABASE_URL` - Same Neon PostgreSQL
- `JWT_SECRET_KEY` - Same key
- `CORS_ORIGINS` - Update only if frontend URL changes

### 2. Vercel (Frontend)

**Update Root Directory:**
```
Settings → Root Directory: phase-3-chatbot/frontend
```

**Add New Environment Variables (Optional):**

| Variable | Value | Required |
|----------|-------|----------|
| `NEXT_PUBLIC_CHATKIT_API_ENDPOINT` | Railway backend URL | Optional |
| `NEXT_PUBLIC_VOICE_INPUT_ENABLED` | `true` | Optional |

**Keep Existing (no changes needed):**
- `NEXT_PUBLIC_API_URL` - Same Railway URL
- `BETTER_AUTH_URL` - Same
- `DATABASE_URL` - Same Neon PostgreSQL
- `JWT_SECRET_KEY` - Must match backend

---

## Deployment Steps (Execute Tomorrow)

### Step 1: Push to GitHub
```bash
cd /mnt/e/projects/hackathon-todo-fullstack
git add .
git commit -m "Complete Phase-III AI Chatbot implementation"
git push origin phase-3-chatbot
```

### Step 2: Create PR and Merge to Main
```bash
gh pr create --title "Phase III: AI Chatbot with MCP Integration" --body "$(cat <<'EOF'
## Summary
- AI-powered chatbot for natural language task management
- MCP server with 5 tools (add, list, complete, update, delete tasks)
- OpenAI Swarm Agent + Gemini API (free tier) backend
- Circuit breaker and intent-based fallback for resilience
- Multilingual support (English + Urdu)

## Test plan
- [ ] Test chat endpoint: POST /api/{user_id}/chat
- [ ] Verify MCP tools execute correctly
- [ ] Test fallback when Gemini API fails
- [ ] Verify JWT authentication works

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"

# After PR is approved:
gh pr merge
```

### Step 3: Update Railway Settings
1. Go to Railway dashboard
2. Select your backend service
3. Settings → Root Directory → Change to `phase-3-chatbot/backend`
4. Add environment variables:
   - `GEMINI_API_KEY` = (your key from Google AI Studio)
   - `GEMINI_MODEL` = `gemini-2.0-flash-exp`
5. Click "Redeploy"

### Step 4: Update Vercel Settings
1. Go to Vercel dashboard
2. Select your frontend project
3. Settings → Root Directory → Change to `phase-3-chatbot/frontend`
4. Click "Redeploy"

### Step 5: Verify Deployment
1. Wait for both deployments to complete
2. Test the chat endpoint:
```bash
curl -X POST https://your-railway-url/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'
```
3. Test the frontend chat UI

---

## Checklist

- [ ] Get Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Push phase-3-chatbot branch to GitHub
- [ ] Create PR and merge to main
- [ ] Update Railway root directory to `phase-3-chatbot/backend`
- [ ] Add `GEMINI_API_KEY` to Railway environment variables
- [ ] Add `GEMINI_MODEL` to Railway environment variables
- [ ] Redeploy Railway backend
- [ ] Update Vercel root directory to `phase-3-chatbot/frontend`
- [ ] Redeploy Vercel frontend
- [ ] Test chat functionality
- [ ] Submit GitHub URL and Vercel URL to instructor

---

## Important Notes

1. **Same Database**: Neon PostgreSQL stays the same. New tables (Conversation, Message) auto-create on first request.

2. **Same Auth**: JWT authentication unchanged. Ensure `JWT_SECRET_KEY` matches on frontend and backend.

3. **Gemini Rate Limits**: Free tier = 15 requests/minute, 1500/day. Circuit breaker handles gracefully.

4. **Cold Start**: First request after deploy takes 15-25 seconds (Vercel cold start + Gemini init).

5. **Database Tables**: Created automatically by SQLModel on app startup (lifespan manager in main.py).

---

## URLs to Submit to Instructor

After deployment:
- **GitHub**: https://github.com/YOUR_USERNAME/hackathon-todo-fullstack
- **Frontend (Vercel)**: https://your-project.vercel.app
- **Backend (Railway)**: https://your-backend.up.railway.app

---

## Skills Updated in This Session

The `chatbot-mcp-integration` skill was improved:
- Expanded from 114 lines to 661 lines
- Added step-by-step implementation guide
- Added concrete code examples from Phase-3
- Added resilience patterns (circuit breaker, fallback)
- Added testing examples
- Removed all TODO placeholders

---

## Resume Command for Next Session

When starting a new session, tell Claude:
```
Please read the file PHASE3-DEPLOYMENT-NOTES.md in the project root to understand the current state and continue with Phase-III deployment.
```
