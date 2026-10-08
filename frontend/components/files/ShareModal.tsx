"use client";

import { useState } from "react";
import {
  X,
  UserPlus,
  Trash2,
  Shield,
  Eye,
  MessageSquare,
  Edit3,
  Link as LinkIcon,
  Copy,
  Check,
  Lock,
  Clock,
  Loader2,
  Globe,
} from "lucide-react";
import { useFileShares, useShareFile, useRevokeShare } from "@/hooks/useSharing";
import { apiClient } from "@/lib/api/client";
import type { PDFFile, SharePermission } from "@/types/api";

interface PublicLinkResponse {
  id: string;
  share_token: string;
  share_url: string;
  expires_at: string | null;
  has_password: boolean;
  allow_download: boolean;
  view_count: number;
}

export function ShareModal({
  file,
  onClose,
}: {
  file: PDFFile;
  onClose: () => void;
}) {
  const [tab, setTab] = useState<"users" | "public">("users");

  // User share state
  const [email, setEmail] = useState("");
  const [permission, setPermission] = useState<SharePermission>("view");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Public link state
  const [expiresInHours, setExpiresInHours] = useState<number | null>(null);
  const [publicPassword, setPublicPassword] = useState("");
  const [allowDownload, setAllowDownload] = useState(true);
  const [creatingPublic, setCreatingPublic] = useState(false);
  const [publicLinkData, setPublicLinkData] = useState<PublicLinkResponse | null>(null);
  const [copied, setCopied] = useState(false);

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

  async function handleCreatePublicLink() {
    setCreatingPublic(true);
    setErrorMsg(null);
    try {
      const res = await apiClient.post<PublicLinkResponse>(`/collaboration/files/${file.id}/public-link`, {
        expires_in_hours: expiresInHours,
        password: publicPassword.trim() || null,
        allow_download: allowDownload,
      });
      setPublicLinkData(res.data);
    } catch (err: any) {
      setErrorMsg(err?.response?.data?.detail ?? "Failed to create public link.");
    } finally {
      setCreatingPublic(false);
    }
  }

  function copyToClipboard(text: string) {
    const fullUrl = `${window.location.origin}${text}`;
    navigator.clipboard.writeText(fullUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-6 shadow-2xl dark:border-slate-800 dark:bg-[#0d1524]">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3 dark:border-white/5">
          <div>
            <h3 className="text-base font-bold text-ink dark:text-white">Share Document</h3>
            <p className="truncate text-xs text-slate-400 max-w-[260px]">{file.original_filename}</p>
          </div>
          <button
            onClick={onClose}
            className="rounded-xl p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-white/5"
          >
            <X size={18} />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="mt-4 flex rounded-xl bg-slate-100 p-1 dark:bg-white/5">
          <button
            type="button"
            onClick={() => setTab("users")}
            className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg py-1.5 text-xs font-semibold transition ${
              tab === "users"
                ? "bg-white text-ink shadow-sm dark:bg-slate-800 dark:text-white"
                : "text-slate-500 hover:text-ink dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            <UserPlus size={14} /> Direct Share
          </button>
          <button
            type="button"
            onClick={() => setTab("public")}
            className={`flex flex-1 items-center justify-center gap-1.5 rounded-lg py-1.5 text-xs font-semibold transition ${
              tab === "public"
                ? "bg-white text-ink shadow-sm dark:bg-slate-800 dark:text-white"
                : "text-slate-500 hover:text-ink dark:text-slate-400 dark:hover:text-white"
            }`}
          >
            <Globe size={14} /> Public Link
          </button>
        </div>

        {errorMsg && (
          <div className="mt-3 rounded-xl border border-red-200 bg-red-50 p-2.5 text-xs text-red-600 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300">
            {errorMsg}
          </div>
        )}

        {/* Tab 1: Direct Internal Share */}
        {tab === "users" && (
          <>
            <form onSubmit={handleShare} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-300">
                  Recipient Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="colleague@example.com"
                  required
                  className="mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-ink outline-none transition focus:border-signal focus:ring-1 focus:ring-signal dark:border-slate-700 dark:bg-white/5 dark:text-white"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-300">
                  Permission Level
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
                            : "border-slate-200 text-slate-600 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-white/5"
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
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-signal px-4 py-2 text-sm font-bold text-ink shadow-sm transition hover:bg-signal-light disabled:opacity-50"
              >
                <UserPlus size={16} />
                {shareFile.isPending ? "Sharing…" : "Grant Access"}
              </button>
            </form>

            <div className="mt-5 border-t border-slate-100 pt-3 dark:border-white/5">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Active Collaborators
              </p>
              <div className="mt-2 max-h-36 space-y-2 overflow-y-auto pr-1">
                {isLoading ? (
                  <p className="text-xs text-slate-400">Loading shares…</p>
                ) : !shares || shares.length === 0 ? (
                  <p className="text-xs text-slate-400">No external users have been granted access yet.</p>
                ) : (
                  shares.map((share) => (
                    <div
                      key={share.id}
                      className="flex items-center justify-between rounded-xl bg-slate-50 p-2.5 text-xs dark:bg-white/5"
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
                        className="rounded-lg p-1 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-white/10"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        )}

        {/* Tab 2: Public Share Link */}
        {tab === "public" && (
          <div className="mt-4 space-y-4">
            {publicLinkData ? (
              <div className="space-y-3 rounded-2xl border border-signal/30 bg-signal/5 p-4">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1 text-xs font-bold text-signal">
                    <Globe size={13} /> Link Ready to Share
                  </span>
                  <span className="rounded bg-signal/10 px-2 py-0.5 text-[10px] font-semibold text-signal-dark dark:text-signal">
                    {publicLinkData.has_password ? "Password Protected" : "Open Access"}
                  </span>
                </div>

                <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white p-2 dark:border-slate-700 dark:bg-black/40">
                  <input
                    type="text"
                    readOnly
                    value={typeof window !== "undefined" ? `${window.location.origin}${publicLinkData.share_url}` : publicLinkData.share_url}
                    className="flex-1 bg-transparent text-xs text-ink outline-none dark:text-white select-all"
                  />
                  <button
                    onClick={() => copyToClipboard(publicLinkData.share_url)}
                    className="flex items-center gap-1 rounded-lg bg-ink px-2.5 py-1 text-xs font-semibold text-white hover:bg-ink-light dark:bg-white dark:text-ink transition"
                  >
                    {copied ? <Check size={12} /> : <Copy size={12} />}
                    {copied ? "Copied" : "Copy"}
                  </button>
                </div>

                <div className="text-[11px] text-slate-400 space-y-0.5">
                  <p>• {publicLinkData.expires_at ? `Expires: ${new Date(publicLinkData.expires_at).toLocaleDateString()}` : "Never expires"}</p>
                  <p>• {publicLinkData.allow_download ? "Download enabled" : "View only (downloads disabled)"}</p>
                </div>

                <button
                  onClick={() => setPublicLinkData(null)}
                  className="w-full text-center text-xs font-semibold text-slate-400 hover:text-white"
                >
                  Create another link
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-slate-600 dark:text-slate-300">
                    Expiration Duration
                  </label>
                  <div className="mt-1 flex items-center gap-2">
                    <Clock size={15} className="text-slate-400 shrink-0" />
                    <select
                      value={expiresInHours === null ? "never" : String(expiresInHours)}
                      onChange={(e) =>
                        setExpiresInHours(e.target.value === "never" ? null : Number(e.target.value))
                      }
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-ink outline-none dark:border-slate-700 dark:bg-white/5 dark:text-white"
                    >
                      <option value="never">Never expires</option>
                      <option value="24">Expires in 24 hours</option>
                      <option value="168">Expires in 7 days</option>
                      <option value="720">Expires in 30 days</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-600 dark:text-slate-300">
                    Access Password (Optional)
                  </label>
                  <div className="mt-1 flex items-center gap-2">
                    <Lock size={15} className="text-slate-400 shrink-0" />
                    <input
                      type="text"
                      value={publicPassword}
                      onChange={(e) => setPublicPassword(e.target.value)}
                      placeholder="Leave blank for public access"
                      className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-ink outline-none dark:border-slate-700 dark:bg-white/5 dark:text-white"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="checkbox"
                    id="allowDownload"
                    checked={allowDownload}
                    onChange={(e) => setAllowDownload(e.target.checked)}
                    className="h-4 w-4 rounded border-slate-300 text-signal cursor-pointer"
                  />
                  <label htmlFor="allowDownload" className="text-xs text-slate-600 dark:text-slate-300 cursor-pointer">
                    Allow recipients to download document
                  </label>
                </div>

                <button
                  type="button"
                  onClick={handleCreatePublicLink}
                  disabled={creatingPublic}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-signal px-4 py-2.5 text-sm font-bold text-ink shadow-sm transition hover:bg-signal-light disabled:opacity-50"
                >
                  {creatingPublic ? <Loader2 size={16} className="animate-spin" /> : <LinkIcon size={16} />}
                  {creatingPublic ? "Creating link…" : "Generate Public Link"}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
