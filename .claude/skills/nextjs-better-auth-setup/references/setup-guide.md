# Better Auth Setup Guide

Complete step-by-step guide for implementing Better Auth in a Next.js application.

## Table of Contents

1. [Installation](#installation)
2. [File Structure](#file-structure)
3. [Environment Configuration](#environment-configuration)
4. [Database Migration](#database-migration)
5. [Implementation Steps](#implementation-steps)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Installation

Install required dependencies:

```bash
npm install better-auth pg jose
npm install --save-dev @better-auth/cli

# For React Hook Form (optional, for form components)
npm install react-hook-form @hookform/resolvers zod
```

**Dependencies explained:**
- `better-auth`: Core authentication library
- `pg`: PostgreSQL client for database connection
- `jose`: JWT generation and validation
- `@better-auth/cli`: CLI tool for database migrations
- `react-hook-form`, `@hookform/resolvers`, `zod`: Form validation (optional)

## File Structure

Create the following directory structure:

```
your-app/
├── lib/
│   ├── auth/
│   │   ├── auth.ts          # Better Auth config (server-side)
│   │   └── client.ts        # Better Auth client (client-side)
│   └── validation/
│       └── schemas.ts       # Zod validation schemas
├── app/
│   ├── api/
│   │   ├── auth/
│   │   │   └── [...betterauth]/
│   │   │       └── route.ts # Better Auth route handler
│   │   └── token/
│   │       └── route.ts     # JWT token generation endpoint
│   ├── (auth)/              # Auth route group
│   │   ├── signup/
│   │   │   └── page.tsx     # Signup page
│   │   └── login/
│   │       └── page.tsx     # Login page
│   └── dashboard/
│       └── page.tsx         # Protected dashboard
└── components/
    └── auth/
        ├── SignupForm.tsx
        └── LoginForm.tsx
```

## Environment Configuration

1. Create `.env.local` file in your project root
2. Copy contents from `assets/.env.example` in this skill
3. Generate required secrets:

```bash
# Generate BETTER_AUTH_SECRET (minimum 32 characters)
openssl rand -base64 32

# Generate JWT_SECRET_KEY (if using separate backend)
openssl rand -hex 32
```

4. Set up Neon PostgreSQL:
   - Visit [https://console.neon.tech](https://console.neon.tech)
   - Create a new project
   - Copy the connection string
   - Add to `.env.local` as `DATABASE_URL`

**Critical:** Ensure `?sslmode=require` is appended to your `DATABASE_URL`

## Database Migration

Run the Better Auth migration to create required database tables:

```bash
npx @better-auth/cli migrate --config lib/auth/auth.ts
```

This creates the following tables:
- `user` - User accounts (id, email, name, password hash, etc.)
- `session` - Active sessions (id, user_id, expires_at, etc.)
- `account` - OAuth accounts (if using OAuth providers)
- `verification` - Email verification tokens

**Verify migration success:**

```sql
-- Connect to your database and run:
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('user', 'session', 'account', 'verification');
```

## Implementation Steps

### Step 1: Configure Better Auth (Server-Side)

Copy `assets/auth-config.ts` to `lib/auth/auth.ts`

**Key configuration points:**
- `database`: PostgreSQL connection pool with SSL
- `emailAndPassword.enabled`: Set to `true`
- `emailAndPassword.requireEmailVerification`: Set to `false` initially (enable after setting up email service)
- `secret`: Must be at least 32 characters (from `BETTER_AUTH_SECRET`)
- `baseURL`: Your Next.js app URL
- `trustedOrigins`: Add backend API URL if using separate backend

### Step 2: Create Auth Client (Client-Side)

Copy `assets/auth-client.ts` to `lib/auth/client.ts`

**Usage in components:**
```typescript
import { authClient } from '@/lib/auth/client';

// Signup
await authClient.signUp.email({ email, password, name });

// Login
await authClient.signIn.email({ email, password });

// Logout
await authClient.signOut();

// Get session (React hook)
const { data: session } = authClient.useSession();
```

### Step 3: Set Up API Routes

**a) Better Auth Route Handler**

Copy `assets/auth-route.ts` to `app/api/auth/[...betterauth]/route.ts`

This single route handles all Better Auth endpoints:
- `POST /api/auth/sign-up/email`
- `POST /api/auth/sign-in/email`
- `POST /api/auth/sign-out`
- `GET /api/auth/get-session`

**b) JWT Token Generation Route (Optional)**

If you have a separate backend API that requires JWT tokens:

Copy `assets/token-route.ts` to `app/api/token/route.ts`

This endpoint:
1. Validates the Better Auth session
2. Generates a JWT token with `user_id` claim
3. Returns the token to be used for backend API authentication

### Step 4: Create Validation Schemas

Copy `assets/validation-schemas.ts` to `lib/validation/schemas.ts`

**Password requirements enforced:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Step 5: Create Auth Forms

**a) Signup Form**

Copy `assets/SignupForm.tsx` to `components/auth/SignupForm.tsx`

**Features:**
- React Hook Form integration
- Zod schema validation
- Loading states
- Error handling
- Auto-redirect on success
- JWT token initialization (if using backend API)

**b) Login Form**

Copy `assets/LoginForm.tsx` to `components/auth/LoginForm.tsx`

**Features:**
- Same as SignupForm
- "Forgot password?" link
- Specific error messages for common scenarios

### Step 6: Create Auth Pages

**a) Signup Page (`app/(auth)/signup/page.tsx`)**

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

**b) Login Page (`app/(auth)/login/page.tsx`)**

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

### Step 7: Protect Routes (Optional)

Create a middleware to protect routes that require authentication:

**`middleware.ts` (project root):**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth/auth';

export async function middleware(request: NextRequest) {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  // Redirect to login if not authenticated
  if (!session && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*'], // Add paths to protect
};
```

## Testing

### Manual Testing

1. **Signup Flow:**
   ```bash
   # Visit http://localhost:3000/signup
   # Fill in: Name, Email, Password, Confirm Password
   # Submit form
   # Verify redirect to /dashboard
   # Verify session cookie is set (check DevTools → Application → Cookies)
   ```

2. **Login Flow:**
   ```bash
   # Visit http://localhost:3000/login
   # Fill in: Email, Password
   # Submit form
   # Verify redirect to /dashboard
   # Verify session cookie is set
   ```

3. **Logout Flow:**
   ```bash
   # While logged in, call:
   await authClient.signOut();
   # Verify redirect to /login
   # Verify session cookie is cleared
   ```

4. **Session Persistence:**
   ```bash
   # After logging in, refresh the page
   # Verify user remains logged in
   # Verify session is still valid (check auth state)
   ```

### Automated Testing (Optional)

**Unit test for SignupForm:**

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SignupForm } from '@/components/auth/SignupForm';

test('validates email format', async () => {
  render(<SignupForm />);

  const emailInput = screen.getByLabelText(/email/i);
  fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
  fireEvent.blur(emailInput);

  await waitFor(() => {
    expect(screen.getByText(/invalid email address/i)).toBeInTheDocument();
  });
});
```

## Troubleshooting

### Common Issues

**1. "SSL connection required" error**

**Cause:** Neon PostgreSQL requires SSL connections

**Solution:** Ensure your `DATABASE_URL` includes `?sslmode=require`:
```
postgresql://user:pass@host/db?sslmode=require
```

**2. "Migration failed" error**

**Cause:** Database connection issues or tables already exist

**Solution:**
- Verify `DATABASE_URL` is correct in `.env.local`
- Check if tables already exist: `SELECT * FROM user LIMIT 1;`
- If tables exist, skip migration
- If connection fails, verify Neon database is running

**3. "Session not found" error**

**Cause:** Cookie not being set or expired session

**Solution:**
- Check browser DevTools → Application → Cookies
- Verify `better_auth_session` cookie exists
- Ensure `BETTER_AUTH_URL` matches your app's URL
- Check session expiration (default: 7 days)

**4. "BETTER_AUTH_SECRET not set" error**

**Cause:** Environment variable missing or `.env.local` not loaded

**Solution:**
- Verify `.env.local` exists in project root
- Ensure variable is set: `BETTER_AUTH_SECRET=your-secret-here`
- Restart dev server after adding `.env.local`

**5. "User already exists" error on signup**

**Cause:** Email already registered

**Solution:**
- Use a different email address
- Or delete the existing user from database:
  ```sql
  DELETE FROM "user" WHERE email = 'user@example.com';
  DELETE FROM "session" WHERE user_id = 'user-id-here';
  ```

**6. "Invalid credentials" on login**

**Cause:** Wrong password or user doesn't exist

**Solution:**
- Verify email is correct
- Reset password or create new account
- Check if user exists in database:
  ```sql
  SELECT id, email FROM "user" WHERE email = 'user@example.com';
  ```

**7. TypeScript errors in form components**

**Cause:** Missing type definitions or imports

**Solution:**
- Ensure all dependencies are installed
- Create type definitions in `types/auth.ts`:
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

**8. 401 errors when calling backend API**

**Cause:** JWT token not being sent or invalid

**Solution:**
- Verify `initializeApiToken()` was called after login
- Check localStorage for `api_token`
- Verify `JWT_SECRET_KEY` matches between frontend and backend
- Check token expiration (default: 7 days)

### Debug Mode

Enable Better Auth debug logging:

```typescript
// lib/auth/auth.ts
export const auth = betterAuth({
  // ... other config
  logger: {
    level: 'debug', // Enable debug logging
  },
});
```

Check server logs for detailed error messages.

## Next Steps

After completing the setup:

1. **Add password reset functionality** - Use `password-reset-auth` skill
2. **Implement email verification** - Set up Resend and enable `requireEmailVerification`
3. **Add OAuth providers** - GitHub, Google, etc. (Better Auth supports many providers)
4. **Customize session duration** - Adjust `session.cookieCache.maxAge`
5. **Add user profile management** - Update user name, email, password
6. **Implement role-based access control (RBAC)** - Add user roles and permissions

## Resources

- [Better Auth Documentation](https://www.better-auth.com/docs)
- [Neon PostgreSQL Docs](https://neon.tech/docs)
- [React Hook Form Docs](https://react-hook-form.com/)
- [Zod Validation Docs](https://zod.dev/)
