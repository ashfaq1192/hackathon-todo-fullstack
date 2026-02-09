# Feature: User Authentication

**Feature ID**: authentication
**Status**: Active
**Phases**: II, III, IV, V

## Overview

Multi-user authentication system using Better Auth with JWT tokens. Enables user isolation, session management, and secure API access across all web-based phases.

## Phase Evolution

| Phase | Implementation | Key Additions |
|-------|---------------|---------------|
| II | Better Auth + JWT | Signup/login, session, 401 handler |
| III | Same + Chat Auth | Chat endpoint auth, conversation isolation |
| IV | Same | Kubernetes secrets management |
| V | Same | Cloud-native identity integration |

## Authentication Flow

```
1. User Registration
   Frontend → Better Auth → PostgreSQL → JWT Cookie

2. User Login
   Frontend → Better Auth → Validate → JWT Cookie

3. API Request
   Client → JWT Header → FastAPI Middleware → Validate → user_id extraction

4. Session Management
   Better Auth manages sessions, JWT in httpOnly cookies
```

## Components

### Frontend (Next.js)
- Better Auth client configuration
- Signup form with Zod validation (name, email, password)
- Login form with Zod validation (email, password)
- Session hook (`useSession`) for auth state
- 401 redirect handler for expired tokens
- Logout functionality

### Backend (FastAPI)
- JWT validation middleware
- User ID extraction from token claims
- Authorization: user_id in JWT must match resource ownership
- 401 Unauthorized for invalid/missing tokens
- 403 Forbidden for user_id mismatch

## JWT Token Structure

```json
{
  "sub": "user_abc123",
  "user_id": "user_abc123",
  "email": "user@example.com",
  "exp": 1703088000,
  "iat": 1703084400
}
```

## Security Requirements

- Passwords hashed with bcrypt (Better Auth default)
- JWT tokens stored in httpOnly cookies (XSS protection)
- HTTPS enforced in production
- Token expiration: configurable (default 7 days)
- CORS configuration for frontend domain

## API Authentication

All protected endpoints require:
```
Authorization: Bearer <jwt_token>
```

### Response Codes
| Code | Meaning |
|------|---------|
| 401 | Missing/invalid/expired JWT token |
| 403 | User ID mismatch (accessing other's resources) |

## Validation Rules

### Signup
- Name: Required, 2-50 characters
- Email: Required, valid email format
- Password: Required, 8+ characters, uppercase, lowercase, number

### Login
- Email: Required, valid format
- Password: Required

## Environment Variables

```bash
# Frontend
BETTER_AUTH_SECRET=<secret-key>
BETTER_AUTH_URL=<auth-url>

# Backend
JWT_SECRET_KEY=<secret-key>
JWT_ALGORITHM=HS256
```

## User Isolation

- Tasks: `user_id` indexed, queries filtered by authenticated user
- Conversations: `user_id` enforced on all chat operations
- API endpoints: Path parameter `{user_id}` validated against JWT

## Related Specifications

- Detailed Phase II frontend: `specs/archive/phase-2/004-frontend-nextjs/spec.md`
- Backend API auth: `specs/archive/phase-2/003-backend-api/spec.md`

---

*Last Updated: 2026-01-18*
