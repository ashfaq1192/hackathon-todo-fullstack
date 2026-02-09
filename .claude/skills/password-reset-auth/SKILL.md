---
name: password-reset-auth
description: Complete password reset functionality with email verification using Better Auth and Resend. Use when implementing forgot password flows with email verification, password reset pages with secure token validation, email service integration for password resets, professional HTML email templates for authentication, password validation with security requirements, or adding password reset to existing Next.js and Better Auth applications.
---

# Password Reset with Email Verification

Implement complete, production-ready password reset functionality with Better Auth and Resend email service.

## Quick Start

**Prerequisites:**
- Next.js 13+ with App Router
- Better Auth configured
- PostgreSQL database
- Resend account (free tier: 100 emails/day)

**Installation:**

1. Install dependencies:
```bash
npm install better-auth resend zod react-hook-form @hookform/resolvers
```

2. Copy bundled resources:
   - `assets/forgot-password-page.tsx` → `app/(auth)/forgot-password/page.tsx`
   - `assets/reset-password-page.tsx` → `app/(auth)/reset-password/page.tsx`
   - `assets/email-client.ts` → `lib/email/client.ts`
   - `assets/validation-schemas.ts` → Add to your schemas file
   - `assets/.env.example` → Reference for environment variables

3. Configure Better Auth server (`lib/auth/auth.ts`):

```typescript
import { betterAuth } from "better-auth";
import { Pool } from "pg";
import { sendPasswordResetEmail } from "@/lib/email/client";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

export const auth = betterAuth({
  database: pool,
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
    sendResetPassword: async ({ user, url }) => {
      return await sendPasswordResetEmail(user.email, url);
    },
  },
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL,
});
```

4. Set environment variables (see `assets/.env.example`):

```bash
# Required
RESEND_API_KEY=re_your_key_here
BETTER_AUTH_SECRET=your_secret_here
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://connection_string

# Optional
RESEND_FROM_EMAIL=onboarding@resend.dev
NEXT_PUBLIC_APP_NAME=Your App Name
```

5. Run database migration:
```bash
npx @better-auth/cli migrate
```

## Implementation Steps

### Step 1: Set Up Email Service

Copy `assets/email-client.ts` to `lib/email/client.ts`.

**Key features:**
- Lazy initialization (prevents crashes when API key missing)
- Automatic fallback to console logging
- Professional HTML email templates
- Error handling with graceful degradation

### Step 2: Add Validation Schemas

Copy password validation schemas from `assets/validation-schemas.ts`.

**Security requirements enforced:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character
- Password confirmation matching

### Step 3: Create Forgot Password Page

Copy `assets/forgot-password-page.tsx` to `app/(auth)/forgot-password/page.tsx`.

**Flow:**
1. User enters email
2. Calls `authClient.requestPasswordReset()`
3. Shows success message
4. Email sent with reset link

**Critical:** Use `requestPasswordReset`, NOT `forgetPassword` (common mistake).

### Step 4: Create Reset Password Page

Copy `assets/reset-password-page.tsx` to `app/(auth)/reset-password/page.tsx`.

**Flow:**
1. Extracts token from URL (`?token=...`)
2. User enters new password
3. Calls `authClient.resetPassword({ newPassword, token })`
4. Redirects to login after success

### Step 5: Configure Better Auth

Update your Better Auth server configuration to include the `sendResetPassword` handler (see Quick Start above).

**Important settings:**
- `resetPasswordTokenExpiresIn`: Default 3600 seconds (1 hour)
- `requireEmailVerification`: Set to `false` for password reset to work without email verification

### Step 6: Test Locally

1. Navigate to `/forgot-password`
2. Enter test email
3. Check Next.js terminal for reset link (logged when email fails)
4. Copy URL and test password reset
5. Verify login with new password

## Production Deployment

See `references/deployment-guide.md` for:
- Vercel environment variable configuration
- Resend domain verification
- Custom domain setup
- Email delivery options

**Quick deployment:**
1. Add environment variables in Vercel dashboard
2. Deploy application
3. Test with your verified Resend email
4. (Optional) Verify custom domain for all users

## Troubleshooting

See `references/troubleshooting.md` for:
- Common errors and solutions
- Email delivery issues
- Resend 403 error fix
- Token validation problems
- Database connection issues

**Quick fixes:**

**"Unexpected end of JSON input":**
- Use `requestPasswordReset` not `forgetPassword`

**"Email sent but not received":**
- Check Resend dashboard
- Look for reset link in console logs
- Verify RESEND_API_KEY is set

**"Invalid token":**
- Token expired (1 hour limit)
- Request new password reset

## Customization

### Email Templates

Modify templates in `lib/email/client.ts`:

```typescript
function getPasswordResetEmailTemplate(resetUrl: string): string {
  // Customize HTML template
  return `...`;
}
```

**Customizable elements:**
- Colors and branding
- Logo and images
- Text content
- Button styles

### Password Requirements

Adjust in `validation-schemas.ts`:

```typescript
const passwordRequirements = {
  minLength: 8,  // Change minimum length
  hasUpperCase: /[A-Z]/,
  // Modify or remove requirements
};
```

### Token Expiration

Configure in Better Auth:

```typescript
emailAndPassword: {
  resetPasswordTokenExpiresIn: 7200,  // 2 hours
}
```

### Email Sender Name

Update in environment variables:

```bash
NEXT_PUBLIC_APP_NAME=Your Company Name
```

## Email Delivery Options

### Option 1: Development (Free)

```bash
RESEND_FROM_EMAIL=onboarding@resend.dev
```

- ✅ Free, works immediately
- ⚠️ Only sends to your Resend account email
- ✅ Reset links logged to console for testing

### Option 2: Verified Email (Free)

```bash
RESEND_FROM_EMAIL=your-verified-email@example.com
```

- ✅ Free, works for all users
- ⚠️ Emails come from personal address
- ✅ Good for hackathons/demos

### Option 3: Custom Domain (Production)

```bash
RESEND_FROM_EMAIL=noreply@yourdomain.com
```

- ✅ Professional, works for all users
- 💰 Requires domain ($10-15/year)
- ⏱️ Takes 24-48 hours to verify
- See `references/deployment-guide.md` for setup

## Security Considerations

**Token Security:**
- Tokens expire in 1 hour (configurable)
- Tokens are single-use
- Tokens stored securely in database

**Password Security:**
- Strong password requirements enforced
- Passwords hashed by Better Auth
- No password transmitted in emails

**Email Security:**
- Reset links contain cryptographically secure tokens
- Links expire automatically
- No sensitive data in email content

## Integration with Existing Apps

**If you already have:**

1. **Better Auth:** Just add email configuration and pages
2. **Custom auth:** Adapt components to your auth library
3. **Different email service:** Replace Resend with your provider
4. **Different UI library:** Copy logic, update UI components

## File Structure

```
app/
├── (auth)/
│   ├── forgot-password/
│   │   └── page.tsx
│   └── reset-password/
│       └── page.tsx
lib/
├── email/
│   └── client.ts
└── validation/
    └── schemas.ts
.env.local
```

## Dependencies

```json
{
  "dependencies": {
    "better-auth": "^1.4.9",
    "resend": "^3.0.0",
    "zod": "^3.22.0",
    "react-hook-form": "^7.50.0",
    "@hookform/resolvers": "^3.3.0"
  }
}
```

## Testing Checklist

- [ ] Forgot password page loads
- [ ] Email validation works
- [ ] Success message appears
- [ ] Reset link logged to console (development)
- [ ] Reset password page loads with token
- [ ] Password requirements enforced
- [ ] Password confirmation matching works
- [ ] New password can be set
- [ ] Login works with new password
- [ ] Token expires after use
- [ ] (Production) Email delivered successfully

## Common Patterns

**Add "Forgot Password" link to login page:**

```typescript
<Link href="/forgot-password" className="text-blue-600">
  Forgot password?
</Link>
```

**Redirect after password reset:**

```typescript
setTimeout(() => {
  router.push('/login?reset=success');
}, 2000);
```

**Show success message on login page:**

```typescript
const searchParams = useSearchParams();
const resetSuccess = searchParams.get('reset') === 'success';

{resetSuccess && (
  <div className="success-message">
    Password reset successful! Please login.
  </div>
)}
```

## Performance

- Email templates cached by Resend
- Database indexed on reset tokens
- Lazy loading of email client
- Console logging fallback (no network calls)

## Limitations

**Resend Free Tier:**
- 100 emails/day
- 3,000 emails/month
- Without domain: only verified email receives emails

**Better Auth:**
- Requires PostgreSQL database
- Token expiration not customizable per-request
- Single-use tokens only

## Next Steps

After implementation:
1. Test thoroughly in development
2. Deploy to staging environment
3. Test with real email addresses
4. Monitor Resend dashboard for delivery
5. (Optional) Verify custom domain
6. Deploy to production
7. Monitor error logs and email metrics

## Support

**Resources:**
- Better Auth docs: https://better-auth.com/docs
- Resend docs: https://resend.com/docs
- Deployment guide: `references/deployment-guide.md`
- Troubleshooting: `references/troubleshooting.md`

**Common issues:** See `references/troubleshooting.md`
