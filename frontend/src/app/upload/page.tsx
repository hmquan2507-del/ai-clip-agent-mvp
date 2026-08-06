"use client";

import { useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, UploadCloud } from "lucide-react";
import { AppShell } from "@/components/layout/app-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/section-header";
import { ProductionMetadataForm, type ProductionMetadata } from "@/features/upload/production-metadata-form";
import { UploadDropzone } from "@/features/upload/upload-dropzone";
import { UploadProgress, type UploadProgressStatus } from "@/features/upload/upload-progress";
import { UploadQueue } from "@/features/upload/upload-queue";
import { validateUploadFile } from "@/features/upload/upload-validation";
import { apiClient } from "@/lib/api-client";

const initialMetadata: ProductionMetadata = {
  title: "",
  description: "",
  style: "Podcast",
};

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [metadata, setMetadata] = useState<ProductionMetadata>(initialMetadata);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<UploadProgressStatus>("idle");
  const [created, setCreated] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasFiles = files.length > 0;

  const validFiles = useMemo(
    () => files.filter((file) => validateUploadFile(file).valid),
    [files],
  );

  const canCreateProduction =
    validFiles.length > 0 &&
    metadata.title.trim().length > 0 &&
    status !== "uploading";

  function handleFilesSelected(selectedFiles: File[]) {
    setFiles((currentFiles) => [...currentFiles, ...selectedFiles]);
    setCreated(false);

    if (selectedFiles[0] && metadata.title.trim().length === 0) {
      setMetadata((current) => ({
        ...current,
        title: selectedFiles[0].name.replace(/\.[^/.]+$/, ""),
      }));
    }
  }

  function handleRemoveFile(fileName: string) {
    setFiles((currentFiles) =>
      currentFiles.filter((file) => file.name !== fileName),
    );
  }

  async function handleCreateProduction() {
    if (!canCreateProduction) return;

    setCreated(false);
    setError(null);
    setStatus("uploading");
    setProgress(15);

    const createdProduction = await apiClient.createProduction({
      title: metadata.title,
      description: metadata.description,
      style: metadata.style,
    });

    if (!createdProduction?.id) {
      setStatus("failed");
      setError(
        "Không thể tạo Production. Kiểm tra backend có đang chạy không, rồi thử lại.",
      );
      return;
    }

    const targetId = createdProduction.id;

    if (validFiles[0]) {
      setProgress(45);
      // The backend automatically builds the AI-edited timeline (real
      // transcript-based subtitles, b-roll, music, SFX) as part of this
      // call - it can take 30-60s for Gemini to process the video.
      const uploadedAsset = await apiClient.uploadSourceVideo(
        targetId,
        validFiles[0],
      );

      if (!uploadedAsset) {
        setStatus("failed");
        setError(
          "Tạo Production thành công nhưng upload video thất bại. Vào Editor để thử upload lại.",
        );
        window.setTimeout(() => {
          window.location.href = `/editor/${targetId}`;
        }, 1200);
        return;
      }
    }

    setProgress(100);
    setStatus("completed");
    setCreated(true);

    window.setTimeout(() => {
      window.location.href = `/editor/${targetId}`;
    }, 800);
  }

  return (
    <AppShell title="Upload & Production Creation" subtitle="Upload raw video footage and metadata to initiate AI processing">
      <div className="grid gap-6" data-upload-page="true">
        <SectionHeader
          eyebrow="Production Creation"
          title="Create a new Production"
          description="Upload source video, validate file quality, add production metadata, and prepare it for AI processing."
        />

        <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <div className="grid gap-6">
            <UploadDropzone onFilesSelected={handleFilesSelected} />

            {hasFiles && (
              <UploadProgress value={progress} status={status} />
            )}
          </div>

          <div className="grid gap-6">
            <UploadQueue files={files} onRemoveFile={handleRemoveFile} />

            <ProductionMetadataForm
              value={metadata}
              onChange={setMetadata}
            />
          </div>
        </section>

        <Card>
          <CardHeader
            title="Create Production"
            description="This action creates a Production and sends valid uploads into the AI processing flow."
          />

          <CardContent>
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="flex flex-wrap gap-2">
                  <Badge tone={validFiles.length > 0 ? "success" : "warning"}>
                    {validFiles.length} valid file{validFiles.length === 1 ? "" : "s"}
                  </Badge>

                  <Badge tone={metadata.title.trim() ? "success" : "warning"}>
                    {metadata.title.trim() ? "Metadata ready" : "Missing title"}
                  </Badge>

                  <Badge tone={created ? "success" : "neutral"}>
                    {created ? "Production created" : "Waiting"}
                  </Badge>
                </div>

                {created && (
                  <p className="mt-3 flex items-center gap-2 text-sm text-emerald-300">
                    <CheckCircle2 className="h-4 w-4" />
                    Đã tạo Production & upload video thành công! Đang chuyển hướng sang Editor (AI đang/đã tự động edit)...
                  </p>
                )}

                {error && (
                  <p className="mt-3 flex items-center gap-2 text-sm text-rose-300">
                    <AlertTriangle className="h-4 w-4" />
                    {error}
                  </p>
                )}
              </div>

              <Button
                type="button"
                onClick={handleCreateProduction}
                disabled={!canCreateProduction}
                className="bg-gradient-to-r from-violet-600 to-indigo-600 px-6 font-semibold text-white shadow-lg transition hover:from-violet-500 hover:to-indigo-500"
              >
                <UploadCloud className="mr-2 h-4 w-4" />
                Tải Lên & Tự Động AI Edit
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}