from app.core.config import settings
from app.storage.base import StorageProvider
from app.storage.local_storage import LocalStorageProvider
from app.storage.r2_storage import CloudflareR2StorageProvider


def get_storage_provider() -> StorageProvider:
    provider = getattr(settings, "storage_provider", "local").lower()

    if provider == "local":
        return LocalStorageProvider(
            base_path=getattr(settings, "local_storage_path", "data/uploads"),
        )

    if provider == "r2":
        return CloudflareR2StorageProvider(
            bucket_name=settings.r2_bucket_name,
            endpoint_url=settings.r2_endpoint_url,
            access_key_id=settings.r2_access_key_id,
            secret_access_key=settings.r2_secret_access_key,
            public_base_url=getattr(settings, "r2_public_base_url", None),
        )

    raise ValueError(f"Unsupported storage provider: {provider}")