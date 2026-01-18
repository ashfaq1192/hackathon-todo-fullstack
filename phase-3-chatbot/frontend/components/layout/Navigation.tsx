'use client';

import { useSession } from '@/lib/auth/client';
import { authClient } from '@/lib/auth/client';
import { clearApiToken } from '@/lib/api/client';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import React, { useState } from 'react'; // Import useState

export function Navigation() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false); // State for mobile menu

  const handleLogout = async () => {
    try {
      clearApiToken();
      await authClient.signOut();
      router.push('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (isPending) {
    return (
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="h-6 w-32 bg-gray-200 animate-pulse rounded"></div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-indigo-600 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo & Navigation Links */}
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              <h1 className="text-2xl font-bold text-white tracking-tight">TodoMaster</h1>
            </div>

            {/* Navigation Links - Desktop Only */}
            {session && (
              <div className="hidden md:flex items-center space-x-1">
                <a
                  href="/dashboard"
                  className="px-4 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium"
                >
                  Tasks
                </a>
                <a
                  href="/chat"
                  className="px-4 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium flex items-center space-x-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                  <span>AI Chat</span>
                </a>
              </div>
            )}
          </div>

          {/* Hamburger menu button for mobile */}
          <div className="md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white transition-colors"
              aria-expanded={isMobileMenuOpen ? 'true' : 'false'}
              aria-controls="mobile-menu"
            >
              <span className="sr-only">Open main menu</span>
              {isMobileMenuOpen ? (
                <svg
                  className="block h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  className="block h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              )}
            </button>
          </div>

          {/* User Info and Logout for desktop */}
          {session && (
            <div className="hidden md:flex items-center space-x-4">
              <div className="flex items-center space-x-3 bg-white/10 rounded-lg px-4 py-2">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-white text-blue-600 font-semibold">
                  {(session.user.name?.[0] || session.user.email?.[0] || 'U').toUpperCase()}
                </div>
                <div className="text-sm">
                  <p className="text-white font-medium">
                    {session.user.name || session.user.email}
                  </p>
                  {session.user.name && (
                    <p className="text-blue-100 text-xs">{session.user.email}</p>
                  )}
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
                className="bg-white/10 text-white border-white/30 hover:bg-white/20 hover:border-white/40"
              >
                Logout
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Mobile menu, show/hide based on menu state. */}
      {isMobileMenuOpen && session && (
        <div className="md:hidden bg-white/10 backdrop-blur-sm" id="mobile-menu">
          <div className="px-4 pt-2 pb-3 space-y-3">
            {/* Mobile Navigation Links */}
            <div className="space-y-1">
              <a
                href="/dashboard"
                className="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium"
              >
                Tasks
              </a>
              <a
                href="/chat"
                className="block px-3 py-2 text-white hover:bg-white/10 rounded-lg transition-colors font-medium flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                <span>AI Chat</span>
              </a>
            </div>

            {/* User Profile */}
            <div className="flex items-center space-x-3 px-3 py-2 rounded-lg bg-white/10">
              <div className="flex items-center justify-center w-10 h-10 rounded-full bg-white text-blue-600 font-semibold text-lg">
                {(session.user.name?.[0] || session.user.email?.[0] || 'U').toUpperCase()}
              </div>
              <div>
                <p className="text-white font-medium">{session.user.name || session.user.email}</p>
                {session.user.name && (
                  <p className="text-blue-100 text-xs">{session.user.email}</p>
                )}
              </div>
            </div>

            {/* Logout Button */}
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="w-full bg-white/10 text-white border-white/30 hover:bg-white/20"
            >
              Logout
            </Button>
          </div>
        </div>
      )}
    </nav>
  );
}
