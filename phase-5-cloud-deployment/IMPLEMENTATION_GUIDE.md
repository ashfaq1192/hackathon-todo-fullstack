 Plan to implement                                                     │
│                                                                       │
│ Phase V Implementation Plan                                           │
│                                                                       │
│ Overview                                                              │
│                                                                       │
│ Implement all 3 parts sequentially: A (Advanced Features) → B (Local  │
│ Dapr+Kafka) → C (Cloud OKE)                                           │
│                                                                       │
│ Architecture: Multi-arch Docker builds (amd64+arm64). OKE nodes:      │
│ VM.Standard.A1.Flex (ARM64, Always Free).                             │
│                                                                       │
│ ---                                                                   │
│ PART A: Advanced Features (Start Here)                                │
│                                                                       │
│ All changes in phase-3-chatbot/ codebase. No infrastructure needed.   │
│                                                                       │
│ Stage 1: Database Migration                                           │
│                                                                       │
│ New file:                                                             │
│ phase-3-chatbot/backend/migrations/008_add_advanced_features.py       │
│                                                                       │
│ Add to tasks table:                                                   │
│ - due_date TIMESTAMP (nullable)                                       │
│ - recurring VARCHAR(10) NOT NULL DEFAULT 'none' (enum:                │
│ none/daily/weekly/monthly/yearly)                                     │
│ - recurring_end_date TIMESTAMP (nullable)                             │
│ - tags TEXT[] DEFAULT '{}' (PostgreSQL array)                         │
│                                                                       │
│ Add indexes: idx_tasks_due_date, idx_tasks_recurring, idx_tasks_tags  │
│ (GIN), idx_tasks_priority, idx_tasks_complete                         │
│                                                                       │
│ Follow pattern from migrations/007_chatbot_mcp.py.                    │
│                                                                       │
│ Stage 2: Backend Model                                                │
│                                                                       │
│ Modify: phase-3-chatbot/backend/src/models/task.py                    │
│ - Add RecurringType(str, Enum): none, daily, weekly, monthly, yearly  │
│ - Add fields to Task: due_date, recurring, recurring_end_date, tags   │
│ - Note: Use sa_column=Column(ARRAY(String)) for tags (PostgreSQL      │
│ array type)                                                           │
│                                                                       │
│ Modify: phase-3-chatbot/backend/src/models/__init__.py                │
│ - Export RecurringType                                                │
│                                                                       │
│ Stage 3: Backend Schemas                                              │
│                                                                       │
│ Modify: phase-3-chatbot/backend/src/schemas/task.py                   │
│ - Add due_date, recurring, recurring_end_date, tags to TaskCreate,    │
│ TaskUpdate, TaskPatch, TaskResponse                                   │
│ - Add TaskQueryParams class for search/filter/sort query parameters:  │
│   - search (str) - keyword search in title/description                │
│   - status (str) - all/pending/completed                              │
│   - priority (TaskPriority) - filter by priority                      │
│   - tags (list[str]) - filter by tags                                 │
│   - sort_by (str) - created_at/due_date/priority/title                │
│   - sort_order (str) - asc/desc                                       │
│                                                                       │
│ Stage 4: CRUD + API Routes                                            │
│                                                                       │
│ Modify: phase-3-chatbot/backend/src/database/crud.py                  │
│ - Update create_task() to accept **kwargs for new fields              │
│ - Add get_tasks_filtered() with dynamic query building (ILIKE search, │
│  status/priority/tag filters, sort)                                   │
│                                                                       │
│ Modify: phase-3-chatbot/backend/src/api/routes/tasks.py               │
│ - Add Query parameters to list_tasks endpoint (search, status,        │
│ priority, tags, sort_by, sort_order)                                  │
│ - Call get_tasks_filtered() instead of get_tasks_by_user()            │
│ - Pass new fields from TaskCreate to create_task() in create_new_task │
│                                                                       │
│ Stage 5: MCP Tools                                                    │
│                                                                       │
│ Modify (5 files):                                                     │
│ - phase-3-chatbot/backend/src/mcp/tools/add_task.py - Add due_date,   │
│ recurring, tags params + schema                                       │
│ - phase-3-chatbot/backend/src/mcp/tools/update_task.py - Add          │
│ due_date, recurring, tags params + schema                             │
│ - phase-3-chatbot/backend/src/mcp/tools/list_tasks.py - Include new   │
│ fields in output, add filter params                                   │
│ - phase-3-chatbot/backend/src/mcp/tools/complete_task.py - Minimal:   │
│ note recurring handling for Part B                                    │
│ - phase-3-chatbot/backend/src/mcp/tools/delete_task.py - No changes   │
│ needed                                                                │
│                                                                       │
│ Modify: phase-3-chatbot/backend/src/services/chat_service.py          │
│ - Update tool wrappers to pass new parameters                         │
│ - Update agent instructions to mention due dates, recurring tasks,    │
│ tags                                                                  │
│ - Update _extract_add_task_params for natural language date/tag       │
│ extraction                                                            │
│                                                                       │
│ Stage 6: Frontend                                                     │
│                                                                       │
│ Modify: phase-3-chatbot/frontend/types/task.ts                        │
│ - Add RecurringType type                                              │
│ - Add due_date, recurring, recurring_end_date, tags to Task,          │
│ TaskCreate, TaskUpdate, TaskPatch                                     │
│                                                                       │
│ Modify: phase-3-chatbot/frontend/components/tasks/CreateTaskForm.tsx  │
│ - Add due date picker (<input type="datetime-local">)                 │
│ - Add recurring select dropdown (none/daily/weekly/monthly/yearly)    │
│ - Add tags input (comma-separated, creates badges)                    │
│ - Update zod schema                                                   │
│                                                                       │
│ Modify: phase-3-chatbot/frontend/components/tasks/TaskItem.tsx        │
│ - Display due date (with overdue highlighting)                        │
│ - Display recurring badge/icon                                        │
│ - Display tags as colored pills                                       │
│ - Update edit mode with new fields                                    │
│                                                                       │
│ Modify: phase-3-chatbot/frontend/components/tasks/TaskList.tsx        │
│ - Add search input bar                                                │
│ - Add sort dropdown (created_at, due_date, priority, title) + order   │
│ toggle                                                                │
│ - Add tag filter                                                      │
│ - Pass query params to API calls                                      │
│                                                                       │
│ Modify: phase-3-chatbot/frontend/app/dashboard/page.tsx               │
│ - Pass search/filter/sort state to TaskList                           │
│                                                                       │
│ Stage 7: Backend Tests                                                │
│                                                                       │
│ Modify:                                                               │
│ - phase-3-chatbot/backend/tests/unit/test_task_model.py -             │
│ RecurringType enum, new field defaults                                │
│ - phase-3-chatbot/backend/tests/unit/test_schemas.py - New schema     │
│ fields validation                                                     │
│ - phase-3-chatbot/backend/tests/unit/mcp/test_add_task.py - New       │
│ params                                                                │
│ - phase-3-chatbot/backend/tests/unit/mcp/test_update_task.py - New    │
│ params                                                                │
│ - phase-3-chatbot/backend/tests/unit/mcp/test_list_tasks.py - New     │
│ output fields                                                         │
│                                                                       │
│ New file:                                                             │
│ phase-3-chatbot/backend/tests/integration/test_search_filter_sort.py  │
│                                                                       │
│ ---                                                                   │
│ PART B: Local Dapr + Kafka on Minikube                                │
│                                                                       │
│ Stage 8: Dapr Component Configs                                       │
│                                                                       │
│ New files in phase-5-cloud-deployment/dapr/components/:               │
│ - kafka-pubsub.yaml - pubsub.kafka pointing to local Redpanda         │
│ - statestore.yaml - state.postgresql using Neon                       │
│ - kubernetes-secrets.yaml - secretstores.kubernetes                   │
│ - cron-binding.yaml - bindings.cron for reminders (or Dapr Jobs)      │
│                                                                       │
│ Stage 9: Event Publisher in Backend                                   │
│                                                                       │
│ New file: phase-3-chatbot/backend/src/services/event_publisher.py     │
│ - Publish to Dapr sidecar HTTP API: POST                              │
│ http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}               │
│ - Events: task-created, task-updated, task-completed, task-deleted on │
│  task-events                                                          │
│ - Reminder scheduling on reminders topic                              │
│ - Real-time sync on task-updates topic                                │
│                                                                       │
│ Modify: phase-3-chatbot/backend/src/database/crud.py                  │
│ - Call publish_task_event() after each CRUD operation (async,         │
│ non-blocking)                                                         │
│                                                                       │
│ New file: phase-3-chatbot/backend/src/services/reminder_service.py    │
│ - Schedule reminders via Dapr Jobs API when tasks have due_date set   │
│                                                                       │
│ Stage 10: Consumer Microservices                                      │
│                                                                       │
│ New directories in phase-5-cloud-deployment/services/:                │
│                                                                       │
│ 1. notification-service/ - Subscribes to reminders, logs              │
│ notifications                                                         │
│ 2. recurring-task-service/ - Subscribes to task-events, creates next  │
│ occurrence on completion                                              │
│ 3. audit-service/ - Subscribes to task-events, stores audit log       │
│                                                                       │
│ Each is a minimal FastAPI app with Dapr subscription endpoint.        │
│                                                                       │
│ Stage 11: Local Kafka + Helm Updates                                  │
│                                                                       │
│ New files in phase-5-cloud-deployment/k8s/kafka/:                     │
│ - Redpanda Helm chart values or Strimzi Kafka cluster manifest        │
│ - Topic definitions: task-events, reminders, task-updates             │
│                                                                       │
│ Modify Helm chart:                                                    │
│ - phase-4-k8s/helm/todo-chatbot/templates/backend-deployment.yaml -   │
│ Add Dapr sidecar annotations                                          │
│ - phase-4-k8s/helm/todo-chatbot/templates/frontend-deployment.yaml -  │
│ Add Dapr annotations                                                  │
│ - Add new deployment templates for consumer services                  │
│ - New file: phase-4-k8s/helm/todo-chatbot/values-dapr.yaml            │
│                                                                       │
│ Modify Docker:                                                        │
│ - phase-4-k8s/docker/backend/Dockerfile - Add                         │
│ --platform=$TARGETPLATFORM for multi-arch                             │
│ - phase-4-k8s/docker/frontend/Dockerfile - Same multi-arch support    │
│ - New Dockerfiles for consumer services                               │
│ - phase-4-k8s/scripts/build-images.sh - Add docker buildx multi-arch  │
│ support                                                               │
│                                                                       │
│ ---                                                                   │
│ PART C: Cloud OKE Deployment                                          │
│                                                                       │
│ Stage 12: OKE Cluster + OCIR                                          │
│                                                                       │
│ - Configure OCI CLI                                                   │
│ - Create Enhanced Cluster with ARM64 node pool (VM.Standard.A1.Flex,  │
│ Always Free)                                                          │
│ - Set up OCIR (Oracle Container Registry)                             │
│ - Push multi-arch images to OCIR                                      │
│ - Generate kubeconfig                                                 │
│                                                                       │
│ Stage 13: Dapr HA + Redpanda Cloud                                    │
│                                                                       │
│ - Install Dapr HA mode on OKE (dapr init -k --enable-ha=true)         │
│ - Create cloud Dapr component: kafka-pubsub-cloud.yaml (Redpanda      │
│ Cloud SASL auth)                                                      │
│ - New file: phase-4-k8s/helm/todo-chatbot/values-oke.yaml (OCIR       │
│ paths, ARM64 affinity, cloud Kafka URLs)                              │
│ - Deploy all services to OKE                                          │
│                                                                       │
│ Stage 14: CI/CD (GitHub Actions)                                      │
│                                                                       │
│ New files:                                                            │
│ - .github/workflows/ci.yml - Test, lint, build, scan (Trivy), push    │
│ images                                                                │
│ - .github/workflows/cd.yml - OIDC auth to OCI, Helm deploy to OKE     │
│                                                                       │
│ Stage 15: Observability                                               │
│                                                                       │
│ New file: phase-3-chatbot/backend/src/observability/tracing.py -      │
│ OpenTelemetry auto-instrumentation                                    │
│ New file: phase-5-cloud-deployment/k8s/otel/otel-collector.yaml -     │
│ OTLP receiver → Grafana Cloud                                         │
│ - Grafana Cloud dashboards: latency, error rates, Kafka consumer lag, │
│  logs                                                                 │
│                                                                       │
│ ---                                                                   │
│ Execution Order                                                       │
│                                                                       │
│ Part A: [Stage 1] → [Stage 2] → [Stage 3] → [Stage 4] → [Stage 5] →   │
│ [Stage 6] → [Stage 7]                                                 │
│ Part B: [Stage 8] → [Stage 9] → [Stage 10] → [Stage 11]               │
│ Part C: [Stage 12] → [Stage 13] → [Stage 14] → [Stage 15]             │
│                                                                       │
│ We start with Stage 1 (database migration) immediately.               │
│                                                                       │
│ ---                                                                   │
│ Verification                                                          │
│                                                                       │
│ Part A verification                                                   │
│                                                                       │
│ - Run backend tests: cd phase-3-chatbot/backend && python -m pytest   │
│ tests/                                                                │
│ - Run frontend tests: cd phase-3-chatbot/frontend && npm test         │
│ - Manual: Create task with due_date, tags, recurring via chat and     │
│ REST API                                                              │
│ - Manual: Search, filter by priority/tags, sort by due_date           │
│                                                                       │
│ Part B verification                                                   │
│                                                                       │
│ - dapr status -k shows all components running                         │
│ - Create task → check task-events Kafka topic has event               │
│ - Set due_date → check reminders topic                                │
│ - Complete recurring task → new occurrence auto-created               │
│ - All Dapr building blocks functional                                 │
│                                                                       │
│ Part C verification                                                   │
│                                                                       │
│ - kubectl get pods -n todo shows all pods running on OKE              │
│ - Application accessible via OKE ingress/load balancer                │
│ - GitHub Actions pipeline runs on push                                │
│ - Grafana Cloud dashboards showing metrics/traces/logs 


**************************************************
  Test Results Summary

  Backend API (port 8000)

  - Health check: Healthy
  - Task CRUD: Create, read, update, patch, delete all working
  - Advanced fields: due_date, recurring, tags all persisted correctly
  - Search/Filter/Sort: Keyword search, priority filter, due date sort, tag filter all working
  - 152 unit/integration tests: All passing

  Frontend (port 3000)

  - Signup: User registration via Better Auth → PostgreSQL (Neon)
  - Dashboard: Loads with authenticated user, shows tasks
  - Create Task Form: Title, Description, Priority, Due Date picker, Recurring Schedule, Tags input — all functional
  - Task Display: Shows ID, priority badge, recurring icon, due date, tags as pills, creation date
  - Search: Keyword search filters tasks in real-time
  - Priority Filter: Low/Medium/High/All filter buttons work
  - Sort: Date Created/Due Date/Priority/Title with Asc/Desc toggle
  - Complete Task: Checkbox toggle with confirmation dialog, optimistic update
  - Filter Counts: Dynamic counts (All 2, Active 1, Completed 1)

  AI Chatbot

  - Task creation via natural language: "Add a low priority task called Buy groceries" → SUCCESS
  - Task listing: "Show me my pending tasks" → Shows all tasks with advanced fields
  - MCP tools: Working correctly through Gemini API

  Missing lib files created during testing

  - lib/api/client.ts — API client with retry logic + task-specific methods
  - lib/auth/client.ts — Better Auth client-side hooks
  - lib/auth/auth.ts — Better Auth server-side config
  - lib/validation/schemas.ts — Zod validation schemas
  - lib/chat/messageUtils.ts — Chat message parsing utilities

  The application is fully functional and ready for deployment (Part C). Shall I proceed with Part C (Cloud OKE Deployment)?     

✻ Crunched for 18m 42s

❯ Before proceeding to deployment please let me know in concise form that what will be your process of deployment (brief in      
  ascending order).                                                                                                              

● Part C: Cloud OKE Deployment Steps

  1. Build & Push Docker Images — Build multi-arch Docker images for backend, frontend, and 3 consumer services; push to OCIR    
  (Oracle Container Registry)
  2. Create OKE Enhanced Cluster — Provision Oracle Kubernetes Engine cluster with x86_64 node pool (~$3/day, deploy-demo-delete 
  within 24h)
  3. Install Dapr on OKE — dapr init -k --enable-ha=true for high-availability mode
  4. Deploy Redpanda/Kafka — Apply Redpanda manifests or connect to Redpanda Cloud; create 3 topics (task-events, reminders,     
  task-updates)
  5. Apply Dapr Components — Deploy Dapr component YAMLs (kafka-pubsub, statestore, kubernetes-secrets, cron-binding)
  6. Deploy via Helm — helm install using values-oke.yaml (backend, frontend, notification-service, recurring-task-service,      
  audit-service)
  7. Configure Ingress/DNS — Set up OKE load balancer for external access
  8. CI/CD Pipeline — GitHub Actions workflows for test → build → scan (Trivy) → push → deploy
  9. Observability — OpenTelemetry Collector + Grafana Cloud (metrics, logs, traces)
  10. Verify & Demo — End-to-end validation, record 90-second demo video, then delete cluster









