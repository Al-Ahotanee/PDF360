"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { PDFFile } from "@/types/api";

function useEditorAction<TReq extends object>(path: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (body: TReq) => (await apiClient.post<PDFFile>(path, body)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useAddHighlight() {
  return useEditorAction<{ file_id: string; page: number; x0: number; y0: number; x1: number; y1: number; color?: string }>(
    "/editor/highlight"
  );
}

export function useAddTextBox() {
  return useEditorAction<{
    file_id: string; page: number; x0: number; y0: number; x1: number; y1: number;
    text: string; font_size?: number; color?: string;
  }>("/editor/text-box");
}

export function useAddStickyNote() {
  return useEditorAction<{ file_id: string; page: number; x: number; y: number; note: string }>(
    "/editor/sticky-note"
  );
}

export function useAddFreehand() {
  return useEditorAction<{ file_id: string; page: number; strokes: [number, number][][]; color?: string; width?: number }>(
    "/editor/freehand"
  );
}

export function useAddUnderline() {
  return useEditorAction<{ file_id: string; page: number; x0: number; y0: number; x1: number; y1: number; color?: string }>(
    "/editor/underline"
  );
}

export function useAddStrikethrough() {
  return useEditorAction<{ file_id: string; page: number; x0: number; y0: number; x1: number; y1: number; color?: string }>(
    "/editor/strikethrough"
  );
}

export function useAddWhiteout() {
  return useEditorAction<{ file_id: string; page: number; x0: number; y0: number; x1: number; y1: number }>(
    "/editor/whiteout"
  );
}
