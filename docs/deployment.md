# Deployment

Tai lieu nay ghi cach chay DeepFace Access Control sau Giai Doan 8.

## Local Dev

Chay stack local:

```powershell
.\scripts\dev.ps1 -Build
```

Seed tai khoan demo:

```powershell
.\scripts\seed.ps1
```

Hoac vua start vua seed:

```powershell
.\scripts\dev.ps1 -Build -Seed
```

URL mac dinh:

- Backend health: `http://localhost:8000/health`
- Backend docs: `http://localhost:8000/docs`
- User app: `http://localhost:5173`
- Admin app: `http://localhost:5174`
- Nginx entrypoint: `http://localhost:8080`
- Prometheus: `http://localhost:9090`
- Alertmanager: `http://localhost:9093`
- Grafana: `http://localhost:3000`
- MinIO console: `http://localhost:9001`
- Qdrant HTTP: `http://localhost:6333`

## Docker Compose Services

`docker-compose.yml` hien co:

- `database`: PostgreSQL.
- `redis`: queue cho embedding/access jobs.
- `backend`: FastAPI API.
- `worker`: DeepFace background worker.
- `frontend-user`: static user UI served by nginx.
- `frontend-admin`: static admin UI served by nginx.
- `nginx`: reverse proxy.
- `prometheus`: scrape backend metrics.
- `alertmanager`: nhan alert tu Prometheus trong local monitoring.
- `grafana`: dashboard doc metric tu Prometheus.
- `minio`: object storage cho upload employee face image va access snapshot.
- `qdrant`: vector database dung lam search index cho access matching; PostgreSQL van la source of truth.

## Health Check

- Backend: `GET /health`, kiem tra database va Redis.
- Backend metrics: `GET /metrics`.
- Docker Compose co healthcheck cho PostgreSQL, Redis, backend, frontend va nginx.
- Worker healthcheck hien ping Redis; worker chua co HTTP health endpoint rieng.

## Nginx Routes

Nginx lang nghe port `8080` mac dinh:

- `/`: user frontend.
- `/admin/`: admin frontend.
- `/api/`: proxy sang backend, strip prefix `/api`.
- `/docs`: Swagger.
- `/openapi.json`: OpenAPI schema.
- `/health`: backend health.
- `/metrics`: backend metrics.

Ghi chu: frontend Docker image build static asset bang Vite roi serve bang nginx. `VITE_API_BASE_URL` va `VITE_BASE_PATH` la build-time config, duoc truyen vao Docker build qua build args trong Docker Compose/CI. Khi muon di tat ca qua nginx, dat:

```text
VITE_API_BASE_URL=/api
```

## Environment

Copy `.env.example` thanh `.env` neu muon tuy bien.

Secret production khong nen commit vao repo. Cac bien can doi khi deploy that:

- `POSTGRES_PASSWORD`
- `AUTH_SECRET_KEY`
- `MINIO_ROOT_USER`
- `MINIO_ROOT_PASSWORD`
- cac URL/host public va CORS origins

## Helm

Chart nam tai:

```text
helm/deepface-access
```

Kiem tra chart:

```powershell
helm lint helm/deepface-access
helm template deepface-access helm/deepface-access
```

Khi bat ingress nginx, chart render 2 ingress:

- `deepface-access-api-ingress`: route `/api(/|$)(.*)` ve backend va rewrite thanh `/$2`, vi backend co route `/auth`, `/access`, `/employees`... chu khong co prefix `/api`.
- `deepface-access-ingress`: route `/docs`, `/openapi.json`, `/admin` va `/` ma khong rewrite prefix.

Vi vay frontend co the dung:

```text
VITE_API_BASE_URL=/api
```

Va cac request nhu `/api/auth/login`, `/api/health` se toi backend lan luot thanh `/auth/login`, `/health`.

Chart hien tai khong tu tao Kubernetes Secret that. Cac template backend/worker/database/minio se doc secret co san ten `deepface-access-secrets`, vi vay secret nay can duoc tao truoc khi deploy that.

### Helm Image Registry

Helm chart dung Docker Hub theo cung format voi GitHub Actions:

```text
<dockerhub-username>/deepface-backend:<tag>
<dockerhub-username>/deepface-worker:<tag>
<dockerhub-username>/deepface-frontend-user:<tag>
<dockerhub-username>/deepface-frontend-admin:<tag>
```

Trong `helm/deepface-access/values.yaml`, cac bien can doi khi deploy image da publish la:

```yaml
global:
  imageRegistry: <dockerhub-username>
  imageTag: <commit-sha-or-latest>
```

Vi du:

```powershell
helm upgrade --install deepface-access helm/deepface-access `
  --set global.imageRegistry=<dockerhub-username> `
  --set global.imageTag=latest
```

Neu Docker Hub repository la private, tao image pull secret va truyen vao `global.imagePullSecrets`.

Secret that nen tao ngoai chart:

```powershell
kubectl create secret generic deepface-access-secrets `
  --from-literal=AUTH_SECRET_KEY='replace-me' `
  --from-literal=POSTGRES_DB='deepface_access' `
  --from-literal=POSTGRES_USER='deepface' `
  --from-literal=POSTGRES_PASSWORD='replace-me'
```

Neu bat MinIO trong chart, bo sung them:

```powershell
kubectl create secret generic deepface-access-secrets `
  --from-literal=AUTH_SECRET_KEY='replace-me' `
  --from-literal=POSTGRES_DB='deepface_access' `
  --from-literal=POSTGRES_USER='deepface' `
  --from-literal=POSTGRES_PASSWORD='replace-me' `
  --from-literal=MINIO_ROOT_USER='replace-me' `
  --from-literal=MINIO_ROOT_PASSWORD='replace-me'
```

Neu secret nay chua ton tai, chart van render duoc nhung pod co the thieu bien moi truong quan trong luc start.

Gioi han hien tai:

- Helm chart la baseline de render/deploy, chua duoc xac nhan tren cluster production that.
- Database/Redis/MinIO/Qdrant trong chart phu hop dev/staging nho; production nen can nhac managed service.
- Cot database `image_path` tam thoi luu MinIO object key de tranh migration lon; neu production hoa nen doi schema ro thanh `image_key`/`object_key`.
