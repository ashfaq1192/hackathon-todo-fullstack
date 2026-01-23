# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/008-local-k8s-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec. Manual validation via deployment scripts.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Infrastructure**: `phase-4-k8s/` directory
- **Source code**: `phase-3-chatbot/` (existing, read-only reference)
- **Dockerfiles**: `phase-4-k8s/docker/{backend,frontend}/Dockerfile`
- **Helm charts**: `phase-4-k8s/helm/todo-chatbot/`
- **Scripts**: `phase-4-k8s/scripts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify prerequisites and establish base structure

- [x] T001 Verify Docker is installed and running with `docker version`
- [x] T002 Verify phase-3-chatbot code exists and is functional in phase-3-chatbot/
- [x] T003 [P] Create phase-4-k8s/CLAUDE.md for AI tool documentation
- [x] T004 [P] Create .dockerignore file in phase-4-k8s/docker/backend/.dockerignore
- [x] T005 [P] Create .dockerignore file in phase-4-k8s/docker/frontend/.dockerignore

---

## Phase 2: User Story 2 - Developer Containerizes Applications (Priority: P1) 🎯 MVP-1

**Goal**: Create optimized Docker images for frontend and backend applications

**Independent Test**: Build Docker images and run with docker-compose, verify all chatbot features work

**Note**: US2 (Containerization) must complete BEFORE US1 (Deployment) per spec dependencies

### Implementation for User Story 2

- [x] T006 [US2] Create multi-stage Dockerfile for backend in phase-4-k8s/docker/backend/Dockerfile
- [x] T007 [US2] Create multi-stage Dockerfile for frontend in phase-4-k8s/docker/frontend/Dockerfile
- [x] T008 [US2] Update phase-4-k8s/scripts/build-images.sh with proper build commands
- [x] T009 [US2] Create docker-compose.yml for local testing in phase-4-k8s/docker-compose.yml
- [x] T010 [US2] Build backend Docker image and verify size <500MB (391MB)
- [x] T011 [US2] Build frontend Docker image and verify size <500MB (238MB)
- [x] T012 [US2] Test containers with docker-compose up and verify chatbot functionality

**Checkpoint**: Both Docker images build successfully and application runs in containers

---

## Phase 3: Foundational (Minikube Setup)

**Purpose**: Set up local Kubernetes cluster - MUST complete before US1

**⚠️ CRITICAL**: No Kubernetes deployment can begin until Minikube is running

- [x] T013 Verify Minikube is installed with `minikube version`
- [ ] T014 Start Minikube cluster with `minikube start --driver=docker --memory=4096 --cpus=2`
- [ ] T015 Enable Minikube ingress addon with `minikube addons enable ingress`
- [ ] T016 Enable Minikube metrics-server addon with `minikube addons enable metrics-server`
- [ ] T017 Verify cluster health with `kubectl cluster-info` and `kubectl get nodes`
- [ ] T018 Load Docker images into Minikube with `minikube image load`

**Checkpoint**: Minikube cluster running with addons, images loaded

---

## Phase 4: User Story 1 - Developer Deploys Chatbot to Local Kubernetes (Priority: P1) 🎯 MVP-2

**Goal**: Deploy application to Minikube using Helm charts

**Independent Test**: Run helm install and access chatbot through Ingress URL

### Implementation for User Story 1

- [ ] T019 [US1] Update Chart.yaml with correct metadata in phase-4-k8s/helm/todo-chatbot/Chart.yaml
- [ ] T020 [US1] Update values.yaml with complete configuration in phase-4-k8s/helm/todo-chatbot/values.yaml
- [ ] T021 [US1] Create values-minikube.yaml with secrets in phase-4-k8s/helm/todo-chatbot/values-minikube.yaml
- [ ] T022 [P] [US1] Update backend-deployment.yaml template in phase-4-k8s/helm/todo-chatbot/templates/backend-deployment.yaml
- [ ] T023 [P] [US1] Update backend-service.yaml template in phase-4-k8s/helm/todo-chatbot/templates/backend-service.yaml
- [ ] T024 [P] [US1] Update frontend-deployment.yaml template in phase-4-k8s/helm/todo-chatbot/templates/frontend-deployment.yaml
- [ ] T025 [P] [US1] Update frontend-service.yaml template in phase-4-k8s/helm/todo-chatbot/templates/frontend-service.yaml
- [ ] T026 [P] [US1] Update configmap.yaml template in phase-4-k8s/helm/todo-chatbot/templates/configmap.yaml
- [ ] T027 [P] [US1] Update secrets.yaml template in phase-4-k8s/helm/todo-chatbot/templates/secrets.yaml
- [ ] T028 [US1] Update ingress.yaml template in phase-4-k8s/helm/todo-chatbot/templates/ingress.yaml
- [ ] T029 [US1] Update _helpers.tpl with helper functions in phase-4-k8s/helm/todo-chatbot/templates/_helpers.tpl
- [ ] T030 [US1] Validate Helm chart with `helm lint phase-4-k8s/helm/todo-chatbot`
- [ ] T031 [US1] Deploy to Minikube with `helm install todo-chatbot ./helm/todo-chatbot`
- [ ] T032 [US1] Wait for pods to be ready with `kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=todo-chatbot`
- [ ] T033 [US1] Configure /etc/hosts with Minikube IP for todo.local
- [ ] T034 [US1] Verify chatbot UI loads at http://todo.local
- [ ] T035 [US1] Test chat functionality: send "Add task to buy groceries" and verify task creation

**Checkpoint**: Application deployed to Minikube, accessible via Ingress, all features working

---

## Phase 5: User Story 5 - Application Maintains Health in Kubernetes (Priority: P2)

**Goal**: Implement health checks for automatic pod recovery

**Independent Test**: Simulate failure and verify Kubernetes restarts pod automatically

### Implementation for User Story 5

- [ ] T036 [US5] Add /health endpoint to backend if not exists (verify in phase-3-chatbot/backend/src/main.py)
- [ ] T037 [US5] Update backend-deployment.yaml with liveness probe configuration
- [ ] T038 [US5] Update backend-deployment.yaml with readiness probe configuration
- [ ] T039 [US5] Update frontend-deployment.yaml with liveness probe configuration
- [ ] T040 [US5] Update frontend-deployment.yaml with readiness probe configuration
- [ ] T041 [US5] Redeploy with `helm upgrade todo-chatbot ./helm/todo-chatbot`
- [ ] T042 [US5] Verify probes are configured with `kubectl describe pod -l app=backend`
- [ ] T043 [US5] Test pod recovery by deleting pod: `kubectl delete pod -l app=backend`

**Checkpoint**: Health probes configured, pods auto-restart on failure

---

## Phase 6: User Story 4 - Developer Manages Application Lifecycle (Priority: P2)

**Goal**: Enable upgrade, rollback, and cleanup operations

**Independent Test**: Perform helm upgrade and rollback, run cleanup script

### Implementation for User Story 4

- [ ] T044 [US4] Update phase-4-k8s/scripts/deploy-minikube.sh with complete deployment logic
- [ ] T045 [US4] Update phase-4-k8s/scripts/cleanup.sh with proper resource removal
- [ ] T046 [US4] Test helm upgrade with modified values
- [ ] T047 [US4] Test helm rollback to previous revision
- [ ] T048 [US4] Test cleanup script removes all K8s resources
- [ ] T049 [US4] Document lifecycle commands in phase-4-k8s/CLAUDE.md

**Checkpoint**: Upgrade, rollback, and cleanup operations work correctly

---

## Phase 7: User Story 3 - Developer Uses AI DevOps Tools (Priority: P2)

**Goal**: Use and document AI-assisted DevOps tools

**Independent Test**: Invoke AI tool, capture output, document in CLAUDE.md

### Implementation for User Story 3

- [ ] T050 [US3] Install kubectl-ai via krew: `kubectl krew install ai`
- [ ] T051 [US3] Use kubectl-ai to check cluster status: `kubectl ai "what pods are running"`
- [ ] T052 [US3] Use kubectl-ai for diagnostics: `kubectl ai "check resource usage"`
- [ ] T053 [US3] Document kubectl-ai usage and outputs in phase-4-k8s/CLAUDE.md
- [ ] T054 [US3] (Optional) Try Docker AI Gordon if available: `docker ai "analyze my Dockerfile"`
- [ ] T055 [US3] Document all AI tool interactions with prompts and responses

**Checkpoint**: At least one AI DevOps tool used and documented

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final cleanup

- [ ] T056 [P] Update README.md with Phase IV deployment instructions
- [ ] T057 [P] Update phase-4-k8s/CLAUDE.md with complete session documentation
- [ ] T058 Run full deployment from scratch using quickstart.md steps
- [ ] T059 Verify all success criteria from spec.md are met
- [ ] T060 Create demo recording showing: image builds, Minikube deploy, app functionality, AI tool usage

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: User Story 2 (Containerization) ─── MUST complete first
    ↓
Phase 3: Foundational (Minikube Setup)
    ↓
Phase 4: User Story 1 (K8s Deployment) ─── Primary MVP
    ↓
Phase 5-7: User Stories 3, 4, 5 (can run in parallel after US1)
    ↓
Phase 8: Polish
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US2 (Containerization) | Setup | Phase 1 complete |
| US1 (K8s Deployment) | US2, Foundational | Phase 3 complete |
| US5 (Health Checks) | US1 | Phase 4 complete |
| US4 (Lifecycle) | US1 | Phase 4 complete |
| US3 (AI Tools) | US1 | Phase 4 complete |

### Parallel Opportunities

**Within Phase 2 (Containerization)**:
- T006 and T007 (backend/frontend Dockerfiles) can run in parallel

**Within Phase 4 (Deployment)**:
- T022, T023, T024, T025, T026, T027 (K8s templates) can run in parallel

**After Phase 4**:
- US3, US4, US5 can all run in parallel (different concerns)

---

## Parallel Example: Helm Templates

```bash
# Launch all template updates together:
Task: "Update backend-deployment.yaml template in phase-4-k8s/helm/todo-chatbot/templates/backend-deployment.yaml"
Task: "Update backend-service.yaml template in phase-4-k8s/helm/todo-chatbot/templates/backend-service.yaml"
Task: "Update frontend-deployment.yaml template in phase-4-k8s/helm/todo-chatbot/templates/frontend-deployment.yaml"
Task: "Update frontend-service.yaml template in phase-4-k8s/helm/todo-chatbot/templates/frontend-service.yaml"
Task: "Update configmap.yaml template in phase-4-k8s/helm/todo-chatbot/templates/configmap.yaml"
Task: "Update secrets.yaml template in phase-4-k8s/helm/todo-chatbot/templates/secrets.yaml"
```

---

## Implementation Strategy

### MVP First (User Stories 2 + 1)

1. Complete Phase 1: Setup ✓
2. Complete Phase 2: User Story 2 (Containerization) - Docker images working
3. Complete Phase 3: Foundational (Minikube Setup)
4. Complete Phase 4: User Story 1 (K8s Deployment)
5. **STOP and VALIDATE**: Application running on Kubernetes
6. Demo/document if ready

### Full Implementation

1. MVP (US2 + US1) → Core deployment working
2. Add US5 (Health Checks) → Production-ready resilience
3. Add US4 (Lifecycle) → Operational management
4. Add US3 (AI Tools) → Hackathon differentiator
5. Polish → Documentation and demo

### Success Criteria Mapping

| Success Criteria | Tasks |
|------------------|-------|
| SC-001: Build <5min | T010, T011 |
| SC-002: Image <500MB | T010, T011 |
| SC-003: Ready <3min | T032 |
| SC-004: Features work | T035 |
| SC-005: Pod recovery | T043 |
| SC-006: AI tool used | T050-T055 |
| SC-007: Lifecycle ops | T044-T048 |
| SC-008: Probe response | T042 |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US2 (Containerization) MUST complete before US1 (Deployment)
- Foundational (Minikube) MUST complete before US1
- US3, US4, US5 can proceed in parallel after US1
- Commit after each task or logical group
- Verify each checkpoint before proceeding
