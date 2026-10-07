"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export function useToggleFavorite() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ fileId, isFavorite }: { fileId: string; isFavorite: boolean }) =>
      (await apiClient.patch(`/organization/files/${fileId}/favorite`, { is_favorite: isFavorite })).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useTrashFile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (fileId: string) => (await apiClient.post(`/organization/files/${fileId}/trash`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}
