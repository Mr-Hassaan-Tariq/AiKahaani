import { forwardRef } from 'react';

import { cn } from 'lib/utils';

interface IconProps extends React.SVGProps<SVGSVGElement> {
  active?: boolean;
}

const CrownIcon = forwardRef<SVGSVGElement, IconProps>(function icon(
  { className, active = false, ...props },
  ref,
) {
  const stroke = active ? '#20BF0E' : '#AAACA6';

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      className={cn(className, stroke)}
      ref={ref}
      {...props}
    >
      <path
        d="M16.7 18.9804H7.3C6.88 18.9804 6.41 18.6504 6.27 18.2504L2.13 6.67035C1.54 5.01035 2.23 4.50035 3.65 5.52035L7.55 8.31035C8.2 8.76035 8.94 8.53035 9.22 7.80035L10.98 3.11035C11.54 1.61035 12.47 1.61035 13.03 3.11035L14.79 7.80035C15.07 8.53035 15.81 8.76035 16.45 8.31035L20.11 5.70035C21.67 4.58035 22.42 5.15035 21.78 6.96035L17.74 18.2704C17.59 18.6504 17.12 18.9804 16.7 18.9804Z"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M6.5 22H17.5"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M9.5 14H14.5"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
});

export default CrownIcon;
