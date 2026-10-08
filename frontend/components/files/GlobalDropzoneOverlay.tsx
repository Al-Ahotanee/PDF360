"use client";

import { useEffect, useState } from "react";
import { UploadCloud, CheckCircle2, Loader2 } from "lucide-react";
import { useUploadFile } from "@/hooks/useFiles";

export function GlobalDropzoneOverlay() {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{ total: number; done: number; isUploading: boolean } | null>(null);
  const upload = useUploadFile();

  useEffect(() => {
    let dragCounter = 0;

    function handleDragEnter(e: DragEvent) {
      e.preventDefault();
      dragCounter++;
      if (e.dataTransfer?.types?.includes("Files")) {
        setIsDragging(true);
      }
    }

    function handleDragLeave(e: DragEvent) {
      e.preventDefault();
      dragCounter--;
      if (dragCounter <= 0) {
        setIsDragging(false);
        dragCounter = 0;
      }
    }

    function handleDragOver(e: DragEvent) {
      e.preventDefault();
      if (e.dataTransfer) {
        e.dataTransfer.dropEffect = "copy";
      }
    }

    async function handleDrop(e: DragEvent) {
      e.preventDefault();
      dragCounter = 0;
      setIsDragging(false);

      const droppedFiles = e.dataTransfer?.files;
      if (!droppedFiles || droppedFiles.length === 0) return;

      const fileList = Array.from(droppedFiles);
      setUploadStatus({ total: fileList.length, done: 0, isUploading: true });

      for (let i = 0; i < fileList.length; i++) {
        try {
          await upload.mutateAsync(fileList[i]);
          setUploadStatus((prev) => (prev ? { ...prev, done: i + 1 } : null));
        } catch (err) {
          console.error("Upload failed for file:", fileList[i].name, err);
        }
      }

      setTimeout(() => {
        setUploadStatus(null);
      }, 3000);
    }

    window.addEventListener("dragenter", handleDragEnter);
    window.addEventListener("dragleave", handleDragLeave);
    window.addEventListener("dragover", handleDragOver);
    window.addEventListener("drop", handleDrop);

    return () => {
      window.removeEventListener("dragenter", handleDragEnter);
      window.removeEventListener("dragleave", handleDragLeave);
      window.removeEventListener("dragover", handleDragOver);
      window.removeEventListener("drop", handleDrop);
    };
  }, [upload]);

  return (
    <>
      {/* Full-Screen Drag-over Overlay */}
      {isDragging && (
        <div className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-black/80 backdrop-blur-md p-6 pointer-events-none animate-in fade-in duration-150">
          <div className="flex flex-col items-center justify-center rounded-3xl border-2 border-dashed border-signal bg-[#0d1524]/90 p-12 text-center shadow-2xl">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-signal/10 text-signal mb-4 animate-bounce">
              <UploadCloud size={40} />
            </div>
            <h2 className="text-2xl font-bold text-white">Drop files anywhere to upload</h2>
            <p className="mt-2 text-sm text-slate-400">PDF, Word, Excel, PowerPoint, or images</p>
            <div className="mt-4 rounded-full bg-signal px-4 py-1 text-xs font-bold text-ink">
              Instant Document Workspace Sync
            </div>
          </div>
        </div>
      )}

      {/* Floating Upload Progress Toast */}
      {uploadStatus && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-2xl border border-white/10 bg-[#0d1524] p-4 text-white shadow-2xl animate-in slide-in-from-bottom-5">
          {uploadStatus.done === uploadStatus.total ? (
            <CheckCircle2 size={24} className="text-green-400 shrink-0" />
          ) : (
            <Loader2 size={24} className="animate-spin text-signal shrink-0" />
          )}
          <div>
            <p className="text-sm font-semibold">
              {uploadStatus.done === uploadStatus.total
                ? `Uploaded ${uploadStatus.total} files successfully`
                : `Uploading ${uploadStatus.done + 1} of ${uploadStatus.total} files…`}
            </p>
            <p className="text-xs text-slate-400">
              {uploadStatus.done === uploadStatus.total ? "All files ready in workspace" : "Please wait a moment"}
            </p>
          </div>
        </div>
      )}
    </>
  );
}
