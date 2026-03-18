'use client';

import { useState } from 'react';

import { useScriptActions } from '../_hooks/useScriptActions';
import ScriptList from './ScriptList';
import { ScriptGeneration } from 'lib/api/types';

interface MyScriptsListProps {
  initialScripts?: ScriptGeneration[];
  error?: any;
  isError?: boolean;
  searchQuery?: string;
  loading?: boolean;
}

export default function MyScriptsList({
  initialScripts = [],
  error,
  isError,
  searchQuery,
  loading = false,
}: MyScriptsListProps) {
  const [scripts, setScripts] = useState<ScriptGeneration[]>(initialScripts);
  const { actions } = useScriptActions();

  if (initialScripts !== scripts && initialScripts.length !== scripts.length) {
    setScripts(initialScripts);
  }

  const emptyState = searchQuery ? (
    <div className="py-12 text-center">
      <p className="text-sm font-medium text-foreground">No results for &quot;{searchQuery}&quot;</p>
      <p className="mt-1 text-xs text-muted-foreground">Try adjusting your search terms.</p>
    </div>
  ) : undefined;

  return (
    <>
      {isError && (
        <div className="rounded-lg border border-destructive/20 bg-destructive/5 p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-destructive">{error?.message || 'Failed to load scripts'}</p>
            <button
              onClick={() => window.location.reload()}
              className="ml-4 rounded-md border border-destructive/30 px-3 py-1 text-xs text-destructive transition-colors hover:bg-destructive/10"
            >
              Retry
            </button>
          </div>
        </div>
      )}
      <ScriptList scripts={scripts} actions={actions} loading={loading} emptyState={emptyState} />
    </>
  );
}
