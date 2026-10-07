"use client";

import Link from "next/link";
import { HardDrive, FileText, Activity, Combine, RefreshCw, ShieldCheck, ScanText, Clock } from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { StatCard } from "@/components/ui/StatCard";
import { useDashboardActivity, useDashboardStats, useRecentFiles } from "@/hooks/useDashboard";
import { formatBytes, formatRelativeDate } from "@/lib/format";

const QUICK_TOOLS = [
  { href: "/tools/organize", label: "Merge PDFs", icon: Combine, desc: "Combine multiple files into one" },
  { href: "/tools/convert", label: "Convert", icon: RefreshCw, desc: "PDF to Word, Excel, images & more" },
  { href: "/tools/secure", label: "Protect", icon: ShieldCheck, desc: "Password-protect or watermark" },
  { href: "/tools/ai", label: "OCR a scan", icon: ScanText, desc: "Make a scanned PDF searchable" },
];

export default function DashboardPage() {
  const { data: stats } = useDashboardStats();
  const { data: recentFiles } = useRecentFiles();
  const { data: activity } = useDashboardActivity();

  return (
    <>
      <Topbar title="Dashboard" />
      <main className="flex-1 overflow-y-auto p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard icon={HardDrive} label="Storage used" value={stats ? formatBytes(stats.storage_used_bytes) : "—"} />
          <StatCard icon={FileText} label="Files" value={stats ? String(stats.file_count) : "—"} />
          <StatCard icon={Activity} label="Jobs (30 days)" value={stats ? String(stats.jobs_last_30_days) : "—"} />
        </div>

        <section className="mt-8">
          <h2 className="mb-3 font-display text-base font-semibold text-ink dark:text-white">Quick tools</h2>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {QUICK_TOOLS.map((tool) => {
              const Icon = tool.icon;
              return (
                <Link
                  key={tool.href}
                  href={tool.href}
                  className="group rounded-2xl border border-slate-200 bg-white p-4 transition hover:border-signal hover:shadow-sm dark:border-slate-800 dark:bg-ink/30"
                >
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-signal/15 text-signal-dark group-hover:bg-signal group-hover:text-white">
                    <Icon size={18} />
                  </div>
                  <p className="mt-3 font-medium text-ink dark:text-white">{tool.label}</p>
                  <p className="mt-0.5 text-sm text-slate-500">{tool.desc}</p>
                </Link>
              );
            })}
          </div>
        </section>

        <section className="mt-8">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-display text-base font-semibold text-ink dark:text-white">Recent files</h2>
            <Link href="/files" className="text-sm text-signal-dark hover:underline">
              View all
            </Link>
          </div>
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-ink/30">
            {!recentFiles || recentFiles.length === 0 ? (
              <p className="p-8 text-center text-sm text-slate-500">
                No files yet — upload your first PDF from the Files page to get started.
              </p>
            ) : (
              <table className="w-full text-sm">
                <tbody>
                  {recentFiles.map((file) => (
                    <tr key={file.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                      <td className="px-4 py-3 font-medium text-ink dark:text-white">{file.original_filename}</td>
                      <td className="px-4 py-3 text-slate-500">{formatBytes(file.size_bytes)}</td>
                      <td className="px-4 py-3 text-right text-slate-500">{formatRelativeDate(file.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>

        <section className="mt-8">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-display text-base font-semibold text-ink dark:text-white">Activity Timeline</h2>
          </div>
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-800 dark:bg-ink/30">
            {!activity || activity.length === 0 ? (
              <p className="p-8 text-center text-sm text-slate-500">
                No recent activity recorded yet. Run a tool or job to populate the feed.
              </p>
            ) : (
              <table className="w-full text-sm">
                <thead className="border-b border-slate-100 bg-slate-50 text-left text-xs uppercase tracking-wider text-slate-500 dark:border-slate-800 dark:bg-ink/50">
                  <tr>
                    <th className="px-4 py-2.5">Action</th>
                    <th className="px-4 py-2.5">Type</th>
                    <th className="px-4 py-2.5 text-right">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {activity.map((item) => (
                    <tr key={item.id} className="border-b border-slate-100 last:border-0 dark:border-slate-800">
                      <td className="px-4 py-3 font-medium text-ink dark:text-white">
                        <span className="inline-flex items-center gap-1.5">
                          <Clock size={14} className="text-signal" />
                          {item.action.replace("job.", "Completed ").replace(/_/g, " ")}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-500">
                        {item.resource_type ?? "Operation"}
                      </td>
                      <td className="px-4 py-3 text-right text-slate-500">
                        {formatRelativeDate(item.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>
      </main>
    </>
  );
}
