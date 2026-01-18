// Signup page with SignupForm component
// T038 [P] [US1] - Page creation
// T039 [US1] - Loading state and error display

import { SignupForm } from '@/components/auth/SignupForm';
import Link from 'next/link';

export const metadata = {
  title: 'Sign Up - Todo App',
  description: 'Create a new account to start managing your tasks',
};

export default function SignupPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gray-50">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link href="/" className="inline-block">
            <h1 className="text-3xl font-bold text-primary">Todo App</h1>
          </Link>
          <h2 className="mt-6 text-2xl font-semibold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Get started with managing your tasks efficiently
          </p>
        </div>

        {/* Signup Form Card */}
        <div className="bg-white p-8 rounded-lg shadow-md">
          <SignupForm />
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-500">
          By signing up, you agree to our Terms of Service and Privacy Policy
        </p>
      </div>
    </div>
  );
}
