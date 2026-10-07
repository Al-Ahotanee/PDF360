"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { Job } from "@/types/api";

/**
 * Polls a job every 1.5s until it reaches a terminal state (done/failed).
 * This is the client-side half of the uniform job pattern described in
 * docs/02-architecture.md — every PDF operation returns a job_id, and the
 * UI always follows the same submit -> poll -> result flow.
 */
export function useJob(jobId: string | null) {
  const queryClient = useQueryClient();
  return useQuery({
    queryKey: ["job", jobId],
    queryFn: async () => (await apiClient.get<Job>(`/pdf/jobs/${jobId}`)).data,
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "done" || status === "failed") {
        queryClient.invalidateQueries({ queryKey: ["files"] });
        return false;
      }
      return 1500;
    },
  });
}
