# Deployment Guide

This guide covers deploying the Todo App with AI Chatbot to Vercel.

## Prerequisites

1. Vercel account (https://vercel.com)
2. Vercel CLI installed: `npm i -g vercel`
3. Neon PostgreSQL database (already configured)
4. Gemini API key (https://makersuite.google.com/app/apikey)

## Environment Variables

### Backend (Vercel Dashboard)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Neon PostgreSQL connection | `postgresql://user:pass@host/db?sslmode=require` |
| `JWT_SECRET_KEY` | JWT signing secret (match frontend) | `your-32-char-secret` |
| `GEMINI_API_KEY` | Google AI Studio API key | `AIzaSy...` |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.5-flash` |
| `CORS_ORIGINS` | Frontend URL | `https://your-frontend.vercel.app` |

### Frontend (Vercel Dashboard)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://your-backend.vercel.app` |
| `BETTER_AUTH_URL` | Frontend URL (for auth) | `https://your-frontend.vercel.app` |
| `BETTER_AUTH_SECRET` | Better Auth secret | `your-32-char-secret` |
| `DATABASE_URL` | Same Neon PostgreSQL | `postgresql://...` |
| `JWT_SECRET_KEY` | Must match backend | `your-32-char-secret` |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | ChatKit domain key (optional) | `ck_...` |

## Deployment Steps

### 1. Deploy Backend

```bash
cd backend

# Login to Vercel (first time only)
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

Note the deployment URL (e.g., `https://hackathon-todo-backend.vercel.app`)

### 2. Configure Backend Environment Variables

In Vercel Dashboard:
1. Go to your backend project
2. Settings → Environment Variables
3. Add all backend variables from the table above

### 3. Deploy Frontend

```bash
cd frontend

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### 4. Configure Frontend Environment Variables

In Vercel Dashboard:
1. Go to your frontend project
2. Settings → Environment Variables
3. Add all frontend variables from the table above
4. Set `NEXT_PUBLIC_API_URL` to your backend URL

### 5. Verify Deployment

1. Visit your frontend URL
2. Sign up for a new account
3. Navigate to /chat
4. Test the chatbot:
   - "Add a task to buy groceries"
   - "Show my tasks"
   - "Complete task 1"

## ChatKit Domain Verification (Optional)

For production ChatKit features:

1. Go to https://platform.openai.com/settings/organization/chatkit
2. Add your Vercel domain (e.g., `your-frontend.vercel.app`)
3. Copy the domain verification key
4. Add as `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` in Vercel

## Troubleshooting

### CORS Errors
- Verify `CORS_ORIGINS` includes your frontend URL
- Check the URL has no trailing slash

### Database Connection Errors
- Ensure `DATABASE_URL` includes `?sslmode=require`
- Verify the IP is allowed in Neon dashboard

### JWT Token Errors
- Ensure `JWT_SECRET_KEY` matches between frontend and backend
- Check token expiration

### Gemini API Errors
- Verify `GEMINI_API_KEY` is valid
- Check rate limits (15 req/min free tier)

### Cold Start Latency
- First request may take 15-25 seconds
- Subsequent requests should be 2-5 seconds
- Consider using Vercel's cron jobs to keep functions warm

## Monitoring

After deployment, monitor:
- Vercel Dashboard → Functions → Logs
- Neon Dashboard → Activity
- Rate limit headers in API responses

## Rollback

If issues occur:
```bash
# List deployments
vercel ls

# Rollback to previous deployment
vercel rollback [deployment-url]
```
