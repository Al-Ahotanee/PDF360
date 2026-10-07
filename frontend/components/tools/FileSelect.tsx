"use client";

import { useFiles } from "@/hooks/useFiles";

export function FileSelect({
  value,
  onChange,
  multiple = false,
  label = "Choose a file",
}: {
  value: string | string[];
  onChange: (value: string | string[]) => void;
  multiple?: boolean;
  label?: string;
}) {
  const { data: files } = useFiles();

  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-ink dark:text-white">{label}</span>
      <select
        multiple={multiple}
        value={value}
        onChange={(e) => {
          if (multiple) {
            onChange(Array.from(e.target.selectedOptions).map((o) => o.value));
          } else {
            onChange(e.target.value);
          }
        }}
        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
        size={multiple ? 5 : undefined}
      >
        {!multiple && <option value="">Select a file…</option>}
        {(files ?? []).map((f) => (
          <option key={f.id} value={f.id}>
            {f.original_filename}
          </option>
        ))}
      </select>
    </label>
  );
}
