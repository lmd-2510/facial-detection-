# Implementation Roadmap

Tai lieu nay la lo trinh de build lai du an DeepFace Access Control MVP tu dau. Muc tieu la code theo tung moc chay duoc, thay vi di sau vao tung file rieng le qua som.

## Cach Dung Tai Lieu Nay

- `README.md` dung de hieu project o muc tong quan.
- `docs/implementation-roadmap.md` dung de biet nen code gi, theo thu tu nao, va khi nao xem la xong.
- Khi bat dau mot giai doan, chi nen tap trung vao file va moc kiem tra cua giai doan do.
- Sau moi giai doan, cap nhat lai docs lien quan neu co thay doi ve kien truc, API hoac database.

## Nguyen Tac Lam Viec

- Di tu tong quan den chi tiet.
- Uu tien tao he thong chay duoc truoc, tinh nang day du lam sau.
- Code theo flow nguoi dung, khong code theo thu muc tu tren xuong.
- Moi giai doan nen co mot moc kiem tra ro rang.
- Chua tich hop AI that ngay; lam fake pipeline truoc de test end-to-end.
- Moi lan code xong mot phan nho, chay test/kiem tra ngay.
- Khong lam deploy, monitoring, AI nang khi core flow chua chay duoc.

## Mo Hinh Can Giu Trong Dau

```text
frontend-user/admin
        |
        v
backend API
        |
        +--> PostgreSQL
        |
        +--> Redis queue
                  |
                  v
                worker
                  |
                  +--> fake AI pipeline truoc
                  +--> DeepFace/Qdrant sau
```

Neu bi roi, quay lai flow nay truoc khi doc tiep code.

## Giai Doan 1: Dung Khung Chay Duoc

Muc tieu: chay duoc he thong rong truoc, chua can chuc nang that.

File dau ra can co:

```text
docker-compose.yml
backend/Dockerfile
backend/requirements.txt
backend/app/main.py
frontend/user/Dockerfile
frontend/user/package.json
frontend/user/src/App.tsx
frontend/admin/Dockerfile
frontend/admin/package.json
frontend/admin/src/App.tsx
worker/Dockerfile
worker/requirements.txt
worker/app/main.py
```

Viec can lam:

1. Viet lai `docker-compose.yml` toi gian.
2. Tao cac service co ban:
   - `database`
   - `redis`
   - `backend`
   - `frontend-user`
   - `frontend-admin`
   - `worker`  
3. Viet `backend/Dockerfile` va `backend/requirements.txt`.
4. Viet `backend/app/main.py` voi endpoint `GET /health`.
5. Viet frontend user toi thieu hien trang "User App".
6. Viet frontend admin toi thieu hien trang "Admin App".
7. Viet `worker/app/main.py` de worker start duoc va log ra console.

Tam thoi chua can:

- MinIO
- Qdrant
- monitoring
- helm
- nginx production config

Moc hoan thanh:

```powershell
docker compose up --build
```

Mo duoc:

```text
http://localhost:8000/health
http://localhost:5173
http://localhost:5174
```

Kiem tra nhanh:

- Backend tra ve JSON health status.
- User frontend render duoc trang toi thieu.
- Admin frontend render duoc trang toi thieu.
- Worker container khong crash.
- `docker compose logs` khong co loi import/module not found.

## Giai Doan 2: Thiet Ke Database Toi Thieu
Muc tieu: xac dinh he thong can luu nhung du lieu gi.

Tai lieu can cap nhat:

```text
docs/db-schema.md
```

Bang toi thieu nen co:

- `users`: tai khoan admin/user.
- `employees`: nhan vien duoc dang ky khuon mat.
- `cameras`: camera hoac cong ra vao.
- `access_logs`: lich su ra vao.
- `face_embeddings`: vector khuon mat cua employee.

Goi y truong du lieu ban dau:

- `users`: `id`, `username`, `password_hash`, `role`, `created_at`.
- `employees`: `id`, `code`, `name`, `department`, `status`, `created_at`.
- `cameras`: `id`, `name`, `location`, `stream_url`, `status`.
- `access_logs`: `id`, `employee_id`, `camera_id`, `status`, `score`, `image_path`, `created_at`.
- `face_embeddings`: `id`, `employee_id`, `vector`, `model_name`, `created_at`.

Viec can lam:

1. Ghi schema tong quan vao `docs/db-schema.md`.
2. Tao model trong `backend/app/models/`.
3. Tao ket noi database trong backend.
4. Dam bao backend ket noi duoc PostgreSQL.
5. Chuan bi cach tao bang/migration.

Moc hoan thanh:

- Backend ket noi duoc PostgreSQL.
- Cac bang co the duoc tao thanh cong.
- Co seed user admin/user de dang nhap thu.

## Giai Doan 3: Lam Backend API Cot Loi

Muc tieu: backend co API that de frontend va worker co the bam vao.

File/folder dau ra can co:

```text
backend/app/api/
backend/app/services/
backend/app/repositories/
backend/app/models/
backend/app/schemas/
backend/app/core/
backend/app/db/
backend/app/tests/
```

Thu tu API nen lam:

1. Auth:
   - `POST /auth/login`
   - `GET /auth/me`
2. Employees:
   - `GET /employees`
   - `POST /employees`
   - `GET /employees/{id}`
   - `PUT /employees/{id}`
   - `DELETE /employees/{id}`
3. Cameras:
   - `GET /cameras`
   - `POST /cameras`
4. Logs:
   - `GET /logs`
5. Access:
   - `POST /access/check`

Cau truc backend nen theo lop:

```text
api -> services -> repositories -> models
```

Vi du voi employee:

```text
backend/app/api/employees.py
backend/app/services/employee_service.py
backend/app/repositories/employee_repository.py
backend/app/models/employee.py
backend/app/schemas/employee.py
```

Moc hoan thanh:

- Mo duoc Swagger tai `http://localhost:8000/docs`.
- Test duoc API cot loi bang Swagger.
- Dang nhap duoc bang tai khoan demo.
- CRUD employee chay duoc.
- CRUD camera co API toi thieu.
- Xem duoc access logs.

Khi nao nen viet test:

- Sau khi auth login chay duoc.
- Sau khi employee CRUD chay duoc.
- Sau khi access check co response on dinh.

## Giai Doan 4: Lam Queue Giua Backend Va Worker

Muc tieu: backend chi nhan request va day job, worker xu ly viec nang o background.

Queue can co:

- `embedding_jobs`: tao embedding cho anh employee.
- `access_jobs`: xu ly anh check ra vao.

Flow:

```text
Admin upload anh employee
-> backend luu file
-> backend push embedding job vao Redis
-> worker lay job
-> worker xu ly
-> worker cap nhat database
```

File nen lam:

```text
backend/app/queues/embedding_queue.py
backend/app/queues/access_queue.py
worker/app/tasks/queue_worker.py
worker/app/tasks/embedding_job.py
worker/app/tasks/access_job.py
```

Moc hoan thanh:

- Backend gui duoc job vao Redis.
- Worker nhan duoc job va log ra console.
- Job payload co format ro rang.
- Neu worker xu ly loi, access log hoac job status khong bi mat thong tin loi.

Goi y payload:

```json
{
  "job_id": "uuid",
  "type": "embedding",
  "employee_id": 1,
  "image_path": "/app/storage/uploads/example.jpg"
}
```

Va access job:

```json
{
  "job_id": "uuid",
  "type": "access_check",
  "camera_id": 1,
  "image_path": "/app/storage/uploads/snapshot.jpg"
}
```

## Giai Doan 5: Lam AI Pipeline Fake Truoc

Muc tieu: chay duoc flow nhan dien end-to-end truoc khi tich hop DeepFace that.

Trong `worker/app/ml/`, tao cac module:

- `detector.py`: gia lap phat hien khuon mat.
- `anti_spoof.py`: ban dau co the luon pass.
- `embedder.py`: tao vector fake tu file anh.
- `matcher.py`: so sanh vector bang cosine similarity.

Moc hoan thanh:

- Upload anh employee thi tao duoc embedding.
- Upload anh check access thi tra ve ket qua `granted`, `denied` hoac `error`.
- Access log duoc cap nhat vao database.

Nguyen tac fake AI:

- Ket qua nen deterministic, cung mot anh thi tao cung mot vector.
- Khong can dung model nang.
- Khong can accuracy cao.
- Muc tieu la test duoc flow tu upload -> queue -> worker -> database -> response/log.

Flow mong muon:

```text
image_path
-> detector
-> anti_spoof
-> embedder
-> matcher
-> decision
-> access_log
```

## Giai Doan 6: Lam Frontend Theo API

Muc tieu: nguoi dung thao tac duoc flow chinh bang UI.

Trang thai hien tai:

- Admin app da co login, dashboard, employee management, camera management, access logs va settings.
- User app da co login, access check, history va profile.
- UI da luu Bearer token trong localStorage va gui token kem request API.
- Da co loading, error va empty state co ban cho cac flow chinh.
- Da co `scripts/test.ps1` de chay backend/worker tests va frontend build neu may co `npm`.
- Gioi han con lai: chua upload file that, van nhap `image_path` thu cong; chua co Playwright end-to-end test tren browser.

Nguyen tac frontend:

- Lam theo API da on dinh, khong tu che flow rieng.
- Admin app uu tien tinh nang quan ly.
- User app uu tien flow check access.
- Moi page nen co loading, error va empty state toi thieu.

Admin app nen lam truoc:

1. Login page.
2. Dashboard.
3. Employee management.
4. Camera management.
5. Access logs.

User app lam sau:

1. Login page.
2. Access check.
3. History.
4. Profile.

Thu tu uu tien:

1. Login.
2. Admin employee CRUD.
3. Admin camera CRUD.
4. User access check.
5. Access history.

Moc hoan thanh:

- Khong can dung Swagger cho flow chinh nua.
- Admin va user co the thao tac tren UI.
- Form co validate co ban.
- Loi API duoc hien thi ro rang.
- Token dang nhap duoc luu va gui kem request.

## Giai Doan 7: Thay Fake AI Bang DeepFace That

Muc tieu: thay toan bo cac phan fake AI trong worker bang pipeline DeepFace that cho flow dang ky va check access.

Y nghia cua "xong Giai Doan 7":

- Khong con detector fake trong flow xu ly that.
- Khong con anti-spoof/liveness fake trong flow xu ly that, hoac phai ghi ro la tam thoi tat tinh nang nay.
- Khong con embedder fake trong flow xu ly that.
- Matching dung embedding that va threshold duoc hieu chinh bang bo anh test toi thieu.
- Worker chay duoc voi Docker Compose va xu ly duoc job that tu dau den cuoi.
- Docs ghi ro phan nao da that, phan nao chua lam.

Trang thai repo hien tai:

- `worker/app/ml/embedder.py` da goi `DeepFace.represent()`.
- `worker/app/ml/detector.py` da goi `DeepFace.extract_faces()` de detect mat.
- `worker/app/ml/anti_spoof.py` da goi `DeepFace.extract_faces(anti_spoofing=True)` de check liveness khi bat config; smoke test local hien mac dinh tat anti-spoof.
- Worker requirements da them `deepface`.
- Cau hinh DeepFace/threshold nam trong bien moi truong `DEEPFACE_*`.
- `face_embeddings.model_name` luu model that, mac dinh `Facenet512`.
- Access matching chi so voi embedding active co cung `model_name`.
- `worker/app/services/storage_service.py` da co resolve/validate `image_path` toi thieu va da duoc noi vao flow embedding/access.
- `worker/app/services/reindex_service.py` da ghi ro chua the reindex that vi `face_embeddings` chua luu source `image_path`.
- Chua co smoke test Docker Compose de xac nhan DeepFace that tai model va chay duoc trong container.
- Chua co bo anh test nho de tinh chinh threshold matching.

Nhung gi con thieu de xem la xong Giai Doan 7:

1. Thay fake detector bang detector that
   - Trang thai: da lam.
   - Quy ve mot wrapper ro rang trong `worker/app/ml/detector.py`.
   - Wrapper nay phai dung detector backend that cua DeepFace hoac mot detector that khac duoc chon ro rang.
   - Khong duoc con logic "neu ten file co chu no_face thi fail".

2. Xu ly anti-spoof/liveness cho dung trang thai that
   - Trang thai: da lam bang anti-spoofing cua DeepFace, co the tat bang `DEEPFACE_ANTI_SPOOFING=false`; smoke test local hien mac dinh tat de tranh blocker dependency `torch`.
   - Neu quyet dinh chua lam anti-spoof that trong MVP, can bo phan fake va ghi ro la "tam thoi khong bat anti-spoof".
   - Neu quyet dinh lam anti-spoof that, can co module that va test toi thieu.
   - Tuyet doi khong de module fake luon pass nhung van doc nhu la tinh nang da co.

3. Chuan hoa pipeline embedding that
   - Trang thai: da lam phan code va unit test mock DeepFace.
   - `worker/app/ml/embedder.py` phai wrap `DeepFace.represent()` o mot contract on dinh.
   - Kiem tra format vector, kich thuoc vector, model name, loi import model, loi khong detect duoc mat.
   - Co test mock unit cho cac truong hop thanh cong va that bai.

4. Lam ro preprocessing anh
   - Trang thai: da dua detector backend, align, enforce detection, normalization vao config.
   - Quy dinh ro detector backend nao duoc dung.
   - Quy dinh co align hay khong.
   - Quy dinh co enforce detection hay khong.
   - Neu can crop/resize truoc khi goi DeepFace, can co service ro rang thay vi de ngam trong code.

5. Hieu chinh matching
   - Chon threshold ban dau theo model cu the.
   - Tao bo anh test toi thieu: cung nguoi, khac nguoi, anh loi, anh khong co mat.
   - Chay access check that va ghi lai score de tinh chinh `DEEPFACE_MATCH_THRESHOLD`.
   - Khong chot threshold chi bang cam tinh.

6. Xac nhan worker chay that trong container
   - Rebuild worker image sau khi them dependency.
   - Xac nhan container boot duoc, import duoc DeepFace, khong loi `cv2`, khong loi model dependency.
   - Chay thu `embedding_job` va `access_job` that bang Docker Compose.

7. Lam ro vai tro `storage_service` trong Giai Doan 7
   - Trang thai: da co implement toi thieu cho local `image_path` va da noi vao flow chinh.
   - Neu worker can doc anh tu local path thi file nay phai co implement toi thieu hoac xoa khoi roadmap giai doan nay.
   - Neu chua dung MinIO/upload file that, can ghi ro Giai Doan 7 van doc tu `image_path` local.
   - Khong de service trong trang thai trong ma khong chu thich.

8. Lam ro vai tro `reindex_service` trong Giai Doan 7
   - Trang thai: da co readiness check va thong bao ro rang la chua the reindex that khi DB chua luu source `image_path`.
   - Neu doi model DeepFace, embedding cu se khong con tuong thich.
   - Can quyet dinh co can reindex lai embedding cu ngay trong Giai Doan 7 hay khong.
   - Neu chua can, ghi ro `reindex_service` de danh cho buoc doi model/Qdrant sau.

9. Don dep fake code va fake message con sot
   - Trang thai: da don trong flow worker chinh; van co the con chu "fake" trong ten bien test mock hoac giai doan cu cua docs.
   - Xoa hoac sua cac message/test/docs con ghi "fake detector", "fake anti-spoof", "fake embedding" o nhung noi da chuyen sang pipeline that.
   - Dam bao docs va code khop nhau.

10. Ghi ro gioi han con lai sau khi xong Giai Doan 7
   - Van co the chua co upload file that.
   - Van co the chua co MinIO.
   - Van co the chua co Qdrant.
   - Nhung khong duoc con fake AI trong flow worker chinh.

Thu tu nen lam:

1. Chot model DeepFace, detector backend, align, normalization, threshold ban dau.
2. Thay `detector.py` bang detector that.
3. Quyet dinh anti-spoof: lam that ngay hoac tam tat va ghi ro.
4. Hoan thien `embedder.py` va test unit.
5. Chay flow `embedding_job` that.
6. Chay flow `access_job` that va ghi score.
7. Tinh chinh threshold.
8. Don dep docs, fake message, service placeholder.

File/folder can xem ky trong Giai Doan 7:

```text
worker/app/ml/detector.py
worker/app/ml/anti_spoof.py
worker/app/ml/embedder.py
worker/app/ml/matcher.py
worker/app/services/embedding_service.py
worker/app/services/face_pipeline_service.py
worker/app/services/storage_service.py
worker/app/services/reindex_service.py
worker/app/tasks/embedding_job.py
worker/app/tasks/access_job.py
worker/app/tests/
docs/ai-pipeline.md
docs/api.md
README.md
```

Moc hoan thanh:

- Dang ky employee bang anh that tao duoc embedding that.
- Check access bang anh that tra ve `granted`, `denied` hoac `error` hop ly.
- Khong con detector fake va anti-spoof fake trong flow chinh.
- Threshold duoc thu bang bo anh test toi thieu va co gia tri mac dinh ro rang.
- Worker chay duoc trong Docker Compose voi DeepFace that.
- Docs khong con mo ta nham rang da "xong AI that" khi ben trong van con fake.

## Giai Doan 8: Hoan Thien Deploy Va Van Hanh

Muc tieu: dua project tu MVP local sang moi truong co the van hanh tot hon.

Y nghia cua "xong Giai Doan 8":

- Khong chi chay duoc tren may dev, ma co cach khoi dong, test, backup, theo doi va deploy ro rang.
- Moi service chinh co health check hoac cach kiem tra song/chet.
- Co reverse proxy gom frontend va backend vao mot entrypoint de gan voi deploy that.
- Co backup/restore toi thieu cho PostgreSQL va thu muc file local; neu them MinIO/Qdrant thi phai co ghi chu backup rieng.
- Co CI chay test/build that, khong con workflow placeholder.
- Config dev/prod duoc tach bang bien moi truong; secret khong hard-code trong source.
- Docs van hanh du de nguoi khac clone repo va chay lai flow co ban.

Trang thai repo sau khi code lop van hanh Giai Doan 8:

- `docker-compose.yml` da co `database`, `redis`, `backend`, `worker`, `frontend-user`, `frontend-admin`, `nginx`, `prometheus`, `minio`, `qdrant`.
- `backend` da co `/health` kiem tra database/Redis va `/metrics` cho Prometheus.
- `scripts/test.ps1` da chay backend tests, worker tests va frontend build neu co `npm`.
- `.github/workflows/ci.yml` da chay backend tests, worker tests, frontend builds va Docker build checks.
- `nginx/nginx.conf`, `monitoring/prometheus/prometheus.yml`, `scripts/dev.ps1`, `scripts/backup.ps1`, `docs/deployment.md`, `docs/monitoring.md`, `docs/backup.md`, `docs/cicd.md` da co noi dung van hanh toi thieu.
- Helm chart `helm/deepface-access` da co `Chart.yaml`, `values.yaml`, configmap, deployments/services, optional MinIO/Qdrant va ingress.
- `backend/app/config/minio.py`, `backend/app/config/qdrant.py`, `worker/app/config/minio.py`, `worker/app/config/qdrant.py` da co config toi thieu.
- MinIO va Qdrant da co service/config, nhung upload flow that va vector search Qdrant chua noi vao flow chinh.

Nguyen tac lam Giai Doan 8:

- Lam phan van hanh theo tung lop, khong nhay thang len Kubernetes khi local deploy chua on.
- Moi phan them vao phai co lenh test nhanh.
- Secret chi nam trong `.env`, GitHub Secrets, Kubernetes Secret hoac file example; khong commit secret that.
- Neu them service nang nhu MinIO/Qdrant/Grafana, phai ghi ro vi sao can va flow nao dang dung no.
- Neu chua noi MinIO/Qdrant vao flow that, chi them config/placeholder co chu thich ro, khong viet docs lam nhu da production-ready.

Thu tu nen lam:

1. Chuan hoa config va health check.
2. Hoan thien script dev/test/seed/backup.
3. Them nginx reverse proxy cho local/prod-like compose.
4. Hoan thien CI test/build.
5. Them monitoring toi thieu.
6. Them backup/restore toi thieu.
7. Quyet dinh pham vi MinIO cho upload/file storage.
8. Quyet dinh pham vi Qdrant cho vector search.
9. Hoan thien Helm chart sau khi compose va config da ro.
10. Cap nhat docs van hanh va README.

### 8.1 Chuan Hoa Config Va Health Check

Muc tieu: moi service chinh co config ro rang va co cach kiem tra song/chet.

Viec can lam:

- Mo rong `.env.example` cho cac bien Giai Doan 8:
  - `APP_ENV`
  - `BACKEND_CORS_ORIGINS`
  - `POSTGRES_*`
  - `REDIS_URL`
  - `MINIO_*`
  - `QDRANT_*`
  - `PROMETHEUS_*` neu can
- Doi `docker-compose.yml` de doc bien moi truong tu `.env` thay vi hard-code qua nhieu noi.
- Them `healthcheck` cho cac service Docker neu hop ly:
  - PostgreSQL: `pg_isready`
  - Redis: `redis-cli ping`
  - Backend: `GET /health`
  - Frontend/nginx: request HTTP toi root
- Can nhac them endpoint health cho worker, vi worker la process nen nen co mot trong hai cach:
  - healthcheck container bang process command/log/Redis ping
  - hoac worker ghi heartbeat vao Redis de backend/monitoring doc sau
- Backend `/health` nen tra ve trang thai database va co the them Redis neu backend phu thuoc Redis de queue job.

File/folder can sua:

```text
.env.example
docker-compose.yml
backend/app/main.py
backend/app/db/health.py
backend/app/config/redis.py
worker/app/main.py
worker/app/config/redis.py
docs/deployment.md
```

Moc hoan thanh:

- `docker compose up --build` van chay duoc.
- `docker compose ps` hien health hop ly cho database/redis/backend.
- `GET http://localhost:8000/health` tra ve trang thai du de debug.

### 8.2 Script Dev, Test, Seed, Backup

Muc tieu: co lenh lap lai duoc cho cac viec van hanh thuong gap.

Viec can lam:

- Hoan thien `scripts/dev.ps1` de chay local stack, vi du:
  - build/up compose
  - init database
  - seed tai khoan demo neu can
- Giu `scripts/test.ps1` lam lenh test tong hop, nhung can dam bao no fail ro rang khi backend/worker/frontend build loi.
- Mo rong `scripts/seed.ps1` neu can truyen bien moi truong seed.
- Viet `scripts/backup.ps1` toi thieu:
  - tao thu muc backup theo timestamp
  - dump PostgreSQL bang `pg_dump` qua Docker Compose
  - copy/nen thu muc `data/` neu dang dung local file storage
  - ghi file manifest nho ve thoi gian backup va service version neu co
- Tao restore notes ro rang trong docs, co the chua can script restore day du ngay buoc dau.

File/folder can sua:

```text
scripts/dev.ps1
scripts/test.ps1
scripts/seed.ps1
scripts/backup.ps1
backup/README.md
docs/backup.md
```

Moc hoan thanh:

- `.\scripts\test.ps1` chay duoc.
- `.\scripts\backup.ps1` tao duoc file dump database va ban sao file local.
- Docs ghi ro restore database bang lenh nao.

### 8.3 Nginx Reverse Proxy

Muc tieu: co mot entrypoint HTTP de route toi backend va frontend, gan voi cach deploy that hon.

Viec can lam:

- Viet `nginx/nginx.conf` de proxy:
  - `/api/` hoac `/backend/` toi backend
  - `/docs` va `/openapi.json` toi backend neu muon giu Swagger
  - `/admin/` toi frontend admin
  - `/` toi frontend user
- Quyet dinh co doi frontend `VITE_API_BASE_URL` sang duong dan relative qua nginx khong.
- Them service `nginx` vao `docker-compose.yml` hoac tao `docker-compose.prod.yml` neu muon tach dev/prod-like.
- Them healthcheck cho nginx.
- Ghi ro port public, vi du `http://localhost:8080`.

File/folder can sua:

```text
nginx/nginx.conf
docker-compose.yml
frontend/user/src/api/client.ts
frontend/admin/src/api/client.ts
docs/deployment.md
README.md
```

Moc hoan thanh:

- Mo user app qua nginx duoc.
- Mo admin app qua nginx duoc.
- Frontend goi backend qua nginx duoc.
- Swagger/backend health van truy cap duoc theo route da chon.

### 8.4 CI/CD

Muc tieu: moi push/pull request co test va build that.

Viec can lam:

- Thay `.github/workflows/ci.yml` placeholder bang job that:
  - checkout code
  - setup Python
  - install backend requirements
  - chay backend tests
  - install worker requirements
  - chay worker tests
  - setup Node
  - `npm ci` va `npm run build` cho `frontend/user`
  - `npm ci` va `npm run build` cho `frontend/admin`
- Can nhac Docker build check:
  - build backend image
  - build worker image
  - build frontend images
- Neu DeepFace dependency qua nang cho CI, co the giu unit test mock DeepFace va chi build image worker; smoke test DeepFace that de manual hoac nightly sau.
- Them cache pip/npm neu can tang toc.

File/folder can sua:

```text
.github/workflows/ci.yml
docs/cicd.md
scripts/test.ps1
```

Moc hoan thanh:

- CI khong con job placeholder.
- Pull request fail neu backend/worker test fail hoac frontend build fail.
- Docs ghi ro CI dang test cai gi va chua test cai gi.

### 8.5 Monitoring Va Logging

Muc tieu: biet service con song khong va co dau hieu loi trong flow queue/AI/database khong.

Viec can lam:

- Viet `monitoring/prometheus/prometheus.yml` de scrape backend neu backend co metrics.
- Them endpoint `/metrics` cho backend neu chon Prometheus.
  - Co the dung `prometheus-fastapi-instrumentator` hoac tu viet metric toi thieu.
- Can nhac metric toi thieu:
  - request count/latency cua backend
  - health database/redis
  - so access log theo status
  - queue length cua `embedding_jobs` va `access_jobs`
  - worker job success/error count neu co cach expose
- Neu chua lam Grafana, docs phai ghi ro Giai Doan 8 moi co Prometheus config truoc.
- Chuan hoa logging:
  - backend log request/error
  - worker log job_id, queue_name, log_id/employee_id, status
  - khong log secret/token

File/folder can sua:

```text
backend/requirements.txt
backend/app/main.py
backend/app/api/admin.py
monitoring/prometheus/prometheus.yml
docker-compose.yml
docs/monitoring.md
```

Moc hoan thanh:

- Prometheus container chay duoc neu duoc them vao compose.
- Truy cap duoc Prometheus UI hoac endpoint metrics.
- Co cach xem queue length va loi worker khi debug.

### 8.6 Backup Va Restore

Muc tieu: mat container khong dong nghia mat du lieu.

Viec can lam:

- Backup PostgreSQL:
  - dump database bang `pg_dump`
  - dat ten file co timestamp
  - ghi restore command bang `psql` hoac `pg_restore`
- Backup local file storage:
  - nen/copy thu muc `data/`
  - ghi ro thu muc nao la smoke data, thu muc nao la upload production neu sau nay them upload
- Neu them MinIO:
  - dung `mc mirror` hoac export bucket
  - docs ghi ro bucket nao can backup
- Neu them Qdrant:
  - dung snapshot Qdrant hoac backup volume
  - docs ghi ro vector co the rebuild tu PostgreSQL hay khong
- Them chinh sach retention don gian, vi du giu N backup gan nhat.

File/folder can sua:

```text
scripts/backup.ps1
backup/README.md
docs/backup.md
docker-compose.yml
```

Moc hoan thanh:

- Co it nhat mot backup database tao duoc tu script.
- Co restore notes da test bang database rong hoac database dev.
- Docs noi ro phan nao duoc backup, phan nao chua.

### 8.7 MinIO Cho File Anh

Muc tieu: thay dan viec nhap/local `image_path` bang object storage co the deploy that.

Can quyet dinh pham vi:

- Neu chi lam van hanh toi thieu: them MinIO service/config/docs, chua doi flow upload.
- Neu lam day du: backend co upload API, luu file vao MinIO, worker doc file tu MinIO hoac tai ve temporary file truoc khi goi DeepFace.

Viec can lam neu lam day du:

- Them MinIO vao `docker-compose.yml`:
  - service `minio`
  - service tao bucket neu can
  - volume rieng cho MinIO
- Implement config trong:
  - `backend/app/config/minio.py`
  - `worker/app/config/minio.py`
- Hoan thien `backend/app/services/storage_service.py`:
  - validate file type/size
  - upload file
  - tra ve object key hoac URL noi bo
- Them API upload neu can:
  - upload anh employee
  - upload snapshot access
- Cap nhat worker `storage_service.py` de resolve object key thanh local temp file.
- Cap nhat frontend de upload file that thay vi nhap `image_path`.

File/folder can sua:

```text
docker-compose.yml
.env.example
backend/requirements.txt
backend/app/config/minio.py
backend/app/services/storage_service.py
backend/app/api/employees.py
backend/app/api/access.py
worker/requirements.txt
worker/app/config/minio.py
worker/app/services/storage_service.py
frontend/user/src/pages/AccessPage.tsx
frontend/admin/src/pages/EmployeePage.tsx
docs/api.md
docs/deployment.md
```

Moc hoan thanh neu lam day du:

- Admin upload anh employee qua UI/API.
- Worker tao embedding tu file trong MinIO.
- User upload snapshot access qua UI/API.
- Backup docs ghi ro MinIO bucket can backup.

### 8.8 Qdrant Cho Vector Search

Muc tieu: khi so luong embedding tang, search vector khong con phu thuoc quet JSONB trong PostgreSQL.

Can quyet dinh pham vi:

- Neu MVP con nho, co the chi them docs/config de danh cho sau.
- Neu lam production-ready hon, worker phai ghi vector vao Qdrant va access matching phai query Qdrant.

Viec can lam neu lam day du:

- Them Qdrant vao `docker-compose.yml`.
- Implement config trong:
  - `backend/app/config/qdrant.py` neu backend can admin/status
  - `worker/app/config/qdrant.py`
- Tao collection theo `model_name`, vector size va distance metric.
- Khi tao employee embedding:
  - van luu metadata trong PostgreSQL
  - upsert vector vao Qdrant voi payload `employee_id`, `embedding_id`, `model_name`, `status`
- Khi check access:
  - tao embedding snapshot
  - query Qdrant top_k
  - verify employee active trong PostgreSQL
  - apply threshold
- Hoan thien `reindex_service.py`:
  - doc embedding PostgreSQL
  - rebuild collection Qdrant
  - hoac ghi ro khong the rebuild neu thieu source image/vector phu hop

File/folder can sua:

```text
docker-compose.yml
.env.example
worker/requirements.txt
worker/app/config/qdrant.py
worker/app/services/embedding_service.py
worker/app/services/face_pipeline_service.py
worker/app/services/reindex_service.py
worker/app/tasks/reindex_job.py
docs/ai-pipeline.md
docs/db-schema.md
docs/deployment.md
```

Moc hoan thanh neu lam day du:

- Qdrant collection duoc tao tu dong hoac bang script ro rang.
- Embedding moi duoc upsert vao Qdrant.
- Access check dung Qdrant de lay candidate.
- Co cach reindex khi doi model/threshold/collection.

### 8.9 Helm Va Kubernetes

Muc tieu: co chart du de deploy len Kubernetes sau khi compose flow da ro.

Viec can lam:

- Hoan thien `helm/deepface-access/values.yaml`:
  - image repository/tag cho tung service
  - env config
  - resources request/limit
  - persistence cho PostgreSQL/Redis/MinIO/Qdrant neu deploy trong cluster
  - ingress host/path
- Hoan thien cac template:
  - backend deployment/service
  - worker deployment
  - frontend user/admin deployment/service
  - database/redis deployment hoac ghi ro dung managed service ben ngoai
  - nginx/ingress
  - secret example
- Khong commit secret that trong chart.
- Them docs cach render/lint chart:
  - `helm lint`
  - `helm template`
  - `helm upgrade --install`

File/folder can sua:

```text
helm/deepface-access/Chart.yaml
helm/deepface-access/values.yaml
helm/deepface-access/templates/
docs/deployment.md
```

Moc hoan thanh:

- `helm lint helm/deepface-access` pass.
- `helm template helm/deepface-access` render duoc manifest hop le.
- Docs ghi ro phan nao dung internal service, phan nao nen thay bang managed service production.

### 8.10 Docs Van Hanh Va Cap Nhat README

Muc tieu: nguoi moi doc repo biet cach chay, test, backup, monitor va deploy.

Docs can cap nhat:

```text
README.md
docs/deployment.md
docs/monitoring.md
docs/backup.md
docs/cicd.md
docs/api.md
docs/ai-pipeline.md
docs/db-schema.md
```

Noi dung can co:

- Cach chay local dev.
- Cach chay prod-like qua nginx.
- Cach seed database.
- Cach chay test.
- Cach backup/restore.
- Cach xem logs va monitoring.
- Bien moi truong quan trong.
- Gioi han con lai:
  - anti-spoof co bat hay chua
  - MinIO da noi flow that hay moi config
  - Qdrant da dung matching that hay moi placeholder
  - Helm da test tren cluster that hay moi render/lint

Moc hoan thanh toan Giai Doan 8:

- `docker compose up --build` chay duoc core app.
- Neu them nginx, truy cap app qua nginx duoc.
- `.\scripts\test.ps1` chay duoc tren may dev.
- CI GitHub Actions chay test/build that.
- `.\scripts\backup.ps1` tao backup toi thieu.
- Co docs restore database.
- Co monitoring toi thieu hoac docs ghi ro phan monitoring nao chua bat.
- Secret that khong nam trong source code.
- README va docs khop voi code/config hien tai.

### Ghi Chu Bo Sung Sau Khi Hoan Thanh Lop Nen Giai Doan 8

Nhung phan duoi day khong con la blocker cho lop van hanh co ban, nhung nen duoc ghi nho de bo sung context o vong sau:

1. Worker health va observability van o muc toi thieu
   - Hien worker healthcheck moi ping Redis; chua co worker heartbeat, worker `/metrics`, hay job success/error metric rieng.
   - Neu muon van hanh lau dai hon, nen them metric cho:
     - so job thanh cong/that bai
     - thoi gian xu ly embedding/access job
     - so lan queue retry hoac poison job neu ve sau co retry

2. Prometheus da co, nhung Grafana va alerting chua co
   - Hien docs da ghi ro chua co Grafana dashboard va alert rule.
   - Ve sau nen bo sung:
     - dashboard backend health/request/queue length
     - canh bao backend 5xx, Redis down, database down, queue tang bat thuong

3. MinIO moi o muc service/config, chua noi vao flow that
   - Backend van nhan `image_path` thay vi upload file.
   - Worker van resolve local path thay vi object key hoac temporary file tu MinIO.
   - Khi quay lai phan nay, nho bo sung:
     - bucket bootstrap/init
     - upload API
     - validate type/size
     - cleanup file tam neu worker tai object ve local

4. Qdrant moi o muc service/config, chua thay flow matching chinh
   - Hien access matching van dua vao vector JSONB trong PostgreSQL.
   - Khi quay lai phan nay, nho chot:
     - collection schema theo `model_name`
     - upsert lifecycle khi employee inactive/delete
     - reindex flow khi doi model DeepFace
     - chinh sach rebuild neu PostgreSQL la source of truth

5. Backup da co muc toi thieu, nhung restore chua duoc tu dong hoa
   - Da co dump PostgreSQL va archive `data/`.
   - Chua co restore script hoan chinh, chua co scheduler, chua co retention policy theo ngay/tuan/thang.
   - Neu bat dau dung MinIO/Qdrant that, backup policy can mo rong cho 2 service nay.

6. Helm chart da render/lint duoc, nhung chua xac nhan tren cluster that
   - Hien chart phu hop baseline dev/staging.
   - Ve sau nen test tren cluster that voi:
     - ingress
     - PVC
     - secret injection
     - image registry that
     - resource requests/limits

7. Frontend van hanh da on, nhung flow production chua xong
   - Chua co upload file that.
   - Chua co Playwright E2E.
   - Camera flow van thieu update/delete day du theo ghi chu cu cua roadmap.

8. Docker Compose hien uu tien local/prod-like, chua tach ro profile theo muc dich
   - Hien tat ca service nam chung trong `docker-compose.yml`.
   - Neu stack tiep tuc lon hon, can can nhac:
     - tach compose override cho dev/prod-like
     - dung `profiles` cho `prometheus`, `minio`, `qdrant`
     - giam thoi gian boot cho may dev chi can core app

9. Worker image DeepFace build rat nang
   - Build worker that hien ton nhieu thoi gian va dung luong do TensorFlow/DeepFace.
   - Ve sau nen xem xet:
     - pin dependency ky hon
     - toi uu Docker layer/cache
     - tach smoke build va runtime build neu CI qua cham

10. Can tiep tuc cap nhat docs khi noi MinIO/Qdrant vao flow chinh
   - `README.md`
   - `docs/api.md`
   - `docs/ai-pipeline.md`
   - `docs/db-schema.md`
   - `docs/deployment.md`
   - `docs/backup.md`

11. Chien luoc migration schema production chua duoc chot
   - Hien repo van nghieng ve `init_db`/metadata create cho dev nhanh.
   - Neu bat dau deploy moi truong dung hon, can chot:
     - co dua Alembic vao quy trinh hay khong
     - ai chay migration, chay luc nao
     - rollback schema se xu ly the nao

12. Security hardening cho moi truong that chua duoc ghi thanh checklist rieng
   - Hien roadmap da co nguyen tac khong commit secret that, nhung chua tach thanh checklist production.
   - Ve sau nen bo sung ro:
     - TLS/HTTPS o ingress hay reverse proxy
     - rotate secret va doi credential mac dinh
     - CORS origin production
     - non-root user, image scanning, dependency audit neu can

## Checklist Truoc Khi Qua Giai Doan Moi

Truoc khi chuyen sang giai doan tiep theo, tu hoi:

- Service hien tai co chay duoc khong?
- Co cach test nhanh khong?
- Loi co hien ra de debug duoc khong?
- Docs lien quan co can cap nhat khong?
- Co phan nao dang fake/stub can ghi chu lai khong?

Neu cau tra loi cho cac cau tren chua ro, nen xu ly truoc khi them tinh nang moi.

## Thu Tu Hoi Codex Sau Nay
Neu muon review:

```text
Hay kiem tra Giai Doan 8 trong docs/implementation-roadmap.md.
So sanh repo hien tai voi roadmap, xem thieu file nao, file nao code chua du function, service nao chua noi duoc, can update docs nao, roi chay test/command kiem tra neu co the, hay kiem tra mot luot giup toi nhe. Ngoai ra, sau khi kiem tra xong het mot luot, hay doc lai ca repo de xem co file quen chua cap nhat khong nhe, tat ca cac file.
Chu y: chi sua cac loi nho ro rang, con loi lon thi bao toi truoc, neu loi nho va chac chan dung huong thi sua truc tiep luon.
Sau khi kiem tra xong, co the cho toi biet tu buoc 1 den buoc 7 da du trong repo chua, con thieu file, folder gi nua khong, so rang se co file thieu code hay structure con thieu gi do, hay readme chua duoc cap nhat. Sau do, cho toi biet tat ca nhung thay doi cua ban va noi tong quan nhung thay doi do
```

## Tom Tat Lo Trinh

```text
1. Giai Doan 1: docker-compose, backend /health, frontend rong, worker rong chay duoc
2. Giai Doan 2: database schema toi thieu
3. Giai Doan 3: backend API cot loi
4. Giai Doan 4: Redis queue giua backend va worker
5. Giai Doan 5: worker fake AI de test end-to-end
6. Giai Doan 6: frontend dung API
7. Giai Doan 7: DeepFace that trong worker
8. Giai Doan 8: deploy / monitoring / backup
```

## Context con thieu can duoc bo sung sau khi 8 giai doan hoan thanh
giai doan 6: thieu update/delete o camera, nen check ki va nen them sau nay
Giai Doan 7: con thieu spoofing
- quay lai test anti-spoof that
- bat `DEEPFACE_ANTI_SPOOFING=true`
- cai them dependency neu can, co the la `torch`
- rebuild worker
- test bo anh spoof/anh that
- danh gia do on dinh va toc do
- quyet dinh giu anti-spoof trong MVP hay tam tat
