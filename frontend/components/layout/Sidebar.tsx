"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderOpen,
  Combine,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Layers,
  Settings,
  Users,
  PenTool,
  FileSignature,
  FilePlus2,
} from "lucide-react";
import { useAuth } from "@/lib/auth/context";

const NAV_SECTIONS = [
  {
    label: "Workspace",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { href: "/files", label: "My Files", icon: FolderOpen },
      { href: "/editor", label: "Editor", icon: PenTool },
    ],
  },
  {
    label: "Tools",
    items: [
      { href: "/tools/create", label: "Create", icon: FilePlus2 },
      { href: "/tools/organize", label: "Organize", icon: Combine },
      { href: "/tools/convert", label: "Convert", icon: RefreshCw },
      { href: "/tools/secure", label: "Secure", icon: ShieldCheck },
      { href: "/tools/forms", label: "Forms", icon: FileSignature },
      { href: "/tools/ai", label: "AI Tools", icon: Sparkles },
      { href: "/tools/batch", label: "Batch", icon: Layers },
    ],
  },
];

function Logo() {
  return (
    <div className="flex items-center gap-3 px-2 py-1">
      {/* Signature mark: layered glowing isometric pages */}
      <div className="relative h-9 w-9 shrink-0">
        <div className="absolute inset-0 translate-x-1.5 translate-y-1.5 rotate-6 rounded-lg bg-signal/30" />
        <div className="absolute inset-0 translate-x-0.5 translate-y-0.5 rotate-3 rounded-lg bg-signal/60" />
        <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-gradient-to-tr from-signal-dark via-signal to-signal-light shadow-md shadow-signal/20">
          <span className="font-display text-sm font-black text-ink">360</span>
        </div>
      </div>
      <div>
        <span className="font-display text-lg font-bold tracking-tight text-white flex items-center gap-0.5">
          PDF<span className="text-signal">360</span>
        </span>
        <p className="text-[10px] font-medium text-slate-400 tracking-wide uppercase">Workspace Pro</p>
      </div>
    </div>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const isAdmin = user?.role === "admin" || user?.role === "super_admin";

  const sections = isAdmin
    ? [...NAV_SECTIONS, { label: "Manage", items: [{ href: "/admin", label: "Admin", icon: Users }] }]
    : NAV_SECTIONS;

  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col bg-ink px-3 py-5 text-slate-300">
      <Logo />
      <nav className="mt-8 flex-1 space-y-6">
        {sections.map((section) => (
          <div key={section.label}>
            <p className="px-2 text-xs font-medium uppercase tracking-wider text-slate-500">
              {section.label}
            </p>
            <div className="mt-2 space-y-0.5">
              {section.items.map((item) => {
                const active = pathname === item.href || pathname.startsWith(item.href + "/");
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`group flex items-center justify-between rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                      active
                        ? "bg-signal/15 text-signal font-semibold shadow-sm shadow-signal/10 border-l-2 border-signal"
                        : "text-slate-400 hover:bg-white/[0.05] hover:text-white"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <Icon size={18} strokeWidth={active ? 2.25 : 1.75} className={active ? "text-signal" : "text-slate-400 group-hover:text-white"} />
                      <span>{item.label}</span>
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
      <div className="pt-4 border-t border-white/5 space-y-1">
        <Link
          href="/settings"
          className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-400 hover:bg-white/[0.05] hover:text-white transition"
        >
          <Settings size={18} strokeWidth={1.75} />
          Settings & Preferences
        </Link>
      </div>
    </aside>
  );
}
