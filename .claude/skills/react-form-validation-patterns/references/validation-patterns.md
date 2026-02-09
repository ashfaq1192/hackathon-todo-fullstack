# Validation Patterns Guide

Comprehensive guide for form validation with React Hook Form + Zod.

## Table of Contents

1. [Basic Form Setup](#basic-form-setup)
2. [Common Validation Patterns](#common-validation-patterns)
3. [Character Counters](#character-counters)
4. [Conditional Validation](#conditional-validation)
5. [Custom Validation Rules](#custom-validation-rules)
6. [File Upload Validation](#file-upload-validation)
7. [Accessibility](#accessibility)

## Basic Form Setup

### Installation

```bash
npm install react-hook-form @hookform/resolvers zod
```

### Minimal Form Example

```typescript
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
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

  const onSubmit = (data: FormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('email')} />
      {errors.email && <p>{errors.email.message}</p>}

      <input {...register('password')} type="password" />
      {errors.password && <p>{errors.password.message}</p>}

      <button type="submit">Submit</button>
    </form>
  );
}
```

## Common Validation Patterns

### Text Length Validation

```typescript
// Required text with min/max length
const titleSchema = z.string()
  .min(1, 'Title is required')
  .max(200, 'Title must be less than 200 characters')
  .trim();

// Optional text with max length
const descriptionSchema = z.string()
  .max(1000, 'Description must be less than 1000 characters')
  .trim()
  .optional()
  .or(z.literal('')); // Allow empty string
```

### Email Validation

```typescript
const emailSchema = z.string()
  .email('Invalid email address')
  .trim()
  .toLowerCase();
```

### Password Validation

**Strong password:**
```typescript
const passwordSchema = z.string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain uppercase letter')
  .regex(/[a-z]/, 'Password must contain lowercase letter')
  .regex(/[0-9]/, 'Password must contain number')
  .regex(/[!@#$%^&*]/, 'Password must contain special character');
```

**Password confirmation:**
```typescript
const signupSchema = z.object({
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine(data => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword'], // Error shows on confirmPassword field
});
```

### Number Validation

```typescript
// Positive integer
const ageSchema = z.number()
  .int('Age must be an integer')
  .positive('Age must be positive');

// Range validation
const ratingSchema = z.number()
  .min(1, 'Rating must be at least 1')
  .max(5, 'Rating must be at most 5');

// Decimal precision
const priceSchema = z.number()
  .refine(
    (val) => (val.toString().split('.')[1] || '').length <= 2,
    { message: 'Price can have at most 2 decimal places' }
  );
```

### Date Validation

```typescript
// Date in the past (e.g., birth date)
const birthDateSchema = z.date()
  .max(new Date(), 'Birth date must be in the past');

// Date in the future (e.g., appointment)
const appointmentSchema = z.date()
  .min(new Date(), 'Appointment must be in the future');

// Date range
const eventDateSchema = z.date()
  .min(new Date('2024-01-01'), 'Event must be after Jan 1, 2024')
  .max(new Date('2024-12-31'), 'Event must be before Dec 31, 2024');
```

### Select/Enum Validation

```typescript
const prioritySchema = z.enum(['low', 'medium', 'high'], {
  errorMap: () => ({ message: 'Priority must be low, medium, or high' }),
});

// Usage in form
<select {...register('priority')}>
  <option value="low">Low</option>
  <option value="medium">Medium</option>
  <option value="high">High</option>
</select>
```

### URL Validation

```typescript
const urlSchema = z.string()
  .url('Invalid URL format')
  .trim();

// Optional URL
const optionalUrlSchema = z.string()
  .url('Invalid URL format')
  .trim()
  .optional()
  .or(z.literal(''));
```

### Phone Number Validation

```typescript
// US phone number
const usPhoneSchema = z.string()
  .regex(
    /^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/,
    'Invalid US phone number'
  );

// International (E.164 format)
const intlPhoneSchema = z.string()
  .regex(/^\+[1-9]\d{1,14}$/, 'Use international format: +1234567890');
```

## Character Counters

### Basic Character Counter

```typescript
import { useForm } from 'react-hook-form';

const { register, watch } = useForm();
const titleLength = watch('title')?.length || 0;

<input {...register('title')} maxLength={200} />
<p>{titleLength} / 200</p>
```

### With Accessibility (aria-live)

```typescript
<input
  {...register('title')}
  aria-describedby="title-counter"
/>
<p
  id="title-counter"
  className="text-xs text-gray-500"
  aria-live="polite"
  aria-atomic="true"
>
  {titleLength} / 200
</p>
```

### Visual Warnings (Approaching Limit)

```typescript
const isApproachingLimit = titleLength >= 180; // 90% of 200
const isOverLimit = titleLength > 200;

const colorClass = isOverLimit
  ? 'text-red-600'
  : isApproachingLimit
  ? 'text-orange-500'
  : 'text-gray-500';

<p className={`text-xs ${colorClass}`} aria-live="polite">
  {titleLength} / 200
  {isOverLimit && <span>⚠️ Limit exceeded</span>}
</p>
```

### Reusable Character Counter Component

See `assets/CharacterCounter.tsx` for a production-ready component.

## Conditional Validation

### Field Depends on Another Field

```typescript
const schema = z.object({
  hasAddress: z.boolean(),
  address: z.string().optional(),
}).refine(
  (data) => !data.hasAddress || data.address,
  {
    message: 'Address is required when checkbox is checked',
    path: ['address'],
  }
);
```

### Different Validation Based on Selection

```typescript
const schema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('email'),
    email: z.string().email(),
  }),
  z.object({
    type: z.literal('phone'),
    phone: z.string().regex(/^\d{10}$/),
  }),
]);
```

### Dynamic Schema Based on User Role

```typescript
const getSchema = (userRole: string) => {
  const baseSchema = {
    name: z.string().min(1),
    email: z.string().email(),
  };

  if (userRole === 'admin') {
    return z.object({
      ...baseSchema,
      permissions: z.array(z.string()).min(1, 'Select at least one permission'),
    });
  }

  return z.object(baseSchema);
};

// Usage
const schema = getSchema(currentUserRole);
const { register } = useForm({ resolver: zodResolver(schema) });
```

## Custom Validation Rules

### Custom Validation Function

```typescript
const usernameSchema = z.string()
  .min(3)
  .refine(
    async (username) => {
      const response = await fetch(`/api/check-username?username=${username}`);
      const data = await response.json();
      return data.available;
    },
    { message: 'Username is already taken' }
  );
```

### Multiple Custom Rules

```typescript
const passwordSchema = z.string()
  .refine((val) => val.length >= 8, { message: 'Too short' })
  .refine((val) => /[A-Z]/.test(val), { message: 'Needs uppercase' })
  .refine((val) => /[a-z]/.test(val), { message: 'Needs lowercase' })
  .refine((val) => /[0-9]/.test(val), { message: 'Needs number' });
```

### Cross-Field Validation

```typescript
const schema = z.object({
  startDate: z.date(),
  endDate: z.date(),
}).refine(
  (data) => data.endDate > data.startDate,
  {
    message: 'End date must be after start date',
    path: ['endDate'],
  }
);
```

## File Upload Validation

### Single File with Size and Type Validation

```typescript
const fileSchema = z
  .instanceof(File)
  .refine(
    (file) => file.size <= 5 * 1024 * 1024, // 5MB
    'File must be less than 5MB'
  )
  .refine(
    (file) => ['image/jpeg', 'image/png'].includes(file.type),
    'Only JPEG and PNG images are allowed'
  );

// Usage
const { register } = useForm({
  resolver: zodResolver(z.object({ avatar: fileSchema })),
});

<input type="file" {...register('avatar')} accept="image/jpeg,image/png" />
```

### Multiple Files

```typescript
const filesSchema = z
  .array(
    z.instanceof(File).refine(
      (file) => file.size <= 10 * 1024 * 1024,
      'Each file must be less than 10MB'
    )
  )
  .min(1, 'At least one file is required')
  .max(5, 'Maximum 5 files allowed');

<input type="file" {...register('documents')} multiple />
```

## Accessibility

### ARIA Attributes

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

<p id="email-hint" className="text-gray-500">
  We'll never share your email
</p>
```

### Focus Management

```typescript
import { useForm } from 'react-hook-form';

const { register, setFocus } = useForm();

// Focus first error on submit
const onSubmit = async (data) => {
  try {
    await api.submit(data);
  } catch (error) {
    setFocus('email'); // Focus specific field
  }
};
```

### Required Field Indicators

```typescript
<label htmlFor="email">
  Email
  {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
</label>
```

## Performance Optimization

### Validation Modes

```typescript
// Validate on change (default)
const { register } = useForm({ mode: 'onChange' });

// Validate on blur (better performance for complex validation)
const { register } = useForm({ mode: 'onBlur' });

// Validate only on submit (best performance)
const { register } = useForm({ mode: 'onSubmit' });

// Validate on submit, then on change
const { register } = useForm({ mode: 'onTouched' });
```

### Debounce Async Validation

```typescript
import { useForm } from 'react-hook-form';
import { debounce } from 'lodash';

const checkUsernameAvailability = debounce(async (username) => {
  const response = await fetch(`/api/check-username?username=${username}`);
  return response.json();
}, 500);

const schema = z.string().refine(
  async (username) => {
    const data = await checkUsernameAvailability(username);
    return data.available;
  },
  { message: 'Username is taken' }
);
```

## Testing Forms

### Unit Test Example

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MyForm } from './MyForm';

test('validates email format', async () => {
  render(<MyForm />);

  const emailInput = screen.getByLabelText(/email/i);
  fireEvent.change(emailInput, { target: { value: 'invalid' } });
  fireEvent.blur(emailInput);

  await waitFor(() => {
    expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
  });
});
```
