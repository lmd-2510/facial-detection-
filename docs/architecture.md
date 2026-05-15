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
-> Backend /employees/{id}/face-image
-> MinIO/S3 object key
-> Backend /employees/{id}/embedding-jobs
-> Redis embedding_jobs
-> Worker
-> download object ve temp file
-> DeepFace detector/liveness/embedder
-> PostgreSQL face_embeddings
```

Flow moi uu tien object key tu MinIO/S3. Cac endpoint JSON van chap nhan `image_path` local de tuong thich smoke test/dev cu.

## Flow Check Access

```text
User UI
-> Backend /access/snapshots
-> MinIO/S3 object key
-> Backend /access/check
-> PostgreSQL access_logs status=processing
-> Redis access_jobs
-> Worker
-> download object ve temp file
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

- Upload file that qua MinIO da co cho employee face image va access snapshot; metadata hien van luu trong cot `image_path` duoi dang object key de tranh migration lon.
- Chua dung Qdrant trong matching production.
- Chua co kenh gui alert ra email/Slack/webhook production.
- Helm chart da render/lint duoc, nhung chua xac nhan tren cluster production.
