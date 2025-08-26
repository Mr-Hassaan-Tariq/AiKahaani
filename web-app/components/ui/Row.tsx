import { DetailedHTMLProps, HTMLAttributes } from 'react';

import { cn } from 'lib/utils';

type RowProps = DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement>;

export default function Row({ children, className, ...props }: RowProps) {
  return (
    <div className={cn('flex items-center justify-between gap-3', className)} {...props}>
      {children}
    </div>
  );
}
