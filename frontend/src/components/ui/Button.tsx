import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      disabled,
      children,
      type = 'button',
      leftIcon,
      rightIcon,
      ...props
    },
    ref
  ) => {
    const variantClasses = {
      primary:
        'bg-gradient-to-r from-brand-600 to-indigo-600 text-white shadow-md shadow-brand-500/20 hover:from-brand-500 hover:to-indigo-500 focus:ring-brand-500 border border-transparent',
      secondary:
        'bg-slate-900 border border-slate-800 text-slate-200 hover:bg-slate-800 hover:text-white focus:ring-slate-500',
      outline:
        'border border-slate-700 bg-transparent text-slate-200 hover:bg-slate-800/80 hover:border-slate-600 focus:ring-slate-500',
      ghost:
        'text-slate-300 hover:bg-slate-800/60 hover:text-white focus:ring-slate-500 border border-transparent',
    };

    const sizeClasses = {
      sm: 'px-3 py-1.5 text-xs rounded-md gap-1.5',
      md: 'px-4 py-2 text-sm rounded-lg gap-2',
      lg: 'px-6 py-3 text-base rounded-xl gap-2.5 font-semibold',
    };

    return (
      <button
        ref={ref}
        type={type}
        disabled={disabled || isLoading}
        className={cn(
          'inline-flex items-center justify-center font-medium transition-all duration-200 select-none focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {isLoading && <Loader2 className="h-4 w-4 animate-spin shrink-0" />}
        {!isLoading && leftIcon && <span className="shrink-0">{leftIcon}</span>}
        {children && <span>{children}</span>}
        {!isLoading && rightIcon && <span className="shrink-0">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
export default Button;
