import { useRouter } from 'next/navigation';
import { Download, Edit2, FileText, ScrollText, Trash2 } from 'lucide-react';

import { ScriptCardProps } from '../_types';
import DeleteScriptModal from './DeleteScriptModal';
import ExportScriptModal from './ExportScriptModal';
import { Button } from 'components/ui/Button';
import { Badge } from 'components/ui/Badge';

export default function ScriptCard({ script, actions, className = '' }: ScriptCardProps) {
  const router = useRouter();
  const isCompleted = script.type === 'script' && script.status === 'generated';
  const scriptId = script.uuid;
  const lastEdited = script.modified
    ? new Date(script.modified).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : 'Unknown';
  const duration = script.estimated_duration
    ? `${Math.round(script.estimated_duration)} min`
    : null;
  const wordCount = script.word_count ? `${script.word_count.toLocaleString()} words` : null;

  return (
    <div className={`flex flex-col justify-between rounded-xl border border-border bg-card p-5 ${className}`}>
      <div>
        {/* Type badge */}
        <div className="mb-3 flex items-center gap-2">
          {isCompleted ? (
            <Badge variant="primary" className="gap-1">
              <ScrollText className="h-3 w-3" /> Script
            </Badge>
          ) : (
            <Badge variant="muted" className="gap-1">
              <FileText className="h-3 w-3" /> Outline
            </Badge>
          )}
        </div>

        {/* Title */}
        <h3 className="line-clamp-2 text-sm font-semibold text-foreground">{script.title}</h3>

        {/* Metadata */}
        <div className="mt-3 space-y-1 text-xs text-muted-foreground">
          <p>Last edited: <span className="font-medium text-foreground">{lastEdited}</span></p>
          {duration && <p>Duration: <span className="font-medium text-foreground">{duration}</span></p>}
          {wordCount && <p>Words: <span className="font-medium text-foreground">{wordCount}</span></p>}
        </div>
      </div>

      <div className="mt-4 flex items-center gap-2">
        <DeleteScriptModal
          trigger={
            <Button variant="outline" size="sm">
              <Trash2 className="h-3.5 w-3.5" /> Delete
            </Button>
          }
          script={script}
          actions={actions}
        />
        {isCompleted ? (
          <ExportScriptModal
            trigger={
              <Button size="sm" className="flex-1">
                <Download className="h-3.5 w-3.5" /> Export
              </Button>
            }
            script={script}
          />
        ) : (
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={() => router.push(`/new-script/${scriptId}`)}
          >
            <Edit2 className="h-3.5 w-3.5" /> Edit
          </Button>
        )}
      </div>
    </div>
  );
}
