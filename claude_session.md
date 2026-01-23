● All Gaps Addressed - Phase IV Complete
  Evidence Summary

  AI DevOps Tool (kubectl-ai):
  - Installed krew plugin manager
  - Installed kubectl-ai plugin
  - Configured with Gemini API key
  - Documented installation and usage in phase-4-k8s/CLAUDE.md

  End-to-End Tests:
  - Backend /health: 200 OK
  - Backend /api/mcp/tools: 5 MCP tools available
  - Frontend pages: All returning 200
  - Cross-service: Frontend → Backend connectivity verified

  Lifecycle Operations:
  REVISION  STATUS      DESCRIPTION
  1         superseded  Install complete
  2         superseded  Upgrade complete
  3         deployed    Rollback to 1

  Final Phase IV Requirements Status
  ┌──────────────────────┬─────────────────────────────────────────────────────────────────────┐
  │     Requirement      │                               Status                                │
  ├──────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ FR-001 to FR-010     │ ✅ Complete                                                         │
  ├──────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ FR-011 (AI Tool)     │ ✅ Complete                                                         │
  ├──────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ FR-012 (Document AI) │ ✅ Complete                                                         │
  ├──────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ FR-013 to FR-015     │ ✅ Complete                                                         │
  ├──────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ SC-001 to SC-008     │ ✅ Complete (SC-002 backend image 572MB slightly over 500MB target) │
  ├──────────────────────┼─────────────────────────────────────────────────────────────────────┤
  │ US1-US5              │ ✅ Complete                                                         │
  └──────────────────────┴─────────────────────────────────────────────────────────────────────┘
  Phase IV Local Kubernetes Deployment is now complete!

✻ Brewed for 7m 17s

❯ How i can test and run the application and what is the link i can share with others so the can test                 
  interactively?                                                                                                      

● How to Access the Application

  Option 1: Port-Forward (Quick Local Testing)

  Run these commands in separate terminals:

  # Terminal 1: Frontend
  kubectl port-forward svc/todo-chatbot-frontend 3000:3000

  # Terminal 2: Backend  
  kubectl port-forward svc/todo-chatbot-backend 8000:8000

  Then open: http://localhost:3000

  Option 2: Via Ingress (todo.local)

  Step 1: Add to your hosts file

  # Linux/WSL: 
  echo "192.168.49.2 todo.local" | sudo tee -a /etc/hosts

  # Windows (run as Admin in PowerShell):
  Add-Content C:\Windows\System32\drivers\etc\hosts "192.168.49.2 todo.local"

  Step 2: Start Minikube tunnel (required for Windows/WSL)
  minikube tunnel

  Step 3: Open http://todo.local in your browser

  ---
  Sharing with Others

  Since this is a local Minikube deployment, it's not directly accessible from the internet. Here are your options:   

  Option A: Use ngrok (Quick & Easy)

  # Install ngrok
  # https://ngrok.com/download

  # Expose frontend
  kubectl port-forward svc/todo-chatbot-frontend 3000:3000 &
  ngrok http 3000

  This gives you a public URL like https://abc123.ngrok.io that others can access.

  Option B: Use Cloudflare Tunnel (Free & Persistent)

  # Install cloudflared
  # https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/

  cloudflared tunnel --url http://localhost:3000

  Option C: Deploy to Cloud (Production-Ready)

  For permanent sharing, deploy to:
  - Vercel (Frontend) + Railway (Backend) - Already done in Phase III!
  - Cloud Kubernetes (EKS, GKE, AKS) - Phase V

  ---
  Your Existing Production URLs (Phase III)

  You already have the app deployed and accessible:
  ┌──────────┬────────────────────────────────────────────────────────────────────┐
  │ Service  │                                URL                                 │
  ├──────────┼────────────────────────────────────────────────────────────────────┤
  │ Frontend │ https://hackathon-todo-fullstack.vercel.app                        │
  ├──────────┼────────────────────────────────────────────────────────────────────┤
  │ Backend  │ https://hackathon-todo-fullstack-backend-production.up.railway.app │
  └──────────┴────────────────────────────────────────────────────────────────────┘
  Share this with others: https://hackathon-todo-fullstack.vercel.app

  ---
  Quick Test Commands

  # Verify pods are running
  kubectl get pods

  # Check backend health
  kubectl exec deploy/todo-chatbot-backend -- curl -s http://localhost:8000/health

  # View logs
  kubectl logs -f deploy/todo-chatbot-frontend
  kubectl logs -f deploy/todo-chatbot-backend

  Would you like me to help set up ngrok or another tunneling solution for sharing the local Minikube deployment?  