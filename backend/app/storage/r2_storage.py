from typing import BinaryIO

from app.storage.base import StorageProvider


class CloudflareR2StorageProvider(StorageProvider):
    def __init__(
        self,
        bucket_name: str,
        endpoint_url: str,
        access_key_id: str,
        secret_access_key: str,
        public_base_url: str | None = None,
    ):
        self.bucket_name = bucket_name
        self.endpoint_url = endpoint_url
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.public_base_url = public_base_url

    def save_file(
        self,
        file: BinaryIO,
        object_key: str,
        content_type: str | None = None,
    ) -> str:
        raise NotImplementedError(
            "Cloudflare R2 upload will be implemented after boto3 integration."
        )

    def delete_file(self, object_key: str) -> None:
        raise NotImplementedError(
            "Cloudflare R2 delete will be implemented after boto3 integration."
        )

    def file_exists(self, object_key: str) -> bool:
        raise NotImplementedError(
            "Cloudflare R2 file_exists will be implemented after boto3 integration."
        )

    def get_public_url(self, object_key: str) -> str:
        if self.public_base_url:
            return f"{self.public_base_url.rstrip('/')}/{object_key}"

        return f"{self.endpoint_url.rstrip('/')}/{self.bucket_name}/{object_key}"

    def get_signed_url(
        self,
        object_key: str,
        expires_in_seconds: int = 3600,
    ) -> str:
        raise NotImplementedError(
            "Cloudflare R2 signed URLs will be implemented after boto3 integration."
        )