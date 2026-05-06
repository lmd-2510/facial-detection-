# AI Pipeline

Tai lieu nay ghi trang thai pipeline AI cho DeepFace Access Control MVP.
Hien tai project da co core fake AI pipeline cua Giai Doan 5 theo
`docs/implementation-roadmap.md`, truoc khi tich hop DeepFace that.

## Muc Tieu Giai Doan 5

Muc tieu la test duoc flow end-to-end:

```text
image_path
-> detector
-> anti_spoof
-> embedder
-> matcher
-> decision
-> access_log
```

Pipeline fake can deterministic: cung mot anh hoac cung mot duong dan anh thi tao cung mot vector.
Do chinh xac AI chua quan trong o giai doan nay; muc tieu la kiem tra queue, worker va database update.

## Module ML Hien Co

### `worker/app/ml/detector.py`

Gia lap phat hien khuon mat.

- Reject `image_path` rong.
- Reject extension khong nam trong danh sach anh ho tro.
- Neu ten file chua marker nhu `no_face`, `noface`, `empty`, `blank` thi gia lap khong thay mat.
- Cac truong hop con lai tra ve `FaceDetectionResult` co bounding box va confidence deterministic.

### `worker/app/ml/anti_spoof.py`

Gia lap anti-spoof/liveness.

- Ban dau pass voi `image_path` hop le.
- Reject `image_path` rong.
- Co helper `require_live_face()` de pipeline co the dung kieu fail-fast.

### `worker/app/ml/embedder.py`

Tao fake embedding.

- Dung hash tu noi dung file neu file ton tai.
- Neu file chua ton tai trong local environment, dung chinh `image_path` lam seed.
- Vector deterministic va duoc normalize.
- Model name hien tai: `fake-hash-embedding-v1`.

### `worker/app/ml/matcher.py`

So sanh vector bang cosine similarity.

- Co `cosine_similarity()`.
- Co `find_best_match()` de tim candidate co score cao nhat.
- Threshold mac dinh hien tai la `0.85`.

## Trang Thai Tich Hop

Da co:

- Cac module ML fake trong `worker/app/ml/`.
- Unit test trong `worker/app/tests/`.
- Worker queue o `worker/app/tasks/queue_worker.py` lay job tu Redis va dispatch sang job handler.
- Ket noi PostgreSQL rieng cho worker trong `worker/app/config/database.py`.
- Schema SQLAlchemy Core toi thieu cho worker trong `worker/app/db/schema.py`.
- `embedding_job.py` goi fake detector/anti-spoof/embedder va luu vao `face_embeddings`.
- `access_job.py` goi fake pipeline, match voi embedding cua employee active, va cap nhat `access_logs`.

Trang thai access log sau worker:

- `granted`: match duoc employee active vuot threshold.
- `denied`: khong co candidate hoac score khong dat threshold.
- `error`: pipeline loi, vi du anh co marker `no_face`.

## Test

Chay test worker ML:

```powershell
$env:PYTHONPATH='worker'; python -m pytest worker\app\tests
```

Hien test cover:

- detector
- anti-spoof
- fake embedder
- matcher cosine similarity
- embedding service ghi `face_embeddings`
- access pipeline cap nhat `access_logs`
- job handlers goi dung service

## Buoc Tiep Theo

Sau Giai Doan 5, cac viec tiep theo nen lam:

1. Lam frontend theo API de thao tac flow chinh.
2. Bo sung upload file that thay vi nhap `image_path`.
3. Chay smoke test bang Docker Compose voi Redis/PostgreSQL that.
4. Sau khi flow fake on dinh, thay fake embedder bang DeepFace that.
