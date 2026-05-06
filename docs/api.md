# Backend API

Tai lieu nay tom tat API backend hien co den Giai Doan 4. Swagger chi tiet co tai:

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

Request tao embedding job:

```json
{
  "image_path": "/app/storage/uploads/employee_1.jpg"
}
```

Response tra ve `job_id`, `type = embedding`, `employee_id`, `image_path` va `queue_name = embedding_jobs`. Giai Doan 4 moi day job vao Redis; worker nhan job va log payload, chua tao embedding that.

## Cameras

Tat ca endpoint cameras can Bearer token.

- `GET /cameras`: danh sach camera/cong.
- `POST /cameras`: tao camera/cong.

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

### `POST /access/check`

Can Bearer token. Giai Doan 4 tao `access_log` trang thai `processing`, day job vao Redis queue `access_jobs`, roi tra response `202 Accepted`. Worker nhan job va log payload; AI pipeline se duoc lam o giai doan sau.

Request:

```json
{
  "camera_id": 1,
  "image_path": "/app/storage/uploads/snapshot.jpg"
}
```

Response hien tai co `status` mac dinh la `processing`, `employee_id` la `null`, `job_id` cua Redis job va `log_id` cua access log vua duoc tao. Fake AI pipeline o Giai Doan 5 se cap nhat log thanh `granted`, `denied` hoac `error`.
