"use client";

import Link from "next/link";
import { useState } from "react";
import { FileText, ArrowRight, ShieldCheck, CheckCircle2 } from "lucide-react";
import { apiClient } from "@/lib/api/client";

export default function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiClient.post("/auth/register", {
        email,
        password,
        full_name: fullName || null,
      });
      const { data } = await apiClient.post("/auth/login", { email, password });
      window.localStorage.setItem("pdf360_access_token", data.access_token);
      window.localStorage.setItem("pdf360_refresh_token", data.refresh_token);
      window.location.href = "/dashboard";
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Could not create your account. Please try again.");
    } finally {
      setLoading(false);
    }
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
          <h1 className="font-display text-2xl sm:text-3xl font-extrabold text-white">Start for free today</h1>
          <p className="mt-2 text-xs sm:text-sm text-slate-400">Transform, merge, and edit documents in one unified platform</p>
        </div>

        {/* Card */}
        <div className="rounded-3xl border border-white/10 bg-[#0e1626]/80 p-8 shadow-2xl backdrop-blur-xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                placeholder="Jane Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:border-signal focus:outline-none focus:ring-1 focus:ring-signal transition"
              />
            </div>

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
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-1.5">
                Password
              </label>
              <input
                type="password"
                required
                minLength={8}
                placeholder="Min. 8 characters"
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
              {loading ? "Creating account…" : "Create Workspace Account"}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-white/5 space-y-2 text-xs text-slate-400">
            <div className="flex items-center gap-2">
              <CheckCircle2 size={14} className="text-emerald-400" />
              <span>Free tier forever, no credit card required</span>
            </div>
            <div className="flex items-center gap-2">
              <ShieldCheck size={14} className="text-emerald-400" />
              <span>Sandboxed container isolation & AES-256 encryption</span>
            </div>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          Already have an account?{" "}
          <Link href="/login" className="font-semibold text-signal hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

