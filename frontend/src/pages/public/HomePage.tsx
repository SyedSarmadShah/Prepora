import React from 'react';
import { 
  Shield, 
  CheckCircle, 
  Terminal, 
  Layers, 
  Cpu, 
  Zap, 
  Database, 
  Award, 
  BookOpen, 
  Sparkles,
  ArrowRight
} from 'lucide-react';

export const HomePage: React.FC = () => {
  return (
    <div className="relative overflow-hidden py-12 lg:py-20">
      {/* Background Decorative Gradients */}
      <div className="pointer-events-none absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-b from-brand-600/15 via-indigo-500/5 to-transparent blur-3xl" />

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10 space-y-16">
        
        {/* Hero Section */}
        <div className="text-center space-y-6 max-w-3xl mx-auto">
          {/* Status Badge */}
          <div className="inline-flex items-center space-x-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3.5 py-1 text-xs font-semibold text-emerald-400 backdrop-blur-md">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>Phase 1 - Step 2: Frontend Foundation Active</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white font-heading">
            Next-Gen Exam Prep for <br className="hidden sm:inline" />
            <span className="gradient-text">Pakistan Armed Forces</span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed">
            Prepora is engineered for military entry tests (PMA, PAF, Navy, ISSB, ASF) and competitive government exams. Experience adaptive practice sessions, timed mock tests, and real-time weak topic diagnostics.
          </p>

          {/* Action CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <button className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-brand-500/25 hover:from-brand-500 hover:to-indigo-500 transition-all hover:scale-105">
              Explore Exam Tracks
              <ArrowRight className="ml-2 h-4 w-4" />
            </button>
            <a 
              href="#system-status" 
              className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl border border-slate-800 bg-slate-900/60 px-6 py-3.5 text-sm font-semibold text-slate-300 hover:bg-slate-800 hover:text-white transition-all backdrop-blur-sm"
            >
              Inspect Architecture
            </a>
          </div>
        </div>

        {/* System Runtime Status Card */}
        <div id="system-status" className="glass-panel rounded-2xl p-6 sm:p-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800/80 pb-4 gap-4">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-brand-500/10 border border-brand-500/20 text-brand-400">
                <Terminal className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white font-heading">Frontend Runtime Status</h3>
                <p className="text-xs text-slate-400">Vite + React 19 + TypeScript + Tailwind CSS</p>
              </div>
            </div>
            <div className="flex items-center space-x-2 text-xs font-mono bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 text-emerald-400">
              <CheckCircle className="h-4 w-4" />
              <span>REACT_APP_READY</span>
            </div>
          </div>

          {/* Module Verification Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="glass-card rounded-xl p-4 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Infrastructure</span>
                <Cpu className="h-4 w-4 text-brand-400" />
              </div>
              <p className="text-sm font-semibold text-white">Vite 6 + React 19</p>
              <p className="text-[11px] text-slate-500">Strict TypeScript mode enabled</p>
            </div>

            <div className="glass-card rounded-xl p-4 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Styling Engine</span>
                <Sparkles className="h-4 w-4 text-indigo-400" />
              </div>
              <p className="text-sm font-semibold text-white">Tailwind CSS 3.4</p>
              <p className="text-[11px] text-slate-500">Curated military color tokens</p>
            </div>

            <div className="glass-card rounded-xl p-4 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Network Layer</span>
                <Zap className="h-4 w-4 text-amber-400" />
              </div>
              <p className="text-sm font-semibold text-white">Axios Interceptors</p>
              <p className="text-[11px] text-slate-500">RFC 7807 Error Envelope Ready</p>
            </div>

            <div className="glass-card rounded-xl p-4 space-y-2">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>State & Storage</span>
                <Database className="h-4 w-4 text-purple-400" />
              </div>
              <p className="text-sm font-semibold text-white">Storage Service</p>
              <p className="text-[11px] text-slate-500">Token persistence helpers</p>
            </div>
          </div>
        </div>

        {/* Target Exam Tracks Overview */}
        <div id="exam-tracks" className="space-y-8">
          <div className="text-center space-y-2">
            <h2 className="text-2xl sm:text-3xl font-bold text-white font-heading">
              Supported Exam Tracks
            </h2>
            <p className="text-sm text-slate-400 max-w-xl mx-auto">
              Curated syllabus taxonomies tailored for entry requirements of Pakistan Armed Forces academies and civil service tests.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Army */}
            <div className="glass-card rounded-2xl p-6 space-y-4 hover:border-emerald-500/40 group transition-all">
              <div className="h-12 w-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Shield className="h-6 w-6" />
              </div>
              <div>
                <span className="text-[10px] font-bold tracking-widest text-emerald-400 uppercase">Pakistan Army</span>
                <h3 className="text-lg font-bold text-white mt-1">PMA Long Course</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Initial academic test, intelligence MCQs (Verbal & Non-Verbal), and ISSB screening drills.
              </p>
            </div>

            {/* PAF */}
            <div className="glass-card rounded-2xl p-6 space-y-4 hover:border-sky-500/40 group transition-all">
              <div className="h-12 w-12 rounded-xl bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Award className="h-6 w-6" />
              </div>
              <div>
                <span className="text-[10px] font-bold tracking-widest text-sky-400 uppercase">Pakistan Air Force</span>
                <h3 className="text-lg font-bold text-white mt-1">PAF GDP & Aeronautical</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Physics, Mathematics, English, and spatial reasoning test battery for PAF officer intake.
              </p>
            </div>

            {/* Navy */}
            <div className="glass-card rounded-2xl p-6 space-y-4 hover:border-blue-500/40 group transition-all">
              <div className="h-12 w-12 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Layers className="h-6 w-6" />
              </div>
              <div>
                <span className="text-[10px] font-bold tracking-widest text-blue-400 uppercase">Pakistan Navy</span>
                <h3 className="text-lg font-bold text-white mt-1">PN Cadet Scheme</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Naval academy entrance exam covering general science, mathematics, and analytical reasoning.
              </p>
            </div>

            {/* FPSC */}
            <div className="glass-card rounded-2xl p-6 space-y-4 hover:border-amber-500/40 group transition-all">
              <div className="h-12 w-12 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <BookOpen className="h-6 w-6" />
              </div>
              <div>
                <span className="text-[10px] font-bold tracking-widest text-amber-400 uppercase">Civil Services</span>
                <h3 className="text-lg font-bold text-white mt-1">FPSC & Police Cadre</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                General Recruitment, Pakistan Affairs, Current Affairs, Every Day Science, and Islamiyat.
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
