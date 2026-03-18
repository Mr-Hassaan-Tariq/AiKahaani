import { Card } from 'components/ui/Card';

function Skeleton({ className }: { className?: string }) {
  return (
    <div className={`animate-pulse rounded-md bg-muted ${className ?? ''}`} />
  );
}

export default function DashboardLoading() {
  return (
    <div className="p-6 space-y-6">
        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} padding="md">
              <div className="flex items-start justify-between">
                <Skeleton className="h-3.5 w-24" />
                <Skeleton className="h-8 w-8 rounded-md" />
              </div>
              <Skeleton className="mt-3 h-8 w-16" />
              <Skeleton className="mt-1.5 h-3 w-20" />
            </Card>
          ))}
        </div>

        {/* Content grid */}
        <div className="grid gap-4 lg:grid-cols-3">
          <Card padding="none" className="lg:col-span-2">
            <div className="border-b border-border px-6 py-4">
              <Skeleton className="h-4 w-32" />
            </div>
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex items-center justify-between px-6 py-4 border-b border-border last:border-0">
                <div className="space-y-1.5">
                  <Skeleton className="h-3.5 w-48" />
                  <Skeleton className="h-3 w-32" />
                </div>
                <Skeleton className="h-5 w-14 rounded-md" />
              </div>
            ))}
          </Card>
          <Card padding="md">
            <Skeleton className="h-4 w-24 mb-1" />
            <Skeleton className="h-3 w-36 mb-4" />
            <div className="space-y-2">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full rounded-lg" />
              ))}
            </div>
          </Card>
        </div>
    </div>
  );
}
