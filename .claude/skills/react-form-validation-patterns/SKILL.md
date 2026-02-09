---
name: react-form-validation-patterns
description: Production-ready form validation patterns using React Hook Form and Zod with character counters, error handling, and accessibility. Use when building forms in React applications, specifically for (1) Creating forms with client-side validation using React Hook Form + Zod, (2) Implementing real-time character counters for text fields, (3) Adding email, password, phone, URL, or custom validation rules, (4) Building accessible forms with ARIA attributes and screen reader support, (5) Validating file uploads with size and type restrictions, (6) Implementing conditional validation and cross-field dependencies, (7) Creating reusable validation schemas for common patterns
---

# React Form Validation Patterns

Production-ready form validation with React Hook Form + Zod, character counters, and accessibility.

## Overview

This skill provides templates and patterns for building validated forms in React. Includes production-ready examples with React Hook Form integration, Zod schemas, real-time character counters, error handling, loading states, and WCAG accessibility compliance.

**Key Features:**
- React Hook Form + Zod integration
- Real-time character counters with visual warnings
- Common validation patterns (email, password, phone, URL, dates, files)
- Accessibility (ARIA attributes, screen reader support)
- Loading states and error handling
- TypeScript type safety
- Reusable components

## Quick Start

### 1. Installation

```bash
npm install react-hook-form @hookform/resolvers zod
```

### 2. Basic Form Example

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Min 8 characters'),
});

type FormData = z.infer<typeof schema>;

function MyForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <input {...register('email')} />
      {errors.email && <p>{errors.email.message}</p>}

      <input {...register('password')} type="password" />
      {errors.password && <p>{errors.password.message}</p>}

      <button type="submit">Submit</button>
    </form>
  );
}
```

### 3. Use Common Validation Schemas

Copy `assets/common-validation-schemas.ts` to `lib/validation/schemas.ts` for reusable patterns:

```typescript
import {
  textField,
  emailField,
  strongPasswordField,
  optionalTextField,
} from '@/lib/validation/schemas';

const taskSchema = z.object({
  title: textField(1, 200, 'Title'),
  description: optionalTextField(1000, 'Description'),
  email: emailField,
  password: strongPasswordField,
});
```

## Production-Ready Templates

### Complete Form with Character Counters

Copy `assets/CreateTaskForm.tsx` for a full example including:
- Character counters for title (200 chars) and description (1000 chars)
- Real-time validation with error messages
- Loading states during submission
- Toast notifications
- Accessibility attributes (aria-describedby, aria-live)
- Form reset on success

### Reusable Character Counter Component

Copy `assets/CharacterCounter.tsx` for a component that:
- Shows current/max character count
- Visual warnings when approaching limit (90%+)
- Error state when over limit
- Accessibility support (aria-live, aria-atomic)

**Usage:**
```typescript
import { CharacterCounter } from '@/components/ui/CharacterCounter';

const { register, watch } = useForm();
const titleLength = watch('title')?.length || 0;

<Input {...register('title')} aria-describedby="title-counter" />
<CharacterCounter current={titleLength} max={200} id="title-counter" />
```

## Common Validation Patterns

### Text Length Validation

```typescript
// Required text with min/max
const titleSchema = z.string()
  .min(1, 'Title is required')
  .max(200, 'Title must be less than 200 characters')
  .trim();

// Optional text with max
const descriptionSchema = z.string()
  .max(1000, 'Max 1000 characters')
  .trim()
  .optional()
  .or(z.literal('')); // Allow empty string
```

### Email & Password Validation

```typescript
// Email
const emailSchema = z.string()
  .email('Invalid email address')
  .trim()
  .toLowerCase();

// Strong password
const passwordSchema = z.string()
  .min(8, 'Min 8 characters')
  .regex(/[A-Z]/, 'Must contain uppercase')
  .regex(/[a-z]/, 'Must contain lowercase')
  .regex(/[0-9]/, 'Must contain number')
  .regex(/[!@#$%^&*]/, 'Must contain special character');

// Password confirmation
const signupSchema = z.object({
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'],
});
```

### Number, Date, and File Validation

```typescript
// Number range
const ratingSchema = z.number().min(1, 'Min 1').max(5, 'Max 5');

// Future date
const appointmentSchema = z.date().min(new Date(), 'Must be in the future');

// File upload
const fileSchema = z.instanceof(File)
  .refine((file) => file.size <= 5 * 1024 * 1024, 'Max 5MB')
  .refine((file) => ['image/jpeg', 'image/png'].includes(file.type), 'Only JPEG/PNG');
```

## Character Counters

### Basic Implementation

```typescript
const { register, watch } = useForm();
const titleLength = watch('title')?.length || 0;

<input {...register('title')} maxLength={200} />
<p aria-live="polite">{titleLength} / 200</p>
```

### With Visual Warnings

```typescript
const isApproachingLimit = titleLength >= 180; // 90% of 200
const isOverLimit = titleLength > 200;

const colorClass = isOverLimit ? 'text-red-600' : isApproachingLimit ? 'text-orange-500' : 'text-gray-500';

<p className={`text-xs ${colorClass}`} aria-live="polite">
  {titleLength} / 200 {isOverLimit && <span>⚠️ Limit exceeded</span>}
</p>
```

## Conditional Validation

```typescript
// Cross-field validation
const schema = z.object({
  startDate: z.date(),
  endDate: z.date(),
}).refine(
  (data) => data.endDate > data.startDate,
  { message: 'End date must be after start date', path: ['endDate'] }
);
```

## Accessibility

```typescript
<input
  {...register('email')}
  aria-invalid={errors.email ? 'true' : 'false'}
  aria-describedby="email-error email-hint"
/>

{errors.email && (
  <p id="email-error" className="text-red-600" role="alert">
    {errors.email.message}
  </p>
)}
```

## Detailed Documentation

**Read:** `references/validation-patterns.md` for comprehensive coverage of all validation patterns, conditional logic, file uploads, performance optimization, and testing.

## Common Schemas Reference

See `assets/common-validation-schemas.ts` for 30+ reusable validation patterns including email, password, phone, URL, dates, files, and complete form examples.
