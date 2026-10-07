"use client";

import { useState } from "react";
import { Users, FileText, Download, Shield } from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { UploadZone } from "@/components/files/UploadZone";
import { FileCard } from "@/components/files/FileCard";
import { useFiles } from "@/hooks/useFiles";
import { useSharedWithMe } from "@/hooks/useSharing";
import { apiClient } from "@/lib/api/client";
import { formatBytes, formatRelativeDate } from "@/lib/format";
import type { PDFFile } from "@/types/api";

export default function FilesPage() {
  const [activeTab, setActiveTab] = useState<"my-files" | "shared">("my-files");
  const { data: files, isLoading } = useFiles();
  const { data: sharedFiles, isLoading: isLoadingShared } = useSharedWithMe();

  async function handleDownloadShared(fileId: string, filename: string) {
    const response = await apiClient.get(`/files/${fileId}/download`, { responseType: "blob" });
    const url = window.URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <>
      <Topbar title="Document Workspace" />
      <main className="flex-1 overflow-y-auto p-6">
        <UploadZone />

        <div className="mt-8">
          <div className="mb-6 flex items-center gap-2 border-b border-slate-200 pb-2 dark:border-slate-800">
            <button
              onClick={() => setActiveTab("my-files")}
              className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition ${
                activeTab === "my-files"
                  ? "bg-ink text-white dark:bg-white dark:text-ink shadow-sm"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
              }`}
            >
              <FileText size={16} />
              My Files ({files?.length ?? 0})
            </button>
            <button
              onClick={() => setActiveTab("shared")}
              className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition ${
                activeTab === "shared"
                  ? "bg-ink text-white dark:bg-white dark:text-ink shadow-sm"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
              }`}
            >
              <Users size={16} />
              Shared with me ({sharedFiles?.length ?? 0})
            </button>
          </div>

          {activeTab === "my-files" ? (
            isLoading ? (
              <p className="text-sm text-slate-500">Loading files…</p>
            ) : !files || files.length === 0 ? (
              <p className="text-sm text-slate-500">No files yet. Upload one above to get started.</p>
            ) : (
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
                {files.map((file) => (
                  <FileCard key={file.id} file={file} />
                ))}
              </div>
            )
          ) : (
            isLoadingShared ? (
              <p className="text-sm text-slate-500">Loading shared files…</p>
            ) : !sharedFiles || sharedFiles.length === 0 ? (
              <p className="text-sm text-slate-500">No documents have been shared with you yet.</p>
            ) : (
              <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-ink/30">
                <table className="w-full text-sm">
                  <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wider text-slate-500 dark:border-slate-800 dark:bg-ink/50">
                    <tr>
                      <th className="px-4 py-3">File Name</th>
                      <th className="px-4 py-3">Shared By</th>
                      <th className="px-4 py-3">Permission</th>
                      <th className="px-4 py-3">Size</th>
                      <th className="px-4 py-3">Shared Date</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sharedFiles.map((item) => (
                      <tr key={item.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                        <td className="px-4 py-3 font-medium text-ink dark:text-white">
                          {item.original_filename}
                        </td>
                        <td className="px-4 py-3 text-slate-500">{item.owner_email ?? "—"}</td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1 rounded bg-signal/10 px-2 py-0.5 text-xs font-semibold text-signal-dark dark:text-signal">
                            <Shield size={12} />
                            {item.permission.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-500">{formatBytes(item.size_bytes)}</td>
                        <td className="px-4 py-3 text-slate-500">{formatRelativeDate(item.created_at)}</td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => handleDownloadShared(item.file_id, item.original_filename)}
                            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
                          >
                            <Download size={13} />
                            Download
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )
          )}
        </div>
      </main>
    </>
  );
}
