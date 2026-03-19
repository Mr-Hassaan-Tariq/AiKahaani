import { Copy } from 'lucide-react';

import { TitleItem } from '../page';
import { cn } from 'lib/utils';
import { Button } from 'components/ui/Button';

const leverColors: Record<string, string> = {
  curiosity: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  emotion: 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400',
  urgency: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  shock: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  mystery: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
};

export default function TitleList({
  titles,
  onCopy,
  selectedTones = [],
}: {
  titles: TitleItem[];
  onCopy: (title: TitleItem) => void;
  selectedTones?: string[];
}) {
  return (
    <div className="flex flex-col gap-4">
      {titles.map((item, i) => {
        const isFeatured = i === 0;
        const charCount = item.length_chars ?? item.title.length;
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
            {/* Badges row */}
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
              {item.word_count && (
                <span className="inline-flex items-center rounded-full bg-secondary px-2.5 py-1 text-xs font-medium text-muted-foreground">
                  {item.word_count} words
                </span>
              )}
              {item.truncation_safe && (
                <span className="inline-flex items-center rounded-full bg-green-100 px-2.5 py-1 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
                  ✓ Truncation safe
                </span>
              )}
            </div>

            {/* Title text */}
            <h3 className="text-[18px] font-bold leading-snug tracking-tight text-foreground sm:text-[22px]">
              {item.title}
            </h3>

            {/* Levers / hooks */}
            {item.levers && item.levers.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {item.levers.map((lever) => (
                  <span
                    key={lever}
                    className={cn(
                      'inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-semibold capitalize',
                      leverColors[lever] ?? 'bg-secondary text-muted-foreground',
                    )}
                  >
                    {lever}
                  </span>
                ))}
              </div>
            )}

            {/* Angle / insight */}
            {item.angle && (
              <p className="text-[13px] leading-relaxed text-muted-foreground">{item.angle}</p>
            )}

            {/* Notes */}
            {item.notes && (
              <p className="text-[12px] italic leading-relaxed text-muted-foreground/70">
                {item.notes}
              </p>
            )}

            {/* Power words */}
            {item.power_words && item.power_words.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {item.power_words.map((word) => (
                  <span
                    key={word}
                    className="inline-flex items-center rounded-md border border-border bg-secondary px-2 py-0.5 text-[11px] font-medium text-foreground"
                  >
                    {word}
                  </span>
                ))}
              </div>
            )}

            {/* Copy button */}
            <div>
              <Button
                size="sm"
                variant={isFeatured ? 'primary' : 'outline'}
                onClick={() => onCopy(item)}
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
