import React from 'react';
import { Shield } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-slate-800/80 bg-slate-950 py-12">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Col */}
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center space-x-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600">
                <Shield className="h-4 w-4 text-white" />
              </div>
              <span className="font-heading text-lg font-bold text-white">PREPORA</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Production-ready test preparation SaaS platform for Pakistan Armed Forces (PMA, PAF, Navy, ISSB, ASF) and FPSC examinations.
            </p>
          </div>

          {/* Exam Tracks */}
          <div>
            <h4 className="font-heading text-xs font-semibold uppercase tracking-wider text-slate-300 mb-3">
              Armed Forces Tracks
            </h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>PMA Long Course Initial Test</li>
              <li>PAF GDP & Aeronautical Eng.</li>
              <li>Pakistan Navy Cadets</li>
              <li>ISSB Intelligence & Screening</li>
            </ul>
          </div>

          {/* Civil Services */}
          <div>
            <h4 className="font-heading text-xs font-semibold uppercase tracking-wider text-slate-300 mb-3">
              Government Services
            </h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>FPSC General Recruitment</li>
              <li>ASF Assistant Inspector</li>
              <li>Police Executive Cadre</li>
              <li>General Ability Tests</li>
            </ul>
          </div>

          {/* Platform Tech */}
          <div>
            <h4 className="font-heading text-xs font-semibold uppercase tracking-wider text-slate-300 mb-3">
              System Architecture
            </h4>
            <ul className="space-y-2 text-xs text-slate-400">
              <li>React 19 + TypeScript + Vite</li>
              <li>Django 5 REST Framework</li>
              <li>PostgreSQL 16 Engine</li>
              <li>Safepay Gateway Integration</li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-slate-900 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500">
          <p>© {new Date().getFullYear()} Prepora Platform. All rights reserved.</p>
          <p className="mt-2 sm:mt-0 font-mono text-[11px] text-slate-600">
            Phase 1 - Step 2 Shell v1.0.0
          </p>
        </div>
      </div>
    </footer>
  );
};
