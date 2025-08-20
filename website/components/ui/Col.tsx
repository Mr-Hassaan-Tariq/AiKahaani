import { DetailedHTMLProps, HTMLAttributes } from 'react';

import { cn } from 'lib/utils';

type ColProps = DetailedHTMLProps<HTMLAttributes<HTMLDivElement>, HTMLDivElement>;

export default function Col({ children, className, ...props }: ColProps) {
  return (
    <div className={cn('flex flex-col justify-between gap-3', className)} {...props}>
      {children}
    </div>
  );
}
