"use client";

import { useAuth } from "@/lib/auth/context";
import { LogOut } from "lucide-react";
import { NotificationBell } from "@/components/layout/NotificationBell";

export function Topbar({ title }: { title: string }) {
  const { user, logout } = useAuth();

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6 dark:border-slate-800 dark:bg-surface-dark">
      <h1 className="font-display text-xl font-semibold text-ink dark:text-white">{title}</h1>
      {user && (
        <div className="flex items-center gap-3">
          <NotificationBell />
          <div className="text-right">
            <p className="text-sm font-medium leading-tight">{user.full_name ?? user.email}</p>
            <p className="text-xs capitalize leading-tight text-slate-500">{user.role.replace("_", " ")}</p>
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-ink text-sm font-semibold text-white">
            {(user.full_name ?? user.email)[0]?.toUpperCase()}
          </div>
          <button
            onClick={logout}
            aria-label="Sign out"
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-ink dark:hover:bg-slate-800"
          >
            <LogOut size={18} />
          </button>
        </div>
      )}
    </header>
  );
}
