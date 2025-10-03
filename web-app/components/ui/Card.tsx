import { DetailedHTMLProps, HTMLAttributes } from 'react';

import { cn } from 'lib/utils';

type ColProps = DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement>;

export default function Card({ children, className, ...props }: ColProps) {
  return (
    <div
      className={cn(
        'px-15 w-full rounded-3xl border border-[#BAFF3812] bg-brand-surface py-5 lg:px-14 lg:py-8',
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
