# Preparación para Kubernetes — Poolar

## Estado
Documentado; no desplegado. Docker Compose es el entorno principal de desarrollo.

## Objetivo
Preparar la arquitectura para que Poolar pueda desplegarse en Kubernetes en el futuro sin reescribir el núcleo.

## Separación de cargas (futuro)
- API de Poolar (Deployment).
- Workers de tareas asíncronas (Deployment futuro).
- Ejecución del Agent Harness (Deployment futuro).
- Procesos de ingestión (Job/CronJob).
- Servicios auxiliares de evaluación (Job).

## Preparación actual
- Dockerfile con usuario no-root y healthcheck.
- docker-compose.yml con PostgreSQL, migrate, api.
- Configuración por variables de entorno.
- Secretos fuera del repositorio.
- Logs estructurados (configurables).
- Endpoint `/health` para verificación.

## Health checks
- **Liveness**: el proceso está vivo (`/health`).
- **Readiness**: el servicio puede atender solicitudes (conexión a PostgreSQL).
- **Dependencias**: conexión y disponibilidad de PostgreSQL.

## Manifiestos de referencia (futuros, no desplegados)
```yaml
# API Deployment (referencia)
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
              name: trama-secrets
              key: database-url
        - name: POOLAR_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: trama-secrets
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
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

## Cuándo introducir Kubernetes
- Aumento real de carga.
- Workers independientes que necesitan escalar.
- Necesidad de alta disponibilidad.
- Varios entornos y despliegues frecuentes.
- Requisitos operativos que Docker Compose ya no puede cubrir.
- Capacidad del equipo para mantener el clúster.

## No incluido (por ahora)
- Helm, operadores, service mesh, HPA.
- Despliegue real en proveedor cloud.
- Microservicios.
- Redis, Celery, Kafka, Temporal.