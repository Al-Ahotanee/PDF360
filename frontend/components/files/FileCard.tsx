"use client";

import { useState } from "react";
import { Star, Download, Trash2, Share2, Eye, PenTool, Loader2, ShieldCheck } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { useToggleFavorite, useTrashFile } from "@/hooks/useOrganization";
import { formatBytes, formatRelativeDate } from "@/lib/format";
import { ShareModal } from "@/components/files/ShareModal";
import type { PDFFile } from "@/types/api";
import Link from "next/link";

export function FileCard({ file, isShared = false }: { file: PDFFile; isShared?: boolean }) {
  const [showShareModal, setShowShareModal] = useState(false);
  const [showViewer, setShowViewer] = useState(false);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [isLoadingBlob, setIsLoadingBlob] = useState(false);
  const [blobError, setBlobError] = useState<string | null>(null);
  const toggleFavorite = useToggleFavorite();
  const trash = useTrashFile();

  async function openViewer() {
    setShowViewer(true);
    if (!blobUrl) {
      setIsLoadingBlob(true);
      setBlobError(null);
      try {
        const response = await apiClient.get(`/files/${file.id}/download`, { responseType: "blob" });
        const url = window.URL.createObjectURL(response.data);
        setBlobUrl(url);
      } catch (err: any) {
        setBlobError("Failed to load PDF preview. File may still be processing or unavailable.");
      } finally {
        setIsLoadingBlob(false);
      }
    }
  }

  function closeViewer() {
    setShowViewer(false);
  }

  async function handleDownload() {
    const response = await apiClient.get(`/files/${file.id}/download`, { responseType: "blob" });
    const url = window.URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = file.original_filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  async function handleDownloadCertificate() {
    const response = await apiClient.get(`/pdf/${file.id}/audit-certificate`, { responseType: "blob" });
    const url = window.URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = `certificate_${file.original_filename}`;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <>
      <div className="group relative rounded-2xl border border-slate-200 bg-white p-4 transition-all hover:border-signal/50 hover:shadow-md dark:border-slate-800 dark:bg-[#0d1524]">
        {/* Clickable thumbnail area to open Viewer */}
        <div
          onClick={openViewer}
          className="cursor-pointer relative flex h-24 w-full items-center justify-center rounded-xl bg-slate-50 border border-slate-100 hover:bg-slate-100/80 dark:border-slate-800 dark:bg-white/[0.02] dark:hover:bg-white/[0.05] transition group/thumb"
        >
          <div className="flex h-12 w-10 items-center justify-center rounded border border-slate-300 bg-white text-xs font-bold text-red-500 shadow-sm dark:border-slate-700 dark:bg-ink">
            {file.original_filename.split(".").pop()?.toUpperCase() ?? "PDF"}
          </div>
          <div className="absolute inset-0 flex items-center justify-center rounded-xl bg-black/40 opacity-0 group-hover/thumb:opacity-100 transition-opacity">
            <span className="inline-flex items-center gap-1 rounded-lg bg-signal px-2.5 py-1 text-xs font-bold text-ink shadow-md">
              <Eye size={13} /> View
            </span>
          </div>
        </div>

        <p
          onClick={openViewer}
          className="mt-3 truncate font-medium text-sm text-ink hover:text-signal dark:text-white cursor-pointer transition"
          title={file.original_filename}
        >
          {file.original_filename}
        </p>
        <p className="text-xs text-slate-400 mt-0.5">
          {formatBytes(file.size_bytes)} · {formatRelativeDate(file.created_at)}
        </p>

        {/* Action Toolbar */}
        <div className="mt-3.5 flex items-center justify-between border-t border-slate-100 pt-2 dark:border-white/5">
          <div className="flex items-center gap-1">
            <button
              onClick={openViewer}
              aria-label="Preview document"
              title="Preview in Viewer"
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-signal dark:hover:bg-slate-800"
            >
              <Eye size={15} />
            </button>
            <Link
              href={`/editor?file=${file.id}`}
              aria-label="Open in editor"
              title="Annotate & Edit"
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-signal dark:hover:bg-slate-800"
            >
              <PenTool size={15} />
            </Link>
            {!isShared && (
              <button
                onClick={() => toggleFavorite.mutate({ fileId: file.id, isFavorite: !file.is_favorite })}
                aria-label="Toggle favorite"
                className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-signal dark:hover:bg-slate-800"
              >
                <Star size={15} fill={file.is_favorite ? "currentColor" : "none"} className={file.is_favorite ? "text-signal" : ""} />
              </button>
            )}
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={handleDownload}
              aria-label="Download"
              title="Download file"
              className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-ink dark:hover:bg-slate-800"
            >
              <Download size={15} />
            </button>
            {!isShared && (
              <>
                <button
                  onClick={() => setShowShareModal(true)}
                  aria-label="Share document"
                  title="Share document"
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-signal dark:hover:bg-slate-800"
                >
                  <Share2 size={15} />
                </button>
                <button
                  onClick={() => trash.mutate(file.id)}
                  aria-label="Move to trash"
                  title="Delete file"
                  className="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-slate-800"
                >
                  <Trash2 size={15} />
                </button>
              </>
            )}
          </div>
        </div>
      </div>

      {showShareModal && (
        <ShareModal file={file} onClose={() => setShowShareModal(false)} />
      )}

      {showViewer && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 md:p-6 animate-in fade-in duration-200">
          <div className="flex h-full max-h-[92vh] w-full max-w-5xl flex-col rounded-3xl border border-white/10 bg-[#0d1524] shadow-2xl overflow-hidden">
            <header className="flex h-16 shrink-0 items-center justify-between border-b border-white/10 bg-[#090f1b] px-6">
              <div className="flex items-center gap-3 min-w-0">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-500/10 text-red-500 font-bold text-xs">
                  PDF
                </div>
                <div className="min-w-0">
                  <h3 className="text-sm font-semibold text-white truncate max-w-sm sm:max-w-md">
                    {file.original_filename}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {formatBytes(file.size_bytes)} · Document Viewer
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Link
                  href={`/editor?file=${file.id}`}
                  className="inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-white/10 hover:text-white"
                >
                  <PenTool size={13} className="text-signal" />
                  Edit & Annotate
                </Link>
                <button
                  onClick={handleDownloadCertificate}
                  title="Download Tamper-Evident Audit Certificate"
                  className="inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-white/10 hover:text-white transition"
                >
                  <ShieldCheck size={13} className="text-signal" />
                  Audit Certificate
                </button>
                <button
                  onClick={handleDownload}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-signal px-3.5 py-1.5 text-xs font-bold text-ink hover:bg-signal-light transition"
                >
                  <Download size={13} />
                  Download
                </button>
                <button
                  onClick={closeViewer}
                  className="rounded-xl p-1.5 text-slate-400 hover:bg-white/10 hover:text-white"
                >
                  ✕
                </button>
              </div>
            </header>
            <div className="relative flex-1 overflow-hidden bg-[#070b12] p-2 flex items-center justify-center">
              {isLoadingBlob && (
                <div className="flex flex-col items-center gap-3 text-slate-400">
                  <Loader2 className="animate-spin text-signal" size={32} />
                  <p className="text-sm font-medium">Loading document preview…</p>
                </div>
              )}
              {blobError && (
                <div className="flex flex-col items-center gap-3 text-center p-6">
                  <p className="text-sm text-red-400 max-w-md">{blobError}</p>
                  <button
                    onClick={() => { setBlobUrl(null); openViewer(); }}
                    className="rounded-xl bg-signal px-4 py-2 text-xs font-bold text-ink hover:bg-signal-light transition"
                  >
                    Retry loading
                  </button>
                </div>
              )}
              {blobUrl && (
                <iframe
                  src={`${blobUrl}#toolbar=1`}
                  className="h-full w-full rounded-2xl border border-white/5 shadow-inner"
                  title={file.original_filename}
                />
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

