# Checklist Kiểm Tra Bonus

Tài liệu này ghi lại cách tự tay kiểm tra các phần bonus hiện có trong repo trước khi thuyết trình hoặc demo.

## 1. Kiểm tra Helm

Mục tiêu:

- xác nhận Helm chart không lỗi cú pháp;
- xác nhận chart render được manifest Kubernetes.

Lệnh chạy:

```powershell
helm lint helm/deepface-access
helm template deepface-access helm/deepface-access
```

Kết quả mong đợi:

- `helm lint` báo pass;
- `helm template` in ra manifest YAML, không báo lỗi template;
- có thể nhìn thấy các resource như:
  - `ConfigMap`
  - `Deployment` cho `backend`, `worker`, `frontend-user`, `frontend-admin`
  - `StatefulSet` cho `database`
  - `Service` cho các thành phần chính

Nếu muốn lưu lại manifest để mở xem:

```powershell
helm template deepface-access helm/deepface-access > helm-rendered.yaml
```

Cách nói ngắn khi demo:

```text
Nhóm em đã xây dựng Helm chart riêng cho hệ thống. Helm lint pass và Helm template render được đầy đủ các resource chính, nên chart đã ở mức sẵn sàng đóng gói và chuẩn bị deploy lên Kubernetes.
```

## 2. Kiểm tra Monitoring

Monitoring hiện tại gồm:

- Prometheus
- Alertmanager
- Grafana

### 2.1. Khởi động monitoring

Chạy:

```powershell
docker compose up -d backend redis database worker prometheus alertmanager grafana
```

Nếu chỉ muốn kiểm tra monitoring tối thiểu:

```powershell
docker compose up -d backend prometheus alertmanager grafana
```

Kiểm tra container:

```powershell
docker compose ps
```

Cần thấy các service đang chạy:

- `backend`
- `prometheus`
- `alertmanager`
- `grafana`

### 2.2. Kiểm tra Prometheus

Mở:

```text
http://localhost:9090
```

Các bước:

1. Bấm `Status`
2. Chọn `Targets`
3. Tìm target của backend

Kết quả mong đợi:

- target `deepface-backend` có trạng thái `UP`

Tiếp theo, quay lại phần query và thử từng metric:

```text
deepface_backend_up
deepface_database_up
deepface_redis_up
deepface_queue_length
deepface_access_logs_total
```

Sau mỗi lần nhập, bấm `Execute`.

Kết quả mong đợi:

- `deepface_backend_up = 1`
- `deepface_database_up = 1`
- `deepface_redis_up = 1`
- `deepface_queue_length` có thể là `0` hoặc số khác
- `deepface_access_logs_total` có thể có hoặc chưa, tùy dữ liệu

### 2.3. Kiểm tra Alertmanager

Mở:

```text
http://localhost:9093
```

Kết quả mong đợi:

- UI của Alertmanager mở được;
- có thể chưa có alert firing nếu hệ thống đang bình thường.

Ý nghĩa:

- Prometheus phát hiện sự cố qua alert rule;
- Alertmanager là nơi nhận và hiển thị alert.

### 2.4. Kiểm tra Grafana

Mở:

```text
http://localhost:3000
```

Đăng nhập:

```text
admin / admin
```

Hoặc dùng tài khoản/mật khẩu bạn đã đổi trong lúc test.

Lưu ý:

- nếu bạn đã đổi mật khẩu Grafana, mật khẩu cũ sẽ không dùng lại được;
- nếu quên mật khẩu, có thể reset Grafana bằng cách xóa volume `grafana_data`.

#### Kiểm tra Data Source

Các bước:

1. Bấm menu bên trái
2. Chọn `Connections`
3. Chọn `Data sources`
4. Chọn `Prometheus`

Nếu Grafana chưa có datasource, có thể vào:

1. `Connections`
2. `Add new connection`
3. Chọn `Prometheus`
4. Nhập URL:

```text
http://prometheus:9090
```

5. Bấm `Save & test`

Kết quả mong đợi:

- hiện thông báo kiểu `Data source is working` hoặc `Successfully queried the Prometheus API`

#### Kiểm tra Dashboard

Các bước:

1. Bấm menu bên trái
2. Chọn `Dashboards`
3. Chọn `Browse`
4. Tìm dashboard:

```text
DeepFace Access Overview
```

5. Mở dashboard đó

Kết quả mong đợi:

- thấy các panel như:
  - `Backend`
  - `Database`
  - `Redis`
  - `Redis Queue Length`
  - `Access Logs By Status`
  - `Total Queued Jobs`
  - `Total Access Logs`
  - `Critical Dependencies`

### 2.5. Kiểm tra alert bằng lỗi có kiểm soát

Nếu muốn test sâu hơn, có thể tắt backend tạm thời:

```powershell
docker compose stop backend
```

Chờ khoảng 1-2 phút, rồi kiểm tra:

- Prometheus target của backend chuyển sang `DOWN`
- Alertmanager xuất hiện alert liên quan đến backend
- Grafana panel backend chuyển trạng thái xấu

Sau đó bật lại:

```powershell
docker compose start backend
```

## 3. Kiểm tra CI/CD

Phần hiện tại là:

- CI chạy test/build
- publish Docker images lên Docker Hub khi push vào `main`

### 3.1. Kiểm tra local trước khi push

Chạy:

```powershell
docker compose config --quiet
.\scripts\test.ps1
```

Nếu muốn chắc hơn, build thử image local:

```powershell
docker build -t deepface-backend:test backend
docker build -t deepface-worker:test worker
docker build -t deepface-frontend-user:test frontend/user
docker build -t deepface-frontend-admin:test frontend/admin
```

### 3.2. Kiểm tra GitHub Actions

Sau khi push code lên GitHub:

1. Vào repo trên GitHub
2. Chọn tab `Actions`
3. Mở workflow `CI`

Kết quả mong đợi:

- 4 job đều xanh:
  - `backend-tests`
  - `worker-tests`
  - `frontend-builds`
  - `docker-builds`

### 3.3. Kiểm tra Docker Hub Repositories

Sau khi workflow chạy xanh trên `main`:

1. Vào Docker Hub
2. Mở namespace của nhóm

Kết quả mong đợi:

- có 4 repository:
  - `<dockerhub-username>/deepface-backend`
  - `<dockerhub-username>/deepface-worker`
  - `<dockerhub-username>/deepface-frontend-user`
  - `<dockerhub-username>/deepface-frontend-admin`

Nếu bấm vào package, nên thấy tag như:

- `latest`
- commit SHA

Ghi chu registry:

```text
Registry chinh thuc hien tai la Docker Hub.
Format chung:
<dockerhub-username>/deepface-backend:<tag>
<dockerhub-username>/deepface-worker:<tag>
<dockerhub-username>/deepface-frontend-user:<tag>
<dockerhub-username>/deepface-frontend-admin:<tag>
```

Khi kiem tra Helm deploy, values nen tro ve cung registry:

```powershell
helm template deepface-access helm/deepface-access `
  --set global.imageRegistry=<dockerhub-username> `
  --set global.imageTag=latest
```

Kiem tra nhanh cau hinh Docker Hub trong repo:

```powershell
.\scripts\check-dockerhub-readiness.ps1 -Namespace <dockerhub-username> -ImageTag latest -SkipRemote
```

Sau khi CI da publish image that len Docker Hub, chay lai lenh tren va bo `-SkipRemote`.

### 3.4. Kiem tra realtime nhe tren User UI

Muc tieu:

- xac nhan User UI co the bat webcam;
- xac nhan mode realtime gui frame dinh ky qua `POST /access/check-image`;
- xac nhan UI khong spam request khi request truoc chua xong.

Cach demo ngan:

```text
User UI -> Check access -> Realtime -> Start camera -> Start realtime
```

Ket qua mong doi:

- trang thai hien `Realtime scanning`;
- UI cap nhat `Last frame ...` sau moi frame thanh cong;
- access logs/history refresh sau khi queue job;
- co the dung `Stop realtime` de dung gui frame.

### 3.5. Cách nói ngắn khi demo

```text
Nhóm em dùng GitHub Actions để tự động chạy backend tests, worker tests, frontend builds và Docker builds. Khi push vào main, workflow sẽ tự publish 4 Docker images lên Docker Hub. Mức hiện tại là CI cộng với artifact publishing; chưa có auto deploy production.
```

## 4. Nếu cần ảnh để thuyết trình

Nên chụp:

- ảnh `helm lint` và `helm template` pass;
- ảnh Prometheus target `UP`;
- ảnh Alertmanager UI;
- ảnh dashboard Grafana;
- ảnh GitHub Actions có 4 job xanh;
- ảnh Docker Hub có 4 repository/image.

## 5. Ghi nhớ nhanh

- `Helm`:
  - `helm lint`
  - `helm template`

- `Monitoring`:
  - Prometheus: `9090`
  - Alertmanager: `9093`
  - Grafana: `3000`

- `CI/CD`:
  - kiểm tra `Actions`
  - kiểm tra Docker Hub repositories
