"use client";

import { Topbar } from "@/components/layout/Topbar";
import {
  useAdminAnalytics,
  useAdminAuditLogs,
  useAdminSystemHealth,
  useAdminUsers,
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

  return (
    <>
      <Topbar title="Admin" />
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

        {isLoading ? (
          <p className="text-sm text-slate-500">Loading users…</p>
        ) : (
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-ink/30">
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
