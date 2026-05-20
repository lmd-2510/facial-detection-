# Sao Lưu Và Khôi Phục

Tài liệu này mô tả đầy đủ luồng sao lưu và khôi phục dữ liệu cho hệ thống. TẤT CẢ lệnh bên dưới phù hợp trên Windows PowerShell.

## 1. Sao Lưu Local (PostgreSQL + data/)

Chạy script:

```powershell
.\scripts\backup.ps1
```

Kết quả được tạo trong thư mục:

```text
backup/<yyyyMMdd-HHmmss>/
  postgres.sql
  data.zip
  manifest.txt
```

Ghi chú:

- `postgres.sql` là dump DB Postgres.
- `data.zip` là thư mục `data/` nếu tồn tại.
- `manifest.txt` ghi thông tin và gợi ý restore.

Mặc định giữ 10 bản mới nhất, có thể đổi số lượng:

```powershell
.\scripts\backup.ps1 -Keep 20
```

## 2. Sao Lưu PostgreSQL Lên S3 (MinIO/AWS)

Script chỉ dump PostgreSQL và upload lên S3 (không gồm `data/`). Hỗ trợ AWS S3 và S3-compatible (MinIO/R2).

### 2.1. Cấu hình biến môi trường

Tạo file `scripts/backup-s3.env`, script sẽ tự động load nếu file tồn tại:

```text
S3_BUCKET=
S3_PREFIX=deepface-db-backups
S3_ENDPOINT_URL=
S3_USE_DOCKER_CLI=
AWS_REGION=
AWS_PROFILE=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

Ghi chú quan trọng:

- **MinIO local**: đặt `S3_ENDPOINT_URL=http://host.docker.internal:9000`.
- **AWS S3**: để trống `S3_ENDPOINT_URL`.
- Nếu máy không cài AWS CLI, đặt `S3_USE_DOCKER_CLI=true`.

### 2.2. Chạy backup

```powershell
./scripts/backup-s3.ps1
```

Nếu không cài AWS CLI:

```powershell
./scripts/backup-s3.ps1 -UseDockerAwsCli
```

Output trên S3:

```text
s3://<bucket>/<prefix>/<yyyyMMdd-HHmmss>/postgres.sql
s3://<bucket>/<prefix>/<yyyyMMdd-HHmmss>/manifest.txt
```

Nếu muốn giữ file local (không xóa thư mục tạm):

```powershell
./scripts/backup-s3.ps1 -KeepLocal 5
```

## 3. Tự Động Sao Lưu Mỗi 5 Ngày (Windows)

Tạo scheduled task (mặc định 02:00) và log:

```powershell
./scripts/schedule-backup-s3.ps1 -StartTime 02:00 -LogPath logs\backup-s3.log
```

Chạy thử ngay:

```powershell
schtasks /Run /TN DeepFaceBackupS3
```

Kiểm tra log:

```powershell
Get-Content logs\backup-s3.log -Tail 50
```

Kiểm tra trạng thái task:

```powershell
schtasks /Query /TN DeepFaceBackupS3 /V /FO LIST | Select-String "Next Run Time|Last Run Time|Last Result|Status"
```

## 4. Khôi Phục PostgreSQL Từ Local Dump

Đảm bảo database container đang chạy:

```powershell
docker compose up -d database
```

Restore từ file dump:

```powershell
Get-Content backup\<timestamp>\postgres.sql | docker compose exec -T database sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## 5. Khôi Phục PostgreSQL Từ S3

```powershell
aws s3 cp s3://<bucket>/<prefix>/<timestamp>/postgres.sql - | docker compose exec -T database sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

## 6. Khôi Phục Thư Mục data/

```powershell
Expand-Archive backup\<timestamp>\data.zip -DestinationPath data -Force
```

## 7. Ghi Chú MinIO

Nếu cần backup bucket MinIO, có thể dùng `mc mirror` hoặc snapshot volume.

## 8. Ghi Chú Qdrant

Qdrant là index. Có thể backup snapshot/volume hoặc rebuild từ PostgreSQL.

## 9. Giới Hạn Hiện Tại

- Chưa có restore script tự động đầy đủ.
- Chưa có retention theo dung lượng/tuần/tháng.
