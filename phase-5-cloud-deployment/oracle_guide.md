# Complete OKE Deployment Guide for Beginners

This guide walks you through deploying the Todo Chatbot application to Oracle Kubernetes Engine (OKE) step by step. No prior cloud experience required.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Oracle Cloud Account Setup](#2-oracle-cloud-account-setup)
3. [Access OCI Cloud Shell](#3-access-oci-cloud-shell)
4. [Create OKE Cluster](#4-create-oke-cluster)
5. [Configure kubectl](#5-configure-kubectl)
6. [Install Ingress Controller](#6-install-ingress-controller)
7. [Create Kubernetes Secrets](#7-create-kubernetes-secrets)
8. [Deploy the Application](#8-deploy-the-application)
9. [Access Your Application](#9-access-your-application)
10. [Verify Everything Works](#10-verify-everything-works)
11. [Cleanup (Important!)](#11-cleanup-important)
12. [Troubleshooting](#12-troubleshooting)
13. [Cost Management](#13-cost-management)

---

## 1. Prerequisites

Before starting, ensure you have:

- [ ] Oracle Cloud account (free tier available at [cloud.oracle.com](https://cloud.oracle.com))
- [ ] Docker Hub account with these images pushed:
  - `ashfaq1192/todo-backend:v2`
  - `ashfaq1192/todo-frontend:v3`
  - `ashfaq1192/todo-audit:v2` (optional)
  - `ashfaq1192/todo-notification:v2` (optional)
  - `ashfaq1192/todo-recurring:v2` (optional)
- [ ] Your environment variables ready:
  - `DATABASE_URL` - Your Neon PostgreSQL connection string
  - `GEMINI_API_KEY` - Your Google Gemini API key
  - `BETTER_AUTH_SECRET` - Your auth secret
  - `JWT_SECRET_KEY` - Your JWT secret

---

## 2. Oracle Cloud Account Setup

### Step 2.1: Create Oracle Cloud Account

1. Go to [cloud.oracle.com](https://cloud.oracle.com)
2. Click "Sign Up" for a free account
3. Complete the registration (credit card required for verification, but free tier has no charges)
4. Wait for account activation email (usually within 15-30 minutes)

### Step 2.2: Sign In to Console

1. Go to [cloud.oracle.com](https://cloud.oracle.com)
2. Click "Sign In"
3. Enter your Cloud Account Name (tenancy)
4. Sign in with your credentials

---

## 3. Access OCI Cloud Shell

Cloud Shell is a free, browser-based terminal that comes pre-installed with all the tools you need.

### Step 3.1: Open Cloud Shell

1. In the OCI Console, look at the top-right corner
2. Click the **Cloud Shell** icon (looks like a terminal `>_`)
3. Wait for the shell to initialize (takes about 30 seconds)

### Step 3.2: Verify Tools

```bash
# Check kubectl is installed
kubectl version --client

# Check helm is installed
helm version

# Check OCI CLI is installed
oci --version
```

You should see version numbers for all three tools.

---

## 4. Create OKE Cluster

> **IMPORTANT**: You MUST create an **Enhanced Cluster**, not a Basic Cluster. Basic Cluster API is non-functional.

### Step 4.1: Navigate to Kubernetes

1. Click the hamburger menu (☰) in the top-left
2. Navigate to: **Developer Services** → **Kubernetes Clusters (OKE)**

### Step 4.2: Create Cluster

1. Click **Create Cluster**
2. Select **Quick Create** (easiest option)
3. Configure the cluster:

   | Setting | Value |
   |---------|-------|
   | Name | `todo-cluster` |
   | Compartment | Your root compartment (default) |
   | Kubernetes Version | Latest stable (e.g., v1.28.x) |
   | **Cluster Type** | **Enhanced** (REQUIRED!) |
   | Visibility Type | Public endpoint |
   | Shape | VM.Standard.E4.Flex |
   | OCPUs per Node | 1 |
   | Memory per Node | 8 GB |
   | Number of Nodes | 2 |

4. Click **Next** to review
5. Click **Create Cluster**

### Step 4.3: Wait for Cluster Creation

- This takes approximately **15-20 minutes**
- Status will change from "Creating" to "Active"
- You can monitor progress on the cluster details page

---

## 5. Configure kubectl

Once your cluster is "Active", configure kubectl to connect to it.

### Step 5.1: Get Cluster Access

1. On the cluster details page, click **Access Cluster**
2. Select **Cloud Shell Access**
3. Copy the provided command (looks like):

   ```bash
   oci ce cluster create-kubeconfig --cluster-id ocid1.cluster.oc1... --file $HOME/.kube/config --region us-ashburn-1 --token-version 2.0.0 --kube-endpoint PUBLIC_ENDPOINT
   ```

4. Paste and run this command in Cloud Shell

### Step 5.2: Verify Connection

```bash
# Check cluster connection
kubectl cluster-info

# Check nodes are ready
kubectl get nodes
```

Expected output:
```
NAME          STATUS   ROLES   AGE   VERSION
10.0.10.123   Ready    node    5m    v1.28.2
10.0.10.124   Ready    node    5m    v1.28.2
```

---

## 6. Install Ingress Controller

The Ingress Controller routes external traffic to your services.

### Step 6.1: Add NGINX Ingress Repository

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
```

### Step 6.2: Install NGINX Ingress Controller

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

### Step 6.3: Wait for External IP

```bash
# Wait for LoadBalancer to get an external IP (takes 2-3 minutes)
kubectl get svc -n ingress-nginx -w
```

Wait until `EXTERNAL-IP` changes from `<pending>` to an IP address:
```
NAME                       TYPE           EXTERNAL-IP      PORT(S)
ingress-nginx-controller   LoadBalancer   129.146.xxx.xxx  80:30080/TCP,443:30443/TCP
```

**Save this IP address** - you'll need it to access your application!

---

## 7. Create Kubernetes Secrets

Secrets store sensitive configuration like database credentials.

### Step 7.1: Create Secrets

Replace the placeholder values with your actual credentials:

```bash
# Backend secrets
kubectl create secret generic todo-backend-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@host/dbname?sslmode=require" \
  --from-literal=GEMINI_API_KEY="your-gemini-api-key" \
  --from-literal=BETTER_AUTH_SECRET="your-auth-secret" \
  --from-literal=JWT_SECRET_KEY="your-jwt-secret"

# Frontend secrets
kubectl create secret generic todo-frontend-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@host/dbname?sslmode=require" \
  --from-literal=BETTER_AUTH_SECRET="your-auth-secret"
```

### Step 7.2: Verify Secrets

```bash
kubectl get secrets
```

You should see:
```
NAME                     TYPE     DATA   AGE
todo-backend-secrets     Opaque   4      10s
todo-frontend-secrets    Opaque   2      5s
```

---

## 8. Deploy the Application

### Step 8.1: Create Deployment Files

Create a file called `todo-deployment.yaml`:

```bash
cat << 'EOF' > todo-deployment.yaml
# Backend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
  labels:
    app: todo-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-backend
  template:
    metadata:
      labels:
        app: todo-backend
    spec:
      containers:
      - name: backend
        image: ashfaq1192/todo-backend:v2
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: DATABASE_URL
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: GEMINI_API_KEY
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: BETTER_AUTH_SECRET
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: todo-backend-secrets
              key: JWT_SECRET_KEY
        - name: LOG_LEVEL
          value: "INFO"
        - name: FRONTEND_URL
          value: "http://YOUR_EXTERNAL_IP"
        resources:
          limits:
            cpu: "1"
            memory: 1Gi
          requests:
            cpu: 250m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
# Backend Service
apiVersion: v1
kind: Service
metadata:
  name: todo-backend
spec:
  selector:
    app: todo-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
# Frontend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-frontend
  labels:
    app: todo-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: todo-frontend
  template:
    metadata:
      labels:
        app: todo-frontend
    spec:
      containers:
      - name: frontend
        image: ashfaq1192/todo-frontend:v3
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_BACKEND_URL
          value: "http://YOUR_EXTERNAL_IP/api"
        - name: NEXT_PUBLIC_BETTER_AUTH_URL
          value: "http://YOUR_EXTERNAL_IP"
        - name: BACKEND_URL
          value: "http://todo-backend:8000"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: todo-frontend-secrets
              key: DATABASE_URL
        - name: BETTER_AUTH_SECRET
          valueFrom:
            secretKeyRef:
              name: todo-frontend-secrets
              key: BETTER_AUTH_SECRET
        resources:
          limits:
            cpu: 500m
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 256Mi
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
---
# Frontend Service
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend
spec:
  selector:
    app: todo-frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
---
# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
spec:
  ingressClassName: nginx
  rules:
  - http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: todo-backend
            port:
              number: 8000
      - path: /health
        pathType: Exact
        backend:
          service:
            name: todo-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: todo-frontend
            port:
              number: 3000
EOF
```

### Step 8.2: Update External IP

Replace `YOUR_EXTERNAL_IP` with your actual Ingress external IP:

```bash
# Get your external IP
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "External IP: $EXTERNAL_IP"

# Update the deployment file
sed -i "s/YOUR_EXTERNAL_IP/$EXTERNAL_IP/g" todo-deployment.yaml
```

### Step 8.3: Apply Deployment

```bash
kubectl apply -f todo-deployment.yaml
```

### Step 8.4: Wait for Pods to Start

```bash
# Watch pods starting up
kubectl get pods -w

# Wait until all pods show "Running" and "1/1" ready
```

Expected output:
```
NAME                            READY   STATUS    RESTARTS   AGE
todo-backend-xxx-yyy            1/1     Running   0          2m
todo-backend-xxx-zzz            1/1     Running   0          2m
todo-frontend-xxx-aaa           1/1     Running   0          2m
todo-frontend-xxx-bbb           1/1     Running   0          2m
```

---

## 9. Access Your Application

### Step 9.1: Get Application URL

```bash
# Get the external IP
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Your app is at: http://<EXTERNAL-IP>
```

### Step 9.2: Open in Browser

Open your browser and navigate to:
```
http://<YOUR-EXTERNAL-IP>
```

You should see the Todo Chatbot login page!

---

## 10. Verify Everything Works

### Step 10.1: Test Health Endpoints

```bash
EXTERNAL_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test backend health
curl http://$EXTERNAL_IP/health
# Expected: {"status":"healthy","service":"Todo API","version":"0.2.0"}

# Test frontend
curl -I http://$EXTERNAL_IP
# Expected: HTTP/1.1 200 OK
```

### Step 10.2: Test Application Flow

1. Open `http://<EXTERNAL-IP>` in browser
2. Create a new account (Sign Up)
3. Log in with your credentials
4. Create a new task
5. Open the chatbot and try: "list my tasks"
6. Verify the chatbot responds with your tasks

### Step 10.3: Check Pod Logs (if issues)

```bash
# Backend logs
kubectl logs -f deployment/todo-backend

# Frontend logs
kubectl logs -f deployment/todo-frontend
```

---

## 11. Cleanup (Important!)

> **WARNING**: OKE Enhanced Cluster costs approximately **$3 per day**. Delete resources when done to avoid charges!

### Step 11.1: Delete Application

```bash
# Delete deployments and services
kubectl delete -f todo-deployment.yaml

# Delete secrets
kubectl delete secret todo-backend-secrets todo-frontend-secrets

# Delete ingress controller
helm uninstall ingress-nginx -n ingress-nginx
kubectl delete namespace ingress-nginx
```

### Step 11.2: Delete OKE Cluster

1. Go to OCI Console
2. Navigate to: **Developer Services** → **Kubernetes Clusters (OKE)**
3. Click on your cluster (`todo-cluster`)
4. Click **Delete Cluster**
5. Confirm deletion

### Step 11.3: Verify No Resources Remain

1. Go to: **Compute** → **Instances** - should be empty
2. Go to: **Networking** → **Load Balancers** - should be empty
3. Go to: **Block Storage** → **Block Volumes** - should be empty

---

## 12. Troubleshooting

### Problem: Pods are in "Pending" state

**Check node resources:**
```bash
kubectl describe nodes
kubectl get events --sort-by=.metadata.creationTimestamp
```

**Solution**: Nodes might not have enough resources. Check the cluster node count.

### Problem: Pods are in "ImagePullBackOff"

**Check image name:**
```bash
kubectl describe pod <pod-name>
```

**Solution**: Verify the Docker Hub images exist and are public.

### Problem: Application returns 502 Bad Gateway

**Check pod health:**
```bash
kubectl get pods
kubectl logs deployment/todo-backend
```

**Solution**: Backend might be crashing. Check logs for errors.

### Problem: Can't connect to database

**Check connection string:**
```bash
kubectl exec deployment/todo-backend -- env | grep DATABASE
```

**Solution**: Verify DATABASE_URL is correct and Neon allows connections from any IP.

### Problem: CORS errors in browser

**Check FRONTEND_URL env:**
```bash
kubectl exec deployment/todo-backend -- env | grep FRONTEND
```

**Solution**: FRONTEND_URL must match the URL you're accessing the app from.

### Problem: Ingress not getting external IP

**Check ingress controller:**
```bash
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

**Solution**: Wait longer or check OCI service limits.

---

## 13. Cost Management

### OKE Costs Breakdown

| Resource | Approximate Cost |
|----------|------------------|
| OKE Control Plane (Enhanced) | ~$2.40/day |
| Worker Nodes (2x VM.Standard.E4.Flex) | ~$0.50/day |
| Load Balancer | ~$0.10/day |
| **Total** | **~$3.00/day** |

### Cost-Saving Tips

1. **Delete when not in use** - Don't leave the cluster running overnight
2. **Use Free Tier resources** - Oracle provides some free tier resources
3. **Reduce node count** - Use 1 node instead of 2 for testing
4. **Demo and delete** - Deploy, record demo video, then immediately delete

### Free Tier Limits

Oracle Cloud Free Tier includes:
- 2 AMD-based VMs (1 OCPU, 1GB each) - Always Free
- 4 ARM-based VMs (24GB total) - Always Free
- 200GB Block Storage - Always Free
- 10TB Outbound Data Transfer - Always Free

**Note**: OKE Enhanced Cluster is NOT part of free tier and will incur charges.

---

## Quick Reference Commands

```bash
# View all resources
kubectl get all

# View pods with more details
kubectl get pods -o wide

# View logs
kubectl logs -f deployment/todo-backend
kubectl logs -f deployment/todo-frontend

# Describe a resource
kubectl describe pod <pod-name>
kubectl describe ingress todo-ingress

# Execute into a pod
kubectl exec -it deployment/todo-backend -- /bin/bash

# Scale deployment
kubectl scale deployment todo-backend --replicas=3

# Restart deployment
kubectl rollout restart deployment/todo-backend

# View events
kubectl get events --sort-by=.metadata.creationTimestamp

# Get external IP
kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

---

## Summary

You have successfully learned how to:

1. ✅ Create an Oracle Cloud account
2. ✅ Use OCI Cloud Shell
3. ✅ Create an OKE Enhanced Cluster
4. ✅ Configure kubectl access
5. ✅ Install NGINX Ingress Controller
6. ✅ Create Kubernetes Secrets
7. ✅ Deploy the Todo Chatbot application
8. ✅ Access and test your application
9. ✅ Clean up resources to avoid charges

**Remember**: Always delete your cluster when done to avoid unnecessary costs!

---

## Need Help?

- **OCI Documentation**: https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Project Repository**: https://github.com/ashfaq1192/hackathon-todo-fullstack
