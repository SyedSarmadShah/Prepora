import React from 'react';
import { Link } from 'react-router-dom';
import logoAsset from '../../assets/brand/prepora-logo.png';
import { cn } from '../../utils/cn';

export interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  href?: string;
}

const sizeClasses: Record<NonNullable<LogoProps['size']>, string> = {
  sm: 'h-8',
  md: 'h-10',
  lg: 'h-14',
};

export const Logo: React.FC<LogoProps> = ({
  size = 'md',
  className,
  href = '/',
}) => {
  const imageElement = (
    <img
      src={logoAsset}
      alt="Prepora"
      className={cn('w-auto object-contain select-none', sizeClasses[size], className)}
    />
  );

  if (href) {
    return (
      <Link
        to={href}
        className="inline-flex items-center rounded-lg transition-opacity hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-brand-500/50"
      >
        {imageElement}
      </Link>
    );
  }

  return imageElement;
};

export default Logo;
