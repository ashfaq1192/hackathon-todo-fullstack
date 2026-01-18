// app/(dashboard)/layout.tsx
'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Navigation } from '@/components/layout/Navigation';
import { getUserId } from '@/lib/api/client'; // Import getUserId

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    const userId = getUserId();
    if (!userId) {
      // If no user ID is found, redirect to the login page
      router.push('/login');
    }
  }, [router]); // Depend on router to avoid unnecessary re-runs

  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation />
      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}
