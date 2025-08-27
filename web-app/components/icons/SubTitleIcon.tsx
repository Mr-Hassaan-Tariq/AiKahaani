import { forwardRef } from 'react';

import { cn } from 'lib/utils';

interface IconProps extends React.SVGProps<SVGSVGElement> {
  active?: boolean;
}

const SubTitleIcon = forwardRef<SVGSVGElement, IconProps>(function icon(
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
        d="M9 22H15C20 22 22 20 22 15V9C22 4 20 2 15 2H9C4 2 2 4 2 9V15C2 20 4 22 9 22Z"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M17.5 17.0801H15.65"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M12.97 17.0801H6.5"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M17.5 13.3203H11.97"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M9.27 13.3203H6.5"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
});

export default SubTitleIcon;
