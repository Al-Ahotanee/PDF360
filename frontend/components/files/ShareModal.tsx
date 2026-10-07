"use client";

import { useState } from "react";
import { X, UserPlus, Trash2, Shield, Eye, MessageSquare, Edit3 } from "lucide-react";
import { useFileShares, useShareFile, useRevokeShare } from "@/hooks/useSharing";
import type { PDFFile, SharePermission } from "@/types/api";

export function ShareModal({
  file,
  onClose,
}: {
  file: PDFFile;
  onClose: () => void;
}) {
  const [email, setEmail] = useState("");
  const [permission, setPermission] = useState<SharePermission>("view");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const { data: shares, isLoading } = useFileShares(file.id);
  const shareFile = useShareFile();
  const revokeShare = useRevokeShare();

  async function handleShare(e: React.FormEvent) {
    e.preventDefault();
    setErrorMsg(null);
    if (!email.trim()) return;

    try {
      await shareFile.mutateAsync({
        fileId: file.id,
        email: email.trim(),
        permission,
      });
      setEmail("");
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setErrorMsg(error?.response?.data?.detail ?? "Failed to share document.");
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-xl dark:border-slate-800 dark:bg-slate-900">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-slate-800">
          <div>
            <h3 className="font-display text-base font-semibold text-ink dark:text-white">
              Share Document
            </h3>
            <p className="truncate text-xs text-slate-500 max-w-[260px]">{file.original_filename}</p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-800"
          >
            <X size={18} />
          </button>
        </div>

        {errorMsg && (
          <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-2.5 text-xs text-red-600 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleShare} className="mt-4 space-y-3">
          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-300">
              Recipient email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="colleague@example.com"
              required
              className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-signal focus:ring-1 focus:ring-signal dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-600 dark:text-slate-300">
              Permission
            </label>
            <div className="mt-1.5 grid grid-cols-3 gap-2">
              {(
                [
                  { id: "view", label: "View", icon: Eye },
                  { id: "comment", label: "Comment", icon: MessageSquare },
                  { id: "edit", label: "Edit", icon: Edit3 },
                ] as const
              ).map((p) => {
                const Icon = p.icon;
                const active = permission === p.id;
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setPermission(p.id)}
                    className={`flex items-center justify-center gap-1.5 rounded-xl border py-2 text-xs font-medium transition ${
                      active
                        ? "border-signal bg-signal/10 text-signal-dark font-semibold dark:border-signal dark:text-signal"
                        : "border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
                    }`}
                  >
                    <Icon size={14} />
                    {p.label}
                  </button>
                );
              })}
            </div>
          </div>

          <button
            type="submit"
            disabled={shareFile.isPending}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-signal px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-signal-dark disabled:opacity-50"
          >
            <UserPlus size={16} />
            {shareFile.isPending ? "Sharing…" : "Grant Access"}
          </button>
        </form>

        <div className="mt-6 border-t border-slate-100 pt-4 dark:border-slate-800">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            People with access
          </p>
          <div className="mt-2 max-h-40 space-y-2 overflow-y-auto pr-1">
            {isLoading ? (
              <p className="text-xs text-slate-400">Loading shares…</p>
            ) : !shares || shares.length === 0 ? (
              <p className="text-xs text-slate-400">No one has been granted access yet.</p>
            ) : (
              shares.map((share) => (
                <div
                  key={share.id}
                  className="flex items-center justify-between rounded-xl bg-slate-50 p-2.5 text-xs dark:bg-slate-800/50"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium text-ink dark:text-white">
                      {share.shared_with_email ?? "User"}
                    </p>
                    <span className="inline-flex items-center gap-1 rounded bg-slate-200/70 px-1.5 py-0.5 text-[10px] font-medium text-slate-700 dark:bg-slate-700 dark:text-slate-300">
                      <Shield size={10} />
                      {share.permission.toUpperCase()}
                    </span>
                  </div>
                  <button
                    onClick={() => revokeShare.mutate({ shareId: share.id, fileId: file.id })}
                    aria-label="Revoke share"
                    className="rounded-lg p-1 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-slate-700"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
