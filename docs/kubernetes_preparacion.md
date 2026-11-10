# Kubernetes Preparation — POOLAR

> Updated: 2026-11-10. Status: **documented; not deployed**. Docker Compose is the primary development environment.

## Objective

Prepare the architecture so POOLAR can be deployed on Kubernetes in the future without rewriting the core.

## Workload separation (future)

- POOLAR API (Deployment)
- Async task workers (future Deployment)
- Agent Harness execution (future Deployment)
- Ingestion processes (Job/CronJob)
- Auxiliary evaluation services (Job)

## Current preparation

- Dockerfile with non-root user and healthcheck.
- `docker-compose.yml` with PostgreSQL, migrate, api services.
- Configuration via environment variables; secrets outside the repository.
- Configurable structured logging.
- `/health` endpoint for checks (correlation/envelope fields added additively).

## Health checks

- **Liveness:** process is alive (`/health`).
- **Readiness:** service can handle requests (including DB connectivity, when implemented/validated).
- **Dependencies:** PostgreSQL connection/availability.

## Reference manifests (future, not deployed)

```yaml
# API Deployment (reference)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: poolar-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: poolar-api
  template:
    metadata:
      labels:
        app: poolar-api
    spec:
      containers:
      - name: poolar-api
        image: poolar:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: poolar-secrets
              key: database-url
        - name: POOLAR_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: poolar-secrets
              key: secret-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

## When to introduce Kubernetes

- Real load/scale needs, independent workers, HA requirements, multiple environments/frequent deploys, or operational needs beyond Docker Compose — and team capacity to operate the cluster.

## Not included (for now)

- Helm/operators/service mesh/HPA, real cloud deployment, microservices split, Redis/Celery/Kafka/Temporal.