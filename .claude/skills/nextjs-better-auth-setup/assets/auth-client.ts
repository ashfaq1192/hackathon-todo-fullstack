/**
 * Better Auth Client
 *
 * Client-side authentication helper for React components.
 * Provides signup, signin, signout, and session management.
 */

import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
});

// Re-export commonly used hooks and methods
export const { useSession, signIn, signUp, signOut } = authClient;
