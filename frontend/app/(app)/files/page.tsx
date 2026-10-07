"use client";

import { Topbar } from "@/components/layout/Topbar";
import { UploadZone } from "@/components/files/UploadZone";
import { FileCard } from "@/components/files/FileCard";
import { useFiles } from "@/hooks/useFiles";

export default function FilesPage() {
  const { data: files, isLoading } = useFiles();

  return (
    <>
      <Topbar title="My Files" />
      <main className="flex-1 overflow-y-auto p-6">
        <UploadZone />

        <div className="mt-8">
          {isLoading ? (
            <p className="text-sm text-slate-500">Loading files…</p>
          ) : !files || files.length === 0 ? (
            <p className="text-sm text-slate-500">No files yet. Upload one above to get started.</p>
          ) : (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
              {files.map((file) => (
                <FileCard key={file.id} file={file} />
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
