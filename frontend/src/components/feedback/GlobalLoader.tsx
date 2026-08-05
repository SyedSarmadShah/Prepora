import React from 'react';

export interface GlobalLoaderProps {
  fullScreen?: boolean;
  message?: string;
}

export const GlobalLoader: React.FC<GlobalLoaderProps> = ({
  fullScreen = false,
  message = 'Loading Prepora Platform...',
}) => {
  const content = (
    <div className="flex flex-col items-center justify-center space-y-4">
      <div className="relative flex items-center justify-center">
        {/* Outer Ring Pulse */}
        <div className="absolute h-16 w-16 rounded-full border-4 border-brand-500/20 animate-ping" />
        {/* Spinning Gradient Ring */}
        <div className="h-14 w-14 rounded-full border-4 border-slate-800 border-t-brand-500 border-r-indigo-400 animate-spin" />
        {/* Center Shield Icon Placeholder */}
        <div className="absolute h-6 w-6 rounded border border-brand-400/50 bg-brand-950 flex items-center justify-center text-xs font-bold text-brand-300">
          P
        </div>
      </div>
      {message && (
        <p className="text-sm font-medium text-slate-400 animate-pulse tracking-wide">
          {message}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 backdrop-blur-sm">
        {content}
      </div>
    );
  }

  return <div className="py-12 flex justify-center">{content}</div>;
};
