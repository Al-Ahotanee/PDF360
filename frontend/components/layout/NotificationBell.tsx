"use client";

import { useState } from "react";
import { Bell } from "lucide-react";
import { useMarkNotificationRead, useNotifications } from "@/hooks/useNotifications";
import { formatRelativeDate } from "@/lib/format";

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const { data: notifications } = useNotifications();
  const markRead = useMarkNotificationRead();

  const unreadCount = notifications?.filter((n) => !n.is_read).length ?? 0;

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        aria-label="Notifications"
        className="relative rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-ink dark:hover:bg-slate-800"
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span className="absolute right-1 top-1 flex h-2 w-2 rounded-full bg-signal" />
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full z-10 mt-2 w-80 rounded-xl border border-slate-200 bg-white shadow-lg dark:border-slate-800 dark:bg-ink">
          <div className="border-b border-slate-100 px-4 py-2.5 text-sm font-medium text-ink dark:border-slate-800 dark:text-white">
            Notifications
          </div>
          <div className="max-h-96 overflow-y-auto">
            {!notifications || notifications.length === 0 ? (
              <p className="p-6 text-center text-sm text-slate-500">No notifications yet.</p>
            ) : (
              notifications.map((n) => (
                <button
                  key={n.id}
                  onClick={() => !n.is_read && markRead.mutate(n.id)}
                  className={`block w-full border-b border-slate-100 px-4 py-3 text-left text-sm last:border-0 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-800/50 ${
                    !n.is_read ? "bg-signal/5" : ""
                  }`}
                >
                  <p className="font-medium text-ink dark:text-white">{n.title}</p>
                  {n.body && <p className="mt-0.5 text-slate-500">{n.body}</p>}
                  <p className="mt-1 text-xs text-slate-400">{formatRelativeDate(n.created_at)}</p>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
