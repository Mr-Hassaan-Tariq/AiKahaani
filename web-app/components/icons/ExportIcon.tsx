import { forwardRef } from 'react';

import { cn } from 'lib/utils';

const FolderCloudIcon = forwardRef<SVGSVGElement, React.SVGProps<SVGSVGElement>>(function icon(
  { className, ...props },
  ref,
) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      className={cn(className)}
      ref={ref}
      {...props}
    >
      <path
        d="M10.961 5.93335C13.361 6.14002 14.341 7.37335 14.341 10.0733V10.16C14.341 13.14 13.1476 14.3333 10.1676 14.3333H5.82763C2.84763 14.3333 1.6543 13.14 1.6543 10.16V10.0733C1.6543 7.39335 2.62096 6.16002 4.98096 5.94002"
        stroke="#0E0F0C"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M8 10V2.41333"
        stroke="#0E0F0C"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M10.2342 3.89996L8.00091 1.66663L5.76758 3.89996"
        stroke="#0E0F0C"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  );
});

export default FolderCloudIcon;
