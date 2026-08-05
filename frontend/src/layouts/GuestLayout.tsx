import React from 'react';
import { Header } from '../components/shared/Header';
import { Footer } from '../components/shared/Footer';

export interface GuestLayoutProps {
  children: React.ReactNode;
}

export const GuestLayout: React.FC<GuestLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-brand-500 selection:text-white">
      {/* Top Header */}
      <Header />

      {/* Main Content Body */}
      <main className="flex-1 w-full">{children}</main>

      {/* Footer */}
      <Footer />
    </div>
  );
};
