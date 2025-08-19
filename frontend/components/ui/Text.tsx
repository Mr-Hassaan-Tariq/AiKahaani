import { ReactNode } from 'react';

import { cn } from 'lib/utils';

type TypographyProps = {
  variant?: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl' | '5xl';
  children?: ReactNode;
  className?: string;
};

const baseStyles = {
  xs: 'text-xs leading-3.5',
  sm: 'text-sm leading-4',
  base: 'text-base',
  lg: 'text-lg leading-7 tracking-[-0.2px]',
  xl: 'text-xl font-medium leading-6 tracking-[-0.2px]',
  '2xl': 'text-2xl leading-7 tracking-[-0.2px] font-semibold',
  '3xl': 'text-3xl',
  '4xl': 'text-4xl',
  '5xl': 'text-5xl font-semibold leading-[120%] tracking-[-0.72px]',
} as const;

export default function Text({ variant = 'base', children, className }: Readonly<TypographyProps>) {
  return <div className={cn('font-figtree', baseStyles[variant], className)}>{children}</div>;
}
