"use client";

import { useMemo, useState } from "react";
import {
  Users,
  FileText,
  Download,
  Shield,
  Search,
  LayoutGrid,
  List,
  Star,
  Trash2,
  Share2,
  Eye,
  ArrowUpDown,
  X,
  CheckSquare,
  Square,
  FileDown,
} from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { UploadZone } from "@/components/files/UploadZone";
import { FileCard } from "@/components/files/FileCard";
import { useFiles } from "@/hooks/useFiles";
import { useSharedWithMe } from "@/hooks/useSharing";
import { useTrashFile, useToggleFavorite } from "@/hooks/useOrganization";
import { apiClient } from "@/lib/api/client";
import { formatBytes, formatRelativeDate } from "@/lib/format";
import type { PDFFile } from "@/types/api";

type FilterType = "all" | "pdf" | "favorites" | "large";
type SortOption = "newest" | "oldest" | "name_asc" | "name_desc" | "size_desc";

export default function FilesPage() {
  const [activeTab, setActiveTab] = useState<"my-files" | "shared">("my-files");
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<FilterType>("all");
  const [sortBy, setSortBy] = useState<SortOption>("newest");
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  const { data: files, isLoading } = useFiles();
  const { data: sharedFiles, isLoading: isLoadingShared } = useSharedWithMe();
  const trash = useTrashFile();
  const toggleFavorite = useToggleFavorite();

  // Filter and Sort Logic for "My Files"
  const filteredFiles = useMemo(() => {
    if (!files) return [];
    let list = [...files];

    // Search query filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      list = list.filter((f) => f.original_filename.toLowerCase().includes(q));
    }

    // Category / Facet filter
    if (filterType === "pdf") {
      list = list.filter((f) => f.original_filename.toLowerCase().endsWith(".pdf"));
    } else if (filterType === "favorites") {
      list = list.filter((f) => f.is_favorite);
    } else if (filterType === "large") {
      list = list.filter((f) => f.size_bytes >= 5 * 1024 * 1024);
    }

    // Sort order
    list.sort((a, b) => {
      if (sortBy === "newest") {
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      }
      if (sortBy === "oldest") {
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
      }
      if (sortBy === "name_asc") {
        return a.original_filename.localeCompare(b.original_filename);
      }
      if (sortBy === "name_desc") {
        return b.original_filename.localeCompare(a.original_filename);
      }
      if (sortBy === "size_desc") {
        return b.size_bytes - a.size_bytes;
      }
      return 0;
    });

    return list;
  }, [files, searchQuery, filterType, sortBy]);

  // Batch actions
  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function selectAll() {
    if (selectedIds.size === filteredFiles.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredFiles.map((f) => f.id)));
    }
  }

  async function batchDownload() {
    for (const id of Array.from(selectedIds)) {
      const file = files?.find((f) => f.id === id);
      if (file) {
        const response = await apiClient.get(`/files/${id}/download`, { responseType: "blob" });
        const url = window.URL.createObjectURL(response.data);
        const a = document.createElement("a");
        a.href = url;
        a.download = file.original_filename;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    }
  }

  function batchTrash() {
    if (confirm(`Move ${selectedIds.size} files to trash?`)) {
      selectedIds.forEach((id) => trash.mutate(id));
      setSelectedIds(new Set());
    }
  }

  async function handleDownload(fileId: string, filename: string) {
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
      <main className="flex-1 overflow-y-auto p-6 space-y-6">
        <UploadZone />

        <div>
          {/* Main Workspace Tabs */}
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 pb-3 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setActiveTab("my-files");
                  setSelectedIds(new Set());
                }}
                className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition ${
                  activeTab === "my-files"
                    ? "bg-ink text-white dark:bg-white dark:text-ink shadow-sm"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                }`}
              >
                <FileText size={16} />
                My Files ({files?.length ?? 0})
              </button>
              <button
                onClick={() => {
                  setActiveTab("shared");
                  setSelectedIds(new Set());
                }}
                className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition ${
                  activeTab === "shared"
                    ? "bg-ink text-white dark:bg-white dark:text-ink shadow-sm"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
                }`}
              >
                <Users size={16} />
                Shared with me ({sharedFiles?.length ?? 0})
              </button>
            </div>

            {/* View Switcher (Grid vs Table) */}
            {activeTab === "my-files" && (
              <div className="flex items-center gap-1 rounded-xl border border-slate-200 bg-slate-50 p-1 dark:border-slate-800 dark:bg-ink">
                <button
                  onClick={() => setViewMode("grid")}
                  title="Grid View"
                  className={`rounded-lg p-1.5 transition ${
                    viewMode === "grid"
                      ? "bg-white text-ink shadow-sm dark:bg-white/10 dark:text-white"
                      : "text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  }`}
                >
                  <LayoutGrid size={16} />
                </button>
                <button
                  onClick={() => setViewMode("table")}
                  title="Table View"
                  className={`rounded-lg p-1.5 transition ${
                    viewMode === "table"
                      ? "bg-white text-ink shadow-sm dark:bg-white/10 dark:text-white"
                      : "text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                  }`}
                >
                  <List size={16} />
                </button>
              </div>
            )}
          </div>

          {activeTab === "my-files" && (
            <div className="mt-4 space-y-4">
              {/* Search, Filter Pills & Sort Bar */}
              <div className="flex flex-wrap items-center justify-between gap-3">
                {/* Search input */}
                <div className="relative min-w-[240px] flex-1 max-w-md">
                  <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search documents by name…"
                    className="w-full rounded-xl border border-slate-200 bg-white py-2 pl-10 pr-9 text-sm text-ink placeholder:text-slate-400 focus:border-signal focus:outline-none dark:border-slate-800 dark:bg-ink/50 dark:text-white"
                  />
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery("")}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    >
                      <X size={14} />
                    </button>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {/* Filter Pills */}
                  <div className="flex items-center gap-1 rounded-xl border border-slate-200 bg-slate-50 p-1 dark:border-slate-800 dark:bg-ink">
                    <button
                      onClick={() => setFilterType("all")}
                      className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                        filterType === "all"
                          ? "bg-white text-ink shadow-sm dark:bg-white/10 dark:text-white"
                          : "text-slate-500 hover:text-ink dark:hover:text-white"
                      }`}
                    >
                      All
                    </button>
                    <button
                      onClick={() => setFilterType("pdf")}
                      className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                        filterType === "pdf"
                          ? "bg-white text-ink shadow-sm dark:bg-white/10 dark:text-white"
                          : "text-slate-500 hover:text-ink dark:hover:text-white"
                      }`}
                    >
                      PDFs
                    </button>
                    <button
                      onClick={() => setFilterType("favorites")}
                      className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                        filterType === "favorites"
                          ? "bg-white text-ink shadow-sm dark:bg-white/10 dark:text-white"
                          : "text-slate-500 hover:text-ink dark:hover:text-white"
                      }`}
                    >
                      Starred
                    </button>
                    <button
                      onClick={() => setFilterType("large")}
                      className={`rounded-lg px-2.5 py-1 text-xs font-medium transition ${
                        filterType === "large"
                          ? "bg-white text-ink shadow-sm dark:bg-white/10 dark:text-white"
                          : "text-slate-500 hover:text-ink dark:hover:text-white"
                      }`}
                    >
                      &gt; 5MB
                    </button>
                  </div>

                  {/* Sort Dropdown */}
                  <div className="flex items-center gap-1.5 rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 dark:border-slate-800 dark:bg-ink dark:text-slate-300">
                    <ArrowUpDown size={13} className="text-slate-400" />
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value as SortOption)}
                      className="bg-transparent focus:outline-none cursor-pointer"
                    >
                      <option value="newest">Newest first</option>
                      <option value="oldest">Oldest first</option>
                      <option value="name_asc">Name (A–Z)</option>
                      <option value="name_desc">Name (Z–A)</option>
                      <option value="size_desc">Size (Largest)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Multi-Select Batch Action Bar */}
              {selectedIds.size > 0 && (
                <div className="flex items-center justify-between rounded-xl bg-ink p-3 text-white shadow-lg dark:bg-slate-800 animate-in fade-in duration-150">
                  <div className="flex items-center gap-3">
                    <button onClick={selectAll} className="flex items-center gap-1.5 text-xs font-medium text-slate-300 hover:text-white">
                      <CheckSquare size={16} />
                      {selectedIds.size === filteredFiles.length ? "Deselect All" : "Select All"}
                    </button>
                    <span className="text-xs font-semibold text-signal">
                      {selectedIds.size} {selectedIds.size === 1 ? "document" : "documents"} selected
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={batchDownload}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-white/10 px-3 py-1.5 text-xs font-medium hover:bg-white/20 transition"
                    >
                      <Download size={13} />
                      Download
                    </button>
                    <button
                      onClick={batchTrash}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-red-600/80 px-3 py-1.5 text-xs font-medium hover:bg-red-600 transition"
                    >
                      <Trash2 size={13} />
                      Move to Trash
                    </button>
                    <button
                      onClick={() => setSelectedIds(new Set())}
                      className="rounded-lg p-1.5 text-slate-400 hover:text-white"
                    >
                      <X size={14} />
                    </button>
                  </div>
                </div>
              )}

              {/* Documents View (Grid vs Table) */}
              {isLoading ? (
                <p className="text-sm text-slate-500">Loading files…</p>
              ) : filteredFiles.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-200 p-12 text-center text-slate-500 dark:border-slate-800">
                  <p className="text-sm">No documents found matching your search or filters.</p>
                </div>
              ) : viewMode === "grid" ? (
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
                  {filteredFiles.map((file) => (
                    <div key={file.id} className="relative group">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(file.id)}
                        onChange={() => toggleSelect(file.id)}
                        className="absolute left-3 top-3 z-10 h-4 w-4 rounded border-slate-300 text-signal opacity-0 group-hover:opacity-100 transition-opacity checked:opacity-100 cursor-pointer"
                      />
                      <FileCard file={file} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-ink/30">
                  <table className="w-full text-sm">
                    <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wider text-slate-500 dark:border-slate-800 dark:bg-ink/50">
                      <tr>
                        <th className="w-10 px-4 py-3">
                          <input
                            type="checkbox"
                            checked={selectedIds.size > 0 && selectedIds.size === filteredFiles.length}
                            onChange={selectAll}
                            className="h-4 w-4 rounded border-slate-300 cursor-pointer"
                          />
                        </th>
                        <th className="px-4 py-3">Document Name</th>
                        <th className="px-4 py-3">Size</th>
                        <th className="px-4 py-3">Created</th>
                        <th className="px-4 py-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredFiles.map((file) => (
                        <tr
                          key={file.id}
                          className="border-b border-slate-100 last:border-0 hover:bg-slate-50/50 dark:border-slate-800 dark:hover:bg-white/[0.02]"
                        >
                          <td className="px-4 py-3">
                            <input
                              type="checkbox"
                              checked={selectedIds.has(file.id)}
                              onChange={() => toggleSelect(file.id)}
                              className="h-4 w-4 rounded border-slate-300 cursor-pointer"
                            />
                          </td>
                          <td className="px-4 py-3 font-medium text-ink dark:text-white flex items-center gap-2.5">
                            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-red-500/10 text-[10px] font-bold text-red-500 shrink-0">
                              PDF
                            </span>
                            <span className="truncate max-w-sm sm:max-w-md">{file.original_filename}</span>
                          </td>
                          <td className="px-4 py-3 text-slate-500">{formatBytes(file.size_bytes)}</td>
                          <td className="px-4 py-3 text-slate-500">{formatRelativeDate(file.created_at)}</td>
                          <td className="px-4 py-3 text-right">
                            <div className="flex items-center justify-end gap-1">
                              <button
                                onClick={() =>
                                  toggleFavorite.mutate({ fileId: file.id, isFavorite: !file.is_favorite })
                                }
                                title="Favorite"
                                className="rounded-lg p-1.5 text-slate-400 hover:text-signal"
                              >
                                <Star
                                  size={15}
                                  fill={file.is_favorite ? "currentColor" : "none"}
                                  className={file.is_favorite ? "text-signal" : ""}
                                />
                              </button>
                              <button
                                onClick={() => handleDownload(file.id, file.original_filename)}
                                title="Download"
                                className="rounded-lg p-1.5 text-slate-400 hover:text-ink dark:hover:text-white"
                              >
                                <Download size={15} />
                              </button>
                              <button
                                onClick={() => trash.mutate(file.id)}
                                title="Trash"
                                className="rounded-lg p-1.5 text-slate-400 hover:text-red-500"
                              >
                                <Trash2 size={15} />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Shared With Me Tab */}
          {activeTab === "shared" && (
            <div className="mt-4">
              {isLoadingShared ? (
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
                              onClick={() => handleDownload(item.file_id, item.original_filename)}
                              className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
                            >
                              <Download size={13} /> Download
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
