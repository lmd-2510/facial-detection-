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
12. Them webcam/camera capture tren frontend user.
13. Bo sung quan ly user va phan quyen admin/user ro rang hon.
14. Chuan hoa Docker image registry theo yeu cau mon hoc.
15. Them script/checklist demo baseline de chung minh cac thanh phan chay that.

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

## 7. Hoan Thien Anti-spoofing/Liveness

### Van De

Repo da co code anti-spoofing trong worker, nhung hien dang de mac dinh tat trong Docker Compose:

```text
DEEPFACE_ANTI_SPOOFING=false
```

Ly do tam tat la anti-spoofing co the can them dependency/model nang, lan dau chay co the tai weight lau, va do on dinh phu thuoc chat luong anh/camera. Neu bat khi chua test ky, flow demo chinh co the bi false reject hoac worker loi dependency.

Ngoai ra docs, `.env.example`, va `docker-compose.yml` deu noi mac dinh la `false`, nhung code worker:

```text
worker/app/config/settings.py
```

co default la `true` neu chay worker ngoai Docker Compose. Can sua de hanh vi local/test/doc khop nhau.

### Dang Nam O Dau

- `worker/app/config/settings.py`
- `worker/app/ml/anti_spoof.py`
- `worker/app/ml/detector.py`
- `worker/app/services/embedding_service.py`
- `worker/app/services/face_pipeline_service.py`
- `worker/app/tests/test_anti_spoof.py`
- `worker/requirements.txt`
- `.env.example`
- `docker-compose.yml`
- `data/smoke/spoof_a.jpg`
- `docs/ai-pipeline.md`
- `docs/implementation-roadmap.md`
- `docs/demo-checklist-bonus.md`

### Trang Thai Hien Tai

- `anti_spoof.py` da wrap `DeepFace.extract_faces(..., anti_spoofing=True)`.
- `require_live_face()` da duoc goi trong flow tao embedding va access check.
- Khi `DEEPFACE_ANTI_SPOOFING=false`, module tra ve pass voi message noi ro anti-spoofing dang tat.
- Unit test hien mock DeepFace nen test contract nhanh, chua chung minh anti-spoof model that chay trong container.
- Smoke test DeepFace gan day moi xac nhan detector/embedding/matching, chua bat anti-spoofing that.

### Nen Sua Nhu The Nao

Lam theo tung buoc nho, khong bat mac dinh ngay:

1. Sua default config cho khop docs:

```python
deepface_anti_spoofing: bool = _get_bool("DEEPFACE_ANTI_SPOOFING", False)
```

2. Them/sua test de confirm:

```text
[ ] Khi khong set env, settings.deepface_anti_spoofing la False
[ ] Khi DEEPFACE_ANTI_SPOOFING=true, anti_spoof.py goi DeepFace voi anti_spoofing=True
[ ] Khi DeepFace tra is_real=false, worker update access log thanh error hoac denied theo quyet dinh ro rang
```

3. Chay thu anti-spoofing bang Docker Compose rieng:

```powershell
$env:DEEPFACE_ANTI_SPOOFING="true"
docker compose up -d --build worker
```

4. Neu worker loi import/dependency, doc log worker roi moi them dependency vao `worker/requirements.txt`. Khong them `torch` hoac dependency nang theo cam tinh neu log chua yeu cau.

5. Chay smoke test rieng:

```text
[ ] employee_a_ref.jpg -> tao embedding pass liveness
[ ] employee_a_ok.jpg -> access pass liveness va co the granted
[ ] employee_b_ok.jpg -> pass liveness nhung denied do khac nguoi
[ ] no_face.jpg -> error do khong co mat
[ ] spoof_a.jpg -> fail liveness neu anh spoof phu hop voi model
```

6. Ghi lai ket qua:

```text
image_name
liveness_status
anti_spoof_score neu co
access_status
match_score neu co
processing_time
dependency/model da tai
```

### Quyet Dinh Trang Thai Sau Khi Test

Sau khi test, chon mot trong hai huong:

```text
Huong A - Bat optional:
DEEPFACE_ANTI_SPOOFING=false mac dinh, docs ghi ro co the bat true khi can demo liveness.

Huong B - Bat mac dinh:
DEEPFACE_ANTI_SPOOFING=true chi khi smoke test that on dinh, toc do chap nhan duoc, va anh that/spoof cho ket qua hop ly.
```

Khuyen nghi hien tai: giu **Huong A** cho den khi co bo anh test that tot hon va da test dependency trong container.

### Moc Hoan Thanh

- Config default khop docs.
- Worker container boot duoc khi `DEEPFACE_ANTI_SPOOFING=true`.
- Anti-spoof model/dependency tai duoc trong container.
- Co smoke result cho anh that, anh khac nguoi, anh khong co mat va anh spoof.
- Docs ghi ro anti-spoof dang optional hay bat mac dinh.
- Demo chinh khong bi phu thuoc vao anti-spoof neu tinh nang nay con chua on dinh.

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

### Trang Thai Da Kiem Tra Gan Day

Smoke test runtime Docker da chay duoc voi bo anh `data/smoke/`:

```text
employee_a_ref.jpg -> tao embedding Facenet512 thanh cong
employee_a_ok.jpg  -> granted, score khoang 0.752256
employee_b_ok.jpg  -> denied, score khoang 0.393336
no_face.jpg        -> error
```

Can dua flow nay vao script hoac checklist chinh thuc de ca nhom lap lai duoc truoc demo.

## 12. Webcam/Camera Capture Tren Frontend User

### Van De

De bai la he thong AI xu ly computer vision, nen demo se thuyet phuc hon neu user co the dung camera/webcam de chup frame that thay vi nhap `image_path` hoac chi upload file.

Hien tai user flow van la:

```text
Nhap image_path -> backend queue access job -> worker xu ly
```

Flow nen co cho demo:

```text
Mo webcam tren User UI
-> chup frame/snapshot
-> gui multipart/form-data len backend
-> backend luu anh vao MinIO/S3
-> worker xu ly DeepFace
-> UI poll log/result va hien granted/denied/error
```

### Dang Nam O Dau

- `frontend/user/src/pages/AccessPage.tsx`
- `frontend/user/src/components/CameraView.tsx`
- `frontend/user/src/api/access.ts`
- `backend/app/api/access.py`
- `backend/app/services/storage_service.py`
- `docs/api.md`
- `docs/use-case.md`

### Nen Sua Nhu The Nao

Them UI dung `navigator.mediaDevices.getUserMedia()`:

```text
[ ] Nut bat/tat camera
[ ] Preview video
[ ] Nut chup frame
[ ] Convert canvas frame thanh Blob/File
[ ] Goi API upload/check-image
[ ] Hien loading khi job dang processing
[ ] Poll `/logs` hoac endpoint log detail de cap nhat ket qua
[ ] Fallback upload file neu trinh duyet khong co camera
```

Backend nen uu tien API multipart:

```text
POST /access/check-image
```

### Moc Hoan Thanh

- Demo duoc bang webcam laptop.
- Anh chup tu UI duoc luu vao MinIO/S3 hoac storage service da chon.
- Access log hien ket qua sau khi worker xu ly.
- Docs co ghi ro trinh duyet can quyen camera.

## 13. Quan Ly User Va Phan Quyen Day Du Hon

### Van De

Repo da co `users` va login, nhung admin UI/API chua quan ly user day du. Neu bi hoi theo de bai ve admin them/xoa user, cap quyen, xem role, repo hien moi dat muc auth co ban.

Phan quyen cung can tach ro:

```text
admin: quan ly employee, camera, user, logs, system status
user: check access, xem profile/history cua flow user
```

### Dang Nam O Dau

- `backend/app/models/user.py`
- `backend/app/api/auth.py`
- `backend/app/core/deps.py`
- `backend/app/db/seed.py`
- `frontend/admin/src/App.tsx`
- `frontend/admin/src/pages/SettingsPage.tsx`
- `frontend/user/src/pages/ProfilePage.tsx`

### Nen Sua Nhu The Nao

Backend:

```text
[ ] Them dependency require_admin_user
[ ] Them API admin users:
    GET /admin/users
    POST /admin/users
    PUT /admin/users/{id}
    DELETE /admin/users/{id} hoac deactivate
[ ] Khong tra password_hash ra frontend
[ ] Test user role bi 403 o endpoint admin
```

Frontend admin:

```text
[ ] Them trang User Management
[ ] Tao/sua role admin/user
[ ] Reset password demo neu can
[ ] Disable user thay vi xoa cung neu muon giu audit
```

### Moc Hoan Thanh

- Token role `user` khong goi duoc API admin.
- Admin tao/sua/disable user duoc.
- README/docs ghi ro tai khoan demo va role.

## 14. Docker Image Registry Theo Yeu Cau Mon Hoc

### Van De

CI hien co build va publish image len GHCR khi push `main`. Neu de bai/giang vien yeu cau Docker Hub, can bo sung Docker Hub hoac ghi ro registry dang dung.

### Dang Nam O Dau

- `.github/workflows/ci.yml`
- `backend/Dockerfile`
- `worker/Dockerfile`
- `frontend/user/Dockerfile`
- `frontend/admin/Dockerfile`
- `docs/cicd.md`
- `docs/deployment.md`

### Nen Sua Nhu The Nao

Neu dung Docker Hub:

```text
[ ] Tao Docker Hub repository cho:
    deepface-backend
    deepface-worker
    deepface-frontend-user
    deepface-frontend-admin
[ ] Them GitHub Secrets:
    DOCKERHUB_USERNAME
    DOCKERHUB_TOKEN
[ ] CI login Docker Hub
[ ] Push tag commit SHA va latest
[ ] Cap nhat Helm values dung image Docker Hub
[ ] Cap nhat docs cach pull/run image
```

Neu tiep tuc dung GHCR:

```text
[ ] Docs noi ro image registry la GHCR
[ ] Demo checklist co link image packages
[ ] Helm values dung image tu GHCR
```

### Moc Hoan Thanh

- Nguoi khac clone repo co the pull image tu registry va chay deploy.
- Docs khop voi registry thuc te.

## 15. Checklist Chung Minh Du Baseline De Bai

### Van De

Repo co nhieu thanh phan nen khi demo de bi hoi "cai nay co chay that khong?". Can mot checklist ngan de chung minh tung yeu cau co bang chung.

### Checklist Nen Co

Tao hoac cap nhat:

```text
docs/demo-checklist-bonus.md
```

Checklist nen gom:

```text
[ ] docker compose up -d --build thanh cong
[ ] docker compose ps tat ca service chinh up/healthy
[ ] backend /health tra database=ok, redis=ok
[ ] backend /metrics co deepface_backend_up, database_up, redis_up, queue_length
[ ] Prometheus target deepface-backend UP
[ ] Grafana dashboard DeepFace Access Overview co du lieu
[ ] Alertmanager UI mo duoc
[ ] Nginx route /, /admin/, /api hoac /health, /docs chay
[ ] Seed user admin/user thanh cong
[ ] Admin tao employee/camera duoc
[ ] User check access duoc
[ ] Worker DeepFace smoke:
    same person -> granted
    different person -> denied
    no face -> error
[ ] MinIO duoc dung trong upload flow that
[ ] Qdrant duoc dung trong matching/search flow that
[ ] Redis queue co job va ve 0 sau khi worker xu ly
[ ] Backup script tao duoc postgres.sql va data/object storage archive
[ ] README co lenh chay lai tu dau
```

### Ghi Chu

Checklist nay khong thay code/test, nhung rat huu ich khi bao ve project vi no noi ro:

- thanh phan nao da chay that;
- thanh phan nao chi la baseline service;
- lenh nao dung de chung minh.

## 16. Cap Nhat README Va Mapping Theo De Bai

### Van De

README hien giai thich repo tot, nhung nen co bang mapping truc tiep giua yeu cau de bai va file/service trong repo. Bang nay giup nguoi cham thay nhanh he thong dap ung muc co ban nao.

### Nen Sua Nhu The Nao

Them section vao README hoac docs rieng:

```text
Yeu cau de bai                         | Repo hien co
-------------------------------------- | --------------------------------
Frontend user                          | frontend/user
Frontend admin                         | frontend/admin
Backend API                            | backend FastAPI
Message queue                          | Redis embedding_jobs/access_jobs
Database                               | PostgreSQL
Object storage                         | MinIO, can noi upload flow
Vector database                        | Qdrant, can noi matching flow
Load balancer/reverse proxy            | nginx
Docker Compose                         | docker-compose.yml
AI model / inference                   | worker DeepFace
Monitoring                             | Prometheus/Grafana/Alertmanager
```

### Moc Hoan Thanh

- README noi ro phan nao da hoan thanh that.
- README khong noi qua tay ve MinIO/Qdrant neu flow chua dung.
- Co link den docs setup, API, AI pipeline, deployment, monitoring, backup.

## Ghi Chu Cuoi

Nhung muc tren khong co nghia repo dang hong. Repo hien da co core flow, test, docs va deploy baseline tot cho MVP. Cac muc nay la nhung viec nen lam de he thong:

- giong flow that hon;
- bam de bai hon;
- de demo hon;
- tranh bi hoi vao cac diem co ban nhu upload, phan quyen, object storage, vector database.

Neu hoan thanh cac muc 1, 2, 3, 4, 8, 11, 12, 13, 14 va 16, repo se vung hon nhieu cho phan yeu cau co ban cua de bai. Cac muc monitoring/Helm/backup hien da co baseline kha tot, nhung van nen giu checklist de chung minh bang lenh chay that.
