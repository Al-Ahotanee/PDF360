"use client";

import { useRef, useState } from "react";
import { Highlighter, Pencil, Type, StickyNote as StickyNoteIcon, Loader2, Underline, Strikethrough, Eraser } from "lucide-react";
import { apiClient } from "@/lib/api/client";
import { useAddHighlight, useAddTextBox, useAddStickyNote, useAddFreehand, useAddUnderline, useAddStrikethrough, useAddWhiteout } from "@/hooks/useEditor";

type Tool = "highlight" | "draw" | "text" | "note" | "underline" | "strikethrough" | "whiteout";

const PREVIEW_DPI = 100;
const PDF_POINTS_PER_INCH = 72;

function toPdfPoints(px: number) {
  return (px / PREVIEW_DPI) * PDF_POINTS_PER_INCH;
}

const TOOLS: { id: Tool; label: string; icon: typeof Highlighter }[] = [
  { id: "highlight", label: "Highlight", icon: Highlighter },
  { id: "underline", label: "Underline", icon: Underline },
  { id: "strikethrough", label: "Strikethrough", icon: Strikethrough },
  { id: "whiteout", label: "Whiteout", icon: Eraser },
  { id: "draw", label: "Draw", icon: Pencil },
  { id: "text", label: "Text", icon: Type },
  { id: "note", label: "Sticky note", icon: StickyNoteIcon },
];

export function PageEditor({ initialFileId, page = 1 }: { initialFileId: string; page?: number }) {
  const [fileId, setFileId] = useState(initialFileId);
  const [tool, setTool] = useState<Tool>("highlight");
  const [color, setColor] = useState("#F5A623");
  const imgRef = useRef<HTMLImageElement>(null);

  // Drag state for highlight boxes
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
  const [dragBox, setDragBox] = useState<{ x: number; y: number; w: number; h: number } | null>(null);

  // Freehand stroke points, on-screen pixels
  const [strokePoints, setStrokePoints] = useState<[number, number][]>([]);

  const addHighlight = useAddHighlight();
  const addTextBox = useAddTextBox();
  const addStickyNote = useAddStickyNote();
  const addFreehand = useAddFreehand();
  const addUnderline = useAddUnderline();
  const addStrikethrough = useAddStrikethrough();
  const addWhiteout = useAddWhiteout();

  const isSaving = addHighlight.isPending || addTextBox.isPending || addStickyNote.isPending || addFreehand.isPending
    || addUnderline.isPending || addStrikethrough.isPending || addWhiteout.isPending;
  const token = typeof window !== "undefined" ? window.localStorage.getItem("pdf360_access_token") : null;
  const previewUrl = `${apiClient.defaults.baseURL}/files/${fileId}/preview/${page}${token ? `?token=${encodeURIComponent(token)}` : ""}`;

  function getRelativePoint(e: React.MouseEvent) {
    const rect = imgRef.current!.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  }

  function handleMouseDown(e: React.MouseEvent) {
    const { x, y } = getRelativePoint(e);
    if (tool === "highlight" || tool === "underline" || tool === "strikethrough" || tool === "whiteout") {
      setDragStart({ x, y });
    } else if (tool === "draw") {
      setStrokePoints([[x, y]]);
    } else if (tool === "text") {
      const text = window.prompt("Text to insert:");
      if (text) {
        addTextBox.mutate(
          {
            file_id: fileId, page,
            x0: toPdfPoints(x), y0: toPdfPoints(y),
            x1: toPdfPoints(x + 180), y1: toPdfPoints(y + 30),
            text, font_size: 12, color,
          },
          { onSuccess: (file) => setFileId(file.id) }
        );
      }
    } else if (tool === "note") {
      const note = window.prompt("Note text:");
      if (note) {
        addStickyNote.mutate(
          { file_id: fileId, page, x: toPdfPoints(x), y: toPdfPoints(y), note },
          { onSuccess: (file) => setFileId(file.id) }
        );
      }
    }
  }

  function handleMouseMove(e: React.MouseEvent) {
    const { x, y } = getRelativePoint(e);
    if ((tool === "highlight" || tool === "underline" || tool === "strikethrough" || tool === "whiteout") && dragStart) {
      setDragBox({
        x: Math.min(x, dragStart.x), y: Math.min(y, dragStart.y),
        w: Math.abs(x - dragStart.x), h: Math.abs(y - dragStart.y),
      });
    } else if (tool === "draw" && strokePoints.length > 0) {
      setStrokePoints((prev) => [...prev, [x, y]]);
    }
  }

  function handleMouseUp() {
    if (dragStart && dragBox && dragBox.w > 5 && dragBox.h > 5) {
      const rect = {
        file_id: fileId, page,
        x0: toPdfPoints(dragBox.x), y0: toPdfPoints(dragBox.y),
        x1: toPdfPoints(dragBox.x + dragBox.w), y1: toPdfPoints(dragBox.y + dragBox.h),
      };
      const onSuccess = { onSuccess: (file: { id: string }) => setFileId(file.id) };
      if (tool === "highlight") {
        addHighlight.mutate({ ...rect, color }, onSuccess);
      } else if (tool === "underline") {
        addUnderline.mutate({ ...rect, color }, onSuccess);
      } else if (tool === "strikethrough") {
        addStrikethrough.mutate({ ...rect, color }, onSuccess);
      } else if (tool === "whiteout") {
        addWhiteout.mutate(rect, onSuccess);
      }
    } else if (tool === "draw" && strokePoints.length > 1) {
      addFreehand.mutate(
        {
          file_id: fileId, page,
          strokes: [strokePoints.map(([x, y]) => [toPdfPoints(x), toPdfPoints(y)] as [number, number])],
          color, width: 2.5,
        },
        { onSuccess: (file) => setFileId(file.id) }
      );
    }
    setDragStart(null);
    setDragBox(null);
    setStrokePoints([]);
  }

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        {TOOLS.map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              onClick={() => setTool(t.id)}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm ${
                tool === t.id ? "bg-ink text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300"
              }`}
            >
              <Icon size={14} /> {t.label}
            </button>
          );
        })}
        <input
          type="color"
          value={color}
          onChange={(e) => setColor(e.target.value)}
          className="h-8 w-8 cursor-pointer rounded border border-slate-300 dark:border-slate-700"
          title="Color"
        />
        {isSaving && (
          <span className="flex items-center gap-1.5 text-sm text-slate-500">
            <Loader2 size={14} className="animate-spin" /> Saving…
          </span>
        )}
      </div>

      <div className="relative inline-block select-none">
        <img
          ref={imgRef}
          src={previewUrl}
          alt={`Page ${page}`}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          className="max-w-full cursor-crosshair rounded-lg border border-slate-200 dark:border-slate-800"
          draggable={false}
        />
        {dragBox && (
          <div
            className="pointer-events-none absolute border-2"
            style={{
              left: dragBox.x, top: dragBox.y, width: dragBox.w, height: dragBox.h,
              borderColor: color, backgroundColor: `${color}33`,
            }}
          />
        )}
        {strokePoints.length > 1 && (
          <svg className="pointer-events-none absolute inset-0 h-full w-full">
            <polyline
              points={strokePoints.map(([x, y]) => `${x},${y}`).join(" ")}
              fill="none"
              stroke={color}
              strokeWidth={2.5}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        )}
      </div>
      <p className="mt-2 text-xs text-slate-400">
        Each edit saves as a new version — download the latest from Files when you're done.
      </p>
    </div>
  );
}
