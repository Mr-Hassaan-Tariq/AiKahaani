import React, { HTMLAttributes } from 'react';

import { cn } from 'lib/utils';

type H5Props = HTMLAttributes<HTMLParagraphElement> & {
  children?: React.ReactNode;
  className?: string;
};

export default function H5({ children, className = '', ...props }: H5Props) {
  return (
    <p
      className={cn('font-figtree text-sm font-semibold leading-4 text-white', className)}
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...props}
    >
      {children}
    </p>
  );
}
