import { Loader } from 'lucide-react';

import { Spinner } from 'components/ui/Spinner';

export function LoadingScreen() {
  return (
    <div className="flex h-full w-full flex-col items-center justify-center">
      <div className="flex min-h-[400px] flex-col items-center justify-center gap-6">
        {/* Animated icon */}
        <div className="relative flex h-16 w-16 items-center justify-center">
          <Loader className="h-7 w-7 animate-ping" />
        </div>

        {/* Text */}
        <div className="text-center">
          <p className="text-sm font-semibold text-foreground">Analyzing your topic…</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Outlining key points and structuring your script
          </p>
        </div>

        {/* Progress shimmer */}
        <div className="w-full max-w-sm space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-3 animate-pulse rounded-full bg-muted"
              style={{ width: `${[88, 72, 95, 64][i]}%` }}
            />
          ))}
        </div>

        {/* Spinner + label */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Spinner size="sm" color="primary" />
          Generating your script outline…
        </div>
      </div>
    </div>
  );
}
