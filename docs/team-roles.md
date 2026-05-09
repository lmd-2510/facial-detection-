# Team Roles

Tai lieu nay goi y cach chia viec khi tiep tuc phat trien DeepFace Access Control.

## Backend

- FastAPI endpoints, auth, service/repository layer.
- PostgreSQL schema/model va seed data.
- Redis queue payload contract.
- Health, metrics va admin status endpoints.

## Worker / AI

- DeepFace detector, liveness, embedding va matching.
- Queue worker, embedding job, access job.
- Threshold tuning va smoke test voi anh that.
- Reindex/Qdrant integration neu bat dau dung vector database.

## Frontend

- Admin UI: employee, camera, logs, settings.
- User UI: access check, history, profile.
- API client, loading/error/empty states.
- Upload UI khi MinIO/upload API duoc noi vao flow.

## DevOps

- Docker Compose, nginx, healthcheck.
- CI/CD workflow.
- Monitoring Prometheus/Grafana.
- Backup/restore.
- Helm/Kubernetes deployment.

## Product / QA

- Xac dinh use case, acceptance criteria va smoke test.
- Chuan bi bo anh that: cung nguoi, khac nguoi, no-face, spoof neu co.
- Kiem tra flow end-to-end sau moi giai doan.
