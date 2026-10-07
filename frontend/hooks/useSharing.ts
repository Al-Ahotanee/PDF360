"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { FileShare, SharePermission, SharedWithMe } from "@/types/api";

export function useFileShares(fileId: string) {
  return useQuery({
    queryKey: ["file-shares", fileId],
    queryFn: async () =>
      (await apiClient.get<FileShare[]>(`/collaboration/files/${fileId}/shares`)).data,
    enabled: Boolean(fileId),
  });
}

export function useShareFile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      fileId,
      email,
      permission,
    }: {
      fileId: string;
      email: string;
      permission: SharePermission;
    }) =>
      (
        await apiClient.post<FileShare>(`/collaboration/files/${fileId}/share`, {
          with_email: email,
          permission,
        })
      ).data,
    onSuccess: (_, { fileId }) => {
      queryClient.invalidateQueries({ queryKey: ["file-shares", fileId] });
      queryClient.invalidateQueries({ queryKey: ["shared-with-me"] });
    },
  });
}

export function useRevokeShare() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ shareId }: { shareId: string; fileId: string }) =>
      (await apiClient.delete(`/collaboration/shares/${shareId}`)).data,
    onSuccess: (_, { fileId }) => {
      queryClient.invalidateQueries({ queryKey: ["file-shares", fileId] });
      queryClient.invalidateQueries({ queryKey: ["shared-with-me"] });
    },
  });
}

export function useSharedWithMe() {
  return useQuery({
    queryKey: ["shared-with-me"],
    queryFn: async () =>
      (await apiClient.get<SharedWithMe[]>("/collaboration/shared-with-me")).data,
  });
}
