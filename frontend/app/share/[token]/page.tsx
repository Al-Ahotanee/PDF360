"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Lock, Download, AlertCircle, Loader2, ShieldCheck, FileText } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { formatBytes } from "@/lib/format";

interface PublicDocInfo {
  file_id: string;
  original_filename: string;
  size_bytes: number;
  mime_type: string | null;
  allow_download: boolean;
  has_password: boolean;
  created_at: string;
}

export default function PublicSharePage() {
  const params = useParams();
  const token = params?.token as string;

  const [loading, setLoading] = useState(true);
  const [docInfo, setDocInfo] = useState<PublicDocInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [passwordRequired, setPasswordRequired] = useState(false);
  const [password, setPassword] = useState("");
  const [unlocking, setUnlocking] = useState(false);

  const [pdfBlobUrl, setPdfBlobUrl] = useState<string | null>(null);
  const [loadingPdf, setLoadingPdf] = useState(false);

  async function loadDocument(pwd?: string) {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const url = `/collaboration/public/${token}${pwd ? `?password=${encodeURIComponent(pwd)}` : ""}`;
      const res = await apiClient.get<PublicDocInfo>(url);
      setDocInfo(res.data);
      setPasswordRequired(false);
      // Fetch the actual PDF content for viewing
      fetchPdfBlob(pwd);
    } catch (err: any) {
      if (err?.response?.status === 401) {
        setPasswordRequired(true);
      } else if (err?.response?.status === 410) {
        setError("This share link has expired and is no longer accessible.");
      } else if (err?.response?.status === 404) {
        setError("The shared document could not be found or access was revoked.");
      } else {
        setError("An error occurred while loading the shared document.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function fetchPdfBlob(pwd?: string) {
    setLoadingPdf(true);
    try {
      const downloadUrl = `/collaboration/public/${token}/download${pwd ? `?password=${encodeURIComponent(pwd)}` : ""}`;
      const res = await apiClient.get(downloadUrl, { responseType: "blob" });
      const objectUrl = window.URL.createObjectURL(res.data);
      setPdfBlobUrl(objectUrl);
    } catch (err) {
      console.error("Failed to load PDF preview bytes", err);
    } finally {
      setLoadingPdf(false);
    }
  }

  useEffect(() => {
    loadDocument();
  }, [token]);

  async function handleUnlock(e: React.FormEvent) {
    e.preventDefault();
    if (!password) return;
    setUnlocking(true);
    await loadDocument(password);
    setUnlocking(false);
  }

  async function handleDownload() {
    if (!pdfBlobUrl || !docInfo) return;
    const a = document.createElement("a");
    a.href = pdfBlobUrl;
    a.download = docInfo.original_filename;
    a.click();
  }

  return (
    <div className="flex h-screen w-screen flex-col bg-[#070b12] text-slate-100">
      {/* Header */}
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-white/10 bg-[#0d1524] px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-signal/10 text-signal font-bold text-sm">
            360
          </div>
          <div>
            <h1 className="text-sm font-semibold text-white truncate max-w-sm sm:max-w-md">
              {docInfo?.original_filename || "Secure Document Viewer"}
            </h1>
            <p className="text-xs text-slate-400">
              {docInfo ? `${formatBytes(docInfo.size_bytes)} · Shared via PDF360` : "PDF360 Enterprise Document Cloud"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {docInfo?.allow_download && pdfBlobUrl && (
            <button
              onClick={handleDownload}
              className="inline-flex items-center gap-1.5 rounded-xl bg-signal px-4 py-2 text-xs font-bold text-ink hover:bg-signal-light shadow-sm transition"
            >
              <Download size={14} /> Download File
            </button>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative flex flex-1 items-center justify-center overflow-hidden p-3 md:p-6">
        {loading ? (
          <div className="flex flex-col items-center gap-3 text-slate-400">
            <Loader2 className="animate-spin text-signal" size={32} />
            <p className="text-sm font-medium">Loading document…</p>
          </div>
        ) : error ? (
          <div className="flex max-w-md flex-col items-center rounded-3xl border border-red-500/20 bg-red-950/20 p-8 text-center shadow-2xl">
            <AlertCircle size={40} className="text-red-400 mb-3" />
            <h2 className="text-lg font-bold text-white">Access Denied</h2>
            <p className="mt-2 text-sm text-slate-300">{error}</p>
          </div>
        ) : passwordRequired ? (
          <form
            onSubmit={handleUnlock}
            className="flex w-full max-w-md flex-col items-center rounded-3xl border border-white/10 bg-[#0d1524] p-8 text-center shadow-2xl"
          >
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-signal/10 text-signal mb-4">
              <Lock size={26} />
            </div>
            <h2 className="text-xl font-bold text-white">Password Protected Document</h2>
            <p className="mt-1 text-xs text-slate-400">
              The sender protected this document with an access password.
            </p>

            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter document password"
              className="mt-6 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-signal focus:outline-none"
              autoFocus
            />

            <button
              type="submit"
              disabled={unlocking || !password}
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-signal px-4 py-2.5 text-sm font-bold text-ink hover:bg-signal-light disabled:opacity-50 transition shadow-md"
            >
              {unlocking ? <Loader2 size={16} className="animate-spin" /> : <ShieldCheck size={16} />}
              {unlocking ? "Unlocking…" : "Unlock Document"}
            </button>
          </form>
        ) : loadingPdf ? (
          <div className="flex flex-col items-center gap-3 text-slate-400">
            <Loader2 className="animate-spin text-signal" size={32} />
            <p className="text-sm font-medium">Decrypting and streaming document…</p>
          </div>
        ) : pdfBlobUrl ? (
          <iframe
            src={`${pdfBlobUrl}#toolbar=1`}
            className="h-full w-full max-w-6xl rounded-2xl border border-white/10 bg-white shadow-2xl"
            title={docInfo?.original_filename || "Document Viewer"}
          />
        ) : null}
      </main>
    </div>
  );
}
