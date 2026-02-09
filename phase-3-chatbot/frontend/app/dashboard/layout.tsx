/**
 * Dashboard Layout
 *
 * Provides layout for authenticated dashboard pages.
 * Includes navigation, authentication guard, and chat widget provider.
 */

'use client';

import { Navigation } from '@/components/layout/Navigation';
import { ChatWidgetProvider } from '@/contexts/ChatWidgetContext';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ChatWidgetProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </div>
    </ChatWidgetProvider>
  );
}
