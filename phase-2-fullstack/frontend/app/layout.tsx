// Root layout

import type { Metadata } from 'next';
import './globals.css';
import { ToastProvider } from '@/components/ui/ToastProvider'; // Import ToastProvider

export const metadata: Metadata = {
  title: 'Todo App - Hackathon II',
  description: 'Full-stack todo application with Next.js and FastAPI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50" suppressHydrationWarning>
        <ToastProvider />
        {children}
      </body>
    </html>
  );
}
