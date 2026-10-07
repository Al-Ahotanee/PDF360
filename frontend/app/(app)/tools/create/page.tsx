"use client";

import { useState } from "react";
import { Topbar } from "@/components/layout/Topbar";
import { ToolCard, PrimaryButton } from "@/components/tools/ToolCard";
import { apiClient } from "@/lib/api/client";
import type { PDFFile } from "@/types/api";

async function downloadFile(fileId: string, filename: string) {
  const response = await apiClient.get(`/files/${fileId}/download`, { responseType: "blob" });
  const url = window.URL.createObjectURL(response.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

function DownloadButton({ file }: { file: PDFFile | null }) {
  if (!file) return null;
  return (
    <button
      onClick={() => downloadFile(file.id, file.original_filename)}
      className="mt-3 rounded-lg bg-ink px-3 py-1.5 text-xs font-medium text-white hover:bg-ink-light"
    >
      Download PDF
    </button>
  );
}

export default function CreateToolsPage() {
  // Blank PDF
  const [blankPages, setBlankPages] = useState(1);
  const [blankSize, setBlankSize] = useState("letter");
  const [blankResult, setBlankResult] = useState<PDFFile | null>(null);
  const [blankBusy, setBlankBusy] = useState(false);

  // Text to PDF
  const [text, setText] = useState("");
  const [textResult, setTextResult] = useState<PDFFile | null>(null);
  const [textBusy, setTextBusy] = useState(false);

  // Invoice
  const [invNumber, setInvNumber] = useState("");
  const [invDate, setInvDate] = useState("");
  const [invFrom, setInvFrom] = useState("");
  const [invTo, setInvTo] = useState("");
  const [invItems, setInvItems] = useState([{ description: "", quantity: 1, unit_price: 0 }]);
  const [invResult, setInvResult] = useState<PDFFile | null>(null);
  const [invBusy, setInvBusy] = useState(false);

  // Certificate
  const [certRecipient, setCertRecipient] = useState("");
  const [certTitle, setCertTitle] = useState("Certificate of Achievement");
  const [certBody, setCertBody] = useState("");
  const [certDate, setCertDate] = useState("");
  const [certSigner, setCertSigner] = useState("");
  const [certResult, setCertResult] = useState<PDFFile | null>(null);
  const [certBusy, setCertBusy] = useState(false);

  // Report
  const [reportTitle, setReportTitle] = useState("");
  const [reportSections, setReportSections] = useState([{ heading: "", body: "" }]);
  const [reportResult, setReportResult] = useState<PDFFile | null>(null);
  const [reportBusy, setReportBusy] = useState(false);

  async function createBlank() {
    setBlankBusy(true);
    try {
      const { data } = await apiClient.post<PDFFile>("/create/blank", { pages: blankPages, page_size: blankSize });
      setBlankResult(data);
    } finally {
      setBlankBusy(false);
    }
  }

  async function createFromText() {
    setTextBusy(true);
    try {
      const { data } = await apiClient.post<PDFFile>("/create/from-text", { text });
      setTextResult(data);
    } finally {
      setTextBusy(false);
    }
  }

  async function createInvoice() {
    setInvBusy(true);
    try {
      const { data } = await apiClient.post<PDFFile>("/create/invoice", {
        invoice_number: invNumber,
        date: invDate,
        from: { name: invFrom },
        to: { name: invTo },
        line_items: invItems.filter((i) => i.description),
      });
      setInvResult(data);
    } finally {
      setInvBusy(false);
    }
  }

  async function createCertificate() {
    setCertBusy(true);
    try {
      const { data } = await apiClient.post<PDFFile>("/create/certificate", {
        recipient: certRecipient, title: certTitle, body: certBody, date: certDate,
        signer: certSigner || null,
      });
      setCertResult(data);
    } finally {
      setCertBusy(false);
    }
  }

  async function createReport() {
    setReportBusy(true);
    try {
      const { data } = await apiClient.post<PDFFile>("/create/report", {
        title: reportTitle, sections: reportSections.filter((s) => s.heading),
      });
      setReportResult(data);
    } finally {
      setReportBusy(false);
    }
  }

  return (
    <>
      <Topbar title="Create" />
      <main className="flex-1 space-y-4 overflow-y-auto p-6">
        <ToolCard title="Blank PDF" description="Create an empty PDF with a given number of pages.">
          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Pages</span>
              <input
                type="number"
                min={1}
                value={blankPages}
                onChange={(e) => setBlankPages(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
              />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page size</span>
              <select
                value={blankSize}
                onChange={(e) => setBlankSize(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
              >
                <option value="letter">Letter</option>
                <option value="a4">A4</option>
              </select>
            </label>
          </div>
          <div className="mt-3">
            <PrimaryButton onClick={createBlank} disabled={blankBusy}>{blankBusy ? "Creating…" : "Create blank PDF"}</PrimaryButton>
          </div>
          <DownloadButton file={blankResult} />
        </ToolCard>

        <ToolCard title="PDF from text" description="Paste plain text and get a formatted, paginated PDF.">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
            placeholder="Paste or type your text here. Separate paragraphs with a blank line."
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
          />
          <div className="mt-3">
            <PrimaryButton onClick={createFromText} disabled={!text.trim() || textBusy}>
              {textBusy ? "Creating…" : "Create PDF"}
            </PrimaryButton>
          </div>
          <DownloadButton file={textResult} />
        </ToolCard>

        <ToolCard title="Invoice" description="Generate a simple, professional invoice.">
          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Invoice #</span>
              <input value={invNumber} onChange={(e) => setInvNumber(e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Date</span>
              <input type="date" value={invDate} onChange={(e) => setInvDate(e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">From</span>
              <input value={invFrom} onChange={(e) => setInvFrom(e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Bill to</span>
              <input value={invTo} onChange={(e) => setInvTo(e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
            </label>
          </div>

          <div className="mt-4 space-y-2">
            {invItems.map((item, i) => (
              <div key={i} className="grid grid-cols-[1fr_80px_100px] gap-2">
                <input
                  placeholder="Description"
                  value={item.description}
                  onChange={(e) => setInvItems((items) => items.map((it, j) => (j === i ? { ...it, description: e.target.value } : it)))}
                  className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                />
                <input
                  type="number"
                  placeholder="Qty"
                  value={item.quantity}
                  onChange={(e) => setInvItems((items) => items.map((it, j) => (j === i ? { ...it, quantity: Number(e.target.value) } : it)))}
                  className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                />
                <input
                  type="number"
                  placeholder="Unit price"
                  value={item.unit_price}
                  onChange={(e) => setInvItems((items) => items.map((it, j) => (j === i ? { ...it, unit_price: Number(e.target.value) } : it)))}
                  className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                />
              </div>
            ))}
            <button
              onClick={() => setInvItems((items) => [...items, { description: "", quantity: 1, unit_price: 0 }])}
              className="text-xs font-medium text-brand hover:underline"
            >
              + Add line item
            </button>
          </div>

          <div className="mt-3">
            <PrimaryButton onClick={createInvoice} disabled={!invNumber || !invDate || invBusy}>
              {invBusy ? "Generating…" : "Generate invoice"}
            </PrimaryButton>
          </div>
          <DownloadButton file={invResult} />
        </ToolCard>

        <ToolCard title="Certificate" description="Generate a certificate of achievement / completion.">
          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Recipient</span>
              <input value={certRecipient} onChange={(e) => setCertRecipient(e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Date</span>
              <input type="date" value={certDate} onChange={(e) => setCertDate(e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
            </label>
            <label className="col-span-2 block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Title</span>
              <input value={certTitle} onChange={(e) => setCertTitle(e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
            </label>
            <label className="col-span-2 block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Body text</span>
              <input value={certBody} onChange={(e) => setCertBody(e.target.value)} placeholder="For outstanding completion of..." className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
            </label>
            <label className="col-span-2 block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Signer (optional)</span>
              <input value={certSigner} onChange={(e) => setCertSigner(e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
            </label>
          </div>
          <div className="mt-3">
            <PrimaryButton onClick={createCertificate} disabled={!certRecipient || !certDate || certBusy}>
              {certBusy ? "Generating…" : "Generate certificate"}
            </PrimaryButton>
          </div>
          <DownloadButton file={certResult} />
        </ToolCard>

        <ToolCard title="Report" description="Generate a structured report with sections.">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Title</span>
            <input value={reportTitle} onChange={(e) => setReportTitle(e.target.value)} className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink" />
          </label>
          <div className="mt-4 space-y-3">
            {reportSections.map((s, i) => (
              <div key={i} className="space-y-2 rounded-lg border border-slate-200 p-3 dark:border-slate-800">
                <input
                  placeholder="Section heading"
                  value={s.heading}
                  onChange={(e) => setReportSections((secs) => secs.map((sec, j) => (j === i ? { ...sec, heading: e.target.value } : sec)))}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                />
                <textarea
                  placeholder="Section body"
                  value={s.body}
                  rows={3}
                  onChange={(e) => setReportSections((secs) => secs.map((sec, j) => (j === i ? { ...sec, body: e.target.value } : sec)))}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                />
              </div>
            ))}
            <button
              onClick={() => setReportSections((secs) => [...secs, { heading: "", body: "" }])}
              className="text-xs font-medium text-brand hover:underline"
            >
              + Add section
            </button>
          </div>
          <div className="mt-3">
            <PrimaryButton onClick={createReport} disabled={!reportTitle || reportBusy}>
              {reportBusy ? "Generating…" : "Generate report"}
            </PrimaryButton>
          </div>
          <DownloadButton file={reportResult} />
        </ToolCard>
      </main>
    </>
  );
}
