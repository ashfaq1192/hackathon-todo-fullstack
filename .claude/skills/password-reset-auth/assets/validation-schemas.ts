/**
 * Password Reset Validation Schemas
 *
 * Zod validation schemas for forgot password and reset password forms.
 * Includes strong password requirements for security.
 */

import { z } from 'zod';

// Password validation regex patterns
const passwordRequirements = {
  minLength: 8,
  hasUpperCase: /[A-Z]/,
  hasLowerCase: /[a-z]/,
  hasNumber: /[0-9]/,
  hasSpecialChar: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/,
};

/**
 * Forgot password form validation
 * Only requires email address
 */
export const forgotPasswordSchema = z.object({
  email: z.string()
    .email('Invalid email address')
    .trim()
    .toLowerCase(),
});

export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>;

/**
 * Reset password form validation
 * Enforces strong password requirements and confirmation matching
 */
export const resetPasswordSchema = z.object({
  password: z.string()
    .min(passwordRequirements.minLength, `Password must be at least ${passwordRequirements.minLength} characters`)
    .max(100, 'Password must be less than 100 characters')
    .regex(passwordRequirements.hasUpperCase, 'Password must contain at least one uppercase letter')
    .regex(passwordRequirements.hasLowerCase, 'Password must contain at least one lowercase letter')
    .regex(passwordRequirements.hasNumber, 'Password must contain at least one number')
    .regex(passwordRequirements.hasSpecialChar, 'Password must contain at least one special character (!@#$%^&*...)'),
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

export type ResetPasswordInput = z.infer<typeof resetPasswordSchema>;
