"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api/client";
import type { ApiKey, ApiKeyCreated, Payment, Subscription } from "@/types/api";

export function useSubscription() {
  return useQuery({
    queryKey: ["billing", "subscription"],
    queryFn: async () => (await apiClient.get<Subscription>("/billing/subscription")).data,
  });
}

export function usePayments() {
  return useQuery({
    queryKey: ["billing", "payments"],
    queryFn: async () => (await apiClient.get<Payment[]>("/billing/payments")).data,
  });
}

export function useChangePlan() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (plan: string) => (await apiClient.post<Subscription>("/billing/subscription", { plan })).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["billing"] });
    },
  });
}

export function useApiKeys() {
  return useQuery({
    queryKey: ["billing", "api-keys"],
    queryFn: async () => (await apiClient.get<ApiKey[]>("/billing/api-keys")).data,
  });
}

export function useCreateApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (name: string) => (await apiClient.post<ApiKeyCreated>("/billing/api-keys", { name })).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["billing", "api-keys"] });
    },
  });
}

export function useRevokeApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (keyId: string) => (await apiClient.delete(`/billing/api-keys/${keyId}`)).data,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["billing", "api-keys"] });
    },
  });
}
