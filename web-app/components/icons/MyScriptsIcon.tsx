import { forwardRef } from 'react';

import { cn } from 'lib/utils';

interface IconProps extends React.SVGProps<SVGSVGElement> {
  active?: boolean;
}

const MyScriptsIcon = forwardRef<SVGSVGElement, IconProps>(function icon(
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
        d="M8 2V5"
        stroke={stroke}
        strokeWidth="1.2"
        strokeMiterlimit="10"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M16 2V5"
        stroke={stroke}
        strokeWidth="1.2"
        strokeMiterlimit="10"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M7 11H15"
        stroke={stroke}
        strokeWidth="1.2"
        strokeMiterlimit="10"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M7 15H12"
        stroke={stroke}
        strokeWidth="1.2"
        strokeMiterlimit="10"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M15 22H9C4 22 3 19.94 3 15.82V9.65C3 4.95 4.67 3.69 8 3.5H16C19.33 3.68 21 4.95 21 9.65V16"
        stroke={stroke}
        strokeWidth="1.2"
        strokeMiterlimit="10"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M21 16L15 22V19C15 17 16 16 18 16H21Z"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
});

export default MyScriptsIcon;
