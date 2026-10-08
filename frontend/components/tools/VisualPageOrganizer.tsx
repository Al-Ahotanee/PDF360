"use client";

import { useEffect, useState } from "react";
import { RotateCw, Trash2, ArrowLeft, ArrowRight, Undo2, Check, Loader2, FileDown, Eye } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import type { Job } from "@/types/api";

interface PageState {
  originalPage: number;
  rotation: number; // 0, 90, 180, 270
  deleted: boolean;
}

export function VisualPageOrganizer({ fileId, onFinish }: { fileId: string; onFinish?: (newFileId: string) => void }) {
  const [pages, setPages] = useState<PageState[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultJobId, setResultJobId] = useState<string | null>(null);
  const [resultFileId, setResultFileId] = useState<string | null>(null);

  const token = typeof window !== "undefined" ? window.localStorage.getItem("pdf360_access_token") : null;

  useEffect(() => {
    let mounted = true;
    async function fetchPages() {
      if (!fileId) return;
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.get<{ page_count: number }>(`/files/${fileId}/page-count`);
        const count = res.data.page_count;
        if (mounted) {
          setPages(
            Array.from({ length: count }, (_, i) => ({
              originalPage: i + 1,
              rotation: 0,
              deleted: false,
            }))
          );
        }
      } catch (err: any) {
        if (mounted) setError("Could not load page thumbnails. Please ensure the document is a valid PDF.");
      } finally {
        if (mounted) setLoading(false);
      }
    }
    fetchPages();
    return () => {
      mounted = false;
    };
  }, [fileId]);

  function rotatePage(index: number) {
    setPages((prev) =>
      prev.map((p, i) => (i === index ? { ...p, rotation: (p.rotation + 90) % 360 } : p))
    );
  }

  function rotateAll() {
    setPages((prev) => prev.map((p) => ({ ...p, rotation: (p.rotation + 90) % 360 })));
  }

  function toggleDelete(index: number) {
    setPages((prev) =>
      prev.map((p, i) => (i === index ? { ...p, deleted: !p.deleted } : p))
    );
  }

  function moveLeft(index: number) {
    if (index === 0) return;
    setPages((prev) => {
      const copy = [...prev];
      const temp = copy[index - 1];
      copy[index - 1] = copy[index];
      copy[index] = temp;
      return copy;
    });
  }

  function moveRight(index: number) {
    if (index === pages.length - 1) return;
    setPages((prev) => {
      const copy = [...prev];
      const temp = copy[index + 1];
      copy[index + 1] = copy[index];
      copy[index] = temp;
      return copy;
    });
  }

  function resetAll() {
    setPages((prev) =>
      [...prev]
        .sort((a, b) => a.originalPage - b.originalPage)
        .map((p) => ({ ...p, rotation: 0, deleted: false }))
    );
  }

  async function applyChanges() {
    setSaving(true);
    setError(null);
    try {
      let currentFileId = fileId;

      // 1. Reorder if page order changed
      const activePages = pages.filter((p) => !p.deleted);
      if (activePages.length === 0) {
        setError("You cannot delete all pages from the document.");
        setSaving(false);
        return;
      }

      const isReordered = activePages.some((p, i) => p.originalPage !== i + 1);
      if (isReordered) {
        const order = activePages.map((p) => p.originalPage);
        const { data: job } = await apiClient.post<Job>("/pdf/pages/reorder", {
          file_id: currentFileId,
          new_order: order,
        });
        if (job.result?.file_id) {
          currentFileId = job.result.file_id as string;
        }
      }

      // 2. Rotate pages if any rotated
      const rotatedPages = activePages
        .map((p, idx) => ({ idx: idx + 1, deg: p.rotation }))
        .filter((p) => p.deg !== 0);

      if (rotatedPages.length > 0) {
        // Group by degrees (90, 180, 270)
        for (const deg of [90, 180, 270]) {
          const matchPages = rotatedPages.filter((r) => r.deg === deg).map((r) => r.idx);
          if (matchPages.length > 0) {
            const { data: job } = await apiClient.post<Job>("/pdf/rotate", {
              file_id: currentFileId,
              page_numbers: matchPages,
              degrees: deg,
            });
            if (job.result?.file_id) {
              currentFileId = job.result.file_id as string;
            }
          }
        }
      }

      // 3. Delete pages if any marked deleted from original file
      const deletedFromOriginal = pages.filter((p) => p.deleted).map((p) => p.originalPage);
      if (!isReordered && deletedFromOriginal.length > 0) {
        const { data: job } = await apiClient.post<Job>("/pdf/pages/delete", {
          file_id: currentFileId,
          page_numbers: deletedFromOriginal,
        });
        if (job.result?.file_id) {
          currentFileId = job.result.file_id as string;
        }
      }

      setResultFileId(currentFileId);
      if (onFinish) onFinish(currentFileId);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to apply page modifications.");
    } finally {
      setSaving(false);
    }
  }

  async function downloadResult() {
    if (!resultFileId) return;
    const res = await apiClient.get(`/files/${resultFileId}/download`, { responseType: "blob" });
    const url = window.URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = "organized_document.pdf";
    a.click();
    window.URL.revokeObjectURL(url);
  }

  if (loading) {
    return (
      <div className="flex h-64 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 dark:border-slate-800">
        <Loader2 className="animate-spin text-signal" size={32} />
        <p className="mt-3 text-sm text-slate-500 font-medium">Generating visual page thumbnails…</p>
      </div>
    );
  }

  if (error && pages.length === 0) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
        <p>{error}</p>
      </div>
    );
  }

  const activeCount = pages.filter((p) => !p.deleted).length;

  return (
    <div className="space-y-4">
      {/* Top Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-ink/40">
        <div className="flex items-center gap-2">
          <span className="rounded-lg bg-signal/10 px-2.5 py-1 text-xs font-semibold text-signal-dark dark:text-signal">
            {activeCount} of {pages.length} Pages Included
          </span>
          <button
            onClick={rotateAll}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-ink dark:text-slate-300"
          >
            <RotateCw size={13} /> Rotate All 90°
          </button>
          <button
            onClick={resetAll}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-100 dark:border-slate-700 dark:bg-ink dark:text-slate-300"
          >
            <Undo2 size={13} /> Reset
          </button>
        </div>

        <div className="flex items-center gap-2">
          {resultFileId && (
            <button
              onClick={downloadResult}
              className="inline-flex items-center gap-1.5 rounded-xl bg-signal px-3.5 py-2 text-xs font-bold text-ink hover:bg-signal-light shadow-sm transition"
            >
              <FileDown size={14} /> Download Organized PDF
            </button>
          )}
          <button
            onClick={applyChanges}
            disabled={saving || activeCount === 0}
            className="inline-flex items-center gap-1.5 rounded-xl bg-ink px-4 py-2 text-xs font-bold text-white hover:bg-ink-light disabled:opacity-50 dark:bg-white dark:text-ink shadow-sm transition"
          >
            {saving ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} />}
            {saving ? "Applying…" : "Save & Apply Changes"}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-xs text-red-600 dark:border-red-900 dark:bg-red-950/30 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Responsive Visual Grid of Pages */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
        {pages.map((page, index) => {
          const previewUrl = `${apiClient.defaults.baseURL}/files/${fileId}/preview/${page.originalPage}${
            token ? `?token=${encodeURIComponent(token)}` : ""
          }`;

          return (
            <div
              key={`${page.originalPage}-${index}`}
              className={`group relative flex flex-col rounded-2xl border transition-all ${
                page.deleted
                  ? "border-red-300 bg-red-50/50 opacity-40 dark:border-red-900 dark:bg-red-950/20"
                  : "border-slate-200 bg-white shadow-sm hover:border-signal/60 hover:shadow-md dark:border-slate-800 dark:bg-[#0d1524]"
              } p-3`}
            >
              {/* Badge & Order indicator */}
              <div className="mb-2 flex items-center justify-between">
                <span className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                  #{index + 1}
                </span>
                <span className="text-[11px] text-slate-400">Orig p.{page.originalPage}</span>
              </div>

              {/* Rendered Thumbnail with CSS rotation */}
              <div className="relative flex h-44 w-full items-center justify-center overflow-hidden rounded-xl bg-slate-100/70 p-2 dark:bg-black/30">
                <img
                  src={previewUrl}
                  alt={`Page ${page.originalPage}`}
                  className="max-h-full max-w-full rounded object-contain shadow-sm transition-transform duration-200"
                  style={{ transform: `rotate(${page.rotation}deg)` }}
                  loading="lazy"
                />
                {page.deleted && (
                  <div className="absolute inset-0 flex items-center justify-center bg-red-900/40 backdrop-blur-[1px]">
                    <span className="rounded-lg bg-red-600 px-2.5 py-1 text-xs font-bold text-white shadow">
                      Excluded
                    </span>
                  </div>
                )}
              </div>

              {/* Card Action Controls */}
              <div className="mt-2.5 flex items-center justify-between border-t border-slate-100 pt-2 dark:border-white/5">
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => moveLeft(index)}
                    disabled={index === 0 || page.deleted}
                    title="Move page left"
                    className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-ink disabled:opacity-30 dark:hover:bg-slate-800"
                  >
                    <ArrowLeft size={13} />
                  </button>
                  <button
                    onClick={() => moveRight(index)}
                    disabled={index === pages.length - 1 || page.deleted}
                    title="Move page right"
                    className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-ink disabled:opacity-30 dark:hover:bg-slate-800"
                  >
                    <ArrowRight size={13} />
                  </button>
                </div>

                <div className="flex items-center gap-1">
                  <button
                    onClick={() => rotatePage(index)}
                    disabled={page.deleted}
                    title="Rotate 90° clockwise"
                    className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-signal disabled:opacity-30 dark:hover:bg-slate-800"
                  >
                    <RotateCw size={13} />
                  </button>
                  <button
                    onClick={() => toggleDelete(index)}
                    title={page.deleted ? "Restore page" : "Exclude page"}
                    className={`rounded-lg p-1 transition ${
                      page.deleted
                        ? "text-red-500 hover:bg-red-100 dark:hover:bg-red-950"
                        : "text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-slate-800"
                    }`}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
