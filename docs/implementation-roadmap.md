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

Tai lieu can cap nhat:  🚩 ĐANG DỪNG TẠI ĐÂY

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

Muc tieu: thay pipeline fake bang model AI that khi flow he thong da on dinh.

Viec can lam:

1. Thay logic trong `worker/app/ml/embedder.py` bang `DeepFace.represent()`.
2. Kiem tra format vector embedding.
3. Dieu chinh threshold matching.
4. Kiem tra toc do xu ly.
5. Sau do moi tich hop Qdrant de search vector tot hon.

Chua nen lam qua som vi AI that se lam debug he thong kho hon.

Dieu can quyet dinh truoc khi thay AI that:

- Model nao dung cho embedding.
- Kich thuoc vector la bao nhieu.
- Threshold matching ban dau.
- Anh dau vao can crop/resize nhu the nao.
- Luu vector trong PostgreSQL truoc hay day sang Qdrant ngay.

Moc hoan thanh:

- Embedding that tao duoc tu anh upload.
- Matching co ket qua on dinh voi bo anh test nho.
- Worker van khong lam backend bi treo.

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

Khi muon lam tiep, co the hoi theo mau:

```text
Hay bam theo docs/implementation-roadmap.md va lam Giai Doan 1.
```

Hoac:

```text
Hay xem Giai Doan 3 trong implementation-roadmap va tao backend API cho employees truoc.
```

Neu muon review:

```text
Hay review hien tai project dang o dau so voi implementation-roadmap.
```
Muon ket hop lam viec va review sau moi moc:

```text
Hay kiem tra Giai Doan 1 trong docs/implementation-roadmap.md.
So sanh repo hien tai voi roadmap, xem thieu file nao, service nao chua noi duoc,
can update docs nao, roi chay test/command kiem tra neu co the.
Chi sua cac loi nho ro rang, con loi lon thi bao toi truoc.
Neu loi nho va chac chan dung huong thi sua truc tiep luon.
```

## Tom Tat Lo Trinh

```text
1. docker-compose chay duoc
2. backend /health chay duoc
3. frontend rong chay duoc
4. database schema
5. backend API
6. Redis queue
7. worker fake AI
8. frontend dung API
9. DeepFace that
10. deploy / monitoring / backup
```

## Buoc Nen Lam Ngay

Neu bat dau code lai tu dau, buoc dau tien nen la:

```text
Viet lai docker-compose.yml toi gian va backend health check.
```

Ly do: khi khung chay duoc, cac phan sau se co diem bam ro rang de phat trien va test.
