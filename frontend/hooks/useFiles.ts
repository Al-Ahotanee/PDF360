"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { PDFFile } from "@/types/api";

export function useFiles() {
  return useQuery({
    queryKey: ["files"],
    queryFn: async () => (await apiClient.get<PDFFile[]>("/files")).data,
  });
}

export function useUploadFile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append("upload", file);
      const { data } = await apiClient.post<PDFFile>("/files/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function downloadFileUrl(fileId: string, baseUrl: string) {
  return `${baseUrl}/files/${fileId}/download`;
}
