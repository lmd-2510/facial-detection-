# Backend API

Tai lieu nay tom tat API backend hien co o Giai Doan 3. Swagger chi tiet co tai:

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

Request tao employee:

```json
{
  "code": "EMP001",
  "name": "Nguyen Van A",
  "department": "Security",
  "status": "active"
}
```

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

Can Bearer token. Giai Doan 3 moi ghi access log placeholder, chua xu ly AI/queue that.

Request:

```json
{
  "camera_id": 1,
  "image_path": "/app/storage/uploads/snapshot.jpg"
}
```

Response hien tai co `status` mac dinh la `denied`, `employee_id` la `null`, va `log_id` cua access log vua duoc tao. Queue va fake AI pipeline se thay the logic placeholder nay o cac giai doan sau.
