import { Sparkles } from 'lucide-react';

import { Spinner } from 'components/ui/Spinner';

export function LoadingScreen() {
  return (
    <div className="flex w-full flex-col items-center justify-center gap-6 py-16">
      <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-accent">
        <Sparkles className="h-6 w-6 text-primary" />
        <span className="absolute inset-0 animate-ping rounded-2xl bg-primary/10" />
      </div>

      <div className="text-center">
        <p className="text-sm font-semibold text-foreground">Analyzing your topic…</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Testing high-CTR variations for your niche
        </p>
      </div>

      <div className="w-full max-w-sm space-y-2">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="h-10 animate-pulse rounded-lg bg-muted"
            style={{ width: `${[90, 75, 85, 70, 80][i]}%` }}
          />
        ))}
      </div>

      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Spinner size="sm" color="primary" />
        Generating titles…
      </div>
    </div>
  );
}
