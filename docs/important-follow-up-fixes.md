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

Repo da co MinIO va Qdrant trong `docker-compose.yml`, `.env.example` va config code. Cac flow chinh hien da noi MinIO cho upload anh va Qdrant cho vector search.

Noi cach khac:

```text
MinIO: luu anh employee/access snapshot tu backend/frontend
Qdrant: search vector embedding trong access matching
```

Day la mot phan quan trong vi de bai co nhac toi object storage va vector database. Trang thai hien tai khong con chi la baseline service: flow chinh da dung ca hai thanh phan nay.

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
- Qdrant luu/search vector embedding, con PostgreSQL van la source of truth.

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
[x] Backend storage service upload file vao MinIO/S3
[x] Backend upload API cho employee face image
[x] Backend upload API cho access snapshot
[x] DB luu object_key thay vi local image_path
[x] Redis job dung image_key/object_key
[x] Worker tai anh tu MinIO/S3 ve temp file
[x] Worker cleanup temp file sau khi DeepFace xu ly
[x] Frontend doi input path thanh file upload
[x] Docs ghi ro MinIO/S3 la noi luu anh that
[x] Backup docs bo sung backup MinIO bucket neu self-host MinIO
```

### Ghi Chu

Trang thai hien tai khi demo co the noi ro:

```text
MinIO va Qdrant da duoc noi vao flow chinh.
PostgreSQL van la source of truth; Qdrant la search index co the rebuild ve sau.
Huong mo rong tiep theo la reindex Qdrant va chuan hoa schema image_key/object_key.
```

## 2. Upload Anh That Thay Vi Nhap `image_path`

Trang thai: da hoan thanh. Admin upload employee face image qua `POST /employees/{id}/face-image` va endpoint nay queue embedding job. User upload snapshot qua `POST /access/check-image` va endpoint nay queue access job. Cac endpoint JSON nhan `image_key`/`image_path` van duoc giu cho smoke test/dev.

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

Trang thai: da hoan thanh. Backend da co dependency `require_admin_user` va ap dung cho `/admin/status`, `/employees/*`, `/cameras/*`. Flow user nhu `/access/check-image`, `/access/check` va `/auth/me` van dung token user binh thuong.

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

Trang thai: da hoan thanh. Worker da co `vector_store_service` de tao collection Qdrant, upsert embedding khi tao face embedding, va search Qdrant trong access matching. PostgreSQL van la source of truth: sau khi Qdrant tra candidate, worker verify embedding/employee active trong PostgreSQL roi moi cap nhat `access_logs`.

### Van De

Repo da co Qdrant service/config, nhung truoc day access matching lay vector tu PostgreSQL JSON/JSONB roi so sanh cosine trong worker.

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
  -> upsert vector vao Qdrant voi payload employee_id, embedding_id, model_name
```

Khi check access:

```text
DeepFace query vector
  -> query Qdrant top_k
  -> verify employee active trong PostgreSQL
  -> apply threshold
  -> update access_logs
```

Da them service Qdrant client trong worker:

```text
worker/app/services/vector_store_service.py
```

### Ghi Chu

PostgreSQL van giu vai tro source of truth, Qdrant la search index. Neu Qdrant collection chua ton tai, worker se tao collection theo kich thuoc vector cua embedding dau tien. Neu collection da ton tai nhung sai vector size, worker bao loi de tranh ghi/search sai model.

## 5. Embedding Job Loi Khong Co Trang Thai Cho Admin

Trang thai: da hoan thanh theo cach nhe. Bang `employees` co `embedding_status` (`none`/`pending`/`success`/`error`) va `embedding_error`. Backend set `pending` khi queue embedding job. Worker set `success` sau khi tao embedding/upsert Qdrant thanh cong, va set `error` kem message neu pipeline loi. Admin UI hien trang thai embedding trong bang employee.

### Van De

Access job co `access_logs.status = processing/granted/denied/error`. Truoc day embedding job neu loi thi worker chi log exception; admin khong biet job tao embedding thanh cong hay that bai.

### Dang Nam O Dau

- `backend/app/api/employees.py`
- `backend/app/queues/embedding_queue.py`
- `worker/app/tasks/embedding_job.py`
- `worker/app/services/embedding_service.py`
- `frontend/admin/src/components/EmployeeTable.tsx`
- `frontend/admin/src/pages/EmployeePage.tsx`

### Cach Da Sua

Cach nhe:

Da them vao `employees`:

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

Cach day du hon neu ve sau can audit tung lan retry/job:

```text
Them bang embedding_jobs
```

### Ghi Chu

Neu can demo nhanh, cach them cot vao `employees` la de hieu nhat.

## 6. Luu Source Image Cua Embedding

Trang thai: da hoan thanh. Bang `face_embeddings` da co `source_image_key` de luu object key MinIO/S3 hoac local image path tuong thich dev/smoke test. Worker ghi gia tri nay khi tao embedding thanh cong, cung luc luu vector/model va upsert Qdrant.

### Van De

Truoc day bang `face_embeddings` chi luu vector va `model_name`, nhung khong luu anh goc da tao ra vector. Vi vay neu sau nay doi model DeepFace hoac can reindex Qdrant, he thong khong biet lay anh nao de tao lai embedding.

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

Sau khi worker tao embedding thanh cong, source nay duoc luu cung record embedding.

### Ghi Chu

`source_image_key` hien luu duoc ca object key MinIO/S3 va local path cu de giu tuong thich smoke test/dev. Automated reindex job van la phan sau, nhung du lieu nguon de reindex da khong con bi mat.

## 7. Hoan Thien Anti-spoofing/Liveness

Trang thai: da hoan thanh phan cau hinh an toan. Code worker, `.env.example`, Docker Compose va docs deu thong nhat `DEEPFACE_ANTI_SPOOFING=false` mac dinh. Anti-spoofing van co san trong `worker/app/ml/anti_spoof.py` va co the bat bang bien moi truong khi can demo liveness that.

### Van De

Repo da co code anti-spoofing trong worker, nhung hien dang de mac dinh tat trong Docker Compose:

```text
DEEPFACE_ANTI_SPOOFING=false
```

Ly do tam tat la anti-spoofing co the can them dependency/model nang, lan dau chay co the tai weight lau, va do on dinh phu thuoc chat luong anh/camera. Neu bat khi chua test ky, flow demo chinh co the bi false reject hoac worker loi dependency.

Truoc day docs, `.env.example`, va `docker-compose.yml` deu noi mac dinh la `false`, nhung code worker:

```text
worker/app/config/settings.py
```

co default la `true` neu chay worker ngoai Docker Compose. Hien da sua ve `false` de hanh vi local/test/doc khop nhau.

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

### Cach Da Sua / Nen Test Tiep

Lam theo tung buoc nho, khong bat mac dinh ngay:

1. Da sua default config cho khop docs:

```python
deepface_anti_spoofing: bool = _get_bool("DEEPFACE_ANTI_SPOOFING", False)
```

2. Da them/sua test de confirm:

```text
[x] Khi khong set env, settings.deepface_anti_spoofing la False
[x] Khi DEEPFACE_ANTI_SPOOFING=true, anti_spoof.py goi DeepFace voi anti_spoofing=True
[x] Khi DeepFace tra is_real=false, require_live_face raise ValueError va worker pipeline se cap nhat status error theo error handling hien co
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

Quyet dinh hien tai: giu **Huong A** cho den khi co bo anh test that tot hon va da test dependency/model trong container.

### Moc Hoan Thanh

- Config default khop docs.
- Worker container boot duoc khi `DEEPFACE_ANTI_SPOOFING=true`.
- Anti-spoof model/dependency tai duoc trong container.
- Co smoke result cho anh that, anh khac nguoi, anh khong co mat va anh spoof.
- Docs ghi ro anti-spoof dang optional hay bat mac dinh.
- Demo chinh khong bi phu thuoc vao anti-spoof neu tinh nang nay con chua on dinh.

## 8. Camera Thieu Update/Delete

Trang thai: da hoan thanh. Backend da co `GET /cameras/{id}`, `PUT /cameras/{id}` va `DELETE /cameras/{id}` soft-delete bang `status = inactive`. Admin UI da co edit va disable camera tu bang camera.

### Van De

Truoc day backend/frontend chi co:

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

### Cach Da Sua

Da them:

```text
GET /cameras/{id}
PUT /cameras/{id}
DELETE /cameras/{id}
```

Delete nen soft-delete bang:

```text
status = inactive
```

Frontend admin da them edit/disable camera tuong tu employee.

## 9. Helm Ingress `/api` Co The Khong Strip Prefix

Trang thai: da hoan thanh. Helm chart da tach rieng API ingress voi nginx rewrite rule de `/api/<path>` duoc strip prefix thanh `/<path>` truoc khi toi backend. Cac route `/docs`, `/openapi.json`, `/admin` va `/` nam trong ingress rieng khong bi rewrite nham.

### Van De

Nginx local route:

```nginx
location /api/ {
    proxy_pass http://backend/;
}
```

Cach nay strip `/api/` truoc khi goi backend.

Truoc day Helm ingress route `/api` thang ve backend. Backend khong co route `/api/auth`, ma co `/auth`.

### Dang Nam O Dau

- `helm/deepface-access/templates/nginx-ingress.yaml`
- `helm/deepface-access/values.yaml`
- `nginx/nginx.conf`
- `docs/deployment.md`

### Cach Da Sua

Dung nginx ingress rewrite rieng cho API:

```text
/api(/|$)(.*) -> /$2
```

Vi rewrite annotation cua nginx ingress ap dung cho toan bo Ingress resource, chart tach API ingress rieng de tranh lam hong `/docs`, `/openapi.json`, `/admin` va `/`.

Da test render/lint:

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
Object storage                         | MinIO, da noi upload flow
Vector database                        | Qdrant, da noi matching flow
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

## Optional Anti-spoof Smoke Test Sau Nay

Phan nay khong chan demo chinh. Hien tai `DEEPFACE_ANTI_SPOOFING=false` mac dinh de flow nhan dien chinh on dinh va khong bi phu thuoc vao model/dependency anti-spoofing nang.

Khi co thoi gian test liveness that, chay rieng:

```powershell
$env:DEEPFACE_ANTI_SPOOFING="true"
docker compose up -d --build worker
docker compose logs -f worker
```

Checklist:

```text
[ ] Worker boot duoc khi DEEPFACE_ANTI_SPOOFING=true.
[ ] employee_a_ref.jpg tao embedding pass liveness.
[ ] employee_a_ok.jpg access pass liveness va co the granted.
[ ] employee_b_ok.jpg pass liveness nhung denied do khac nguoi.
[ ] no_face.jpg loi dung do khong co mat.
[ ] spoof_a.jpg fail liveness neu anh spoof phu hop voi model.
[ ] Neu worker loi import/dependency, doc log truoc roi moi them dependency nhu torch.
[ ] Ghi lai liveness score, access status, match score va thoi gian xu ly.
```

Khuyen nghi: khong them `torch` hoac dependency nang theo cam tinh. Chi them khi da bat anti-spoofing that va log worker noi ro dang thieu dependency nao.
