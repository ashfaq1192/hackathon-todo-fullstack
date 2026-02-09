"use client";

import { useSession } from '@/lib/auth/client'; // Assuming Better Auth client is available
import ChatInterface from '@/components/chat/ChatInterface';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ChatPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  useEffect(() => {
    // Redirect to login if not authenticated and session is resolved
    if (!isPending && !session) {
      router.push('/login');
    }
  }, [session, isPending, router]);

  if (isPending) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p>Loading session...</p>
      </div>
    );
  }

  if (!session) {
    // Should be redirected by useEffect, but as a fallback
    return (
      <div className="flex justify-center items-center min-h-screen">
        <p>Redirecting to login...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      <header className="bg-gray-800 text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">AI Chatbot</h1>
        {/* Potentially add a logout button here */}
      </header>
      <main className="flex-grow">
        <ChatInterface />
      </main>
    </div>
  );
}
