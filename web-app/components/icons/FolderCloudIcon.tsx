import { forwardRef } from 'react';

import { cn } from 'lib/utils';

const FolderCloudIcon = forwardRef<SVGSVGElement, React.SVGProps<SVGSVGElement>>(function icon(
  { className, ...props },
  ref,
) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
      className={cn(className)}
      ref={ref}
      {...props}
    >
      <path
        d="M7.49935 18.3333H5.83268C2.49935 18.3333 1.66602 17.5 1.66602 14.1666V5.83329C1.66602 2.49996 2.49935 1.66663 5.83268 1.66663H7.08268C8.33268 1.66663 8.6077 2.0333 9.0827 2.66664L10.3327 4.3333C10.6494 4.74997 10.8327 4.99996 11.666 4.99996H14.166C17.4993 4.99996 18.3327 5.83329 18.3327 9.16663V10.8333"
        stroke="white"
        stroke-width="1.5"
        stroke-miterlimit="10"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M11.4668 15.2667C9.50846 15.4084 9.50846 18.2417 11.4668 18.3834H16.1001C16.6585 18.3834 17.2085 18.1751 17.6168 17.8001C18.9918 16.6001 18.2584 14.2001 16.4501 13.9751C15.8001 10.0667 10.1501 11.5501 11.4835 15.2751"
        stroke="white"
        stroke-width="1.5"
        stroke-miterlimit="10"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  );
});

export default FolderCloudIcon;
