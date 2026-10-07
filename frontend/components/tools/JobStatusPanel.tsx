"use client";

import Link from "next/link";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { useJob } from "@/hooks/useJob";
import { apiClient } from "@/lib/api/client";

async function downloadResultFile(fileId: string, filename = "result.pdf") {
  const response = await apiClient.get(`/files/${fileId}/download`, { responseType: "blob" });
  const url = window.URL.createObjectURL(response.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

export function JobStatusPanel({ jobId }: { jobId: string | null }) {
  const { data: job } = useJob(jobId);
  if (!jobId || !job) return null;

  if (job.status === "queued" || job.status === "processing") {
    return (
      <div className="mt-4 flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600 dark:border-slate-800 dark:bg-ink/40 dark:text-slate-300">
        <Loader2 className="animate-spin text-signal" size={16} />
        {job.status === "queued" ? "Queued…" : "Processing…"}
      </div>
    );
  }

  if (job.status === "failed") {
    return (
      <div className="mt-4 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
        <XCircle size={16} className="mt-0.5 shrink-0" />
        <span>{job.error_message ?? "The operation failed."}</span>
      </div>
    );
  }

  // done
  const resultFileId = job.result?.file_id as string | undefined;
  const resultFileIds = job.result?.file_ids as string[] | undefined;

  return (
    <div className="mt-4 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800 dark:border-green-900 dark:bg-green-950/30 dark:text-green-300">
      <div className="flex items-center gap-2">
        <CheckCircle2 size={16} />
        Done!
      </div>
      <div className="mt-2 flex flex-wrap gap-2">
        {resultFileId && (
          <>
            <button
              onClick={() => downloadResultFile(resultFileId)}
              className="rounded-lg bg-ink px-3 py-1.5 text-xs font-medium text-white hover:bg-ink-light"
            >
              Download result
            </button>
            <Link
              href={`/editor?file=${resultFileId}`}
              className="inline-flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-ink dark:text-slate-200"
            >
              Open in Editor
            </Link>
          </>
        )}
        {resultFileIds?.map((id, i) => (
          <button
            key={id}
            onClick={() => downloadResultFile(id, `result_${i + 1}.pdf`)}
            className="rounded-lg bg-ink px-3 py-1.5 text-xs font-medium text-white hover:bg-ink-light"
          >
            Download part {i + 1}
          </button>
        ))}
      </div>
    </div>
  );
}
