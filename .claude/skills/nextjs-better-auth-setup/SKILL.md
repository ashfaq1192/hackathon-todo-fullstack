---
name: nextjs-better-auth-setup
description: Production-ready Better Auth integration for Next.js applications with PostgreSQL, JWT tokens in httpOnly cookies, signup/login forms with validation, and session management. Use when implementing authentication in Next.js apps, specifically for (1) Setting up Better Auth with Neon PostgreSQL or other PostgreSQL providers, (2) Creating signup and login forms with React Hook Form and Zod validation, (3) Implementing JWT-based authentication for separate backend APIs, (4) Managing sessions with httpOnly cookies for XSS protection, (5) Adding user authentication to existing Next.js projects, (6) Building secure auth flows with TypeScript type safety
---

# Next.js Better Auth Setup

Production-ready Better Auth integration for Next.js 16+ with PostgreSQL database.

## Overview

This skill provides complete templates for implementing Better Auth in Next.js applications. It includes server and client configuration, signup/login forms with validation, JWT token generation for backend APIs, and production security best practices.

**Key Features:**
- JWT tokens in httpOnly cookies (XSS protection)
- Password validation (8+ chars, uppercase, lowercase, number, special char)
- Auto-redirect on 401 Unauthorized
- Session persistence (7 days default)
- TypeScript type safety
- React Hook Form + Zod validation
- Loading states and error handling

## Quick Start

### 1. Install Dependencies

```bash
npm install better-auth pg jose
npm install --save-dev @better-auth/cli
npm install react-hook-form @hookform/resolvers zod  # For forms
```

### 2. Set Up Environment Variables

Copy `assets/.env.example` to `.env.local` in your project root and configure:

```bash
# Generate secrets
openssl rand -base64 32  # For BETTER_AUTH_SECRET
openssl rand -hex 32     # For JWT_SECRET_KEY (if using backend)

# Required environment variables:
BETTER_AUTH_SECRET=...           # Minimum 32 characters
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://...?sslmode=require  # Neon or other PostgreSQL
```

**Critical:** Ensure `DATABASE_URL` includes `?sslmode=require` for Neon PostgreSQL

### 3. Create File Structure

Copy these asset files to your project:

| Asset File | Destination Path | Purpose |
|------------|------------------|---------|
| `auth-config.ts` | `lib/auth/auth.ts` | Server-side Better Auth config |
| `auth-client.ts` | `lib/auth/client.ts` | Client-side auth helper |
| `auth-route.ts` | `app/api/auth/[...betterauth]/route.ts` | Better Auth route handler |
| `token-route.ts` | `app/api/token/route.ts` | JWT token generation (optional) |
| `SignupForm.tsx` | `components/auth/SignupForm.tsx` | Signup form component |
| `LoginForm.tsx` | `components/auth/LoginForm.tsx` | Login form component |
| `validation-schemas.ts` | `lib/validation/schemas.ts` | Zod validation schemas |

### 4. Run Database Migration

```bash
npx @better-auth/cli migrate --config lib/auth/auth.ts
```

This creates required tables: `user`, `session`, `account`, `verification`

### 5. Create Auth Pages

**Signup Page (`app/(auth)/signup/page.tsx`):**

```typescript
import { SignupForm } from '@/components/auth/SignupForm';

export default function SignupPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-6">Sign Up</h1>
        <SignupForm />
      </div>
    </div>
  );
}
```

**Login Page (`app/(auth)/login/page.tsx`):**

```typescript
import { LoginForm } from '@/components/auth/LoginForm';

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-6">Log In</h1>
        <LoginForm />
      </div>
    </div>
  );
}
```

### 6. Use Auth in Components

```typescript
import { authClient } from '@/lib/auth/client';

// Get current session
const { data: session, isPending, error } = authClient.useSession();

// Logout
await authClient.signOut();

// Check if authenticated
if (session) {
  console.log('User:', session.user.email);
}
```

## Authentication Flow

**Signup Flow:**
1. User fills signup form → validates with Zod schema
2. `authClient.signUp.email()` → Better Auth creates user + session
3. `initializeApiToken()` → generates JWT for backend API (optional)
4. Redirect to `/dashboard`

**Login Flow:**
1. User fills login form → validates with Zod schema
2. `authClient.signIn.email()` → Better Auth validates credentials + creates session
3. `initializeApiToken()` → generates JWT for backend API (optional)
4. Redirect to `/dashboard`

**Session Management:**
- Session stored in httpOnly cookie (`better_auth_session`)
- 7-day expiration (configurable in `auth.ts`)
- Auto-refresh on page load
- 401 errors trigger auto-redirect to `/login`

## JWT Token Integration (Optional)

If you have a separate backend API that requires JWT authentication:

**After login:**
```typescript
import { initializeApiToken } from '@/lib/api/client';

// Called automatically in SignupForm and LoginForm
const tokenData = await initializeApiToken();
// Stores token in localStorage as 'api_token'
```

**Token endpoint (`app/api/token/route.ts`):**
- Validates Better Auth session
- Generates JWT with `user_id` claim
- Uses `JWT_SECRET_KEY` (must match backend)
- 7-day expiration

**Backend validation:**
```python
# FastAPI example
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

def get_current_user(credentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Integration with ChatKit

When using the OpenAI ChatKit for a conversational UI, it's crucial to ensure that the user's authentication context (from Better Auth) is correctly passed to the ChatKit component and subsequently to your backend chat endpoint.

**Challenge:** ChatKit needs to know *who* the authenticated user is to make calls to your backend that are tied to that specific user's session.

**Solution:** The most straightforward way is to retrieve the authenticated user's JWT token (or a session ID) on the client-side and provide it to ChatKit's configuration. Your backend's `/api/chatkit/session` endpoint (if used) should then validate this token and generate a ChatKit session that respects the user's identity.

**Client-Side Integration Example (Conceptual):**

```typescript
// frontend/components/chat/ChatInterface.tsx (conceptual)
import { useSession } from '@/lib/auth/client'; // From Better Auth client
import { getApiToken } from '@/lib/api/client'; // Helper to retrieve JWT

// ... inside your ChatKit component or setup function
const { data: session } = useSession(); // Get Better Auth session

// Only render ChatKit if authenticated
if (!session) {
  return <div>Please log in to use the chatbot.</div>;
}

// Assume ChatKit uses a backend endpoint to establish its session
// Your backend's /api/chatkit/session endpoint will receive the JWT
// via a standard Authorization header or a custom mechanism.
// This endpoint must validate the JWT and return appropriate ChatKit config.

const chatkitConfig = {
  // ... other ChatKit configuration
  apiEndpoint: process.env.NEXT_PUBLIC_CHATKIT_API_ENDPOINT, // Your custom backend
  // Potentially pass the JWT to a token provider endpoint if ChatKit supports it
  // tokenProviderEndpoint: '/api/chatkit/token-provider', // Your endpoint that returns a valid token
};

// ... then initialize ChatKit with chatkitConfig
```

**Backend `/api/chatkit/session` Endpoint (Conceptual):**

Your backend endpoint (e.g., `phase-3-chatbot/backend/src/api/routes/chatkit.py` or similar) responsible for providing ChatKit session data must:

1.  Receive the JWT token from the frontend (e.g., in the `Authorization` header).
2.  Validate the JWT using the same mechanism as other protected routes.
3.  Extract the `user_id` from the token.
4.  Generate and return the necessary ChatKit session configuration, including the `user_id` so that subsequent ChatKit calls made by the SDK to your backend can be associated with the correct user.
```

## Protect Routes with Middleware

Create `middleware.ts` in project root to protect authenticated routes:

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth/auth';

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  if (!session && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'],
};
```

## UI Components Required

The forms use these reusable UI components (not included in skill, create as needed):

**Button Component (`components/ui/Button.tsx`):**
```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  disabled?: boolean;
  type?: 'submit' | 'button';
  className?: string;
  children: React.ReactNode;
}
```

**Input Component (`components/ui/Input.tsx`):**
```typescript
interface InputProps {
  label?: string;
  error?: string;
  type?: string;
  required?: boolean;
  disabled?: boolean;
  // ...standard input props
}
```

## TypeScript Types

Create `types/auth.ts`:

```typescript
export interface SignupPayload {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}
```

## Configuration Options

**In `lib/auth/auth.ts`:**

```typescript
export const auth = betterAuth({
  database: pool,
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,  // Set to true for email verification
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24 * 7,  // 7 days (adjust as needed)
    },
  },
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL,
  trustedOrigins: [
    process.env.BETTER_AUTH_URL,
    process.env.NEXT_PUBLIC_API_URL,  // Add backend API URL
  ].filter(Boolean),
});
```

## Security Best Practices

✅ **Implemented:**
- JWT in httpOnly cookies (XSS protection)
- HTTPS enforced in production
- Password strength requirements
- Auto-redirect on 401 Unauthorized
- Session expiration (7 days default)
- PostgreSQL with SSL/TLS (sslmode=require)

✅ **Additional recommendations:**
- Enable email verification (`requireEmailVerification: true`)
- Add rate limiting on auth endpoints
- Implement CSRF protection
- Use environment variables for secrets
- Never commit `.env.local` to version control

## Detailed Documentation

For comprehensive setup instructions, troubleshooting, and testing:

**Read:** `references/setup-guide.md`

**Covers:**
- Complete installation steps
- Database migration details
- Protected route implementation
- Manual and automated testing
- Common issues and solutions
- Debug mode configuration

## Common Issues

**"SSL connection required":**
- Ensure `DATABASE_URL` includes `?sslmode=require`

**"Migration failed":**
- Verify `DATABASE_URL` is correct
- Check if tables already exist
- Ensure Neon database is running

**"Session not found":**
- Check browser cookies for `better_auth_session`
- Verify `BETTER_AUTH_URL` matches app URL
- Check session expiration

**Full troubleshooting guide:** See `references/setup-guide.md` section "Troubleshooting"
