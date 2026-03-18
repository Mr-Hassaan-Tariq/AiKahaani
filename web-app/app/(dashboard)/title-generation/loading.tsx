import { Skeleton } from 'components/shadcn_ui/skeleton';

export default function TitleGeneratorLoading() {
  return (
    <div className="flex flex-col">
      <div className="flex h-16 items-center border-b border-border px-6">
        <div className="flex flex-col gap-1">
          <Skeleton className="h-4 w-36" />
          <Skeleton className="h-3 w-48" />
        </div>
      </div>

      <div className="mx-auto flex w-full max-w-2xl flex-col gap-6 px-6 py-8">
        {/* Tabs */}
        <Skeleton className="h-10 w-full rounded-lg" />

        {/* Textarea */}
        <div className="flex flex-col gap-2">
          <Skeleton className="h-4 w-40" />
          <Skeleton className="h-24 w-full rounded-xl" />
        </div>

        {/* Tones */}
        <div className="flex flex-col gap-3">
          <Skeleton className="h-4 w-24" />
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
  );
}
