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
    <div className="flex items-center gap-2 px-2">
      {/* Signature mark: three stacked, slightly fanned "pages" */}
      <div className="relative h-8 w-8 shrink-0">
        <div className="absolute inset-0 translate-x-1 translate-y-1 rotate-6 rounded-sm bg-signal/40" />
        <div className="absolute inset-0 translate-x-0.5 translate-y-0.5 rotate-3 rounded-sm bg-signal/70" />
        <div className="absolute inset-0 rounded-sm bg-signal" />
      </div>
      <span className="font-display text-lg font-semibold tracking-tight text-white">
        PDF360
      </span>
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
                    className={`flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors ${
                      active
                        ? "bg-ink-light text-white"
                        : "text-slate-300 hover:bg-ink-light/60 hover:text-white"
                    }`}
                  >
                    <Icon size={17} strokeWidth={active ? 2.25 : 1.75} />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>
      <Link
        href="/settings"
        className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-slate-400 hover:bg-ink-light/60 hover:text-white"
      >
        <Settings size={17} strokeWidth={1.75} />
        Settings
      </Link>
    </aside>
  );
}
