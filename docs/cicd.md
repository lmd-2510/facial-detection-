# CI/CD

GitHub Actions workflow nam o:

```text
.github/workflows/ci.yml
```

Pipeline hien tai la CI + publish Docker images. Workflow tu dong test/build tren moi `push` va `pull_request`; rieng khi `push` vao `main`, workflow se publish Docker images len Docker Hub.

## Jobs

CI hien co 4 job:

- `backend-tests`: cai `backend/requirements.txt` va chay `python -m pytest backend/app/tests`.
- `worker-tests`: cai `worker/requirements.txt` va chay `python -m pytest worker/app/tests`.
- `frontend-builds`: chay `npm ci` va `npm run build` cho user/admin frontend.
- `docker-builds`: build Docker image cho backend, worker, user frontend va admin frontend; khi push vao `main` thi publish image len Docker Hub.

## Dieu CI Dang Bat Loi

- Backend API contract bi loi.
- Worker DeepFace wrapper/service contract bi loi.
- TypeScript/frontend build bi loi.
- Dockerfile khong build duoc.

## Docker Images

Images duoc publish len Docker Hub theo format:

```text
<dockerhub-username>/deepface-backend:<commit-sha>
<dockerhub-username>/deepface-backend:latest
<dockerhub-username>/deepface-worker:<commit-sha>
<dockerhub-username>/deepface-worker:latest
<dockerhub-username>/deepface-frontend-user:<commit-sha>
<dockerhub-username>/deepface-frontend-user:latest
<dockerhub-username>/deepface-frontend-admin:<commit-sha>
<dockerhub-username>/deepface-frontend-admin:latest
```

Workflow dung Docker Hub access token de login. Can them 2 GitHub Actions secrets truoc khi publish tren `main`:

```text
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
```

Registry chinh thuc cua repo hien tai la Docker Hub, khop voi workflow CI va Helm chart. Neu deploy bang Helm, dat:

```powershell
helm upgrade --install deepface-access helm/deepface-access `
  --set global.imageRegistry=<dockerhub-username> `
  --set global.imageTag=<commit-sha>
```

Trong do `<dockerhub-username>` phai trung voi Docker Hub namespace duoc dung trong CI. Neu Docker Hub repositories dang private, tao Kubernetes image pull secret va truyen vao chart:

```powershell
kubectl create secret docker-registry dockerhub-pull `
  --docker-server=https://index.docker.io/v1/ `
  --docker-username=<dockerhub-username> `
  --docker-password=<dockerhub-token>

helm upgrade --install deepface-access helm/deepface-access `
  --set global.imageRegistry=<dockerhub-username> `
  --set global.imageTag=<commit-sha> `
  --set global.imagePullSecrets[0].name=dockerhub-pull
```

Co the kiem tra cau hinh Docker Hub trong repo bang:

```powershell
.\scripts\check-dockerhub-readiness.ps1 -Namespace <dockerhub-username> -ImageTag latest -SkipRemote
```

Sau khi workflow tren `main` da push image that, bo `-SkipRemote` de script kiem tra tag `latest` tren Docker Hub.

## Dieu Pipeline Chua Lam

- Chua deploy tu dong len server, Kubernetes hoac staging.
- Chua chay smoke test DeepFace that voi model weight trong container.
- Chua chay browser E2E bang Playwright.

## Chay Local Truoc Khi Push

```powershell
.\scripts\test.ps1
docker compose build backend worker frontend-user frontend-admin
```

Neu worker dependency DeepFace qua nang cho may CI, co the tach Docker build worker sang workflow nightly sau, nhung khong nen bo worker tests.

## Cach Trinh Bay

Co the mo ta pipeline hien tai la:

```text
test backend/worker -> build frontend -> build Docker images -> publish images to Docker Hub on main
```

Day la muc CI + artifact publishing. De thanh CD day du hon, buoc tiep theo se la tu dong deploy image vua publish len staging/server.
