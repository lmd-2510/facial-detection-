# Backup And Restore

Giai Doan 8 co backup toi thieu cho PostgreSQL va thu muc `data/` local.

Tai lieu nay la nguon huong dan backup/restore chinh cua repo. Thu muc `backup/` duoc dung de chua output backup local do script tao ra, khong can them mot file README rieng trong thu muc do.

## Tao Backup

Chay:

```powershell
.\scripts\backup.ps1
```

Script se tao thu muc:

```text
backup/<yyyyMMdd-HHmmss>/
```

Ben trong co:

- `postgres.sql`: dump PostgreSQL bang `pg_dump`.
- `data.zip`: archive thu muc `data/` neu ton tai.
- `manifest.txt`: thong tin backup va goi y restore.

Ghi chu:

- Thu muc `backup/` co the chua cac ban backup timestamp do script tao ra.
- Co the an toan xoa cac file tai lieu placeholder trong `backup/` neu docs da duoc giu tai day.

Mac dinh script giu 10 backup moi nhat. Doi so luong:

```powershell
.\scripts\backup.ps1 -Keep 20
```

## Restore PostgreSQL

Dam bao database container dang chay:

```powershell
docker compose up -d database
```

Restore tu file dump:

```powershell
Get-Content backup\<timestamp>\postgres.sql | docker compose exec -T database sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
```

Neu database da co du lieu cu, can can nhac xoa/recreate database truoc khi restore de tranh trung khoa.

## Restore Local Data

Giai nen `data.zip` ve thu muc `data/`.

```powershell
Expand-Archive backup\<timestamp>\data.zip -DestinationPath data -Force
```

## MinIO

Compose da co service MinIO va flow upload employee face image/access snapshot da dung bucket MinIO. Neu self-host MinIO, can backup bucket bang `mc mirror` hoac co che snapshot volume.

Nhung bucket can backup sau khi noi flow:

- `MINIO_BUCKET`, mac dinh `deepface-images`.

## Qdrant

Compose da co service Qdrant, nhung access matching hien van dung vector JSONB trong PostgreSQL.

Khi noi Qdrant vao flow that, can chon mot trong hai chien luoc:

- backup Qdrant snapshot/volume;
- hoac coi Qdrant la index co the rebuild tu PostgreSQL.

Neu doi model DeepFace, can reindex vector theo `model_name` moi.

## Gioi Han Con Lai

- Chua co restore script tu dong day du.
- Chua co backup scheduler.
- Chua co retention theo dung luong/tuan/thang.
