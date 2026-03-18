'use client';

import Link from 'next/link';

import { cn } from 'lib/utils';
import { Button } from 'components/ui/Button';

interface ComponentNavProps {
  title?: string;
  buttonText?: string;
  buttonIcon?: React.ReactNode;
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
      className={cn('flex flex-col justify-between gap-2 md:flex-row md:items-center', className)}
    >
      <h2 className="text-lg font-semibold text-foreground">{title}</h2>

      {typeof _onButtonClick === 'string' ? (
        <Link href={_onButtonClick}>
          <Button size="sm" className={cn(buttonClassName)} disabled={disabled}>
            {buttonIcon}
            {buttonText}
          </Button>
        </Link>
      ) : (
        <Button
          size="sm"
          className={cn(buttonClassName)}
          onClick={_onButtonClick}
          disabled={disabled}
        >
          {buttonIcon}
          {buttonText}
        </Button>
      )}
    </div>
  );
}
