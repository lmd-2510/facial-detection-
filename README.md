<div align="center">

# DeepFace Access Control

**MVP kiem soat ra vao bang nhan dien khuon mat, gom frontend, backend API, worker AI va day du ha tang demo local.**

<p>
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-Vite-61DAFB?style=for-the-badge&logo=react&logoColor=111111">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

<p>
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white">
  <img alt="Redis" src="https://img.shields.io/badge/Redis-Queue-DC382D?style=flat-square&logo=redis&logoColor=white">
  <img alt="MinIO" src="https://img.shields.io/badge/MinIO-Object_Storage-C72E49?style=flat-square&logo=minio&logoColor=white">
  <img alt="Qdrant" src="https://img.shields.io/badge/Qdrant-Vector_DB-DC244C?style=flat-square">
  <img alt="Prometheus" src="https://img.shields.io/badge/Prometheus-Metrics-E6522C?style=flat-square&logo=prometheus&logoColor=white">
  <img alt="Grafana" src="https://img.shields.io/badge/Grafana-Dashboard-F46800?style=flat-square&logo=grafana&logoColor=white">
</p>

<p>
  <a href="#preview">Preview</a> |
  <a href="#quick-start">Quick Start</a> |
  <a href="#architecture">Architecture</a> |
  <a href="#services">Services</a> |
  <a href="#testing">Testing</a> |
  <a href="#production-notes">Production Notes</a>
</p>

</div>

---

## Overview

DeepFace Access Control la he thong demo kiem soat ra vao bang khuon mat. Project duoc thiet ke theo kien truc multi-service de co the demo end-to-end: giao dien user/admin, API, queue, worker AI, database, object storage, vector search va monitoring.

<table>
  <tr>
    <td><strong>Frontend</strong></td>
    <td>Home page, User access terminal, Admin console</td>
  </tr>
  <tr>
    <td><strong>Backend</strong></td>
    <td>FastAPI, auth, employee/camera/log APIs, upload image, push jobs to Redis</td>
  </tr>
  <tr>
    <td><strong>AI Worker</strong></td>
    <td>DeepFace detection, optional anti-spoofing, embedding, Qdrant search, access decision update</td>
  </tr>
  <tr>
    <td><strong>Infrastructure</strong></td>
    <td>PostgreSQL, Redis, MinIO, Qdrant, Nginx, Prometheus, Alertmanager, Grafana</td>
  </tr>
  <tr>
    <td><strong>Delivery</strong></td>
    <td>Docker Compose local stack, GitHub Actions, Docker image publishing, Helm chart baseline</td>
  </tr>
</table>

Verified locally: Docker Compose build/start passed, frontend/backend services are healthy, and the UI screenshots below were captured from the running stack.

## Preview

<div align="center">

### Home

<img src="docs/screenshots/home.png" alt="DeepFace home screen" width="860">

<br><br>

<table>
  <tr>
    <th>User access terminal</th>
    <th>Admin dashboard</th>
  </tr>
  <tr>
    <td><img src="docs/screenshots/user-access.png" alt="User access terminal" width="430"></td>
    <td><img src="docs/screenshots/admin-dashboard.png" alt="Admin dashboard" width="430"></td>
  </tr>
</table>

</div>

Screenshots were captured on a machine using port overrides because another local stack was occupying the default ports. The checked UI still uses the same Docker Compose services and application flow.

## Architecture

```text
Frontend Home / User / Admin
          |
          v
      Nginx Gateway
          |
          v
      Backend API
          |
          +--> PostgreSQL        users, employees, cameras, logs, embeddings
          +--> MinIO             enrollment images and access snapshots
          +--> Redis             embedding_jobs and access_jobs
                    |
                    v
                AI Worker
                    |
                    +--> DeepFace detection / embedding / liveness
                    +--> Qdrant vector search
                    +--> PostgreSQL access log update
```

### Main Flow

1. Admin creates an employee.
2. Admin uploads employee face images.
3. Backend stores images in MinIO and queues `embedding_jobs`.
4. Worker creates face embeddings and indexes them in Qdrant.
5. User uploads or captures an access snapshot.
6. Backend stores the snapshot and queues `access_jobs`.
7. Worker matches the snapshot against Qdrant embeddings.
8. Access log becomes `granted`, `denied`, `processing`, or `error`.

## Quick Start

Requirements:

- Docker Desktop is running.
- Docker Compose plugin is available through `docker compose`.
- First worker build/start can take longer because DeepFace/TensorFlow and model weights are heavy.

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```

Check the stack:

```powershell
docker compose ps
.\scripts\demo-baseline-check.ps1
```

Stop the stack:

```powershell
docker compose down
```

## Default URLs

| Component | Default URL | Purpose |
| --- | --- | --- |
| Home gateway | `http://localhost:8080` | Role selection |
| User UI | `http://localhost:8080/user/` | Access terminal |
| Admin UI | `http://localhost:8080/admin/` | Management console |
| Backend health | `http://localhost:8000/health` | API health |
| Backend docs | `http://localhost:8000/docs` | Swagger UI |
| MinIO console | `http://localhost:9001` | Object storage |
| Prometheus | `http://localhost:9090` | Metrics |
| Alertmanager | `http://localhost:9093` | Alert routing |
| Grafana | `http://localhost:3000` | Dashboard |
| Qdrant HTTP | `http://localhost:6333` | Vector database |

If default ports are already occupied, override host ports in `.env` before starting the stack:

```env
POSTGRES_PORT=15432
REDIS_PORT=16379
BACKEND_PORT=18001
FRONTEND_HOME_PORT=15172
FRONTEND_USER_PORT=15173
FRONTEND_ADMIN_PORT=15174
NGINX_PORT=18081
MINIO_API_PORT=19000
MINIO_CONSOLE_PORT=19001
QDRANT_HTTP_PORT=16333
QDRANT_GRPC_PORT=16334
PROMETHEUS_PORT=19090
ALERTMANAGER_PORT=19093
GRAFANA_PORT=13000
VITE_API_BASE_URL=http://localhost:18001
```

When `VITE_API_BASE_URL` changes, rebuild the frontend images:

```powershell
docker compose up --build -d frontend-user frontend-admin nginx
```

If user/admin/gateway ports are changed, add those origins to `BACKEND_CORS_ORIGINS`.

## Demo Accounts

| Role | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| User | `user` | `user123` |
| Grafana | `admin` | Value of `GRAFANA_ADMIN_PASSWORD` |
| MinIO | Value of `MINIO_ROOT_USER` | Value of `MINIO_ROOT_PASSWORD` |

Demo accounts are created by the `db-seed` service. Override them through `SEED_ADMIN_USERNAME`, `SEED_ADMIN_PASSWORD`, `SEED_USER_USERNAME`, and `SEED_USER_PASSWORD`.

## Services

| Service | Role | Default host port | Override variable |
| --- | --- | --- | --- |
| `database` | PostgreSQL source of truth | `5432` | `POSTGRES_PORT` |
| `redis` | Job queue | `6379` | `REDIS_PORT` |
| `db-seed` | Create tables and seed demo data | none | none |
| `backend` | FastAPI server | `8000` | `BACKEND_PORT` |
| `worker` | AI job processor | none | none |
| `frontend-home` | Home page | `5172` | `FRONTEND_HOME_PORT` |
| `frontend-user` | User terminal | `5173` | `FRONTEND_USER_PORT` |
| `frontend-admin` | Admin console | `5174` | `FRONTEND_ADMIN_PORT` |
| `nginx` | Gateway | `8080` | `NGINX_PORT` |
| `minio` | S3-compatible object storage | `9000`, `9001` | `MINIO_API_PORT`, `MINIO_CONSOLE_PORT` |
| `qdrant` | Vector database | `6333`, `6334` | `QDRANT_HTTP_PORT`, `QDRANT_GRPC_PORT` |
| `prometheus` | Metrics scrape | `9090` | `PROMETHEUS_PORT` |
| `alertmanager` | Local alert routing | `9093` | `ALERTMANAGER_PORT` |
| `grafana` | Metrics dashboard | `3000` | `GRAFANA_PORT` |

## Repository Layout

```text
.
|-- backend/                 FastAPI API, models, schemas, repositories, tests
|-- worker/                  DeepFace pipeline, job handlers, vector search, tests
|-- frontend/
|   |-- home/                Static home page
|   |-- user/                React user terminal
|   `-- admin/               React admin console
|-- nginx/                   Gateway config
|-- monitoring/              Prometheus, Alertmanager, Grafana provisioning
|-- helm/deepface-access/    Kubernetes chart baseline
|-- docs/                    Architecture, API, deployment and operations notes
|-- docs/screenshots/        README preview screenshots
|-- scripts/                 Test, seed, smoke, backup and readiness scripts
|-- data/smoke/              Small smoke-test image set
`-- docker-compose.yml       Local multi-service runtime
```

## Testing

Run the full project test script:

```powershell
.\scripts\test.ps1
```

It runs:

| Area | Command |
| --- | --- |
| Backend API tests | `python -m pytest backend\app\tests` |
| Worker tests | `python -m pytest worker\app\tests` |
| Admin frontend build | `npm run build` |
| User frontend build | `npm run build` |

Runtime baseline check:

```powershell
.\scripts\demo-baseline-check.ps1
```

Static-only baseline:

```powershell
.\scripts\demo-baseline-check.ps1 -StaticOnly
```

DeepFace runtime smoke test:

```powershell
.\scripts\smoke-deepface.ps1
```

The DeepFace smoke test uses PostgreSQL, Qdrant, and the worker container to create real embeddings and validate matching. The first run can be slower because model weights are cached into the `deepface_weights` Docker volume.

## API Surface

| Group | Representative endpoints | Purpose |
| --- | --- | --- |
| Auth | `POST /auth/login`, `GET /auth/me` | Login and current user |
| Admin users | `GET/POST/PUT/DELETE /admin/users` | Account management |
| Employees | `GET/POST/PUT/DELETE /employees` | Employee management |
| Employee images | `POST /employees/{id}/face-image` | Upload enrollment image and queue embedding job |
| Cameras | `GET/POST/PUT/DELETE /cameras` | Camera management |
| Access | `POST /access/check`, `POST /access/check-image` | Queue access checks |
| Logs | `GET /logs` | Access history |
| Operations | `GET /health`, `GET /metrics`, `GET /admin/status` | Runtime status and metrics |

More detail is documented in `docs/api.md`.

## Key Configuration

| Variable | Meaning |
| --- | --- |
| `DATABASE_URL` | PostgreSQL connection string for backend and worker |
| `REDIS_URL` | Redis queue URL |
| `AUTH_SECRET_KEY` | JWT signing secret |
| `BACKEND_CORS_ORIGINS` | Allowed frontend origins |
| `VITE_API_BASE_URL` | Backend URL baked into frontend assets |
| `MINIO_ENDPOINT` | Internal MinIO endpoint in Docker network |
| `MINIO_BUCKET` | Image bucket |
| `QDRANT_URL` | Internal Qdrant URL |
| `QDRANT_COLLECTION` | Vector embedding collection |
| `DEEPFACE_MODEL_NAME` | Embedding model, default `Facenet512` |
| `DEEPFACE_MATCH_THRESHOLD` | Matching threshold |
| `DEEPFACE_ANTI_SPOOFING` | Enable or disable anti-spoofing |
| `MAX_PROCESSING_ACCESS_LOGS_PER_CAMERA` | Queue pressure limit per camera |

## Production Notes

The defaults are for local demos. Before real deployment:

- Replace `AUTH_SECRET_KEY`, PostgreSQL password, MinIO credentials, Grafana password and seed passwords.
- Do not use `admin123`, `user123`, or `minioadmin` outside demo.
- Restrict `BACKEND_CORS_ORIGINS` to real frontend domains.
- Prefer immutable image tags such as commit SHA instead of `latest`.
- Put HTTPS/TLS at the public ingress or reverse proxy.
- Add upload file size limits and real image content validation, not only extension checks.
- Review `GET /logs` permission. It is fine for demo/operator usage, but too broad if `user` means an individual employee.
- Move schema changes to Alembic once the database model is stable.

## CI/CD And Deployment

GitHub Actions currently:

- Runs backend tests on Python 3.12.
- Runs worker tests on Python 3.12.
- Builds user/admin frontends on Node 22.
- Builds Docker images for backend, worker, frontend-home, frontend-user and frontend-admin.
- Publishes Docker Hub images on `main` when `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets are configured.

The Kubernetes baseline lives in `helm/deepface-access`. For a real cluster, create Kubernetes Secrets for database/auth/minio and configure the image registry and tag explicitly.

## Backup

```powershell
.\scripts\backup.ps1
```

Backup output is written under `backup/`. Generated backup files are ignored by Git, while `.gitkeep` files preserve the directory structure.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| `Bind for 0.0.0.0:<port> failed` | Another app/container owns the port. Set port override variables in `.env`. |
| Docker API connection failed | Start Docker Desktop and wait for the daemon to be ready. |
| DeepFace startup is slow | First run downloads or initializes model weights. Later runs reuse `deepface_weights`. |
| Frontend calls the wrong backend URL | Check `VITE_API_BASE_URL`, then rebuild frontend images. |
| Browser CORS error | Add the active frontend/gateway origin to `BACKEND_CORS_ORIGINS`. |

## Roadmap

- Split `image_key` / `object_key` into dedicated schema fields instead of storing them in `image_path`.
- Add Alembic migrations.
- Add max upload size, MIME sniffing and image dimension validation.
- Add Playwright E2E tests for login, employee enrollment and access check.
- Store multiple embeddings per employee for better stability across lighting and pose.
- Add a small accuracy report: correct, wrong, rejected and average latency.
- Add realtime evidence: average latency, worst-case latency, success rate and queue pressure.
- Harden role/permission boundaries for access logs if user and operator roles diverge.
