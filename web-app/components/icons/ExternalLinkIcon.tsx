import { forwardRef } from 'react';

import { cn } from 'lib/utils';

const ExternalLinkIcon = forwardRef<SVGSVGElement, React.SVGProps<SVGSVGElement>>(function icon(
  { className, ...props },
  ref,
) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="17"
      viewBox="0 0 16 17"
      fill="none"
      className={cn(className)}
      ref={ref}
      {...props}
    >
      <path
        d="M8.66669 7.83385L14.1334 2.36719"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M14.6667 5.03398V1.83398H11.4667"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M7.33331 1.83398H5.99998C2.66665 1.83398 1.33331 3.16732 1.33331 6.50065V10.5007C1.33331 13.834 2.66665 15.1673 5.99998 15.1673H9.99998C13.3333 15.1673 14.6666 13.834 14.6666 10.5007V9.16732"
        stroke="white"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
});

export default ExternalLinkIcon;
