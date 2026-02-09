# Helm Chart Patterns

## Table of Contents
- [Chart Structure](#chart-structure)
- [Chart.yaml](#chartyaml)
- [values.yaml (Defaults)](#valuesyaml-defaults)
- [values-minikube.yaml (Overrides)](#values-minikubeyaml-overrides)
- [Template Helpers (_helpers.tpl)](#template-helpers-_helperstpl)
- [Deployment Templates](#deployment-templates)
- [Service Templates](#service-templates)
- [ConfigMap Template](#configmap-template)
- [Secrets Template](#secrets-template)
- [Ingress Template](#ingress-template)

## Chart Structure

```
helm/<release-name>/
├── Chart.yaml
├── values.yaml              # Defaults (no secrets)
├── values-minikube.yaml     # Local overrides (gitignored secrets)
└── templates/
    ├── _helpers.tpl
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    └── ingress.yaml
```

## Chart.yaml

```yaml
apiVersion: v2
name: <release-name>
description: A Helm chart for <app-name>
type: application
version: 0.1.0
appVersion: "1.0.0"
keywords:
  - <keyword1>
  - <keyword2>
maintainers:
  - name: <team-name>
```

## values.yaml (Defaults)

Structure with backend/frontend sections, local image pull policy, resource limits, health probes, ingress, configmap, and secrets:

```yaml
global:
  imagePullPolicy: Never  # Local images via minikube image load

backend:
  replicaCount: 1
  image:
    repository: <backend-image>
    tag: latest
    pullPolicy: Never
  service:
    type: ClusterIP
    port: 8000
    targetPort: 8000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 256Mi
  env:
    DATABASE_URL: ""
    API_KEY: ""
    LOG_LEVEL: "INFO"
  probes:
    liveness:
      path: /health
      port: 8000
      initialDelaySeconds: 10
      periodSeconds: 10
    readiness:
      path: /health
      port: 8000
      initialDelaySeconds: 5
      periodSeconds: 5

frontend:
  replicaCount: 1
  image:
    repository: <frontend-image>
    tag: latest
    pullPolicy: Never
  service:
    type: ClusterIP
    port: 3000
    targetPort: 3000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 256Mi
  env:
    NEXT_PUBLIC_BACKEND_URL: ""
    BACKEND_URL: ""

ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
  hosts:
    - host: <app>.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /
          pathType: Prefix
          service: frontend

configMap:
  create: true
  data:
    LOG_LEVEL: "INFO"
    FRONTEND_URL: "http://<app>.local"

secrets:
  create: true
```

## values-minikube.yaml (Overrides)

Override image tags, set actual secrets, and adjust ingress for local:

```yaml
backend:
  image:
    tag: v1
    pullPolicy: Never
  env:
    DATABASE_URL: "<actual-connection-string>"
    API_KEY: "<actual-key>"
    LOG_LEVEL: "DEBUG"

frontend:
  image:
    tag: v1
    pullPolicy: Never
  env:
    NEXT_PUBLIC_BACKEND_URL: "http://<app>.local/api"
    BACKEND_URL: "http://<release-name>-backend:8000"

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: <app>.local
      paths:
        - path: /api
          pathType: Prefix
          service: backend
        - path: /health
          pathType: Exact
          service: backend
        - path: /
          pathType: Prefix
          service: frontend
```

## Template Helpers (_helpers.tpl)

```yaml
{{- define "<release>.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "<release>.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "<release>.labels" -}}
helm.sh/chart: {{ include "<release>.name" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "<release>.backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "<release>.name" . }}-backend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "<release>.frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "<release>.name" . }}-frontend
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

## Deployment Templates

Backend deployment pattern:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "<release>.fullname" . }}-backend
  labels:
    {{- include "<release>.labels" . | nindent 4 }}
    {{- include "<release>.backend.selectorLabels" . | nindent 4 }}
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "<release>.backend.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "<release>.backend.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: backend
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.backend.service.targetPort }}
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
          envFrom:
            - configMapRef:
                name: {{ include "<release>.fullname" . }}-config
            - secretRef:
                name: {{ include "<release>.fullname" . }}-secrets
```

Frontend follows the same pattern with frontend values and port 3000.

## Service Templates

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "<release>.fullname" . }}-backend
  labels:
    {{- include "<release>.labels" . | nindent 4 }}
spec:
  type: {{ .Values.backend.service.type }}
  ports:
    - port: {{ .Values.backend.service.port }}
      targetPort: {{ .Values.backend.service.targetPort }}
      protocol: TCP
      name: http
  selector:
    {{- include "<release>.backend.selectorLabels" . | nindent 4 }}
```

## ConfigMap Template

```yaml
{{- if .Values.configMap.create }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "<release>.fullname" . }}-config
  labels:
    {{- include "<release>.labels" . | nindent 4 }}
data:
  LOG_LEVEL: {{ .Values.configMap.data.LOG_LEVEL | default "INFO" | quote }}
  FRONTEND_URL: {{ .Values.configMap.data.FRONTEND_URL | quote }}
  NEXT_PUBLIC_BACKEND_URL: {{ .Values.frontend.env.NEXT_PUBLIC_BACKEND_URL | quote }}
  BACKEND_URL: {{ .Values.frontend.env.BACKEND_URL | quote }}
{{- end }}
```

## Secrets Template

```yaml
{{- if .Values.secrets.create }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ include "<release>.fullname" . }}-secrets
  labels:
    {{- include "<release>.labels" . | nindent 4 }}
type: Opaque
stringData:
  DATABASE_URL: {{ .Values.backend.env.DATABASE_URL | quote }}
  API_KEY: {{ .Values.backend.env.API_KEY | quote }}
{{- end }}
```

Use `stringData` (not `data`) to avoid manual base64 encoding. Helm handles it.

## Ingress Template

```yaml
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "<release>.fullname" . }}
  labels:
    {{- include "<release>.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  ingressClassName: {{ .Values.ingress.className }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                {{- if eq .service "backend" }}
                name: {{ include "<release>.fullname" $ }}-backend
                port:
                  number: {{ $.Values.backend.service.port }}
                {{- else }}
                name: {{ include "<release>.fullname" $ }}-frontend
                port:
                  number: {{ $.Values.frontend.service.port }}
                {{- end }}
          {{- end }}
    {{- end }}
{{- end }}
```
