# Use Cases

Tai lieu nay tom tat cac use case chinh cua DeepFace Access Control MVP.

## Admin

- Dang nhap bang tai khoan admin.
- Tao va cap nhat ho so employee.
- Upload anh khuon mat employee len MinIO/S3 va tao embedding job bang `image_key`.
- Tao camera/cong ra vao.
- Xem access logs va trang thai `processing`, `granted`, `denied`, `error`.
- Kiem tra trang thai van hanh qua `/admin/status`.

## User

- Dang nhap bang tai khoan user.
- Upload snapshot len MinIO/S3 va gui yeu cau check access bang `camera_id` va `image_key`.
- Xem lich su access logs.
- Xem thong tin profile dang nhap.

## Operator / DevOps

- Chay local stack bang Docker Compose.
- Kiem tra health/metrics.
- Xem dashboard Grafana va alert local qua Alertmanager.
- Chay test tong hop.
- Backup PostgreSQL va thu muc `data/`.
- Render/lint Helm chart truoc khi deploy.

## Ngoai Pham Vi Hien Tai

- Upload file that qua UI/API.
- Matching vector bang Qdrant trong flow chinh.
- Kenh gui alert production nhu email/Slack.
- Playwright E2E tren browser that.
