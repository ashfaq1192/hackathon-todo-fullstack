11:52:06.258 Running build in Washington, D.C., USA (East) – iad1
11:52:06.258 Build machine configuration: 2 cores, 8 GB
11:52:06.411 Cloning github.com/ashfaq1192/hackathon-todo-fullstack (Branch: main, Commit: a2efc1a)
11:52:06.412 Previous build caches not available.
11:52:06.767 Cloning completed: 355.000ms
11:52:07.252 Running "vercel build"
11:52:08.297 Vercel CLI 50.4.4
11:52:08.600 Running "install" command: `npm install`...
11:52:39.254 npm warn deprecated next@15.1.0: This version has a security vulnerability. Please upgrade to a patched version. See https://nextjs.org/blog/CVE-2025-66478 for more details.
11:52:39.801 
11:52:39.802 added 886 packages, and audited 887 packages in 31s
11:52:39.802 
11:52:39.802 286 packages are looking for funding
11:52:39.802   run `npm fund` for details
11:52:39.882 
11:52:39.882 8 vulnerabilities (7 moderate, 1 critical)
11:52:39.882 
11:52:39.883 To address all issues (including breaking changes), run:
11:52:39.883   npm audit fix --force
11:52:39.883 
11:52:39.883 Run `npm audit` for details.
11:52:39.953 Detected Next.js version: 15.1.0
11:52:39.954 Running "npm run build"
11:52:40.204 
11:52:40.205 > hackathon-todo-frontend@0.1.0 build
11:52:40.205 > next build
11:52:40.206 
11:52:40.986  ⚠ Invalid next.config.js options detected: 
11:52:40.987  ⚠     Expected object, received boolean at "devIndicators"
11:52:40.987  ⚠ See more info here: https://nextjs.org/docs/messages/invalid-next-config
11:52:40.995 Attention: Next.js now collects completely anonymous telemetry regarding usage.
11:52:40.998 This information is used to shape Next.js' roadmap and prioritize features.
11:52:40.998 You can learn more, including how to opt-out if you'd not like to participate in this anonymous program, by visiting the following URL:
11:52:40.998 https://nextjs.org/telemetry
11:52:40.999 
11:52:41.056    ▲ Next.js 15.1.0
11:52:41.057 
11:52:41.081    Creating an optimized production build ...
11:52:50.484 Failed to compile.
11:52:50.485 
11:52:50.485 ./app/(auth)/forgot-password/page.tsx
11:52:50.486 Module not found: Can't resolve '@/lib/validation/schemas'
11:52:50.487 
11:52:50.487 https://nextjs.org/docs/messages/module-not-found
11:52:50.487 
11:52:50.487 ./app/(auth)/forgot-password/page.tsx
11:52:50.487 Module not found: Can't resolve '@/lib/auth/client'
11:52:50.488 
11:52:50.488 https://nextjs.org/docs/messages/module-not-found
11:52:50.488 
11:52:50.488 ./app/(auth)/reset-password/page.tsx
11:52:50.488 Module not found: Can't resolve '@/lib/validation/schemas'
11:52:50.489 
11:52:50.489 https://nextjs.org/docs/messages/module-not-found
11:52:50.489 
11:52:50.489 ./app/(auth)/reset-password/page.tsx
11:52:50.489 Module not found: Can't resolve '@/lib/auth/client'
11:52:50.489 
11:52:50.489 https://nextjs.org/docs/messages/module-not-found
11:52:50.491 
11:52:50.491 ./app/dashboard/page.tsx
11:52:50.491 Module not found: Can't resolve '@/lib/auth/client'
11:52:50.491 
11:52:50.491 https://nextjs.org/docs/messages/module-not-found
11:52:50.491 
11:52:50.497 
11:52:50.498 > Build failed because of webpack errors
11:52:50.528 Error: Command "npm run build" exited with 1