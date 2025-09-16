import { ButtonHTMLAttributes, ReactNode } from 'react';

import { cn } from 'lib/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  justIcon?: boolean;
  fullRounded?: boolean;
  children?: ReactNode | string;
  height?: 52 | 41;
  variant?: 'green' | 'gray' | 'ghost' | 'red';
}

export default function Button(props: ButtonProps) {
  const {
    children,
    justIcon,
    className,
    fullRounded = true,
    disabled,
    height = 52,
    variant = 'green',
    ...buttonProps
  } = props;

  return (
    <button
      className={cn(
        "flex w-full items-center justify-center gap-2.5 rounded-xl px-5 transition-all duration-200 [font-feature-settings:'liga'_off,'clig'_off] active:scale-95",
        fullRounded && 'rounded-full',
        !justIcon && 'min-w-5',
        heightClasses[height],
        variantClasses[variant],
        className,
        disabled && 'opacity-40 hover:bg-current active:scale-100',
        '',
      )}
      disabled={disabled}
      // eslint-disable-next-line react/jsx-props-no-spreading
      {...buttonProps}
    >
      {children}
    </button>
  );
}

const heightClasses = {
  52: 'h-[52px] text-base font-bold leading-5',
  41: 'h-[41px] text-sm font-semibold',
};

const variantClasses = {
  green:
    'bg-gradient-to-r from-[#2BFF13] to-[#20BF0E] text-[#0E0F0C] hover:bg-gradient-to-r hover:from-white hover:to-white disabled:bg-[#7C9971]',
  gray: 'bg-white/10 text-white  backdrop-blur-sm hover:bg-white hover:text-[#0E0F0C] disabled:bg-white/10 disabled:backdrop-blur-sm',
  ghost: 'bg-transparent text-[#EAECE5] rounded-none hover:border-b hover:border-[#2BFF13]',
  red: 'bg-error text-white  backdrop-blur-sm backdrop-blur-sm hover:bg-white hover:text-[#0E0F0C]',
};
