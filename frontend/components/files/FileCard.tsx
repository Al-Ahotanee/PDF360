"use client";

import { Star, Download, Trash2 } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { useToggleFavorite, useTrashFile } from "@/hooks/useOrganization";
import { formatBytes, formatRelativeDate } from "@/lib/format";
import type { PDFFile } from "@/types/api";

export function FileCard({ file }: { file: PDFFile }) {
  const toggleFavorite = useToggleFavorite();
  const trash = useTrashFile();

  async function handleDownload() {
    const response = await apiClient.get(`/files/${file.id}/download`, { responseType: "blob" });
    const url = window.URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = file.original_filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <div className="group rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-ink/30">
      <div className="relative h-16 w-14">
        <div className="absolute inset-0 translate-x-1.5 translate-y-1 rotate-3 rounded-sm border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800" />
        <div className="absolute inset-0 flex items-center justify-center rounded-sm border border-slate-300 bg-white text-[10px] font-semibold text-slate-400 dark:border-slate-600 dark:bg-ink dark:text-slate-500">
          {file.original_filename.split(".").pop()?.toUpperCase()}
        </div>
      </div>

      <p className="mt-3 truncate font-medium text-ink dark:text-white" title={file.original_filename}>
        {file.original_filename}
      </p>
      <p className="text-sm text-slate-500">
        {formatBytes(file.size_bytes)} · {formatRelativeDate(file.created_at)}
      </p>

      <div className="mt-3 flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        <button
          onClick={() => toggleFavorite.mutate({ fileId: file.id, isFavorite: !file.is_favorite })}
          aria-label="Toggle favorite"
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-signal dark:hover:bg-slate-800"
        >
          <Star size={16} fill={file.is_favorite ? "currentColor" : "none"} className={file.is_favorite ? "text-signal" : ""} />
        </button>
        <button
          onClick={handleDownload}
          aria-label="Download"
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-ink dark:hover:bg-slate-800"
        >
          <Download size={16} />
        </button>
        <button
          onClick={() => trash.mutate(file.id)}
          aria-label="Move to trash"
          className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-slate-800"
        >
          <Trash2 size={16} />
        </button>
      </div>
    </div>
  );
}
