import { CheckCircle2, Loader2, UploadCloud, XCircle } from "lucide-react";
import { Progress } from "@/components/ui/progress";

export type UploadProgressStatus =
  | "idle"
  | "uploading"
  | "completed"
  | "failed";

type UploadProgressProps = {
  value: number;
  status?: UploadProgressStatus;
};

export function UploadProgress({
  value,
  status = "idle",
}: UploadProgressProps) {
  const statusConfig = {
    idle: {
      label: "Waiting to upload",
      icon: UploadCloud,
      className: "text-slate-400",
    },
    uploading: {
      label: "Uploading video",
      icon: Loader2,
      className: "text-violet-300 animate-spin",
    },
    completed: {
      label: "Upload completed",
      icon: CheckCircle2,
      className: "text-emerald-300",
    },
    failed: {
      label: "Upload failed",
      icon: XCircle,
      className: "text-rose-300",
    },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
      <div className="mb-3 flex items-center gap-2">
        <Icon className={`h-4 w-4 ${config.className}`} />
        <span className="text-sm font-medium text-slate-300">
          {config.label}
        </span>
      </div>

      <Progress
        value={value}
        label="Upload progress"
        helperText={`${Math.round(value)}%`}
      />
    </div>
  );
}