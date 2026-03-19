import { Copy } from 'lucide-react';

import { cn } from 'lib/utils';
import { Button } from 'components/ui/Button';

export default function TitleList({
  titles,
  onCopy,
  selectedTones = [],
}: {
  titles: string[];
  onCopy: (title: string) => void;
  selectedTones?: string[];
}) {
  return (
    <div className="flex flex-col gap-4">
      {titles.map((title, i) => {
        const isFeatured = i === 0;
        const charCount = title.length;
        const tone = selectedTones[i % selectedTones.length] || null;

        return (
          <div
            key={i}
            className={cn(
              'flex flex-col gap-4 rounded-xl border border-border p-4 sm:p-5',
              isFeatured
                ? 'border-primary/20 bg-gradient-to-b from-primary/[0.04] to-card'
                : 'bg-card',
            )}
          >
            {/* Top: badges */}
            <div className="flex flex-wrap items-center gap-2">
              {isFeatured && (
                <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">
                  Top pick
                </span>
              )}
              {tone && (
                <span className="inline-flex items-center rounded-full bg-secondary px-2.5 py-1 text-xs font-medium text-muted-foreground">
                  {tone}
                </span>
              )}
              <span className="inline-flex items-center rounded-full bg-secondary px-2.5 py-1 text-xs font-medium text-muted-foreground">
                {charCount} chars
              </span>
            </div>

            {/* Title text */}
            <h3 className="text-[18px] font-bold leading-snug tracking-tight text-foreground sm:text-[22px]">
              {title}
            </h3>

            {/* Copy button */}
            <div>
              <Button
                size="sm"
                variant={isFeatured ? 'primary' : 'outline'}
                onClick={() => onCopy(title)}
                className="gap-2"
              >
                <Copy className="h-3.5 w-3.5" />
                {isFeatured ? 'Copy Title' : 'Copy'}
              </Button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
