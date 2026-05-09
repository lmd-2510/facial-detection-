# Use Cases

Tai lieu nay tom tat cac use case chinh cua DeepFace Access Control MVP.

## Admin

- Dang nhap bang tai khoan admin.
- Tao va cap nhat ho so employee.
- Tao embedding job cho anh khuon mat employee bang `image_path`.
- Tao camera/cong ra vao.
- Xem access logs va trang thai `processing`, `granted`, `denied`, `error`.
- Kiem tra trang thai van hanh qua `/admin/status`.

## User

- Dang nhap bang tai khoan user.
- Gui yeu cau check access bang `camera_id` va `image_path`.
- Xem lich su access logs.
- Xem thong tin profile dang nhap.

## Operator / DevOps

- Chay local stack bang Docker Compose.
- Kiem tra health/metrics.
- Chay test tong hop.
- Backup PostgreSQL va thu muc `data/`.
- Render/lint Helm chart truoc khi deploy.

## Ngoai Pham Vi Hien Tai

- Upload file that qua UI/API.
- Matching vector bang Qdrant trong flow chinh.
- Dashboard Grafana va alerting.
- Playwright E2E tren browser that.
