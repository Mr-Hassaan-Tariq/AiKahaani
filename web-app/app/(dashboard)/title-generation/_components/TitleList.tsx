import { Copy } from 'lucide-react';

import { Button } from 'components/ui/Button';
import { cn } from 'lib/utils';

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
              'rounded-xl border border-border p-5 flex flex-col gap-4',
              isFeatured
                ? 'bg-gradient-to-b from-primary/[0.04] to-card border-primary/20'
                : 'bg-card',
            )}
          >
            {/* Top: badges */}
            <div className="flex items-center gap-2 flex-wrap">
              {isFeatured && (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold">
                  Top pick
                </span>
              )}
              {tone && (
                <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-secondary text-muted-foreground text-xs font-medium">
                  {tone}
                </span>
              )}
              <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-secondary text-muted-foreground text-xs font-medium">
                {charCount} chars
              </span>
            </div>

            {/* Title text */}
            <h3 className="text-[22px] font-bold text-foreground leading-snug tracking-tight">
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
