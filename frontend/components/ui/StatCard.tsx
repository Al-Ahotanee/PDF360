import { LucideIcon } from "lucide-react";

export function StatCard({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-800 dark:bg-ink/30">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon size={16} />
        <p className="text-sm">{label}</p>
      </div>
      <p className="mt-2 font-display text-2xl font-semibold text-ink dark:text-white">{value}</p>
    </div>
  );
}
