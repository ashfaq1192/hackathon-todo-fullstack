/**
 * Better Auth API Route Handler
 *
 * Handles all Better Auth routes via catch-all route pattern:
 * - POST /api/auth/sign-up/email - User registration
 * - POST /api/auth/sign-in/email - User login
 * - POST /api/auth/sign-out - User logout
 * - GET /api/auth/get-session - Get current session
 *
 * Better Auth automatically provides these endpoints.
 */

import { auth } from "@/lib/auth/auth";
import { toNextJsHandler } from "better-auth/next-js";

// Export GET and POST handlers for Better Auth
export const { POST, GET } = toNextJsHandler(auth);
