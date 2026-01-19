# Evolution of Todo - Phase II: Full-Stack Web Application

This document provides details for Phase II of the "Evolution of Todo" project, which evolves the simple CLI application into a full-stack, production-ready web application.

## 🎯 Project Overview

Phase II transforms the Todo application into a modern, cloud-native web application. It introduces a separate backend API and a frontend user interface, both built with modern technologies. This phase focuses on delivering a feature-rich, secure, and user-friendly experience, demonstrating the principles of Spec-Driven Development on a larger scale.

## 🛠️ Tech Stack

### Backend
- **Web Framework**: FastAPI 0.115.0+ (Python 3.13+)
- **ORM**: SQLModel 0.0.22+ (combining Pydantic and SQLAlchemy)
- **Database**: Neon Serverless PostgreSQL (with SSL/TLS)
- **Authentication**: JWT with Better Auth integration
- **Testing**: `pytest` and `pytest-cov` (85% coverage)
- **Deployment**: Railway (serverless Python environment)

### Frontend
- **Framework**: Next.js 16+ (using the App Router)
- **UI Library**: React 19+
- **Language**: TypeScript 5+ (in strict mode)
- **Styling**: Tailwind CSS 4+
- **Authentication**: Better Auth for email/password and JWT management
- **Password Reset**: `Resend` for handling email services
- **Forms**: React Hook Form combined with `Zod` for validation
- **HTTP Client**: `Axios` with built-in retry logic
- **Testing**: `Vitest` for unit tests and `Playwright` for E2E tests
- **Deployment**: Vercel (providing CDN and HTTPS)

## ✨ Features

### ✅ Authentication & Security
- User signup with email validation.
- User login that issues JWT tokens.
- Secure password hashing via Better Auth.
- Password reset functionality using email verification.
- JWTs are stored in httpOnly cookies to protect against XSS attacks.
- Strict user data isolation, ensuring users can only see their own tasks.
- Automatic redirection to the login page upon a 401 Unauthorized error.

### ✅ Task Management (CRUD)
- Create tasks with validation (title max 200, description max 1000 characters).
- View all tasks with loading states for a better UX.
- Mark tasks as complete or incomplete with optimistic updates for a faster feel.
- Update the details of existing tasks.
- Delete tasks from the list.
- Real-time character counters on input fields.

### ✅ User Experience
- Fully responsive design for mobile, tablet, and desktop.
- Loading skeletons are shown while data is being fetched.
- Toast notifications provide feedback for all user actions.
- Empty state messages are displayed when there are no tasks.
- Robust error handling with a retry mechanism (3 attempts with exponential backoff).
- Enhanced accessibility with ARIA labels and keyboard navigation.

### ✅ Production Readiness
- TypeScript is in strict mode with zero errors.
- ESLint is configured for code quality (ESLint 9).
- A comprehensive suite of 14 passing unit tests written with Vitest.
- The application builds successfully for production (Next.js 16.1.1).
- Deployed to Vercel (frontend) and Railway (backend).
- HTTPS is enforced for all traffic.
- Secure management of environment variables.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Next.js 16 App (React 19 + TypeScript 5)                  │ │
│  │  • App Router (app/)                                        │ │
│  │  • Better Auth (email/password, JWT in httpOnly cookies)   │ │
│  │  • Tailwind CSS 4 (responsive design)                      │ │
│  │  • React Hook Form + Zod (validation)                      │ │
│  │  • Axios with retry logic                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ HTTPS (Vercel CDN)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (Railway)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  FastAPI 0.115.0+ (Python 3.13+)                           │ │
│  │  • JWT Middleware (validates tokens)                       │ │
│  │  • CORS configured for Vercel domain                       │ │
│  │  • SQLModel ORM                                            │ │
│  │  • Pydantic request/response validation                    │ │
│  │  • User isolation enforced via JWT claims                  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ SSL/TLS
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DATABASE (Neon PostgreSQL)                      │
│  • Serverless PostgreSQL (auto-scaling)                         │
│  • SSL required                                                  │
│  • Branching for dev/staging/prod                               │
│  • Automatic backups                                             │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Getting Started

### Prerequisites
- Python 3.13+
- Node.js 20+
- `uv` Python package manager
- A free Neon account for the PostgreSQL database.

### Backend Setup

1.  **Navigate to the backend directory**:
    ```bash
    cd phase-2-fullstack/backend
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

3.  **Configure the environment**:
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file with your Neon `DATABASE_URL` and a `JWT_SECRET_KEY`.

4.  **Run database migrations**:
    ```bash
    python -c "from src.database import init_db, get_engine; init_db(get_engine())"
    ```

5.  **Start the backend server**:
    ```bash
    uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The backend will be running at `http://localhost:8000`, and API documentation will be available at `http://localhost:8000/docs`.

### Frontend Setup

1.  **Navigate to the frontend directory**:
    ```bash
    cd phase-2-fullstack/frontend
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    ```

3.  **Configure the environment**:
    ```bash
    cp .env.example .env.local
    ```
    Edit the `.env.local` file with your `DATABASE_URL`, a `BETTER_AUTH_SECRET`, the same `JWT_SECRET_KEY` as the backend, and set `NEXT_PUBLIC_API_URL=http://localhost:8000`.

4.  **Run Better Auth migrations**:
    ```bash
    npx @better-auth/cli migrate --config lib/auth/auth.ts
    ```

5.  **Start the frontend server**:
    ```bash
    npm run dev
    ```
    The frontend will be running at `http://localhost:3000`.

### Access the Application

1.  Open your browser to `http://localhost:3000`.
2.  Click **"Sign Up"** to create an account.
3.  Log in to access the dashboard and start managing your tasks.

## 🧪 Testing

### Backend (pytest)
```bash
cd phase-2-fullstack/backend
pytest --cov=src
```

### Frontend (Vitest + Playwright)
```bash
cd phase-2-fullstack/frontend
npm run test  # Unit tests
npm run test:e2e # E2E tests
```
