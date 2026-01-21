nvironment Variable Configuration

  Your backend and frontend have separate configurations, but they must be synchronized for your     
  application to work. Here are the critical variables to set in your Vercel project's settings:     

   * NEXT_PUBLIC_API_URL: This must be set to your backend's URL:
     https://hackathon-todo-fullstack-backend-production.up.railway.app
   * DATABASE_URL: This must be the same Neon PostgreSQL connection string you used for your backend.   * JWT_SECRET_KEY: This must be identical to the JWT_SECRET_KEY in your backend.
   * BETTER_AUTH_SECRET: Generate a new secure string for this. You can use openssl rand -base64 32  
     in your terminal to create one.
   * BETTER_AUTH_URL: This will be your Vercel app's URL (e.g.,
     https://your-project-name.vercel.app).

  Step-by-Step Vercel Deployment

  This guide is based on the frontend-vercel-deployment skill and is tailored for your project.      

  1. Vercel Project Settings

  In your Vercel project dashboard, make sure the settings match these verified values:

   * Framework: Next.js
   * Root Directory: phase-3-chatbot/frontend
   * Install Command: npm 1install
   * Build Command: npm run build

  2. Configure Environment Variables

  In your Vercel project, go to Settings > Environment Variables and add the variables listed in the 
  "Environment Variable Configuration" section above.

  3. Deploy using Vercel CLI

  For the first deployment, using the Vercel CLI is recommended as it allows you to see build logs in  real-time.

   1. Install Vercel CLI:
   1     npm install -g vercel

   2. Navigate to your project's root directory:
   1     cd /mnt/e/projects/hackathon-todo-fullstack

   3. Link your local project to Vercel:
   1     vercel link
      Follow the prompts to connect to your Vercel project.

   4. Deploy to production:
   1     vercel --prod

  This command will start the deployment process. You can monitor the build and deployment progress  
  directly in your terminal.

  Deployment Checklist

  Before deploying, ensure you've followed these steps:

   * [ ] Root Directory is set to phase-3-chatbot/frontend in Vercel.
   * [ ] phase-3-chatbot/frontend/vercel.json uses npm and not pnpm.
   * [ ] No environment variables are hardcoded in vercel.json.
   * [ ] phase-3-chatbot/frontend/tsconfig.json has "baseUrl": "." and "moduleResolution": "node".   
   * [ ] phase-3-chatbot/frontend/next.config.js does not have an eslint section.
   * [ ] All necessary environment variables are set in the Vercel Dashboard.

  Once the deployment is complete, your frontend will be live on Vercel and connected to your Railway  backend.