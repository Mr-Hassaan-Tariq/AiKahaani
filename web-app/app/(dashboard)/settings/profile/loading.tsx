import { Skeleton } from 'components/shadcn_ui/skeleton';

export default function Loading() {
  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      {/* Photo card skeleton */}
      <div className="rounded-xl border border-border bg-card p-6">
        <Skeleton className="mb-5 h-4 w-28" />
        <div className="flex items-center gap-5">
          <Skeleton className="h-24 w-24 rounded-full" />
          <div className="flex flex-col gap-3">
            <div className="space-y-1.5">
              <Skeleton className="h-3.5 w-44" />
              <Skeleton className="h-3.5 w-52" />
            </div>
            <div className="flex gap-2">
              <Skeleton className="h-8 w-32 rounded-lg" />
              <Skeleton className="h-8 w-24 rounded-lg" />
            </div>
          </div>
        </div>
      </div>

      {/* Details card skeleton */}
      <div className="rounded-xl border border-border bg-card p-6">
        <Skeleton className="mb-5 h-4 w-32" />
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex flex-col gap-1.5">
              <Skeleton className="h-3.5 w-20" />
              <Skeleton className="h-9 w-full rounded-lg" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
