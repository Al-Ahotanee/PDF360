"use client";

import { useState } from "react";
import { Topbar } from "@/components/layout/Topbar";
import { FileSelect } from "@/components/tools/FileSelect";
import { ToolCard, PrimaryButton } from "@/components/tools/ToolCard";
import { apiClient } from "@/lib/api/client";
import { useJob } from "@/hooks/useJob";

function BatchJobList({ jobIds }: { jobIds: string[] }) {
  if (jobIds.length === 0) return null;
  return (
    <div className="mt-4 space-y-2">
      {jobIds.map((id) => (
        <BatchJobRow key={id} jobId={id} />
      ))}
    </div>
  );
}

function BatchJobRow({ jobId }: { jobId: string }) {
  const { data: job } = useJob(jobId);
  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-800">
      <span className="text-slate-500">Job {jobId.slice(0, 8)}…</span>
      <span
        className={
          job?.status === "done"
            ? "text-green-600"
            : job?.status === "failed"
            ? "text-red-500"
            : "text-slate-500"
        }
      >
        {job?.status ?? "queued"}
      </span>
    </div>
  );
}

export default function BatchToolsPage() {
  const [compressFiles, setCompressFiles] = useState<string[]>([]);
  const [quality, setQuality] = useState("medium");
  const [compressJobIds, setCompressJobIds] = useState<string[]>([]);

  const [splitFiles, setSplitFiles] = useState<string[]>([]);
  const [splitRanges, setSplitRanges] = useState("1-1");
  const [splitJobIds, setSplitJobIds] = useState<string[]>([]);

  const [ocrFiles, setOcrFiles] = useState<string[]>([]);
  const [ocrJobIds, setOcrJobIds] = useState<string[]>([]);

  const [wmFiles, setWmFiles] = useState<string[]>([]);
  const [wmText, setWmText] = useState("CONFIDENTIAL");
  const [wmJobIds, setWmJobIds] = useState<string[]>([]);

  async function runBatchCompress() {
    const { data } = await apiClient.post("/batch/compress", { file_ids: compressFiles, quality });
    setCompressJobIds(data.job_ids);
  }
  async function runBatchSplit() {
    const page_ranges = splitRanges.split(",").map((r) => {
      const [a, b] = r.trim().split("-").map(Number);
      return [a, b || a];
    });
    const { data } = await apiClient.post("/batch/split", { file_ids: splitFiles, page_ranges });
    setSplitJobIds(data.job_ids);
  }
  async function runBatchOcr() {
    const { data } = await apiClient.post("/batch/ocr", { file_ids: ocrFiles, languages: ["english"] });
    setOcrJobIds(data.job_ids);
  }
  async function runBatchWatermark() {
    const { data } = await apiClient.post("/batch/watermark", { file_ids: wmFiles, text: wmText, opacity: 0.3 });
    setWmJobIds(data.job_ids);
  }

  return (
    <>
      <Topbar title="Batch Processing" />
      <main className="flex-1 space-y-4 overflow-y-auto p-6">
        <ToolCard title="Batch compress" description="Compress many files at once — each gets its own job.">
          <FileSelect value={compressFiles} onChange={(v) => setCompressFiles(v as string[])} multiple label="Files" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Quality</span>
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runBatchCompress} disabled={compressFiles.length === 0}>
              Compress {compressFiles.length || ""} files
            </PrimaryButton>
          </div>
          <BatchJobList jobIds={compressJobIds} />
        </ToolCard>

        <ToolCard title="Batch split" description="Apply the same page-range split to many files at once.">
          <FileSelect value={splitFiles} onChange={(v) => setSplitFiles(v as string[])} multiple label="Files" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page ranges</span>
            <input
              value={splitRanges}
              onChange={(e) => setSplitRanges(e.target.value)}
              placeholder="1-3, 4-6"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runBatchSplit} disabled={splitFiles.length === 0}>
              Split {splitFiles.length || ""} files
            </PrimaryButton>
          </div>
          <BatchJobList jobIds={splitJobIds} />
        </ToolCard>

        <ToolCard title="Batch OCR" description="Make many scanned files searchable at once.">
          <FileSelect value={ocrFiles} onChange={(v) => setOcrFiles(v as string[])} multiple label="Files" />
          <div className="mt-3">
            <PrimaryButton onClick={runBatchOcr} disabled={ocrFiles.length === 0}>
              OCR {ocrFiles.length || ""} files
            </PrimaryButton>
          </div>
          <BatchJobList jobIds={ocrJobIds} />
        </ToolCard>

        <ToolCard title="Batch watermark" description="Stamp the same watermark across many files.">
          <FileSelect value={wmFiles} onChange={(v) => setWmFiles(v as string[])} multiple label="Files" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Watermark text</span>
            <input
              value={wmText}
              onChange={(e) => setWmText(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runBatchWatermark} disabled={wmFiles.length === 0}>
              Watermark {wmFiles.length || ""} files
            </PrimaryButton>
          </div>
          <BatchJobList jobIds={wmJobIds} />
        </ToolCard>
      </main>
    </>
  );
}
