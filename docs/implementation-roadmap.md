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

Viec can lam:

- `nginx`: reverse proxy.
- `backup`: backup database va file.
- `monitoring`: Prometheus/Grafana hoac metric can thiet.
- `CI/CD`: test va build tu dong.
- `helm`: deploy Kubernetes.
- `MinIO`: luu file anh theo object storage.
- `Qdrant`: vector search production-ready hon.

Nen lam sau khi core app da chay on dinh.

Moc hoan thanh:

- Co script backup/restore toi thieu.
- Co health check cho cac service chinh.
- Co CI chay test/build.
- Co config deploy tach bien moi truong dev/prod.
- Secret khong nam truc tiep trong source code.

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
Hay kiem tra Giai Doan 7 trong docs/implementation-roadmap.md.
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