# CI/CD

GitHub Actions workflow nam o:

```text
.github/workflows/ci.yml
```

## Jobs

CI hien co 4 job:

- `backend-tests`: cai `backend/requirements.txt` va chay `python -m pytest backend/app/tests`.
- `worker-tests`: cai `worker/requirements.txt` va chay `python -m pytest worker/app/tests`.
- `frontend-builds`: chay `npm ci` va `npm run build` cho user/admin frontend.
- `docker-builds`: build Docker image cho backend, worker, user frontend va admin frontend.

## Dieu CI Dang Bat Loi

- Backend API contract bi loi.
- Worker DeepFace wrapper/service contract bi loi.
- TypeScript/frontend build bi loi.
- Dockerfile khong build duoc.

## Dieu CI Chua Lam

- Chua push image len registry.
- Chua deploy tu dong.
- Chua chay smoke test DeepFace that voi model weight trong container.
- Chua chay browser E2E bang Playwright.

## Chay Local Truoc Khi Push

```powershell
.\scripts\test.ps1
docker compose build backend worker frontend-user frontend-admin
```

Neu worker dependency DeepFace qua nang cho may CI, co the tach Docker build worker sang workflow nightly sau, nhung khong nen bo worker tests.
