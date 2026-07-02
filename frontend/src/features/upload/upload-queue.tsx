import { FileVideo, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { formatFileSize, validateUploadFile } from "@/features/upload/upload-validation";

type UploadQueueProps = {
  files: File[];
  onRemoveFile?: (fileName: string) => void;
};

export function UploadQueue({ files, onRemoveFile }: UploadQueueProps) {
  if (files.length === 0) {
    return (
      <Card>
        <CardHeader
          title="Upload Queue"
          description="Selected videos will appear here before creating a Production."
        />
        <CardContent>
          <p className="text-sm text-slate-500">
            No files selected yet.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader
        title="Upload Queue"
        description={`${files.length} file${files.length > 1 ? "s" : ""} selected.`}
      />

      <CardContent>
        <div className="space-y-3">
          {files.map((file) => {
            const validation = validateUploadFile(file);

            return (
              <div
                key={`${file.name}-${file.size}`}
                className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"
              >
                <div className="flex items-start gap-3">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-violet-500/10 text-violet-300">
                    <FileVideo className="h-5 w-5" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate font-medium text-white">
                          {file.name}
                        </p>
                        <p className="mt-1 text-sm text-slate-500">
                          {formatFileSize(file.size)}
                        </p>
                      </div>

                      <div className="flex items-center gap-2">
                        <Badge tone={validation.valid ? "success" : "danger"}>
                          {validation.valid ? "Valid" : "Invalid"}
                        </Badge>

                        {onRemoveFile && (
                          <button
                            type="button"
                            onClick={() => onRemoveFile(file.name)}
                            className="rounded-lg p-1 text-slate-500 transition hover:bg-slate-800 hover:text-white"
                            aria-label={`Remove ${file.name}`}
                          >
                            <XCircle className="h-5 w-5" />
                          </button>
                        )}
                      </div>
                    </div>

                    {!validation.valid && (
                      <div className="mt-3 space-y-1">
                        {validation.errors.map((error) => (
                          <p key={error} className="text-sm text-rose-300">
                            {error}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}