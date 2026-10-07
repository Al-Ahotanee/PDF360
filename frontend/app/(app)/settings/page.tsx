"use client";

import { useState } from "react";
import { Topbar } from "@/components/layout/Topbar";
import { ToolCard, PrimaryButton } from "@/components/tools/ToolCard";
import { useAuth } from "@/lib/auth/context";
import {
  useApiKeys,
  useChangePlan,
  useCreateApiKey,
  usePayments,
  useRevokeApiKey,
  useSubscription,
} from "@/hooks/useBilling";

const PLAN_LABELS: Record<string, string> = {
  free: "Free",
  premium_monthly: "Premium (Monthly)",
  premium_yearly: "Premium (Yearly)",
};

export default function SettingsPage() {
  const { user } = useAuth();
  const { data: subscription } = useSubscription();
  const { data: payments } = usePayments();
  const changePlan = useChangePlan();

  const { data: apiKeys } = useApiKeys();
  const createApiKey = useCreateApiKey();
  const revokeApiKey = useRevokeApiKey();
  const [newKeyName, setNewKeyName] = useState("");
  const [revealedKey, setRevealedKey] = useState<string | null>(null);

  async function handleCreateKey() {
    if (!newKeyName.trim()) return;
    const created = await createApiKey.mutateAsync(newKeyName.trim());
    setRevealedKey(created.raw_key);
    setNewKeyName("");
  }

  return (
    <>
      <Topbar title="Settings" />
      <main className="flex-1 space-y-4 overflow-y-auto p-6">
        <ToolCard title="Profile" description="Your account details.">
          <dl className="grid grid-cols-[120px_1fr] gap-y-2 text-sm">
            <dt className="text-slate-500">Name</dt>
            <dd className="text-ink dark:text-white">{user?.full_name ?? "—"}</dd>
            <dt className="text-slate-500">Email</dt>
            <dd className="text-ink dark:text-white">{user?.email}</dd>
            <dt className="text-slate-500">Role</dt>
            <dd className="capitalize text-ink dark:text-white">{user?.role.replace("_", " ")}</dd>
          </dl>
        </ToolCard>

        <ToolCard title="Billing & Subscription" description="Manage your PDF360 plan.">
          <div className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-3 dark:border-slate-800">
            <div>
              <p className="text-sm font-medium text-ink dark:text-white">
                Current plan: {subscription ? PLAN_LABELS[subscription.plan] : "—"}
              </p>
              {subscription?.current_period_end && (
                <p className="text-xs text-slate-500">Renews {new Date(subscription.current_period_end).toLocaleDateString()}</p>
              )}
            </div>
            <span className="rounded-full bg-signal/20 px-2.5 py-1 text-xs font-medium capitalize text-ink dark:text-white">
              {subscription?.status ?? "—"}
            </span>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <PrimaryButton onClick={() => changePlan.mutate("premium_monthly")} disabled={subscription?.plan === "premium_monthly"}>
              Upgrade — Monthly ($9.99/mo)
            </PrimaryButton>
            <PrimaryButton onClick={() => changePlan.mutate("premium_yearly")} disabled={subscription?.plan === "premium_yearly"}>
              Upgrade — Yearly ($89.99/yr)
            </PrimaryButton>
            {subscription?.plan !== "free" && (
              <PrimaryButton onClick={() => changePlan.mutate("free")}>Downgrade to Free</PrimaryButton>
            )}
          </div>

          {payments && payments.length > 0 && (
            <div className="mt-4">
              <p className="mb-2 text-sm font-medium text-ink dark:text-white">Payment history</p>
              <ul className="space-y-1 text-sm text-slate-500">
                {payments.map((p) => (
                  <li key={p.id} className="flex justify-between border-b border-slate-100 py-1 dark:border-slate-800">
                    <span>{new Date(p.created_at).toLocaleDateString()}</span>
                    <span className="capitalize">{p.status}</span>
                    <span>
                      {p.currency} {p.amount.toFixed(2)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </ToolCard>

        <ToolCard title="Notifications" description="Manage how PDF360 notifies you about completed jobs.">
          <p className="text-sm text-slate-500">
            In-app notifications are on by default. Email and push preferences are planned for a future update.
          </p>
        </ToolCard>

        <ToolCard title="API Keys" description="Generate keys for programmatic access to PDF360.">
          <div className="flex gap-2">
            <input
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              placeholder='Key name, e.g. "CI server"'
              className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-ink"
            />
            <PrimaryButton onClick={handleCreateKey} disabled={!newKeyName.trim() || createApiKey.isPending}>
              Generate key
            </PrimaryButton>
          </div>

          {revealedKey && (
            <div className="mt-3 rounded-lg border border-signal bg-signal/10 px-4 py-3 text-sm">
              <p className="font-medium text-ink dark:text-white">Copy this key now — it won&apos;t be shown again:</p>
              <code className="mt-1 block break-all text-xs">{revealedKey}</code>
            </div>
          )}

          <ul className="mt-4 space-y-2">
            {apiKeys?.map((key) => (
              <li
                key={key.id}
                className="flex items-center justify-between rounded-lg border border-slate-200 px-4 py-2 text-sm dark:border-slate-800"
              >
                <div>
                  <p className="font-medium text-ink dark:text-white">{key.name}</p>
                  <p className="text-xs text-slate-500">
                    {key.key_prefix}… · {key.is_active ? "Active" : "Revoked"}
                  </p>
                </div>
                {key.is_active && (
                  <button
                    onClick={() => revokeApiKey.mutate(key.id)}
                    className="rounded-lg px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30"
                  >
                    Revoke
                  </button>
                )}
              </li>
            ))}
            {apiKeys?.length === 0 && <p className="text-sm text-slate-500">No API keys yet.</p>}
          </ul>
        </ToolCard>
      </main>
    </>
  );
}
