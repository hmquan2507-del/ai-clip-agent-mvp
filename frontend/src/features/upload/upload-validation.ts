export type UploadValidationResult = {
  valid: boolean;
  errors: string[];
};

const allowedMimeTypes = [
  "video/mp4",
  "video/quicktime",
  "video/webm",
  "video/x-matroska",
];

const maxFileSizeInMb = 500;
const maxFileSizeInBytes = maxFileSizeInMb * 1024 * 1024;

export function validateUploadFile(file: File): UploadValidationResult {
  const errors: string[] = [];

  if (!allowedMimeTypes.includes(file.type)) {
    errors.push("Unsupported video format. Please upload MP4, MOV, WEBM, or MKV.");
  }

  if (file.size > maxFileSizeInBytes) {
    errors.push(`File is too large. Maximum size is ${maxFileSizeInMb}MB.`);
  }

  if (file.size === 0) {
    errors.push("File is empty. Please choose another video.");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B";

  const units = ["B", "KB", "MB", "GB"];
  const index = Math.floor(Math.log(bytes) / Math.log(1024));
  const value = bytes / Math.pow(1024, index);

  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[index]}`;
}