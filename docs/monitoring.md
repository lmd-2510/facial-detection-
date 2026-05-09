# Monitoring

Sau Giai Doan 8, monitoring toi thieu gom backend `/health`, backend `/metrics`, Docker healthcheck, Prometheus, Alertmanager va Grafana dashboard.

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
monitoring/prometheus/rules/deepface-alerts.yml
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

Alert rules hien co:

- `BackendMetricsDown`: Prometheus khong scrape duoc backend `/metrics`.
- `DatabaseUnavailable`: backend bao PostgreSQL down.
- `RedisUnavailable`: backend bao Redis down.
- `QueueBacklogHigh`: tong queue Redis lon hon 20 trong 5 phut.
- `AccessProcessingBacklog`: access logs status `processing` lon hon 10 trong 5 phut.
- `AccessErrorsPresent`: co access log status `error`.

## Alertmanager

Alertmanager nhan alert tu Prometheus va hien thi alert firing/resolved trong local UI.

Config nam o:

```text
monitoring/alertmanager/alertmanager.yml
```

Chay local:

```powershell
docker compose up -d alertmanager prometheus
```

Mo UI:

```text
http://localhost:9093
```

Hien tai Alertmanager dung receiver local de xem alert trong UI. Chua cau hinh kenh gui email, Slack hoac webhook that.

## Grafana

Grafana duoc cau hinh trong Docker Compose va tu dong nap datasource/dashboard tu:

```text
monitoring/grafana/provisioning/
monitoring/grafana/dashboards/
```

Chay local:

```powershell
docker compose up -d grafana
```

Mo UI:

```text
http://localhost:3000
```

Tai khoan mac dinh trong local dev:

```text
admin / admin
```

Co the doi bang cac bien:

- `GRAFANA_PORT`
- `GRAFANA_ADMIN_USER`
- `GRAFANA_ADMIN_PASSWORD`

Dashboard mac dinh:

- `DeepFace Access Overview`

Dashboard hien thi:

- trang thai backend, database va Redis;
- do dai queue `embedding_jobs` va `access_jobs`;
- tong access logs theo status;
- tong so job dang cho xu ly.

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

- Worker chua expose `/metrics` rieng; hien theo doi worker qua logs va Redis queue length.
- Chua co kenh gui alert ra email, Slack hoac webhook production.
