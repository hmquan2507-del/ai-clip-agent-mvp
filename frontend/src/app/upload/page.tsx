"use client";

import { useMemo, useState } from "react";
import { CheckCircle2, UploadCloud } from "lucide-react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/section-header";
import { ProductionMetadataForm, type ProductionMetadata } from "@/features/upload/production-metadata-form";
import { UploadDropzone } from "@/features/upload/upload-dropzone";
import { UploadProgress, type UploadProgressStatus } from "@/features/upload/upload-progress";
import { UploadQueue } from "@/features/upload/upload-queue";
import { validateUploadFile } from "@/features/upload/upload-validation";

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

  function handleCreateProduction() {
    if (!canCreateProduction) return;

    setCreated(false);
    setStatus("uploading");
    setProgress(15);

    window.setTimeout(() => setProgress(45), 350);
    window.setTimeout(() => setProgress(72), 700);
    window.setTimeout(() => {
      setProgress(100);
      setStatus("completed");
      setCreated(true);
    }, 1100);
  }

  return (
    <DashboardShell
      title="Upload"
      eyebrow="Production Creation"
      actionHref="/productions"
      actionLabel="View Productions"
    >
      <div className="grid gap-6">
        <SectionHeader
          eyebrow="Sprint 4.4"
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
                    Production created successfully. Next step: AI Queue.
                  </p>
                )}
              </div>

              <Button
                type="button"
                onClick={handleCreateProduction}
                disabled={!canCreateProduction}
              >
                <UploadCloud className="h-4 w-4" />
                Create Production
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}