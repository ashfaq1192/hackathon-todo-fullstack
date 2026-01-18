# Todo App Frontend

A modern, responsive todo application built with Next.js 16, React 19, and Better Auth.

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **UI Library**: React 19+
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 4+
- **Authentication**: Better Auth with JWT
- **Form Management**: React Hook Form + Zod
- **HTTP Client**: Axios with retry logic
- **Notifications**: React Hot Toast
- **Testing**: Vitest + Playwright
- **Database**: Neon Serverless PostgreSQL
- **Deployment**: Vercel

## Features

### Core Functionality
- ✅ User authentication (signup/login) with Better Auth
- ✅ View all tasks with loading states and empty state
- ✅ Create new tasks with validation
- ✅ Mark tasks as complete/incomplete with optimistic updates
- ✅ Real-time character counters for title (200) and description (1000)
- ✅ Toast notifications for all operations
- ✅ Responsive design (mobile, tablet, desktop)

### UX Enhancements
- ✅ Loading skeletons during data fetch
- ✅ Error handling with retry logic (3 attempts, exponential backoff)
- ✅ 401 auto-redirect to login
- ✅ Logout functionality
- ✅ Visual distinction for completed tasks (strikethrough, green background)
- ✅ Accessibility attributes (ARIA labels, keyboard navigation)
- ✅ Touch-friendly buttons (44x44px minimum per WCAG)

### Security
- ✅ JWT stored in httpOnly cookies (XSS protection)
- ✅ HTTPS enforced in production
- ✅ Environment variables for sensitive config
- ✅ Auto-redirect on unauthorized access

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth route group
│   │   ├── login/         # Login page
│   │   └── signup/        # Signup page
│   ├── (dashboard)/       # Dashboard route group
│   │   └── page.tsx       # Tasks dashboard
│   ├── api/               # API routes
│   │   ├── auth/          # Better Auth endpoints
│   │   └── token/         # JWT token endpoint
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Landing page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── auth/              # SignupForm, LoginForm
│   ├── tasks/             # TaskList, TaskItem, CreateTaskForm
│   ├── layout/            # Navigation
│   └── ui/                # Button, Input, Spinner, ToastProvider
├── lib/                   # Utilities
│   ├── api/               # API client with retry logic
│   ├── auth/              # Better Auth config
│   └── validation/        # Zod schemas
├── types/                 # TypeScript types
│   ├── user.ts            # User types
│   ├── task.ts            # Task types
│   ├── auth.ts            # Auth payload types
│   ├── api.ts             # API error types
│   └── ui.ts              # UI state types
├── __tests__/             # Unit tests (Vitest)
├── e2e/                   # E2E tests (Playwright)
└── public/                # Static assets
```

## Prerequisites

- Node.js 20+ (or 18+)
- npm or pnpm or yarn
- Backend API running at `http://localhost:8000` (or configure `NEXT_PUBLIC_API_URL`)
- Neon PostgreSQL database (for Better Auth)

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
# or
pnpm install
# or
yarn install
```

### 2. Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
# Neon PostgreSQL connection string (for Better Auth)
DATABASE_URL=postgres://user:password@host/database?sslmode=require

# Better Auth configuration
BETTER_AUTH_SECRET=your-32-character-secret-key-here
BETTER_AUTH_URL=http://localhost:3000

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# JWT secret (must match backend)
JWT_SECRET_KEY=your-jwt-secret-key-matching-backend
```

**Important**:
- `BETTER_AUTH_SECRET` should be a random 32+ character string
- `JWT_SECRET_KEY` must match the backend for token validation
- `DATABASE_URL` should point to your Neon PostgreSQL instance

### 3. Run Database Migrations

Better Auth requires database tables for user authentication:

```bash
npx @better-auth/cli migrate --config lib/auth/auth.ts
```

This creates the following tables:
- `user` - User accounts
- `session` - Active sessions
- `account` - OAuth accounts (if using OAuth)
- `verification` - Email verification tokens

### 4. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Available Scripts

```bash
# Development
npm run dev              # Start dev server (port 3000)

# Build
npm run build            # Create production build
npm start                # Start production server

# Type Checking
npm run type-check       # Run TypeScript compiler (no emit)

# Testing
npm run test             # Run unit tests (Vitest)
npm run test:ui          # Run unit tests with UI
npm run test:coverage    # Run tests with coverage report
npm run test:e2e         # Run E2E tests (Playwright)
npm run test:e2e:ui      # Run E2E tests with UI

# Code Quality
npm run lint             # Run ESLint
npm run format           # Format code with Prettier
npm run format:check     # Check code formatting
```

## Usage Guide

### 1. Create an Account

1. Visit `http://localhost:3000`
2. Click "Sign Up"
3. Enter email and password (min 8 characters)
4. Confirm password
5. Click "Sign Up" button
6. You'll be auto-logged in and redirected to the dashboard

### 2. Log In

1. Visit `http://localhost:3000/login`
2. Enter your email and password
3. Click "Log In"
4. You'll be redirected to the tasks dashboard

### 3. Create a Task

1. Fill in the title (required, max 200 chars)
2. Optionally add a description (max 1000 chars)
3. Watch the character counter update in real-time
4. Click "Add Task"
5. The task appears immediately in the list

### 4. Mark Task as Complete

1. Click the checkbox next to any task
2. The UI updates immediately (optimistic update)
3. Task shows strikethrough and green background
4. Click again to mark as incomplete

### 5. Log Out

1. Click the "Logout" button in the top navigation
2. You'll be redirected to the login page
3. Your session is cleared

## Environment Configuration

### Development
- API URL: `http://localhost:8000`
- Frontend URL: `http://localhost:3000`
- Database: Neon PostgreSQL (development instance)

### Production (Vercel)
- Set all environment variables in Vercel dashboard
- `NEXT_PUBLIC_API_URL` should point to your production backend
- `BETTER_AUTH_URL` should be your Vercel domain
- Ensure CORS is configured on the backend for your Vercel domain

## Testing

### Unit Tests

```bash
# Run all unit tests
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test -- --watch
```

Current test coverage:
- SignupForm: 7 tests
- LoginForm: 7 tests
- CreateTaskForm: 8 tests
- TaskItem: 3 tests
- TaskList: 5 tests

### E2E Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with UI
npm run test:e2e:ui
```

E2E test scenarios:
- Authentication flow (signup, login, logout)
- Task CRUD operations (create, read, update, delete)
- Responsive design at multiple viewports

## API Integration

The frontend communicates with the backend via the API client (`lib/api/client.ts`):

### Endpoints Used

- `POST /api/auth/sign-up/email` - User signup
- `POST /api/auth/sign-in/email` - User login
- `POST /api/auth/sign-out` - User logout
- `GET /api/{user_id}/tasks` - Fetch all tasks
- `POST /api/{user_id}/tasks` - Create new task
- `PATCH /api/{user_id}/tasks/{id}` - Update task (partial)
- `DELETE /api/{user_id}/tasks/{id}` - Delete task

### Retry Logic

The API client includes exponential backoff retry:
- 3 attempts total
- Delays: 1s, 2s, 4s
- Retries only on network errors (not HTTP errors)
- Auto-redirects to `/login` on 401 Unauthorized

## Troubleshooting

### "User not authenticated" error
- Check that you're logged in
- Verify JWT token is stored in localStorage (`api_token`)
- Check browser console for 401 errors
- Try logging out and back in

### Build fails with TypeScript errors
```bash
npm run type-check
```
Fix any type errors reported

### Database migration fails
- Verify `DATABASE_URL` is correct
- Ensure Neon PostgreSQL instance is accessible
- Check that SSL is enabled (`?sslmode=require`)

### Tasks not loading
- Verify backend is running at `NEXT_PUBLIC_API_URL`
- Check browser Network tab for API call failures
- Verify CORS is configured on backend

### Hot reload not working
- Restart the dev server (`npm run dev`)
- Clear `.next` directory (`rm -rf .next`)
- Check for file system issues (WSL users: move project to Linux filesystem)

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile: iOS Safari, Chrome Android

## Performance

- Lighthouse Score: >90 (all categories)
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- Cumulative Layout Shift: <0.1

## Accessibility

- WCAG 2.1 Level AA compliance
- Keyboard navigation supported
- Screen reader friendly (ARIA labels)
- Touch targets ≥44x44px
- Color contrast ratios ≥4.5:1

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues, questions, or contributions:
- GitHub Issues: [your-repo/issues](https://github.com/your-repo/issues)
- Email: support@yourdomain.com

---

**Built with ❤️ for Hackathon Phase II**
