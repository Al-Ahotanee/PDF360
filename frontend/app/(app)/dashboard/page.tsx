"use client";

import Link from "next/link";
import {
  HardDrive,
  FileText,
  Activity,
  Combine,
  RefreshCw,
  ShieldCheck,
  ScanText,
  Clock,
  ArrowUpRight,
  Sparkles,
  Layers,
  FilePlus2,
  FileSignature,
  Download,
} from "lucide-react";
import { Topbar } from "@/components/layout/Topbar";
import { StatCard } from "@/components/ui/StatCard";
import { useDashboardActivity, useDashboardStats, useRecentFiles } from "@/hooks/useDashboard";
import { formatBytes, formatRelativeDate } from "@/lib/format";

const QUICK_TOOLS = [
  { href: "/tools/organize", label: "Merge & Split", icon: Combine, desc: "Combine or slice documents", tag: "Popular", color: "text-amber-500 bg-amber-500/10" },
  { href: "/tools/convert", label: "Convert File", icon: RefreshCw, desc: "To Word, Excel, images", tag: "Fast", color: "text-blue-500 bg-blue-500/10" },
  { href: "/tools/secure", label: "Protect & Sign", icon: ShieldCheck, desc: "Password, watermark & AES", tag: "Secure", color: "text-emerald-500 bg-emerald-500/10" },
  { href: "/tools/ai", label: "OCR & AI Extract", icon: ScanText, desc: "Scan to text & smart insights", tag: "AI", color: "text-purple-400 bg-purple-500/10" },
  { href: "/tools/forms", label: "Interactive Forms", icon: FileSignature, desc: "Fill & flatten AcroForms", tag: "Forms", color: "text-rose-400 bg-rose-500/10" },
  { href: "/tools/batch", label: "Batch Pipelines", icon: Layers, desc: "Async high-volume workflows", tag: "Celery", color: "text-sky-400 bg-sky-500/10" },
];

export default function DashboardPage() {
  const { data: stats } = useDashboardStats();
  const { data: recentFiles } = useRecentFiles();
  const { data: activity } = useDashboardActivity();

  return (
    <>
      <Topbar title="Workspace Dashboard" />
      <main className="flex-1 overflow-y-auto p-6 md:p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* Metric Overview */}
        <section>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
            <StatCard
              icon={HardDrive}
              label="Cloud Storage Used"
              value={stats ? formatBytes(stats.storage_used_bytes) : "—"}
            />
            <StatCard
              icon={FileText}
              label="Indexed Documents"
              value={stats ? String(stats.file_count) : "—"}
            />
            <StatCard
              icon={Activity}
              label="Processed Jobs (30d)"
              value={stats ? String(stats.jobs_last_30_days) : "—"}
            />
          </div>
        </section>

        {/* Quick Tools Grid */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-display text-lg font-bold text-ink dark:text-white">Quick Actions</h2>
              <p className="text-xs text-slate-500">Launch any core PDF processing tool in one click</p>
            </div>
            <Link href="/files" className="text-xs font-semibold text-signal-dark dark:text-signal hover:underline flex items-center gap-1">
              Browse workspace files <ArrowUpRight size={14} />
            </Link>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {QUICK_TOOLS.map((tool) => {
              const Icon = tool.icon;
              return (
                <Link
                  key={tool.href}
                  href={tool.href}
                  className="group relative flex items-start gap-4 rounded-2xl border border-slate-200/80 bg-white p-5 transition-all hover:border-signal/50 hover:shadow-md hover:-translate-y-0.5 dark:border-slate-800 dark:bg-[#0d1524]"
                >
                  <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${tool.color} transition group-hover:scale-105`}>
                    <Icon size={20} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <p className="font-display font-semibold text-sm text-ink group-hover:text-signal transition-colors dark:text-white truncate">
                        {tool.label}
                      </p>
                      <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600 dark:bg-white/5 dark:text-slate-400">
                        {tool.tag}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 line-clamp-1">{tool.desc}</p>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* Recent Files & Activity Timeline Split */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Files */}
          <section className="flex flex-col">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="font-display text-lg font-bold text-ink dark:text-white">Recent Documents</h2>
                <p className="text-xs text-slate-500">Your latest uploaded or modified files</p>
              </div>
              <Link href="/files" className="text-xs font-semibold text-signal-dark dark:text-signal hover:underline">
                View all
              </Link>
            </div>

            <div className="flex-1 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-[#0d1524]">
              {!recentFiles || recentFiles.length === 0 ? (
                <div className="p-12 text-center">
                  <FileText className="mx-auto h-8 w-8 text-slate-400 opacity-60 mb-2" />
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">No documents yet</p>
                  <p className="text-xs text-slate-400 mt-1">Upload a PDF to get started with analysis and conversions.</p>
                  <Link
                    href="/files"
                    className="mt-4 inline-flex items-center gap-1.5 rounded-xl bg-signal px-3.5 py-2 text-xs font-semibold text-ink hover:bg-signal-light transition"
                  >
                    Upload Document
                  </Link>
                </div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {recentFiles.slice(0, 5).map((file) => (
                    <div key={file.id} className="flex items-center justify-between p-4 hover:bg-slate-50 dark:hover:bg-white/[0.02] transition">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-500/10 text-red-500 font-bold text-xs">
                          PDF
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-sm text-ink dark:text-white truncate max-w-[200px] sm:max-w-xs">
                            {file.original_filename}
                          </p>
                          <p className="text-xs text-slate-400">{formatBytes(file.size_bytes)}</p>
                        </div>
                      </div>
                      <span className="text-xs text-slate-400 shrink-0">{formatRelativeDate(file.created_at)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>

          {/* Activity Timeline */}
          <section className="flex flex-col">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="font-display text-lg font-bold text-ink dark:text-white">Activity Feed</h2>
                <p className="text-xs text-slate-500">Live log of workspace operations</p>
              </div>
            </div>

            <div className="flex-1 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-[#0d1524]">
              {!activity || activity.length === 0 ? (
                <div className="p-12 text-center">
                  <Activity className="mx-auto h-8 w-8 text-slate-400 opacity-60 mb-2" />
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-400">No activity logged</p>
                  <p className="text-xs text-slate-400 mt-1">Actions performed on files will appear here in real time.</p>
                </div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800/60">
                  {activity.slice(0, 5).map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 hover:bg-slate-50 dark:hover:bg-white/[0.02] transition">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-signal/15 text-signal-dark dark:text-signal">
                          <Clock size={16} />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-ink dark:text-white">
                            {item.action.replace("job.", "Completed ").replace(/_/g, " ")}
                          </p>
                          <p className="text-xs text-slate-400">{item.resource_type ?? "System"}</p>
                        </div>
                      </div>
                      <span className="text-xs text-slate-400 shrink-0">{formatRelativeDate(item.created_at)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
    </>
  );
}
