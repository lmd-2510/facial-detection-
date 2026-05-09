# Architecture

DeepFace Access Control MVP duoc chia thanh cac khoi service doc lap, chay local bang Docker Compose va co baseline Helm cho Kubernetes.

## So Do Tong Quan

```text
User/Admin Frontend
        |
        v
      Nginx
        |
        v
   Backend API
   |        |
   v        v
PostgreSQL Redis Queue
             |
             v
           Worker
             |
             v
        DeepFace pipeline
```

## Runtime Services

- `frontend-user`: React/Vite UI cho nguoi dung check access va xem history.
- `frontend-admin`: React/Vite UI cho admin quan ly employee, camera va logs.
- `nginx`: reverse proxy local/prod-like, route `/`, `/admin/`, `/api/`, `/docs`, `/health`, `/metrics`.
- `backend`: FastAPI API, auth, employee/camera/log/access endpoints, health va metrics.
- `database`: PostgreSQL luu users, employees, cameras, face_embeddings va access_logs.
- `redis`: queue `embedding_jobs` va `access_jobs`.
- `worker`: xu ly job DeepFace, tao embedding, match vector va cap nhat access log.
- `prometheus`: scrape backend `/metrics`.
- `alertmanager`: nhan alert tu Prometheus trong local monitoring.
- `grafana`: dashboard doc metric tu Prometheus.
- `minio`: object storage da san sang ve service/config, chua noi vao upload flow that.
- `qdrant`: vector database da san sang ve service/config, chua noi vao access matching that.

## Flow Dang Ky Khuon Mat

```text
Admin UI
-> Backend /employees
-> Backend /employees/{id}/embedding-jobs
-> Redis embedding_jobs
-> Worker
-> DeepFace detector/liveness/embedder
-> PostgreSQL face_embeddings
```

Hien tai input van la `image_path` local.

## Flow Check Access

```text
User UI
-> Backend /access/check
-> PostgreSQL access_logs status=processing
-> Redis access_jobs
-> Worker
-> DeepFace embedding
-> PostgreSQL face_embeddings matching
-> PostgreSQL access_logs status=granted/denied/error
```

## Van Hanh

- Backend `/health` kiem tra PostgreSQL va Redis.
- Backend `/metrics` expose metric Prometheus toi thieu.
- Docker Compose co healthcheck cho service chinh.
- `scripts/backup.ps1` backup PostgreSQL va thu muc `data/`.
- Helm chart nam trong `helm/deepface-access`.

## Gioi Han Hien Tai

- Chua co upload file that qua MinIO.
- Chua dung Qdrant trong matching production.
- Chua co kenh gui alert ra email/Slack/webhook production.
- Helm chart da render/lint duoc, nhung chua xac nhan tren cluster production.
