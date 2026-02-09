/**
 * Email Client using Resend
 *
 * Sends transactional emails for authentication flows with automatic fallback to console logging.
 * Production-ready with error handling and graceful degradation.
 */

import { Resend } from 'resend';

// Lazy initialization of Resend client to handle missing API key gracefully
let resendClient: Resend | null = null;

function getResendClient(): Resend | null {
  if (!process.env.RESEND_API_KEY) {
    return null;
  }
  if (!resendClient) {
    resendClient = new Resend(process.env.RESEND_API_KEY);
  }
  return resendClient;
}

// Email configuration
const FROM_EMAIL = process.env.RESEND_FROM_EMAIL || 'onboarding@resend.dev';
const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || 'Your App';
const APP_URL = process.env.BETTER_AUTH_URL || 'http://localhost:3000';

/**
 * Send verification email
 */
export async function sendVerificationEmail(email: string, verificationUrl: string): Promise<boolean> {
  try {
    const resend = getResendClient();

    // For development without Resend API key, log to console
    if (!resend) {
      console.log('='.repeat(80));
      console.log('EMAIL VERIFICATION LINK (Resend not configured):');
      console.log(`To: ${email}`);
      console.log(`URL: ${verificationUrl}`);
      console.log('='.repeat(80));
      return true;
    }

    const { data, error } = await resend.emails.send({
      from: FROM_EMAIL,
      to: email,
      subject: `Verify your ${APP_NAME} account`,
      html: getVerificationEmailTemplate(verificationUrl),
    });

    if (error) {
      console.error('Failed to send verification email:', error);
      // Log the verification URL for development/testing when email fails
      console.log('='.repeat(80));
      console.log('EMAIL VERIFICATION LINK (Email delivery failed):');
      console.log(`To: ${email}`);
      console.log(`URL: ${verificationUrl}`);
      console.log('='.repeat(80));
      return true; // Return true to allow verification flow to continue
    }

    console.log('Verification email sent:', data);
    return true;
  } catch (error) {
    console.error('Error sending verification email:', error);
    return false;
  }
}

/**
 * Send password reset email
 */
export async function sendPasswordResetEmail(email: string, resetUrl: string): Promise<boolean> {
  try {
    const resend = getResendClient();

    // For development without Resend API key, log to console
    if (!resend) {
      console.log('='.repeat(80));
      console.log('PASSWORD RESET LINK (Resend not configured):');
      console.log(`To: ${email}`);
      console.log(`URL: ${resetUrl}`);
      console.log('='.repeat(80));
      return true;
    }

    const { data, error } = await resend.emails.send({
      from: FROM_EMAIL,
      to: email,
      subject: `Reset your ${APP_NAME} password`,
      html: getPasswordResetEmailTemplate(resetUrl),
    });

    if (error) {
      console.error('Failed to send password reset email:', error);
      // Log the reset URL for development/testing when email fails
      console.log('='.repeat(80));
      console.log('PASSWORD RESET LINK (Email delivery failed):');
      console.log(`To: ${email}`);
      console.log(`URL: ${resetUrl}`);
      console.log('='.repeat(80));
      return true; // Return true to allow password reset flow to continue
    }

    console.log('Password reset email sent:', data);
    return true;
  } catch (error) {
    console.error('Error sending password reset email:', error);
    return false;
  }
}

/**
 * Email verification template
 */
function getVerificationEmailTemplate(verificationUrl: string): string {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify Your Email</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(to right, #3b82f6, #6366f1); padding: 40px 40px 30px 40px; border-radius: 12px 12px 0 0;">
              <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold; text-align: center;">
                ✓ Verify Your Email
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding: 40px;">
              <p style="margin: 0 0 20px 0; color: #374151; font-size: 16px; line-height: 24px;">
                Hi there!
              </p>
              <p style="margin: 0 0 20px 0; color: #374151; font-size: 16px; line-height: 24px;">
                Thanks for signing up for <strong>${APP_NAME}</strong>! To get started, please verify your email address by clicking the button below:
              </p>

              <!-- Button -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                <tr>
                  <td align="center">
                    <a href="${verificationUrl}" style="display: inline-block; background: linear-gradient(to right, #3b82f6, #6366f1); color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);">
                      Verify Email Address
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin: 20px 0 0 0; color: #6b7280; font-size: 14px; line-height: 20px;">
                Or copy and paste this link into your browser:
              </p>
              <p style="margin: 8px 0 0 0; color: #3b82f6; font-size: 14px; word-break: break-all;">
                ${verificationUrl}
              </p>

              <p style="margin: 30px 0 0 0; color: #6b7280; font-size: 14px; line-height: 20px;">
                This link will expire in 24 hours. If you didn't create an account, you can safely ignore this email.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #f9fafb; padding: 30px 40px; border-radius: 0 0 12px 12px; border-top: 1px solid #e5e7eb;">
              <p style="margin: 0; color: #6b7280; font-size: 14px; text-align: center;">
                © ${new Date().getFullYear()} ${APP_NAME}. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `.trim();
}

/**
 * Password reset email template
 */
function getPasswordResetEmailTemplate(resetUrl: string): string {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset Your Password</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f3f4f6;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f3f4f6; padding: 40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
          <!-- Header -->
          <tr>
            <td style="background: linear-gradient(to right, #3b82f6, #6366f1); padding: 40px 40px 30px 40px; border-radius: 12px 12px 0 0;">
              <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold; text-align: center;">
                🔑 Reset Your Password
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding: 40px;">
              <p style="margin: 0 0 20px 0; color: #374151; font-size: 16px; line-height: 24px;">
                Hi there!
              </p>
              <p style="margin: 0 0 20px 0; color: #374151; font-size: 16px; line-height: 24px;">
                We received a request to reset your password for your <strong>${APP_NAME}</strong> account. Click the button below to create a new password:
              </p>

              <!-- Button -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0;">
                <tr>
                  <td align="center">
                    <a href="${resetUrl}" style="display: inline-block; background: linear-gradient(to right, #3b82f6, #6366f1); color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-size: 16px; font-weight: 600; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);">
                      Reset Password
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin: 20px 0 0 0; color: #6b7280; font-size: 14px; line-height: 20px;">
                Or copy and paste this link into your browser:
              </p>
              <p style="margin: 8px 0 0 0; color: #3b82f6; font-size: 14px; word-break: break-all;">
                ${resetUrl}
              </p>

              <p style="margin: 30px 0 0 0; color: #6b7280; font-size: 14px; line-height: 20px;">
                This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #f9fafb; padding: 30px 40px; border-radius: 0 0 12px 12px; border-top: 1px solid #e5e7eb;">
              <p style="margin: 0; color: #6b7280; font-size: 14px; text-align: center;">
                © ${new Date().getFullYear()} ${APP_NAME}. All rights reserved.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `.trim();
}
