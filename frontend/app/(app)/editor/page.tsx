"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Topbar } from "@/components/layout/Topbar";
import { FileSelect } from "@/components/tools/FileSelect";
import { PageEditor } from "@/components/tools/PageEditor";
import { ChevronLeft, ChevronRight } from "lucide-react";

function EditorContent() {
  const searchParams = useSearchParams();
  const fileParam = searchParams.get("file") || "";
  const [fileId, setFileId] = useState(fileParam);
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (fileParam && fileParam !== fileId) {
      setFileId(fileParam);
      setPage(1);
    }
  }, [fileParam]);

  return (
    <>
      <Topbar title="Editor" />
      <main className="flex-1 overflow-y-auto p-6">
        <div className="mb-4 max-w-sm">
          <FileSelect value={fileId} onChange={(v) => { setFileId(v as string); setPage(1); }} label="File to edit" />
        </div>

        {fileId ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-ink/30">
            <div className="mb-3 flex items-center gap-3">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                aria-label="Previous page"
              >
                <ChevronLeft size={18} />
              </button>
              <span className="text-sm text-slate-500">Page {page}</span>
              <button
                onClick={() => setPage((p) => p + 1)}
                className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                aria-label="Next page"
              >
                <ChevronRight size={18} />
              </button>
            </div>
            <PageEditor key={`${fileId}-${page}`} initialFileId={fileId} page={page} />
          </div>
        ) : (
          <p className="text-sm text-slate-500">Choose a file above to start editing.</p>
        )}
      </main>
    </>
  );
}

export default function EditorPage() {
  return (
    <Suspense fallback={<div className="flex-1 p-6">Loading editor…</div>}>
      <EditorContent />
    </Suspense>
  );
}

