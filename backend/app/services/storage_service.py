from dataclasses import dataclass
from pathlib import PurePath
from typing import BinaryIO
from uuid import uuid4

from fastapi import UploadFile

from app.config.minio import get_minio_client, minio_settings


SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


class UnsupportedImageTypeError(Exception):
    pass


@dataclass(frozen=True)
class StoredImage:
    object_key: str
    bucket: str
    content_type: str
    size: int


def validate_image_name(filename: str) -> str:
    extension = PurePath(filename).suffix.lower()
    if extension not in SUPPORTED_IMAGE_EXTENSIONS:
        raise UnsupportedImageTypeError(f"Unsupported image extension: {extension}")

    return extension


def build_object_key(prefix: str, filename: str) -> str:
    extension = validate_image_name(filename)
    normalized_prefix = prefix.strip("/").replace("\\", "/")
    return f"{normalized_prefix}/{uuid4().hex}{extension}"


def ensure_bucket_exists() -> None:
    client = get_minio_client()
    if not client.bucket_exists(minio_settings.bucket):
        client.make_bucket(minio_settings.bucket)


def upload_image_file(
    file_obj: BinaryIO,
    *,
    filename: str,
    prefix: str,
    content_type: str | None = None,
) -> StoredImage:
    object_key = build_object_key(prefix, filename)
    file_obj.seek(0, 2)
    size = file_obj.tell()
    file_obj.seek(0)
    if size <= 0:
        raise ValueError("Uploaded image is empty.")

    ensure_bucket_exists()
    resolved_content_type = content_type or "application/octet-stream"
    get_minio_client().put_object(
        minio_settings.bucket,
        object_key,
        file_obj,
        size,
        content_type=resolved_content_type,
    )
    return StoredImage(
        object_key=object_key,
        bucket=minio_settings.bucket,
        content_type=resolved_content_type,
        size=size,
    )


def upload_fastapi_image(
    upload: UploadFile,
    *,
    prefix: str,
) -> StoredImage:
    filename = upload.filename or "upload.jpg"
    return upload_image_file(
        upload.file,
        filename=filename,
        prefix=prefix,
        content_type=upload.content_type,
    )
