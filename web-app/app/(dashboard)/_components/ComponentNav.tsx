'use client';

import Image from 'next/image';

import Text from 'components/ui/Text';
import { Button } from 'components/common/Button';

interface ComponentNavProps {
  title?: string;
  buttonText?: string;
  buttonIcon?: any;
  _onButtonClick?: () => void;
}

export default function ComponentNav({
  title,
  buttonText,
  buttonIcon,
  _onButtonClick,
}: ComponentNavProps) {
  return (
    <div className="flex flex-col justify-between gap-2 md:flex-row lg:flex-row lg:items-center">
      <Text variant="3xl" className="text-[32px] font-semibold text-white">
        {title}
      </Text>
      <Button className="md:max-w-[200px] lg:max-w-[200px]">
        {buttonIcon && <Image src={buttonIcon} alt="icon" width={20} height={20} />}
        <span className="font-bold">{buttonText}</span>
      </Button>
    </div>
  );
}
