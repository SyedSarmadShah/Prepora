import React from 'react';
import { BookOpen, Award, CheckCircle2, ChevronRight } from 'lucide-react';
import { Logo } from '../brand/Logo';

export const Header: React.FC = () => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center">
            <Logo size="md" href="/" />
          </div>

          {/* Nav Items Placeholder */}
          <nav className="hidden md:flex items-center space-x-8">
            <a href="#exam-tracks" className="text-sm font-medium text-slate-300 hover:text-white transition-colors flex items-center gap-1.5">
              <Award className="h-4 w-4 text-brand-400" />
              Exam Tracks
            </a>
            <a href="#features" className="text-sm font-medium text-slate-300 hover:text-white transition-colors flex items-center gap-1.5">
              <BookOpen className="h-4 w-4 text-indigo-400" />
              Features
            </a>
            <a href="#status" className="text-sm font-medium text-slate-300 hover:text-white transition-colors flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              System Status
            </a>
          </nav>

          {/* Action CTAs Placeholder */}
          <div className="flex items-center space-x-3">
            <button className="hidden sm:inline-flex items-center justify-center rounded-lg px-4 py-2 text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-900 transition-all border border-slate-800">
              Sign In
            </button>
            <button className="inline-flex items-center justify-center rounded-lg bg-gradient-to-r from-brand-600 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-md shadow-brand-500/20 hover:from-brand-500 hover:to-indigo-500 transition-all">
              Get Started
              <ChevronRight className="ml-1 h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
