import { DetailedHTMLProps, HTMLAttributes } from 'react';

import { cn } from 'lib/utils';

type ColProps = DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement>;

export default function Card({ children, className, ...props }: ColProps) {
  return (
    <div
      className={cn(
        'w-full rounded-3xl border border-[#BAFF3812] bg-brand-surface px-4 py-5 lg:px-8 lg:py-8',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
