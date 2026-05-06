# DeepFace Access Control MVP

Day la repository MVP cho he thong kiem soat ra vao bang nhan dien khuon mat. Project duoc to chuc theo huong nhieu service chay bang Docker, gom frontend, backend API, worker xu ly AI, database va cac thanh phan ha tang phu tro.

Muc tieu hien tai cua README nay la giup nguoi doc co ban do tong quan truoc khi di vao code chi tiet.

## Tong Quan He Thong

He thong co the hieu theo cac khoi lon sau:

- `frontend/`: giao dien nguoi dung va giao dien admin.
- `backend/`: FastAPI backend, nhan request tu frontend va dieu phoi nghiep vu.
- `worker/`: tien trinh nen xu ly anh, embedding va matching khuon mat.
- `database/`: du lieu khoi tao va ghi chu schema.
- `data/`: noi luu tru file local duoc mount vao container.
- `nginx/`: cau hinh reverse proxy/web server.
- `monitoring/`: cau hinh theo doi he thong.
- `backup/`: tai lieu va cau hinh lien quan den backup.
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

MinIO va Qdrant chua nam trong compose toi thieu cua Giai Doan 1. Hai service nay se duoc them sau khi core flow da on dinh.

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
2. Admin cung cap `image_path` anh khuon mat cho employee.
3. Backend tao embedding job trong Redis.
4. Worker doc job tu Redis.
5. Worker tao embedding cho anh khuon mat.
6. User cung cap `image_path` anh/snapshot de kiem tra quyen ra vao.
7. Worker so sanh embedding cua snapshot voi embedding da dang ky.
8. He thong ghi access log voi ket qua `granted`, `denied` hoac `error`.

Hien tai project da hoan thanh core flow cua Giai Doan 5: backend co API cot loi cho auth, employees, cameras, logs, va day duoc `embedding_jobs` / `access_jobs` vao Redis. Worker nghe Redis queue, chay fake AI pipeline deterministic, luu fake embedding vao `face_embeddings`, va cap nhat `access_logs` thanh `granted`, `denied` hoac `error`.

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

Sau khi chay, co the mo:

- Backend health: http://localhost:8000/health
- Backend API docs: http://localhost:8000/docs
- User app: http://localhost:5173
- Admin app: http://localhost:5174

Tao bang va seed tai khoan demo:

```powershell
docker compose run --rm backend python -m app.db.seed
```

Tai khoan demo mac dinh:

- `admin` / `admin123`
- `user` / `user123`

## File Cau Hinh Quan Trong

- `.env.example`: danh sach bien moi truong mau.
- `docker-compose.yml`: khai bao service local.
- `backend/Dockerfile`: cach build backend image.
- `worker/Dockerfile`: cach build worker image.
- `frontend/user/Dockerfile`: cach build user frontend.
- `frontend/admin/Dockerfile`: cach build admin frontend.

## Huong Phat Trien Tiep Theo

Nhung phan nen uu tien sau khi da nam tong quan:

- Hoan thien `docs/architecture.md` de mo ta kien truc ro hon.
- Hoan thien frontend theo API de thao tac flow chinh khong can Swagger.
- Bo sung upload file that thay vi nhap `image_path` thu cong.
- Sau khi fake pipeline on dinh, thay fake embedding bang DeepFace that trong worker.
- Dua embedding search sang Qdrant khi pipeline AI da on dinh.
