# Setup

Tai lieu nay ghi cach chuan bi moi truong dev cho DeepFace Access Control sau Giai Doan 8.

## Yeu Cau

- Docker Desktop va Docker Compose.
- Python 3.12 neu muon chay test ngoai container.
- Node/npm neu muon build frontend ngoai container.
- Helm neu muon kiem tra chart Kubernetes.

Trong may dev hien tai, co the dung conda env `ltxldl` cho Python/Node/Helm.

## Chay Local Bang Docker

Luong nhanh cho nguoi moi clone repo:

```powershell
docker compose up --build -d
.\scripts\demo-baseline-check.ps1
```

Lenh `docker compose up --build -d` da tu chay service `db-seed` mot lan de tao bang, seed tai khoan demo va du lieu mau toi thieu. Chi can copy `.env.example` thanh `.env` neu muon doi port, secret hoac thong tin seed.

Tai khoan demo mac dinh:

- Admin: `admin` / `admin123`
- User: `user` / `user123`

Neu muon chay tung buoc:

```powershell
.\scripts\dev.ps1 -Build
```

Seed tai khoan demo:

```powershell
docker compose run --rm db-seed
```

Mo nhanh:

- Backend: `http://localhost:8000`
- Home: `http://localhost:8080`
- User app: `http://localhost:8080/user/` hoac `http://localhost:5173/user/`
- Admin app: `http://localhost:5174`
- Nginx: `http://localhost:8080`
- MinIO console: `http://localhost:9001`
- Prometheus: `http://localhost:9090`
- Alertmanager: `http://localhost:9093`
- Grafana: `http://localhost:3000`

Neu can chung minh AI runtime that, chay rieng:

```powershell
.\scripts\smoke-deepface.ps1 -SkipBuild
```

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

MinIO da duoc noi vao flow upload employee face image/access snapshot. PostgreSQL hien van luu object key trong cot `image_path` de tranh migration lon. Qdrant da duoc noi vao flow matching, con PostgreSQL van la source of truth cho employee/embedding metadata.

## Loi Hay Gap

- Docker Desktop chua chay: start Docker Desktop roi chay lai `docker compose`.
- Port bi trung: kiem tra cac port `5173`, `5174`, `8000`, `8080`, `9000`, `9001`, `9090`, `9093`, `3000`. Co the doi cong qua `.env`, vi du `NGINX_PORT=8081`.
- DeepFace lan dau cham: worker can tai model weight; smoke script se cache trong volume `deepface_weights`.
- Webcam khong mo duoc: trinh duyet can chay tren `localhost` hoac HTTPS va phai duoc cap quyen camera.
- Worker bi cham hoac fail vi tai nguyen: tang RAM/CPU cho Docker Desktop hoac chay smoke test rieng thay vi full stack.
