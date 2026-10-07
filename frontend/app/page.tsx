import Link from "next/link";
import {
  FileText,
  Combine,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  FileSignature,
  FilePlus2,
  Layers,
  ArrowRight,
  CheckCircle2,
  Zap,
  Lock,
  Cloud,
  Cpu,
  Users,
  Eye,
  Check,
  Shield,
} from "lucide-react";

export default function HomePage() {
  const tools = [
    {
      category: "Organize & Combine",
      title: "Merge & Split PDF",
      description: "Combine multiple PDFs in exact page sequences or split large documents into dedicated chapters.",
      icon: Combine,
      tag: "Fast & Lossless",
      color: "from-amber-500/20 to-orange-500/10 text-amber-500",
      href: "/tools/organize",
    },
    {
      category: "High-Fidelity Engine",
      title: "Convert to Any Format",
      description: "Convert PDFs to Word (DOCX), Excel spreadsheets, high-res images, plain text, and HTML effortlessly.",
      icon: RefreshCw,
      tag: "Bi-directional",
      color: "from-blue-500/20 to-cyan-500/10 text-blue-500",
      href: "/tools/convert",
    },
    {
      category: "Enterprise Security",
      title: "Encrypt, Protect & Watermark",
      description: "Military-grade AES-256 encryption, password authorization, dynamic watermarking, and metadata stripping.",
      icon: ShieldCheck,
      tag: "AES-256",
      color: "from-emerald-500/20 to-teal-500/10 text-emerald-500",
      href: "/tools/secure",
    },
    {
      category: "AI & Neural Vision",
      title: "OCR & Document Intelligence",
      description: "State-of-the-art OCR across 100+ languages with automatic summarization, table extraction, and search.",
      icon: Sparkles,
      tag: "AI Powered",
      color: "from-purple-500/20 to-indigo-500/10 text-purple-400",
      href: "/tools/ai",
    },
    {
      category: "Legal & Forms",
      title: "Form Filler & e-Signatures",
      description: "Auto-detect form fields, fill interactive AcroForms, export structured JSON form data, and stamp legal signatures.",
      icon: FileSignature,
      tag: "Compliant",
      color: "from-rose-500/20 to-pink-500/10 text-rose-500",
      href: "/tools/forms",
    },
    {
      category: "Automated Workflows",
      title: "High-Volume Batch Processing",
      description: "Process thousands of PDFs simultaneously in async queues with live websocket progress tracking.",
      icon: Layers,
      tag: "Async Celery",
      color: "from-sky-500/20 to-blue-500/10 text-sky-400",
      href: "/tools/batch",
    },
  ];

  const features = [
    {
      icon: Zap,
      title: "Instant In-Memory Streaming",
      desc: "Zero disk bottlenecks. Files stream seamlessly directly into Python PyMuPDF & pdfplumber engines with sub-second execution.",
    },
    {
      icon: Cloud,
      title: "Neon S3 Cloud Storage",
      desc: "Enterprise S3-compatible cloud object storage powered by Neon Serverless architecture. High durability with fast regional edge delivery.",
    },
    {
      icon: Lock,
      title: "Zero-Knowledge Privacy",
      desc: "Documents are processed inside sandboxed containers with strict workspace isolation. Data is encrypted in transit and at rest.",
    },
    {
      icon: Cpu,
      title: "Asynchronous Celery Workers",
      desc: "Heavy operations (OCR, PDF/A archival, batch conversions) execute asynchronously without blocking your browser UI.",
    },
  ];

  const pricingPlans = [
    {
      name: "Starter",
      badge: "Free Forever",
      price: "$0",
      period: "forever",
      desc: "Ideal for individual professionals and students needing everyday PDF utilities.",
      features: [
        "Up to 25 MB document sizes",
        "Merge, Split, Rotate & Reorder",
        "PDF to Word & Image conversion",
        "Standard OCR processing",
        "Direct local & Neon storage",
        "No credit card required",
      ],
      cta: "Get Started Free",
      popular: false,
      href: "/register",
    },
    {
      name: "Professional",
      badge: "Most Popular",
      price: "$12",
      period: "/month",
      desc: "For heavy document workflows, team collaboration, and AI summarization.",
      features: [
        "Unlimited file sizes (up to 500 MB)",
        "Advanced Multi-Language OCR",
        "AI Summaries & Question-Answering",
        "AcroForms filling & field extraction",
        "Team document sharing & mentions",
        "Priority asynchronous queue processing",
        "Audit trail & version history",
      ],
      cta: "Start 14-Day Free Trial",
      popular: true,
      href: "/register",
    },
    {
      name: "Enterprise",
      badge: "Custom Scale",
      price: "$49",
      period: "/seat/mo",
      desc: "Designed for legal, finance, and healthcare organizations with strict compliance needs.",
      features: [
        "Dedicated Celery worker capacity",
        "Custom Neon S3 bucket integration",
        "SSO / SAML 2.0 & Role-Based Access",
        "HIPAA & SOC-2 compliance mode",
        "Full REST API webhook access",
        "24/7 dedicated enterprise support",
      ],
      cta: "Contact Sales",
      popular: false,
      href: "/register",
    },
  ];

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 selection:bg-signal selection:text-ink">
      {/* Background glowing accents */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10">
        <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-[500px] w-[1000px] rounded-full bg-gradient-to-b from-signal/15 via-blue-600/10 to-transparent blur-3xl opacity-70" />
        <div className="absolute top-1/3 -left-40 h-[400px] w-[400px] rounded-full bg-purple-600/10 blur-3xl" />
        <div className="absolute top-2/3 -right-40 h-[400px] w-[400px] rounded-full bg-amber-500/10 blur-3xl" />
      </div>

      {/* Navigation Header */}
      <header className="sticky top-0 z-50 border-b border-white/5 bg-[#070b12]/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-3">
            {/* Logo mark */}
            <div className="relative h-9 w-9 shrink-0">
              <div className="absolute inset-0 translate-x-1 translate-y-1 rotate-6 rounded-lg bg-signal/30" />
              <div className="absolute inset-0 translate-x-0.5 translate-y-0.5 rotate-3 rounded-lg bg-signal/70" />
              <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-gradient-to-tr from-signal-dark via-signal to-signal-light shadow-md shadow-signal/20">
                <FileText className="h-5 w-5 text-ink font-bold" />
              </div>
            </div>
            <span className="font-display text-xl font-bold tracking-tight text-white">
              PDF<span className="text-signal">360</span>
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
            <a href="#features" className="transition hover:text-white">Features</a>
            <a href="#tools" className="transition hover:text-white">Tool Suite</a>
            <a href="#security" className="transition hover:text-white">Security & Cloud</a>
            <a href="#pricing" className="transition hover:text-white">Pricing</a>
          </nav>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="rounded-xl px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-white/5 hover:text-white"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="inline-flex items-center gap-1.5 rounded-xl bg-signal px-4 py-2 text-sm font-semibold text-ink shadow-lg shadow-signal/25 transition hover:bg-signal-light hover:scale-[1.02] active:scale-[0.98]"
            >
              Get Started Free
              <ArrowRight size={15} />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 md:pt-32 md:pb-28">
        <div className="mx-auto max-w-5xl px-6 text-center">
          {/* Animated Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-signal/30 bg-signal/10 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-signal mb-8 backdrop-blur-sm animate-pulse">
            <Sparkles size={14} className="text-signal" />
            <span>Next-Generation Document Cloud • 100% Free Tier</span>
          </div>

          <h1 className="font-display text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-white leading-[1.1]">
            Everything PDF. <br />
            <span className="bg-gradient-to-r from-signal via-amber-200 to-white bg-clip-text text-transparent">
              One Unified Workspace.
            </span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-lg sm:text-xl text-slate-400 font-normal leading-relaxed">
            Eliminate fragmented tools. Merge, edit, convert, OCR, sign, encrypt, and orchestrate high-volume PDF pipelines with enterprise precision.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 rounded-2xl bg-signal px-7 py-3.5 text-base font-semibold text-ink shadow-xl shadow-signal/25 transition hover:bg-signal-light hover:scale-105 active:scale-95"
            >
              Open Workspace Free
              <ArrowRight size={18} />
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-6 py-3.5 text-base font-medium text-slate-200 backdrop-blur-sm transition hover:bg-white/10 hover:border-white/20"
            >
              <Eye size={18} className="text-slate-400" />
              Live Interactive Demo
            </Link>
          </div>

          {/* Social Proof / Stats Pill */}
          <div className="mt-14 inline-flex flex-wrap items-center justify-center gap-8 border-y border-white/5 py-4 text-xs font-medium text-slate-400">
            <span className="flex items-center gap-2">
              <CheckCircle2 size={16} className="text-emerald-400" />
              Zero Credit Card Required
            </span>
            <span className="flex items-center gap-2">
              <ShieldCheck size={16} className="text-emerald-400" />
              AES-256 Cloud Encryption
            </span>
            <span className="flex items-center gap-2">
              <Cloud size={16} className="text-emerald-400" />
              Neon S3 Serverless Storage
            </span>
            <span className="flex items-center gap-2">
              <Cpu size={16} className="text-emerald-400" />
              Celery Distributed Workers
            </span>
          </div>
        </div>

        {/* Hero Interactive App Preview */}
        <div className="mx-auto mt-16 max-w-6xl px-6">
          <div className="relative rounded-3xl border border-white/10 bg-[#0e1626]/80 p-3 shadow-2xl backdrop-blur-xl">
            <div className="flex items-center justify-between border-b border-white/5 px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-rose-500/80" />
                <div className="h-3 w-3 rounded-full bg-amber-500/80" />
                <div className="h-3 w-3 rounded-full bg-emerald-500/80" />
                <span className="ml-3 text-xs font-mono text-slate-400">pdf360.app/dashboard</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 px-2 py-0.5 text-emerald-400 font-medium">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  API Connected
                </span>
              </div>
            </div>

            {/* Mock Dashboard Preview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-5">
              <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-4 text-left">
                <p className="text-xs text-slate-400 font-medium">Active Documents</p>
                <p className="text-2xl font-bold font-display text-white mt-1">1,482</p>
                <div className="mt-2 text-xs text-emerald-400 flex items-center gap-1">
                  ↑ 14% this month
                </div>
              </div>
              <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-4 text-left">
                <p className="text-xs text-slate-400 font-medium">Processing Time</p>
                <p className="text-2xl font-bold font-display text-white mt-1">0.42s</p>
                <div className="mt-2 text-xs text-slate-400 flex items-center gap-1">
                  Average per operation
                </div>
              </div>
              <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-4 text-left">
                <p className="text-xs text-slate-400 font-medium">OCR Accuracy</p>
                <p className="text-2xl font-bold font-display text-white mt-1">99.8%</p>
                <div className="mt-2 text-xs text-signal flex items-center gap-1">
                  Neural Tesseract engine
                </div>
              </div>
              <div className="rounded-2xl border border-white/5 bg-white/[0.02] p-4 text-left">
                <p className="text-xs text-slate-400 font-medium">Storage Engine</p>
                <p className="text-2xl font-bold font-display text-white mt-1">Neon S3</p>
                <div className="mt-2 text-xs text-blue-400 flex items-center gap-1">
                  Multi-region bucket
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section id="features" className="py-20 border-t border-white/5 bg-white/[0.01]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-signal">Engineered for Scale</h2>
            <h3 className="font-display text-3xl sm:text-4xl font-bold text-white mt-2">
              Built on High-Performance Document Architecture
            </h3>
            <p className="text-slate-400 mt-4 text-base">
              Say goodbye to sluggish web tools that crash on large files. PDF360 leverages native C++ PDF bindings, distributed Celery pipelines, and Neon object storage.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feat, idx) => {
              const Icon = feat.icon;
              return (
                <div
                  key={idx}
                  className="rounded-2xl border border-white/5 bg-[#0b1322] p-6 hover:border-signal/40 transition-all hover:-translate-y-1"
                >
                  <div className="h-10 w-10 rounded-xl bg-signal/10 flex items-center justify-center text-signal mb-4">
                    <Icon size={20} />
                  </div>
                  <h4 className="font-display text-lg font-semibold text-white">{feat.title}</h4>
                  <p className="text-sm text-slate-400 mt-2 leading-relaxed">{feat.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Tool Suite Bento Grid */}
      <section id="tools" className="py-24 border-t border-white/5">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex flex-col md:flex-row md:items-end justify-between mb-16 gap-4">
            <div>
              <h2 className="text-xs font-bold uppercase tracking-wider text-signal">Comprehensive Tool Suite</h2>
              <h3 className="font-display text-3xl sm:text-4xl font-bold text-white mt-2">
                Every Operation Under One Roof
              </h3>
            </div>
            <Link
              href="/register"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-signal hover:text-signal-light"
            >
              Explore all tools in dashboard <ArrowRight size={16} />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tools.map((tool, idx) => {
              const Icon = tool.icon;
              return (
                <div
                  key={idx}
                  className="group relative rounded-3xl border border-white/10 bg-[#0e1626]/60 p-7 transition hover:border-signal/50 hover:bg-[#121c32]/80 hover:shadow-xl hover:shadow-black/50"
                >
                  <div className="flex items-center justify-between mb-5">
                    <div className={`h-12 w-12 rounded-2xl bg-gradient-to-br ${tool.color} flex items-center justify-center transition group-hover:scale-110`}>
                      <Icon size={22} />
                    </div>
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">
                      {tool.tag}
                    </span>
                  </div>

                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">{tool.category}</p>
                  <h4 className="font-display text-xl font-bold text-white mt-1 group-hover:text-signal transition-colors">
                    {tool.title}
                  </h4>
                  <p className="text-sm text-slate-400 mt-2.5 leading-relaxed">
                    {tool.description}
                  </p>

                  <div className="mt-6 pt-4 border-t border-white/5 flex items-center justify-between text-xs font-medium text-slate-400 group-hover:text-white">
                    <span>Try tool</span>
                    <ArrowRight size={14} className="transform transition group-hover:translate-x-1 text-signal" />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Cloud & Security Section */}
      <section id="security" className="py-20 border-t border-white/5 bg-gradient-to-b from-[#0b1322] to-[#070b12]">
        <div className="mx-auto max-w-7xl px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-1 text-xs font-semibold text-emerald-400 mb-6">
                <ShieldCheck size={14} />
                <span>Zero-Trust Security & Compliance</span>
              </div>
              <h3 className="font-display text-3xl sm:text-4xl font-bold text-white leading-tight">
                Your Documents Never Leave Your Secure Perimeter
              </h3>
              <p className="mt-4 text-slate-300 text-base leading-relaxed">
                Whether you connect Neon S3 Web Storage, AWS S3, or local encrypted storage, PDF360 enforces automated access controls, workspace separation, and ephemeral temp-file destruction.
              </p>

              <div className="mt-8 space-y-4">
                <div className="flex items-start gap-3.5">
                  <div className="h-6 w-6 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5">
                    <Check size={14} strokeWidth={3} />
                  </div>
                  <div>
                    <h5 className="text-sm font-semibold text-white">Full S3 Compatibility with Neon Object Storage</h5>
                    <p className="text-xs text-slate-400 mt-0.5">Native AWS SDK / boto3 driver support for Neon API storage keys.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3.5">
                  <div className="h-6 w-6 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5">
                    <Check size={14} strokeWidth={3} />
                  </div>
                  <div>
                    <h5 className="text-sm font-semibold text-white">Idempotent Database Migrations</h5>
                    <p className="text-xs text-slate-400 mt-0.5">Robust PostgreSQL enum handling and Alembic auto-recovery on Neon PSQL.</p>
                  </div>
                </div>
                <div className="flex items-start gap-3.5">
                  <div className="h-6 w-6 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5">
                    <Check size={14} strokeWidth={3} />
                  </div>
                  <div>
                    <h5 className="text-sm font-semibold text-white">Granular Document Sharing & Permissions</h5>
                    <p className="text-xs text-slate-400 mt-0.5">Share with view, edit, or admin permissions, complete with user mentions and activity auditing.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-[#0e1626] p-8 shadow-2xl">
              <div className="flex items-center gap-3 border-b border-white/10 pb-4 mb-6">
                <Shield className="h-6 w-6 text-signal" />
                <h4 className="font-display font-semibold text-white text-lg">Enterprise Compliance Spec</h4>
              </div>

              <div className="space-y-4 font-mono text-xs">
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <span className="text-slate-400">Encryption Standard</span>
                  <span className="text-emerald-400 font-bold">AES-256-GCM / TLS 1.3</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <span className="text-slate-400">Storage Architecture</span>
                  <span className="text-blue-400 font-bold">Neon S3 / S3-Compatible</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <span className="text-slate-400">Database Driver</span>
                  <span className="text-amber-400 font-bold">Neon Serverless PostgreSQL</span>
                </div>
                <div className="flex justify-between items-center py-2 border-b border-white/5">
                  <span className="text-slate-400">Async Task Broker</span>
                  <span className="text-purple-400 font-bold">Embedded In-Memory Redis</span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-slate-400">Temporary File Lifecycle</span>
                  <span className="text-emerald-400 font-bold">Auto-Purged on Completion</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Comparison Section */}
      <section id="pricing" className="py-24 border-t border-white/5">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-signal">Transparent Pricing</h2>
            <h3 className="font-display text-3xl sm:text-4xl font-bold text-white mt-2">
              Start Free. Scale as Your Team Grows.
            </h3>
            <p className="text-slate-400 mt-4 text-base">
              No credit card required to deploy or use. Fully compatible with free tier hosting on Render & Neon.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
            {pricingPlans.map((plan, idx) => (
              <div
                key={idx}
                className={`relative flex flex-col justify-between rounded-3xl p-8 transition ${
                  plan.popular
                    ? "border-2 border-signal bg-[#121f36] shadow-2xl shadow-signal/15"
                    : "border border-white/10 bg-[#0e1626]/70 hover:border-white/20"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 rounded-full bg-signal px-3.5 py-0.5 text-xs font-bold uppercase tracking-wider text-ink shadow-md">
                    {plan.badge}
                  </div>
                )}

                <div>
                  <div className="flex justify-between items-center">
                    <h4 className="font-display text-xl font-bold text-white">{plan.name}</h4>
                    {!plan.popular && (
                      <span className="text-xs font-medium text-slate-400 bg-white/5 rounded-full px-2.5 py-0.5 border border-white/10">
                        {plan.badge}
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-slate-400 mt-2">{plan.desc}</p>

                  <div className="mt-6 flex items-baseline gap-1">
                    <span className="font-display text-4xl sm:text-5xl font-extrabold text-white">{plan.price}</span>
                    <span className="text-xs font-medium text-slate-400">{plan.period}</span>
                  </div>

                  <ul className="mt-8 space-y-3.5 text-sm text-slate-300">
                    {plan.features.map((feature, fIdx) => (
                      <li key={fIdx} className="flex items-center gap-2.5">
                        <Check size={16} className="text-signal shrink-0" />
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="mt-8 pt-6 border-t border-white/5">
                  <Link
                    href={plan.href}
                    className={`block w-full rounded-xl py-3 text-center text-sm font-semibold transition ${
                      plan.popular
                        ? "bg-signal text-ink hover:bg-signal-light shadow-lg shadow-signal/20"
                        : "bg-white/10 text-white hover:bg-white/20"
                    }`}
                  >
                    {plan.cta}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pre-Footer Call to Action */}
      <section className="py-20 border-t border-white/5 bg-gradient-to-b from-[#0e1626] to-[#070b12]">
        <div className="mx-auto max-w-4xl px-6 text-center">
          <h3 className="font-display text-3xl sm:text-5xl font-extrabold text-white">
            Ready to upgrade your document workflow?
          </h3>
          <p className="mt-4 text-slate-400 text-lg">
            Create your free account today and experience lightning-fast PDF tools powered by Python & Neon.
          </p>
          <div className="mt-8 flex justify-center">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 rounded-2xl bg-signal px-8 py-4 text-base font-bold text-ink shadow-xl shadow-signal/25 transition hover:bg-signal-light hover:scale-105 active:scale-95"
            >
              Get Started with PDF360
              <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-[#05080e] py-12 text-slate-400 text-xs">
        <div className="mx-auto max-w-7xl px-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded bg-signal flex items-center justify-center font-bold text-ink text-xs">
              P
            </div>
            <span className="font-display font-semibold text-white text-sm">PDF360</span>
            <span className="text-slate-500 ml-2">© {new Date().getFullYear()} PDF360 SaaS. All rights reserved.</span>
          </div>

          <div className="flex items-center gap-6">
            <a href="#features" className="hover:text-white transition">Features</a>
            <a href="#tools" className="hover:text-white transition">Tools</a>
            <a href="#security" className="hover:text-white transition">Security</a>
            <a href="#pricing" className="hover:text-white transition">Pricing</a>
            <Link href="/login" className="hover:text-white transition">Sign In</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
