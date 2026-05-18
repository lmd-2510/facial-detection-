# CI/CD

GitHub Actions workflow nam o:

```text
.github/workflows/ci.yml
```

Pipeline hien tai la CI + publish Docker images. Workflow tu dong test/build tren moi `push` va `pull_request`; rieng khi `push` vao `main`, workflow se publish Docker images len GitHub Container Registry (GHCR).

## Jobs

CI hien co 4 job:

- `backend-tests`: cai `backend/requirements.txt` va chay `python -m pytest backend/app/tests`.
- `worker-tests`: cai `worker/requirements.txt` va chay `python -m pytest worker/app/tests`.
- `frontend-builds`: chay `npm ci` va `npm run build` cho user/admin frontend.
- `docker-builds`: build Docker image cho backend, worker, user frontend va admin frontend; khi push vao `main` thi publish image len GHCR.

## Dieu CI Dang Bat Loi

- Backend API contract bi loi.
- Worker DeepFace wrapper/service contract bi loi.
- TypeScript/frontend build bi loi.
- Dockerfile khong build duoc.

## Docker Images

Images duoc publish len GHCR theo format:

```text
ghcr.io/<owner>/<repo>/backend:<commit-sha>
ghcr.io/<owner>/<repo>/backend:latest
ghcr.io/<owner>/<repo>/worker:<commit-sha>
ghcr.io/<owner>/<repo>/worker:latest
ghcr.io/<owner>/<repo>/frontend-user:<commit-sha>
ghcr.io/<owner>/<repo>/frontend-user:latest
ghcr.io/<owner>/<repo>/frontend-admin:<commit-sha>
ghcr.io/<owner>/<repo>/frontend-admin:latest
```

Workflow dung `GITHUB_TOKEN` de login GHCR, nen khong can them Docker Hub secret. Can dam bao repository cho phep GitHub Actions ghi package voi quyen `packages: write`.

Registry chinh thuc cua repo hien tai la GHCR, khop voi workflow CI va Helm chart. Neu deploy bang Helm, dat:

```powershell
helm upgrade --install deepface-access helm/deepface-access `
  --set global.imageRegistry=ghcr.io/<owner>/<repo> `
  --set global.imageTag=<commit-sha>
```

Trong do `<owner>/<repo>` phai trung voi `GITHUB_REPOSITORY` trong workflow, viet thuong. Neu package GHCR dang private, tao Kubernetes image pull secret va truyen vao chart:

```powershell
kubectl create secret docker-registry ghcr-pull `
  --docker-server=ghcr.io `
  --docker-username=<github-username> `
  --docker-password=<github-token>

helm upgrade --install deepface-access helm/deepface-access `
  --set global.imageRegistry=ghcr.io/<owner>/<repo> `
  --set global.imageTag=<commit-sha> `
  --set global.imagePullSecrets[0].name=ghcr-pull
```

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
test backend/worker -> build frontend -> build Docker images -> publish images to GHCR on main
```

Day la muc CI + artifact publishing. De thanh CD day du hon, buoc tiep theo se la tu dong deploy image vua publish len staging/server.
