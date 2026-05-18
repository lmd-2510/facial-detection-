# DeepFace Access Control MVP

Day la repository MVP cho he thong kiem soat ra vao bang nhan dien khuon mat. Project duoc to chuc theo huong nhieu service chay bang Docker, gom frontend, backend API, worker xu ly AI, database va cac thanh phan ha tang phu tro.

Muc tieu hien tai cua README nay la giup nguoi doc co ban do tong quan truoc khi di vao code chi tiet.

## Tong Quan He Thong

He thong co the hieu theo cac khoi lon sau:

- `frontend/`: giao dien nguoi dung va giao dien admin.
- `backend/`: FastAPI backend, nhan request tu frontend va dieu phoi nghiep vu.
- `worker/`: tien trinh nen xu ly anh, embedding va matching khuon mat.
- `data/`: noi luu tru file local duoc mount vao container.
- `nginx/`: cau hinh reverse proxy/web server.
- `monitoring/`: cau hinh theo doi he thong.
- `backup/`: noi mac dinh de script luu output backup local.
- `helm/`: cau hinh deploy len Kubernetes.
- `scripts/`: cac script ho tro dev, test, seed data va backup.
- `docs/`: tai lieu giai thich kien truc, API, database, AI pipeline, CI/CD va van hanh.

## Cac Service Chinh

Trong `docker-compose.yml`, he thong duoc chay bang cac service chinh:

- `frontend-user`: ung dung React cho nguoi dung.
- `frontend-admin`: ung dung React cho quan tri vien.
- `backend`: FastAPI API server.
- `worker`: background worker xu ly cac job AI.
- `database`: PostgreSQL, luu user, employee, camera, access log va embedding.
- `redis`: queue trung gian giua backend va worker.
- `nginx`: reverse proxy prod-like cho frontend/backend.
- `prometheus`: scrape metric toi thieu cua backend.
- `alertmanager`: nhan alert tu Prometheus trong local monitoring.
- `grafana`: dashboard truc quan hoa metric Prometheus.
- `minio`: object storage cho anh employee/access snapshot trong flow upload moi.
- `qdrant`: vector database dung lam search index cho access matching; PostgreSQL van la source of truth.

Co the hinh dung luong tong quat nhu sau:

```text
Frontend User/Admin
        |
        v
Backend API
        |
        +--> PostgreSQL
        |
        +--> Redis Queue
                  |
                  v
                Worker
                  |
                  +--> xu ly face embedding / matching
                  +--> cap nhat ket qua vao database
```

## MVP Flow

Flow chinh cua MVP:

1. Admin tao employee.
2. Admin upload anh khuon mat cho employee len MinIO va nhan `image_key`.
3. Backend tao embedding job trong Redis.
4. Worker doc job tu Redis.
5. Worker tao embedding cho anh khuon mat.
6. User upload anh/snapshot len MinIO va gui `image_key` de kiem tra quyen ra vao.
7. Worker so sanh embedding cua snapshot voi embedding da dang ky.
8. He thong ghi access log voi ket qua `granted`, `denied` hoac `error`.

Hien tai project da hoan thanh phan code cot loi cua Giai Doan 7 va lop van hanh Giai Doan 8. Backend co API cot loi cho auth, employees, cameras, logs, upload anh len MinIO, va day duoc `embedding_jobs` / `access_jobs` vao Redis bang object key. Worker nghe Redis queue, tai anh tu MinIO ve temp file, dung DeepFace cho face detection, anti-spoofing/liveness, embedding va cosine matching, luu vector vao `face_embeddings`, va cap nhat `access_logs` thanh `granted`, `denied` hoac `error`. Admin/user frontend da co login, thao tac flow chinh theo API, hien thi loading/error/empty state co ban; user UI co the upload snapshot hoac chup frame tu webcam de check access.

## Mapping Theo Yeu Cau De Bai

Bang nay giup doi chieu nhanh giua cac yeu cau he thong va phan hien co trong repo.

| Yeu cau / thanh phan | Repo hien co | Bang chung nhanh |
| --- | --- | --- |
| Frontend user | `frontend/user` | User UI login, upload file/chup webcam snapshot, check access, xem history/profile |
| Frontend admin | `frontend/admin` | Admin UI login, quan ly employee, camera, user va access logs |
| Backend API | `backend` | FastAPI routes cho auth, employees, cameras, users, logs, access, health, metrics |
| Message queue | `redis` service, `backend/app/queues`, `worker/app/tasks` | Redis queues `embedding_jobs` va `access_jobs` |
| Database | `database` PostgreSQL, `backend/app/models`, `worker/app/db/schema.py` | Luu users, employees, cameras, face_embeddings, access_logs |
| Object storage | `minio` service, `backend/app/services/storage_service.py`, `worker/app/services/storage_service.py` | Upload employee face image va access snapshot vao MinIO/S3 flow |
| Vector database | `qdrant` service, `worker/app/services/vector_store_service.py` | Worker upsert/search embedding bang Qdrant, PostgreSQL van la source of truth |
| AI inference | `worker/app/ml`, `worker/app/services` | DeepFace detect face, optional anti-spoofing, embedding Facenet512, matching |
| Frontend webcam/camera capture | `frontend/user/src/components/CameraView.tsx` | User UI chup frame JPEG bang browser webcam va gui qua `/access/check-image` |
| Authentication / roles | `backend/app/core/deps.py`, `backend/app/api/admin.py`, `frontend/admin/src/pages/UserPage.tsx` | Bearer token, role `admin`/`user`, admin user management |
| Reverse proxy / load balancer baseline | `nginx/nginx.conf` | Route `/`, `/admin/`, `/api/`, `/health`, `/docs`, `/metrics` |
| Docker Compose | `docker-compose.yml` | Chay local multi-service bang `docker compose up --build` |
| Monitoring | `monitoring/prometheus`, `monitoring/grafana`, `monitoring/alertmanager` | Prometheus scrape `/metrics`, Grafana dashboard, Alertmanager UI |
| Backup | `scripts/backup.ps1`, `docs/backup.md` | Backup PostgreSQL dump va archive thu muc `data/` |
| CI/CD artifact publishing | `.github/workflows/ci.yml`, `docs/cicd.md` | Test/build va publish Docker images len Docker Hub khi push `main` |
| Helm / Kubernetes packaging | `helm/deepface-access`, `docs/deployment.md` | Helm chart render/lint duoc; deploy cluster can secret va image registry dung |
| Demo verification | `docs/demo-checklist.md`, `scripts/demo-baseline-check.ps1`, `scripts/smoke-deepface.ps1` | Checklist va script de chung minh cac thanh phan chay that |

Ghi chu trung thuc khi demo:

- MinIO va Qdrant da duoc noi vao flow chinh; PostgreSQL van giu vai tro source of truth.
- Helm chart la baseline packaging cho Kubernetes; can deploy len cluster that neu muon chung minh production runtime.
- Anti-spoofing dang de optional voi `DEEPFACE_ANTI_SPOOFING=false` mac dinh de demo nhan dien chinh on dinh.

## Cau Truc Thu Muc Nen Doc Truoc

Nen doc project theo thu tu nay de tranh bi lac:

1. `README.md`: nam muc tieu va ban do tong quan.
2. `docker-compose.yml`: hieu cac service va cach chung ket noi voi nhau.
3. `docs/`: doc cac tai lieu kien truc, AI pipeline, database, API.
4. `backend/app/api/`: xem he thong co nhung API nao.
5. `backend/app/services/`: xem logic nghiep vu chinh.
6. `worker/app/tasks/`: xem worker nhan va xu ly job nao.
7. `worker/app/ml/`: xem phan AI/face processing nam o dau.
8. `frontend/user/` va `frontend/admin/`: xem cac man hinh su dung API nhu the nao.

## Chay Local

Yeu cau may co Docker va Docker Compose.

Chay toan bo he thong:

```powershell
docker compose up --build
```

Hoac dung script dev:

```powershell
.\scripts\dev.ps1 -Build
```

Sau khi chay, co the mo:

- Backend health: http://localhost:8000/health
- Backend API docs: http://localhost:8000/docs
- User app: http://localhost:5173
- Admin app: http://localhost:5174
- Nginx entrypoint: http://localhost:8080
- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- Grafana: http://localhost:3000
- MinIO console: http://localhost:9001
- Qdrant HTTP: http://localhost:6333

Tao bang va seed tai khoan demo:

```powershell
docker compose run --rm backend python -m app.db.seed
```

Tai khoan demo mac dinh:

- `admin` / `admin123`
- `user` / `user123`

Admin UI co trang Users de tao tai khoan demo moi, doi role `admin`/`user`, reset password va xoa user khac.

Chay test tong hop:

```powershell
.\scripts\test.ps1
```

Ghi chu test va smoke test Giai Doan 6 nam trong `docs/phase6-testing.md`.

Chay smoke test DeepFace that trong worker container, chi start cac thanh phan lien quan:

```powershell
.\scripts\smoke-deepface.ps1
```

Smoke test nay dung PostgreSQL, Qdrant va worker container de tao embedding that, matching same-person/different-person va case khong co mat, khong start frontend/nginx/monitoring.
Script cache DeepFace model weight trong Docker volume `deepface_weights`, nen lan dau co the cham hon cac lan sau.

Kiem tra baseline demo nhe khi stack da chay:

```powershell
.\scripts\demo-baseline-check.ps1
```

Neu chi muon kiem tra file/cau hinh ma khong goi endpoint runtime:

```powershell
.\scripts\demo-baseline-check.ps1 -StaticOnly
```

Backup toi thieu database va thu muc `data/`:

```powershell
.\scripts\backup.ps1
```

## File Cau Hinh Quan Trong

- `.env.example`: danh sach bien moi truong mau.
- `docker-compose.yml`: khai bao service local.
- `nginx/nginx.conf`: reverse proxy local/prod-like.
- `monitoring/prometheus/prometheus.yml`: Prometheus scrape config.
- `monitoring/prometheus/rules/`: Prometheus alert rules.
- `monitoring/alertmanager/alertmanager.yml`: Alertmanager local routing config.
- `monitoring/grafana/`: Grafana datasource provisioning va dashboard.
- `.github/workflows/ci.yml`: GitHub Actions test/build va publish Docker images len Docker Hub.
- `backend/Dockerfile`: cach build backend image.
- `worker/Dockerfile`: cach build worker image.
- `frontend/user/Dockerfile`: cach build user frontend.
- `frontend/admin/Dockerfile`: cach build admin frontend.
- `helm/deepface-access/values.yaml`: cau hinh image registry/tag khi deploy Kubernetes, mac dinh theo format Docker Hub `<dockerhub-username>/deepface-<service>:<tag>`.

## Ghi Chu Ve Database

- Schema va mo ta bang du lieu nen doc trong `docs/db-schema.md`.
- Logic model/database cua backend nam trong `backend/app/models/` va `backend/app/db/`.
- Worker giu schema/doc DB toi thieu rieng phuc vu xu ly job trong `worker/app/db/schema.py`.
- Seed tai khoan demo hien duoc thuc hien qua `backend/app/db/seed.py` va `scripts/seed.ps1`.

## Huong Phat Trien Tiep Theo

Nhung phan nen uu tien sau khi da nam tong quan:

- Hoan thien schema rieng cho `image_key`/`object_key` thay vi tam luu trong cot `image_path`.
- Bo sung Playwright end-to-end test khi muon test UI tren browser that.
- Smoke test DeepFace voi bo anh that nho, roi tinh chinh `DEEPFACE_MATCH_THRESHOLD`.
- Bo sung reindex Qdrant khi doi model hoac can rebuild collection.
- Hoan thien kenh gui alert ra email/Slack neu can.
