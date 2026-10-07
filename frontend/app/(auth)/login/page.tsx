"use client";

import Link from "next/link";
import { useState } from "react";
import { FileText, Lock, ArrowRight, ShieldCheck, Sparkles, CheckCircle2 } from "lucide-react";
import { apiClient } from "@/lib/api/client";

const DEMO_PRESETS = [
  { role: "Super Admin", email: "superadmin@pdf360.internal", badge: "All Access" },
  { role: "Admin", email: "admin@pdf360.internal", badge: "Org Manager" },
  { role: "Pro User", email: "pro@pdf360.internal", badge: "Pro Plan" },
  { role: "Demo User", email: "demo@pdf360.internal", badge: "Free Plan" },
];

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const { data } = await apiClient.post("/auth/login", { email, password });
      window.localStorage.setItem("pdf360_access_token", data.access_token);
      window.localStorage.setItem("pdf360_refresh_token", data.refresh_token);
      window.location.href = "/dashboard";
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Incorrect email or password.");
    } finally {
      setLoading(false);
    }
  }

  function handleQuickFill(demoEmail: string) {
    setEmail(demoEmail);
    setPassword("Password123!");
    setError(null);
  }

  return (
    <div className="flex min-h-screen bg-[#070b12] text-slate-100 selection:bg-signal selection:text-ink">
      {/* Background glowing accents */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-[500px] w-[900px] rounded-full bg-gradient-to-b from-signal/15 via-blue-600/10 to-transparent blur-3xl opacity-70" />
      </div>

      <div className="flex flex-1 flex-col justify-center px-6 py-12 lg:px-8 max-w-md mx-auto w-full">
        {/* Branding header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2.5 mb-6 group">
            <div className="relative h-10 w-10 shrink-0">
              <div className="absolute inset-0 translate-x-1 translate-y-1 rotate-6 rounded-xl bg-signal/30 group-hover:rotate-12 transition-transform" />
              <div className="absolute inset-0 translate-x-0.5 translate-y-0.5 rotate-3 rounded-xl bg-signal/70" />
              <div className="absolute inset-0 flex items-center justify-center rounded-xl bg-gradient-to-tr from-signal-dark via-signal to-signal-light shadow-md shadow-signal/20">
                <FileText className="h-5 w-5 text-ink font-bold" />
              </div>
            </div>
            <span className="font-display text-2xl font-bold tracking-tight text-white">
              PDF<span className="text-signal">360</span>
            </span>
          </Link>
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold text-white">Welcome back</h1>
          <p className="mt-2 text-xs sm:text-sm text-slate-400">Sign in to manage and transform your documents</p>
        </div>

        {/* Card */}
        <div className="rounded-3xl border border-white/10 bg-[#0e1626]/80 p-8 shadow-2xl backdrop-blur-xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Work Email
              </label>
              <input
                type="email"
                required
                placeholder="name@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-signal focus:outline-none focus:ring-1 focus:ring-signal transition"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Password
                </label>
              </div>
              <input
                type="password"
                required
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-signal focus:outline-none focus:ring-1 focus:ring-signal transition"
              />
            </div>

            {error && (
              <div className="rounded-xl border border-rose-500/20 bg-rose-500/10 p-3 text-xs text-rose-400">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 inline-flex items-center justify-center gap-2 rounded-xl bg-signal px-4 py-3 text-sm font-bold text-ink shadow-lg shadow-signal/20 transition hover:bg-signal-light hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
            >
              {loading ? "Authenticating…" : "Sign In to Workspace"}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          {/* Quick-fill demo presets */}
          <div className="mt-6 pt-6 border-t border-white/10">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2.5 flex items-center gap-1.5">
              <Sparkles size={13} className="text-signal" /> Quick-Test Preset Accounts
            </p>
            <div className="grid grid-cols-2 gap-2">
              {DEMO_PRESETS.map((preset) => (
                <button
                  key={preset.email}
                  type="button"
                  onClick={() => handleQuickFill(preset.email)}
                  className="flex flex-col items-start rounded-xl border border-white/5 bg-white/[0.03] p-2.5 text-left text-xs transition hover:border-signal/40 hover:bg-white/[0.06]"
                >
                  <span className="font-semibold text-white truncate w-full">{preset.role}</span>
                  <span className="text-[10px] text-slate-400 truncate w-full mt-0.5">{preset.badge}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          Don&apos;t have an account yet?{" "}
          <Link href="/register" className="font-semibold text-signal hover:underline">
            Create an account free
          </Link>
        </p>
      </div>
    </div>
  );
}

