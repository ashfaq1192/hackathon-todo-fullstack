// LoginForm component with email/password fields
// T042 [P] [US2] - Component creation
// T043 [US2] - React Hook Form + Zod integration
// T044 [US2] - Form validation
// T045 [US2] - Submission handler
// T046 [US2] - Error handling

'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { loginSchema } from '@/lib/validation/schemas';
import { authClient } from '@/lib/auth/client';
import { initializeApiToken } from '@/lib/api/client';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import type { LoginPayload } from '@/types/auth';

interface LoginFormProps {
  onSubmit?: (data: LoginPayload) => Promise<void>;
}

export function LoginForm({ onSubmit }: LoginFormProps = {}) {
  const router = useRouter();
  const [apiError, setApiError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginPayload>({
    resolver: zodResolver(loginSchema),
    mode: 'onChange',
    reValidateMode: 'onChange',
  });

  const handleFormSubmit = async (data: LoginPayload) => {
    setApiError(null);
    setIsLoading(true);

    try {
      if (onSubmit) {
        // Custom onSubmit handler (for testing)
        await onSubmit(data);
      } else {
        // Better Auth login flow
        const response = await authClient.signIn.email({
          email: data.email,
          password: data.password,
        });

        if (response.error) {
          throw new Error(response.error.message || 'Login failed');
        }

        // Initialize API token for backend authentication
        await initializeApiToken();

        // Successful login - redirect to dashboard page
        router.push('/dashboard');
      }
    } catch (error) {
      if (error instanceof Error) {
        // Handle specific error cases
        const errorMessage = error.message.toLowerCase();

        if (errorMessage.includes('invalid') && errorMessage.includes('credentials')) {
          setApiError('Invalid credentials. Please check your email and password.');
        } else if (errorMessage.includes('not found') || errorMessage.includes('does not exist')) {
          setApiError('Account not found. Please check your email or sign up.');
        } else if (errorMessage.includes('incorrect') || errorMessage.includes('wrong password')) {
          setApiError('Incorrect password. Please try again.');
        } else if (errorMessage.includes('verification') || errorMessage.includes('verify')) {
          setApiError('Please verify your email address before logging in.');
        } else {
          // Show the actual error message from the API
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
      <div>
        <div className="flex items-center justify-between mb-2">
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password
          </label>
          <Link
            href="/forgot-password"
            className="text-sm text-blue-600 hover:text-blue-500 font-medium"
          >
            Forgot password?
          </Link>
        </div>
        <Input
          label=""
          id="password"
          type="password"
          {...register('password')}
          error={errors.password?.message}
          disabled={isLoading}
          required
          autoComplete="current-password"
          placeholder="Enter your password"
        />
      </div>

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
        {isLoading ? 'Logging in...' : 'Log In'}
      </Button>

      {/* Signup Link */}
      <p className="text-center text-sm text-gray-600">
        Don't have an account?{' '}
        <a href="/signup" className="text-primary hover:underline font-medium">
          Sign up
        </a>
      </p>
    </form>
  );
}
