import React from 'react';
import { Logo } from '../components/brand/Logo';

export interface AuthLayoutProps {
  children: React.ReactNode;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen w-full bg-slate-950 text-slate-100 selection:bg-brand-500 selection:text-white flex flex-col items-center justify-center p-4 sm:p-6 lg:p-8 relative overflow-hidden">
      {/* Background Decorative Ambient Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-brand-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-80 h-80 bg-indigo-600/10 rounded-full blur-[100px] pointer-events-none" />

      {/* Main Centered Auth Container */}
      <div className="w-full max-w-md space-y-6 relative z-10">
        {/* Central Brand Logo Header */}
        <div className="flex flex-col items-center justify-center space-y-1 text-center">
          <Logo size="lg" href="/" />
          <p className="text-[11px] font-semibold tracking-widest text-brand-400 uppercase">
            Armed Forces Prep Platform
          </p>
        </div>

        {/* Auth Content Card */}
        <main className="w-full">{children}</main>

        {/* Footer Copyright */}
        <div className="text-center text-xs text-slate-500">
          <p>© {new Date().getFullYear()} Prepora Platform. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout;
