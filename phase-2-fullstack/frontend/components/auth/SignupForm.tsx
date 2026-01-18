// SignupForm component with email/password/confirmPassword fields
// T033 [P] [US1] - Component creation
// T034 [US1] - React Hook Form + Zod integration
// T035 [US1] - Form validation
// T036 [US1] - Submission handler
// T037 [US1] - Error handling

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { signupSchema } from '@/lib/validation/schemas';
import { authClient } from '@/lib/auth/client';
import { initializeApiToken } from '@/lib/api/client';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import type { SignupPayload } from '@/types/auth';

interface SignupFormProps {
  onSubmit?: (data: SignupPayload) => Promise<void>;
}

export function SignupForm({ onSubmit }: SignupFormProps = {}) {
  const router = useRouter();
  const [apiError, setApiError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupPayload>({
    resolver: zodResolver(signupSchema),
    mode: 'onChange',
    reValidateMode: 'onChange',
  });

  const handleFormSubmit = async (data: SignupPayload) => {
    setApiError(null);
    setIsLoading(true);

    try {
      if (onSubmit) {
        // Custom onSubmit handler (for testing)
        await onSubmit(data);
      } else {
        // Better Auth signup flow
        const response = await authClient.signUp.email({
          email: data.email,
          password: data.password,
          name: data.name, // Use the full name provided by user
        });

        if (response.error) {
          throw new Error(response.error.message || 'Signup failed');
        }

        // Initialize API token for backend authentication
        const tokenData = await initializeApiToken();

        if (!tokenData) {
          throw new Error('Failed to initialize session. Please try logging in.');
        }

        // Successful signup - redirect to dashboard (user is auto-logged in)
        router.push('/dashboard');
      }
    } catch (error) {
      if (error instanceof Error) {
        // Handle specific error cases
        if (error.message.toLowerCase().includes('email')) {
          setApiError('Email already exists. Please use a different email or log in.');
        } else if (error.message.toLowerCase().includes('password')) {
          setApiError('Password does not meet requirements. Please use a stronger password.');
        } else {
          setApiError(error.message);
        }
      } else {
        setApiError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {/* Full Name Field */}
      <Input
        label="Full Name"
        type="text"
        {...register('name')}
        error={errors.name?.message}
        disabled={isLoading}
        required
        autoComplete="name"
        placeholder="John Doe"
      />

      {/* Email Field */}
      <Input
        label="Email"
        type="email"
        {...register('email')}
        error={errors.email?.message}
        disabled={isLoading}
        required
        autoComplete="email"
        placeholder="you@example.com"
      />

      {/* Password Field */}
      <Input
        label="Password"
        type="password"
        {...register('password')}
        error={errors.password?.message}
        disabled={isLoading}
        required
        autoComplete="new-password"
        placeholder="Minimum 8 characters"
      />

      {/* Confirm Password Field */}
      <Input
        label="Confirm Password"
        type="password"
        {...register('confirmPassword')}
        error={errors.confirmPassword?.message}
        disabled={isLoading}
        required
        autoComplete="new-password"
        placeholder="Re-enter your password"
      />

      {/* API Error Display */}
      {apiError && (
        <div
          className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700"
          role="alert"
        >
          {apiError}
        </div>
      )}

      {/* Submit Button */}
      <Button
        type="submit"
        variant="primary"
        disabled={isLoading}
        className="w-full"
      >
        {isLoading ? 'Signing up...' : 'Sign Up'}
      </Button>

      {/* Login Link */}
      <p className="text-center text-sm text-gray-600">
        Already have an account?{' '}
        <a href="/login" className="text-primary hover:underline font-medium">
          Log in
        </a>
      </p>
    </form>
  );
}
