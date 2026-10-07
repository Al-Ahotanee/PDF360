"use client";

import { useState } from "react";
import { Plus, Trash2, Sliders, ToggleLeft, ToggleRight } from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import {
  useAdminAnalytics,
  useAdminAuditLogs,
  useAdminFeatureFlags,
  useAdminSystemHealth,
  useAdminUsers,
  useDeleteFeatureFlag,
  useSetFeatureFlag,
  useSetUserActive,
  useSetUserRole,
} from "@/hooks/useAdmin";

const ROLES = ["guest", "registered_user", "premium_user", "admin", "super_admin"];

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-ink/30">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 font-display text-2xl font-semibold text-ink dark:text-white">{value}</p>
    </div>
  );
}

export default function AdminPage() {
  const { data: users, isLoading, error } = useAdminUsers();
  const setRole = useSetUserRole();
  const setActive = useSetUserActive();
  const { data: analytics } = useAdminAnalytics();
  const { data: health } = useAdminSystemHealth();
  const { data: auditLogs } = useAdminAuditLogs();
  const { data: featureFlags } = useAdminFeatureFlags();
  const setFlag = useSetFeatureFlag();
  const deleteFlag = useDeleteFeatureFlag();

  const [newKey, setNewKey] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newValEnabled, setNewValEnabled] = useState(true);

  async function handleAddFlag(e: React.FormEvent) {
    e.preventDefault();
    if (!newKey.trim()) return;
    await setFlag.mutateAsync({
      key: newKey.trim(),
      value: { enabled: newValEnabled },
      description: newDesc.trim() || null,
    });
    setNewKey("");
    setNewDesc("");
  }

  return (
    <>
      <Topbar title="Admin Management" />
      <main className="flex-1 space-y-6 overflow-y-auto p-6">
        {error && (
          <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-300">
            You need admin permissions to view this page.
          </p>
        )}

        {analytics && (
          <div className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
            <StatCard label="Total users" value={analytics.total_users} />
            <StatCard label="Active users" value={analytics.active_users} />
            <StatCard label="Total files" value={analytics.total_files} />
            <StatCard label="Total jobs" value={analytics.total_jobs} />
            <StatCard label="Premium subs" value={analytics.premium_subscribers} />
            <StatCard label="Revenue" value={`$${analytics.total_revenue.toFixed(2)}`} />
          </div>
        )}

        {health && (
          <div className="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-ink/30">
            <p className="text-sm font-medium text-ink dark:text-white">System health</p>
            <div className="mt-2 flex flex-wrap gap-4 text-sm text-slate-500">
              <span>Status: <span className="text-ink dark:text-white">{health.status}</span></span>
              <span>Queued jobs: {health.queued_jobs}</span>
              <span>Processing jobs: {health.processing_jobs}</span>
              <span>Failed (last 100): {health.failed_jobs_last_100}</span>
            </div>
          </div>
        )}

        {/* Feature Flags Section */}
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-ink/30">
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <Sliders size={16} className="text-signal" />
              <p className="text-sm font-medium text-ink dark:text-white">System Feature Flags</p>
            </div>
          </div>

          <form onSubmit={handleAddFlag} className="flex flex-wrap items-center gap-3 border-b border-slate-100 bg-slate-50/50 p-3 dark:border-slate-800 dark:bg-ink/20">
            <input
              type="text"
              placeholder="flag_key (e.g. enable_beta_ocr)"
              value={newKey}
              onChange={(e) => setNewKey(e.target.value)}
              required
              className="rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs text-ink outline-none focus:border-signal dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              className="flex-1 rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-xs text-ink outline-none focus:border-signal dark:border-slate-700 dark:bg-slate-800 dark:text-white"
            />
            <label className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-300">
              <input
                type="checkbox"
                checked={newValEnabled}
                onChange={(e) => setNewValEnabled(e.target.checked)}
                className="rounded text-signal focus:ring-signal"
              />
              Enabled
            </label>
            <button
              type="submit"
              disabled={setFlag.isPending}
              className="inline-flex items-center gap-1 rounded-lg bg-signal px-3 py-1 text-xs font-semibold text-white shadow-sm hover:bg-signal-dark disabled:opacity-50"
            >
              <Plus size={14} />
              Set Flag
            </button>
          </form>

          <table className="w-full text-sm">
            <thead className="border-b border-slate-100 bg-slate-50 text-left text-xs uppercase tracking-wider text-slate-500 dark:border-slate-800 dark:bg-ink/50">
              <tr>
                <th className="px-4 py-2.5">Key</th>
                <th className="px-4 py-2.5">Description</th>
                <th className="px-4 py-2.5">State</th>
                <th className="px-4 py-2.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {!featureFlags || featureFlags.length === 0 ? (
                <tr>
                  <td colSpan={4} className="p-4 text-center text-xs text-slate-400">
                    No custom feature flags configured.
                  </td>
                </tr>
              ) : (
                featureFlags.map((flag) => {
                  const isEnabled = Boolean(flag.value?.enabled ?? true);
                  return (
                    <tr key={flag.key} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                      <td className="px-4 py-2.5 font-mono text-xs font-semibold text-ink dark:text-white">
                        {flag.key}
                      </td>
                      <td className="px-4 py-2.5 text-xs text-slate-500">{flag.description ?? "—"}</td>
                      <td className="px-4 py-2.5">
                        <button
                          onClick={() =>
                            setFlag.mutate({
                              key: flag.key,
                              value: { ...flag.value, enabled: !isEnabled },
                              description: flag.description,
                            })
                          }
                          className="inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium"
                        >
                          {isEnabled ? (
                            <span className="flex items-center gap-1 text-green-600 dark:text-green-400">
                              <ToggleRight size={18} /> Active
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-slate-400">
                              <ToggleLeft size={18} /> Disabled
                            </span>
                          )}
                        </button>
                      </td>
                      <td className="px-4 py-2.5 text-right">
                        <button
                          onClick={() => deleteFlag.mutate(flag.key)}
                          className="rounded-lg p-1 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-slate-800"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* User Management Section */}
        {isLoading ? (
          <p className="text-sm text-slate-500">Loading users…</p>
        ) : (
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-ink/30">
            <div className="border-b border-slate-200 px-4 py-3 dark:border-slate-800">
              <p className="text-sm font-medium text-ink dark:text-white">Users & Roles</p>
            </div>
            <table className="w-full text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wider text-slate-500 dark:border-slate-800 dark:bg-ink/50">
                <tr>
                  <th className="px-4 py-3">Name</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {users?.map((u) => (
                  <tr key={u.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                    <td className="px-4 py-3 text-ink dark:text-white">{u.full_name ?? "—"}</td>
                    <td className="px-4 py-3 text-slate-500">{u.email}</td>
                    <td className="px-4 py-3">
                      <select
                        value={u.role}
                        onChange={(e) => setRole.mutate({ userId: u.id, roleName: e.target.value })}
                        className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-sm dark:border-slate-700 dark:bg-ink"
                      >
                        {ROLES.map((r) => (
                          <option key={r} value={r}>
                            {r.replace("_", " ")}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => setActive.mutate({ userId: u.id, isActive: !u.is_active })}
                        className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                          u.is_active
                            ? "bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-300"
                            : "bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-300"
                        }`}
                      >
                        {u.is_active ? "Active" : "Deactivated"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Audit Log Section */}
        {auditLogs && auditLogs.length > 0 && (
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-ink/30">
            <div className="border-b border-slate-200 px-4 py-3 dark:border-slate-800">
              <p className="text-sm font-medium text-ink dark:text-white">Audit log</p>
            </div>
            <table className="w-full text-sm">
              <thead className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wider text-slate-500 dark:border-slate-800 dark:bg-ink/50">
                <tr>
                  <th className="px-4 py-3">Action</th>
                  <th className="px-4 py-3">Target</th>
                  <th className="px-4 py-3">Details</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                    <td className="px-4 py-3 text-ink dark:text-white">{log.action}</td>
                    <td className="px-4 py-3 text-slate-500">{log.target_type ?? "—"}</td>
                    <td className="px-4 py-3 text-slate-500">{JSON.stringify(log.metadata_json)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </>
  );
}
