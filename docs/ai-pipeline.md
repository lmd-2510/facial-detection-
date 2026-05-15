# AI Pipeline

Tai lieu nay ghi trang thai pipeline AI cho DeepFace Access Control MVP.
Sau Giai Doan 7, worker da thay cac phan fake AI trong flow chinh bang DeepFace.

## Flow Hien Tai

```text
image_key/object_key
-> worker tai anh tu MinIO/S3 ve temp file
-> DeepFace.extract_faces() de detect mat
-> DeepFace.extract_faces(anti_spoofing=True) de check liveness
-> DeepFace.represent()
-> Qdrant vector search
-> PostgreSQL verify employee/embedding active
-> decision
-> access_log
```

Worker van chap nhan `image_path` local de giu smoke test/dev cu, nhung flow UI/API moi upload anh len MinIO/S3 va dung object key trong Redis job. Access UI dung `POST /access/check-image` de upload snapshot va queue access job trong mot request.

`detector.py`, `anti_spoof.py` va `embedder.py` deu wrap DeepFace de giu contract noi bo on dinh cho worker.

## Cau Hinh DeepFace

Worker doc cac bien moi truong sau:

| Bien | Mac dinh | Ghi chu |
| --- | --- | --- |
| `DEEPFACE_MODEL_NAME` | `Facenet512` | Model dung de tao embedding |
| `DEEPFACE_DETECTOR_BACKEND` | `opencv` | Detector backend cua DeepFace |
| `DEEPFACE_ENFORCE_DETECTION` | `true` | Loi neu DeepFace khong thay mat |
| `DEEPFACE_ALIGN` | `true` | Can chinh mat truoc khi tao vector |
| `DEEPFACE_NORMALIZATION` | `base` | Chuan hoa anh dau vao theo DeepFace |
| `DEEPFACE_MATCH_THRESHOLD` | `0.70` | Nguong cosine similarity de grant access |
| `DEEPFACE_ANTI_SPOOFING` | `false` | Bat/tat anti-spoofing cua DeepFace |
| `QDRANT_URL` | `http://qdrant:6333` | Qdrant HTTP endpoint dung cho vector search |
| `QDRANT_COLLECTION` | `deepface_embeddings` | Collection luu/search face embedding |

Nguong `0.70` la moc ban dau cho cosine similarity khi dung `Facenet512`. Can smoke test voi bo anh that cua du an de tinh chinh nguong nay.
Mac dinh smoke test local nen tat `DEEPFACE_ANTI_SPOOFING` de tranh blocker dependency `torch`; khi muon test liveness that thi bat lai va bo sung dependency phu hop.

## Module ML Hien Co

### `worker/app/ml/detector.py`

Detect mat bang `DeepFace.extract_faces()`.

- Reject `image_path` rong.
- Reject extension khong nam trong danh sach anh ho tro.
- Tra ve `FaceDetectionResult` voi bounding box va confidence tu DeepFace.
- Khong con logic fake dua tren ten file.

### `worker/app/ml/anti_spoof.py`

Check liveness bang `DeepFace.extract_faces(anti_spoofing=True)`.

- Reject `image_path` rong.
- Tra ve fail neu DeepFace bao `is_real = false`.
- Neu `DEEPFACE_ANTI_SPOOFING=false`, module tra ve pass voi message noi ro anti-spoofing dang tat theo cau hinh.

### `worker/app/ml/embedder.py`

Tao embedding that bang DeepFace.

- Goi `DeepFace.represent()` bang config tu bien moi truong.
- Lay embedding cua face dau tien trong ket qua.
- Validate vector khong rong va toan so.
- Luu `model_name` vao database de tranh match nham voi embedding cua model khac.

### `worker/app/ml/matcher.py`

So sanh vector bang cosine similarity.

- Co `cosine_similarity()`.
- Co `find_best_match()` de tim candidate co score cao nhat.
- Threshold mac dinh hien tai doc tu `DEEPFACE_MATCH_THRESHOLD`.

### `worker/app/services/vector_store_service.py`

Noi worker voi Qdrant qua HTTP API.

- Tao collection Qdrant neu collection chua ton tai.
- Upsert vector employee embedding voi payload `embedding_id`, `employee_id`, `model_name`.
- Search top candidate theo query vector va filter `model_name`.
- Worker van verify candidate voi PostgreSQL de dam bao employee con `active`.

## Trang Thai Tich Hop

Da co:

- Worker queue o `worker/app/tasks/queue_worker.py` lay job tu Redis va dispatch sang job handler.
- Ket noi PostgreSQL rieng cho worker trong `worker/app/config/database.py`.
- Schema SQLAlchemy Core toi thieu cho worker trong `worker/app/db/schema.py`.
- `embedding_job.py` goi detector/liveness/embedder, luu vector DeepFace vao `face_embeddings`, roi upsert vector vao Qdrant.
- `access_job.py` goi pipeline, query Qdrant theo vector cung `model_name`, verify employee active trong PostgreSQL, roi cap nhat `access_logs`.
- `storage_service.py` normalize va validate `image_path` local truoc khi worker goi DeepFace.
- `reindex_service.py` hien chi co readiness check vi DB chua luu source `image_path` de tao lai embedding khi doi model.

Trang thai access log sau worker:

- `granted`: match duoc employee active vuot threshold.
- `denied`: khong co candidate hoac score khong dat threshold.
- `error`: pipeline loi, vi du input khong hop le hoac DeepFace khong tao duoc embedding.

## Test

Chay test worker:

```powershell
$env:PYTHONPATH='worker'; python -m pytest worker\app\tests
```

Unit test mock DeepFace de test nhanh contract cua detector, anti-spoof, embedder va service. Smoke test voi anh that nen chay qua Docker Compose sau khi rebuild worker de cai dependency va tai model weight.

## Buoc Tiep Theo

1. Chuan bi bo anh test nho gom cung nguoi/khac nguoi/anh loi/spoof neu co.
2. Chay embedding job va access job that voi Docker Compose.
3. Dieu chinh `DEEPFACE_MATCH_THRESHOLD` theo ket qua thuc te.
4. Luu them source `image_path` cho embedding neu muon reindex model ve sau.
5. Bo sung reindex Qdrant khi doi model hoac rebuild collection.
