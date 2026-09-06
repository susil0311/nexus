'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import {
  Brain, Mic, Link2, TrendingUp, AlertTriangle, BookOpen, Map,
  ChevronRight, Zap, Shield, BarChart3, ArrowRight, Star,
  CheckCircle2, Cpu, Database, Globe, Activity,
} from 'lucide-react';

function Counter({ target, suffix = '' }: { target: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    const step = Math.ceil(target / 60);
    const timer = setInterval(() => {
      setCount((c) => { if (c + step >= target) { clearInterval(timer); return target; } return c + step; });
    }, 20);
    return () => clearInterval(timer);
  }, [target]);
  return <span>{count.toLocaleString()}{suffix}</span>;
}

const features = [
  { icon: Mic, title: 'TIME Agent', subtitle: 'Voice-to-Schedule AI', description: 'Field supervisors speak in Hindi/English. Gemini 1.5 Flash transcribes and extracts structured progress events with ≥87% accuracy — no forms, no data entry.', color: 'from-violet-500 to-purple-600', badge: 'Gemini 1.5 Flash' },
  { icon: Link2, title: 'Semantic Linker', subtitle: 'NLP Activity Matching', description: 'MiniLM embeddings + fuzzy matching maps "pipeline hydro-test completed" → WBS node L3.2.4 in milliseconds. Auto-accepts ≥0.85 confidence; flags borderline matches for review.', color: 'from-blue-500 to-cyan-600', badge: 'ChromaDB + MiniLM' },
  { icon: TrendingUp, title: 'Delay Oracle', subtitle: 'XGBoost Forecasting', description: 'Predicts completion dates with SPI/CPI trend analysis. What-if simulator lets PMs model monsoon delays, resource constraints, and mitigation scenarios.', color: 'from-emerald-500 to-teal-600', badge: 'XGBoost ML' },
  { icon: AlertTriangle, title: 'Anomaly Sentinel', subtitle: 'Isolation Forest Alerts', description: 'Detects ghost progress, sudden SPI drops, repeated delays, and suspicious patterns. Six rule-based checks run alongside ML anomaly detection.', color: 'from-orange-500 to-red-600', badge: 'Isolation Forest' },
  { icon: BookOpen, title: 'Institutional Memory', subtitle: 'RAG Knowledge Base', description: 'Ask "Why do pipeline activities in Assam always slip in June?" — ChromaDB RAG retrieves historical lessons, contractor records, and corrective actions.', color: 'from-pink-500 to-rose-600', badge: 'RAG + ChromaDB' },
  { icon: Map, title: 'GIS Site Map', subtitle: 'Live Geospatial View', description: 'Pin-drop site zones on an interactive map. Filter by discipline, progress status, or anomaly flag. Ideal for remote supervision of pipeline corridors.', color: 'from-yellow-500 to-amber-600', badge: 'Mapbox GL' },
];

const techStack = [
  { label: 'Gemini 1.5 Flash', color: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
  { label: 'FastAPI', color: 'bg-green-500/20 text-green-300 border-green-500/30' },
  { label: 'Next.js 14', color: 'bg-gray-500/20 text-gray-300 border-gray-500/30' },
  { label: 'PostgreSQL', color: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' },
  { label: 'ChromaDB', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
  { label: 'XGBoost', color: 'bg-orange-500/20 text-orange-300 border-orange-500/30' },
  { label: 'MiniLM', color: 'bg-pink-500/20 text-pink-300 border-pink-500/30' },
  { label: 'Redis', color: 'bg-red-500/20 text-red-300 border-red-500/30' },
  { label: 'Celery', color: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' },
  { label: 'Docker', color: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30' },
];

const demoAccounts = [
  { role: 'Project Manager', email: 'pm@oilindia.com', password: 'demo1234', color: 'border-violet-500/50 bg-violet-500/5' },
  { role: 'Site Supervisor', email: 'supervisor@oilindia.com', password: 'demo1234', color: 'border-blue-500/50 bg-blue-500/5' },
  { role: 'Admin', email: 'admin@oilindia.com', password: 'demo1234', color: 'border-emerald-500/50 bg-emerald-500/5' },
];

const pipeline = [
  { icon: Mic, label: 'Voice / Text / Excel', sub: 'Field input (any format)', color: 'bg-violet-600' },
  { icon: Brain, label: 'Gemini Extraction', sub: 'NLP parsing + structuring', color: 'bg-blue-600' },
  { icon: Link2, label: 'Semantic Matching', sub: 'WBS activity linking', color: 'bg-cyan-600' },
  { icon: CheckCircle2, label: 'Human-in-Loop', sub: 'Review & approve queue', color: 'bg-teal-600' },
  { icon: BarChart3, label: 'Schedule Update', sub: 'Real-time SPI/CPI', color: 'bg-emerald-600' },
  { icon: AlertTriangle, label: 'Anomaly Alert', sub: 'Sentinel monitoring', color: 'bg-orange-600' },
];

export default function LandingPage() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  useEffect(() => {
    const handler = (e: MouseEvent) => setMousePos({ x: e.clientX, y: e.clientY });
    window.addEventListener('mousemove', handler);
    return () => window.removeEventListener('mousemove', handler);
  }, []);

  return (
    <div className="min-h-screen bg-[#070B14] text-white overflow-x-hidden">
      <div className="pointer-events-none fixed inset-0 z-0 transition-opacity duration-300" style={{ background: `radial-gradient(600px circle at ${mousePos.x}px ${mousePos.y}px, rgba(99,102,241,0.07), transparent 60%)` }} />

      {/* NAV */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-[#070B14]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center">
              <Cpu className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg tracking-tight">NEXUS PM</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-gray-400">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#pipeline" className="hover:text-white transition-colors">Architecture</a>
            <a href="#demo" className="hover:text-white transition-colors">Demo</a>
            <a href="#tech" className="hover:text-white transition-colors">Tech Stack</a>
          </div>
          <Link href="/login" className="flex items-center gap-2 px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-sm font-medium transition-colors">
            Launch App <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      {/* HERO */}
      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-16">
        <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.5) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.5) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />
        <div className="absolute top-1/3 left-1/4 w-96 h-96 bg-violet-600/20 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-1/2 right-1/4 w-80 h-80 bg-blue-600/15 rounded-full blur-[100px] pointer-events-none" />
        <div className="relative z-10 text-center max-w-5xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-violet-500/30 bg-violet-500/10 text-violet-300 text-xs font-medium mb-8">
            <Star className="w-3 h-3 fill-violet-400 text-violet-400" />
            SIH 2026 · PS No. SIH26122 · Oil India Limited
            <Star className="w-3 h-3 fill-violet-400 text-violet-400" />
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-tight mb-6">
            <span className="bg-gradient-to-r from-white via-violet-200 to-blue-300 bg-clip-text text-transparent">NEXUS PM</span>
            <br />
            <span className="text-3xl md:text-4xl font-semibold text-gray-300">Neural Execution · Unified Scheduling · Real-Time Truth</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto mb-4 leading-relaxed">
            AI-powered infrastructure project management that captures field progress through{' '}
            <strong className="text-violet-300">voice, text &amp; Excel</strong>, semantically links it to L5 WBS schedules, and surfaces{' '}
            <strong className="text-blue-300">real-time SPI/CPI forecasts</strong> — no manual data entry.
          </p>
          <p className="text-base text-gray-500 mb-10 italic">"From site voice to schedule truth — in under 15 minutes."</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/login" className="flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 font-semibold text-lg transition-all shadow-lg shadow-violet-500/25 hover:shadow-violet-500/40 hover:scale-105">
              <Zap className="w-5 h-5" /> Launch Live Demo <ChevronRight className="w-5 h-5" />
            </Link>
            <a href="#pipeline" className="flex items-center gap-2 px-8 py-4 rounded-xl border border-white/10 hover:border-white/20 bg-white/5 hover:bg-white/10 font-medium transition-all">
              <Activity className="w-5 h-5" /> See Architecture
            </a>
          </div>
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-3xl mx-auto">
            {[{ value: 87, suffix: '%', label: 'Extraction Accuracy' }, { value: 15, suffix: 'min', label: 'Field-to-Dashboard' }, { value: 6, suffix: '+', label: 'AI Components' }, { value: 11, suffix: ' tables', label: 'Smart DB Schema' }].map((s) => (
              <div key={s.label} className="rounded-xl border border-white/5 bg-white/[0.03] p-4">
                <div className="text-3xl font-extrabold text-violet-300"><Counter target={s.value} suffix={s.suffix} /></div>
                <div className="text-xs text-gray-500 mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PROBLEM */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto rounded-2xl border border-orange-500/20 bg-orange-500/5 p-8 md:p-12">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center flex-shrink-0 mt-1">
              <AlertTriangle className="w-5 h-5 text-orange-400" />
            </div>
            <div>
              <p className="text-xs font-mono text-orange-400 mb-2">PROBLEM STATEMENT · SIH26122</p>
              <h2 className="text-2xl font-bold text-white mb-4">The Data Gap in Indian Infrastructure Projects</h2>
              <p className="text-gray-300 leading-relaxed mb-4">
                Oil India Limited manages 200+ simultaneous pipeline and infrastructure projects across remote Assam, Rajasthan and offshore assets. Field DPRs are captured on paper, WhatsApp, and Excel spreadsheets — creating a <strong className="text-orange-300">2–7 day reporting lag</strong> and systematic schedule distortions of 15–40% that go undetected until milestone reviews.
              </p>
              <p className="text-gray-400 leading-relaxed">
                NEXUS PM eliminates this gap with an intelligent data capture layer that works the way field engineers actually communicate — voice, free text, or existing DPR formats — and automatically links every update to the master schedule with AI-validated confidence scores.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-violet-400 text-sm font-mono mb-3">AI CAPABILITIES</p>
            <h2 className="text-4xl font-bold">Six Intelligent Layers</h2>
            <p className="text-gray-400 mt-3 max-w-2xl mx-auto">Each layer is independently deployable and production-hardened with mock fallbacks for zero-downtime demo safety.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <div key={f.title} className="group relative rounded-2xl border border-white/5 bg-white/[0.02] p-6 hover:border-white/10 hover:bg-white/[0.04] transition-all duration-300 overflow-hidden">
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl ${f.color} opacity-5 rounded-full -translate-y-8 translate-x-8 group-hover:opacity-10 transition-opacity`} />
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4`}>
                  <f.icon className="w-5 h-5 text-white" />
                </div>
                <div className="text-xs text-gray-500 mb-1">{f.subtitle}</div>
                <h3 className="text-lg font-bold mb-2">{f.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed mb-4">{f.description}</p>
                <span className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border border-white/10 bg-white/5 text-gray-300">
                  <Cpu className="w-3 h-3" /> {f.badge}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PIPELINE */}
      <section id="pipeline" className="py-20 px-6 bg-white/[0.01]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-blue-400 text-sm font-mono mb-3">SYSTEM ARCHITECTURE</p>
            <h2 className="text-4xl font-bold">Field → AI → Schedule Pipeline</h2>
          </div>
          <div className="relative">
            <div className="absolute top-8 left-[10%] right-[10%] h-px bg-gradient-to-r from-violet-600 via-blue-600 to-emerald-600 hidden md:block" />
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              {pipeline.map((step, i) => (
                <div key={step.label} className="flex flex-col items-center text-center relative">
                  <div className={`w-16 h-16 rounded-2xl ${step.color} flex items-center justify-center mb-3 shadow-lg z-10 relative`}>
                    <step.icon className="w-7 h-7 text-white" />
                    <div className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-[#070B14] border border-white/20 flex items-center justify-center text-xs font-bold">{i + 1}</div>
                  </div>
                  <div className="text-sm font-semibold">{step.label}</div>
                  <div className="text-xs text-gray-500 mt-1">{step.sub}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="mt-16 grid md:grid-cols-3 gap-6">
            {[
              { icon: Globe, title: 'Frontend', tech: 'Next.js 14 · TypeScript · Tailwind', items: ['React Query · Zustand state', 'Recharts S-curves', 'PWA · Offline-ready'], color: 'border-violet-500/20' },
              { icon: Database, title: 'Backend', tech: 'FastAPI · PostgreSQL · Redis', items: ['Async SQLAlchemy', 'JWT Auth · RBAC', 'Celery workers · Audit SHA-256'], color: 'border-blue-500/20' },
              { icon: Brain, title: 'AI Service', tech: 'Python · Gemini · ChromaDB', items: ['MiniLM embeddings', 'XGBoost forecasting', 'Isolation Forest sentinel'], color: 'border-emerald-500/20' },
            ].map((box) => (
              <div key={box.title} className={`rounded-2xl border ${box.color} bg-white/[0.02] p-6`}>
                <div className="flex items-center gap-3 mb-3">
                  <box.icon className="w-5 h-5 text-gray-400" />
                  <div><div className="font-semibold">{box.title}</div><div className="text-xs text-gray-500">{box.tech}</div></div>
                </div>
                <ul className="space-y-1.5">
                  {box.items.map((item) => (
                    <li key={item} className="flex items-center gap-2 text-sm text-gray-400">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" /> {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TECH STACK */}
      <section id="tech" className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-emerald-400 text-sm font-mono mb-3">TECH STACK</p>
          <h2 className="text-4xl font-bold mb-12">Built with Production-Grade Tools</h2>
          <div className="flex flex-wrap gap-3 justify-center">
            {techStack.map((t) => (
              <span key={t.label} className={`px-4 py-2 rounded-full border text-sm font-medium ${t.color}`}>{t.label}</span>
            ))}
          </div>
        </div>
      </section>

      {/* DEMO */}
      <section id="demo" className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-pink-400 text-sm font-mono mb-3">LIVE DEMO</p>
            <h2 className="text-4xl font-bold mb-3">Try It Right Now</h2>
            <p className="text-gray-400">Three pre-seeded accounts with realistic Oil India project data.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-4 mb-10">
            {demoAccounts.map((acc) => (
              <div key={acc.email} className={`rounded-2xl border ${acc.color} p-6`}>
                <div className="flex items-center gap-2 mb-3">
                  <Shield className="w-4 h-4 text-gray-400" />
                  <span className="text-xs text-gray-400 uppercase tracking-wider">{acc.role}</span>
                </div>
                <div className="font-mono text-sm text-white mb-1">{acc.email}</div>
                <div className="font-mono text-sm text-gray-500">pw: {acc.password}</div>
              </div>
            ))}
          </div>
          <div className="text-center">
            <Link href="/login" className="inline-flex items-center gap-3 px-10 py-5 rounded-2xl bg-gradient-to-r from-violet-600 to-blue-600 hover:from-violet-500 hover:to-blue-500 font-bold text-xl transition-all shadow-2xl shadow-violet-500/30 hover:shadow-violet-500/50 hover:scale-105">
              <Zap className="w-6 h-6" /> Launch NEXUS PM <ArrowRight className="w-6 h-6" />
            </Link>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-white/5 py-10 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-gray-500 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center">
              <Cpu className="w-3 h-3 text-white" />
            </div>
            <span className="font-semibold text-white">NEXUS PM</span>
            <span>· Neural Execution and Unified Scheduling Platform</span>
          </div>
          <div className="flex items-center gap-6">
            <span>SIH 2026</span><span>·</span><span>PS SIH26122</span><span>·</span><span>Oil India Limited</span><span>·</span><span>Team Sonora</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
