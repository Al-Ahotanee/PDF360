"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";

export type AdminUser = {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
};

export function useAdminUsers() {
  return useQuery({
    queryKey: ["admin", "users"],
    queryFn: async () => (await apiClient.get<AdminUser[]>("/admin/users")).data,
  });
}

export function useSetUserRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ userId, roleName }: { userId: string; roleName: string }) =>
      (await apiClient.patch(`/admin/users/${userId}/role`, { role_name: roleName })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
  });
}

export function useSetUserActive() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ userId, isActive }: { userId: string; isActive: boolean }) =>
      (await apiClient.patch(`/admin/users/${userId}/active`, { is_active: isActive })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
  });
}

export type AnalyticsSummary = {
  total_users: number;
  active_users: number;
  total_files: number;
  total_jobs: number;
  premium_subscribers: number;
  total_revenue: number;
};

export type SystemHealth = {
  status: string;
  queued_jobs: number;
  processing_jobs: number;
  failed_jobs_last_100: number;
};

export type AuditLogEntry = {
  id: string;
  actor_id: string | null;
  action: string;
  target_type: string | null;
  target_id: string | null;
  metadata_json: Record<string, unknown>;
};

export function useAdminAnalytics() {
  return useQuery({
    queryKey: ["admin", "analytics"],
    queryFn: async () => (await apiClient.get<AnalyticsSummary>("/admin/analytics")).data,
  });
}

export function useAdminSystemHealth() {
  return useQuery({
    queryKey: ["admin", "system-health"],
    queryFn: async () => (await apiClient.get<SystemHealth>("/admin/system-health")).data,
    refetchInterval: 15000,
  });
}

export function useAdminAuditLogs() {
  return useQuery({
    queryKey: ["admin", "audit-logs"],
    queryFn: async () => (await apiClient.get<AuditLogEntry[]>("/admin/audit-logs")).data,
  });
}
