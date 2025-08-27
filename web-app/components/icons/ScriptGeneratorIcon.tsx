import { forwardRef } from 'react';

import { cn } from 'lib/utils';

interface IconProps extends React.SVGProps<SVGSVGElement> {
  active?: boolean;
}

const ScriptGeneratorIcon = forwardRef<SVGSVGElement, IconProps>(function icon(
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
        d="M3.5 20.5004C4.33 21.3304 5.67 21.3304 6.5 20.5004L19.5 7.50043C20.33 6.67043 20.33 5.33043 19.5 4.50043C18.67 3.67043 17.33 3.67043 16.5 4.50043L3.5 17.5004C2.67 18.3304 2.67 19.6704 3.5 20.5004Z"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M18.01 8.99023L15.01 5.99023"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8.5 2.44L10 2L9.56 3.5L10 5L8.5 4.56L7 5L7.44 3.5L7 2L8.5 2.44Z"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M4.5 8.44L6 8L5.56 9.5L6 11L4.5 10.56L3 11L3.44 9.5L3 8L4.5 8.44Z"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M19.5 13.44L21 13L20.56 14.5L21 16L19.5 15.56L18 16L18.44 14.5L18 13L19.5 13.44Z"
        stroke={stroke}
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
});

export default ScriptGeneratorIcon;
