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
      <div className={`mt-6 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 ${className}`}>
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="animate-pulse">
            <div className="h-64 rounded-lg bg-white/10"></div>
          </div>
        ))}
      </div>
    );
  }

  if (scripts.length === 0) {
    return (
      <div className={`mt-6 ${className}`}>
        {emptyState || (
          <div className="py-12 text-center">
            <div className="mb-4 text-6xl">📝</div>
            <h3 className="mb-2 text-xl font-semibold text-white">No scripts found</h3>
            <p className="text-gray-400">
              Start creating your first script or outline to get started.
            </p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`mt-6 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 ${className}`}>
      {scripts?.map((script) => (
        <ScriptCard key={script.uuid} script={script} actions={actions} />
      ))}
    </div>
  );
}
