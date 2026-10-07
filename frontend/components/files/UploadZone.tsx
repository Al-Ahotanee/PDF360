"use client";

import { useCallback, useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { useUploadFile } from "@/hooks/useFiles";

export function UploadZone() {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const upload = useUploadFile();

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files) return;
      Array.from(files).forEach((file) => upload.mutate(file));
    },
    [upload]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      onClick={() => inputRef.current?.click()}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition-colors ${
        isDragging
          ? "border-signal bg-signal/5"
          : "border-slate-300 hover:border-signal/60 dark:border-slate-700"
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.jpeg"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
      <UploadCloud className="text-signal" size={28} />
      <p className="mt-3 font-medium text-ink dark:text-white">
        {upload.isPending ? "Uploading…" : "Drop files here, or click to browse"}
      </p>
      <p className="mt-1 text-sm text-slate-500">PDF, Word, Excel, PowerPoint, or images</p>
    </div>
  );
}
