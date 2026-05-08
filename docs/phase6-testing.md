# Phase 6 Frontend And Test Notes

Tai lieu nay ghi nhanh nhung gi can kiem tra sau khi Giai Doan 6 noi frontend theo API.

## Flow Da Co Tren UI

Admin app:

- Dang nhap bang `POST /auth/login`.
- Xem dashboard tong quan tu employees, cameras va access logs.
- Tao, sua, disable employee.
- Tao embedding job cho employee bang `image_path`.
- Tao camera/cong ra vao.
- Xem access logs.
- Xem thong tin session va API base URL.

User app:

- Dang nhap bang `POST /auth/login`.
- Goi `POST /access/check` voi `camera_id` va `image_path`.
- Xem ket qua job ban dau o trang access check.
- Xem access history tu `GET /logs`.
- Xem profile tu token hien tai.

## Cach Chay Test Tong Hop

Chay script:

```powershell
.\scripts\test.ps1
```

Script nay chay:

- Backend API tests trong `backend/app/tests`.
- Worker fake AI pipeline tests trong `worker/app/tests`.
- Admin frontend build bang `npm run build` neu may co `npm`.
- User frontend build bang `npm run build` neu may co `npm`.

Neu `npm` khong co trong PATH, script van chay backend/worker tests va bo qua frontend build co thong bao ro rang.

## Dieu Can Smoke Test Bang Docker Compose

Sau khi seed demo data:

```powershell
docker compose run --rm backend python -m app.db.seed
docker compose up --build
```

Kiem tra thu cong:

- Mo admin app tai `http://localhost:5174`, dang nhap `admin` / `admin123`.
- Tao employee va queue embedding job voi mot `image_path`.
- Tao camera neu chua co camera.
- Mo user app tai `http://localhost:5173`, dang nhap `user` / `user123`.
- Goi access check voi `camera_id` ton tai va `image_path`.
- Refresh logs/history de xem status sau khi worker xu ly.

## Gioi Han Hien Tai

- UI van nhap `image_path` thu cong, chua upload file that.
- Access check tra ve job `processing` ngay luc queue; can refresh logs/history de xem worker cap nhat thanh `granted`, `denied` hoac `error`.
- Test frontend hien tai la build-level check, chua co Playwright end-to-end vi project chua cai dependency test frontend.
