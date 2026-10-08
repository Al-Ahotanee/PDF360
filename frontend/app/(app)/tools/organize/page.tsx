"use client";

import { useState } from "react";
import { LayoutGrid, SlidersHorizontal } from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { FileSelect } from "@/components/tools/FileSelect";
import { JobStatusPanel } from "@/components/tools/JobStatusPanel";
import { ToolCard, PrimaryButton } from "@/components/tools/ToolCard";
import { VisualPageOrganizer } from "@/components/tools/VisualPageOrganizer";
import { apiClient } from "@/lib/api/client";
import type { Job } from "@/types/api";

export default function OrganizeToolsPage() {
  const [organizeMode, setOrganizeMode] = useState<"visual" | "tools">("visual");
  const [visualFileId, setVisualFileId] = useState("");

  // Merge
  const [mergeFiles, setMergeFiles] = useState<string[]>([]);
  const [mergeJobId, setMergeJobId] = useState<string | null>(null);

  // Compress
  const [compressFile, setCompressFile] = useState("");
  const [quality, setQuality] = useState("medium");
  const [customDpi, setCustomDpi] = useState(100);
  const [customQuality, setCustomQuality] = useState(50);
  const [compressJobId, setCompressJobId] = useState<string | null>(null);

  // Split
  const [splitFile, setSplitFile] = useState("");
  const [ranges, setRanges] = useState("1-1");
  const [splitJobId, setSplitJobId] = useState<string | null>(null);

  // Delete pages
  const [delFile, setDelFile] = useState("");
  const [delPages, setDelPages] = useState("");
  const [delJobId, setDelJobId] = useState<string | null>(null);

  // Insert blank page
  const [insFile, setInsFile] = useState("");
  const [insPosition, setInsPosition] = useState(1);
  const [insJobId, setInsJobId] = useState<string | null>(null);

  // Duplicate page
  const [dupFile, setDupFile] = useState("");
  const [dupPage, setDupPage] = useState(1);
  const [dupJobId, setDupJobId] = useState<string | null>(null);

  // Reorder pages
  const [reoFile, setReoFile] = useState("");
  const [reoOrder, setReoOrder] = useState("");
  const [reoJobId, setReoJobId] = useState<string | null>(null);

  // Page numbers
  const [numFile, setNumFile] = useState("");
  const [numPosition, setNumPosition] = useState("bottom-center");
  const [numJobId, setNumJobId] = useState<string | null>(null);

  // Header / footer
  const [hfFile, setHfFile] = useState("");
  const [headerText, setHeaderText] = useState("");
  const [footerText, setFooterText] = useState("");
  const [hfJobId, setHfJobId] = useState<string | null>(null);

  // Rotate
  const [rotFile, setRotFile] = useState("");
  const [rotPages, setRotPages] = useState("");
  const [rotDegrees, setRotDegrees] = useState(90);
  const [rotJobId, setRotJobId] = useState<string | null>(null);

  // Extract
  const [extFile, setExtFile] = useState("");
  const [extPages, setExtPages] = useState("");
  const [extJobId, setExtJobId] = useState<string | null>(null);

  // Crop
  const [cropFile, setCropFile] = useState("");
  const [cropMargins, setCropMargins] = useState({ left: 0, top: 0, right: 0, bottom: 0 });
  const [cropJobId, setCropJobId] = useState<string | null>(null);

  // Replace pages
  const [replFile, setReplFile] = useState("");
  const [replReplacementFile, setReplReplacementFile] = useState("");
  const [replPages, setReplPages] = useState("");
  const [replJobId, setReplJobId] = useState<string | null>(null);

  // Remove watermark
  const [rwFile, setRwFile] = useState("");
  const [rwText, setRwText] = useState("");
  const [rwJobId, setRwJobId] = useState<string | null>(null);

  // Bookmarks
  const [bmFile, setBmFile] = useState("");
  const [bmTitle, setBmTitle] = useState("");
  const [bmPage, setBmPage] = useState(1);
  const [bmList, setBmList] = useState<{ level: number; title: string; page: number }[]>([]);
  const [bmSaving, setBmSaving] = useState(false);

  async function runMerge() {
    const { data } = await apiClient.post<Job>("/pdf/merge", { file_ids: mergeFiles });
    setMergeJobId(data.id);
  }

  async function runCompress() {
    const { data } = await apiClient.post<Job>("/pdf/compress", {
      file_id: compressFile, quality,
      custom_dpi_target: quality === "custom" ? customDpi : undefined,
      custom_quality: quality === "custom" ? customQuality : undefined,
    });
    setCompressJobId(data.id);
  }

  async function runSplit() {
    const page_ranges = ranges.split(",").map((r) => {
      const [a, b] = r.trim().split("-").map(Number);
      return [a, b || a];
    });
    const { data } = await apiClient.post<Job>("/pdf/split", { file_id: splitFile, page_ranges });
    setSplitJobId(data.id);
  }

  async function runDeletePages() {
    const page_numbers = delPages.split(",").map((n) => Number(n.trim())).filter(Boolean);
    const { data } = await apiClient.post<Job>("/pdf/pages/delete", { file_id: delFile, page_numbers });
    setDelJobId(data.id);
  }

  async function runInsertBlank() {
    const { data } = await apiClient.post<Job>("/pdf/pages/insert-blank", { file_id: insFile, position: insPosition });
    setInsJobId(data.id);
  }

  async function runDuplicate() {
    const { data } = await apiClient.post<Job>("/pdf/pages/duplicate", { file_id: dupFile, page_number: dupPage });
    setDupJobId(data.id);
  }

  async function runReorder() {
    const new_order = reoOrder.split(",").map((n) => Number(n.trim())).filter(Boolean);
    const { data } = await apiClient.post<Job>("/pdf/pages/reorder", { file_id: reoFile, new_order });
    setReoJobId(data.id);
  }

  async function runPageNumbers() {
    const { data } = await apiClient.post<Job>("/pdf/pages/numbers", { file_id: numFile, position: numPosition });
    setNumJobId(data.id);
  }

  async function runHeaderFooter() {
    const { data } = await apiClient.post<Job>("/pdf/pages/header-footer", {
      file_id: hfFile, header_text: headerText || null, footer_text: footerText || null,
    });
    setHfJobId(data.id);
  }

  async function runRotate() {
    const page_numbers = rotPages.split(",").map((n) => Number(n.trim())).filter(Boolean);
    const { data } = await apiClient.post<Job>("/pdf/rotate", { file_id: rotFile, page_numbers, degrees: rotDegrees });
    setRotJobId(data.id);
  }

  async function runExtract() {
    const page_numbers = extPages.split(",").map((n) => Number(n.trim())).filter(Boolean);
    const { data } = await apiClient.post<Job>("/pdf/extract", { file_id: extFile, page_numbers });
    setExtJobId(data.id);
  }

  async function runCrop() {
    const { data } = await apiClient.post<Job>("/pdf/crop", { file_id: cropFile, margins: cropMargins });
    setCropJobId(data.id);
  }

  async function runReplacePages() {
    const page_numbers = replPages.split(",").map((n) => Number(n.trim())).filter(Boolean);
    const { data } = await apiClient.post<Job>("/pdf/replace-pages", {
      file_id: replFile, replacement_file_id: replReplacementFile, page_numbers,
    });
    setReplJobId(data.id);
  }

  async function runRemoveWatermark() {
    const { data } = await apiClient.post<Job>("/pdf/watermark/remove", { file_id: rwFile, text: rwText });
    setRwJobId(data.id);
  }

  async function loadBookmarks() {
    const { data } = await apiClient.get<{ level: number; title: string; page: number }[]>(`/pdf/bookmarks/${bmFile}`);
    setBmList(data);
  }

  function addBookmarkEntry() {
    if (!bmTitle.trim()) return;
    setBmList((prev) => [...prev, { level: 1, title: bmTitle.trim(), page: bmPage }]);
    setBmTitle("");
  }

  async function saveBookmarks() {
    setBmSaving(true);
    try {
      await apiClient.post("/pdf/bookmarks", { file_id: bmFile, bookmarks: bmList });
    } finally {
      setBmSaving(false);
    }
  }

  return (
    <>
      <Topbar title="Organize" />
      <main className="flex-1 space-y-4 overflow-y-auto p-6">
        {/* Mode Selector Tabs */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-3 dark:border-slate-800">
          <button
            onClick={() => setOrganizeMode("visual")}
            className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition ${
              organizeMode === "visual"
                ? "bg-ink text-white dark:bg-white dark:text-ink shadow-sm"
                : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            }`}
          >
            <LayoutGrid size={16} />
            Visual Page Organizer
          </button>
          <button
            onClick={() => setOrganizeMode("tools")}
            className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition ${
              organizeMode === "tools"
                ? "bg-ink text-white dark:bg-white dark:text-ink shadow-sm"
                : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            }`}
          >
            <SlidersHorizontal size={16} />
            Individual Tool Forms
          </button>
        </div>

        {organizeMode === "visual" ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-ink/30">
            <div className="mb-4 max-w-sm">
              <FileSelect
                value={visualFileId}
                onChange={(v) => setVisualFileId(v as string)}
                label="Choose document to visually organize"
              />
            </div>
            {visualFileId ? (
              <VisualPageOrganizer fileId={visualFileId} />
            ) : (
              <div className="rounded-xl border border-dashed border-slate-200 p-12 text-center text-sm text-slate-500 dark:border-slate-800">
                <LayoutGrid size={32} className="mx-auto mb-3 text-slate-400" />
                <p className="font-semibold text-ink dark:text-white">Interactive Visual Page Organizer</p>
                <p className="mt-1 text-xs text-slate-400">
                  Select any PDF document above to view all rendered pages and visually reorder, rotate, or exclude pages with 1 click.
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <ToolCard title="Merge PDFs" description="Combine multiple files into one, in the order selected.">
          <FileSelect value={mergeFiles} onChange={(v) => setMergeFiles(v as string[])} multiple label="Files to merge (select 2+)" />
          <div className="mt-3">
            <PrimaryButton onClick={runMerge} disabled={mergeFiles.length < 2}>
              Merge
            </PrimaryButton>
          </div>
          <JobStatusPanel jobId={mergeJobId} />
        </ToolCard>

        <ToolCard title="Compress PDF" description="Reduce file size by recompressing embedded images.">
          <FileSelect value={compressFile} onChange={(v) => setCompressFile(v as string)} label="File to compress" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Quality</span>
            <select
              value={quality}
              onChange={(e) => setQuality(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            >
              <option value="low">Low compression (best quality)</option>
              <option value="medium">Medium</option>
              <option value="high">High compression (smallest file)</option>
              <option value="custom">Custom</option>
            </select>
          </label>
          {quality === "custom" && (
            <div className="mt-3 grid grid-cols-2 gap-3">
              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Target DPI</span>
                <input
                  type="number"
                  min={36}
                  max={300}
                  value={customDpi}
                  onChange={(e) => setCustomDpi(Number(e.target.value))}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                />
              </label>
              <label className="block">
                <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">JPEG quality (1-95)</span>
                <input
                  type="number"
                  min={1}
                  max={95}
                  value={customQuality}
                  onChange={(e) => setCustomQuality(Number(e.target.value))}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                />
              </label>
            </div>
          )}
          <div className="mt-3">
            <PrimaryButton onClick={runCompress} disabled={!compressFile}>
              Compress
            </PrimaryButton>
          </div>
          <JobStatusPanel jobId={compressJobId} />
        </ToolCard>

        <ToolCard title="Split PDF" description="Extract page ranges into separate files, e.g. 1-3, 5-5.">
          <FileSelect value={splitFile} onChange={(v) => setSplitFile(v as string)} label="File to split" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page ranges</span>
            <input
              value={ranges}
              onChange={(e) => setRanges(e.target.value)}
              placeholder="1-3, 5-5"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runSplit} disabled={!splitFile}>
              Split
            </PrimaryButton>
          </div>
          <JobStatusPanel jobId={splitJobId} />
        </ToolCard>

        <ToolCard title="Delete pages" description="Remove specific pages, e.g. 2, 4, 7.">
          <FileSelect value={delFile} onChange={(v) => setDelFile(v as string)} label="File" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page numbers</span>
            <input
              value={delPages}
              onChange={(e) => setDelPages(e.target.value)}
              placeholder="2, 4, 7"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runDeletePages} disabled={!delFile || !delPages}>Delete pages</PrimaryButton>
          </div>
          <JobStatusPanel jobId={delJobId} />
        </ToolCard>

        <ToolCard title="Insert blank page" description="Insert a blank page at a given position.">
          <FileSelect value={insFile} onChange={(v) => setInsFile(v as string)} label="File" />
          <label className="mt-3 block max-w-[160px]">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Position</span>
            <input
              type="number"
              min={1}
              value={insPosition}
              onChange={(e) => setInsPosition(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runInsertBlank} disabled={!insFile}>Insert blank page</PrimaryButton>
          </div>
          <JobStatusPanel jobId={insJobId} />
        </ToolCard>

        <ToolCard title="Duplicate page" description="Insert a copy of a page immediately after itself.">
          <FileSelect value={dupFile} onChange={(v) => setDupFile(v as string)} label="File" />
          <label className="mt-3 block max-w-[160px]">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page number</span>
            <input
              type="number"
              min={1}
              value={dupPage}
              onChange={(e) => setDupPage(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runDuplicate} disabled={!dupFile}>Duplicate page</PrimaryButton>
          </div>
          <JobStatusPanel jobId={dupJobId} />
        </ToolCard>

        <ToolCard title="Rearrange pages" description="Reorder every page, e.g. 3, 1, 2 moves page 3 to the front.">
          <FileSelect value={reoFile} onChange={(v) => setReoFile(v as string)} label="File" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">New order</span>
            <input
              value={reoOrder}
              onChange={(e) => setReoOrder(e.target.value)}
              placeholder="3, 1, 2"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runReorder} disabled={!reoFile || !reoOrder}>Rearrange</PrimaryButton>
          </div>
          <JobStatusPanel jobId={reoJobId} />
        </ToolCard>

        <ToolCard title="Add page numbers" description="Stamp a page number onto every page.">
          <FileSelect value={numFile} onChange={(v) => setNumFile(v as string)} label="File" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Position</span>
            <select
              value={numPosition}
              onChange={(e) => setNumPosition(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            >
              <option value="bottom-center">Bottom center</option>
              <option value="bottom-left">Bottom left</option>
              <option value="bottom-right">Bottom right</option>
              <option value="top-center">Top center</option>
              <option value="top-left">Top left</option>
              <option value="top-right">Top right</option>
            </select>
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runPageNumbers} disabled={!numFile}>Add page numbers</PrimaryButton>
          </div>
          <JobStatusPanel jobId={numJobId} />
        </ToolCard>

        <ToolCard title="Header & footer" description="Add repeating header/footer text to every page.">
          <FileSelect value={hfFile} onChange={(v) => setHfFile(v as string)} label="File" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Header text</span>
            <input
              value={headerText}
              onChange={(e) => setHeaderText(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Footer text</span>
            <input
              value={footerText}
              onChange={(e) => setFooterText(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runHeaderFooter} disabled={!hfFile || (!headerText && !footerText)}>
              Apply
            </PrimaryButton>
          </div>
          <JobStatusPanel jobId={hfJobId} />
        </ToolCard>

        <ToolCard title="Rotate pages" description="Rotate specific pages by 90/180/270 degrees.">
          <FileSelect value={rotFile} onChange={(v) => setRotFile(v as string)} label="File" />
          <div className="mt-3 grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page numbers</span>
              <input
                value={rotPages}
                onChange={(e) => setRotPages(e.target.value)}
                placeholder="1, 2, 3"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
              />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Degrees</span>
              <select
                value={rotDegrees}
                onChange={(e) => setRotDegrees(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
              >
                <option value={90}>90°</option>
                <option value={180}>180°</option>
                <option value={270}>270°</option>
                <option value={-90}>-90°</option>
              </select>
            </label>
          </div>
          <div className="mt-3">
            <PrimaryButton onClick={runRotate} disabled={!rotFile || !rotPages}>Rotate</PrimaryButton>
          </div>
          <JobStatusPanel jobId={rotJobId} />
        </ToolCard>

        <ToolCard title="Extract pages" description="Pull specific pages out into a brand-new PDF.">
          <FileSelect value={extFile} onChange={(v) => setExtFile(v as string)} label="File" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page numbers</span>
            <input
              value={extPages}
              onChange={(e) => setExtPages(e.target.value)}
              placeholder="1, 3, 5"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runExtract} disabled={!extFile || !extPages}>Extract</PrimaryButton>
          </div>
          <JobStatusPanel jobId={extJobId} />
        </ToolCard>

        <ToolCard title="Crop pages" description="Trim margins inward from every page's edge (in PDF points).">
          <FileSelect value={cropFile} onChange={(v) => setCropFile(v as string)} label="File" />
          <div className="mt-3 grid grid-cols-4 gap-2">
            {(["left", "top", "right", "bottom"] as const).map((side) => (
              <label key={side} className="block">
                <span className="mb-1.5 block text-xs font-medium capitalize text-ink dark:text-white">{side}</span>
                <input
                  type="number"
                  min={0}
                  value={cropMargins[side]}
                  onChange={(e) => setCropMargins((m) => ({ ...m, [side]: Number(e.target.value) }))}
                  className="w-full rounded-lg border border-slate-300 bg-white px-2 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                />
              </label>
            ))}
          </div>
          <div className="mt-3">
            <PrimaryButton onClick={runCrop} disabled={!cropFile}>Crop</PrimaryButton>
          </div>
          <JobStatusPanel jobId={cropJobId} />
        </ToolCard>

        <ToolCard title="Replace pages" description="Swap specific pages with pages from another PDF.">
          <FileSelect value={replFile} onChange={(v) => setReplFile(v as string)} label="File to edit" />
          <div className="mt-3">
            <FileSelect value={replReplacementFile} onChange={(v) => setReplReplacementFile(v as string)} label="Replacement pages come from" />
          </div>
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page numbers to replace</span>
            <input
              value={replPages}
              onChange={(e) => setReplPages(e.target.value)}
              placeholder="2, 3"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <p className="mt-2 text-xs text-slate-500">Page 1 of the replacement file fills the first number listed, page 2 the second, and so on.</p>
          <div className="mt-3">
            <PrimaryButton onClick={runReplacePages} disabled={!replFile || !replReplacementFile || !replPages}>
              Replace pages
            </PrimaryButton>
          </div>
          <JobStatusPanel jobId={replJobId} />
        </ToolCard>

        <ToolCard title="Remove watermark" description="Strip every occurrence of a known watermark text from the document.">
          <FileSelect value={rwFile} onChange={(v) => setRwFile(v as string)} label="File" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Watermark text</span>
            <input
              value={rwText}
              onChange={(e) => setRwText(e.target.value)}
              placeholder="CONFIDENTIAL"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <p className="mt-2 text-xs text-slate-500">Works for text-based watermarks only — for a logo or scanned stamp, use Redact instead.</p>
          <div className="mt-3">
            <PrimaryButton onClick={runRemoveWatermark} disabled={!rwFile || !rwText}>Remove watermark</PrimaryButton>
          </div>
          <JobStatusPanel jobId={rwJobId} />
        </ToolCard>

        <ToolCard title="Bookmarks / table of contents" description="Build or replace a PDF's outline.">
          <FileSelect value={bmFile} onChange={(v) => { setBmFile(v as string); setBmList([]); }} label="File" />
          <div className="mt-3">
            <PrimaryButton onClick={loadBookmarks} disabled={!bmFile}>Load existing bookmarks</PrimaryButton>
          </div>
          {bmList.length > 0 && (
            <ul className="mt-3 space-y-1 text-sm text-slate-500">
              {bmList.map((b, i) => (
                <li key={i} className="flex justify-between border-b border-slate-100 py-1 dark:border-slate-800">
                  <span>{b.title}</span>
                  <span>page {b.page}</span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3 grid grid-cols-[1fr_100px] gap-2">
            <input
              value={bmTitle}
              onChange={(e) => setBmTitle(e.target.value)}
              placeholder="Bookmark title"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
            <input
              type="number"
              min={1}
              value={bmPage}
              onChange={(e) => setBmPage(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </div>
          <div className="mt-3 flex gap-2">
            <PrimaryButton onClick={addBookmarkEntry} disabled={!bmFile || !bmTitle.trim()}>Add entry</PrimaryButton>
            <PrimaryButton onClick={saveBookmarks} disabled={!bmFile || bmList.length === 0 || bmSaving}>
              {bmSaving ? "Saving…" : "Save bookmarks"}
            </PrimaryButton>
          </div>
        </ToolCard>
          </div>
        )}
      </main>
    </>
  );
}
