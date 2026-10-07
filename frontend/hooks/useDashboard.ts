"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { ActivityLogEntry, DashboardStats, Job, PDFFile } from "@/types/api";

export function useDashboardStats() {
  return useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: async () => (await apiClient.get<DashboardStats>("/dashboard/stats")).data,
  });
}

export function useRecentFiles() {
  return useQuery({
    queryKey: ["dashboard", "recent-files"],
    queryFn: async () => (await apiClient.get<PDFFile[]>("/dashboard/recent-files")).data,
  });
}

export function useRecentJobs() {
  return useQuery({
    queryKey: ["dashboard", "recent-jobs"],
    queryFn: async () => (await apiClient.get<Job[]>("/dashboard/recent-jobs")).data,
  });
}

export function useDashboardActivity() {
  return useQuery({
    queryKey: ["dashboard", "activity"],
    queryFn: async () => (await apiClient.get<ActivityLogEntry[]>("/dashboard/activity")).data,
  });
}
