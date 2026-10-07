"use client";

import { useRef, useState } from "react";
import { apiClient } from "@/lib/api/client";

type Box = { x0: number; y0: number; x1: number; y1: number };

/**
 * Renders the actual page (via /files/{id}/preview/{page}) and lets the
 * person drag boxes on it. Boxes are captured in on-screen pixels, then
 * scaled to PDF points (72 DPI) using the render DPI (100) before being
 * sent to /pdf/redact — so what you see is what gets redacted, without
 * the user ever entering a raw coordinate.
 */
const PREVIEW_DPI = 100;
const PDF_POINTS_PER_INCH = 72;

export function RedactionPicker({
  fileId,
  page,
  onBoxesChange,
}: {
  fileId: string;
  page: number;
  onBoxesChange: (boxes: Box[]) => void;
}) {
  const [boxes, setBoxes] = useState<Box[]>([]);
  const [drawing, setDrawing] = useState<{ startX: number; startY: number } | null>(null);
  const [current, setCurrent] = useState<{ x: number; y: number; w: number; h: number } | null>(null);
  const imgRef = useRef<HTMLImageElement>(null);

  const previewUrl = `${apiClient.defaults.baseURL}/files/${fileId}/preview/${page}`;

  function toPdfPoints(px: number) {
    return (px / PREVIEW_DPI) * PDF_POINTS_PER_INCH;
  }

  function handleMouseDown(e: React.MouseEvent<HTMLImageElement>) {
    const rect = e.currentTarget.getBoundingClientRect();
    setDrawing({ startX: e.clientX - rect.left, startY: e.clientY - rect.top });
  }

  function handleMouseMove(e: React.MouseEvent<HTMLImageElement>) {
    if (!drawing) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    setCurrent({
      x: Math.min(x, drawing.startX),
      y: Math.min(y, drawing.startY),
      w: Math.abs(x - drawing.startX),
      h: Math.abs(y - drawing.startY),
    });
  }

  function handleMouseUp() {
    if (!drawing || !current || current.w < 5 || current.h < 5) {
      setDrawing(null);
      setCurrent(null);
      return;
    }
    const newBox: Box = {
      x0: toPdfPoints(current.x),
      y0: toPdfPoints(current.y),
      x1: toPdfPoints(current.x + current.w),
      y1: toPdfPoints(current.y + current.h),
    };
    const updated = [...boxes, newBox];
    setBoxes(updated);
    onBoxesChange(updated);
    setDrawing(null);
    setCurrent(null);
  }

  function removeBox(index: number) {
    const updated = boxes.filter((_, i) => i !== index);
    setBoxes(updated);
    onBoxesChange(updated);
  }

  return (
    <div>
      <p className="mb-2 text-sm text-slate-500">
        Click and drag on the page below to mark areas to permanently redact.
      </p>
      <div className="relative inline-block select-none">
        <img
          ref={imgRef}
          src={previewUrl}
          alt={`Page ${page} preview`}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          className="max-w-full cursor-crosshair rounded-lg border border-slate-300"
          draggable={false}
        />
        {boxes.map((box, i) => (
          <div
            key={i}
            onClick={() => removeBox(i)}
            title="Click to remove"
            className="absolute cursor-pointer border-2 border-signal bg-signal/30 hover:bg-red-500/40"
            style={{
              left: (box.x0 / PDF_POINTS_PER_INCH) * PREVIEW_DPI,
              top: (box.y0 / PDF_POINTS_PER_INCH) * PREVIEW_DPI,
              width: ((box.x1 - box.x0) / PDF_POINTS_PER_INCH) * PREVIEW_DPI,
              height: ((box.y1 - box.y0) / PDF_POINTS_PER_INCH) * PREVIEW_DPI,
            }}
          />
        ))}
        {current && (
          <div
            className="pointer-events-none absolute border-2 border-dashed border-signal bg-signal/20"
            style={{ left: current.x, top: current.y, width: current.w, height: current.h }}
          />
        )}
      </div>
      {boxes.length > 0 && (
        <p className="mt-2 text-xs text-slate-500">{boxes.length} area(s) marked — click a box to remove it.</p>
      )}
    </div>
  );
}
