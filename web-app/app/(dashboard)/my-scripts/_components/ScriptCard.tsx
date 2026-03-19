'use client';

import { useRouter } from 'next/navigation';
import { Download, FileText, ListTree, MoreVertical } from 'lucide-react';

import { ScriptCardProps } from '../_types';
import DeleteScriptModal from './DeleteScriptModal';
import ExportScriptModal from './ExportScriptModal';
import { cn } from 'lib/utils';

function formatRelativeDate(dateString?: string | null): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
  if (diffDays === 1) return 'yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

export default function ScriptCard({ script, actions, className = '' }: ScriptCardProps) {
  const router = useRouter();
  const isScript = script.type === 'script';
  const relativeDate = formatRelativeDate((script as any).modified || (script as any).created);

  // Meta pill: scripts show read time, outlines show section count
  const metaPill = isScript
    ? script.estimated_duration
      ? `${Math.round(script.estimated_duration)} min read`
      : script.word_count
        ? `${Math.round(script.word_count / 130)} min read`
        : null
    : (script as any).section_count
      ? `${(script as any).section_count} sections`
      : null;

  const handleCardClick = () => {
    if (isScript) {
      router.push(`/new-script/script/${script.uuid}`);
    } else {
      router.push(`/new-script/${script.uuid}`);
    }
  };
  console.log(script);

  return (
    <div
      className={cn(
        'flex min-h-[200px] cursor-pointer flex-col justify-between rounded-xl border border-border bg-card p-4 transition-colors hover:shadow-sm sm:min-h-[232px] sm:p-6',
        className,
      )}
      onClick={handleCardClick}
    >
      {/* Top: icon + action buttons */}
      <div className="mb-5 flex items-start justify-between">
        <div
          className={cn(
            'flex h-14 w-14 items-center justify-center rounded-lg',
            isScript ? 'bg-red-50 text-primary' : 'bg-blue-50 text-blue-500',
          )}
        >
          {isScript ? <FileText className="h-6 w-6" /> : <ListTree className="h-6 w-6" />}
        </div>

        <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
          {isScript && (
            <ExportScriptModal
              trigger={
                <button className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-secondary text-muted-foreground transition-colors hover:text-foreground">
                  <Download className="h-[18px] w-[18px]" />
                </button>
              }
              script={script}
            />
          )}
          <DeleteScriptModal
            trigger={
              <button className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-secondary text-muted-foreground transition-colors hover:text-foreground">
                <MoreVertical className="h-[18px] w-[18px]" />
              </button>
            }
            script={script}
            actions={actions}
          />
        </div>
      </div>

      {/* Title + meta */}
      <div className="flex-1">
        <h3 className="line-clamp-2 text-xl font-semibold leading-snug tracking-tight text-foreground sm:text-2xl">
          {script.title}
        </h3>
        <div className="mt-3 flex flex-wrap items-center gap-2.5">
          <span
            className={cn(
              'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold',
              isScript ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600',
            )}
          >
            {isScript ? 'Full Script' : 'Outline'}
          </span>
          {relativeDate && (
            <span className="text-sm text-muted-foreground">Generated {relativeDate}</span>
          )}
        </div>
      </div>

      {/* Footer meta pill */}
      {metaPill && (
        <div className="mt-6">
          <span className="inline-flex items-center rounded-full bg-secondary px-3 py-2 text-[13px] font-medium text-muted-foreground">
            {metaPill}
          </span>
        </div>
      )}
    </div>
  );
}
