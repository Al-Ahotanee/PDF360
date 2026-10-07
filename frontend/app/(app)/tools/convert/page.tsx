"use client";

import { useState } from "react";
import { Topbar } from "@/components/layout/Topbar";
import { FileSelect } from "@/components/tools/FileSelect";
import { JobStatusPanel } from "@/components/tools/JobStatusPanel";
import { ToolCard, PrimaryButton } from "@/components/tools/ToolCard";
import { apiClient } from "@/lib/api/client";
import type { Job } from "@/types/api";

export default function ConvertToolsPage() {
  const [toPdfFile, setToPdfFile] = useState("");
  const [toPdfJobId, setToPdfJobId] = useState<string | null>(null);

  const [fromPdfFile, setFromPdfFile] = useState("");
  const [targetFormat, setTargetFormat] = useState("docx");
  const [fromPdfJobId, setFromPdfJobId] = useState<string | null>(null);

  const [ocrFile, setOcrFile] = useState("");
  const [ocrJobId, setOcrJobId] = useState<string | null>(null);

  async function runToPdf() {
    const { data } = await apiClient.post<Job>("/pdf/convert-to-pdf", { file_id: toPdfFile });
    setToPdfJobId(data.id);
  }
  async function runFromPdf() {
    const { data } = await apiClient.post<Job>("/pdf/convert-from-pdf", { file_id: fromPdfFile, target_format: targetFormat });
    setFromPdfJobId(data.id);
  }
  async function runOcr() {
    const { data } = await apiClient.post<Job>("/pdf/ocr", { file_id: ocrFile, languages: ["english"] });
    setOcrJobId(data.id);
  }

  return (
    <>
      <Topbar title="Convert" />
      <main className="flex-1 space-y-4 overflow-y-auto p-6">
        <ToolCard title="Convert to PDF" description="Word, Excel, PowerPoint, or an image → PDF.">
          <FileSelect value={toPdfFile} onChange={(v) => setToPdfFile(v as string)} label="Source file" />
          <div className="mt-3">
            <PrimaryButton onClick={runToPdf} disabled={!toPdfFile}>Convert</PrimaryButton>
          </div>
          <JobStatusPanel jobId={toPdfJobId} />
        </ToolCard>

        <ToolCard title="Convert from PDF" description="PDF → Word, PowerPoint, Excel, images, or text.">
          <FileSelect value={fromPdfFile} onChange={(v) => setFromPdfFile(v as string)} label="PDF file" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Target format</span>
            <select
              value={targetFormat}
              onChange={(e) => setTargetFormat(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            >
              <option value="docx">Word (.docx)</option>
              <option value="pptx">PowerPoint (.pptx)</option>
              <option value="xlsx">Excel (.xlsx) — requires detectable tables</option>
              <option value="png">Images (.png, one per page)</option>
              <option value="txt">Plain text</option>
            </select>
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runFromPdf} disabled={!fromPdfFile}>Convert</PrimaryButton>
          </div>
          <JobStatusPanel jobId={fromPdfJobId} />
        </ToolCard>

        <ToolCard title="OCR (make searchable)" description="Add a searchable text layer to a scanned PDF or image.">
          <FileSelect value={ocrFile} onChange={(v) => setOcrFile(v as string)} label="File to OCR" />
          <div className="mt-3">
            <PrimaryButton onClick={runOcr} disabled={!ocrFile}>Run OCR</PrimaryButton>
          </div>
          <JobStatusPanel jobId={ocrJobId} />
        </ToolCard>
      </main>
    </>
  );
}
