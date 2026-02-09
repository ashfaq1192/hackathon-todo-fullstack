# Deployment Guide - Password Reset with Resend

Comprehensive guide for deploying password reset functionality in production.

## Environment Variables Setup

### Vercel Deployment

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables

2. Add these variables:

```bash
# Resend Email Service
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=onboarding@resend.dev  # or your_domain

# Better Auth
BETTER_AUTH_SECRET=your_secret_key_here
BETTER_AUTH_URL=https://your-app.vercel.app
NEXT_PUBLIC_BETTER_AUTH_URL=https://your-app.vercel.app

# Database
DATABASE_URL=postgresql://connection_string

# Optional
NEXT_PUBLIC_APP_NAME=Your App Name
```

3. Redeploy your application

## Resend Email Configuration

### Free Tier (No Domain)

**Using Resend Test Domain:**
```bash
RESEND_FROM_EMAIL=onboarding@resend.dev
```

**Limitations:**
- Only delivers emails to your Resend account email
- Other users won't receive emails (but flow still works)
- Reset links are logged to console as fallback

**Good for:**
- Development
- Testing
- Hackathons
- Personal projects

### Production (Custom Domain)

**Step 1: Buy a Domain**
- Cost: $10-15/year
- Providers: Namecheap, GoDaddy, Cloudflare Registrar

**Step 2: Add Domain to Vercel**
1. Vercel Dashboard → Project → Settings → Domains
2. Add custom domain: `yourdomain.com`
3. Add DNS records provided by Vercel to your domain registrar

**Step 3: Verify Domain in Resend**
1. Go to: https://resend.com/domains
2. Click "Add Domain"
3. Enter: `yourdomain.com`
4. Add DNS records provided by Resend to your domain registrar:
   - TXT record for domain verification
   - CNAME records for DKIM
   - MX records (optional)
5. Wait 24-48 hours for verification

**Step 4: Update Environment Variables**
```bash
RESEND_FROM_EMAIL=noreply@yourdomain.com
# or
RESEND_FROM_EMAIL=support@yourdomain.com
```

**Benefits:**
- ✅ Send emails to ANY user
- ✅ Professional appearance
- ✅ No console logging needed

## Alternative: Use Verified Email

You can use your Resend account email as the FROM address:

```bash
RESEND_FROM_EMAIL=your-verified-email@example.com
```

**Pros:**
- Free
- Works for all users
- No domain needed

**Cons:**
- Emails come from your personal address
- Less professional for production apps

## Resend Free Tier Limits

- **100 emails/day**
- **3,000 emails/month**
- Perfect for:
  - Small apps
  - MVPs
  - Hackathons
  - Testing

## DNS Record Configuration

When verifying a custom domain, you'll need to add these records to your domain registrar:

### 1. Domain Verification (TXT Record)
```
Type: TXT
Name: @ (or your domain)
Value: [Provided by Resend]
TTL: 3600
```

### 2. DKIM Records (CNAME)
```
Type: CNAME
Name: resend._domainkey
Value: [Provided by Resend]
TTL: 3600
```

```
Type: CNAME
Name: resend2._domainkey
Value: [Provided by Resend]
TTL: 3600
```

### 3. Return-Path (CNAME)
```
Type: CNAME
Name: resend
Value: [Provided by Resend]
TTL: 3600
```

## Verification Checklist

- [ ] Resend API key added to environment variables
- [ ] FROM email address configured
- [ ] Better Auth environment variables set
- [ ] Database connection string configured
- [ ] Application deployed and accessible
- [ ] Test password reset with your email
- [ ] (Optional) Custom domain verified in Resend
- [ ] (Production) Test with multiple user emails

## Common Deployment Issues

**Issue: "Email sent successfully" but no email received**
- Cause: Resend free tier restriction
- Solution: Use verified email or verify a custom domain

**Issue: "Missing API key" error**
- Cause: RESEND_API_KEY not set or not loaded
- Solution: Check environment variables in deployment platform

**Issue: "Invalid domain" error**
- Cause: FROM email domain not verified
- Solution: Use `onboarding@resend.dev` or verify your domain

**Issue: Reset links don't work in production**
- Cause: BETTER_AUTH_URL not set correctly
- Solution: Ensure it matches your production URL

## Testing in Production

1. Request password reset with your verified email
2. Check inbox for reset email
3. Click reset link
4. Set new password
5. Verify login with new password

## Monitoring

Check Resend dashboard for:
- Email delivery status
- Bounce rates
- Spam reports
- Usage statistics

Access at: https://resend.com/emails
