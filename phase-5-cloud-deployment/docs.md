# Phase V: Cloud Deployment Guide

A step-by-step learning guide for deploying the Todo app to Oracle Cloud (OKE).
Each step explains **what** we're using, **why** we need it, and **how** it fits into the overall deployment.

---

## Table of Contents

1. [Build & Push Docker Images](#step-1-build--push-docker-images)
2. [Create OKE Enhanced Cluster](#step-2-create-oke-enhanced-cluster)
3. [Install Dapr on OKE](#step-3-install-dapr-on-oke)
4. [Deploy Redpanda/Kafka](#step-4-deploy-redpandakafka)
5. [Apply Dapr Components](#step-5-apply-dapr-components)
6. [Deploy via Helm](#step-6-deploy-via-helm)
7. [Configure Ingress/DNS](#step-7-configure-ingressdns)
8. [CI/CD Pipeline](#step-8-cicd-pipeline)
9. [Observability](#step-9-observability)
10. [Verify & Demo](#step-10-verify--demo)

---

## Step 1: Build & Push Docker Images

### What are Docker Images?

Think of a Docker image as a **portable box** that contains your application code, all its dependencies (libraries, runtime, OS packages), and instructions on how to run it. Instead of saying "install Python 3.12, then install FastAPI, then copy my code...", you package everything into one image that runs identically everywhere — your laptop, a test server, or the cloud.

### Why do we need them?

Kubernetes (which runs on OKE) doesn't run raw code. It runs **containers** — live instances of Docker images. So before we can deploy anything to the cloud, we must package each piece of our app into an image.

### What images are we building?

| # | Image Name | Source Code | Purpose |
|---|-----------|-------------|---------|
| 1 | `todo-backend` | `phase-3-chatbot/backend/` | The FastAPI server that handles all API requests, database operations, and chatbot logic |
| 2 | `todo-frontend` | `phase-3-chatbot/frontend/` | The Next.js web app that users see and interact with in their browser |
| 3 | `todo-notification` | `phase-5-cloud-deployment/services/notification-service/` | Listens to Kafka `reminders` topic and sends due date reminders to users |
| 4 | `todo-recurring` | `phase-5-cloud-deployment/services/recurring-task-service/` | Listens to Kafka `task-events` topic; when a recurring task is completed, auto-creates the next occurrence |
| 5 | `todo-audit` | `phase-5-cloud-deployment/services/audit-service/` | Listens to Kafka `task-events` topic and logs all task operations as an audit trail |

### Where do we push them?

To **OCIR (Oracle Container Image Registry)** — Oracle's private image storage. It's like a private Google Drive but for Docker images. OKE pulls images from OCIR when deploying containers.

### How it fits together

```
[Your Code] --docker build--> [Docker Image] --docker push--> [OCIR Registry] --kubectl deploy--> [Running on OKE]
```

---

## Step 2: Create OKE Enhanced Cluster

*(Will be filled before executing this step)*

---

## Step 3: Install Dapr on OKE

*(Will be filled before executing this step)*

---

## Step 4: Deploy Redpanda/Kafka

*(Will be filled before executing this step)*

---

## Step 5: Apply Dapr Components

*(Will be filled before executing this step)*

---

## Step 6: Deploy via Helm

*(Will be filled before executing this step)*

---

## Step 7: Configure Ingress/DNS

*(Will be filled before executing this step)*

---

## Step 8: CI/CD Pipeline

*(Will be filled before executing this step)*

---

## Step 9: Observability

*(Will be filled before executing this step)*

---

## Step 10: Verify & Demo

*(Will be filled before executing this step)*

---

*This document is updated as each step is implemented during the deployment session.*
