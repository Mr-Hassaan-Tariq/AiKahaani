import { ReactNode } from 'react';
import { InfoIcon } from 'lucide-react';

import { Popover, PopoverContent, PopoverTrigger } from 'components/shadcn_ui/popover';

export default function InfoModal({ description }: { description: ReactNode }) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          className="inline-flex text-muted-foreground transition-colors hover:text-foreground"
        >
          <InfoIcon className="h-4 w-4" />
        </button>
      </PopoverTrigger>
      <PopoverContent
        className="w-64 rounded-lg border border-border bg-card p-3 shadow-md"
        align="start"
        side="top"
      >
        <p className="text-xs leading-relaxed text-muted-foreground">{description}</p>
      </PopoverContent>
    </Popover>
  );
}
