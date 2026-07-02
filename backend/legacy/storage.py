import mimetypes
import os
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class StoredFile:
    provider: str
    key: str
    filename: str
    size: int
    mime_type: str
    local_path: Path | None = None
    url: str = ""
    expires_at: int | None = None


def guess_mime(filename):
    return mimetypes.guess_type(filename)[0] or "application/octet-stream"


class LocalStorageAdapter:
    provider = "local"

    def __init__(self, jobs_dir):
        self.jobs_dir = Path(jobs_dir)

    def save_upload(self, job_id, filename, content):
        job_dir = self.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        path = job_dir / filename
        path.write_bytes(content)
        return StoredFile(
            provider=self.provider,
            key=f"{job_id}/{filename}",
            filename=filename,
            size=len(content),
            mime_type=guess_mime(filename),
            local_path=path,
            url=f"/jobs/{job_id}/{filename}",
        )

    def output_path(self, job_id, filename):
        job_dir = self.jobs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir / filename

    def public_url(self, job_id, filename):
        return f"/jobs/{job_id}/{filename}"

    def create_presigned_upload(self, job_id, filename, content_type):
        raise NotImplementedError("Local multipart upload is used in MVP mode.")


class S3CompatibleStorageAdapter:
    def __init__(self, provider):
        self.provider = provider
        self.bucket = os.environ.get("STORAGE_BUCKET", "")
        self.region = os.environ.get("STORAGE_REGION", "auto")
        self.endpoint_url = os.environ.get("STORAGE_ENDPOINT_URL", "")
        self.public_base_url = os.environ.get("STORAGE_PUBLIC_BASE_URL", "").rstrip("/")
        self.prefix = os.environ.get("STORAGE_PREFIX", "uploads").strip("/")

    def _client(self):
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError("boto3 is required for S3/R2 storage") from exc
        if not self.bucket:
            raise RuntimeError("STORAGE_BUCKET is required for S3/R2 storage")
        kwargs = {"region_name": self.region}
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url
        return boto3.client("s3", **kwargs)

    def key_for(self, job_id, filename):
        return f"{self.prefix}/{job_id}/{filename}" if self.prefix else f"{job_id}/{filename}"

    def create_presigned_upload(self, job_id, filename, content_type):
        key = self.key_for(job_id, filename)
        client = self._client()
        expires_in = int(os.environ.get("STORAGE_PRESIGN_SECONDS", "900"))
        upload_url = client.generate_presigned_url(
            "put_object",
            Params={"Bucket": self.bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expires_in,
            HttpMethod="PUT",
        )
        public_url = f"{self.public_base_url}/{key}" if self.public_base_url else ""
        return {
            "provider": self.provider,
            "bucket": self.bucket,
            "key": key,
            "upload_url": upload_url,
            "public_url": public_url,
            "headers": {"Content-Type": content_type},
            "expires_at": int(time.time()) + expires_in,
        }

    def save_upload(self, job_id, filename, content):
        key = self.key_for(job_id, filename)
        content_type = guess_mime(filename)
        client = self._client()
        client.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType=content_type)
        public_url = f"{self.public_base_url}/{key}" if self.public_base_url else ""
        return StoredFile(
            provider=self.provider,
            key=key,
            filename=filename,
            size=len(content),
            mime_type=content_type,
            url=public_url,
        )


def create_storage_adapter(jobs_dir):
    provider = os.environ.get("STORAGE_PROVIDER", "local").lower()
    if provider in {"s3", "r2"}:
        return S3CompatibleStorageAdapter(provider)
    return LocalStorageAdapter(jobs_dir)
