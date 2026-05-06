# Database Schema

Tai lieu nay ghi schema toi thieu cho DeepFace Access Control MVP. Muc tieu cua Giai Doan 2 la co ban thiet ke du lieu ro rang truoc khi tao SQLAlchemy model va migration trong backend.

## Nguyen Tac Thiet Ke

- PostgreSQL la database chinh trong MVP.
- Dung `id` kieu integer auto-increment cho cac bang nghiep vu de don gian khi build API.
- Dung `created_at` cho tat ca bang chinh de audit co ban.
- Cac truong trang thai nen dung chuoi ngan va co tap gia tri ro rang.
- Anh upload ban dau luu bang duong dan local trong `image_path`; MinIO se tinh sau.
- Vector khuon mat ban dau co the luu trong PostgreSQL de test end-to-end; Qdrant se tinh sau khi pipeline on dinh.

## So Do Tong Quan

```text
users

employees 1 ---- n face_embeddings
employees 1 ---- n access_logs

cameras   1 ---- n access_logs
```

## Bang `users`

Luu tai khoan dang nhap cho admin va user.

| Cot | Kieu du kien | Bat buoc | Ghi chu |
| --- | --- | --- | --- |
| `id` | integer | yes | Primary key |
| `username` | varchar(100) | yes | Unique, dung de dang nhap |
| `password_hash` | varchar(255) | yes | Mat khau da hash, khong luu plain text |
| `role` | varchar(50) | yes | `admin` hoac `user` |
| `created_at` | timestamptz | yes | Thoi diem tao tai khoan |

Gia tri `role` ban dau:

- `admin`: quan ly employee, camera, log.
- `user`: thuc hien check access va xem lich su lien quan.

## Bang `employees`

Luu nhan vien duoc dang ky khuon mat.

| Cot | Kieu du kien | Bat buoc | Ghi chu |
| --- | --- | --- | --- |
| `id` | integer | yes | Primary key |
| `code` | varchar(50) | yes | Ma nhan vien, unique |
| `name` | varchar(150) | yes | Ten hien thi |
| `department` | varchar(150) | no | Phong ban |
| `status` | varchar(50) | yes | Trang thai nhan vien |
| `created_at` | timestamptz | yes | Thoi diem tao ho so |

Gia tri `status` ban dau:

- `active`: duoc phep check access.
- `inactive`: tam ngung hoac da nghi viec.

## Bang `cameras`

Luu camera hoac cong ra vao.

| Cot | Kieu du kien | Bat buoc | Ghi chu |
| --- | --- | --- | --- |
| `id` | integer | yes | Primary key |
| `name` | varchar(150) | yes | Ten camera/cong |
| `location` | varchar(255) | no | Vi tri lap dat |
| `stream_url` | text | no | URL stream neu co |
| `status` | varchar(50) | yes | Trang thai camera |
| `created_at` | timestamptz | yes | Thoi diem tao camera/cong |

Gia tri `status` ban dau:

- `active`: camera/cong dang hoat dong.
- `inactive`: khong dung trong flow check access.

## Bang `face_embeddings`

Luu vector khuon mat cua employee. Trong MVP, mot employee co the co nhieu embedding neu upload nhieu anh.

| Cot | Kieu du kien | Bat buoc | Ghi chu |
| --- | --- | --- | --- |
| `id` | integer | yes | Primary key |
| `employee_id` | integer | yes | Foreign key den `employees.id` |
| `vector` | jsonb | yes | Mang so thuc, vi du `[0.12, 0.34, ...]` |
| `model_name` | varchar(100) | yes | Ten model/fake embedder da tao vector |
| `created_at` | timestamptz | yes | Thoi diem tao embedding |

Ghi chu:

- Giai doan fake AI co the dung vector kich thuoc nho va deterministic.
- Khi thay bang DeepFace that, can ghi ro `model_name` de tranh tron embedding cua nhieu model.
- Khi tich hop Qdrant, bang nay van co the giu metadata va id tham chieu vector.

## Bang `access_logs`

Luu lich su check ra vao.

| Cot | Kieu du kien | Bat buoc | Ghi chu |
| --- | --- | --- | --- |
| `id` | integer | yes | Primary key |
| `employee_id` | integer | no | Foreign key den `employees.id`, null neu khong match duoc ai |
| `camera_id` | integer | no | Foreign key den `cameras.id`, null neu check thu cong khong co camera |
| `status` | varchar(50) | yes | Ket qua check access |
| `score` | double precision | no | Diem matching/cosine similarity |
| `image_path` | text | no | Duong dan anh snapshot/upload |
| `created_at` | timestamptz | yes | Thoi diem ghi log |

Gia tri `status` ban dau:

- `processing`: da nhan request va dang cho worker xu ly.
- `granted`: match duoc employee active va vuot threshold.
- `denied`: khong match, score thap, employee inactive, hoac khong du quyen.
- `error`: pipeline loi hoac input khong hop le.

## Quan He Va Rang Buoc

- `employees.code` nen unique de tranh trung ma nhan vien.
- `users.username` nen unique de tranh trung tai khoan.
- `face_embeddings.employee_id` tham chieu `employees.id`.
- `access_logs.employee_id` tham chieu `employees.id`, cho phep null.
- `access_logs.camera_id` tham chieu `cameras.id`, cho phep null.
- Khi xoa employee, nen uu tien soft-delete bang `status = inactive` thay vi xoa that de giu access log.

## Seed Data Toi Thieu

Can co seed user de test login sau khi auth API duoc lam:

| username | role | Ghi chu |
| --- | --- | --- |
| `admin` | `admin` | Tai khoan quan tri demo |
| `user` | `user` | Tai khoan nguoi dung demo |

Mat khau seed khong nen hard-code trong code production. Giai doan dev co the dung bien moi truong hoac script seed rieng.

Lenh seed du lieu demo:

```powershell
docker compose run --rm backend python -m app.db.seed
```

Co the doi tai khoan demo bang cac bien moi truong:

- `SEED_ADMIN_USERNAME`
- `SEED_ADMIN_PASSWORD`
- `SEED_USER_USERNAME`
- `SEED_USER_PASSWORD`

## Huong Tao Model O Buoc Tiep Theo

Khi tao model trong `backend/app/models/`, co the chia theo file:

```text
backend/app/models/user.py
backend/app/models/employee.py
backend/app/models/camera.py
backend/app/models/access_log.py
backend/app/models/face_embedding.py
```

Backend can them ket noi database trong:

```text
backend/app/db/base.py
backend/app/db/session.py
backend/app/core/config.py
```

Sau khi co model, can chuan bi mot trong hai cach tao bang:

- Dung SQLAlchemy `Base.metadata.create_all()` cho MVP dev nhanh:

```powershell
docker compose run --rm backend python -m app.db.init_db
```

- Dung Alembic migration neu muon version schema ro rang hon.
