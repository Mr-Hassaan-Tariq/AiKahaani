import { ReactNode } from 'react';
import { InfoIcon } from 'lucide-react';

import Text from 'components/ui/Text';
import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

export default function InfoModal({ description }: { description: ReactNode }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <InfoIcon size={16} className="text-white" />
      </PopoverTrigger>
      <PopoverContent
        className="w-fit max-w-56 rounded-lg border border-[#BAFF38]/[12%] bg-brand-surface bg-white/10 p-2"
        align="start"
        side="top"
      >
        <Text variant="sm" className="w-fit text-white">
          {description}
        </Text>
      </PopoverContent>
    </Popover>
  );
}
