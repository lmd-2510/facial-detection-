# Monitoring

Sau Giai Doan 8, monitoring toi thieu gom backend `/health`, backend `/metrics`, Docker healthcheck va Prometheus.

## Backend Health

Endpoint:

```text
GET /health
```

Tra ve:

- `status`: `ok` hoac `error`.
- `database`: `ok` hoac `error`.
- `redis`: `ok` hoac `error`.
- `environment`: gia tri `APP_ENV`.

Neu database hoac Redis loi, backend tra HTTP `503`.

## Backend Metrics

Endpoint:

```text
GET /metrics
```

Dang text Prometheus. Metric hien co:

- `deepface_backend_up`
- `deepface_database_up`
- `deepface_redis_up`
- `deepface_queue_length{queue="embedding_jobs"}`
- `deepface_queue_length{queue="access_jobs"}`
- `deepface_access_logs_total{status="..."}`

## Prometheus

Config nam o:

```text
monitoring/prometheus/prometheus.yml
```

Prometheus scrape:

```text
backend:8000/metrics
```

Chay local:

```powershell
docker compose up -d prometheus
```

Mo UI:

```text
http://localhost:9090
```

## Logging

Backend va worker log ra stdout/stderr de Docker hoac Kubernetes thu thap.

Lenh xem log local:

```powershell
docker compose logs -f backend
docker compose logs -f worker
```

Worker log cac thong tin quan trong:

- queue name
- `job_id`
- `employee_id` hoac `log_id`
- access status va score

Khong nen log token, password, secret hoac anh raw.

## Gioi Han Con Lai

- Chua co Grafana dashboard.
- Worker chua expose `/metrics` rieng; hien theo doi worker qua logs va Redis queue length.
- Chua co alert rule.
