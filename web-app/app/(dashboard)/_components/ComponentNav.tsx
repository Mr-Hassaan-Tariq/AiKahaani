'use client';

import { cn } from 'lib/utils';
import Text from 'components/ui/Text';
import { Button } from 'components/common/Button';

interface ComponentNavProps {
  title?: string;
  buttonText?: string;
  buttonIcon?: any;
  _onButtonClick?: () => void;
  className?: string;
  buttonClassName?: string;
}

export default function ComponentNav({
  title,
  buttonText,
  buttonIcon,
  _onButtonClick,
  className,
  buttonClassName,
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
      <Button className={cn('md:max-w-[200px] lg:max-w-[200px]', buttonClassName)}>
        {buttonIcon && buttonIcon}
        <span className="font-bold">{buttonText}</span>
      </Button>
    </div>
  );
}
