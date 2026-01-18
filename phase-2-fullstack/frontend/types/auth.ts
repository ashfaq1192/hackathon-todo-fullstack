// Authentication payload types for Better Auth

import { User } from './user';

export interface SignupPayload {
  name: string;                  // User's full name
  email: string;                 // User's email
  password: string;              // User's password (min 8 chars)
  confirmPassword?: string;      // Password confirmation (client-side only)
}

export interface LoginPayload {
  email: string;                 // User's email
  password: string;              // User's password
}

export interface AuthResponse {
  user: User;                    // User object
  token: string;                 // JWT access token
  expiresAt: string;             // Token expiration timestamp
}
