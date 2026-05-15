# Important Follow-up Fixes

Tai lieu nay ghi lai cac van de quan trong nhung chua nen lam lan man ngay. Muc tieu la giup nhom biet sau nay can sua gi, sua o dau, va bam vao tai lieu/file nao.

## Tong Quan Uu Tien

Neu thoi gian it, nen uu tien theo thu tu:

1. Chuan hoa pipeline data/upload qua MinIO/S3.
2. Upload anh that thay vi nhap `image_path`.
3. Chan quyen `admin` / `user` tren backend.
4. Noi Qdrant vao flow matching that.
5. Theo doi trang thai embedding job.
6. Luu source image cua embedding de reindex ve sau.
7. Sua default anti-spoof cho khop docs.
8. Bo sung update/delete camera.
9. Kiem tra/sua Helm ingress `/api`.
10. Doi frontend Dockerfile sang serve static build neu can demo deploy nghiem tuc.
11. Chay smoke test DeepFace that trong container.

## 1. Chuan Hoa Pipeline Data/Upload Qua MinIO/S3

### Van De

Hien tai repo da co MinIO va Qdrant trong `docker-compose.yml`, `.env.example` va config code, nhung chung moi o muc service/config baseline. MinIO chua duoc noi vao upload flow that, Qdrant chua duoc noi vao matching flow that.

Noi cach khac:

```text
MinIO: co service, chua luu anh that tu backend/frontend
Qdrant: co service, chua duoc dung de search vector
```

Day la mot phan can fix vi de bai co nhac toi object storage va vector database. Neu chi co service nhung flow chinh khong dung, khi demo can noi ro day moi la baseline, chua phai tich hop day du.

### Pipeline Mong Muon Sau Nay

```text
Frontend upload anh
       |
       v
Backend nhan file
       |
       v
Backend luu anh vao MinIO/S3
       |
       v
Backend luu object_key vao PostgreSQL
       |
       v
Worker lay anh tu MinIO/S3
       |
       v
DeepFace xu ly
       |
       v
PostgreSQL luu embedding / access log
```

Trong pipeline nay:

- MinIO/S3 luu file anh that.
- PostgreSQL luu metadata, object key, employee, camera, access log, embedding metadata.
- Worker khong doc local path nua, ma tai anh tu object key ve temp file trong container.
- Qdrant sau nay nen luu/search vector embedding, con PostgreSQL van la source of truth.

### Dang Nam O Dau

- `docker-compose.yml`
- `.env.example`
- `backend/app/config/minio.py`
- `backend/app/config/qdrant.py`
- `backend/app/services/storage_service.py`
- `backend/app/api/employees.py`
- `backend/app/api/access.py`
- `backend/app/queues/embedding_queue.py`
- `backend/app/queues/access_queue.py`
- `backend/app/models/face_embedding.py`
- `backend/app/models/access_log.py`
- `worker/app/config/minio.py`
- `worker/app/config/qdrant.py`
- `worker/app/services/storage_service.py`
- `worker/app/services/embedding_service.py`
- `worker/app/services/face_pipeline_service.py`
- `frontend/admin/src/components/EmployeeTable.tsx`
- `frontend/user/src/pages/AccessPage.tsx`
- `docs/architecture.md`
- `docs/api.md`
- `docs/ai-pipeline.md`
- `docs/db-schema.md`
- `docs/deployment.md`
- `docs/backup.md`

### Nen Sua Nhu The Nao

Lam theo cac buoc nho:

```text
[ ] Backend storage service upload file vao MinIO/S3
[ ] Backend upload API cho employee face image
[ ] Backend upload API cho access snapshot
[ ] DB luu object_key thay vi local image_path
[ ] Redis job dung image_key/object_key
[ ] Worker tai anh tu MinIO/S3 ve temp file
[ ] Worker cleanup temp file sau khi DeepFace xu ly
[ ] Frontend doi input path thanh file upload
[ ] Docs ghi ro MinIO/S3 la noi luu anh that
[ ] Backup docs bo sung backup MinIO bucket neu self-host MinIO
```

### Ghi Chu

Neu chua kip lam day du, khi demo nen noi ro:

```text
Hien tai MinIO va Qdrant da co service/config baseline.
Flow chinh hien van dung image_path local va PostgreSQL JSON vector.
Huong mo rong tiep theo la noi upload vao MinIO va matching vao Qdrant.
```

## 2. Upload Anh That Thay Vi Nhap `image_path`

### Van De

Hien tai admin/user phai nhap duong dan anh thu cong, vi du:

```text
/app/data/smoke/employee_a_ref.jpg
```

Flow nay dung cho MVP/dev, nhung khi demo nhu mot he thong that thi chua tu nhien. De deploy dung hon, user/admin nen upload file anh, backend luu anh vao MinIO/S3, worker doc anh tu do.

### Dang Nam O Dau

- `backend/app/api/employees.py`
- `backend/app/api/access.py`
- `backend/app/schemas/employee.py`
- `backend/app/schemas/access.py`
- `backend/app/queues/embedding_queue.py`
- `backend/app/queues/access_queue.py`
- `worker/app/services/storage_service.py`
- `worker/app/services/embedding_service.py`
- `worker/app/services/face_pipeline_service.py`
- `frontend/admin/src/components/EmployeeTable.tsx`
- `frontend/user/src/pages/AccessPage.tsx`
- `docs/api.md`
- `docs/ai-pipeline.md`
- `docs/db-schema.md`
- `docs/deployment.md`

### Nen Sua Nhu The Nao

Them upload API:

```text
POST /employees/{id}/face-image
POST /access/check-image
```

Backend nhan `multipart/form-data`, validate file, upload vao MinIO, roi push Redis job bang object key thay vi local path.

Payload Redis nen chuyen tu:

```json
{
  "image_path": "/app/data/smoke/employee_a_ref.jpg"
}
```

sang:

```json
{
  "image_key": "employees/1/reference/<uuid>.jpg"
}
```

Worker tai object tu MinIO ve temp file, chay DeepFace, sau do xoa temp file.

### Ghi Chu

MinIO da co service/config trong repo, nhung chua noi vao flow that.

## 3. Role `admin` / `user` Chua Duoc Chan That

### Van De

Backend hien kiem tra nguoi dung da dang nhap chua, nhung chua chan ro endpoint nao chi danh cho admin. Tai khoan co role `user` van co the goi mot so API quan tri neu co token hop le.

Dung ra:

```text
admin: quan ly employee, camera, admin status, xem toan bo logs
user: check access, xem profile/history phu hop
```

### Dang Nam O Dau

- `backend/app/core/deps.py`
- `backend/app/models/user.py`
- `backend/app/api/admin.py`
- `backend/app/api/employees.py`
- `backend/app/api/cameras.py`
- `backend/app/api/logs.py`
- `backend/app/api/access.py`
- `backend/app/tests/test_auth.py`
- `backend/app/tests/test_employees.py`
- `backend/app/tests/test_cameras.py`
- `backend/app/tests/test_logs.py`

### Nen Sua Nhu The Nao

Them dependency trong `backend/app/core/deps.py`, vi du:

```python
def require_admin_user(current_user: CurrentUser) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user
```

Sau do dung cho cac endpoint quan tri:

```text
/admin/status
/employees/*
/cameras/*
```

Them test:

```text
user role goi POST /employees -> 403
user role goi POST /cameras -> 403
user role goi GET /admin/status -> 403
admin role van goi duoc -> 200/201
```

### Ghi Chu

Day la loi phan quyen co ban, khac voi MinIO/Qdrant. MinIO/Qdrant la luu tru va vector search; role la bao mat API.

## 4. Qdrant Chua Duoc Dung Trong Matching That

### Van De

Repo da co Qdrant service/config, nhung access matching hien van lay vector tu PostgreSQL JSON/JSONB roi so sanh cosine trong worker.

Neu de bai yeu cau vector database, can bien Qdrant tu "co service" thanh "duoc dung trong flow".

### Dang Nam O Dau

- `docker-compose.yml`
- `.env.example`
- `backend/app/config/qdrant.py`
- `worker/app/config/qdrant.py`
- `worker/app/services/embedding_service.py`
- `worker/app/services/face_pipeline_service.py`
- `worker/app/services/reindex_service.py`
- `worker/app/ml/matcher.py`
- `docs/ai-pipeline.md`
- `docs/db-schema.md`
- `docs/deployment.md`

### Nen Sua Nhu The Nao

Khi tao employee embedding:

```text
DeepFace vector
  -> luu metadata/vector vao PostgreSQL
  -> upsert vector vao Qdrant
```

Khi check access:

```text
DeepFace query vector
  -> query Qdrant top_k
  -> verify employee active trong PostgreSQL
  -> apply threshold
  -> update access_logs
```

Can them service Qdrant client trong worker, vi du:

```text
worker/app/services/vector_store_service.py
```

### Ghi Chu

Co the van giu PostgreSQL la source of truth, Qdrant la search index.

## 5. Embedding Job Loi Khong Co Trang Thai Cho Admin

### Van De

Access job co `access_logs.status = processing/granted/denied/error`. Nhung embedding job neu loi thi worker chi log exception; admin khong biet job tao embedding thanh cong hay that bai.

### Dang Nam O Dau

- `backend/app/api/employees.py`
- `backend/app/queues/embedding_queue.py`
- `worker/app/tasks/embedding_job.py`
- `worker/app/services/embedding_service.py`
- `frontend/admin/src/components/EmployeeTable.tsx`
- `frontend/admin/src/pages/EmployeePage.tsx`

### Nen Sua Nhu The Nao

Cach nhe:

Them vao `employees`:

```text
embedding_status: none/pending/success/error
embedding_error: nullable text
```

Khi queue job:

```text
embedding_status = pending
```

Worker thanh cong:

```text
embedding_status = success
embedding_error = null
```

Worker loi:

```text
embedding_status = error
embedding_error = message
```

Cach day du hon:

```text
Them bang embedding_jobs
```

### Ghi Chu

Neu can demo nhanh, cach them cot vao `employees` la de hieu nhat.

## 6. Chua Luu Source Image Cua Embedding

### Van De

Bang `face_embeddings` hien luu vector va `model_name`, nhung khong luu anh goc da tao ra vector. Vi vay neu sau nay doi model DeepFace hoac can reindex Qdrant, he thong khong biet lay anh nao de tao lai embedding.

### Dang Nam O Dau

- `backend/app/models/face_embedding.py`
- `worker/app/db/schema.py`
- `worker/app/services/embedding_service.py`
- `worker/app/services/reindex_service.py`
- `docs/db-schema.md`
- `docs/ai-pipeline.md`

### Nen Sua Nhu The Nao

Neu van dung path local:

```text
face_embeddings.source_image_path
```

Neu chuyen sang MinIO:

```text
face_embeddings.source_image_key
```

Sau khi worker tao embedding thanh cong, luu source nay cung record embedding.

### Ghi Chu

Nen lam chung voi upload MinIO de tranh doi schema hai lan.

## 7. Default Anti-spoof Khong Khop Docs

### Van De

Docs, `.env.example`, va `docker-compose.yml` deu noi mac dinh:

```text
DEEPFACE_ANTI_SPOOFING=false
```

Nhung trong code worker:

```text
worker/app/config/settings.py
```

default hien la `true` neu chay worker ngoai Docker Compose.

### Dang Nam O Dau

- `worker/app/config/settings.py`
- `.env.example`
- `docker-compose.yml`
- `docs/ai-pipeline.md`
- `docs/implementation-roadmap.md`

### Nen Sua Nhu The Nao

Doi default trong `worker/app/config/settings.py` thanh:

```python
deepface_anti_spoofing: bool = _get_bool("DEEPFACE_ANTI_SPOOFING", False)
```

Them/sua test neu can de confirm default.

## 8. Camera Thieu Update/Delete

### Van De

Backend/frontend hien co:

```text
GET /cameras
POST /cameras
```

Nhung chua co update/delete. Roadmap da ghi day la phan con thieu cua Giai Doan 6.

### Dang Nam O Dau

- `backend/app/api/cameras.py`
- `backend/app/services/camera_service.py`
- `backend/app/repositories/camera_repository.py`
- `backend/app/schemas/camera.py`
- `backend/app/tests/test_cameras.py`
- `frontend/admin/src/api/cameras.ts`
- `frontend/admin/src/pages/CameraPage.tsx`
- `frontend/admin/src/components/CameraForm.tsx`

### Nen Sua Nhu The Nao

Them:

```text
GET /cameras/{id}
PUT /cameras/{id}
DELETE /cameras/{id}
```

Delete nen soft-delete bang:

```text
status = inactive
```

Frontend admin them edit/disable camera tuong tu employee.

## 9. Helm Ingress `/api` Co The Khong Strip Prefix

### Van De

Nginx local route:

```nginx
location /api/ {
    proxy_pass http://backend/;
}
```

Cach nay strip `/api/` truoc khi goi backend.

Nhung Helm ingress hien route `/api` thang ve backend. Backend khong co route `/api/auth`, ma co `/auth`.

### Dang Nam O Dau

- `helm/deepface-access/templates/nginx-ingress.yaml`
- `helm/deepface-access/values.yaml`
- `nginx/nginx.conf`
- `docs/deployment.md`

### Nen Sua Nhu The Nao

Neu dung nginx ingress, them rewrite annotation phu hop, hoac doi frontend trong Helm khong goi `/api`.

Can test:

```text
GET https://host/api/health
POST https://host/api/auth/login
```

## 10. Frontend Dockerfile Dang Chay Dev Server

### Van De

`frontend/user/Dockerfile` va `frontend/admin/Dockerfile` hien chay:

```text
npm run dev
```

Dieu nay on cho local demo, nhung production image nen build static va serve bang nginx/caddy.

### Dang Nam O Dau

- `frontend/user/Dockerfile`
- `frontend/admin/Dockerfile`
- `docker-compose.yml`
- `.github/workflows/ci.yml`
- `docs/deployment.md`

### Nen Sua Nhu The Nao

Dung multi-stage Dockerfile:

```text
node build stage -> nginx runtime stage
```

Neu chua lam, docs nen ghi ro frontend container hien la dev/prod-like local, khong phai production-hardened image.

## 11. Can Smoke Test DeepFace That Trong Container

### Van De

Unit test worker hien mock DeepFace. Dieu nay tot cho CI nhanh, nhung chua chung minh model weight tai duoc va DeepFace chay that trong container.

### Dang Nam O Dau

- `data/smoke/`
- `worker/app/tests/`
- `docs/phase6-testing.md`
- `docs/ai-pipeline.md`
- `docs/demo-checklist-bonus.md`

### Nen Sua Nhu The Nao

Tao smoke test manual hoac script rieng:

```text
1. Seed DB.
2. Tao employee A.
3. Queue embedding voi data/smoke/employee_a_ref.jpg.
4. Check access voi employee_a_ok.jpg -> mong doi granted.
5. Check access voi employee_b_ok.jpg -> mong doi denied.
6. Check no_face.jpg -> mong doi error.
7. Neu bat anti-spoof, test spoof_a.jpg.
```

Nen ghi lai score that de chinh:

```text
DEEPFACE_MATCH_THRESHOLD
```

## Ghi Chu Cuoi

Nhung muc tren khong co nghia repo dang hong. Repo hien da co core flow, test, docs va deploy baseline tot cho MVP. Cac muc nay la nhung viec nen lam de he thong:

- giong flow that hon;
- bam de bai hon;
- de demo hon;
- tranh bi hoi vao cac diem co ban nhu upload, phan quyen, object storage, vector database.
