# Troubleshooting Guide - Password Reset

Common issues and solutions for password reset functionality.

## Frontend Issues

### "Unexpected end of JSON input"

**Cause:** Wrong Better Auth method name or API endpoint

**Solution:**
```typescript
// ❌ Wrong
authClient.forgetPassword({ email, redirectTo })

// ✅ Correct
authClient.requestPasswordReset({ email, redirectTo })
```

### "Invalid or missing reset token"

**Cause:**
- Token expired (default: 1 hour)
- Token not in URL parameters
- Token already used

**Solution:**
1. Check URL contains `?token=...`
2. Request a new password reset
3. Complete reset within 1 hour

### Form submission shows success but no action

**Cause:** JavaScript error preventing submission

**Solution:**
1. Open browser console (F12)
2. Check for errors
3. Verify `authClient` is imported correctly

## Email Delivery Issues

### Resend 403 Error: "validation_error"

**Full error:**
```
You can only send testing emails to your own email address (your@email.com).
To send emails to other recipients, please verify a domain.
```

**Cause:** Resend free tier restriction without domain verification

**Solutions:**

**Option 1: Use your verified email for testing**
```bash
# Test with the email registered in your Resend account
```

**Option 2: Change FROM address to verified email**
```bash
RESEND_FROM_EMAIL=your-verified-email@example.com
```

**Option 3: Verify a custom domain**
See deployment-guide.md for domain verification steps

**Option 4: Use console logs (development)**
- Reset links are automatically logged to console when email fails
- Check Next.js terminal for the password reset URL

### Email sent but not received

**Debugging steps:**

1. **Check spam/junk folder**
2. **Verify email address is correct**
3. **Check Resend dashboard** (https://resend.com/emails)
   - Look for email in sent items
   - Check delivery status
   - Review any errors

4. **Console logs:**
   - Check Next.js terminal
   - Reset link should be logged when email fails

### "Missing API key" error

**Cause:** RESEND_API_KEY not set or not loaded

**Solutions:**

1. **Check `.env.local` exists**
2. **Verify variable is set:**
   ```bash
   RESEND_API_KEY=re_your_key_here
   ```
3. **Restart development server:**
   ```bash
   npm run dev
   ```
4. **In production, check environment variables in deployment platform**

## Better Auth Issues

### "User not found" error

**Cause:** Email doesn't exist in database

**Solution:**
- Verify email is correct
- Check user exists in database
- Better Auth intentionally returns success even for non-existent emails (security best practice)

### Password reset doesn't work after deployment

**Cause:** Environment variables not set correctly in production

**Solution:**
1. Check all environment variables in Vercel/deployment platform
2. Ensure `BETTER_AUTH_URL` matches production URL
3. Redeploy after setting variables

### Token validation fails

**Cause:**
- Token expired
- Database connection issue
- Token already used

**Solution:**
1. Request new password reset
2. Check database connection
3. Verify `DATABASE_URL` is correct

## Database Issues

### "Connection refused" error

**Cause:** Database not accessible or wrong connection string

**Solution:**
1. Verify `DATABASE_URL` is correct
2. Check database is running (for local dev)
3. For Neon: verify SSL mode is set (`?sslmode=require`)

### Better Auth tables don't exist

**Cause:** Database migration not run

**Solution:**
```bash
npx @better-auth/cli migrate
```

## Password Validation Issues

### "Password doesn't meet requirements"

**Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character (!@#$%^&*...)

**Example valid password:** `Test123!@#`

### Passwords don't match error

**Cause:** Password and confirm password fields don't match

**Solution:** Ensure both fields have identical values

## Development Issues

### Reset link not appearing in console

**Cause:** Email client not configured to log on failure

**Solution:**
Verify `email-client.ts` has fallback logging:
```typescript
if (error) {
  console.log('='.repeat(80));
  console.log('PASSWORD RESET LINK (Email delivery failed):');
  console.log(`To: ${email}`);
  console.log(`URL: ${resetUrl}`);
  console.log('='.repeat(80));
}
```

### Page not found (404) for `/reset-password`

**Cause:** Reset password page not created

**Solution:**
1. Create `app/(auth)/reset-password/page.tsx`
2. Copy from `assets/reset-password-page.tsx`

## Production Issues

### Vercel deployment fails

**Common causes:**
1. Build errors - check build logs
2. Missing environment variables
3. TypeScript errors

**Solution:**
1. Run `npm run build` locally first
2. Fix any TypeScript errors
3. Add all required environment variables in Vercel

### Users can't access password reset

**Checklist:**
- [ ] `/forgot-password` route exists
- [ ] `/reset-password` route exists
- [ ] Better Auth API routes configured
- [ ] Database connection working
- [ ] Email service configured

## Debug Mode

Enable detailed logging by adding:

```typescript
// In email-client.ts
console.log('Email config:', {
  from: FROM_EMAIL,
  to: email,
  hasApiKey: !!process.env.RESEND_API_KEY,
});
```

## Getting Help

If issues persist:

1. **Check Resend dashboard:** https://resend.com/emails
2. **Better Auth docs:** https://better-auth.com/docs
3. **Review environment variables:** Ensure all are set correctly
4. **Check database tables:** Verify Better Auth tables exist
5. **Test with verified email first:** Eliminate email delivery as variable

## Quick Diagnostic Checklist

- [ ] Environment variables set correctly
- [ ] Database connection working
- [ ] Better Auth tables exist in database
- [ ] Resend API key valid
- [ ] Email templates loading correctly
- [ ] Validation schemas imported correctly
- [ ] Routes exist: `/forgot-password`, `/reset-password`
- [ ] Better Auth client configured correctly
- [ ] Tested with verified email address
