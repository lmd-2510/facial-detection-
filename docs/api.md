# Backend API

Tai lieu nay tom tat API backend hien co sau Giai Doan 8. Swagger chi tiet co tai:

```text
http://localhost:8000/docs
```

## Auth

### `POST /auth/login`

Dang nhap bang username/password va nhan Bearer token.

Request:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response gom `access_token`, `token_type`, `expires_in` va thong tin `user`.

### `GET /auth/me`

Tra ve user hien tai dua tren header:

```text
Authorization: Bearer <access_token>
```

## Employees

Tat ca endpoint employees can Bearer token.

- `GET /employees`: danh sach employee.
- `POST /employees`: tao employee.
- `GET /employees/{id}`: xem chi tiet employee.
- `PUT /employees/{id}`: cap nhat employee.
- `DELETE /employees/{id}`: soft-delete employee bang cach doi `status` thanh `inactive`.
- `POST /employees/{id}/face-image`: upload anh khuon mat employee len MinIO/S3, tra ve `object_key` va queue embedding job.
- `POST /employees/{id}/embedding-jobs`: tao job Redis de worker xu ly embedding cho anh employee.

Request tao employee:

```json
{
  "code": "EMP001",
  "name": "Nguyen Van A",
  "department": "Security",
  "status": "active"
}
```

Employee response gom them `embedding_status` va `embedding_error` de admin biet job tao embedding gan nhat dang `none`, `pending`, `success` hay `error`.

Request tao embedding job:

```json
{
  "image_key": "employee-faces/1/<uuid>.jpg"
}
```

Response tra ve `job_id`, `type = embedding`, `employee_id`, `image_key`, `image_path` va `queue_name = embedding_jobs`. `image_path` duoc giu de tuong thich nguoc, nhung gia tri chinh trong flow moi la MinIO/S3 object key. Worker se nhan job tu Redis, tai object ve file tam, chay DeepFace detector/anti-spoofing, goi DeepFace de tao embedding, roi luu vector vao bang `face_embeddings`.

Khi job duoc queue, backend cap nhat employee `embedding_status = pending`. Worker cap nhat thanh `success` neu tao embedding/upsert Qdrant thanh cong, hoac `error` kem `embedding_error` neu pipeline loi.

## Cameras

Tat ca endpoint cameras can Bearer token.

- `GET /cameras`: danh sach camera/cong.
- `POST /cameras`: tao camera/cong.
- `GET /cameras/{id}`: xem chi tiet camera/cong.
- `PUT /cameras/{id}`: cap nhat camera/cong.
- `DELETE /cameras/{id}`: soft-delete camera/cong bang cach doi `status` thanh `inactive`.

Request tao camera:

```json
{
  "name": "Main Gate",
  "location": "Lobby",
  "stream_url": "rtsp://example.local/main",
  "status": "active"
}
```

## Logs

### `GET /logs`

Can Bearer token. Tra ve danh sach access logs moi nhat truoc.

Moi log gom cac truong chinh:

```text
id, employee_id, camera_id, status, score, image_path, created_at
```

## Access

### `POST /access/snapshots`

Can Bearer token admin hoac user. Upload anh snapshot len MinIO/S3 va tra ve object key.

Response:

```json
{
  "object_key": "access-snapshots/<uuid>.jpg",
  "bucket": "deepface-images",
  "content_type": "image/jpeg",
  "size": 12345
}
```

### `POST /access/check-image`

Can Bearer token admin hoac user. Nhan `multipart/form-data` gom `camera_id` va file anh snapshot. Backend upload anh len MinIO/S3, tao `access_log` trang thai `processing`, day job vao Redis queue `access_jobs`, roi tra response `202 Accepted`.

Endpoint nay la flow UI chinh sau buoc upload that.

### `POST /access/check`

Can Bearer token admin hoac user. Backend tao `access_log` trang thai `processing`, day job vao Redis queue `access_jobs`, roi tra response `202 Accepted`. Worker se xu ly job bat dong bo bang DeepFace embedding pipeline va cap nhat `access_logs`.

Request:

```json
{
  "camera_id": 1,
  "image_key": "access-snapshots/<uuid>.jpg"
}
```

Response ban dau co `status` mac dinh la `processing`, `employee_id` la `null`, `job_id` cua Redis job va `log_id` cua access log vua duoc tao. `image_path` trong response/log hien luu cung gia tri object key de tranh migration lon. Sau khi worker xu ly xong, log co the duoc cap nhat thanh:

- `granted`: match duoc employee active vuot threshold.
- `denied`: khong co embedding phu hop hoac score duoi threshold.
- `error`: pipeline loi, vi du khong detect duoc mat hoac DeepFace khong tao duoc embedding.

Co the goi `GET /logs` de xem ket qua sau khi worker xu ly.

## Admin / Operations

### `GET /admin/status`

Can Bearer token role `admin`. Tra ve trang thai van hanh toi thieu:

- database ok/error
- Redis ok/error
- queue length cua `embedding_jobs`
- queue length cua `access_jobs`

### `GET /health`

Khong can token. Dung cho Docker/Kubernetes health check. Kiem tra backend, database va Redis.

### `GET /metrics`

Khong can token. Tra ve metric dang Prometheus text format cho monitoring toi thieu.
