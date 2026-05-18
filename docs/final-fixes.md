# Final Fixes

Tai lieu nay la ban do sua cuoi truoc khi nop/demo. Muc tieu la lam 3 viec:

1. Chuyen image registry tu GHCR sang Docker Hub de bam sat de bai hon.
2. Nang user UI tu chup anh thu cong sang realtime nhe theo kieu gui frame dinh ky.
3. Lam luong chay lai tu dau cho giang vien that ro rang va it phu thuoc vao may cua tac gia.

Nguyen tac test: chi test phan lien quan, tranh full stack khi khong can. Chi chay Docker/DeepFace that khi thay doi dung toi compose, image, hoac AI runtime.

## 1. Docker Hub Registry

Trang thai: da thuc hien trong repo. CI, Docker Compose, Helm values va docs chinh da duoc chuyen sang Docker Hub. Repo cung co `scripts/check-dockerhub-readiness.ps1` de nhac va kiem tra phan ben ngoai Docker Hub truoc demo.

### Muc tieu

Thong nhat toan bo repo theo Docker Hub thay vi GHCR:

```text
<dockerhub-username>/deepface-backend:<tag>
<dockerhub-username>/deepface-worker:<tag>
<dockerhub-username>/deepface-frontend-user:<tag>
<dockerhub-username>/deepface-frontend-admin:<tag>
```

Sau khi xong, co the noi voi giang vien:

```text
CI build va publish Docker images len Docker Hub. Docker Compose va Helm deu co cau hinh de dung dung cac image do.
```

### File can sua

- `.github/workflows/ci.yml`
- `docker-compose.yml`
- `helm/deepface-access/values.yaml`
- `README.md`
- `docs/cicd.md`
- `docs/deployment.md`
- `docs/demo-checklist.md`
- `docs/important-follow-up-fixes.md`

### Cach sua chi tiet

1. Tao Docker Hub repositories:
   - `deepface-backend`
   - `deepface-worker`
   - `deepface-frontend-user`
   - `deepface-frontend-admin`

2. Tao GitHub Actions secrets:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`

3. Sua `.github/workflows/ci.yml`:
   - Doi `IMAGE_PREFIX` tu `ghcr.io/${GITHUB_REPOSITORY}` thanh `${{ secrets.DOCKERHUB_USERNAME }}`.
   - Doi login tu `docker login ghcr.io` sang `docker login`.
   - Doi tag image tu:

```text
ghcr.io/<owner>/<repo>/backend:<tag>
```

   thanh:

```text
<dockerhub-username>/deepface-backend:<tag>
```

4. Sua `helm/deepface-access/values.yaml`:

```yaml
global:
  imageRegistry: your-dockerhub-username
  imageTag: latest
  imagePullSecrets: []

backend:
  imageRepository: deepface-backend

worker:
  imageRepository: deepface-worker

frontendUser:
  imageRepository: deepface-frontend-user

frontendAdmin:
  imageRepository: deepface-frontend-admin
```

5. Sua `docker-compose.yml` theo 1 trong 2 cach.

Cach A, de demo local va cham bai offline:

```yaml
backend:
  image: ${BACKEND_IMAGE:-your-dockerhub-username/deepface-backend:latest}
  build:
    context: ./backend
```

Cach nay linh hoat: may co source thi build duoc, muon pull image san thi set bien `BACKEND_IMAGE`.

Cach B, neu muon bat buoc pull Docker Hub:

```yaml
backend:
  image: your-dockerhub-username/deepface-backend:latest
```

Voi du an nay nen chon Cach A, vi giang vien clone repo ve van co the build local neu chua pull image duoc.

6. Cap nhat docs:
   - Doi moi noi nhac `GHCR` thanh `Docker Hub`.
   - Ghi ro Docker Hub username can thay bang username that cua nhom.
   - Ghi ro cach chay:

```powershell
docker compose up -d
```

### Test can chay

Test cau hinh compose:

```powershell
docker compose config --quiet
```

Test build image lien quan, khong can build worker neu chi sua registry/docs:

```powershell
docker build -t your-dockerhub-username/deepface-backend:registry-check backend
docker build -t your-dockerhub-username/deepface-frontend-user:registry-check frontend/user
```

Test Helm render:

```powershell
docker run --rm -v "${PWD}:/workspace" -w /workspace alpine/helm:3.15.4 template deepface-access helm/deepface-access --set global.imageRegistry=your-dockerhub-username --set global.imageTag=registry-check
```

Test Docker Hub readiness truoc khi demo:

```powershell
.\scripts\check-dockerhub-readiness.ps1 -Namespace your-dockerhub-username -ImageTag latest -SkipRemote
```

Sau khi CI da push image len Docker Hub that:

```powershell
.\scripts\check-dockerhub-readiness.ps1 -Namespace your-dockerhub-username -ImageTag latest
```

### Tieu chi hoan thanh

- CI login Docker Hub bang secrets.
- CI push du 4 image len Docker Hub.
- Helm render ra image Docker Hub, khong con GHCR.
- Docs khong con huong dan GHCR lam registry chinh.
- `docker compose config --quiet` pass.
- `scripts/check-dockerhub-readiness.ps1` pass voi namespace that truoc demo.

## 2. Realtime Nhe Cho User UI

### Muc tieu

Khong lam streaming that. Lam realtime nhe theo kieu:

1. User bat webcam.
2. Frontend tu chup 1 frame moi 1-2 giay.
3. Moi frame duoc gui qua API `POST /access/check-image`.
4. Neu request truoc chua xong thi bo qua frame tiep theo.
5. UI cap nhat ket qua gan realtime.

Day la cach phu hop voi may local yeu hon va van demo duoc "camera realtime" o muc ung dung.

### File can sua

- `frontend/user/src/components/CameraView.tsx`
- `frontend/user/src/pages/AccessPage.tsx`
- `frontend/user/src/styles/globals.css`
- `README.md`
- `docs/ai-pipeline.md`
- `docs/demo-checklist.md`
- `docs/important-follow-up-fixes.md`

Neu can API rieng cho realtime sau nay:

- `backend/app/api/access.py`
- `backend/app/tests/...`

Nhung lan sua dau tien nen tan dung endpoint hien co truoc.

### Cach sua chi tiet

1. Trong `CameraView.tsx`, them props:

```ts
mode: "manual" | "realtime";
isRealtimeActive: boolean;
isSubmittingFrame: boolean;
intervalMs: number;
onRealtimeFrame: (file: File) => Promise<void>;
```

2. Tach logic `captureFrame()` thanh ham co the dung lai:

```ts
async function createFrameFile(): Promise<File | null>
```

3. Them timer bang `useEffect`:

```ts
useEffect(() => {
  if (!isCameraOn || !isRealtimeActive) return;
  const timer = window.setInterval(async () => {
    if (isSubmittingFrame) return;
    const file = await createFrameFile();
    if (file) await onRealtimeFrame(file);
  }, intervalMs);
  return () => window.clearInterval(timer);
}, [isCameraOn, isRealtimeActive, isSubmittingFrame, intervalMs, onRealtimeFrame]);
```

4. Trong `AccessPage.tsx`, them state:

```ts
const [mode, setMode] = useState<"manual" | "realtime">("manual");
const [isRealtimeActive, setIsRealtimeActive] = useState(false);
const [isSubmittingFrame, setIsSubmittingFrame] = useState(false);
const [lastRealtimeAt, setLastRealtimeAt] = useState<string | null>(null);
```

5. Them handler gui frame realtime:

```ts
async function handleRealtimeFrame(file: File) {
  if (isSubmittingFrame) return;
  setIsSubmittingFrame(true);
  try {
    const response = await checkAccessImage(token, Number(cameraId), file);
    setImageKey(response.image_key);
    setResult(response);
    setLastRealtimeAt(new Date().toLocaleTimeString());
    await onAccessQueued();
  } catch (err) {
    setError(err instanceof Error ? err.message : "Cannot check realtime frame");
  } finally {
    setIsSubmittingFrame(false);
  }
}
```

6. Them UI dieu khien:
   - Toggle `Manual` / `Realtime`.
   - Nut `Start realtime` / `Stop realtime`.
   - Hien trang thai `Scanning...`, `Waiting`, hoac `Last frame HH:mm:ss`.

7. Dat mac dinh interval:

```text
1500ms hoac 2000ms
```

Khong nen gui lien tuc 10-30 FPS, vi DeepFace nang va worker se bi qua tai.

8. Them cooldown neu can:
   - Neu ket qua la `granted`, dung realtime 3-5 giay hoac tam dung.
   - Neu dang co request, bo qua frame moi.

### Test can chay

Build frontend user:

```powershell
cd frontend/user
npm run build
```

Neu co the mo trinh duyet:

```powershell
docker compose up -d backend frontend-user database redis minio qdrant worker
```

Sau do test tay:

- Mo user UI.
- Start camera.
- Bat realtime.
- Quan sat UI co gui frame dinh ky.
- Ket qua cap nhat, khong spam request khi request cu chua xong.

Neu muon test API/worker that:

```powershell
.\scripts\smoke-deepface.ps1 -SkipBuild
```

### Tieu chi hoan thanh

- User co the chon manual hoac realtime.
- Realtime gui frame dinh ky thanh cong.
- Khong gui frame moi khi request cu chua xong.
- UI co trang thai dang scan va ket qua gan nhat.
- `frontend/user` build pass.
- Smoke DeepFace van pass neu co dung den flow AI.

## 3. Luong Deploy Lai Tu Dau Cho Giang Vien

### Muc tieu

Nguoi cham clone repo ve va co the chay he thong ma khong can hoi tac gia.

Noi cach khac: README phai tra loi duoc 5 cau:

1. Can cai gi truoc?
2. Can file `.env` nhu nao?
3. Lenh nao de start?
4. Mo URL nao de demo?
5. Loi thi xem o dau?

### File can sua

- `README.md`
- `.env.example`
- `docs/setup.md`
- `docs/demo-checklist.md`
- `scripts/demo-baseline-check.ps1`
- `scripts/dev.ps1`

### Cach sua chi tiet

1. Them section `Quick Start For Grading` vao README:

```markdown
## Quick Start For Grading

1. Copy environment file:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Start stack:
   ```powershell
   docker compose up -d --build
   ```

3. Wait and verify:
   ```powershell
   docker compose ps
   .\scripts\demo-baseline-check.ps1
   ```

4. Open:
   - User UI: http://localhost:5173
   - Admin UI: http://localhost:5174/admin/
   - Backend health: http://localhost:8000/health
   - Nginx gateway: http://localhost:8080
   - MinIO console: http://localhost:9001
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000

5. Run AI smoke:
   ```powershell
   .\scripts\smoke-deepface.ps1 -SkipBuild
   ```
```

2. Ghi tai khoan demo ro rang trong README.

Neu seed script hien co da tao user:

```text
Admin: admin / admin123
User: user / user123
```

Neu chua co seed user on dinh, can sua seed truoc khi ghi.

3. Kiem tra `.env.example` co du:
   - Database
   - Redis
   - MinIO
   - Qdrant
   - Auth secret
   - CORS
   - DeepFace config
   - Docker Hub image variables neu dung

4. Cap nhat `docs/demo-checklist.md` thanh thu tu demo:
   - Start stack.
   - Health check.
   - Login admin.
   - Tao employee.
   - Upload/reference image.
   - Login user.
   - Manual check.
   - Realtime check.
   - Xem logs.
   - MinIO/Qdrant/Redis.
   - Monitoring.
   - Docker Hub image.
   - Helm render.

5. Cap nhat `scripts/demo-baseline-check.ps1` neu can:
   - Check URL health.
   - Check frontend user/admin.
   - Check Prometheus/Grafana/MinIO ports.
   - Check `docker compose ps` neu script dang chay tren may co Docker.

6. Them muc troubleshooting:
   - Port bi trung.
   - Docker Desktop chua bat.
   - DeepFace lan dau tai model lau.
   - Webcam can HTTPS hoac localhost.
   - Worker can them RAM/CPU.

### Test can chay

Test docs/static:

```powershell
.\scripts\demo-baseline-check.ps1 -StaticOnly
```

Test compose config:

```powershell
docker compose config --quiet
```

Test runtime toi thieu:

```powershell
docker compose up -d database redis minio qdrant backend frontend-user frontend-admin nginx
.\scripts\demo-baseline-check.ps1
```

Chi chay worker/DeepFace khi can chung minh AI:

```powershell
docker compose up -d worker
.\scripts\smoke-deepface.ps1 -SkipBuild
```

### Tieu chi hoan thanh

- Mot nguoi moi co the lam theo README tu dau den cuoi.
- Co tai khoan demo ro rang.
- Co URL demo ro rang.
- Co script check baseline.
- Co smoke test AI that.
- Co troubleshooting cho loi hay gap.

## Thu Tu Lam De An Toan

Nen lam theo thu tu nay:

1. Docker Hub registry.
2. Quick start cho giang vien.
3. Realtime nhe.
4. Chay demo checklist mot luot.
5. Cap nhat `docs/important-follow-up-fixes.md`.

Ly do: Docker Hub va quick start la phan bam de bai va cham diem de nhat. Realtime nhe la phan nang chat demo, nen lam sau khi duong chay co ban da chac.

## Commit Goi Y

Neu tach commit:

```text
feat(registry): switch deployment images to Docker Hub
docs(demo): add grading quick start flow
feat(user): add lightweight realtime camera checks
```

Neu gom thanh 1 commit lon:

```text
feat(final): align Docker Hub deploy flow and realtime demo checks
```

Nen tach commit neu co thoi gian, vi de review va rollback hon.
