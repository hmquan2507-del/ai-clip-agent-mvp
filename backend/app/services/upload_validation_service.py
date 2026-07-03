from fastapi import UploadFile


ALLOWED_VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
    "video/x-matroska",
}

MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024


class UploadValidationError(Exception):
    pass


class UploadValidationService:
    def validate_video_file(self, file: UploadFile) -> None:
        if file.content_type not in ALLOWED_VIDEO_MIME_TYPES:
            raise UploadValidationError(
                "Unsupported video format. Allowed: MP4, MOV, WEBM, MKV."
            )