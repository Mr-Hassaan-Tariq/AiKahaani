import { Skeleton } from 'components/shadcn_ui/skeleton';

export default function NewScriptLoading() {
  return (
    <div className="flex flex-col">
      {/* Topbar skeleton */}
      <div className="flex h-16 items-center border-b border-border px-6">
        <div className="flex flex-col gap-1">
          <Skeleton className="h-4 w-36" />
          <Skeleton className="h-3 w-56" />
        </div>
      </div>

      <div className="mx-auto w-full max-w-3xl px-6 py-8">
        <div className="flex flex-col gap-6">
          {/* Textarea */}
          <div className="flex flex-col gap-2">
            <Skeleton className="h-4 w-44" />
            <Skeleton className="h-36 w-full rounded-xl" />
          </div>

          <Skeleton className="h-px w-full" />

          {/* Templates */}
          <div className="flex flex-col gap-3">
            <Skeleton className="h-4 w-28" />
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-24 w-full rounded-xl" />
              ))}
            </div>
          </div>

          {/* Slider */}
          <div className="flex flex-col gap-3">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-2 w-full rounded-full" />
            <div className="flex justify-between">
              <Skeleton className="h-3 w-20" />
              <Skeleton className="h-3 w-20" />
            </div>
          </div>

          {/* Tones */}
          <div className="flex flex-col gap-3">
            <Skeleton className="h-4 w-20" />
            <div className="flex flex-wrap gap-2">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-8 w-20 rounded-md" />
              ))}
            </div>
          </div>

          {/* Submit */}
          <Skeleton className="h-12 w-full rounded-lg" />
        </div>
      </div>
    </div>
  );
}
