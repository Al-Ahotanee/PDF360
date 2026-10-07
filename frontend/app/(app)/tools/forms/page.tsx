"use client";

import { useState } from "react";
import { Topbar } from "@/components/layout/Topbar";
import { FileSelect } from "@/components/tools/FileSelect";
import { ToolCard, PrimaryButton } from "@/components/tools/ToolCard";
import { apiClient } from "@/lib/api/client";
import type { PDFFile } from "@/types/api";

type FormField = {
  page: number;
  field_name: string;
  field_type: string;
  field_value: string | boolean | null;
};

async function downloadFile(fileId: string, filename: string) {
  const response = await apiClient.get(`/files/${fileId}/download`, { responseType: "blob" });
  const url = window.URL.createObjectURL(response.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

export default function FormsToolsPage() {
  // Create text field
  const [textFile, setTextFile] = useState("");
  const [textPage, setTextPage] = useState(1);
  const [textFieldName, setTextFieldName] = useState("");
  const [textDefault, setTextDefault] = useState("");
  const [textCoords, setTextCoords] = useState({ x0: 72, y0: 700, x1: 300, y1: 725 });
  const [creatingText, setCreatingText] = useState(false);
  const [textResult, setTextResult] = useState<PDFFile | null>(null);

  // Create checkbox field
  const [cbFile, setCbFile] = useState("");
  const [cbPage, setCbPage] = useState(1);
  const [cbFieldName, setCbFieldName] = useState("");
  const [cbChecked, setCbChecked] = useState(false);
  const [cbCoords, setCbCoords] = useState({ x0: 72, y0: 660, x1: 90, y1: 678 });
  const [creatingCb, setCreatingCb] = useState(false);
  const [cbResult, setCbResult] = useState<PDFFile | null>(null);

  // List / fill fields
  const [fillFile, setFillFile] = useState("");
  const [fields, setFields] = useState<FormField[] | null>(null);
  const [values, setValues] = useState<Record<string, string | boolean>>({});
  const [loadingFields, setLoadingFields] = useState(false);
  const [filling, setFilling] = useState(false);
  const [fillResult, setFillResult] = useState<PDFFile | null>(null);

  async function createTextField() {
    setCreatingText(true);
    try {
      const { data } = await apiClient.post<PDFFile>("/editor/form-fields/text", {
        file_id: textFile,
        page: textPage,
        ...textCoords,
        field_name: textFieldName,
        default_value: textDefault,
      });
      setTextResult(data);
    } finally {
      setCreatingText(false);
    }
  }

  async function createCheckboxField() {
    setCreatingCb(true);
    try {
      const { data } = await apiClient.post<PDFFile>("/editor/form-fields/checkbox", {
        file_id: cbFile,
        page: cbPage,
        ...cbCoords,
        field_name: cbFieldName,
        checked: cbChecked,
      });
      setCbResult(data);
    } finally {
      setCreatingCb(false);
    }
  }

  async function loadFields() {
    setLoadingFields(true);
    try {
      const { data } = await apiClient.get<FormField[]>(`/editor/form-fields/${fillFile}`);
      setFields(data);
      const initial: Record<string, string | boolean> = {};
      data.forEach((f) => {
        initial[f.field_name] = f.field_value ?? (f.field_type === "checkbox" ? false : "");
      });
      setValues(initial);
      setFillResult(null);
    } finally {
      setLoadingFields(false);
    }
  }

  async function submitFill() {
    setFilling(true);
    try {
      const { data } = await apiClient.post<PDFFile>("/editor/form-fields/fill", {
        file_id: fillFile,
        values,
      });
      setFillResult(data);
    } finally {
      setFilling(false);
    }
  }

  return (
    <>
      <Topbar title="Forms" />
      <main className="flex-1 space-y-4 overflow-y-auto p-6">
        <ToolCard title="Fill a form" description="Load a PDF's form fields, fill them in, and export a completed copy.">
          <FileSelect value={fillFile} onChange={(v) => { setFillFile(v as string); setFields(null); }} label="Form file" />
          <div className="mt-3">
            <PrimaryButton onClick={loadFields} disabled={!fillFile || loadingFields}>
              {loadingFields ? "Loading fields…" : "Load fields"}
            </PrimaryButton>
          </div>

          {fields && fields.length === 0 && (
            <p className="mt-3 text-sm text-slate-500">This file has no form fields yet — create some below first.</p>
          )}

          {fields && fields.length > 0 && (
            <div className="mt-4 space-y-3">
              {fields.map((f) => (
                <label key={f.field_name} className="block">
                  <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">
                    {f.field_name} <span className="text-xs text-slate-400">({f.field_type}, page {f.page})</span>
                  </span>
                  {f.field_type === "checkbox" ? (
                    <input
                      type="checkbox"
                      checked={Boolean(values[f.field_name])}
                      onChange={(e) => setValues((v) => ({ ...v, [f.field_name]: e.target.checked }))}
                    />
                  ) : (
                    <input
                      value={String(values[f.field_name] ?? "")}
                      onChange={(e) => setValues((v) => ({ ...v, [f.field_name]: e.target.value }))}
                      className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
                    />
                  )}
                </label>
              ))}
              <PrimaryButton onClick={submitFill} disabled={filling}>
                {filling ? "Filling…" : "Fill & export"}
              </PrimaryButton>
              {fillResult && (
                <button
                  onClick={() => downloadFile(fillResult.id, fillResult.original_filename)}
                  className="ml-2 rounded-lg bg-ink px-3 py-1.5 text-xs font-medium text-white hover:bg-ink-light"
                >
                  Download filled PDF
                </button>
              )}
            </div>
          )}
        </ToolCard>

        <ToolCard title="Add a text field" description="Place a fillable text field on a page.">
          <FileSelect value={textFile} onChange={(v) => setTextFile(v as string)} label="File" />
          <div className="mt-3 grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page</span>
              <input
                type="number"
                min={1}
                value={textPage}
                onChange={(e) => setTextPage(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
              />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Field name</span>
              <input
                value={textFieldName}
                onChange={(e) => setTextFieldName(e.target.value)}
                placeholder="full_name"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
              />
            </label>
          </div>
          <label className="mt-3 block">
            <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Default value (optional)</span>
            <input
              value={textDefault}
              onChange={(e) => setTextDefault(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
          </label>
          <p className="mt-3 text-xs text-slate-500">
            Position (PDF points from bottom-left): default box is a 228×25pt field near the top of the page — adjust
            per-field if needed via the API.
          </p>
          <div className="mt-3">
            <PrimaryButton onClick={createTextField} disabled={!textFile || !textFieldName || creatingText}>
              {creatingText ? "Adding…" : "Add text field"}
            </PrimaryButton>
          </div>
          {textResult && (
            <button
              onClick={() => downloadFile(textResult.id, textResult.original_filename)}
              className="mt-3 rounded-lg bg-ink px-3 py-1.5 text-xs font-medium text-white hover:bg-ink-light"
            >
              Download updated PDF
            </button>
          )}
        </ToolCard>

        <ToolCard title="Add a checkbox field" description="Place a fillable checkbox on a page.">
          <FileSelect value={cbFile} onChange={(v) => setCbFile(v as string)} label="File" />
          <div className="mt-3 grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Page</span>
              <input
                type="number"
                min={1}
                value={cbPage}
                onChange={(e) => setCbPage(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
              />
            </label>
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">Field name</span>
              <input
                value={cbFieldName}
                onChange={(e) => setCbFieldName(e.target.value)}
                placeholder="agree_to_terms"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
              />
            </label>
          </div>
          <label className="mt-3 flex items-center gap-2 text-sm">
            <input type="checkbox" checked={cbChecked} onChange={(e) => setCbChecked(e.target.checked)} />
            Checked by default
          </label>
          <div className="mt-3">
            <PrimaryButton onClick={createCheckboxField} disabled={!cbFile || !cbFieldName || creatingCb}>
              {creatingCb ? "Adding…" : "Add checkbox field"}
            </PrimaryButton>
          </div>
          {cbResult && (
            <button
              onClick={() => downloadFile(cbResult.id, cbResult.original_filename)}
              className="mt-3 rounded-lg bg-ink px-3 py-1.5 text-xs font-medium text-white hover:bg-ink-light"
            >
              Download updated PDF
            </button>
          )}
        </ToolCard>
      </main>
    </>
  );
}
