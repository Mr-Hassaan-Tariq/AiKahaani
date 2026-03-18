import { ScriptListProps } from '../_types';
import ScriptCard from './ScriptCard';

export default function ScriptList({
  scripts,
  actions,
  loading = false,
  emptyState,
  className = '',
}: ScriptListProps) {
  if (loading) {
    return (
      <div
        className={`mt-6 grid gap-5 [grid-template-columns:repeat(auto-fill,minmax(280px,1fr))] ${className}`}
      >
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-[232px] animate-pulse rounded-xl bg-muted" />
        ))}
      </div>
    );
  }

  if (scripts.length === 0) {
    return (
      <div className={`mt-6 ${className}`}>
        {emptyState || (
          <div className="py-16 text-center">
            <p className="text-sm font-medium text-foreground">No scripts found</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Start creating your first script or outline to get started.
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div
      className={`mt-6 grid gap-5 [grid-template-columns:repeat(auto-fill,minmax(280px,1fr))] ${className}`}
    >
      {scripts.map((script) => (
        <ScriptCard key={script.uuid} script={script} actions={actions} />
      ))}
    </div>
  );
}
