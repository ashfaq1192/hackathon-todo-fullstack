// User types for Better Auth integration

export interface User {
  id: string;                    // Unique user identifier (UUID from Better Auth)
  email: string;                 // User's email address
  createdAt: string;             // ISO 8601 timestamp of account creation
}

export interface UserSession {
  user: User;
  token: string;                 // JWT access token
  expiresAt: string;             // ISO 8601 timestamp of token expiration
}
