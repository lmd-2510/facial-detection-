# Setup

Tai lieu nay ghi cach chuan bi moi truong dev cho DeepFace Access Control sau Giai Doan 8.

## Yeu Cau

- Docker Desktop va Docker Compose.
- Python 3.12 neu muon chay test ngoai container.
- Node/npm neu muon build frontend ngoai container.
- Helm neu muon kiem tra chart Kubernetes.

Trong may dev hien tai, co the dung conda env `ltxldl` cho Python/Node/Helm.

## Chay Local Bang Docker

```powershell
.\scripts\dev.ps1 -Build
```

Seed tai khoan demo:

```powershell
.\scripts\seed.ps1
```

Mo nhanh:

- Backend: `http://localhost:8000`
- User app: `http://localhost:5173`
- Admin app: `http://localhost:5174`
- Nginx: `http://localhost:8080`
- Prometheus: `http://localhost:9090`
- Alertmanager: `http://localhost:9093`
- Grafana: `http://localhost:3000`

## Chay Test

```powershell
.\scripts\test.ps1
```

Script se chay:

- backend pytest
- worker pytest
- admin frontend build neu co npm
- user frontend build neu co npm

## Kiem Tra Deploy Config

```powershell
docker compose config --quiet
helm lint helm/deepface-access
helm template deepface-access helm/deepface-access
```

Neu dung conda `ltxldl`, can dam bao PATH co:

```text
C:\Users\Dell\.conda\envs\ltxldl
C:\Users\Dell\.conda\envs\ltxldl\Library\bin
```

## Ghi Chu

MinIO va Qdrant da co service/config trong Giai Doan 8, nhung flow chinh hien van nhap `image_path` local va match vector tu PostgreSQL.
