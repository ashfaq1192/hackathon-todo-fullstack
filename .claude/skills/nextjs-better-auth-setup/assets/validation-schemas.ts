// Zod validation schemas for authentication forms

import { z } from 'zod';

// Password validation regex patterns
const passwordRequirements = {
  minLength: 8,
  hasUpperCase: /[A-Z]/,
  hasLowerCase: /[a-z]/,
  hasNumber: /[0-9]/,
  hasSpecialChar: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/,
};

// Signup form validation
export const signupSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be less than 100 characters')
    .trim(),
  email: z.string()
    .email('Invalid email address')
    .trim()
    .toLowerCase(),
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

export type SignupInput = z.infer<typeof signupSchema>;

// Login form validation
export const loginSchema = z.object({
  email: z.string()
    .email('Invalid email address')
    .trim()
    .toLowerCase(),
  password: z.string()
    .min(1, 'Password is required'),
});

export type LoginInput = z.infer<typeof loginSchema>;
