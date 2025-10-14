'use client';

import Link from 'next/link';

import { cn } from 'lib/utils';
import Text from 'components/ui/Text';
import { Button } from 'components/common/Button';

interface ComponentNavProps {
  title?: string;
  buttonText?: string;
  buttonIcon?: any;
  _onButtonClick?: (() => void) | string;
  className?: string;
  buttonClassName?: string;
  disabled?: boolean;
}

export default function ComponentNav({
  title,
  buttonText,
  buttonIcon,
  _onButtonClick,
  className,
  buttonClassName,
  disabled = false,
}: ComponentNavProps) {
  return (
    <div
      className={cn(
        'flex flex-col justify-between gap-2 md:flex-row lg:flex-row lg:items-center',
        className,
      )}
    >
      <Text variant="3xl" className="text-[32px] font-semibold text-white">
        {title}
      </Text>

      {typeof _onButtonClick === 'string' ? (
        <Link href={_onButtonClick}>
          <Button
            className={cn('md:max-w-[200px] lg:max-w-[200px]', buttonClassName)}
            disabled={disabled}
          >
            {buttonIcon && buttonIcon}
            <span className="font-bold">{buttonText}</span>
          </Button>
        </Link>
      ) : (
        <Button
          className={cn('md:max-w-[200px] lg:max-w-[200px]', buttonClassName)}
          onClick={_onButtonClick}
          disabled={disabled}
        >
          {buttonIcon && buttonIcon}
          <span className="font-bold">{buttonText}</span>
        </Button>
      )}
    </div>
  );
}
