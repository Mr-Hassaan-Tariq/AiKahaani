'use client';

import Image from 'next/image';

interface LogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  priority?: boolean;
}

const sizes = {
  sm: { width: 155, height: 56, className: 'h-14 w-auto' },
  md: { width: 177, height: 64, className: 'h-16 w-auto' },
  lg: { width: 221, height: 80, className: 'h-20 w-auto' },
};

export function Logo({ className = '', size = 'sm', priority = false }: LogoProps) {
  const { width, height, className: sizeClass } = sizes[size];

  return (
    <>
      <Image
        src="/logos/colored-logo.svg"
        alt="AIKahaani"
        width={width}
        height={height}
        className={`${sizeClass} object-contain dark:hidden ${className}`}
        priority={priority}
      />
      <Image
        src="/logos/logo-dark.svg"
        alt="AIKahaani"
        width={width}
        height={height}
        className={`${sizeClass} hidden object-contain dark:block ${className}`}
        priority={priority}
      />
    </>
  );
}
