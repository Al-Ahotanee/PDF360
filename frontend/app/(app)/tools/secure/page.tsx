"use client";

import { useState } from "react";
import { Topbar } from "@/components/layout/Topbar";
import { FileSelect } from "@/components/tools/FileSelect";
import { JobStatusPanel } from "@/components/tools/JobStatusPanel";
import { RedactionPicker } from "@/components/tools/RedactionPicker";
import { ToolCard, PrimaryButton } from "@/components/tools/ToolCard";
import { apiClient } from "@/lib/api/client";
import type { Job } from "@/types/api";

type Box = { x0: number; y0: number; x1: number; y1: number };

export default function SecureToolsPage() {
  const [encFile, setEncFile] = useState("");
  const [password, setPassword] = useState("");
  const [encJobId, setEncJobId] = useState<string | null>(null);

  const [decFile, setDecFile] = useState("");
  const [decPassword, setDecPassword] = useState("");
  const [decJobId, setDecJobId] = useState<string | null>(null);

  const [wmFile, setWmFile] = useState("");
  const [wmText, setWmText] = useState("CONFIDENTIAL");
  const [wmJobId, setWmJobId] = useState<string | null>(null);

  const [redactFile, setRedactFile] = useState("");
  const [redactPage, setRedactPage] = useState(1);
  const [redactBoxes, setRedactBoxes] = useState<Box[]>([]);
  const [redactJobId, setRedactJobId] = useState<string | null>(null);

  const [signFile, setSignFile] = useState("");
  const [signerName, setSignerName] = useState("");
  const [signReason, setSignReason] = useState("");
  const [signJobId, setSignJobId] = useState<string | null>(null);

  const [verifyFile, setVerifyFile] = useState("");
  const [verifyResult, setVerifyResult] = useState<Record<string, unknown> | null>(null);
  const [verifyLoading, setVerifyLoading] = useState(false);

  const [permFile, setPermFile] = useState("");
  const [allowPrinting, setAllowPrinting] = useState(true);
  const [allowCopying, setAllowCopying] = useState(true);
  const [allowEditing, setAllowEditing] = useState(false);
  const [allowAnnotations, setAllowAnnotations] = useState(true);
  const [permJobId, setPermJobId] = useState<string | null>(null);

  async function runEncrypt() {
    const { data } = await apiClient.post<Job>("/pdf/encrypt", { file_id: encFile, user_password: password });
    setEncJobId(data.id);
  }
  async function runDecrypt() {
    const { data } = await apiClient.post<Job>("/pdf/decrypt", { file_id: decFile, password: decPassword });
    setDecJobId(data.id);
  }
  async function runWatermark() {
    const { data } = await apiClient.post<Job>("/pdf/watermark", { file_id: wmFile, text: wmText, opacity: 0.3 });
    setWmJobId(data.id);
  }

  async function runRedact() {
    const redactions = redactBoxes.map((b) => ({ page: redactPage, ...b }));
    const { data } = await apiClient.post<Job>("/pdf/redact", { file_id: redactFile, redactions });
    setRedactJobId(data.id);
  }

  async function runSign() {
    const { data } = await apiClient.post<Job>("/pdf/sign", {
      file_id: signFile, signer_name: signerName, reason: signReason || null,
    });
    setSignJobId(data.id);
  }

  async function runVerify() {
    setVerifyLoading(true);
    try {
      const { data } = await apiClient.get(`/pdf/sign/${verifyFile}/verify`);
      setVerifyResult(data);
    } finally {
      setVerifyLoading(false);
    }
  }

  async function runPermissions() {
    const { data } = await apiClient.post<Job>("/pdf/permissions", {
      file_id: permFile, allow_printing: allowPrinting, allow_copying: allowCopying,
      allow_editing: allowEditing, allow_annotations: allowAnnotations,
    });
    setPermJobId(data.id);
  }

  return (
    <>
      <Topbar title="Secure" />
      <main className="flex-1 space-y-4 overflow-y-auto p-6">
        <ToolCard title="Password-protect" description="Require a password to open this PDF.">
          <FileSelect value={encFile} onChange={(v) => setEncFile(v as string)} label="File to protect" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runEncrypt} disabled={!encFile || !password}>Protect</PrimaryButton>
          </div>
          <JobStatusPanel jobId={encJobId} />
        </ToolCard>

        <ToolCard title="Remove password" description="Unlock a password-protected PDF you have the password for.">
          <FileSelect value={decFile} onChange={(v) => setDecFile(v as string)} label="Protected file" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Current password</span>
            <input
              type="password"
              value={decPassword}
              onChange={(e) => setDecPassword(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runDecrypt} disabled={!decFile || !decPassword}>Remove password</PrimaryButton>
          </div>
          <JobStatusPanel jobId={decJobId} />
        </ToolCard>

        <ToolCard title="Add watermark" description="Stamp diagonal text across every page.">
          <FileSelect value={wmFile} onChange={(v) => setWmFile(v as string)} label="File to watermark" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Watermark text</span>
            <input
              value={wmText}
              onChange={(e) => setWmText(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runWatermark} disabled={!wmFile || !wmText}>Add watermark</PrimaryButton>
          </div>
          <JobStatusPanel jobId={wmJobId} />
        </ToolCard>

        <ToolCard title="Redact" description="Permanently remove sensitive content from a page — not just a visual cover.">
          <FileSelect value={redactFile} onChange={(v) => { setRedactFile(v as string); setRedactBoxes([]); }} label="File to redact" />
          {redactFile && (
            <>
              <label className="mt-3 block max-w-[120px]">
                <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page</span>
                <input
                  type="number"
                  min={1}
                  value={redactPage}
                  onChange={(e) => { setRedactPage(Number(e.target.value)); setRedactBoxes([]); }}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                />
              </label>
              <div className="mt-3">
                <RedactionPicker fileId={redactFile} page={redactPage} onBoxesChange={setRedactBoxes} />
              </div>
            </>
          )}
          <div className="mt-3">
            <PrimaryButton onClick={runRedact} disabled={!redactFile || redactBoxes.length === 0}>
              Apply redaction
            </PrimaryButton>
          </div>
          <JobStatusPanel jobId={redactJobId} />
        </ToolCard>

        <ToolCard title="Sign PDF" description="Stamp a visible e-signature block onto a page.">
          <FileSelect value={signFile} onChange={(v) => setSignFile(v as string)} label="File to sign" />
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Signer name</span>
            <input
              value={signerName}
              onChange={(e) => setSignerName(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Reason (optional)</span>
            <input
              value={signReason}
              onChange={(e) => setSignReason(e.target.value)}
              placeholder="e.g. Approved"
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={runSign} disabled={!signFile || !signerName}>Sign</PrimaryButton>
          </div>
          <JobStatusPanel jobId={signJobId} />
        </ToolCard>

        <ToolCard title="Verify signature" description="Check whether a PDF carries a PDF360 e-signature.">
          <FileSelect value={verifyFile} onChange={(v) => setVerifyFile(v as string)} label="File" />
          <div className="mt-3">
            <PrimaryButton onClick={runVerify} disabled={!verifyFile || verifyLoading}>
              {verifyLoading ? "Checking…" : "Verify"}
            </PrimaryButton>
          </div>
          {verifyResult && (
            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm dark:border-slate-800 dark:bg-ink/40">
              {verifyResult.is_signed ? (
                <ul className="space-y-1">
                  <li>Signer: {String(verifyResult.signer ?? "—")}</li>
                  {verifyResult.reason ? <li>Reason: {String(verifyResult.reason)}</li> : null}
                  <li>Signed: {String(verifyResult.timestamp ?? "—")}</li>
                </ul>
              ) : (
                <span className="text-slate-500">No PDF360 signature found on this document.</span>
              )}
            </div>
          )}
        </ToolCard>

        <ToolCard title="Set permissions" description="Restrict printing, copying, editing, or annotating without requiring a password to open.">
          <FileSelect value={permFile} onChange={(v) => setPermFile(v as string)} label="File" />
          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={allowPrinting} onChange={(e) => setAllowPrinting(e.target.checked)} />
              Allow printing
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={allowCopying} onChange={(e) => setAllowCopying(e.target.checked)} />
              Allow copying
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={allowEditing} onChange={(e) => setAllowEditing(e.target.checked)} />
              Allow editing
            </label>
            <label className="flex items-center gap-2">
              <input type="checkbox" checked={allowAnnotations} onChange={(e) => setAllowAnnotations(e.target.checked)} />
              Allow annotations
            </label>
          </div>
          <div className="mt-3">
            <PrimaryButton onClick={runPermissions} disabled={!permFile}>Apply permissions</PrimaryButton>
          </div>
          <JobStatusPanel jobId={permJobId} />
        </ToolCard>
      </main>
    </>
  );
}
