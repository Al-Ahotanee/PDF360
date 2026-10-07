"use client";

import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { DashboardStats, Job, PDFFile } from "@/types/api";

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
