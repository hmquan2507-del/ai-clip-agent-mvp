"use client";

import { useRef } from "react";
import { UploadCloud } from "lucide-react";

type UploadDropzoneProps = {
  onFilesSelected?: (files: File[]) => void;
};

export function UploadDropzone({
  onFilesSelected,
}: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  function openPicker() {
    inputRef.current?.click();
  }

  function handleFiles(files: FileList | null) {
    if (!files) return;

    onFilesSelected?.(Array.from(files));
  }

  return (
    <div
      onClick={openPicker}
      className="
        flex
        min-h-[280px]
        cursor-pointer
        flex-col
        items-center
        justify-center
        rounded-3xl
        border-2
        border-dashed
        border-slate-700
        bg-slate-900/40
        p-8
        transition
        hover:border-violet-500
        hover:bg-slate-900
      "
    >
      <UploadCloud className="h-12 w-12 text-violet-400" />

      <h3 className="mt-6 text-xl font-semibold text-white">
        Upload Source Video
      </h3>

      <p className="mt-3 max-w-md text-center text-sm leading-6 text-slate-400">
        Drag & Drop video here or click to choose a file.
      </p>

      <p className="mt-4 text-xs text-slate-500">
        MP4 • MOV • MKV • WEBM
      </p>

      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        hidden
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}