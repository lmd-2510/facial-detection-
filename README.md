# DeepFace Access Control MVP

He thong demo kiem soat ra vao bang nhan dien khuon mat. Repo nay gom day du frontend, backend API, worker AI, database, object storage, vector database, reverse proxy, monitoring, backup script, CI va Helm chart baseline.

Trang thai da verify gan nhat tren may local: Docker Compose build/start thanh cong, backend va frontend healthy, UI da duoc chup lai trong `docs/screenshots`.

## Tong Quan

He thong duoc chia thanh cac khoi chinh:

- `frontend/home`: trang chon vai tro.
- `frontend/user`: giao dien nhan vien/nguoi dung de check access.
- `frontend/admin`: giao dien quan tri vien de quan ly employee, camera, user va log.
- `backend`: FastAPI API server, auth, CRUD, upload anh va day job vao Redis.
- `worker`: xu ly face detection, anti-spoofing tuy chon, embedding, matching va cap nhat access log.
- `database`: PostgreSQL, luu user, employee, camera, embedding va access log.
- `redis`: hang doi `embedding_jobs` va `access_jobs`.
- `minio`: object storage cho anh enrollment va snapshot access.
- `qdrant`: vector database de tim embedding gan nhat.
- `nginx`: gateway cho home/user/admin/backend.
- `monitoring`: Prometheus, Alertmanager, Grafana.
- `helm`: baseline chart de package len Kubernetes.

Luong chinh:

```text
Frontend Home/User/Admin
        |
        v
Nginx Gateway
        |
        +--> Backend API
                |
                +--> PostgreSQL
                +--> MinIO
                +--> Redis queues
                         |
                         v
                       Worker
                         |
                         +--> DeepFace pipeline
                         +--> Qdrant vector search
                         +--> update PostgreSQL access_logs
```

## Anh Giao Dien

Mot vai man hinh chinh duoc chup tu Docker Compose stack local. May hien tai co mot stack khac dang dung port mac dinh, nen lan chup nay dung port override trong `.env`: gateway `18081`, backend `18001`, user `15173`, admin `15174`.

| Home |
| --- |
| <img src="docs/screenshots/home.png" alt="Home screen" width="760"> |

| User access | Admin dashboard |
| --- | --- |
| <img src="docs/screenshots/user-access.png" alt="User access screen" width="420"> | <img src="docs/screenshots/admin-dashboard.png" alt="Admin dashboard" width="420"> |

## Quick Start

Yeu cau:

- Docker Desktop dang chay.
- Docker Compose plugin co san qua lenh `docker compose`.
- Lan dau build worker co the lau vi phai cai DeepFace/TensorFlow va tai model weight.

Chay nhanh:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```

Kiem tra stack:

```powershell
docker compose ps
.\scripts\demo-baseline-check.ps1
```

Dung stack:

```powershell
docker compose down
```

Neu may dang co tien trinh khac dung port mac dinh, dat cac bien port trong `.env` truoc khi build:

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

Khi doi `VITE_API_BASE_URL`, can rebuild frontend:

```powershell
docker compose up --build -d frontend-user frontend-admin nginx
```

Neu frontend duoc mo tu port override, them cac origin do vao `BACKEND_CORS_ORIGINS`.

## URL Mac Dinh

| Thanh phan | URL mac dinh | Ghi chu |
| --- | --- | --- |
| Home gateway | `http://localhost:8080` | Trang chon User/Admin |
| User UI qua gateway | `http://localhost:8080/user/` | Flow check access |
| Admin UI qua gateway | `http://localhost:8080/admin/` | Quan tri he thong |
| User UI truc tiep | `http://localhost:5173/user/` | Container frontend-user |
| Admin UI truc tiep | `http://localhost:5174/admin/` | Container frontend-admin |
| Backend health | `http://localhost:8000/health` | API health |
| Backend docs | `http://localhost:8000/docs` | Swagger UI |
| MinIO console | `http://localhost:9001` | Object storage UI |
| Prometheus | `http://localhost:9090` | Metrics/targets |
| Alertmanager | `http://localhost:9093` | Alert routing local |
| Grafana | `http://localhost:3000` | Dashboard |
| Qdrant HTTP | `http://localhost:6333` | Vector DB API |

Neu `.env` co port override, thay port trong bang bang gia tri tu `.env`.

## Tai Khoan Demo

| Vai tro | Username | Password |
| --- | --- | --- |
| Admin | `admin` | `admin123` |
| User | `user` | `user123` |
| Grafana | `admin` | Gia tri `GRAFANA_ADMIN_PASSWORD` |
| MinIO | Gia tri `MINIO_ROOT_USER` | Gia tri `MINIO_ROOT_PASSWORD` |

Tai khoan demo duoc seed boi service `db-seed`. Co the doi bang cac bien `SEED_ADMIN_USERNAME`, `SEED_ADMIN_PASSWORD`, `SEED_USER_USERNAME`, `SEED_USER_PASSWORD`.

## Flow Demo Chinh

1. Admin dang nhap vao `/admin/`.
2. Admin tao employee.
3. Admin upload anh khuon mat cho employee. Backend luu anh vao MinIO va day `embedding_jobs`.
4. Worker xu ly anh, tao embedding, luu PostgreSQL va upsert vector vao Qdrant.
5. User dang nhap vao `/user/`.
6. User upload snapshot hoac chup frame webcam.
7. Backend luu snapshot vao MinIO va day `access_jobs`.
8. Worker tao embedding snapshot, search Qdrant, so khop threshold va cap nhat `access_logs`.
9. User/Admin xem ket qua `granted`, `denied`, `processing` hoac `error`.

## Service Trong Docker Compose

| Service | Vai tro | Port host mac dinh | Bien override |
| --- | --- | --- | --- |
| `database` | PostgreSQL | `5432` | `POSTGRES_PORT` |
| `redis` | Queue | `6379` | `REDIS_PORT` |
| `db-seed` | Tao bang va seed demo | Khong expose | Khong co |
| `backend` | FastAPI | `8000` | `BACKEND_PORT` |
| `worker` | Xu ly AI jobs | Khong expose | Khong co |
| `frontend-home` | Home UI | `5172` | `FRONTEND_HOME_PORT` |
| `frontend-user` | User UI | `5173` | `FRONTEND_USER_PORT` |
| `frontend-admin` | Admin UI | `5174` | `FRONTEND_ADMIN_PORT` |
| `nginx` | Gateway | `8080` | `NGINX_PORT` |
| `minio` | S3-compatible storage | `9000`, `9001` | `MINIO_API_PORT`, `MINIO_CONSOLE_PORT` |
| `qdrant` | Vector DB | `6333`, `6334` | `QDRANT_HTTP_PORT`, `QDRANT_GRPC_PORT` |
| `prometheus` | Metrics scrape | `9090` | `PROMETHEUS_PORT` |
| `alertmanager` | Alert routing | `9093` | `ALERTMANAGER_PORT` |
| `grafana` | Dashboard | `3000` | `GRAFANA_PORT` |

## Cau Truc Thu Muc

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
|-- docs/                    Architecture, API, deployment, operations notes
|-- docs/screenshots/        UI screenshots captured from local stack
|-- scripts/                 Test, seed, smoke, backup, readiness scripts
|-- data/smoke/              Small smoke-test image set
`-- docker-compose.yml       Local multi-service runtime
```

## Test Va Kiem Tra

Chay test tong hop tren may co Python dependencies va Node/npm:

```powershell
.\scripts\test.ps1
```

Script nay chay:

- Backend API tests: `python -m pytest backend\app\tests`
- Worker tests: `python -m pytest worker\app\tests`
- Admin frontend build: `npm run build`
- User frontend build: `npm run build`

Kiem tra baseline demo khi stack dang chay:

```powershell
.\scripts\demo-baseline-check.ps1
```

Chi kiem tra file/cau hinh, khong goi runtime:

```powershell
.\scripts\demo-baseline-check.ps1 -StaticOnly
```

Smoke test DeepFace that:

```powershell
.\scripts\smoke-deepface.ps1
```

Smoke test nay dung PostgreSQL, Qdrant va worker container de tao embedding that va test matching. Lan dau co the cham vi DeepFace tai model weight vao volume `deepface_weights`.

## API Chinh

| Nhom | Endpoint tieu bieu | Vai tro |
| --- | --- | --- |
| Auth | `POST /auth/login`, `GET /auth/me` | Dang nhap va lay user hien tai |
| Admin users | `GET/POST/PUT/DELETE /admin/users` | Quan ly tai khoan |
| Employees | `GET/POST/PUT/DELETE /employees` | Quan ly nhan vien |
| Employee images | `POST /employees/{id}/face-image` | Upload anh enrollment va tao embedding job |
| Cameras | `GET/POST/PUT/DELETE /cameras` | Quan ly camera |
| Access | `POST /access/check`, `POST /access/check-image` | Tao access check |
| Logs | `GET /logs` | Xem access logs |
| Operations | `GET /health`, `GET /metrics`, `GET /admin/status` | Health/metrics/status |

Chi tiet hon nam trong `docs/api.md`.

## Cau Hinh Quan Trong

| Bien | Y nghia |
| --- | --- |
| `DATABASE_URL` | Connection string PostgreSQL cho backend/worker |
| `REDIS_URL` | Redis queue URL |
| `AUTH_SECRET_KEY` | Secret ky JWT |
| `BACKEND_CORS_ORIGINS` | Danh sach origin frontend duoc goi API |
| `VITE_API_BASE_URL` | Backend URL duoc build vao frontend |
| `MINIO_ENDPOINT` | Endpoint MinIO noi bo trong Docker network |
| `MINIO_BUCKET` | Bucket luu anh |
| `QDRANT_URL` | Qdrant URL noi bo |
| `QDRANT_COLLECTION` | Collection vector embedding |
| `DEEPFACE_MODEL_NAME` | Model embedding, mac dinh `Facenet512` |
| `DEEPFACE_MATCH_THRESHOLD` | Threshold matching |
| `DEEPFACE_ANTI_SPOOFING` | Bat/tat anti-spoofing |
| `MAX_PROCESSING_ACCESS_LOGS_PER_CAMERA` | Gioi han frame dang processing moi camera |

## Bao Mat Va Luu Y Production

Gia tri mac dinh trong repo chi phu hop demo local. Truoc khi deploy that:

- Doi `AUTH_SECRET_KEY`, PostgreSQL password, MinIO credential, Grafana password va seed password.
- Khong dung `admin123`, `user123`, `minioadmin` ngoai demo.
- Dat `BACKEND_CORS_ORIGINS` dung domain that, khong mo rong hon can thiet.
- Dung image tag bat bien nhu commit SHA thay vi `latest`.
- Bat HTTPS/TLS o ingress hoac reverse proxy public.
- Gioi han kich thuoc upload va validate content anh that, khong chi dua vao extension.
- Xem lai quyen `GET /logs`: hien moi user da login co the doc log, phu hop cho demo/operator nhung co the qua rong neu user la nhan vien ca nhan.
- Chuyen migration sang Alembic khi schema bat dau on dinh; hien tai code dung `create_all` va mot so `ALTER TABLE` baseline.

## CI/CD Va Deployment

Workflow `.github/workflows/ci.yml` hien co:

- Chay backend tests tren Python 3.12.
- Chay worker tests tren Python 3.12.
- Build user/admin frontend tren Node 22.
- Build Docker images cho backend, worker, frontend-home, frontend-user, frontend-admin.
- Push Docker Hub khi push len `main` va co secrets `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`.

Helm chart baseline nam trong `helm/deepface-access`. Khi deploy Kubernetes that, can tao Kubernetes Secret rieng cho database/auth/minio va cau hinh image registry/tag dung.

## Backup

Chay backup toi thieu:

```powershell
.\scripts\backup.ps1
```

Script luu dump database va archive local vao `backup/`. Thu muc backup output duoc ignore, chi giu `.gitkeep`.

## Troubleshooting

Port da bi chiem:

```text
Bind for 0.0.0.0:<port> failed: port is already allocated
```

Xu ly:

1. Kiem tra container/ung dung dang dung port.
2. Doi bien port trong `.env`.
3. Neu doi backend port, doi luon `VITE_API_BASE_URL` va rebuild frontend.
4. Neu doi frontend/gateway port, them origin moi vao `BACKEND_CORS_ORIGINS`.

Docker daemon chua chay:

```text
failed to connect to the docker API
```

Mo Docker Desktop, doi daemon san sang, sau do chay lai `docker compose up --build -d`.

DeepFace lan dau khoi dong cham:

- Worker co the tai model weight lan dau.
- Volume `deepface_weights` giup cache model cho cac lan sau.

Frontend dang goi sai backend:

- Kiem tra `VITE_API_BASE_URL`.
- Vi Vite build-time env duoc dong goi vao static assets, can rebuild image frontend sau khi doi bien nay.

## Huong Phat Trien Tiep Theo

- Tach schema `image_key`/`object_key` rieng thay vi luu tam trong cot `image_path`.
- Them Alembic migrations.
- Them max upload size, MIME sniffing va image dimension validation.
- Bo sung Playwright E2E test cho login, upload employee image va access check.
- Luu nhieu embedding cho moi employee de on dinh voi nhieu goc mat/anh sang.
- Tao accuracy report nho: so ca dung, sai, reject va latency trung binh.
- Bo sung realtime evidence: latency average/worst-case, success rate va queue pressure khi spam frame.
- Hardening role/permission cho access logs neu can tach user ca nhan va operator.
