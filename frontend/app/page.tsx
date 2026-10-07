import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 px-6 text-center">
      <h1 className="font-display text-4xl font-bold tracking-tight text-ink dark:text-white">PDF360</h1>
      <p className="text-lg text-slate-500">Everything PDF. One Platform.</p>
      <Link
        href="/login"
        className="mt-2 rounded-lg bg-signal px-5 py-2.5 text-sm font-semibold text-ink hover:bg-signal-dark hover:text-white"
      >
        Sign in
      </Link>
    </main>
  );
}
