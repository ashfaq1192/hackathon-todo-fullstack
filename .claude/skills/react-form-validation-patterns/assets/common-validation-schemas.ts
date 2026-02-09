// Common Zod validation schemas for forms
// Reusable patterns for email, password, text length, numbers, dates, etc.

import { z } from 'zod';

// ============================================================================
// Text Field Validation
// ============================================================================

// Required text with min/max length
export const textField = (minLength: number, maxLength: number, fieldName: string = 'Field') =>
  z.string()
    .min(minLength, `${fieldName} must be at least ${minLength} characters`)
    .max(maxLength, `${fieldName} must be less than ${maxLength} characters`)
    .trim();

// Optional text with max length
export const optionalTextField = (maxLength: number, fieldName: string = 'Field') =>
  z.string()
    .max(maxLength, `${fieldName} must be less than ${maxLength} characters`)
    .trim()
    .optional()
    .or(z.literal('')); // Allow empty string

// ============================================================================
// Email Validation
// ============================================================================

export const emailField = z.string()
  .email('Invalid email address')
  .trim()
  .toLowerCase();

// ============================================================================
// Password Validation
// ============================================================================

const passwordRequirements = {
  minLength: 8,
  hasUpperCase: /[A-Z]/,
  hasLowerCase: /[a-z]/,
  hasNumber: /[0-9]/,
  hasSpecialChar: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/,
};

export const strongPasswordField = z.string()
  .min(passwordRequirements.minLength, `Password must be at least ${passwordRequirements.minLength} characters`)
  .max(100, 'Password must be less than 100 characters')
  .regex(passwordRequirements.hasUpperCase, 'Password must contain at least one uppercase letter')
  .regex(passwordRequirements.hasLowerCase, 'Password must contain at least one lowercase letter')
  .regex(passwordRequirements.hasNumber, 'Password must contain at least one number')
  .regex(passwordRequirements.hasSpecialChar, 'Password must contain at least one special character (!@#$%^&*...)');

// Simple password (only minimum length)
export const simplePasswordField = z.string()
  .min(8, 'Password must be at least 8 characters');

// ============================================================================
// Number Validation
// ============================================================================

// Positive integer
export const positiveIntegerField = (fieldName: string = 'Value') =>
  z.number({
    required_error: `${fieldName} is required`,
    invalid_type_error: `${fieldName} must be a number`,
  })
    .int(`${fieldName} must be an integer`)
    .positive(`${fieldName} must be positive`);

// Integer within range
export const rangedIntegerField = (min: number, max: number, fieldName: string = 'Value') =>
  z.number()
    .int(`${fieldName} must be an integer`)
    .min(min, `${fieldName} must be at least ${min}`)
    .max(max, `${fieldName} must be at most ${max}`);

// Decimal with precision
export const decimalField = (decimals: number, fieldName: string = 'Value') =>
  z.number()
    .refine(
      (val) => {
        const decimalPart = (val.toString().split('.')[1] || '').length;
        return decimalPart <= decimals;
      },
      { message: `${fieldName} can have at most ${decimals} decimal places` }
    );

// ============================================================================
// URL Validation
// ============================================================================

export const urlField = z.string()
  .url('Invalid URL format')
  .trim();

export const optionalUrlField = z.string()
  .url('Invalid URL format')
  .trim()
  .optional()
  .or(z.literal(''));

// ============================================================================
// Phone Number Validation
// ============================================================================

// US phone number (simple)
export const usPhoneField = z.string()
  .regex(/^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/, 'Invalid US phone number');

// International phone number (E.164 format)
export const internationalPhoneField = z.string()
  .regex(/^\+[1-9]\d{1,14}$/, 'Invalid phone number (use international format: +1234567890)');

// ============================================================================
// Date Validation
// ============================================================================

// Date in the past
export const pastDateField = (fieldName: string = 'Date') =>
  z.date({
    required_error: `${fieldName} is required`,
    invalid_type_error: `${fieldName} must be a valid date`,
  })
    .max(new Date(), `${fieldName} must be in the past`);

// Date in the future
export const futureDateField = (fieldName: string = 'Date') =>
  z.date()
    .min(new Date(), `${fieldName} must be in the future`);

// Date within range
export const rangedDateField = (minDate: Date, maxDate: Date, fieldName: string = 'Date') =>
  z.date()
    .min(minDate, `${fieldName} must be after ${minDate.toDateString()}`)
    .max(maxDate, `${fieldName} must be before ${maxDate.toDateString()}`);

// ============================================================================
// Enum Validation
// ============================================================================

export const enumField = <T extends [string, ...string[]]>(
  values: T,
  fieldName: string = 'Value'
) =>
  z.enum(values, {
    errorMap: () => ({ message: `${fieldName} must be one of: ${values.join(', ')}` }),
  });

// ============================================================================
// File Upload Validation
// ============================================================================

export const fileField = (
  maxSizeMB: number,
  allowedTypes: string[],
  fieldName: string = 'File'
) =>
  z
    .instanceof(File)
    .refine(
      (file) => file.size <= maxSizeMB * 1024 * 1024,
      `${fieldName} must be less than ${maxSizeMB}MB`
    )
    .refine(
      (file) => allowedTypes.includes(file.type),
      `${fieldName} must be one of: ${allowedTypes.join(', ')}`
    );

// ============================================================================
// Array Validation
// ============================================================================

// Non-empty array
export const nonEmptyArrayField = <T extends z.ZodTypeAny>(
  itemSchema: T,
  fieldName: string = 'List'
) =>
  z.array(itemSchema).min(1, `${fieldName} must contain at least one item`);

// Array with min/max length
export const rangedArrayField = <T extends z.ZodTypeAny>(
  itemSchema: T,
  minLength: number,
  maxLength: number,
  fieldName: string = 'List'
) =>
  z
    .array(itemSchema)
    .min(minLength, `${fieldName} must contain at least ${minLength} items`)
    .max(maxLength, `${fieldName} must contain at most ${maxLength} items`);

// ============================================================================
// Common Form Schemas (Examples)
// ============================================================================

// Task creation schema
export const createTaskSchema = z.object({
  title: textField(1, 200, 'Title'),
  description: optionalTextField(1000, 'Description'),
  priority: enumField(['low', 'medium', 'high'], 'Priority').optional(),
});

// Signup schema with password confirmation
export const signupSchema = z.object({
  name: textField(2, 100, 'Name'),
  email: emailField,
  password: strongPasswordField,
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});

// Login schema
export const loginSchema = z.object({
  email: emailField,
  password: z.string().min(1, 'Password is required'),
});

// Contact form schema
export const contactFormSchema = z.object({
  name: textField(2, 100, 'Name'),
  email: emailField,
  subject: textField(5, 200, 'Subject'),
  message: textField(10, 2000, 'Message'),
});

// Profile update schema
export const profileUpdateSchema = z.object({
  name: textField(2, 100, 'Name').optional(),
  bio: optionalTextField(500, 'Bio'),
  website: optionalUrlField,
  phone: usPhoneField.optional(),
});

// Export type inference helpers
export type CreateTaskInput = z.infer<typeof createTaskSchema>;
export type SignupInput = z.infer<typeof signupSchema>;
export type LoginInput = z.infer<typeof loginSchema>;
export type ContactFormInput = z.infer<typeof contactFormSchema>;
export type ProfileUpdateInput = z.infer<typeof profileUpdateSchema>;
